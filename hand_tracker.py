"""
Módulo para el seguimiento de manos usando MediaPipe.

Este módulo proporciona la clase HandTracker que utiliza MediaPipe Hands
para detectar la posición y orientación de la mano en tiempo real.
"""

import mediapipe as mp
import numpy as np
import cv2
from typing import Tuple, Optional


class HandTracker:
    """
    Clase para rastrear la mano usando MediaPipe Hands.
    
    Detecta 21 puntos de referencia en la mano y calcula:
    - Posición (x, y) del centro de la palma
    - Ángulo de rotación (orientación) de la mano
    """
    
    def __init__(self, max_num_hands: int = 1, min_detection_confidence: float = 0.5):
        """
        Inicializa el rastreador de manos.
        
        Args:
            max_num_hands: Número máximo de manos a detectar
            min_detection_confidence: Confianza mínima para la detección
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def detect_hand(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[float], Optional[Tuple[float, float]]]:
        """
        Detecta la mano en un fotograma.
        
        Args:
            frame: Fotograma de OpenCV (BGR)
            
        Returns:
            Tupla con:
            - landmarks: Array de 21 puntos (x, y, z) o None si no hay mano
            - angle: Ángulo de rotación de la mano en radianes o None
            - position: Tupla (x, y) del centro de la palma o None
        """
        # Convertir BGR a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
            landmarks = results.multi_hand_landmarks[0]
            
            # Convertir landmarks a array numpy
            h, w, c = frame.shape
            landmarks_array = np.array([
                [lm.x * w, lm.y * h, lm.z] for lm in landmarks.landmark
            ])
            
            # Calcular posición (centro de la palma)
            # Usamos la muñeca (punto 0) como referencia
            wrist = landmarks_array[0]
            position = (wrist[0], wrist[1])
            
            # Calcular ángulo de rotación
            angle = self._calculate_hand_angle(landmarks_array)
            
            return landmarks_array, angle, position
        
        return None, None, None
    
    def _calculate_hand_angle(self, landmarks: np.ndarray) -> float:
        """
        Calcula el ángulo de rotación de la mano.
        
        Utiliza los puntos de la muñeca (0) y el dedo medio (9) para
        determinar la orientación de la mano en el plano 2D.
        
        Matemática:
        - Vector desde muñeca hasta dedo medio: v = (x9 - x0, y9 - y0)
        - Ángulo = arctan2(v_y, v_x)
        - Rango: [-π, π] radianes
        
        Args:
            landmarks: Array de 21 puntos de referencia
            
        Returns:
            Ángulo en radianes
        """
        # Punto 0: Muñeca (WRIST)
        # Punto 9: Articulación MCP del dedo medio (MIDDLE_FINGER_MCP)
        wrist = landmarks[0]
        middle_mcp = landmarks[9]
        
        # Vector desde muñeca hasta dedo medio
        vector = middle_mcp[:2] - wrist[:2]
        
        # Calcular ángulo usando arctan2
        angle = np.arctan2(vector[1], vector[0])
        
        return angle
    
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
        
        # Dibujar puntos
        for i, landmark in enumerate(landmarks):
            x, y = int(landmark[0]), int(landmark[1])
            cv2.circle(frame_copy, (x, y), 3, (0, 255, 0), -1)
            cv2.putText(frame_copy, str(i), (x + 5, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        # Dibujar conexiones principales
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Pulgar
            (0, 5), (5, 6), (6, 7), (7, 8),  # Índice
            (0, 9), (9, 10), (10, 11), (11, 12),  # Dedo medio
            (0, 13), (13, 14), (14, 15), (15, 16),  # Anular
            (0, 17), (17, 18), (18, 19), (19, 20)  # Meñique
        ]
        
        for start, end in connections:
            pt1 = tuple(landmarks[start][:2].astype(int))
            pt2 = tuple(landmarks[end][:2].astype(int))
            cv2.line(frame_copy, pt1, pt2, (0, 255, 0), 2)
        
        return frame_copy
    
    def release(self):
        """Libera los recursos de MediaPipe."""
        self.hands.close()
