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

        # Control de tiempo para reinicio
        self.reset_timer = 0
        self.reset_delay = 1.0  # segundos

        # AI Controller (se inicializa si es necesario)
        self.ai_controller = None

        # Fondo
        self.background_tile = None

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

        # Cargar fondo
        self.background_tile = asset_manager.get_image('star_tile')

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
            # Pausar con ESC
            if event.key == pygame.K_ESCAPE:
                if self.game_over:
                    # Volver al menú
                    if self.game.state_manager:
                        self.game.state_manager.change_state(GameState.MENU)
                else:
                    self.paused = not self.paused
                return

            # Reiniciar si terminó el juego
            if self.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._reset_game()
                return

        # Pasar eventos al input handler si no está pausado
        if not self.paused and not self.game_over:
            self.input_handler.handle_event(event)

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
                # Meteorito va hacia el que recibió el punto
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

        # Overlay de pausa
        if self.paused:
            self._render_pause_overlay(screen)

        # Overlay de fin de juego
        if self.game_over:
            self._render_game_over(screen)

    def _render_background(self, screen: pygame.Surface):
        """
        Renderiza el fondo espacial.

        Args:
            screen: Superficie donde dibujar
        """
        screen.fill(SPACE_BLACK)

        # Tilear el fondo si hay sprite
        if self.background_tile:
            tile_w = self.background_tile.get_width()
            tile_h = self.background_tile.get_height()

            for x in range(0, SCREEN_WIDTH, tile_w):
                for y in range(0, SCREEN_HEIGHT, tile_h):
                    screen.blit(self.background_tile, (x, y))

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

        # Texto de pausa
        font = pygame.font.Font(None, 74)
        text = font.render("PAUSA", True, (255, 255, 255))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, rect)

        # Instrucciones
        font_small = pygame.font.Font(None, 36)
        hint = font_small.render("Presiona ESC para continuar", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(hint, hint_rect)

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
