"""
Space Pong - Play State
Estado principal del juego donde se desarrolla la acción
"""

import pygame
from typing import TYPE_CHECKING, Optional

from .base_state import BaseState
from ..core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SPACE_BLACK,
    GameState, GameMode, WINNING_SCORE
)
from ..entities.ship import Ship
from ..entities.ball import Ball
from ..entities.laser_grid import LaserGrid
from ..systems.input_handler import InputHandler
from ..systems.physics import PhysicsSystem
from ..systems.collision import CollisionSystem
from ..ui.scoreboard import Scoreboard
from ..managers.asset_manager import get_asset_manager

if TYPE_CHECKING:
    from ..core.game import Game


class PlayState(BaseState):
    """
    Estado de juego activo.
    Maneja toda la lógica del gameplay.
    """

    def __init__(self, game: 'Game'):
        """
        Inicializa el estado de juego.

        Args:
            game: Referencia al juego principal
        """
        super().__init__(game)

        # Modo de juego
        self.game_mode = GameMode.PVP
        self.ai_difficulty = 'medium'

        # Entidades
        self.player1: Optional[Ship] = None
        self.player2: Optional[Ship] = None
        self.ball: Optional[Ball] = None
        self.laser_grid: Optional[LaserGrid] = None

        # Sistemas
        self.input_handler = InputHandler()
        self.physics = PhysicsSystem()
        self.collision = CollisionSystem()

        # UI
        self.scoreboard = Scoreboard()

        # Estado del juego
        self.paused = False
        self.game_over = False
        self.winner = None

        # Menú de pausa
        self.pause_menu_options = ["Continuar", "Salir al Menú"]
        self.pause_menu_selected = 0
        self.show_exit_confirmation = False

        # Control de tiempo para reinicio
        self.reset_timer = 0
        self.reset_delay = 1.0  # segundos

        # AI Controller (se inicializa si es necesario)
        self.ai_controller = None

        # Sistema de niveles (solo en modo PVE)
        self.current_level = 1
        self.level_points = 0  # Puntos del jugador en este nivel
        self.points_for_next_level = 3  # Aumenta +1 por nivel

        # Velocidades base para el sistema de niveles
        self.base_player_speed = 400  # Velocidad del jugador (constante)
        self.base_bot_speed = 240     # Bot empieza lento (60% del jugador)
        self.base_ball_speed = 200    # Ball empieza lenta

        # Fondo - lista de tiles para variedad
        self.background_tiles = []

    def enter(self):
        """Inicializa el estado al entrar"""
        print("Entrando a PlayState")

        # Cargar assets
        asset_manager = get_asset_manager()

        # Crear jugadores
        ship1_sprite = asset_manager.get_image('ship_crystal')
        ship2_sprite = asset_manager.get_image('ship_ufo')

        self.player1 = Ship(1, ship1_sprite, is_bot=False)
        self.player2 = Ship(
            2,
            ship2_sprite,
            is_bot=(self.game_mode == GameMode.PVE)
        )

        # Crear meteorito
        ball_sprite = asset_manager.get_image('meteorite')
        self.ball = Ball(sprite=ball_sprite)

        # Crear malla láser
        laser_sprite = asset_manager.get_image('laser_grid')
        self.laser_grid = LaserGrid(sprite=laser_sprite)

        # Configurar input handler
        self.input_handler.set_ships(self.player1, self.player2)

        # Cargar todos los tiles de fondo
        tile_names = ['star_tile', 'star_tile_dense', 'star_tile_sparse', 
                      'star_tile_nebula', 'star_tile_cluster']
        self.background_tiles = [asset_manager.get_image(name) for name in tile_names]
        self.background_tiles = [t for t in self.background_tiles if t is not None]

        # Inicializar AI si es necesario
        if self.game_mode == GameMode.PVE:
            self._init_ai()

        # Resetear estado
        self._reset_game()

    def _init_ai(self):
        """Inicializa el controlador de IA"""
        try:
            from ..systems.ai_controller import AIController
            self.ai_controller = AIController(self.ai_difficulty)
        except ImportError:
            print("AVISO: AI Controller no disponible")
            self.ai_controller = None

    def _reset_game(self):
        """Reinicia el juego completamente"""
        self.player1.reset_position()
        self.player1.reset_score()

        self.player2.reset_position()
        self.player2.reset_score()

        self.ball.reset()

        self.scoreboard.reset()

        self.game_over = False
        self.winner = None
        self.reset_timer = 0

        # Resetear sistema de niveles
        self.current_level = 1
        self.level_points = 0
        self.points_for_next_level = 3
        self._apply_level_speeds()

    def _reset_round(self, towards_player: Optional[int] = None):
        """
        Reinicia una ronda después de un punto.

        Args:
            towards_player: Dirección inicial del meteorito
        """
        self.player1.reset_position()
        self.player2.reset_position()
        self.ball.reset(towards_player)
        self.reset_timer = 0

    def _apply_level_speeds(self):
        """Aplica las velocidades segun el nivel actual"""
        if self.game_mode != GameMode.PVE:
            return

        level = self.current_level

        # Calcular velocidades segun nivel
        # Bot: aumenta 15% por nivel
        bot_speed = self.base_bot_speed * (1 + (level - 1) * 0.15)

        # Ball: aumenta 30% por nivel (x2 que el bot)
        ball_speed = self.base_ball_speed * (1 + (level - 1) * 0.30)

        # Limitar velocidades maximas
        bot_speed = min(bot_speed, 500)
        ball_speed = min(ball_speed, 600)

        # Aplicar a las entidades
        if self.player2 and self.player2.is_bot:
            self.player2.speed = bot_speed

        if self.ball:
            self.ball.speed = ball_speed
            # Normalizar velocidad actual manteniendo direccion
            if self.ball.velocity.length() > 0:
                self.ball.velocity = self.ball.velocity.normalize() * ball_speed

        # Ajustar dificultad de la IA segun nivel
        if self.ai_controller:
            if level <= 2:
                self.ai_controller.set_difficulty('easy')
            elif level <= 4:
                self.ai_controller.set_difficulty('medium')
            else:
                self.ai_controller.set_difficulty('hard')

    def _check_level_up(self):
        """Verifica si el jugador sube de nivel"""
        if self.game_mode != GameMode.PVE:
            return

        # Solo contar puntos del jugador 1
        if self.level_points >= self.points_for_next_level:
            self.current_level += 1
            self.level_points = 0
            self.points_for_next_level += 1  # Cada nivel requiere +1 punto mas
            self._apply_level_speeds()
            print(f'NIVEL UP! Ahora nivel {self.current_level}')

    def exit(self):
        """Limpieza al salir del estado"""
        self.input_handler.clear()

    def handle_event(self, event: pygame.event.Event):
        """
        Procesa eventos de pygame.

        Args:
            event: Evento a procesar
        """
        if event.type == pygame.KEYDOWN:
            # Manejar diálogo de confirmación de salida
            if self.show_exit_confirmation:
                self._handle_confirmation_input(event)
                return

            # Manejar menú de pausa
            if self.paused:
                self._handle_pause_menu_input(event)
                return

            # Pausar con ESC durante el juego
            if event.key == pygame.K_ESCAPE:
                if self.game_over:
                    # Volver al menú
                    if self.game.state_manager:
                        self.game.state_manager.change_state(GameState.MENU)
                else:
                    self.paused = True
                    self.pause_menu_selected = 0
                return

            # Reiniciar si terminó el juego
            if self.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._reset_game()
                return

        # Pasar eventos al input handler si no está pausado
        if not self.paused and not self.game_over:
            self.input_handler.handle_event(event)

    def _handle_pause_menu_input(self, event: pygame.event.Event):
        """
        Maneja la entrada del menú de pausa.

        Args:
            event: Evento de teclado
        """
        if event.key in (pygame.K_UP, pygame.K_w):
            self.pause_menu_selected = (self.pause_menu_selected - 1) % len(self.pause_menu_options)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.pause_menu_selected = (self.pause_menu_selected + 1) % len(self.pause_menu_options)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._select_pause_option()
        elif event.key == pygame.K_ESCAPE:
            # ESC en el menú de pausa = continuar
            self.paused = False

    def _handle_confirmation_input(self, event: pygame.event.Event):
        """
        Maneja la entrada del diálogo de confirmación.

        Args:
            event: Evento de teclado
        """
        if event.key in (pygame.K_s, pygame.K_RETURN):
            # Confirmar salida
            self.show_exit_confirmation = False
            self.paused = False
            if self.game.state_manager:
                self.game.state_manager.change_state(GameState.MENU)
        elif event.key in (pygame.K_n, pygame.K_ESCAPE):
            # Cancelar, volver al menú de pausa
            self.show_exit_confirmation = False

    def _select_pause_option(self):
        """Ejecuta la opción seleccionada del menú de pausa"""
        if self.pause_menu_selected == 0:
            # Continuar
            self.paused = False
        elif self.pause_menu_selected == 1:
            # Salir al menú - mostrar confirmación
            self.show_exit_confirmation = True

    def update(self, dt: float):
        """
        Actualiza la lógica del juego.

        Args:
            dt: Delta time en segundos
        """
        if self.paused or self.game_over:
            return

        # Timer de reinicio después de punto
        if self.reset_timer > 0:
            self.reset_timer -= dt
            return

        # Actualizar input (método continuo)
        self.input_handler.update()

        # Actualizar IA si está activa
        if self.ai_controller and self.player2.is_bot:
            ai_direction = self.ai_controller.update(dt, self.ball, self.player2)
            self.player2.set_movement(ai_direction)

        # Actualizar entidades
        self.player1.update(dt)
        self.player2.update(dt)
        self.ball.update(dt)
        self.laser_grid.update(dt)

        # Verificar colisiones
        self._check_collisions()

        # Verificar puntuación
        self._check_scoring()

        # Actualizar UI
        self.scoreboard.update(dt)

    def _check_collisions(self):
        """Verifica todas las colisiones"""
        if not self.ball:
            return

        # Colisión con nave 1
        if self.ball.velocity.x < 0:  # Va hacia la izquierda
            result = self.collision.check_ball_ship_collision(self.ball, self.player1)
            if result.collided:
                PhysicsSystem.bounce_off_paddle(self.ball, self.player1)

        # Colisión con nave 2
        if self.ball.velocity.x > 0:  # Va hacia la derecha
            result = self.collision.check_ball_ship_collision(self.ball, self.player2)
            if result.collided:
                PhysicsSystem.bounce_off_paddle(self.ball, self.player2)

        # Colisión de naves con láser
        laser_rect = self.laser_grid.get_collision_rect()

        if self.laser_grid.check_collision(self.player1.get_rect()):
            self._on_laser_touch(self.player1)

        if self.laser_grid.check_collision(self.player2.get_rect()):
            self._on_laser_touch(self.player2)

    def _on_laser_touch(self, ship: Ship):
        """
        Maneja cuando una nave toca el láser.

        Args:
            ship: Nave que tocó el láser
        """
        # El oponente gana un punto
        if ship.player_id == 1:
            self.player2.add_score()
            self.scoreboard.add_point_p2()
        else:
            self.player1.add_score()
            self.scoreboard.add_point_p1()

        # Alejar la nave del láser
        ship.reset_position()

        # Verificar ganador
        self._check_winner()

    def _check_scoring(self):
        """Verifica si se anotó un punto"""
        if not self.ball:
            return

        out, scorer = self.ball.is_out_of_bounds()

        if out:
            if scorer == 1:
                self.player1.add_score()
                self.scoreboard.add_point_p1()
                # Contar punto para el sistema de niveles
                if self.game_mode == GameMode.PVE:
                    self.level_points += 1
                    self._check_level_up()
                # Meteorito va hacia el que recibio el punto
                self._start_reset_round(towards_player=2)
            elif scorer == 2:
                self.player2.add_score()
                self.scoreboard.add_point_p2()
                self._start_reset_round(towards_player=1)

            self._check_winner()

    def _start_reset_round(self, towards_player: int):
        """
        Inicia el timer para reiniciar la ronda.

        Args:
            towards_player: Hacia qué jugador irá el meteorito
        """
        self.reset_timer = self.reset_delay
        self._reset_round(towards_player)

    def _check_winner(self):
        """Verifica si hay un ganador"""
        winner = self.scoreboard.get_winner()
        if winner:
            self.game_over = True
            self.winner = winner

    def render(self, screen: pygame.Surface):
        """
        Dibuja el estado de juego.

        Args:
            screen: Superficie donde dibujar
        """
        # Fondo
        self._render_background(screen)

        # Entidades
        if self.laser_grid:
            self.laser_grid.render(screen)

        if self.player1:
            self.player1.render(screen)

        if self.player2:
            self.player2.render(screen)

        if self.ball:
            self.ball.render_with_trail(screen)

        # UI
        self.scoreboard.render(screen)

        # Marcador de nivel (solo en PVE)
        if self.game_mode == GameMode.PVE:
            self._render_level_indicator(screen)

        # Overlay de pausa
        if self.paused:
            self._render_pause_overlay(screen)

        # Overlay de fin de juego
        if self.game_over:
            self._render_game_over(screen)

    def _render_background(self, screen: pygame.Surface):
        """
        Renderiza el fondo espacial con tiles variados.

        Args:
            screen: Superficie donde dibujar
        """
        import random
        screen.fill(SPACE_BLACK)

        # Tilear el fondo con tiles aleatorios
        if self.background_tiles:
            tile_w = self.background_tiles[0].get_width()
            tile_h = self.background_tiles[0].get_height()

            # Seed fijo para que el patron sea consistente entre frames
            random.seed(12345)
            for x in range(0, SCREEN_WIDTH, tile_w):
                for y in range(0, SCREEN_HEIGHT, tile_h):
                    tile = random.choice(self.background_tiles)
                    screen.blit(tile, (x, y))


    def _render_level_indicator(self, screen: pygame.Surface):
        """Renderiza el indicador de nivel en el centro superior"""
        font_level = pygame.font.Font(None, 36)
        font_progress = pygame.font.Font(None, 24)

        # Texto del nivel
        level_text = f"NIVEL {self.current_level}"
        level_surface = font_level.render(level_text, True, (100, 200, 255))
        level_rect = level_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))

        # Fondo del indicador
        bg_rect = pygame.Rect(level_rect.left - 15, level_rect.top - 5,
                              level_rect.width + 30, level_rect.height + 25)
        pygame.draw.rect(screen, (20, 40, 60), bg_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 200, 255), bg_rect, 2, border_radius=8)

        screen.blit(level_surface, level_rect)

        # Barra de progreso
        progress = self.level_points / self.points_for_next_level
        bar_width = 80
        bar_height = 6
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = level_rect.bottom + 5

        # Fondo de la barra
        pygame.draw.rect(screen, (40, 40, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
        # Progreso
        if progress > 0:
            pygame.draw.rect(screen, (100, 255, 150),
                           (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=3)
        # Borde
        pygame.draw.rect(screen, (100, 200, 255), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=3)

        # Texto de progreso
        progress_text = f"{self.level_points}/{self.points_for_next_level}"
        progress_surface = font_progress.render(progress_text, True, (150, 150, 180))
        progress_rect = progress_surface.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height + 12))
        screen.blit(progress_surface, progress_rect)

    def _render_pause_overlay(self, screen: pygame.Surface):
        """
        Renderiza el overlay de pausa.

        Args:
            screen: Superficie donde dibujar
        """
        # Oscurecer pantalla
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Si hay confirmación pendiente, mostrar ese diálogo
        if self.show_exit_confirmation:
            self._render_exit_confirmation(screen)
            return

        # Texto de pausa
        font_title = pygame.font.Font(None, 74)
        title = font_title.render("PAUSA", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(title, title_rect)

        # Opciones del menú
        font_option = pygame.font.Font(None, 48)
        start_y = SCREEN_HEIGHT // 2

        for i, option in enumerate(self.pause_menu_options):
            if i == self.pause_menu_selected:
                # Opción seleccionada
                color = (100, 255, 100)
                prefix = "> "
            else:
                color = (200, 200, 200)
                prefix = "  "

            text = font_option.render(prefix + option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 50))
            screen.blit(text, text_rect)

        # Instrucciones
        font_hint = pygame.font.Font(None, 28)
        hint = font_hint.render("Flechas/W/S: Navegar | ENTER: Seleccionar | ESC: Continuar", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130))
        screen.blit(hint, hint_rect)

    def _render_exit_confirmation(self, screen: pygame.Surface):
        """
        Renderiza el diálogo de confirmación de salida.

        Args:
            screen: Superficie donde dibujar
        """
        # Cuadro de diálogo
        dialog_width = 450
        dialog_height = 180
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2

        # Fondo del diálogo
        dialog_bg = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        dialog_bg.fill((30, 30, 50, 240))
        screen.blit(dialog_bg, (dialog_x, dialog_y))

        # Borde
        pygame.draw.rect(screen, (100, 150, 255), (dialog_x, dialog_y, dialog_width, dialog_height), 3)

        # Texto de confirmación
        font_title = pygame.font.Font(None, 42)
        title = font_title.render("¿Salir al menú principal?", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, dialog_y + 50))
        screen.blit(title, title_rect)

        # Advertencia
        font_warning = pygame.font.Font(None, 30)
        warning = font_warning.render("Se perderá el progreso actual", True, (255, 200, 100))
        warning_rect = warning.get_rect(center=(SCREEN_WIDTH // 2, dialog_y + 90))
        screen.blit(warning, warning_rect)

        # Opciones
        font_options = pygame.font.Font(None, 36)
        options_text = font_options.render("[S] Sí, salir    [N] No, continuar", True, (150, 255, 150))
        options_rect = options_text.get_rect(center=(SCREEN_WIDTH // 2, dialog_y + 140))
        screen.blit(options_text, options_rect)

    def _render_game_over(self, screen: pygame.Surface):
        """
        Renderiza la pantalla de fin de juego.

        Args:
            screen: Superficie donde dibujar
        """
        # Oscurecer pantalla
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Texto de ganador
        font = pygame.font.Font(None, 74)
        winner_text = f"JUGADOR {self.winner} GANA!"
        text = font.render(winner_text, True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(text, rect)

        # Instrucciones
        font_small = pygame.font.Font(None, 36)
        hint = font_small.render(
            "ESPACIO para jugar de nuevo | ESC para salir",
            True,
            (200, 200, 200)
        )
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        screen.blit(hint, hint_rect)

    def set_game_mode(self, mode: str, difficulty: str = 'medium'):
        """
        Configura el modo de juego.

        Args:
            mode: GameMode.PVP o GameMode.PVE
            difficulty: Dificultad de la IA (si aplica)
        """
        self.game_mode = mode
        self.ai_difficulty = difficulty
