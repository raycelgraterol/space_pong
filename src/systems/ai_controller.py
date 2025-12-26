"""
Space Pong - AI Controller
Controla la nave del bot con diferentes niveles de dificultad
"""

import random
import math
from typing import TYPE_CHECKING

from ..core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    AI_DIFFICULTY, SHIP_HEIGHT
)

if TYPE_CHECKING:
    from ..entities.ball import Ball
    from ..entities.ship import Ship


class AIController:
    """
    Controlador de IA para la nave del bot.
    Implementa predicción de trayectoria con imperfecciones configurables.
    """

    def __init__(self, difficulty: str = 'medium'):
        """
        Inicializa el controlador de IA.

        Args:
            difficulty: 'easy', 'medium', o 'hard'
        """
        self.difficulty = difficulty
        self.settings = AI_DIFFICULTY.get(difficulty, AI_DIFFICULTY['medium'])

        # Objetivo Y donde el bot quiere posicionarse
        self.target_y = SCREEN_HEIGHT // 2

        # Timer de reacción
        self.reaction_timer = 0

        # Error de predicción actual
        self.current_error = 0

        # Estado del bot
        self.is_returning_to_center = False
        self.last_ball_direction = 0

        # Sistema de desenfoque aleatorio
        self.drift_offset = 0  # Desviacion actual del objetivo
        self.drift_timer = 0   # Timer para cambiar el drift
        self.drift_target = 0  # Objetivo del drift

    def update(self, dt: float, ball: 'Ball', ship: 'Ship') -> int:
        """
        Actualiza el controlador y retorna la dirección de movimiento.

        Args:
            dt: Delta time en segundos
            ball: Meteorito
            ship: Nave del bot

        Returns:
            -1 (arriba), 0 (quieto), 1 (abajo)
        """
        # Actualizar sistema de desenfoque (drift)
        self._update_drift(dt)

        # Actualizar timer de reacción
        self.reaction_timer -= dt

        # Detectar cambio de dirección del meteorito
        ball_direction = 1 if ball.velocity.x > 0 else -1
        if ball_direction != self.last_ball_direction:
            self.last_ball_direction = ball_direction
            # Forzar recálculo de predicción
            self.reaction_timer = 0

        # Verificar si el meteorito viene hacia el bot (jugador 2, lado derecho)
        ball_coming_to_bot = ball.velocity.x > 0

        if ball_coming_to_bot:
            self.is_returning_to_center = False

            # Solo actualizar predicción cuando el timer expire
            if self.reaction_timer <= 0:
                self.target_y = self._predict_ball_position(ball, ship.position.x)
                self.target_y += self._add_error()
                self.reaction_timer = self.settings['reaction_delay']

                # Posibilidad de cometer un error grande
                if random.random() < self.settings['mistake_chance']:
                    self.target_y += random.uniform(-100, 100)

        else:
            # Meteorito va hacia el oponente, volver gradualmente al centro
            if not self.is_returning_to_center:
                self.is_returning_to_center = True

            self.target_y = SCREEN_HEIGHT // 2

        # Calcular dirección de movimiento con drift aplicado
        effective_target = self.target_y + self.drift_offset
        return self._get_movement_direction(ship.position.y, effective_target)

    def _predict_ball_position(self, ball: 'Ball', target_x: float) -> float:
        """
        Predice la posición Y donde llegará el meteorito.

        Args:
            ball: Meteorito
            target_x: Posición X donde queremos predecir

        Returns:
            Posición Y predicha
        """
        # Simulación simple de trayectoria
        sim_x = ball.position.x
        sim_y = ball.position.y
        sim_vx = ball.velocity.x
        sim_vy = ball.velocity.y

        # Tamaño del paso de simulación
        step = 0.016  # ~60 FPS
        max_iterations = 1000
        iterations = 0

        half_size = ball.rect.width // 2 if ball.rect else 20

        while iterations < max_iterations:
            # Avanzar simulación
            sim_x += sim_vx * step
            sim_y += sim_vy * step

            # Simular rebotes en paredes
            if sim_y - half_size <= 0:
                sim_y = half_size
                sim_vy = abs(sim_vy)
            elif sim_y + half_size >= SCREEN_HEIGHT:
                sim_y = SCREEN_HEIGHT - half_size
                sim_vy = -abs(sim_vy)

            # Verificar si llegó al objetivo
            if sim_x >= target_x:
                return sim_y

            iterations += 1

        # Si no se alcanzó, retornar posición actual
        return sim_y

    def _add_error(self) -> float:
        """
        Añade error a la predicción basado en dificultad.

        Returns:
            Error en pixeles
        """
        error_range = self.settings['prediction_error']
        return random.uniform(-error_range, error_range)

    def _update_drift(self, dt: float):
        """
        Actualiza el sistema de desenfoque aleatorio.
        El bot pierde momentáneamente el foco del objetivo.

        Args:
            dt: Delta time en segundos
        """
        focus_drift = self.settings.get('focus_drift', 0.3)
        drift_speed = self.settings.get('drift_speed', 1.0)

        # Actualizar timer del drift
        self.drift_timer -= dt

        # Cuando el timer expira, calcular nuevo objetivo de drift
        if self.drift_timer <= 0:
            # Rango de desenfoque basado en dificultad (% de la pantalla)
            max_drift = SCREEN_HEIGHT * focus_drift * 0.5

            # Nuevo objetivo de drift aleatorio
            self.drift_target = random.uniform(-max_drift, max_drift)

            # Resetear timer (intervalo aleatorio)
            self.drift_timer = random.uniform(0.5, 2.0)

        # Interpolar suavemente hacia el objetivo de drift
        drift_delta = self.drift_target - self.drift_offset
        self.drift_offset += drift_delta * drift_speed * dt

    def _get_movement_direction(self, current_y: float, target_y: float) -> int:
        """
        Calcula la dirección de movimiento hacia el objetivo.

        Args:
            current_y: Posición Y actual
            target_y: Posición Y objetivo

        Returns:
            -1 (arriba), 0 (quieto), 1 (abajo)
        """
        # Zona muerta para evitar oscilaciones
        threshold = SHIP_HEIGHT // 4

        if target_y < current_y - threshold:
            return -1  # Mover arriba
        elif target_y > current_y + threshold:
            return 1   # Mover abajo

        return 0  # Quieto

    def set_difficulty(self, difficulty: str):
        """
        Cambia la dificultad del bot.

        Args:
            difficulty: 'easy', 'medium', o 'hard'
        """
        self.difficulty = difficulty
        self.settings = AI_DIFFICULTY.get(difficulty, AI_DIFFICULTY['medium'])

    def get_target_y(self) -> float:
        """Retorna la posición Y objetivo actual"""
        return self.target_y

    def reset(self):
        """Reinicia el estado del controlador"""
        self.target_y = SCREEN_HEIGHT // 2
        self.reaction_timer = 0
        self.current_error = 0
        self.is_returning_to_center = False
        self.last_ball_direction = 0
        # Reset del sistema de drift
        self.drift_offset = 0
        self.drift_timer = 0
        self.drift_target = 0
