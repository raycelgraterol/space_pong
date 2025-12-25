"""
Space Pong - State Manager
Gestiona los estados del juego y las transiciones entre ellos
"""

import pygame
from typing import Optional, Dict, Type, TYPE_CHECKING

from ..states.base_state import BaseState
from ..core.constants import GameState

if TYPE_CHECKING:
    from ..core.game import Game


class StateManager:
    """
    Gestiona los estados del juego.
    Maneja transiciones y mantiene referencia al estado actual.
    """

    def __init__(self, game: 'Game'):
        """
        Inicializa el gestor de estados.

        Args:
            game: Referencia al objeto Game principal
        """
        self.game = game

        # Diccionario de estados registrados
        self._states: Dict[str, BaseState] = {}

        # Estado actual
        self._current_state: Optional[BaseState] = None
        self._current_state_name: str = ""

        # Estado pendiente (para transiciones)
        self._pending_state: Optional[str] = None

    def register_state(self, name: str, state: BaseState):
        """
        Registra un estado en el manager.

        Args:
            name: Nombre identificador del estado
            state: Instancia del estado
        """
        self._states[name] = state

    def register_state_class(self, name: str, state_class: Type[BaseState]):
        """
        Registra una clase de estado (se instanciará cuando se necesite).

        Args:
            name: Nombre identificador del estado
            state_class: Clase del estado
        """
        self._states[name] = state_class(self.game)

    def change_state(self, state_name: str, immediate: bool = False):
        """
        Cambia al estado especificado.

        Args:
            state_name: Nombre del estado al que cambiar
            immediate: Si True, cambia inmediatamente; si False, al final del frame
        """
        if state_name not in self._states:
            print(f"AVISO: Estado '{state_name}' no registrado")
            return

        if immediate:
            self._do_state_change(state_name)
        else:
            self._pending_state = state_name

    def _do_state_change(self, state_name: str):
        """
        Realiza el cambio de estado.

        Args:
            state_name: Nombre del nuevo estado
        """
        # Salir del estado actual
        if self._current_state:
            self._current_state.exit()

        # Entrar al nuevo estado
        self._current_state = self._states[state_name]
        self._current_state_name = state_name
        self._current_state.enter()

        print(f"Estado cambiado a: {state_name}")

    def handle_event(self, event: pygame.event.Event):
        """
        Pasa un evento al estado actual.

        Args:
            event: Evento a procesar
        """
        if self._current_state:
            self._current_state.handle_event(event)

    def update(self, dt: float):
        """
        Actualiza el estado actual.

        Args:
            dt: Delta time en segundos
        """
        # Procesar cambio de estado pendiente
        if self._pending_state:
            self._do_state_change(self._pending_state)
            self._pending_state = None

        # Actualizar estado actual
        if self._current_state:
            self._current_state.update(dt)

    def render(self, screen: pygame.Surface):
        """
        Renderiza el estado actual.

        Args:
            screen: Superficie donde dibujar
        """
        if self._current_state:
            self._current_state.render(screen)

    @property
    def current_state(self) -> Optional[BaseState]:
        """Retorna el estado actual"""
        return self._current_state

    @property
    def current_state_name(self) -> str:
        """Retorna el nombre del estado actual"""
        return self._current_state_name

    def is_state(self, state_name: str) -> bool:
        """
        Verifica si el estado actual es el especificado.

        Args:
            state_name: Nombre del estado a verificar

        Returns:
            True si es el estado actual
        """
        return self._current_state_name == state_name
