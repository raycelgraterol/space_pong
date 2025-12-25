#!/usr/bin/env python3
"""
Space Pong - Tenis Espacial
===========================

Un juego de Pong espacial con naves, meteoritos y mallas láser.

Ejecutar:
    python main.py

Controles:
    Jugador 1: W/S (arriba/abajo)
    Jugador 2: Flechas arriba/abajo
    ESC: Pausar/Salir
    F11: Pantalla completa
    F3: Mostrar/ocultar FPS

Autor: Generado con Claude Code
"""

import sys
from pathlib import Path

# Asegurar que el directorio src está en el path
src_path = Path(__file__).parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def main():
    """Punto de entrada principal del juego"""
    try:
        from src.core.game import Game

        # Crear e iniciar el juego
        game = Game()
        game.run()

    except ImportError as e:
        print(f"Error de importación: {e}")
        print("Asegúrate de haber instalado las dependencias:")
        print("    pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
