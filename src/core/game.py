"""
Space Pong - Main Game Class
Clase principal que controla el loop del juego
"""

import sys
import pygame

from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE,
    SPACE_BLACK, GameState
)
from .settings import get_settings


class Game:
    """
    Clase principal del juego Space Pong.
    Maneja el game loop, eventos y coordinación de estados.
    """

    def __init__(self):
        """Inicializa Pygame y todos los componentes del juego"""
        # Inicializar Pygame
        pygame.init()
        pygame.mixer.init()

        # Obtener configuración
        self.settings = get_settings()

        # Crear ventana
        self._setup_display()

        # Reloj para controlar FPS
        self.clock = pygame.time.Clock()

        # Estado del juego
        self.running = True
        self.current_state = GameState.MENU

        # Delta time
        self.dt = 0

        # Managers
        self.state_manager = None
        self.asset_manager = None
        self.sound_manager = None

        # Inicializar managers
        self._init_managers()

        # Debug info
        self.show_fps = True

    def _setup_display(self):
        """Configura la ventana del juego"""
        display_flags = pygame.DOUBLEBUF

        if self.settings.video.fullscreen:
            display_flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode(
            (self.settings.video.width, self.settings.video.height),
            display_flags
        )
        pygame.display.set_caption(GAME_TITLE)

    def _init_managers(self):
        """Inicializa los managers del juego"""
        # Asset Manager
        try:
            from ..managers.asset_manager import get_asset_manager
            self.asset_manager = get_asset_manager()
        except Exception as e:
            print(f"Aviso: No se pudo inicializar AssetManager: {e}")

        # State Manager
        try:
            from ..managers.state_manager import StateManager
            from ..states.menu_state import MenuState
            from ..states.play_state import PlayState

            self.state_manager = StateManager(self)

            # Registrar estados
            self.state_manager.register_state(GameState.MENU, MenuState(self))
            self.state_manager.register_state(GameState.PLAYING, PlayState(self))

            # Iniciar en el menú
            self.state_manager.change_state(GameState.MENU, immediate=True)

        except Exception as e:
            print(f"Aviso: No se pudo inicializar StateManager: {e}")
            import traceback
            traceback.print_exc()

    def run(self):
        """
        Loop principal del juego.
        Ejecuta hasta que self.running sea False.
        """
        while self.running:
            # Calcular delta time (tiempo desde el último frame)
            self.dt = self.clock.tick(self.settings.video.fps) / 1000.0

            # Procesar eventos
            self._handle_events()

            # Actualizar lógica
            self._update()

            # Renderizar
            self._render()

        # Limpieza al salir
        self._quit()

    def _handle_events(self):
        """Procesa todos los eventos de Pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                # Toggle fullscreen con F11
                if event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                    continue

                # Toggle FPS display con F3
                if event.key == pygame.K_F3:
                    self.show_fps = not self.show_fps
                    continue

            # Delegar eventos al state manager
            if self.state_manager:
                self.state_manager.handle_event(event)

    def _update(self):
        """Actualiza la lógica del juego"""
        if self.state_manager:
            self.state_manager.update(self.dt)

    def _render(self):
        """Dibuja el frame actual"""
        # Limpiar pantalla
        self.screen.fill(SPACE_BLACK)

        # Renderizar estado actual
        if self.state_manager:
            self.state_manager.render(self.screen)
        else:
            self._render_fallback_screen()

        # Mostrar FPS si está habilitado
        if self.show_fps:
            self._render_fps()

        # Actualizar display
        pygame.display.flip()

    def _render_fallback_screen(self):
        """Pantalla de respaldo si no hay state manager"""
        font = pygame.font.Font(None, 48)
        text = font.render("Cargando...", True, (100, 150, 255))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)

    def _render_fps(self):
        """Muestra el contador de FPS"""
        fps = int(self.clock.get_fps())
        font = pygame.font.Font(None, 30)
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 0))
        self.screen.blit(fps_text, (10, 10))

    def _toggle_fullscreen(self):
        """Alterna entre pantalla completa y ventana"""
        self.settings.video.fullscreen = not self.settings.video.fullscreen
        self._setup_display()

    def _quit(self):
        """Limpieza y cierre del juego"""
        # Guardar configuración
        self.settings.save()

        # Cerrar Pygame
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()

    def get_screen(self) -> pygame.Surface:
        """Retorna la superficie de pantalla"""
        return self.screen

    def get_dt(self) -> float:
        """Retorna el delta time actual"""
        return self.dt

    def change_state(self, new_state: str):
        """
        Cambia el estado actual del juego.
        Args:
            new_state: Nuevo estado (usar constantes de GameState)
        """
        self.current_state = new_state
        if self.state_manager:
            self.state_manager.change_state(new_state)

    def quit_game(self):
        """Solicita cerrar el juego"""
        self.running = False
