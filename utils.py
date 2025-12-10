"""
Módulo de utilidades para conversiones y funciones auxiliares.

Proporciona funciones para convertir coordenadas de MediaPipe a Pymunk
y otras operaciones auxiliares.
"""

import numpy as np
from typing import Tuple


def mediapipe_to_pymunk(
    x: float, 
    y: float, 
    frame_width: int, 
    frame_height: int, 
    physics_width: int, 
    physics_height: int
) -> Tuple[float, float]:
    """
    Convierte coordenadas de MediaPipe a coordenadas de Pymunk.
    
    MediaPipe devuelve coordenadas normalizadas (0-1) con origen en arriba-izquierda.
    Pymunk usa coordenadas en píxeles con origen en abajo-izquierda.
    
    Args:
        x: Coordenada x en píxeles (MediaPipe)
        y: Coordenada y en píxeles (MediaPipe)
        frame_width: Ancho del fotograma
        frame_height: Alto del fotograma
        physics_width: Ancho del mundo de física
        physics_height: Alto del mundo de física
        
    Returns:
        Tupla (x_pymunk, y_pymunk) en coordenadas de Pymunk
    """
    # Escalar a las dimensiones del mundo de física
    pymunk_x = (x / frame_width) * physics_width
    # Invertir eje Y (MediaPipe: arriba=0, Pymunk: abajo=0)
    pymunk_y = physics_height - (y / frame_height) * physics_height
    
    return pymunk_x, pymunk_y


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Limita un valor entre un mínimo y máximo.
    
    Args:
        value: Valor a limitar
        min_val: Valor mínimo
        max_val: Valor máximo
        
    Returns:
        Valor limitado
    """
    return max(min_val, min(max_val, value))


def normalize_angle(angle: float) -> float:
    """
    Normaliza un ángulo al rango [-π, π].
    
    Args:
        angle: Ángulo en radianes
        
    Returns:
        Ángulo normalizado
    """
    while angle > np.pi:
        angle -= 2 * np.pi
    while angle < -np.pi:
        angle += 2 * np.pi
    return angle


def smooth_value(current: float, target: float, factor: float = 0.1) -> float:
    """
    Suaviza un valor usando interpolación lineal.
    
    Args:
        current: Valor actual
        target: Valor objetivo
        factor: Factor de suavizado (0-1)
        
    Returns:
        Valor suavizado
    """
    return current + (target - current) * factor


def distance_2d(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calcula la distancia euclidiana entre dos puntos en 2D.
    
    Args:
        p1: Primer punto (x, y)
        p2: Segundo punto (x, y)
        
    Returns:
        Distancia euclidiana
    """
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def get_hand_center(landmarks: np.ndarray) -> Tuple[float, float]:
    """
    Calcula el centro de la mano a partir de los puntos de referencia.
    
    Args:
        landmarks: Array de 21 puntos de referencia
        
    Returns:
        Tupla (x, y) del centro de la mano
    """
    center_x = np.mean(landmarks[:, 0])
    center_y = np.mean(landmarks[:, 1])
    return center_x, center_y


def angle_difference(angle1: float, angle2: float) -> float:
    """
    Calcula la diferencia mínima entre dos ángulos.
    
    Args:
        angle1: Primer ángulo en radianes
        angle2: Segundo ángulo en radianes
        
    Returns:
        Diferencia de ángulo en radianes
    """
    diff = angle1 - angle2
    while diff > np.pi:
        diff -= 2 * np.pi
    while diff < -np.pi:
        diff += 2 * np.pi
    return diff
