"""
Space Pong - Base Entity
Clase base para todas las entidades del juego
"""

import pygame
from typing import Optional


class Entity:
    """
    Clase base para todas las entidades del juego.
    Proporciona funcionalidad común de posición, sprite y renderizado.
    """

    def __init__(
        self,
        x: float,
        y: float,
        sprite: Optional[pygame.Surface] = None
    ):
        """
        Inicializa una entidad.

        Args:
            x: Posición X inicial
            y: Posición Y inicial
            sprite: Superficie de pygame para renderizar
        """
        # Posición usando Vector2 para operaciones matemáticas
        self.position = pygame.math.Vector2(x, y)

        # Velocidad
        self.velocity = pygame.math.Vector2(0, 0)

        # Sprite y rectángulo de colisión
        self.sprite = sprite
        if sprite:
            self.rect = sprite.get_rect(center=(int(x), int(y)))
        else:
            self.rect = pygame.Rect(x - 25, y - 25, 50, 50)

        # Estado
        self.active = True
        self.visible = True

    def update(self, dt: float):
        """
        Actualiza la entidad.
        Debe ser sobrescrito por subclases.

        Args:
            dt: Delta time en segundos
        """
        pass

    def render(self, screen: pygame.Surface):
        """
        Dibuja la entidad en pantalla.

        Args:
            screen: Superficie donde dibujar
        """
        if not self.visible or self.sprite is None:
            return

        # Actualizar posición del rectángulo
        self.rect.center = (int(self.position.x), int(self.position.y))

        # Dibujar sprite
        screen.blit(self.sprite, self.rect)

    def render_debug(self, screen: pygame.Surface):
        """
        Dibuja información de debug (hitbox, posición).

        Args:
            screen: Superficie donde dibujar
        """
        # Dibujar hitbox
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)

        # Dibujar centro
        pygame.draw.circle(
            screen,
            (0, 255, 0),
            (int(self.position.x), int(self.position.y)),
            3
        )

    def get_center(self) -> pygame.math.Vector2:
        """Retorna el centro de la entidad"""
        return self.position.copy()

    def get_rect(self) -> pygame.Rect:
        """Retorna el rectángulo de colisión actualizado"""
        self.rect.center = (int(self.position.x), int(self.position.y))
        return self.rect

    def set_position(self, x: float, y: float):
        """Establece la posición de la entidad"""
        self.position.x = x
        self.position.y = y
        self.rect.center = (int(x), int(y))

    def move(self, dx: float, dy: float):
        """Mueve la entidad por un delta"""
        self.position.x += dx
        self.position.y += dy

    def collides_with(self, other: 'Entity') -> bool:
        """
        Verifica colisión con otra entidad.

        Args:
            other: Otra entidad

        Returns:
            True si hay colisión
        """
        return self.get_rect().colliderect(other.get_rect())

    def collides_with_rect(self, rect: pygame.Rect) -> bool:
        """
        Verifica colisión con un rectángulo.

        Args:
            rect: Rectángulo a verificar

        Returns:
            True si hay colisión
        """
        return self.get_rect().colliderect(rect)

    def set_sprite(self, sprite: pygame.Surface):
        """
        Cambia el sprite de la entidad.

        Args:
            sprite: Nuevo sprite
        """
        self.sprite = sprite
        if sprite:
            old_center = self.rect.center
            self.rect = sprite.get_rect(center=old_center)

    def get_bounds(self) -> tuple[float, float, float, float]:
        """
        Retorna los límites de la entidad.

        Returns:
            Tupla (left, top, right, bottom)
        """
        rect = self.get_rect()
        return (rect.left, rect.top, rect.right, rect.bottom)
