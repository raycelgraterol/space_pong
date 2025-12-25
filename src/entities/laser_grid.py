"""
Space Pong - Laser Grid Entity
Representa la malla láser central que divide el campo
"""

import pygame
import math
from typing import Optional

from .base_entity import Entity
from ..core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    LASER_GRID_WIDTH, LASER_GRID_HEIGHT,
    LASER_RED, LASER_GLOW
)


class LaserGrid(Entity):
    """
    Malla láser central que divide el campo de juego.
    Las naves no pueden tocarla sin penalización.
    """

    def __init__(self, sprite: Optional[pygame.Surface] = None):
        """
        Inicializa la malla láser.

        Args:
            sprite: Sprite del láser (opcional)
        """
        # Posición central
        x = SCREEN_WIDTH // 2
        y = SCREEN_HEIGHT // 2

        super().__init__(x, y, sprite)

        # Dimensiones
        self.width = LASER_GRID_WIDTH
        self.height = LASER_GRID_HEIGHT

        # Animación
        self.animation_time = 0
        self.pulse_speed = 2.0  # Velocidad del pulso
        self.glow_intensity = 1.0

        # Colores
        self.base_color = LASER_RED
        self.glow_color = LASER_GLOW

        # Crear sprite si no se proporcionó
        if self.sprite is None:
            self._create_sprite()

        # Actualizar rect para colisiones
        self.rect = pygame.Rect(
            x - self.width // 2,
            0,
            self.width,
            SCREEN_HEIGHT
        )

        # Zona de peligro (más amplia que el láser visual)
        self.danger_zone = pygame.Rect(
            x - self.width - 10,
            0,
            self.width * 2 + 20,
            SCREEN_HEIGHT
        )

    def _create_sprite(self):
        """Crea el sprite del láser con efecto de glow"""
        # Superficie con alpha
        self.sprite = pygame.Surface(
            (self.width * 3, SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        center_x = self.width * 3 // 2

        # Glow exterior
        for i in range(5, 0, -1):
            alpha = int(50 * (1 - i / 6))
            glow_width = self.width + i * 4
            pygame.draw.rect(
                self.sprite,
                (*self.glow_color[:3], alpha),
                (center_x - glow_width // 2, 0, glow_width, SCREEN_HEIGHT)
            )

        # Línea central brillante
        pygame.draw.rect(
            self.sprite,
            self.base_color,
            (center_x - self.width // 2, 0, self.width, SCREEN_HEIGHT)
        )

        # Núcleo más brillante
        pygame.draw.rect(
            self.sprite,
            (255, 200, 200),
            (center_x - 1, 0, 2, SCREEN_HEIGHT)
        )

        # Segmentos horizontales decorativos
        for y in range(0, SCREEN_HEIGHT, 30):
            pygame.draw.line(
                self.sprite,
                (255, 150, 150, 200),
                (center_x - self.width, y),
                (center_x + self.width, y),
                1
            )

        # Actualizar rect del sprite
        self.rect = self.sprite.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def update(self, dt: float):
        """
        Actualiza la animación del láser.

        Args:
            dt: Delta time en segundos
        """
        # Actualizar tiempo de animación
        self.animation_time += dt

        # Calcular intensidad del pulso
        self.glow_intensity = 0.7 + 0.3 * math.sin(self.animation_time * self.pulse_speed * math.pi)

    def render(self, screen: pygame.Surface):
        """
        Renderiza el láser con efectos.

        Args:
            screen: Superficie donde dibujar
        """
        if not self.visible:
            return

        # Crear versión con intensidad variable del sprite
        if self.sprite:
            # Aplicar alpha basado en intensidad
            temp_surface = self.sprite.copy()
            temp_surface.set_alpha(int(255 * self.glow_intensity))
            screen.blit(temp_surface, self.rect)

            # Efecto de partículas en el láser
            self._render_particles(screen)

    def _render_particles(self, screen: pygame.Surface):
        """
        Renderiza partículas de energía en el láser.

        Args:
            screen: Superficie donde dibujar
        """
        import random

        center_x = SCREEN_WIDTH // 2

        # Semilla basada en tiempo para movimiento consistente
        random.seed(int(self.animation_time * 10))

        for i in range(10):
            # Posición Y que se mueve con el tiempo
            base_y = (i * SCREEN_HEIGHT // 10 + int(self.animation_time * 100)) % SCREEN_HEIGHT
            offset_x = random.randint(-5, 5)

            # Tamaño y alpha variable
            size = random.randint(2, 4)
            alpha = int(150 + 100 * self.glow_intensity)

            # Dibujar partícula
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface,
                (255, 200, 200, alpha),
                (size, size),
                size
            )
            screen.blit(
                particle_surface,
                (center_x + offset_x - size, base_y - size)
            )

    def render_simple(self, screen: pygame.Surface):
        """
        Renderiza una versión simple del láser (para mejor rendimiento).

        Args:
            screen: Superficie donde dibujar
        """
        center_x = SCREEN_WIDTH // 2

        # Glow
        glow_alpha = int(100 * self.glow_intensity)
        glow_surface = pygame.Surface((self.width * 3, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(
            glow_surface,
            (*self.glow_color[:3], glow_alpha),
            (self.width, 0, self.width, SCREEN_HEIGHT)
        )
        screen.blit(glow_surface, (center_x - self.width * 3 // 2, 0))

        # Línea central
        pygame.draw.rect(
            screen,
            self.base_color,
            (center_x - self.width // 2, 0, self.width, SCREEN_HEIGHT)
        )

    def get_collision_rect(self) -> pygame.Rect:
        """
        Retorna el rectángulo de colisión del láser.

        Returns:
            Rectángulo para detección de colisiones
        """
        return pygame.Rect(
            SCREEN_WIDTH // 2 - self.width // 2,
            0,
            self.width,
            SCREEN_HEIGHT
        )

    def get_danger_zone(self) -> pygame.Rect:
        """
        Retorna la zona de peligro (más amplia para advertencias).

        Returns:
            Rectángulo de la zona de peligro
        """
        return self.danger_zone

    def is_ship_in_danger(self, ship_rect: pygame.Rect) -> bool:
        """
        Verifica si una nave está en la zona de peligro.

        Args:
            ship_rect: Rectángulo de la nave

        Returns:
            True si está en peligro
        """
        return self.danger_zone.colliderect(ship_rect)

    def check_collision(self, ship_rect: pygame.Rect) -> bool:
        """
        Verifica si una nave toca el láser.

        Args:
            ship_rect: Rectángulo de la nave

        Returns:
            True si hay colisión
        """
        return self.get_collision_rect().colliderect(ship_rect)
