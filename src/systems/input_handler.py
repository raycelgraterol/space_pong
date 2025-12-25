"""
Space Pong - Input Handler
Maneja la entrada del teclado para los jugadores
"""

import pygame
from typing import Optional

from ..core.constants import CONTROLS
from ..entities.ship import Ship


class InputHandler:
    """
    Maneja la entrada del teclado y la traduce a acciones de juego.
    Soporta múltiples esquemas de control.
    """

    def __init__(self):
        """Inicializa el handler de input"""
        self.controls = CONTROLS

        # Estado de teclas presionadas
        self._keys_pressed: set[int] = set()

        # Referencias a naves (se asignan externamente)
        self.player1_ship: Optional[Ship] = None
        self.player2_ship: Optional[Ship] = None

    def set_ships(self, player1: Ship, player2: Optional[Ship] = None):
        """
        Asigna las naves a controlar.

        Args:
            player1: Nave del jugador 1
            player2: Nave del jugador 2 (None si es bot)
        """
        self.player1_ship = player1
        self.player2_ship = player2

    def handle_event(self, event: pygame.event.Event):
        """
        Procesa un evento de pygame.

        Args:
            event: Evento a procesar
        """
        if event.type == pygame.KEYDOWN:
            self._keys_pressed.add(event.key)
            self._on_key_down(event.key)

        elif event.type == pygame.KEYUP:
            self._keys_pressed.discard(event.key)
            self._on_key_up(event.key)

    def _on_key_down(self, key: int):
        """
        Maneja evento de tecla presionada.

        Args:
            key: Código de tecla
        """
        # Player 1
        if self.player1_ship and not self.player1_ship.is_bot:
            if key in self.controls['player1']['up']:
                self.player1_ship.move_up()
            elif key in self.controls['player1']['down']:
                self.player1_ship.move_down()

        # Player 2
        if self.player2_ship and not self.player2_ship.is_bot:
            if key in self.controls['player2']['up']:
                self.player2_ship.move_up()
            elif key in self.controls['player2']['down']:
                self.player2_ship.move_down()

    def _on_key_up(self, key: int):
        """
        Maneja evento de tecla liberada.

        Args:
            key: Código de tecla
        """
        # Player 1
        if self.player1_ship and not self.player1_ship.is_bot:
            p1_controls = self.controls['player1']
            if key in p1_controls['up']:
                # Solo detener si no está presionada la otra dirección
                if not any(k in self._keys_pressed for k in p1_controls['down']):
                    self.player1_ship.stop()
                else:
                    self.player1_ship.move_down()
            elif key in p1_controls['down']:
                if not any(k in self._keys_pressed for k in p1_controls['up']):
                    self.player1_ship.stop()
                else:
                    self.player1_ship.move_up()

        # Player 2
        if self.player2_ship and not self.player2_ship.is_bot:
            p2_controls = self.controls['player2']
            if key in p2_controls['up']:
                if not any(k in self._keys_pressed for k in p2_controls['down']):
                    self.player2_ship.stop()
                else:
                    self.player2_ship.move_down()
            elif key in p2_controls['down']:
                if not any(k in self._keys_pressed for k in p2_controls['up']):
                    self.player2_ship.stop()
                else:
                    self.player2_ship.move_up()

    def update(self):
        """
        Actualización continua basada en teclas presionadas.
        Alternativa al sistema de eventos para movimiento más fluido.
        """
        keys = pygame.key.get_pressed()

        # Player 1
        if self.player1_ship and not self.player1_ship.is_bot:
            p1_up = any(keys[k] for k in self.controls['player1']['up'])
            p1_down = any(keys[k] for k in self.controls['player1']['down'])

            if p1_up and not p1_down:
                self.player1_ship.move_up()
            elif p1_down and not p1_up:
                self.player1_ship.move_down()
            else:
                self.player1_ship.stop()

        # Player 2
        if self.player2_ship and not self.player2_ship.is_bot:
            p2_up = any(keys[k] for k in self.controls['player2']['up'])
            p2_down = any(keys[k] for k in self.controls['player2']['down'])

            if p2_up and not p2_down:
                self.player2_ship.move_up()
            elif p2_down and not p2_up:
                self.player2_ship.move_down()
            else:
                self.player2_ship.stop()

    def is_key_pressed(self, key: int) -> bool:
        """
        Verifica si una tecla está presionada.

        Args:
            key: Código de tecla

        Returns:
            True si está presionada
        """
        return key in self._keys_pressed

    def is_action_pressed(self, action: str) -> bool:
        """
        Verifica si una acción general está activa.

        Args:
            action: 'pause', 'confirm', 'back'

        Returns:
            True si alguna tecla de la acción está presionada
        """
        if action in self.controls['general']:
            return any(
                key in self._keys_pressed
                for key in self.controls['general'][action]
            )
        return False

    def clear(self):
        """Limpia el estado de teclas presionadas"""
        self._keys_pressed.clear()

        if self.player1_ship:
            self.player1_ship.stop()
        if self.player2_ship:
            self.player2_ship.stop()
