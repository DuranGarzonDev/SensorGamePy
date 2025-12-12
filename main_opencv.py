"""
Programa principal: Plataforma de Equilibrio Controlada por Gestos.

Versión OpenCV - Sin MediaPipe.

Autores: Juan David Durán Garzón, Ángel Andrés Boada Salazar
Curso: Sistemas de Interacción Persona-Computador
Universidad: Universidad de La Laguna
"""

import cv2
import numpy as np
from hand_tracker_opencv import HandTrackerOpenCV
from physics_world import PhysicsWorld
from utils import mediapipe_to_pymunk, clamp, smooth_value


class GestureBalanceGame:
    """
    Clase principal del juego.
    
    Integra detección de manos y física.
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
        
        # Inicializar componentes
        self.hand_tracker = HandTrackerOpenCV()
        self.physics_world = PhysicsWorld(width, height)
        
        # Variables de suavizado
        self.smoothed_x = width / 2
        self.smoothed_y = height / 2
        self.smoothed_angle = 0
        
        # FPS
        self.clock = cv2.getTickCount()
        self.fps = 0
        self.frame_count = 0
        
        # Estado
        self.paused = False
        self.show_landmarks = True
        
    def run(self):
        """Ejecuta el bucle principal del juego."""
        # Abrir cámara
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: No se pudo acceder a la cámara.")
            return
        
        # Configurar cámara
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("=" * 60)
        print("PLATAFORMA DE EQUILIBRIO - CONTROL POR GESTOS")
        print("=" * 60)
        print("\nControles:")
        print("  - Mueve tu MANO DERECHA para controlar la plataforma")
        print("  - Rota tu mano para inclinar la plataforma")
        print("  - Presiona 'L' para mostrar/ocultar landmarks")
        print("  - Presiona 'P' para pausar/reanudar")
        print("  - Presiona 'R' para reiniciar")
        print("  - Presiona 'Q' para salir")
        print("\n¡La cara NO será detectada!")
        print("=" * 60)
        
        try:
            while self.running:
                ret, frame = cap.read()
                
                if not ret:
                    print("Error al leer fotograma.")
                    break
                
                # Espejo
                frame = cv2.flip(frame, 1)
                
                # Detectar mano
                landmarks, angle, position = self.hand_tracker.detect_hand(frame)
                
                # Actualizar si se detectó mano
                if landmarks is not None and position is not None and angle is not None:
                    # Convertir coordenadas
                    pymunk_x, pymunk_y = mediapipe_to_pymunk(
                        position[0], position[1],
                        self.width, self.height,
                        self.width, self.height
                    )
                    
                    # Suavizar
                    self.smoothed_x = smooth_value(self.smoothed_x, pymunk_x, 0.2)
                    self.smoothed_y = smooth_value(self.smoothed_y, pymunk_y, 0.2)
                    self.smoothed_angle = smooth_value(self.smoothed_angle, angle, 0.15)
                    
                    # Limitar
                    self.smoothed_x = clamp(self.smoothed_x, 70, self.width - 70)
                    self.smoothed_y = clamp(self.smoothed_y, 70, self.height - 70)
                    
                    # Actualizar plataforma
                    if not self.paused:
                        self.physics_world.update_platform(
                            (self.smoothed_x, self.smoothed_y),
                            self.smoothed_angle
                        )
                    
                    # Dibujar landmarks
                    if self.show_landmarks:
                        frame = self.hand_tracker.draw_landmarks(frame, landmarks)
                
                # Actualizar física
                if not self.paused:
                    self.physics_world.update()
                
                # Renderizar
                frame = self._render_scene(frame)
                
                # Calcular FPS
                self.frame_count += 1
                if self.frame_count % 10 == 0:
                    elapsed = (cv2.getTickCount() - self.clock) / cv2.getTickFrequency()
                    self.fps = 10 / elapsed
                    self.clock = cv2.getTickCount()
                
                # Dibujar UI
                self._draw_ui(frame)
                
                # Mostrar
                cv2.imshow("Plataforma de Equilibrio - Control por Gestos", frame)
                
                # Procesar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key == ord('l'):
                    self.show_landmarks = not self.show_landmarks
                elif key == ord('p'):
                    self.paused = not self.paused
                elif key == ord('r'):
                    self.physics_world.reset()
        
        except KeyboardInterrupt:
            print("\nJuego interrumpido.")
        
        finally:
            cap.release()
            self.hand_tracker.release()
            cv2.destroyAllWindows()
            print("Juego finalizado.")
    
    def _draw_ui(self, frame: np.ndarray):
        """Dibuja la interfaz de usuario."""
        # Panel de información
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Textos
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Bolas capturadas: {self.physics_world.balls_caught}", (20, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "OpenCV (Sin MediaPipe)", (20, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # Pausado
        if self.paused:
            cv2.putText(frame, "PAUSADO", (self.width // 2 - 100, self.height // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    
    def _render_scene(self, frame: np.ndarray) -> np.ndarray:
        """Renderiza los objetos de física."""
        # Zona de captura
        bucket_x, bucket_y, bucket_w, bucket_h = self.physics_world.get_bucket_rect()
        
        # Fondo de zona
        overlay = frame.copy()
        cv2.rectangle(overlay,
                     (int(bucket_x), int(bucket_y)),
                     (int(bucket_x + bucket_w), int(bucket_y + bucket_h)),
                     (255, 100, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Borde de zona
        cv2.rectangle(frame,
                     (int(bucket_x), int(bucket_y)),
                     (int(bucket_x + bucket_w), int(bucket_y + bucket_h)),
                     (255, 150, 0), 3)
        
        # Texto de zona
        cv2.putText(frame, "ZONA CAPTURA", (int(bucket_x + 30), int(bucket_y + 40)),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Dibujar plataforma
        self._draw_platform(frame)
        
        # Dibujar bolas
        for body, shape in self.physics_world.get_balls():
            self._draw_ball(frame, body, shape)
        
        # Dibujar paredes
        self._draw_walls(frame)
        
        return frame
    
    def _draw_platform(self, frame: np.ndarray):
        """Dibuja la plataforma."""
        body = self.physics_world.platform_body
        if body is None:
            return
        
        x, y = body.position
        angle = body.angle
        width, height = 120, 15
        
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
        corners = corners.astype(int)
        
        # Sombra
        shadow = corners + np.array([3, 3])
        cv2.fillPoly(frame, [shadow], (50, 50, 50))
        
        # Plataforma
        cv2.fillPoly(frame, [corners], (0, 200, 255))
        cv2.polylines(frame, [corners], True, (0, 255, 255), 3)
    
    def _draw_ball(self, frame: np.ndarray, body, shape):
        """Dibuja una bola."""
        x, y = int(body.position.x), int(body.position.y)
        radius = int(shape.radius)
        
        # Sombra
        cv2.circle(frame, (x + 2, y + 2), radius, (50, 50, 50), -1)
        
        # Bola
        cv2.circle(frame, (x, y), radius, (255, 100, 100), -1)
        
        # Borde
        cv2.circle(frame, (x, y), radius, (255, 150, 150), 2)
        
        # Brillo
        cv2.circle(frame, (x - radius//3, y - radius//3), radius//4, (255, 220, 220), -1)
    
    def _draw_walls(self, frame: np.ndarray):
        """Dibuja las paredes."""
        cv2.line(frame, (0, 0), (0, self.height), (200, 200, 200), 4)
        cv2.line(frame, (self.width-1, 0), (self.width-1, self.height), (200, 200, 200), 4)
        cv2.line(frame, (0, 0), (self.width, 0), (200, 200, 200), 4)


def main():
    """Función principal."""
    game = GestureBalanceGame(width=800, height=600)
    game.run()


if __name__ == "__main__":
    main()
