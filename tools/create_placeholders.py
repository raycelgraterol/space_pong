#!/usr/bin/env python3
"""
Crear sprites placeholder usando pygame
"""
import pygame
import random
from pathlib import Path

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'assets' / 'images'


def create_ship_sprite(width, height, color, filename):
    """Crea un sprite de nave simple"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # Dibujar forma de nave
    pygame.draw.ellipse(surface, color, (10, 10, width - 20, height - 20))
    pygame.draw.ellipse(surface, (255, 255, 255), (15, 15, width - 30, height - 30), 2)

    # Guardar
    output_path = OUTPUT_DIR / 'ships' / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(output_path))
    print(f"Creado: {output_path}")


def create_ball_sprite(size, filename):
    """Crea el sprite del meteorito"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)

    center = size // 2
    pygame.draw.circle(surface, (139, 69, 19), (center, center), center - 5)
    pygame.draw.circle(surface, (160, 82, 45), (center, center), center - 10)

    for i in range(8):
        angle = i * 45
        import math
        x = center + int(math.cos(math.radians(angle)) * (center - 3))
        y = center + int(math.sin(math.radians(angle)) * (center - 3))
        pygame.draw.circle(surface, (255, 100, 0), (x, y), 5)

    output_path = OUTPUT_DIR / 'ball' / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(output_path))
    print(f"Creado: {output_path}")


def create_star_tile(size, filename):
    """Crea un tile de fondo con estrellas"""
    surface = pygame.Surface((size, size))
    surface.fill((10, 10, 25))

    random.seed(42)
    for _ in range(30):
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        brightness = random.randint(150, 255)
        star_size = random.choice([1, 1, 1, 2])
        pygame.draw.circle(surface, (brightness, brightness, brightness - 20), (x, y), star_size)

    output_path = OUTPUT_DIR / 'backgrounds' / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(output_path))
    print(f"Creado: {output_path}")


def create_star_tile_dense(size, filename):
    """Crea un tile con alta densidad de estrellas"""
    surface = pygame.Surface((size, size))
    surface.fill((10, 10, 25))

    random.seed(101)
    for _ in range(70):
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        brightness = random.randint(180, 255)
        star_size = random.choice([1, 1, 2, 2, 3])
        pygame.draw.circle(surface, (brightness, brightness, brightness - 10), (x, y), star_size)

    output_path = OUTPUT_DIR / 'backgrounds' / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(output_path))
    print(f"Creado: {output_path}")


def create_star_tile_sparse(size, filename):
    """Crea un tile con pocas estrellas grandes"""
    surface = pygame.Surface((size, size))
    surface.fill((8, 8, 20))

    random.seed(202)
    for _ in range(12):
        x = random.randint(5, size - 5)
        y = random.randint(5, size - 5)
        brightness = random.randint(200, 255)
        star_size = random.choice([2, 3, 3, 4])
        pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), star_size)
        pygame.draw.circle(surface, (brightness // 2, brightness // 2, brightness // 2), (x, y), star_size + 2, 1)

    output_path = OUTPUT_DIR / 'backgrounds' / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(output_path))
    print(f"Creado: {output_path}")


def create_star_tile_nebula(size, filename):
    """Crea un tile con efecto de nebulosa colorida"""
    surface = pygame.Surface((size, size))
    surface.fill((10, 10, 25))

    random.seed(303)
    for _ in range(5):
        x = random.randint(0, size)
        y = random.randint(0, size)
        colors = [(30, 20, 80), (50, 20, 60), (40, 15, 50)]
        color = random.choice(colors)
        radius = random.randint(20, 40)
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -3):
            alpha = int(30 * (r / radius))
            pygame.draw.circle(glow, (*color, alpha), (radius, radius), r)
        surface.blit(glow, (x - radius, y - radius))

    for _ in range(25):
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        brightness = random.randint(150, 255)
        star_size = random.choice([1, 1, 2])
        if random.random() > 0.7:
            color = random.choice([(brightness, brightness // 2, brightness),
                                   (brightness // 2, brightness // 2, brightness),
                                   (brightness, brightness, brightness // 2)])
        else:
            color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (x, y), star_size)

    output_path = OUTPUT_DIR / 'backgrounds' / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(output_path))
    print(f"Creado: {output_path}")


def create_star_tile_cluster(size, filename):
    """Crea un tile con estrellas agrupadas en clusters"""
    surface = pygame.Surface((size, size))
    surface.fill((10, 10, 25))

    random.seed(404)
    num_clusters = random.randint(4, 5)
    for _ in range(num_clusters):
        cx = random.randint(15, size - 15)
        cy = random.randint(15, size - 15)
        num_stars = random.randint(3, 6)
        for _ in range(num_stars):
            offset_x = random.randint(-12, 12)
            offset_y = random.randint(-12, 12)
            x = cx + offset_x
            y = cy + offset_y
            if 0 <= x < size and 0 <= y < size:
                brightness = random.randint(180, 255)
                star_size = random.choice([1, 1, 2])
                pygame.draw.circle(surface, (brightness, brightness, brightness - 15), (x, y), star_size)

    for _ in range(8):
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        brightness = random.randint(120, 200)
        pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), 1)

    output_path = OUTPUT_DIR / 'backgrounds' / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(output_path))
    print(f"Creado: {output_path}")


def create_laser_grid(width, height, filename):
    """Crea la malla laser central"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    center_x = width // 2
    pygame.draw.line(surface, (255, 50, 50), (center_x, 0), (center_x, height), 3)

    for i in range(1, 5):
        alpha = 150 - i * 30
        color = (255, 100, 100, alpha)
        glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.line(glow_surface, color,
                         (center_x - i * 2, 0), (center_x - i * 2, height), 2)
        pygame.draw.line(glow_surface, color,
                         (center_x + i * 2, 0), (center_x + i * 2, height), 2)
        surface.blit(glow_surface, (0, 0))

    for y in range(0, height, 20):
        pygame.draw.line(surface, (255, 150, 150),
                         (center_x - 5, y), (center_x + 5, y), 1)

    output_path = OUTPUT_DIR / 'effects' / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(output_path))
    print(f"Creado: {output_path}")


def main():
    """Crea todos los sprites placeholder"""
    print("=" * 50)
    print("Space Pong - Crear Sprites Placeholder")
    print("=" * 50)

    pygame.init()

    print("\nCreando sprites...")

    create_ship_sprite(80, 100, (100, 150, 255), 'ship_crystal.png')
    create_ship_sprite(100, 60, (100, 255, 150), 'ship_ufo.png')

    create_ball_sprite(50, 'meteorite.png')

    create_star_tile(128, 'star_tile.png')
    create_star_tile_dense(128, 'star_tile_dense.png')
    create_star_tile_sparse(128, 'star_tile_sparse.png')
    create_star_tile_nebula(128, 'star_tile_nebula.png')
    create_star_tile_cluster(128, 'star_tile_cluster.png')

    create_laser_grid(20, 720, 'laser_grid.png')

    pygame.quit()

    print("\nSprites placeholder creados exitosamente!")
    print(f"Ubicacion: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
