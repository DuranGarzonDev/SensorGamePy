"""
Programa principal optimizado: Plataforma de Equilibrio Controlada por Gestos (Versión OpenCV).

Esta es una versión optimizada que NO requiere MediaPipe.
Utiliza solo OpenCV para la detección de manos con filtrado de cara.

Autores: Juan David Durán Garzón, Ángel Andrés Boada Salazar
Curso: Sistemas de Interacción Persona-Computador
Universidad: Universidad de La Laguna
"""

import cv2
import numpy as np
import sys
from hand_tracker_opencv import HandTrackerOpenCV
from physics_world import PhysicsWorld
from utils import mediapipe_to_pymunk, clamp, smooth_value


class GestureBalanceGameOpenCV:
    """
    Clase principal optimizada que integra el rastreador de manos (OpenCV) y el mundo de física.
    
    Gestiona:
    - Captura de video
    - Detección de manos con OpenCV (sin detectar cara)
    - Actualización del mundo de física
    - Renderizado mejorado de la escena
    - Optimización de FPS
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Inicializa el juego.
        
        Args:
            width: Ancho de la ventana
            height: Alto de la ventana
        """
        self.width = width
        self.height = height
        self.running = True
        
        # Inicializar rastreador de manos (OpenCV)
        self.hand_tracker = HandTrackerOpenCV()
        
        # Inicializar mundo de física
        self.physics_world = PhysicsWorld(width, height)
        
        # Variables de suavizado
        self.smoothed_x = width / 2
        self.smoothed_y = height / 2
        self.smoothed_angle = 0
        
        # FPS y timing
        self.clock = cv2.getTickCount()
        self.fps = 0
        self.frame_count = 0
        
        # Estado del juego
        self.paused = False
        self.show_landmarks = True
        self.show_mask = False
        
        # Optimización: procesar cada N frames para detección
        self.detection_interval = 1  # Detectar cada frame
        self.detection_counter = 0
        
    def run(self):
        """Ejecuta el bucle principal del juego."""
        # Abrir cámara
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: No se pudo acceder a la cámara.")
            return
        
        # Configurar resolución de la cámara
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, 30)  # Limitar a 30 FPS
        
        print("Iniciando juego optimizado (Versión OpenCV - Sin MediaPipe)...")
        print("Controles:")
        print("  - Mueve tu mano DERECHA para controlar la plataforma")
        print("  - Rota tu mano para inclinar la plataforma")
        print("  - Presiona 'L' para mostrar/ocultar puntos de referencia")
        print("  - Presiona 'M' para mostrar/ocultar máscara de detección")
        print("  - Presiona 'P' para pausar/reanudar")
        print("  - Presiona 'R' para reiniciar")
        print("  - Presiona 'Q' para salir")
        print("\nNOTA: La cara NO será detectada, solo la mano.")
        
        try:
            while self.running:
                ret, frame = cap.read()
                
                if not ret:
                    print("Error: No se pudo leer el fotograma.")
                    break
                
                # Espejo horizontal
                frame = cv2.flip(frame, 1)
                
                # Detectar mano (optimizado)
                self.detection_counter += 1
                if self.detection_counter >= self.detection_interval:
                    landmarks, angle, position = self.hand_tracker.detect_hand(frame)
                    self.detection_counter = 0
                    
                    # Mostrar máscara si está habilitada
                    if self.show_mask:
                        mask = self.hand_tracker.draw_hand_mask(frame)
                        cv2.imshow("Máscara de Detección (Sin Cara)", mask)
                    
                    # Actualizar física si se detectó una mano
                    if landmarks is not None and position is not None and angle is not None:
                        # Convertir coordenadas
                        pymunk_x, pymunk_y = mediapipe_to_pymunk(
                            position[0], position[1],
                            self.width, self.height,
                            self.width, self.height
                        )
                        
                        # Suavizar valores
                        self.smoothed_x = smooth_value(self.smoothed_x, pymunk_x, 0.2)
                        self.smoothed_y = smooth_value(self.smoothed_y, pymunk_y, 0.2)
                        self.smoothed_angle = smooth_value(self.smoothed_angle, angle, 0.15)
                        
                        # Limitar posición dentro de los límites
                        self.smoothed_x = clamp(self.smoothed_x, 60, self.width - 60)
                        self.smoothed_y = clamp(self.smoothed_y, 60, self.height - 60)
                        
                        # Actualizar plataforma
                        if not self.paused:
                            self.physics_world.update_platform(
                                (self.smoothed_x, self.smoothed_y),
                                self.smoothed_angle
                            )
                        
                        # Dibujar landmarks si está habilitado
                        if self.show_landmarks:
                            frame = self.hand_tracker.draw_landmarks(frame, landmarks)
                
                # Actualizar física
                if not self.paused:
                    self.physics_world.update()
                
                # Renderizar escena
                frame = self._render_scene(frame)
                
                # Mostrar FPS
                self.frame_count += 1
                if self.frame_count % 10 == 0:
                    elapsed = (cv2.getTickCount() - self.clock) / cv2.getTickFrequency()
                    self.fps = 10 / elapsed
                    self.clock = cv2.getTickCount()
                
                # Interfaz mejorada
                self._draw_ui(frame)
                
                # Mostrar frame
                cv2.imshow("Plataforma de Equilibrio - Control por Gestos (OpenCV)", frame)
                
                # Procesar entrada
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key == ord('l'):
                    self.show_landmarks = not self.show_landmarks
                elif key == ord('m'):
                    self.show_mask = not self.show_mask
                    if not self.show_mask:
                        cv2.destroyWindow("Máscara de Detección (Sin Cara)")
                elif key == ord('p'):
                    self.paused = not self.paused
                elif key == ord('r'):
                    self.physics_world.reset()
        
        except KeyboardInterrupt:
            print("\nJuego interrumpido por el usuario.")
        
        finally:
            # Liberar recursos
            cap.release()
            self.hand_tracker.release()
            cv2.destroyAllWindows()
            print("Juego finalizado.")
    
    def _draw_ui(self, frame: np.ndarray):
        """
        Dibuja la interfaz de usuario mejorada.
        
        Args:
            frame: Fotograma de OpenCV
        """
        # Panel de información con fondo semitransparente
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (350, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (15, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Bolas capturadas
        cv2.putText(frame, f"Bolas capturadas: {self.physics_world.balls_caught}", (15, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Versión
        cv2.putText(frame, "OpenCV (Sin MediaPipe)", (15, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Instrucción
        cv2.putText(frame, "Usa tu MANO DERECHA", (15, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # Pausado
        if self.paused:
            cv2.putText(frame, "PAUSADO", (self.width // 2 - 80, self.height // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    
    def _render_scene(self, frame: np.ndarray) -> np.ndarray:
        """
        Renderiza los objetos del mundo de física en el fotograma con gráficos mejorados.
        
        Args:
            frame: Fotograma de OpenCV
            
        Returns:
            Fotograma con los objetos renderizados
        """
        # Dibujar zona de captura (bucket) mejorada
        bucket_x, bucket_y, bucket_w, bucket_h = self.physics_world.get_bucket_rect()
        
        # Fondo de la zona con transparencia
        overlay = frame.copy()
        cv2.rectangle(overlay, 
                     (int(bucket_x), int(bucket_y)),
                     (int(bucket_x + bucket_w), int(bucket_y + bucket_h)),
                     (255, 100, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Borde de la zona
        cv2.rectangle(frame, 
                     (int(bucket_x), int(bucket_y)),
                     (int(bucket_x + bucket_w), int(bucket_y + bucket_h)),
                     (255, 150, 0), 3)
        
        # Texto de la zona
        cv2.putText(frame, "ZONA CAPTURA", (int(bucket_x + 20), int(bucket_y + 30)),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Dibujar plataforma
        self._draw_platform(frame)
        
        # Dibujar bolas
        for body, shape in self.physics_world.get_balls():
            self._draw_circle(frame, body, shape)
        
        # Dibujar paredes
        self._draw_walls(frame)
        
        return frame
    
    def _draw_platform(self, frame: np.ndarray):
        """Dibuja la plataforma en el fotograma con mejor visualización."""
        body = self.physics_world.platform_body
        if body is None:
            return
        
        # Obtener vértices del rectángulo rotado
        x, y = body.position
        angle = body.angle
        width, height = 120, 12
        
        # Calcular vértices
        corners = np.array([
            [-width/2, -height/2],
            [width/2, -height/2],
            [width/2, height/2],
            [-width/2, height/2]
        ])
        
        # Rotar
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        rotation = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        corners = corners @ rotation.T
        
        # Trasladar
        corners = corners + np.array([x, y])
        
        # Convertir a enteros
        corners = corners.astype(int)
        
        # Dibujar sombra
        shadow_corners = corners + np.array([3, 3])
        cv2.fillPoly(frame, [shadow_corners], (50, 50, 50))
        
        # Dibujar plataforma con gradiente simulado
        cv2.fillPoly(frame, [corners], (0, 180, 220))
        cv2.polylines(frame, [corners], True, (0, 220, 255), 3)
        
        # Dibujar línea central
        center_start = ((corners[0] + corners[1]) / 2).astype(int)
        center_end = ((corners[2] + corners[3]) / 2).astype(int)
        cv2.line(frame, tuple(center_start), tuple(center_end), (255, 255, 255), 1)
    
    def _draw_circle(self, frame: np.ndarray, body, shape):
        """Dibuja una bola en el fotograma con mejor visualización."""
        x, y = int(body.position.x), int(body.position.y)
        radius = int(shape.radius)
        
        # Sombra
        cv2.circle(frame, (x + 2, y + 2), radius, (50, 50, 50), -1)
        
        # Bola principal
        cv2.circle(frame, (x, y), radius, (255, 80, 80), -1)
        
        # Borde
        cv2.circle(frame, (x, y), radius, (255, 120, 120), 2)
        
        # Brillo
        cv2.circle(frame, (x - radius//3, y - radius//3), radius//4, (255, 200, 200), -1)
        
        # Centro
        cv2.circle(frame, (x, y), 2, (200, 0, 0), -1)
    
    def _draw_walls(self, frame: np.ndarray):
        """Dibuja las paredes en el fotograma."""
        # Pared izquierda
        cv2.line(frame, (0, 0), (0, self.height), (200, 200, 200), 4)
        # Pared derecha
        cv2.line(frame, (self.width-1, 0), (self.width-1, self.height), (200, 200, 200), 4)
        # Piso
        cv2.line(frame, (0, 0), (self.width, 0), (200, 200, 200), 4)


def main():
    """Función principal."""
    print("=" * 60)
    print("PLATAFORMA DE EQUILIBRIO - CONTROL POR GESTOS")
    print("Versión Optimizada con OpenCV")
    print("=" * 60)
    print()
    
    game = GestureBalanceGameOpenCV(width=800, height=600)
    game.run()


if __name__ == "__main__":
    main()
