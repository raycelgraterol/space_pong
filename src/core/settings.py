"""
Space Pong - Game Settings
Configuraciones dinámicas y persistentes del juego
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    AI_DIFFICULTY, GameMode
)


@dataclass
class VideoSettings:
    """Configuración de video"""
    width: int = SCREEN_WIDTH
    height: int = SCREEN_HEIGHT
    fullscreen: bool = False
    fps: int = FPS
    vsync: bool = True


@dataclass
class AudioSettings:
    """Configuración de audio"""
    master_volume: float = 1.0
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    muted: bool = False


@dataclass
class GameplaySettings:
    """Configuración de gameplay"""
    winning_score: int = 10
    ai_difficulty: str = 'medium'
    game_mode: str = GameMode.PVE


@dataclass
class Settings:
    """Configuración principal del juego"""
    video: VideoSettings = field(default_factory=VideoSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)
    gameplay: GameplaySettings = field(default_factory=GameplaySettings)

    # Ruta del archivo de configuración
    _config_path: Optional[Path] = field(default=None, repr=False)

    def __post_init__(self):
        """Inicializa la ruta de configuración"""
        if self._config_path is None:
            self._config_path = Path.home() / '.space_pong' / 'settings.json'

    def save(self) -> bool:
        """
        Guarda la configuración en archivo JSON
        Returns: True si se guardó correctamente
        """
        try:
            # Crear directorio si no existe
            self._config_path.parent.mkdir(parents=True, exist_ok=True)

            # Convertir a diccionario (excluyendo _config_path)
            data = {
                'video': asdict(self.video),
                'audio': asdict(self.audio),
                'gameplay': asdict(self.gameplay)
            }

            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False

    def load(self) -> bool:
        """
        Carga la configuración desde archivo JSON
        Returns: True si se cargó correctamente
        """
        try:
            if not self._config_path.exists():
                return False

            with open(self._config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Actualizar configuraciones
            if 'video' in data:
                self.video = VideoSettings(**data['video'])
            if 'audio' in data:
                self.audio = AudioSettings(**data['audio'])
            if 'gameplay' in data:
                self.gameplay = GameplaySettings(**data['gameplay'])

            return True
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return False

    def reset_to_defaults(self):
        """Restaura todas las configuraciones a valores por defecto"""
        self.video = VideoSettings()
        self.audio = AudioSettings()
        self.gameplay = GameplaySettings()

    def get_ai_settings(self) -> dict:
        """Obtiene la configuración de IA según la dificultad actual"""
        return AI_DIFFICULTY.get(
            self.gameplay.ai_difficulty,
            AI_DIFFICULTY['medium']
        )

    def get_display_size(self) -> tuple[int, int]:
        """Retorna las dimensiones de pantalla actuales"""
        return (self.video.width, self.video.height)

    def get_effective_volume(self, volume_type: str) -> float:
        """
        Calcula el volumen efectivo considerando master y mute
        Args:
            volume_type: 'music' o 'sfx'
        """
        if self.audio.muted:
            return 0.0

        base_volume = (
            self.audio.music_volume if volume_type == 'music'
            else self.audio.sfx_volume
        )
        return base_volume * self.audio.master_volume


# Instancia global de configuración (singleton pattern)
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Obtiene la instancia global de Settings
    Carga desde archivo si existe, si no usa valores por defecto
    """
    global _settings_instance

    if _settings_instance is None:
        _settings_instance = Settings()
        _settings_instance.load()  # Intenta cargar, si falla usa defaults

    return _settings_instance
