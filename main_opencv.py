"""
Programa principal alternativo: Plataforma de Equilibrio Controlada por Gestos (Versión OpenCV).

Esta es una versión alternativa que NO requiere MediaPipe.
Utiliza solo OpenCV para la detección de manos.

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
    Clase principal que integra el rastreador de manos (OpenCV) y el mundo de física.
    
    Gestiona:
    - Captura de video
    - Detección de manos con OpenCV
    - Actualización del mundo de física
    - Renderizado de la escena
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
        
        print("Iniciando juego (Versión OpenCV - Sin MediaPipe)...")
        print("Controles:")
        print("  - Mueve tu mano para controlar la plataforma")
        print("  - Rota tu mano para inclinar la plataforma")
        print("  - Presiona 'L' para mostrar/ocultar puntos de referencia")
        print("  - Presiona 'M' para mostrar/ocultar máscara de detección")
        print("  - Presiona 'P' para pausar/reanudar")
        print("  - Presiona 'R' para reiniciar")
        print("  - Presiona 'A' para ajustar rango de piel")
        print("  - Presiona 'Q' para salir")
        
        try:
            while self.running:
                ret, frame = cap.read()
                
                if not ret:
                    print("Error: No se pudo leer el fotograma.")
                    break
                
                # Espejo horizontal
                frame = cv2.flip(frame, 1)
                
                # Detectar mano
                landmarks, angle, position = self.hand_tracker.detect_hand(frame)
                
                # Mostrar máscara si está habilitada
                if self.show_mask:
                    mask = self.hand_tracker.draw_hand_mask(frame)
                    cv2.imshow("Máscara de Detección", mask)
                
                # Actualizar física si se detectó una mano
                if landmarks is not None and position is not None and angle is not None:
                    # Convertir coordenadas
                    pymunk_x, pymunk_y = mediapipe_to_pymunk(
                        position[0], position[1],
                        self.width, self.height,
                        self.width, self.height
                    )
                    
                    # Suavizar valores
                    self.smoothed_x = smooth_value(self.smoothed_x, pymunk_x, 0.15)
                    self.smoothed_y = smooth_value(self.smoothed_y, pymunk_y, 0.15)
                    self.smoothed_angle = smooth_value(self.smoothed_angle, angle, 0.1)
                    
                    # Limitar posición dentro de los límites
                    self.smoothed_x = clamp(self.smoothed_x, 50, self.width - 50)
                    self.smoothed_y = clamp(self.smoothed_y, 50, self.height - 50)
                    
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
                
                cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Bolas capturadas: {self.physics_world.balls_caught}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Versión: OpenCV (Sin MediaPipe)", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                
                if self.paused:
                    cv2.putText(frame, "PAUSADO", (self.width // 2 - 50, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
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
                elif key == ord('p'):
                    self.paused = not self.paused
                elif key == ord('r'):
                    self.physics_world.reset()
                elif key == ord('a'):
                    self._adjust_skin_detection()
        
        except KeyboardInterrupt:
            print("\nJuego interrumpido por el usuario.")
        
        finally:
            # Liberar recursos
            cap.release()
            self.hand_tracker.release()
            cv2.destroyAllWindows()
            print("Juego finalizado.")
    
    def _adjust_skin_detection(self):
        """Permite ajustar el rango HSV para la detección de piel."""
        print("\n=== Ajuste de Detección de Piel ===")
        print("Ingresa los valores HSV (Hue, Saturation, Value)")
        print("Rango: Hue (0-180), Saturation (0-255), Value (0-255)")
        print("Valores por defecto: H(0-20), S(20-255), V(70-255)")
        
        try:
            lower_h = int(input("Hue mínimo (0-180): ") or 0)
            upper_h = int(input("Hue máximo (0-180): ") or 20)
            lower_s = int(input("Saturation mínima (0-255): ") or 20)
            upper_s = int(input("Saturation máxima (0-255): ") or 255)
            lower_v = int(input("Value mínimo (0-255): ") or 70)
            upper_v = int(input("Value máximo (0-255): ") or 255)
            
            self.hand_tracker.adjust_skin_range(lower_h, upper_h, lower_s, upper_s, lower_v, upper_v)
            print("Rango ajustado correctamente.")
        except ValueError:
            print("Valores inválidos. Se mantienen los valores anteriores.")
    
    def _render_scene(self, frame: np.ndarray) -> np.ndarray:
        """
        Renderiza los objetos del mundo de física en el fotograma.
        
        Args:
            frame: Fotograma de OpenCV
            
        Returns:
            Fotograma con los objetos renderizados
        """
        # Dibujar zona de captura (bucket)
        bucket_x, bucket_y, bucket_w, bucket_h = self.physics_world.get_bucket_rect()
        cv2.rectangle(frame, 
                     (int(bucket_x), int(bucket_y)),
                     (int(bucket_x + bucket_w), int(bucket_y + bucket_h)),
                     (255, 0, 0), 2)
        cv2.putText(frame, "ZONA CAPTURA", (int(bucket_x + 10), int(bucket_y + 30)),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Dibujar plataforma
        self._draw_platform(frame)
        
        # Dibujar bolas
        for body, shape in self.physics_world.get_balls():
            self._draw_circle(frame, body, shape)
        
        # Dibujar paredes
        self._draw_walls(frame)
        
        return frame
    
    def _draw_platform(self, frame: np.ndarray):
        """Dibuja la plataforma en el fotograma."""
        body = self.physics_world.platform_body
        if body is None:
            return
        
        # Obtener vértices del rectángulo rotado
        x, y = body.position
        angle = body.angle
        width, height = 100, 15
        
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
        
        # Dibujar rectángulo
        cv2.polylines(frame, [corners], True, (0, 255, 255), 3)
        cv2.fillPoly(frame, [corners], (0, 200, 200))
    
    def _draw_circle(self, frame: np.ndarray, body, shape):
        """Dibuja una bola en el fotograma."""
        x, y = int(body.position.x), int(body.position.y)
        radius = int(shape.radius)
        cv2.circle(frame, (x, y), radius, (0, 0, 255), 2)
        cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
    
    def _draw_walls(self, frame: np.ndarray):
        """Dibuja las paredes en el fotograma."""
        # Pared izquierda
        cv2.line(frame, (0, 0), (0, self.height), (255, 255, 255), 3)
        # Pared derecha
        cv2.line(frame, (self.width, 0), (self.width, self.height), (255, 255, 255), 3)
        # Piso
        cv2.line(frame, (0, 0), (self.width, 0), (255, 255, 255), 3)


def main():
    """Función principal."""
    game = GestureBalanceGameOpenCV(width=800, height=600)
    game.run()


if __name__ == "__main__":
    main()
