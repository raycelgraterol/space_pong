"""
Space Pong - Scoreboard UI
Muestra la puntuación de los jugadores
"""

import pygame
from typing import Optional

from ..core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    UI_PRIMARY, UI_TEXT, WINNING_SCORE
)


class Scoreboard:
    """
    Muestra y gestiona la visualización de la puntuación.
    """

    def __init__(self, font: Optional[pygame.font.Font] = None):
        """
        Inicializa el scoreboard.

        Args:
            font: Fuente para el texto (None usa la por defecto)
        """
        # Fuentes
        if font:
            self.font_large = font
        else:
            self.font_large = pygame.font.Font(None, 72)

        self.font_small = pygame.font.Font(None, 36)

        # Puntuaciones
        self.score_p1 = 0
        self.score_p2 = 0

        # Posiciones
        self.p1_pos = (SCREEN_WIDTH // 4, 50)
        self.p2_pos = (3 * SCREEN_WIDTH // 4, 50)

        # Colores
        self.color_normal = UI_TEXT
        self.color_highlight = (255, 255, 100)
        self.color_winner = (100, 255, 100)

        # Animación
        self.p1_scale = 1.0
        self.p2_scale = 1.0
        self.animation_time = 0

    def update(self, dt: float):
        """
        Actualiza animaciones del scoreboard.

        Args:
            dt: Delta time en segundos
        """
        self.animation_time += dt

        # Regresar escalas a normal gradualmente
        if self.p1_scale > 1.0:
            self.p1_scale = max(1.0, self.p1_scale - dt * 3)
        if self.p2_scale > 1.0:
            self.p2_scale = max(1.0, self.p2_scale - dt * 3)

    def set_scores(self, p1: int, p2: int):
        """
        Establece las puntuaciones.

        Args:
            p1: Puntuación del jugador 1
            p2: Puntuación del jugador 2
        """
        # Detectar cambios para animación
        if p1 > self.score_p1:
            self.p1_scale = 1.5
        if p2 > self.score_p2:
            self.p2_scale = 1.5

        self.score_p1 = p1
        self.score_p2 = p2

    def add_point_p1(self):
        """Añade un punto al jugador 1"""
        self.score_p1 += 1
        self.p1_scale = 1.5

    def add_point_p2(self):
        """Añade un punto al jugador 2"""
        self.score_p2 += 1
        self.p2_scale = 1.5

    def reset(self):
        """Reinicia las puntuaciones"""
        self.score_p1 = 0
        self.score_p2 = 0
        self.p1_scale = 1.0
        self.p2_scale = 1.0

    def get_winner(self) -> Optional[int]:
        """
        Retorna el ganador si hay uno.

        Returns:
            1 o 2 si hay ganador, None si no
        """
        if self.score_p1 >= WINNING_SCORE:
            return 1
        if self.score_p2 >= WINNING_SCORE:
            return 2
        return None

    def render(self, screen: pygame.Surface):
        """
        Renderiza el scoreboard.

        Args:
            screen: Superficie donde dibujar
        """
        # Determinar colores
        winner = self.get_winner()

        if winner == 1:
            color_p1 = self.color_winner
            color_p2 = self.color_normal
        elif winner == 2:
            color_p1 = self.color_normal
            color_p2 = self.color_winner
        else:
            color_p1 = self.color_highlight if self.p1_scale > 1.0 else self.color_normal
            color_p2 = self.color_highlight if self.p2_scale > 1.0 else self.color_normal

        # Renderizar puntuación P1
        p1_text = self.font_large.render(str(self.score_p1), True, color_p1)
        if self.p1_scale != 1.0:
            scaled_size = (
                int(p1_text.get_width() * self.p1_scale),
                int(p1_text.get_height() * self.p1_scale)
            )
            p1_text = pygame.transform.scale(p1_text, scaled_size)
        p1_rect = p1_text.get_rect(center=self.p1_pos)
        screen.blit(p1_text, p1_rect)

        # Renderizar puntuación P2
        p2_text = self.font_large.render(str(self.score_p2), True, color_p2)
        if self.p2_scale != 1.0:
            scaled_size = (
                int(p2_text.get_width() * self.p2_scale),
                int(p2_text.get_height() * self.p2_scale)
            )
            p2_text = pygame.transform.scale(p2_text, scaled_size)
        p2_rect = p2_text.get_rect(center=self.p2_pos)
        screen.blit(p2_text, p2_rect)

        # Separador central
        separator = self.font_large.render("-", True, self.color_normal)
        sep_rect = separator.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(separator, sep_rect)

        # Etiquetas de jugadores
        p1_label = self.font_small.render("P1", True, (150, 150, 180))
        p2_label = self.font_small.render("P2", True, (150, 150, 180))
        screen.blit(p1_label, (self.p1_pos[0] - p1_label.get_width() // 2, 90))
        screen.blit(p2_label, (self.p2_pos[0] - p2_label.get_width() // 2, 90))

    def render_minimal(self, screen: pygame.Surface):
        """
        Renderiza una versión minimalista del scoreboard.

        Args:
            screen: Superficie donde dibujar
        """
        # Solo números grandes
        text = self.font_large.render(
            f"{self.score_p1}  -  {self.score_p2}",
            True,
            self.color_normal
        )
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(text, rect)
