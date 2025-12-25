"""
Space Pong - Physics System
Sistema de física para movimiento y rebotes
"""

import pygame
import math
from typing import Optional

from ..core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    MAX_BOUNCE_ANGLE, BALL_SPEED_INCREMENT, BALL_MAX_SPEED,
    WALL_BOUNCE_VARIATION
)
from ..entities.ball import Ball
from ..entities.ship import Ship


class PhysicsSystem:
    """
    Sistema de física que maneja movimiento y rebotes.
    """

    def __init__(self):
        """Inicializa el sistema de física"""
        pass

    def update(self, dt: float, ball: Ball, ships: list[Ship]):
        """
        Actualiza la física del juego.

        Args:
            dt: Delta time en segundos
            ball: Meteorito
            ships: Lista de naves
        """
        # Actualizar posición del meteorito
        self._update_ball_position(ball, dt)

        # Verificar colisiones con paredes
        self._handle_wall_collisions(ball)

    def _update_ball_position(self, ball: Ball, dt: float):
        """
        Actualiza la posición del meteorito.

        Args:
            ball: Meteorito
            dt: Delta time
        """
        ball.position.x += ball.velocity.x * dt
        ball.position.y += ball.velocity.y * dt

    def _handle_wall_collisions(self, ball: Ball):
        """
        Maneja colisiones del meteorito con las paredes.

        Args:
            ball: Meteorito
        """
        half_size = ball.rect.width // 2

        # Pared superior
        if ball.position.y - half_size <= 0:
            ball.position.y = half_size
            ball.velocity.y = abs(ball.velocity.y)
            self._add_bounce_variation(ball)

        # Pared inferior
        elif ball.position.y + half_size >= SCREEN_HEIGHT:
            ball.position.y = SCREEN_HEIGHT - half_size
            ball.velocity.y = -abs(ball.velocity.y)
            self._add_bounce_variation(ball)

    def _add_bounce_variation(self, ball: Ball):
        """
        Añade variación aleatoria al rebote.

        Args:
            ball: Meteorito
        """
        import random
        ball.velocity.y += random.uniform(-WALL_BOUNCE_VARIATION, WALL_BOUNCE_VARIATION)

    @staticmethod
    def bounce_off_paddle(ball: Ball, ship: Ship) -> bool:
        """
        Calcula el rebote del meteorito en una nave.

        Args:
            ball: Meteorito
            ship: Nave

        Returns:
            True si se realizó el rebote
        """
        # Calcular posición relativa de impacto (-1 a 1)
        relative_y = (ball.position.y - ship.position.y) / (ship.rect.height / 2)
        relative_y = max(-1, min(1, relative_y))

        # Calcular ángulo de rebote basado en donde golpeó la nave
        max_angle = math.radians(MAX_BOUNCE_ANGLE)
        bounce_angle = relative_y * max_angle

        # Determinar dirección horizontal
        going_right = ship.player_id == 1  # Si golpea nave izquierda, va a la derecha

        # Aumentar velocidad
        new_speed = min(ball.speed * BALL_SPEED_INCREMENT, BALL_MAX_SPEED)
        ball.speed = new_speed

        # Calcular nueva velocidad
        direction = 1 if going_right else -1
        ball.velocity.x = math.cos(bounce_angle) * new_speed * direction
        ball.velocity.y = math.sin(bounce_angle) * new_speed

        # Asegurar velocidad horizontal mínima
        min_x_speed = new_speed * 0.3
        if abs(ball.velocity.x) < min_x_speed:
            ball.velocity.x = min_x_speed * direction

        # Separar el meteorito de la nave para evitar múltiples colisiones
        if going_right:
            ball.position.x = ship.rect.right + ball.rect.width // 2 + 5
        else:
            ball.position.x = ship.rect.left - ball.rect.width // 2 - 5

        # Registrar último golpe
        ball.last_hit_by = ship.player_id

        return True

    @staticmethod
    def predict_ball_position(
        ball: Ball,
        target_x: float,
        max_iterations: int = 1000
    ) -> float:
        """
        Predice la posición Y donde llegará el meteorito a una X dada.
        Usado para la IA.

        Args:
            ball: Meteorito
            target_x: Posición X objetivo
            max_iterations: Máximo de iteraciones de simulación

        Returns:
            Posición Y predicha
        """
        # Simular movimiento
        sim_x = ball.position.x
        sim_y = ball.position.y
        sim_vx = ball.velocity.x
        sim_vy = ball.velocity.y

        # Tamaño del paso de simulación
        step = 0.016  # ~60 FPS

        # Si la pelota no va hacia el objetivo, no hay predicción válida
        if (target_x > sim_x and sim_vx <= 0) or (target_x < sim_x and sim_vx >= 0):
            return SCREEN_HEIGHT // 2

        iterations = 0
        half_size = ball.rect.width // 2

        while iterations < max_iterations:
            # Avanzar simulación
            sim_x += sim_vx * step
            sim_y += sim_vy * step

            # Simular rebotes en paredes
            if sim_y - half_size <= 0:
                sim_y = half_size
                sim_vy = abs(sim_vy)
            elif sim_y + half_size >= SCREEN_HEIGHT:
                sim_y = SCREEN_HEIGHT - half_size
                sim_vy = -abs(sim_vy)

            # Verificar si llegó al objetivo
            if (sim_vx > 0 and sim_x >= target_x) or (sim_vx < 0 and sim_x <= target_x):
                return sim_y

            iterations += 1

        # Si no se alcanzó, retornar posición actual
        return sim_y

    @staticmethod
    def calculate_collision_normal(
        ball: Ball,
        ship: Ship
    ) -> Optional[pygame.math.Vector2]:
        """
        Calcula la normal de colisión entre meteorito y nave.

        Args:
            ball: Meteorito
            ship: Nave

        Returns:
            Vector normal de la superficie de colisión, o None si no hay colisión
        """
        ball_rect = ball.get_rect()
        ship_rect = ship.get_rect()

        if not ball_rect.colliderect(ship_rect):
            return None

        # Determinar qué lado de la nave fue golpeado
        ball_center = pygame.math.Vector2(ball.position.x, ball.position.y)
        ship_center = pygame.math.Vector2(ship.position.x, ship.position.y)

        # Vector desde el centro de la nave al centro del meteorito
        to_ball = ball_center - ship_center

        # Determinar el lado de colisión
        # Para este juego, solo nos interesa izquierda/derecha
        if to_ball.x > 0:
            return pygame.math.Vector2(1, 0)  # Normal hacia la derecha
        else:
            return pygame.math.Vector2(-1, 0)  # Normal hacia la izquierda
