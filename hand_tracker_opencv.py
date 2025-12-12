"""
Módulo para el seguimiento de manos usando OpenCV.

Detecta la mano usando color de piel y excluye la cara.
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class HandTrackerOpenCV:
    """
    Clase para rastrear la mano usando OpenCV.
    
    Utiliza detección de color de piel y excluye la cara.
    """
    
    def __init__(self):
        """Inicializa el rastreador de manos."""
        # Rango HSV para piel
        self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Kernel para morfología
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        
        # Detector de cara
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
    def detect_hand(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[float], Optional[Tuple[float, float]]]:
        """
        Detecta la mano en un fotograma.
        
        Args:
            frame: Fotograma BGR de OpenCV
            
        Returns:
            Tupla (landmarks, angle, position) o (None, None, None)
        """
        h, w = frame.shape[:2]
        
        # Detectar caras
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Crear máscara excluyendo caras
        face_mask = np.ones((h, w), dtype=np.uint8) * 255
        for (x, y, fw, fh) in faces:
            # Expandir región de la cara
            margin = 40
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(w, x + fw + margin)
            y2 = min(h, y + fh + margin)
            cv2.rectangle(face_mask, (x1, y1), (x2, y2), 0, -1)
        
        # Convertir a HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Detectar piel
        skin_mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
        
        # Aplicar máscara de cara
        skin_mask = cv2.bitwise_and(skin_mask, face_mask)
        
        # Limitar a mitad derecha (donde está la mano)
        roi_mask = np.zeros((h, w), dtype=np.uint8)
        roi_mask[:, w//2:] = 255
        skin_mask = cv2.bitwise_and(skin_mask, roi_mask)
        
        # Morfología
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, self.kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, self.kernel)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return None, None, None
        
        # Contorno más grande
        hand_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(hand_contour)
        
        # Filtrar por área
        if area < 5000 or area > 150000:
            return None, None, None
        
        # Calcular centro
        M = cv2.moments(hand_contour)
        if M["m00"] == 0:
            return None, None, None
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        # Verificar que esté en la mitad derecha
        if cx < w // 2:
            return None, None, None
        
        position = (cx, cy)
        
        # Calcular ángulo
        angle = self._calculate_angle(hand_contour)
        
        # Generar landmarks
        landmarks = self._generate_landmarks(hand_contour, cx, cy)
        
        return landmarks, angle, position
    
    def _calculate_angle(self, contour: np.ndarray) -> float:
        """Calcula el ángulo del contorno."""
        if len(contour) < 5:
            return 0.0
        
        ellipse = cv2.fitEllipse(contour)
        angle = ellipse[2]
        angle_rad = np.radians(angle - 90)
        
        return angle_rad
    
    def _generate_landmarks(self, contour: np.ndarray, cx: int, cy: int) -> np.ndarray:
        """Genera puntos de referencia del contorno."""
        landmarks = np.zeros((21, 3), dtype=np.float32)
        
        # Centro
        landmarks[0] = [cx, cy, 0]
        
        # Aproximar contorno
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Distribuir puntos
        num_points = min(20, len(approx))
        for i in range(num_points):
            pt = approx[i][0]
            landmarks[i+1] = [pt[0], pt[1], 0]
        
        # Rellenar faltantes
        for i in range(num_points+1, 21):
            landmarks[i] = landmarks[i-1]
        
        return landmarks
    
    def draw_landmarks(self, frame: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Dibuja los puntos de referencia."""
        if landmarks is None:
            return frame
        
        frame_copy = frame.copy()
        
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
                cv2.line(frame_copy, pt1, pt2, (0, 255, 0), 2)
        
        # Dibujar puntos
        for i, landmark in enumerate(landmarks):
            x, y = int(landmark[0]), int(landmark[1])
            if i == 0:
                cv2.circle(frame_copy, (x, y), 8, (0, 0, 255), -1)
            else:
                cv2.circle(frame_copy, (x, y), 5, (0, 255, 0), -1)
        
        return frame_copy
    
    def release(self):
        """Libera recursos."""
        pass
