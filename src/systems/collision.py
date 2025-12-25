"""
Space Pong - Collision System
Sistema de detección y manejo de colisiones
"""

import pygame
from typing import Optional, Tuple
from dataclasses import dataclass

from ..core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BALL_SIZE
from ..entities.ball import Ball
from ..entities.ship import Ship


@dataclass
class CollisionResult:
    """Resultado de una verificación de colisión"""
    collided: bool = False
    collision_type: str = ""  # 'paddle', 'wall_top', 'wall_bottom', 'goal_left', 'goal_right', 'laser'
    hit_position: float = 0.0  # Posición relativa de impacto (-1 a 1)
    entity: Optional[object] = None  # Entidad con la que colisionó


class CollisionSystem:
    """
    Sistema de detección de colisiones.
    """

    def __init__(self):
        """Inicializa el sistema de colisiones"""
        self._last_collision_frame = 0
        self._collision_cooldown = 5  # Frames mínimos entre colisiones con la misma nave

    def check_all_collisions(
        self,
        ball: Ball,
        ships: list[Ship],
        laser_rect: Optional[pygame.Rect] = None
    ) -> list[CollisionResult]:
        """
        Verifica todas las colisiones del meteorito.

        Args:
            ball: Meteorito
            ships: Lista de naves
            laser_rect: Rectángulo del láser (opcional)

        Returns:
            Lista de resultados de colisión
        """
        results = []

        # Colisiones con naves
        for ship in ships:
            result = self.check_ball_ship_collision(ball, ship)
            if result.collided:
                results.append(result)

        # Colisiones con paredes
        wall_result = self.check_ball_wall_collision(ball)
        if wall_result.collided:
            results.append(wall_result)

        # Verificar goles
        goal_result = self.check_goal(ball)
        if goal_result.collided:
            results.append(goal_result)

        # Colisiones de naves con láser
        if laser_rect:
            for ship in ships:
                laser_result = self.check_ship_laser_collision(ship, laser_rect)
                if laser_result.collided:
                    results.append(laser_result)

        return results

    def check_ball_ship_collision(self, ball: Ball, ship: Ship) -> CollisionResult:
        """
        Verifica colisión entre meteorito y nave.

        Args:
            ball: Meteorito
            ship: Nave

        Returns:
            Resultado de la colisión
        """
        result = CollisionResult()

        ball_rect = ball.get_rect()
        ship_rect = ship.get_paddle_rect()

        if not ball_rect.colliderect(ship_rect):
            return result

        # Verificar que el meteorito viene en la dirección correcta
        # (evitar colisiones cuando el meteorito ya rebotó)
        if ship.player_id == 1 and ball.velocity.x > 0:
            return result  # El meteorito ya va hacia la derecha
        if ship.player_id == 2 and ball.velocity.x < 0:
            return result  # El meteorito ya va hacia la izquierda

        # Colisión válida
        result.collided = True
        result.collision_type = 'paddle'
        result.hit_position = ship.get_relative_hit_position(ball.position.y)
        result.entity = ship

        return result

    def check_ball_wall_collision(self, ball: Ball) -> CollisionResult:
        """
        Verifica colisión del meteorito con paredes.

        Args:
            ball: Meteorito

        Returns:
            Resultado de la colisión
        """
        result = CollisionResult()
        half_size = ball.rect.width // 2

        if ball.position.y - half_size <= 0:
            result.collided = True
            result.collision_type = 'wall_top'
        elif ball.position.y + half_size >= SCREEN_HEIGHT:
            result.collided = True
            result.collision_type = 'wall_bottom'

        return result

    def check_goal(self, ball: Ball) -> CollisionResult:
        """
        Verifica si el meteorito salió por un lado (gol).

        Args:
            ball: Meteorito

        Returns:
            Resultado con el tipo de gol
        """
        result = CollisionResult()

        if ball.position.x + ball.rect.width // 2 < 0:
            result.collided = True
            result.collision_type = 'goal_left'  # Jugador 2 anota
        elif ball.position.x - ball.rect.width // 2 > SCREEN_WIDTH:
            result.collided = True
            result.collision_type = 'goal_right'  # Jugador 1 anota

        return result

    def check_ship_laser_collision(
        self,
        ship: Ship,
        laser_rect: pygame.Rect
    ) -> CollisionResult:
        """
        Verifica si una nave toca el láser.

        Args:
            ship: Nave
            laser_rect: Rectángulo del láser

        Returns:
            Resultado de la colisión
        """
        result = CollisionResult()

        ship_rect = ship.get_rect()

        if ship_rect.colliderect(laser_rect):
            result.collided = True
            result.collision_type = 'laser'
            result.entity = ship

        return result

    @staticmethod
    def get_collision_point(ball: Ball, ship: Ship) -> Tuple[float, float]:
        """
        Calcula el punto exacto de colisión.

        Args:
            ball: Meteorito
            ship: Nave

        Returns:
            Tupla (x, y) del punto de colisión
        """
        # Punto de colisión aproximado en el borde de la nave
        if ship.player_id == 1:
            x = ship.rect.right
        else:
            x = ship.rect.left

        # Y es la posición del meteorito limitada al rango de la nave
        y = max(ship.rect.top, min(ship.rect.bottom, ball.position.y))

        return (x, y)

    @staticmethod
    def circles_collide(
        x1: float, y1: float, r1: float,
        x2: float, y2: float, r2: float
    ) -> bool:
        """
        Verifica colisión entre dos círculos.

        Args:
            x1, y1: Centro del primer círculo
            r1: Radio del primer círculo
            x2, y2: Centro del segundo círculo
            r2: Radio del segundo círculo

        Returns:
            True si hay colisión
        """
        distance_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        radius_sum = r1 + r2
        return distance_sq <= radius_sum ** 2

    @staticmethod
    def point_in_rect(
        px: float, py: float,
        rect: pygame.Rect
    ) -> bool:
        """
        Verifica si un punto está dentro de un rectángulo.

        Args:
            px, py: Coordenadas del punto
            rect: Rectángulo

        Returns:
            True si el punto está dentro
        """
        return (rect.left <= px <= rect.right and
                rect.top <= py <= rect.bottom)
