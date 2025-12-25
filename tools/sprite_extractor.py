#!/usr/bin/env python3
"""
Space Pong - Sprite Extractor
=============================

Herramienta para extraer sprites individuales de la imagen compuesta.
Analiza la imagen y extrae cada elemento a archivos PNG separados.

Uso:
    python tools/sprite_extractor.py
"""

from PIL import Image
from pathlib import Path
import sys


# Rutas
PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_IMAGE = PROJECT_ROOT / 'images' / 'recuadro-imagenes-multiples.png'
OUTPUT_DIR = PROJECT_ROOT / 'assets' / 'images'


# Definición de sprites a extraer (coordenadas aproximadas basadas en la imagen)
# Formato: (nombre, (x, y, ancho, alto), carpeta_destino, rotacion)
SPRITES_TO_EXTRACT = [
    # Nave 1: Esfera/Cápsula espacial (arriba izquierda)
    {
        'name': 'ship_crystal',
        'bbox': (20, 10, 170, 180),  # (left, top, right, bottom)
        'output_dir': 'ships',
        'rotation': 0,
        'scale': (80, 100)
    },
    # Nave 2: OVNI Verde (abajo derecha)
    {
        'name': 'ship_ufo',
        'bbox': (70, 420, 230, 520),
        'output_dir': 'ships',
        'rotation': 0,
        'scale': (100, 60)
    },
    # Meteorito en llamas (centro izquierda)
    {
        'name': 'meteorite',
        'bbox': (10, 185, 170, 350),
        'output_dir': 'ball',
        'rotation': 0,
        'scale': (50, 50)
    },
    # Tiles de estrellas 1 (pequeño, arriba derecha)
    {
        'name': 'star_tile_1',
        'bbox': (175, 10, 235, 70),
        'output_dir': 'backgrounds',
        'rotation': 0,
        'scale': None  # Mantener tamaño original
    },
    # Tiles de estrellas 2 (medio)
    {
        'name': 'star_tile_2',
        'bbox': (175, 75, 235, 135),
        'output_dir': 'backgrounds',
        'rotation': 0,
        'scale': None
    },
    # Tiles de estrellas 3
    {
        'name': 'star_tile_3',
        'bbox': (175, 140, 235, 200),
        'output_dir': 'backgrounds',
        'rotation': 0,
        'scale': None
    },
    # Elemento rojo con estrellas (para efectos/láser)
    {
        'name': 'laser_decoration',
        'bbox': (10, 350, 230, 420),
        'output_dir': 'effects',
        'rotation': 90,  # Rotar para uso vertical
        'scale': None
    },
    # Tile de estrellas grande (abajo izquierda)
    {
        'name': 'star_tile_large',
        'bbox': (5, 325, 65, 390),
        'output_dir': 'backgrounds',
        'rotation': 0,
        'scale': None
    },
]


def extract_sprite(image: Image.Image, sprite_def: dict) -> Image.Image:
    """
    Extrae un sprite de la imagen fuente.

    Args:
        image: Imagen PIL fuente
        sprite_def: Diccionario con definición del sprite

    Returns:
        Imagen PIL del sprite extraído
    """
    # Recortar
    sprite = image.crop(sprite_def['bbox'])

    # Rotar si es necesario
    if sprite_def.get('rotation', 0) != 0:
        sprite = sprite.rotate(
            sprite_def['rotation'],
            expand=True,
            resample=Image.Resampling.BICUBIC
        )

    # Escalar si está especificado
    if sprite_def.get('scale'):
        sprite = sprite.resize(
            sprite_def['scale'],
            resample=Image.Resampling.LANCZOS
        )

    return sprite


def create_placeholder_sprites():
    """
    Crea sprites placeholder si no se puede extraer de la imagen.
    Útil para desarrollo mientras no se tienen los assets finales.
    """
    print("Creando sprites placeholder...")

    # Nave 1 (rectángulo azul)
    ship1 = Image.new('RGBA', (80, 100), (0, 0, 0, 0))
    for y in range(100):
        for x in range(80):
            # Forma de nave simple
            if 20 < x < 60 and 10 < y < 90:
                ship1.putpixel((x, y), (100, 150, 255, 255))
    ship1_path = OUTPUT_DIR / 'ships' / 'ship_crystal.png'
    ship1_path.parent.mkdir(parents=True, exist_ok=True)
    ship1.save(ship1_path)
    print(f"  Creado: {ship1_path}")

    # Nave 2 (rectángulo verde)
    ship2 = Image.new('RGBA', (100, 60), (0, 0, 0, 0))
    for y in range(60):
        for x in range(100):
            if 10 < x < 90 and 10 < y < 50:
                ship2.putpixel((x, y), (100, 255, 150, 255))
    ship2_path = OUTPUT_DIR / 'ships' / 'ship_ufo.png'
    ship2.save(ship2_path)
    print(f"  Creado: {ship2_path}")

    # Meteorito (círculo naranja)
    ball = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
    center = 25
    for y in range(50):
        for x in range(50):
            dist = ((x - center) ** 2 + (y - center) ** 2) ** 0.5
            if dist < 20:
                # Gradiente de naranja a rojo
                intensity = int(255 * (1 - dist / 25))
                ball.putpixel((x, y), (255, intensity, 50, 255))
    ball_path = OUTPUT_DIR / 'ball' / 'meteorite.png'
    ball_path.parent.mkdir(parents=True, exist_ok=True)
    ball.save(ball_path)
    print(f"  Creado: {ball_path}")

    # Tile de estrellas (fondo negro con puntos)
    tile = Image.new('RGBA', (64, 64), (10, 10, 25, 255))
    import random
    random.seed(42)  # Para reproducibilidad
    for _ in range(20):
        x, y = random.randint(0, 63), random.randint(0, 63)
        brightness = random.randint(150, 255)
        tile.putpixel((x, y), (brightness, brightness, brightness - 20, 255))
    tile_path = OUTPUT_DIR / 'backgrounds' / 'star_tile.png'
    tile_path.parent.mkdir(parents=True, exist_ok=True)
    tile.save(tile_path)
    print(f"  Creado: {tile_path}")

    # Efecto láser (línea roja con glow)
    laser = Image.new('RGBA', (10, 200), (0, 0, 0, 0))
    for y in range(200):
        for x in range(10):
            dist_from_center = abs(x - 5)
            if dist_from_center < 2:
                laser.putpixel((x, y), (255, 50, 50, 255))
            elif dist_from_center < 4:
                alpha = int(200 * (1 - dist_from_center / 5))
                laser.putpixel((x, y), (255, 100, 100, alpha))
    laser_path = OUTPUT_DIR / 'effects' / 'laser_grid.png'
    laser_path.parent.mkdir(parents=True, exist_ok=True)
    laser.save(laser_path)
    print(f"  Creado: {laser_path}")

    print("\nSprites placeholder creados exitosamente!")


def extract_all_sprites():
    """
    Extrae todos los sprites definidos de la imagen fuente.
    """
    print(f"Buscando imagen fuente: {SOURCE_IMAGE}")

    if not SOURCE_IMAGE.exists():
        print(f"ERROR: No se encontró la imagen fuente: {SOURCE_IMAGE}")
        print("Creando sprites placeholder en su lugar...")
        create_placeholder_sprites()
        return False

    try:
        # Abrir imagen fuente
        source = Image.open(SOURCE_IMAGE).convert('RGBA')
        print(f"Imagen cargada: {source.size[0]}x{source.size[1]} pixels")

        extracted_count = 0

        for sprite_def in SPRITES_TO_EXTRACT:
            try:
                # Extraer sprite
                sprite = extract_sprite(source, sprite_def)

                # Crear directorio de destino
                output_path = OUTPUT_DIR / sprite_def['output_dir'] / f"{sprite_def['name']}.png"
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Guardar
                sprite.save(output_path, 'PNG')
                print(f"  Extraído: {output_path.name} ({sprite.size[0]}x{sprite.size[1]})")
                extracted_count += 1

            except Exception as e:
                print(f"  ERROR extrayendo {sprite_def['name']}: {e}")

        print(f"\nExtracción completada: {extracted_count}/{len(SPRITES_TO_EXTRACT)} sprites")

        # Si no se extrajo ninguno, crear placeholders
        if extracted_count == 0:
            print("No se pudo extraer ningún sprite, creando placeholders...")
            create_placeholder_sprites()

        return extracted_count > 0

    except Exception as e:
        print(f"ERROR abriendo imagen: {e}")
        print("Creando sprites placeholder...")
        create_placeholder_sprites()
        return False


def interactive_extractor():
    """
    Modo interactivo para ajustar coordenadas de extracción.
    Útil para calibrar las bounding boxes de los sprites.
    """
    try:
        import pygame
        pygame.init()

        if not SOURCE_IMAGE.exists():
            print(f"No se encontró: {SOURCE_IMAGE}")
            return

        # Cargar imagen
        source = pygame.image.load(str(SOURCE_IMAGE))
        img_width, img_height = source.get_size()

        # Crear ventana más grande para ver mejor
        scale = 2
        screen = pygame.display.set_mode((img_width * scale, img_height * scale))
        pygame.display.set_caption("Sprite Extractor - Click para ver coordenadas")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    real_x, real_y = x // scale, y // scale
                    print(f"Coordenadas: ({real_x}, {real_y})")

            # Dibujar imagen escalada
            scaled = pygame.transform.scale(source, (img_width * scale, img_height * scale))
            screen.blit(scaled, (0, 0))

            # Dibujar cursor de coordenadas
            mx, my = pygame.mouse.get_pos()
            pygame.draw.line(screen, (255, 0, 0), (mx, 0), (mx, img_height * scale), 1)
            pygame.draw.line(screen, (255, 0, 0), (0, my), (img_width * scale, my), 1)

            pygame.display.flip()

        pygame.quit()

    except ImportError:
        print("Pygame no disponible para modo interactivo")


def main():
    """Función principal"""
    print("=" * 50)
    print("Space Pong - Sprite Extractor")
    print("=" * 50)

    # Verificar argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive':
            interactive_extractor()
            return
        elif sys.argv[1] == '--placeholders':
            create_placeholder_sprites()
            return

    # Extracción normal
    success = extract_all_sprites()

    if success:
        print("\n¡Sprites listos para usar!")
    else:
        print("\nSe crearon placeholders. Puedes reemplazarlos con assets reales.")

    print("\nUso:")
    print("  python sprite_extractor.py              - Extraer sprites")
    print("  python sprite_extractor.py --interactive - Modo interactivo")
    print("  python sprite_extractor.py --placeholders - Solo crear placeholders")


if __name__ == '__main__':
    main()
