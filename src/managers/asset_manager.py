"""
Space Pong - Asset Manager
Gestiona la carga y caché de todos los recursos del juego
"""

import pygame
from pathlib import Path
from typing import Optional

from ..core.constants import (
    ASSETS_DIR, IMAGES_DIR, SOUNDS_DIR, FONTS_DIR,
    SHIPS_DIR, BALL_DIR, EFFECTS_DIR, BACKGROUNDS_DIR
)


class AssetManager:
    """
    Singleton para gestión de assets del juego.
    Carga y cachea imágenes, sonidos y fuentes.
    """

    _instance: Optional['AssetManager'] = None

    def __new__(cls):
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializa el manager si no está inicializado"""
        if self._initialized:
            return

        self._initialized = True

        # Cachés de recursos
        self._images: dict[str, pygame.Surface] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._fonts: dict[tuple[str, int], pygame.font.Font] = {}

        # Pre-cargar assets esenciales
        self._preload_essential_assets()

    def _preload_essential_assets(self):
        """Carga los assets esenciales al inicio"""
        print("Cargando assets...")

        # Cargar naves
        self.load_image('ship_crystal', SHIPS_DIR / 'ship_crystal.png')
        self.load_image('ship_ufo', SHIPS_DIR / 'ship_ufo.png')

        # Cargar meteorito
        self.load_image('meteorite', BALL_DIR / 'meteorite.png')

        # Cargar efectos
        self.load_image('laser_grid', EFFECTS_DIR / 'laser_grid.png')

        # Cargar fondos
        self.load_image('star_tile', BACKGROUNDS_DIR / 'star_tile.png')

        print(f"Assets cargados: {len(self._images)} imágenes")

    def load_image(
        self,
        name: str,
        path: Path,
        convert_alpha: bool = True,
        scale: Optional[tuple[int, int]] = None
    ) -> Optional[pygame.Surface]:
        """
        Carga una imagen y la almacena en caché.

        Args:
            name: Nombre identificador del asset
            path: Ruta al archivo de imagen
            convert_alpha: Si debe convertir con alpha (transparencia)
            scale: Tupla (ancho, alto) para redimensionar

        Returns:
            pygame.Surface o None si falla
        """
        if name in self._images:
            return self._images[name]

        try:
            if not path.exists():
                print(f"  AVISO: No se encontró imagen: {path}")
                return None

            image = pygame.image.load(str(path))

            if convert_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()

            if scale:
                image = pygame.transform.scale(image, scale)

            self._images[name] = image
            print(f"  Cargado: {name}")
            return image

        except Exception as e:
            print(f"  ERROR cargando {name}: {e}")
            return None

    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """
        Obtiene una imagen cargada.

        Args:
            name: Nombre identificador del asset

        Returns:
            pygame.Surface o None si no existe
        """
        return self._images.get(name)

    def get_image_copy(self, name: str) -> Optional[pygame.Surface]:
        """
        Obtiene una copia de una imagen (para modificaciones).

        Args:
            name: Nombre identificador del asset

        Returns:
            Copia de pygame.Surface o None
        """
        image = self._images.get(name)
        if image:
            return image.copy()
        return None

    def load_sound(self, name: str, path: Path) -> Optional[pygame.mixer.Sound]:
        """
        Carga un sonido y lo almacena en caché.

        Args:
            name: Nombre identificador del sonido
            path: Ruta al archivo de sonido

        Returns:
            pygame.mixer.Sound o None si falla
        """
        if name in self._sounds:
            return self._sounds[name]

        try:
            if not path.exists():
                print(f"  AVISO: No se encontró sonido: {path}")
                return None

            sound = pygame.mixer.Sound(str(path))
            self._sounds[name] = sound
            return sound

        except Exception as e:
            print(f"  ERROR cargando sonido {name}: {e}")
            return None

    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Obtiene un sonido cargado"""
        return self._sounds.get(name)

    def get_font(
        self,
        name: Optional[str] = None,
        size: int = 36
    ) -> pygame.font.Font:
        """
        Obtiene una fuente, cargándola si es necesario.

        Args:
            name: Nombre del archivo de fuente (None para fuente por defecto)
            size: Tamaño de la fuente

        Returns:
            pygame.font.Font
        """
        cache_key = (name, size)

        if cache_key in self._fonts:
            return self._fonts[cache_key]

        try:
            if name:
                font_path = FONTS_DIR / name
                if font_path.exists():
                    font = pygame.font.Font(str(font_path), size)
                else:
                    font = pygame.font.Font(None, size)
            else:
                font = pygame.font.Font(None, size)

            self._fonts[cache_key] = font
            return font

        except Exception as e:
            print(f"Error cargando fuente: {e}")
            return pygame.font.Font(None, size)

    def create_scaled_image(
        self,
        name: str,
        new_name: str,
        scale: tuple[int, int]
    ) -> Optional[pygame.Surface]:
        """
        Crea una versión escalada de una imagen existente.

        Args:
            name: Nombre de la imagen original
            new_name: Nombre para la versión escalada
            scale: Nuevo tamaño (ancho, alto)

        Returns:
            Imagen escalada o None
        """
        original = self.get_image(name)
        if original is None:
            return None

        scaled = pygame.transform.scale(original, scale)
        self._images[new_name] = scaled
        return scaled

    def create_rotated_image(
        self,
        name: str,
        new_name: str,
        angle: float
    ) -> Optional[pygame.Surface]:
        """
        Crea una versión rotada de una imagen existente.

        Args:
            name: Nombre de la imagen original
            new_name: Nombre para la versión rotada
            angle: Ángulo de rotación en grados

        Returns:
            Imagen rotada o None
        """
        original = self.get_image(name)
        if original is None:
            return None

        rotated = pygame.transform.rotate(original, angle)
        self._images[new_name] = rotated
        return rotated

    def unload_image(self, name: str):
        """Elimina una imagen de la caché"""
        if name in self._images:
            del self._images[name]

    def clear_cache(self):
        """Limpia toda la caché de recursos"""
        self._images.clear()
        self._sounds.clear()
        self._fonts.clear()

    def get_stats(self) -> dict:
        """Retorna estadísticas de recursos cargados"""
        return {
            'images': len(self._images),
            'sounds': len(self._sounds),
            'fonts': len(self._fonts)
        }


# Función de conveniencia para obtener el singleton
def get_asset_manager() -> AssetManager:
    """Obtiene la instancia del AssetManager"""
    return AssetManager()
