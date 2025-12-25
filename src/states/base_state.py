"""
Space Pong - Base State
Clase base abstracta para todos los estados del juego
"""

from abc import ABC, abstractmethod
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.game import Game


class BaseState(ABC):
    """
    Clase base abstracta para estados del juego.
    Define la interfaz que todos los estados deben implementar.
    """

    def __init__(self, game: 'Game'):
        """
        Inicializa el estado.

        Args:
            game: Referencia al objeto Game principal
        """
        self.game = game

    def enter(self):
        """
        Llamado cuando se entra a este estado.
        Override para inicialización específica.
        """
        pass

    def exit(self):
        """
        Llamado cuando se sale de este estado.
        Override para limpieza específica.
        """
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """
        Procesa un evento de pygame.

        Args:
            event: Evento a procesar
        """
        pass

    @abstractmethod
    def update(self, dt: float):
        """
        Actualiza la lógica del estado.

        Args:
            dt: Delta time en segundos
        """
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface):
        """
        Dibuja el estado en pantalla.

        Args:
            screen: Superficie donde dibujar
        """
        pass
