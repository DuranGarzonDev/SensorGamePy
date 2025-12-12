"""
Módulo alternativo para el seguimiento de manos usando solo OpenCV.

Este módulo proporciona la clase HandTrackerOpenCV que utiliza detección
de contornos y color de piel para detectar la mano sin depender de MediaPipe.
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class HandTrackerOpenCV:
    """
    Clase para rastrear la mano usando solo OpenCV.
    
    Utiliza:
    - Detección de color de piel (HSV)
    - Detección de contornos
    - Análisis de forma
    """
    
    def __init__(self):
        """Inicializa el rastreador de manos con OpenCV."""
        # Rango HSV para detectar piel (ajustable según iluminación)
        self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Kernel para operaciones morfológicas
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        
    def detect_hand(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[float], Optional[Tuple[float, float]]]:
        """
        Detecta la mano en un fotograma usando OpenCV.
        
        Args:
            frame: Fotograma de OpenCV (BGR)
            
        Returns:
            Tupla con:
            - landmarks: Array de puntos de la mano o None
            - angle: Ángulo de rotación en radianes o None
            - position: Tupla (x, y) del centro de la mano o None
        """
        h, w = frame.shape[:2]
        
        # Convertir a HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Detectar piel
        mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
        
        # Operaciones morfológicas
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=1)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return None, None, None
        
        # Encontrar el contorno más grande (la mano)
        hand_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(hand_contour)
        
        # Filtrar por área mínima
        if area < 1000:
            return None, None, None
        
        # Obtener el centro y el área de la mano
        M = cv2.moments(hand_contour)
        if M["m00"] == 0:
            return None, None, None
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        position = (cx, cy)
        
        # Calcular el ángulo usando el eje principal del contorno
        angle = self._calculate_contour_angle(hand_contour)
        
        # Generar puntos simulados (no son tan precisos como MediaPipe)
        landmarks = self._generate_landmarks(hand_contour, cx, cy)
        
        return landmarks, angle, position
    
    def _calculate_contour_angle(self, contour: np.ndarray) -> float:
        """
        Calcula el ángulo del contorno usando la elipse ajustada.
        
        Args:
            contour: Contorno de OpenCV
            
        Returns:
            Ángulo en radianes
        """
        if len(contour) < 5:
            return 0.0
        
        # Ajustar elipse
        ellipse = cv2.fitEllipse(contour)
        angle = ellipse[2]
        
        # Convertir a radianes
        angle_rad = np.radians(angle)
        
        return angle_rad
    
    def _generate_landmarks(self, contour: np.ndarray, cx: int, cy: int) -> np.ndarray:
        """
        Genera puntos de referencia simulados a partir del contorno.
        
        Args:
            contour: Contorno de la mano
            cx: Coordenada x del centro
            cy: Coordenada y del centro
            
        Returns:
            Array de puntos de referencia
        """
        # Aproximar el contorno
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Crear array de landmarks (simulados)
        landmarks = np.zeros((21, 3), dtype=np.float32)
        
        # Centro (punto 0 - muñeca)
        landmarks[0] = [cx, cy, 0]
        
        # Distribuir puntos alrededor del contorno
        if len(approx) > 0:
            for i in range(1, min(21, len(approx))):
                pt = approx[i][0]
                landmarks[i] = [pt[0], pt[1], 0]
        
        # Rellenar puntos faltantes interpolando
        for i in range(len(approx), 21):
            if i > 0:
                landmarks[i] = landmarks[i-1]
        
        return landmarks
    
    def draw_landmarks(self, frame: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """
        Dibuja los puntos de referencia en el fotograma.
        
        Args:
            frame: Fotograma de OpenCV
            landmarks: Array de puntos de referencia
            
        Returns:
            Fotograma con los puntos dibujados
        """
        frame_copy = frame.copy()
        
        if landmarks is None:
            return frame_copy
        
        # Dibujar puntos
        for i, landmark in enumerate(landmarks):
            x, y = int(landmark[0]), int(landmark[1])
            if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
                cv2.circle(frame_copy, (x, y), 3, (0, 255, 0), -1)
                if i == 0:
                    cv2.putText(frame_copy, "W", (x + 5, y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        # Dibujar conexiones
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20)
        ]
        
        for start, end in connections:
            if start < len(landmarks) and end < len(landmarks):
                pt1 = tuple(landmarks[start][:2].astype(int))
                pt2 = tuple(landmarks[end][:2].astype(int))
                if (0 <= pt1[0] < frame.shape[1] and 0 <= pt1[1] < frame.shape[0] and
                    0 <= pt2[0] < frame.shape[1] and 0 <= pt2[1] < frame.shape[0]):
                    cv2.line(frame_copy, pt1, pt2, (0, 255, 0), 2)
        
        return frame_copy
    
    def draw_hand_mask(self, frame: np.ndarray) -> np.ndarray:
        """
        Dibuja la máscara de detección de piel.
        
        Args:
            frame: Fotograma de OpenCV
            
        Returns:
            Máscara de piel
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        return mask
    
    def adjust_skin_range(self, lower_h: int, upper_h: int, lower_s: int, upper_s: int, 
                         lower_v: int, upper_v: int):
        """
        Ajusta el rango HSV para la detección de piel.
        
        Útil si la detección no funciona bien con la iluminación actual.
        
        Args:
            lower_h, upper_h: Rango de Hue
            lower_s, upper_s: Rango de Saturation
            lower_v, upper_v: Rango de Value
        """
        self.lower_skin = np.array([lower_h, lower_s, lower_v], dtype=np.uint8)
        self.upper_skin = np.array([upper_h, upper_s, upper_v], dtype=np.uint8)
    
    def release(self):
        """Libera los recursos."""
        pass
