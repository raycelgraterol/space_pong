"""
Space Pong - Menu State
Menú principal del juego
"""

import pygame
from typing import TYPE_CHECKING, List

from .base_state import BaseState
from ..core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SPACE_BLACK,
    GameState, GameMode, UI_PRIMARY, UI_HIGHLIGHT, UI_TEXT
)

if TYPE_CHECKING:
    from ..core.game import Game


class MenuItem:
    """Representa un item del menú"""

    def __init__(self, text: str, action: str, y_position: int):
        self.text = text
        self.action = action
        self.y_position = y_position
        self.selected = False


class MenuState(BaseState):
    """
    Estado del menú principal.
    Permite seleccionar modo de juego y configuraciones.
    """

    def __init__(self, game: 'Game'):
        """
        Inicializa el estado del menú.

        Args:
            game: Referencia al juego principal
        """
        super().__init__(game)

        # Fuentes
        self.font_title = None
        self.font_menu = None
        self.font_hint = None

        # Items del menú
        self.menu_items: List[MenuItem] = []
        self.selected_index = 0

        # Animación
        self.animation_time = 0
        self.title_offset = 0

        # Fondo
        self.stars = []

    def enter(self):
        """Inicializa el menú al entrar"""
        print("Entrando a MenuState")

        # Inicializar fuentes
        self.font_title = pygame.font.Font(None, 80)
        self.font_menu = pygame.font.Font(None, 48)
        self.font_hint = pygame.font.Font(None, 28)

        # Crear items del menú
        self._create_menu_items()

        # Generar estrellas para el fondo
        self._generate_stars()

        self.selected_index = 0

    def _create_menu_items(self):
        """Crea los items del menú"""
        self.menu_items = [
            MenuItem("JUGAR VS BOT", "play_bot", SCREEN_HEIGHT // 2),
            MenuItem("JUGAR 2 JUGADORES", "play_pvp", SCREEN_HEIGHT // 2 + 60),
            MenuItem("SALIR", "quit", SCREEN_HEIGHT // 2 + 120),
        ]

        if self.menu_items:
            self.menu_items[0].selected = True

    def _generate_stars(self):
        """Genera estrellas aleatorias para el fondo"""
        import random
        self.stars = []
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.choice([1, 1, 1, 2, 2, 3])
            brightness = random.randint(100, 255)
            speed = random.uniform(0.2, 1.0)
            self.stars.append({
                'x': x, 'y': y, 'size': size,
                'brightness': brightness, 'speed': speed
            })

    def exit(self):
        """Limpieza al salir del menú"""
        pass

    def handle_event(self, event: pygame.event.Event):
        """
        Procesa eventos del menú.

        Args:
            event: Evento a procesar
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move_selection(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._move_selection(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._select_current()
            elif event.key == pygame.K_ESCAPE:
                self.game.quit_game()

    def _move_selection(self, direction: int):
        """
        Mueve la selección del menú.

        Args:
            direction: -1 arriba, 1 abajo
        """
        self.menu_items[self.selected_index].selected = False

        self.selected_index += direction
        if self.selected_index < 0:
            self.selected_index = len(self.menu_items) - 1
        elif self.selected_index >= len(self.menu_items):
            self.selected_index = 0

        self.menu_items[self.selected_index].selected = True

    def _select_current(self):
        """Ejecuta la acción del item seleccionado"""
        if not self.menu_items:
            return

        action = self.menu_items[self.selected_index].action

        if action == "play_bot":
            self._start_game(GameMode.PVE)
        elif action == "play_pvp":
            self._start_game(GameMode.PVP)
        elif action == "quit":
            self.game.quit_game()

    def _start_game(self, mode: str):
        """
        Inicia el juego con el modo especificado.

        Args:
            mode: GameMode.PVP o GameMode.PVE
        """
        if self.game.state_manager:
            # Configurar el modo en PlayState
            play_state = self.game.state_manager._states.get(GameState.PLAYING)
            if play_state and hasattr(play_state, 'set_game_mode'):
                play_state.set_game_mode(mode)

            self.game.state_manager.change_state(GameState.PLAYING)

    def update(self, dt: float):
        """
        Actualiza la animación del menú.

        Args:
            dt: Delta time en segundos
        """
        self.animation_time += dt

        # Animación del título
        import math
        self.title_offset = math.sin(self.animation_time * 2) * 5

        # Mover estrellas
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = 0
                star['x'] = pygame.time.get_ticks() % SCREEN_WIDTH

    def render(self, screen: pygame.Surface):
        """
        Dibuja el menú.

        Args:
            screen: Superficie donde dibujar
        """
        # Fondo
        screen.fill(SPACE_BLACK)

        # Estrellas
        self._render_stars(screen)

        # Título
        self._render_title(screen)

        # Items del menú
        self._render_menu_items(screen)

        # Instrucciones
        self._render_hints(screen)

    def _render_stars(self, screen: pygame.Surface):
        """Renderiza las estrellas del fondo"""
        for star in self.stars:
            color = (star['brightness'],) * 3
            pygame.draw.circle(
                screen, color,
                (int(star['x']), int(star['y'])),
                star['size']
            )

    def _render_title(self, screen: pygame.Surface):
        """Renderiza el título del juego"""
        # Sombra
        shadow = self.font_title.render("SPACE PONG", True, (50, 50, 100))
        shadow_rect = shadow.get_rect(
            center=(SCREEN_WIDTH // 2 + 3, 120 + self.title_offset + 3)
        )
        screen.blit(shadow, shadow_rect)

        # Título principal
        title = self.font_title.render("SPACE PONG", True, UI_PRIMARY)
        title_rect = title.get_rect(
            center=(SCREEN_WIDTH // 2, 120 + self.title_offset)
        )
        screen.blit(title, title_rect)

        # Subtítulo
        subtitle = self.font_hint.render("Tenis Espacial", True, (150, 150, 180))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 165))
        screen.blit(subtitle, subtitle_rect)

    def _render_menu_items(self, screen: pygame.Surface):
        """Renderiza los items del menú"""
        for item in self.menu_items:
            if item.selected:
                # Item seleccionado - con highlight
                color = UI_HIGHLIGHT

                # Indicador de selección
                indicator = self.font_menu.render(">", True, UI_HIGHLIGHT)
                ind_rect = indicator.get_rect(
                    right=SCREEN_WIDTH // 2 - 120,
                    centery=item.y_position
                )
                screen.blit(indicator, ind_rect)

                # Fondo del item
                item_width = 300
                bg_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - item_width // 2 - 10,
                    item.y_position - 20,
                    item_width + 20,
                    40
                )
                pygame.draw.rect(screen, (40, 60, 100), bg_rect, border_radius=5)
                pygame.draw.rect(screen, UI_PRIMARY, bg_rect, 2, border_radius=5)
            else:
                color = UI_TEXT

            # Texto del item
            text = self.font_menu.render(item.text, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, item.y_position))
            screen.blit(text, text_rect)

    def _render_hints(self, screen: pygame.Surface):
        """Renderiza las instrucciones en la parte inferior"""
        hints = [
            "W/S o Flechas: Navegar",
            "ENTER/ESPACIO: Seleccionar",
            "ESC: Salir"
        ]

        y = SCREEN_HEIGHT - 80
        for hint in hints:
            text = self.font_hint.render(hint, True, (120, 120, 150))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            screen.blit(text, text_rect)
            y += 25
