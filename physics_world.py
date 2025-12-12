"""
Módulo para el mundo de física usando Pymunk.

Este módulo proporciona la clase PhysicsWorld que gestiona:
- Espacios de física 2D
- Objetos dinámicos (bolas)
- Paredes estáticas
- Plataforma controlada por el usuario
- Simulación de gravedad, colisiones y fricción
"""

import pymunk
import numpy as np
from typing import List, Tuple, Optional
import random


class PhysicsWorld:
    """
    Clase que gestiona el mundo de física 2D con Pymunk.
    
    Maneja:
    - Espacio de física con gravedad
    - Objetos dinámicos (bolas)
    - Paredes estáticas
    - Plataforma controlada por el usuario
    - Zona de captura (bucket)
    """
    
    def __init__(self, width: int = 800, height: int = 600, gravity: float = -9.81):
        """
        Inicializa el mundo de física.
        
        Args:
            width: Ancho del mundo de física
            height: Alto del mundo de física
            gravity: Aceleración de gravedad (negativa = hacia abajo)
        """
        self.width = width
        self.height = height
        self.space = pymunk.Space()
        self.space.gravity = (0, gravity)
        
        # Elasticidad y fricción
        self.elasticity = 0.7
        self.friction = 0.5
        
        # Crear paredes estáticas
        self._create_walls()
        
        # Plataforma controlada por el usuario
        self.platform = None
        self.platform_body = None
        self.platform_shape = None
        self._create_platform()
        
        # Zona de captura (bucket)
        # Definida por coordenadas, no por objeto Rect
        
        # Lista de bolas
        self.balls: List[Tuple[pymunk.Body, pymunk.Circle]] = []
        self.max_balls = 5
        
        # Contador de bolas capturadas
        self.balls_caught = 0
        
        # Tiempo para generar nuevas bolas
        self.spawn_timer = 0
        self.spawn_interval = 60  # Frames entre generaciones
        
    def _create_walls(self):
        """Crea las paredes estáticas del mundo."""
        # Pared izquierda
        left_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        left_shape = pymunk.Segment(left_body, (0, 0), (0, self.height), 5)
        left_shape.elasticity = self.elasticity
        left_shape.friction = self.friction
        self.space.add(left_body, left_shape)
        
        # Pared derecha
        right_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        right_shape = pymunk.Segment(right_body, (self.width, 0), (self.width, self.height), 5)
        right_shape.elasticity = self.elasticity
        right_shape.friction = self.friction
        self.space.add(right_body, right_shape)
        
        # Piso
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, (0, 0), (self.width, 0), 5)
        floor_shape.elasticity = self.elasticity
        floor_shape.friction = self.friction
        self.space.add(floor_body, floor_shape)
    
    def _create_platform(self):
        """Crea la plataforma controlada por el usuario."""
        # Dimensiones de la plataforma
        platform_width = 100
        platform_height = 15
        
        # Posición inicial (centro)
        initial_x = self.width / 2
        initial_y = self.height / 2
        
        # Cuerpo dinámico
        moment = pymunk.moment_for_box(1.0, (platform_width, platform_height))
        self.platform_body = pymunk.Body(1.0, moment)
        self.platform_body.position = (initial_x, initial_y)
        
        # Forma (rectángulo)
        self.platform_shape = pymunk.Poly.create_box(self.platform_body, (platform_width, platform_height))
        self.platform_shape.elasticity = 0.9
        self.platform_shape.friction = 0.8
        
        self.space.add(self.platform_body, self.platform_shape)
    
    def update_platform(self, position: Tuple[float, float], angle: float, dt: float = 1/60):
        """
        Actualiza la posición y rotación de la plataforma.
        
        Args:
            position: Tupla (x, y) de la nueva posición
            angle: Ángulo de rotación en radianes
            dt: Delta de tiempo
        """
        if self.platform_body is None:
            return
        
        # Actualizar posición
        self.platform_body.position = position
        
        # Actualizar rotación
        self.platform_body.angle = angle
    
    def spawn_ball(self) -> Optional[Tuple[pymunk.Body, pymunk.Circle]]:
        """
        Genera una nueva bola en la parte superior del mundo.
        
        Returns:
            Tupla (body, shape) de la bola creada o None si se alcanzó el máximo
        """
        if len(self.balls) >= self.max_balls:
            return None
        
        # Posición aleatoria en la parte superior
        x = random.uniform(50, self.width - 50)
        y = self.height - 30
        
        # Radio de la bola
        radius = 10
        
        # Crear cuerpo
        mass = 1.0
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        
        # Velocidad inicial aleatoria
        body.velocity = (random.uniform(-50, 50), random.uniform(-20, 0))
        
        # Crear forma
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.8
        shape.friction = 0.5
        
        # Agregar al espacio
        self.space.add(body, shape)
        self.balls.append((body, shape))
        
        return (body, shape)
    
    def update(self, dt: float = 1/60):
        """
        Actualiza la simulación de física.
        
        Args:
            dt: Delta de tiempo
        """
        # Actualizar espacio de física
        self.space.step(dt)
        
        # Actualizar timer de generación
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_ball()
            self.spawn_timer = 0
        
        # Remover bolas que cayeron
        self.balls = [
            (body, shape) for body, shape in self.balls 
            if body.position.y > -50
        ]
        
        # Verificar bolas en la zona de captura
        self._check_caught_balls()
    
    def _check_caught_balls(self):
        """Verifica si hay bolas en la zona de captura."""
        bucket_x_min = self.width * 0.35
        bucket_x_max = self.width * 0.65
        bucket_y_max = 50
        
        caught = []
        for i, (body, shape) in enumerate(self.balls):
            x, y = body.position
            if bucket_x_min <= x <= bucket_x_max and y <= bucket_y_max:
                caught.append(i)
        
        # Remover bolas capturadas (en orden inverso para no afectar índices)
        for i in sorted(caught, reverse=True):
            body, shape = self.balls[i]
            self.space.remove(body, shape)
            self.balls.pop(i)
            self.balls_caught += 1
    
    def get_platform_position(self) -> Tuple[float, float]:
        """Retorna la posición actual de la plataforma."""
        if self.platform_body is None:
            return (0, 0)
        return self.platform_body.position
    
    def get_platform_angle(self) -> float:
        """Retorna el ángulo actual de la plataforma."""
        if self.platform_body is None:
            return 0
        return self.platform_body.angle
    
    def get_balls(self) -> List[Tuple[pymunk.Body, pymunk.Circle]]:
        """Retorna la lista de bolas activas."""
        return self.balls
    
    def get_shapes(self) -> List:
        """Retorna todas las formas en el espacio de física."""
        return self.space.shapes
    
    def get_bucket_rect(self) -> Tuple[float, float, float, float]:
        """Retorna el rectángulo de la zona de captura."""
        x_min = self.width * 0.35
        x_max = self.width * 0.65
        return (x_min, 0, x_max - x_min, 50)
    
    def reset(self):
        """Reinicia el mundo de física."""
        # Remover todas las bolas
        for body, shape in self.balls:
            self.space.remove(body, shape)
        self.balls.clear()
        
        # Reiniciar contador
        self.balls_caught = 0
        self.spawn_timer = 0
        
        # Reiniciar posición de la plataforma
        if self.platform_body is not None:
            self.platform_body.position = (self.width / 2, self.height / 2)
            self.platform_body.angle = 0
            self.platform_body.velocity = (0, 0)
            self.platform_body.angular_velocity = 0
