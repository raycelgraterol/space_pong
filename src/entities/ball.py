"""
Space Pong - Ball (Meteorite) Entity
Representa el meteorito que actúa como pelota del juego
"""

import pygame
import math
import random
from typing import Optional

from .base_entity import Entity
from ..core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BALL_SIZE, BALL_INITIAL_SPEED, BALL_MAX_SPEED,
    BALL_SPEED_INCREMENT, MAX_BOUNCE_ANGLE, WALL_BOUNCE_VARIATION
)


class Ball(Entity):
    """
    Meteorito que rebota entre las naves.
    Implementa física de movimiento y rebotes.
    """

    def __init__(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        sprite: Optional[pygame.Surface] = None
    ):
        """
        Inicializa el meteorito.

        Args:
            x: Posición X inicial (None = centro)
            y: Posición Y inicial (None = centro)
            sprite: Sprite del meteorito
        """
        # Posición inicial en el centro
        if x is None:
            x = SCREEN_WIDTH // 2
        if y is None:
            y = SCREEN_HEIGHT // 2

        super().__init__(x, y, sprite)

        # Velocidad
        self.speed = BALL_INITIAL_SPEED
        self.max_speed = BALL_MAX_SPEED

        # Rotación visual
        self.rotation = 0
        self.rotation_speed = 180  # grados por segundo

        # Sprite original (sin rotar)
        self.original_sprite = sprite

        # Estado
        self.is_active = True
        self.last_hit_by = None  # 1 o 2 (jugador)

        # Si no hay sprite, crear placeholder
        if self.sprite is None:
            self._create_placeholder_sprite()
            self.original_sprite = self.sprite.copy()

        # Iniciar con dirección aleatoria
        self._set_random_direction()

    def _create_placeholder_sprite(self):
        """Crea un sprite placeholder del meteorito"""
        size = BALL_SIZE
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)

        center = size // 2

        # Cuerpo del meteorito
        pygame.draw.circle(
            self.sprite,
            (139, 69, 19),  # Marrón
            (center, center),
            center - 5
        )
        pygame.draw.circle(
            self.sprite,
            (160, 82, 45),  # Marrón claro
            (center, center),
            center - 10
        )

        # Efecto de fuego
        for i in range(8):
            angle = i * 45
            fx = center + int(math.cos(math.radians(angle)) * (center - 5))
            fy = center + int(math.sin(math.radians(angle)) * (center - 5))
            pygame.draw.circle(self.sprite, (255, 100, 0), (fx, fy), 4)

        self.rect = self.sprite.get_rect(center=(int(self.position.x), int(self.position.y)))

    def _set_random_direction(self):
        """Establece una dirección inicial aleatoria"""
        # Ángulo aleatorio entre -45 y 45 grados
        angle = random.uniform(-math.pi / 4, math.pi / 4)

        # Dirección horizontal aleatoria
        direction = random.choice([-1, 1])

        self.velocity.x = math.cos(angle) * self.speed * direction
        self.velocity.y = math.sin(angle) * self.speed

    def update(self, dt: float):
        """
        Actualiza el meteorito.

        Args:
            dt: Delta time en segundos
        """
        if not self.is_active:
            return

        # Actualizar posición
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt

        # Actualizar rotación visual
        # Rotar en la dirección del movimiento
        rotation_dir = 1 if self.velocity.x > 0 else -1
        self.rotation += self.rotation_speed * dt * rotation_dir
        self.rotation %= 360

        # Actualizar sprite rotado
        self._update_rotated_sprite()

        # Actualizar rect
        self.rect.center = (int(self.position.x), int(self.position.y))

        # Verificar colisiones con paredes (arriba/abajo)
        self._check_wall_collision()

    def _update_rotated_sprite(self):
        """Actualiza el sprite con la rotación actual"""
        if self.original_sprite:
            self.sprite = pygame.transform.rotate(self.original_sprite, -self.rotation)
            # Mantener el centro
            old_center = self.rect.center
            self.rect = self.sprite.get_rect(center=old_center)

    def _check_wall_collision(self):
        """Verifica y maneja colisiones con paredes superior/inferior"""
        half_size = BALL_SIZE // 2

        # Pared superior
        if self.position.y - half_size <= 0:
            self.position.y = half_size
            self.velocity.y = abs(self.velocity.y)
            # Pequeña variación aleatoria
            self.velocity.y += random.uniform(-WALL_BOUNCE_VARIATION, WALL_BOUNCE_VARIATION)

        # Pared inferior
        elif self.position.y + half_size >= SCREEN_HEIGHT:
            self.position.y = SCREEN_HEIGHT - half_size
            self.velocity.y = -abs(self.velocity.y)
            # Pequeña variación aleatoria
            self.velocity.y += random.uniform(-WALL_BOUNCE_VARIATION, WALL_BOUNCE_VARIATION)

    def bounce_off_paddle(self, paddle_center_y: float, paddle_height: float, going_right: bool):
        """
        Rebota el meteorito en una nave.

        Args:
            paddle_center_y: Centro Y de la nave
            paddle_height: Altura de la nave
            going_right: Si debe ir hacia la derecha después del rebote
        """
        # Calcular posición relativa de impacto (-1 a 1)
        relative_y = (self.position.y - paddle_center_y) / (paddle_height / 2)
        relative_y = max(-1, min(1, relative_y))

        # Calcular ángulo de rebote
        max_angle = math.radians(MAX_BOUNCE_ANGLE)
        bounce_angle = relative_y * max_angle

        # Aumentar velocidad
        self.speed = min(self.speed * BALL_SPEED_INCREMENT, self.max_speed)

        # Calcular nueva velocidad
        direction = 1 if going_right else -1
        self.velocity.x = math.cos(bounce_angle) * self.speed * direction
        self.velocity.y = math.sin(bounce_angle) * self.speed

        # Asegurar velocidad horizontal mínima para evitar rebotes verticales infinitos
        min_x_speed = self.speed * 0.3
        if abs(self.velocity.x) < min_x_speed:
            self.velocity.x = min_x_speed * direction

    def bounce_horizontal(self):
        """Rebota horizontalmente (invierte dirección X)"""
        self.velocity.x *= -1

    def bounce_vertical(self):
        """Rebota verticalmente (invierte dirección Y)"""
        self.velocity.y *= -1

    def reset(self, towards_player: Optional[int] = None):
        """
        Reinicia el meteorito al centro.

        Args:
            towards_player: 1 o 2 para dirigir hacia ese jugador, None para aleatorio
        """
        self.position.x = SCREEN_WIDTH // 2
        self.position.y = SCREEN_HEIGHT // 2
        self.speed = BALL_INITIAL_SPEED
        self.rotation = 0
        self.is_active = True
        self.last_hit_by = None

        # Establecer dirección
        if towards_player is None:
            self._set_random_direction()
        else:
            angle = random.uniform(-math.pi / 4, math.pi / 4)
            direction = -1 if towards_player == 1 else 1
            self.velocity.x = math.cos(angle) * self.speed * direction
            self.velocity.y = math.sin(angle) * self.speed

    def is_out_left(self) -> bool:
        """Verifica si salió por la izquierda"""
        return self.position.x + BALL_SIZE < 0

    def is_out_right(self) -> bool:
        """Verifica si salió por la derecha"""
        return self.position.x - BALL_SIZE > SCREEN_WIDTH

    def is_out_of_bounds(self) -> tuple[bool, int]:
        """
        Verifica si salió de los límites.

        Returns:
            Tupla (salió, jugador_que_anota)
            jugador_que_anota: 1 si salió derecha, 2 si salió izquierda
        """
        if self.is_out_left():
            return True, 2  # Jugador 2 anota
        elif self.is_out_right():
            return True, 1  # Jugador 1 anota
        return False, 0

    def get_direction(self) -> int:
        """
        Retorna la dirección horizontal del movimiento.

        Returns:
            -1 (izquierda), 0 (sin movimiento), 1 (derecha)
        """
        if self.velocity.x < 0:
            return -1
        elif self.velocity.x > 0:
            return 1
        return 0

    def set_speed(self, speed: float):
        """
        Establece la velocidad manteniendo la dirección.

        Args:
            speed: Nueva velocidad
        """
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * speed
        self.speed = speed

    def render(self, screen: pygame.Surface):
        """Renderiza el meteorito"""
        if not self.visible or self.sprite is None:
            return

        # Dibujar sprite rotado
        screen.blit(self.sprite, self.rect)

    def render_with_trail(self, screen: pygame.Surface, trail_length: int = 5):
        """
        Renderiza el meteorito con efecto de estela.

        Args:
            screen: Superficie donde dibujar
            trail_length: Longitud de la estela
        """
        # Dibujar estela
        if self.velocity.length() > 0:
            trail_dir = -self.velocity.normalize()
            for i in range(trail_length):
                alpha = int(150 * (1 - i / trail_length))
                size = int(BALL_SIZE * (1 - i * 0.15))

                trail_pos = (
                    int(self.position.x + trail_dir.x * i * 8),
                    int(self.position.y + trail_dir.y * i * 8)
                )

                trail_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(
                    trail_surface,
                    (255, 150, 50, alpha),
                    (size // 2, size // 2),
                    size // 2
                )
                screen.blit(
                    trail_surface,
                    (trail_pos[0] - size // 2, trail_pos[1] - size // 2)
                )

        # Dibujar meteorito
        self.render(screen)

    def __str__(self) -> str:
        return f"Ball(pos=({self.position.x:.0f}, {self.position.y:.0f}), vel=({self.velocity.x:.0f}, {self.velocity.y:.0f}))"
