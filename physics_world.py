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
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Inicializa el mundo de física.
        
        Args:
            width: Ancho del mundo de física
            height: Alto del mundo de física
        """
        self.width = width
        self.height = height
        
        # Crear espacio de física
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)  # Gravedad hacia abajo
        
        # Propiedades físicas
        self.elasticity = 0.7
        self.friction = 0.5
        
        # Crear paredes
        self._create_walls()
        
        # Crear plataforma
        self.platform_body = None
        self.platform_shape = None
        self._create_platform()
        
        # Lista de bolas
        self.balls: List[Tuple[pymunk.Body, pymunk.Circle]] = []
        self.max_balls = 5
        
        # Contador de bolas capturadas
        self.balls_caught = 0
        
        # Timer para generar bolas
        self.spawn_timer = 0
        self.spawn_interval = 60  # Frames entre generaciones
        
    def _create_walls(self):
        """Crea las paredes estáticas del mundo."""
        static_body = self.space.static_body
        
        # Paredes (segmentos)
        walls = [
            pymunk.Segment(static_body, (0, 0), (0, self.height), 5),  # Izquierda
            pymunk.Segment(static_body, (self.width, 0), (self.width, self.height), 5),  # Derecha
            pymunk.Segment(static_body, (0, 0), (self.width, 0), 5),  # Piso
        ]
        
        for wall in walls:
            wall.elasticity = self.elasticity
            wall.friction = self.friction
            self.space.add(wall)
    
    def _create_platform(self):
        """Crea la plataforma controlada por el usuario."""
        # Dimensiones
        platform_width = 120
        platform_height = 15
        
        # Posición inicial
        initial_x = self.width / 2
        initial_y = self.height / 2
        
        # Cuerpo cinemático (controlado manualmente)
        self.platform_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.platform_body.position = (initial_x, initial_y)
        
        # Forma rectangular
        self.platform_shape = pymunk.Poly.create_box(
            self.platform_body,
            (platform_width, platform_height)
        )
        self.platform_shape.elasticity = 0.8
        self.platform_shape.friction = 0.8
        
        self.space.add(self.platform_body, self.platform_shape)
    
    def update_platform(self, position: Tuple[float, float], angle: float):
        """
        Actualiza la posición y rotación de la plataforma.
        
        Args:
            position: Tupla (x, y) de la nueva posición
            angle: Ángulo de rotación en radianes
        """
        if self.platform_body is None:
            return
        
        # Calcular velocidad para colisiones realistas
        old_pos = self.platform_body.position
        dt = 1/60
        velocity = (
            (position[0] - old_pos[0]) / dt,
            (position[1] - old_pos[1]) / dt
        )
        
        self.platform_body.position = position
        self.platform_body.angle = angle
        self.platform_body.velocity = velocity
    
    def spawn_ball(self) -> Optional[Tuple[pymunk.Body, pymunk.Circle]]:
        """
        Genera una nueva bola en la parte superior.
        
        Returns:
            Tupla (body, shape) de la bola creada o None
        """
        if len(self.balls) >= self.max_balls:
            return None
        
        # Posición aleatoria en la parte superior
        x = random.uniform(100, self.width - 100)
        y = self.height - 50
        
        # Radio
        radius = 15
        
        # Crear cuerpo dinámico
        mass = 2.0
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        
        # Velocidad inicial pequeña
        body.velocity = (random.uniform(-50, 50), 0)
        
        # Crear forma circular
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.7
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
        # Actualizar física
        self.space.step(dt)
        
        # Generar bolas
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_ball()
            self.spawn_timer = 0
        
        # Remover bolas que cayeron
        balls_to_remove = []
        for i, (body, shape) in enumerate(self.balls):
            if body.position.y < -100:
                balls_to_remove.append(i)
        
        for i in sorted(balls_to_remove, reverse=True):
            body, shape = self.balls[i]
            self.space.remove(body, shape)
            self.balls.pop(i)
        
        # Verificar captura
        self._check_caught_balls()
    
    def _check_caught_balls(self):
        """Verifica si hay bolas en la zona de captura."""
        # Zona de captura (parte inferior central)
        bucket_x_min = self.width * 0.35
        bucket_x_max = self.width * 0.65
        bucket_y_min = 20
        bucket_y_max = 80
        
        caught = []
        for i, (body, shape) in enumerate(self.balls):
            x, y = body.position
            if (bucket_x_min <= x <= bucket_x_max and 
                bucket_y_min <= y <= bucket_y_max):
                # Verificar que esté relativamente quieta
                if abs(body.velocity.y) < 150:
                    caught.append(i)
        
        # Remover bolas capturadas
        for i in sorted(caught, reverse=True):
            body, shape = self.balls[i]
            self.space.remove(body, shape)
            self.balls.pop(i)
            self.balls_caught += 1
    
    def get_platform_position(self) -> Tuple[float, float]:
        """Retorna la posición de la plataforma."""
        if self.platform_body is None:
            return (0, 0)
        return self.platform_body.position
    
    def get_platform_angle(self) -> float:
        """Retorna el ángulo de la plataforma."""
        if self.platform_body is None:
            return 0
        return self.platform_body.angle
    
    def get_balls(self) -> List[Tuple[pymunk.Body, pymunk.Circle]]:
        """Retorna la lista de bolas activas."""
        return self.balls
    
    def get_bucket_rect(self) -> Tuple[float, float, float, float]:
        """Retorna el rectángulo de la zona de captura (x, y, w, h)."""
        x_min = self.width * 0.35
        x_max = self.width * 0.65
        y_min = 20
        y_max = 80
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    
    def reset(self):
        """Reinicia el mundo de física."""
        # Remover todas las bolas
        for body, shape in self.balls:
            self.space.remove(body, shape)
        self.balls.clear()
        
        # Reiniciar contadores
        self.balls_caught = 0
        self.spawn_timer = 0
        
        # Reiniciar plataforma
        if self.platform_body is not None:
            self.platform_body.position = (self.width / 2, self.height / 2)
            self.platform_body.angle = 0
            self.platform_body.velocity = (0, 0)
