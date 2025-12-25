"""
Space Pong - Ship Entity
Representa las naves de los jugadores
"""

import pygame
from typing import Optional

from .base_entity import Entity
from ..core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SHIP_WIDTH, SHIP_HEIGHT, SHIP_SPEED,
    SHIP_MARGIN, SHIP_P1_X, SHIP_P2_X,
    LASER_GRID_WIDTH
)


class Ship(Entity):
    """
    Nave espacial controlada por un jugador o la IA.
    Se mueve verticalmente y rebota el meteorito.
    """

    def __init__(
        self,
        player_id: int,
        sprite: Optional[pygame.Surface] = None,
        is_bot: bool = False
    ):
        """
        Inicializa una nave.

        Args:
            player_id: 1 para jugador izquierdo, 2 para jugador derecho
            sprite: Sprite de la nave
            is_bot: Si es controlado por IA
        """
        # Determinar posición inicial según el jugador
        if player_id == 1:
            x = SHIP_P1_X + SHIP_WIDTH // 2
        else:
            x = SHIP_P2_X + SHIP_WIDTH // 2

        y = SCREEN_HEIGHT // 2

        super().__init__(x, y, sprite)

        # Atributos de jugador
        self.player_id = player_id
        self.is_bot = is_bot

        # Puntuación
        self.score = 0

        # Movimiento
        self.speed = SHIP_SPEED
        self.move_direction = 0  # -1 arriba, 0 quieto, 1 abajo

        # Límites de movimiento vertical
        self.min_y = SHIP_HEIGHT // 2 + 10
        self.max_y = SCREEN_HEIGHT - SHIP_HEIGHT // 2 - 10

        # Límites horizontales (para evitar tocar el láser)
        self._calculate_horizontal_limits()

        # Si no hay sprite, crear placeholder
        if self.sprite is None:
            self._create_placeholder_sprite()

    def _calculate_horizontal_limits(self):
        """Calcula los límites horizontales de movimiento"""
        center_x = SCREEN_WIDTH // 2
        laser_half = LASER_GRID_WIDTH // 2

        if self.player_id == 1:
            # Jugador 1: desde el borde izquierdo hasta antes del láser
            self.min_x = SHIP_MARGIN + SHIP_WIDTH // 2
            self.max_x = center_x - laser_half - SHIP_WIDTH // 2 - 10
        else:
            # Jugador 2: desde después del láser hasta el borde derecho
            self.min_x = center_x + laser_half + SHIP_WIDTH // 2 + 10
            self.max_x = SCREEN_WIDTH - SHIP_MARGIN - SHIP_WIDTH // 2

    def _create_placeholder_sprite(self):
        """Crea un sprite placeholder si no se proporcionó uno"""
        self.sprite = pygame.Surface((SHIP_WIDTH, SHIP_HEIGHT), pygame.SRCALPHA)

        # Color según jugador
        color = (100, 150, 255) if self.player_id == 1 else (100, 255, 150)

        # Dibujar forma de nave
        pygame.draw.ellipse(
            self.sprite,
            color,
            (5, 5, SHIP_WIDTH - 10, SHIP_HEIGHT - 10)
        )
        pygame.draw.ellipse(
            self.sprite,
            (255, 255, 255),
            (10, 10, SHIP_WIDTH - 20, SHIP_HEIGHT - 20),
            2
        )

        # Actualizar rect
        self.rect = self.sprite.get_rect(center=(int(self.position.x), int(self.position.y)))

    def update(self, dt: float):
        """
        Actualiza la nave.

        Args:
            dt: Delta time en segundos
        """
        if not self.active:
            return

        # Aplicar movimiento vertical
        if self.move_direction != 0:
            self.velocity.y = self.move_direction * self.speed
        else:
            self.velocity.y = 0

        # Actualizar posición
        new_y = self.position.y + self.velocity.y * dt

        # Limitar a los bordes de la pantalla
        new_y = max(self.min_y, min(self.max_y, new_y))

        self.position.y = new_y

        # Actualizar rect
        self.rect.center = (int(self.position.x), int(self.position.y))

    def move_up(self):
        """Comienza a mover hacia arriba"""
        self.move_direction = -1

    def move_down(self):
        """Comienza a mover hacia abajo"""
        self.move_direction = 1

    def stop(self):
        """Detiene el movimiento"""
        self.move_direction = 0

    def set_movement(self, direction: int):
        """
        Establece la dirección de movimiento.

        Args:
            direction: -1 (arriba), 0 (quieto), 1 (abajo)
        """
        self.move_direction = max(-1, min(1, direction))

    def reset_position(self):
        """Vuelve a la posición inicial"""
        if self.player_id == 1:
            x = SHIP_P1_X + SHIP_WIDTH // 2
        else:
            x = SHIP_P2_X + SHIP_WIDTH // 2

        self.position.x = x
        self.position.y = SCREEN_HEIGHT // 2
        self.velocity.y = 0
        self.move_direction = 0

    def add_score(self, points: int = 1):
        """
        Añade puntos al marcador.

        Args:
            points: Puntos a añadir
        """
        self.score += points

    def reset_score(self):
        """Reinicia el marcador"""
        self.score = 0

    def get_paddle_rect(self) -> pygame.Rect:
        """
        Retorna el rectángulo de colisión para rebotes.
        Puede ser diferente del rect visual.
        """
        # Usar un rect ligeramente más pequeño para colisiones más precisas
        padding = 5
        return pygame.Rect(
            self.rect.x + padding,
            self.rect.y + padding,
            self.rect.width - padding * 2,
            self.rect.height - padding * 2
        )

    def get_relative_hit_position(self, ball_y: float) -> float:
        """
        Calcula la posición relativa de impacto del meteorito.

        Args:
            ball_y: Posición Y del meteorito

        Returns:
            Valor entre -1 (arriba) y 1 (abajo)
        """
        relative = (ball_y - self.position.y) / (self.rect.height / 2)
        return max(-1, min(1, relative))

    def is_touching_laser_zone(self) -> bool:
        """
        Verifica si la nave está en la zona del láser.

        Returns:
            True si está muy cerca del centro
        """
        center_x = SCREEN_WIDTH // 2
        distance_to_center = abs(self.position.x - center_x)
        danger_zone = LASER_GRID_WIDTH + SHIP_WIDTH // 2 + 20

        return distance_to_center < danger_zone

    def render(self, screen: pygame.Surface):
        """Renderiza la nave"""
        super().render(screen)

    def render_with_effects(self, screen: pygame.Surface):
        """Renderiza la nave con efectos visuales"""
        super().render(screen)

        # Efecto de glow si está cerca del láser
        if self.is_touching_laser_zone():
            glow = pygame.Surface(
                (self.rect.width + 20, self.rect.height + 20),
                pygame.SRCALPHA
            )
            pygame.draw.ellipse(
                glow,
                (255, 0, 0, 50),
                glow.get_rect()
            )
            screen.blit(
                glow,
                (self.rect.x - 10, self.rect.y - 10)
            )

    def __str__(self) -> str:
        return f"Ship(P{self.player_id}, score={self.score}, pos=({self.position.x:.0f}, {self.position.y:.0f}))"
