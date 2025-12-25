# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Space Pong ("Tenis Espacial") is a space-themed Pong game built with Pygame. Players control spaceships that bounce a meteorite, with a central laser grid hazard. Supports PvP and PvE modes with configurable AI difficulty.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py

# Extract sprites from composite image
python tools/sprite_extractor.py

# Create placeholder sprites (for development)
python tools/sprite_extractor.py --placeholders

# Interactive sprite extraction (calibration)
python tools/sprite_extractor.py --interactive
```

## Architecture

### Game Loop Pattern
The game uses a classic game loop in [game.py](src/core/game.py): events → update → render, with delta time for frame-independent movement.

### State Machine
Game flow is managed through a state machine pattern:
- `StateManager` in [state_manager.py](src/managers/state_manager.py) handles state transitions
- States inherit from `BaseState` ([base_state.py](src/states/base_state.py)) implementing `handle_event()`, `update(dt)`, `render(screen)`
- States: `MenuState`, `PlayState` (registered via `GameState` enum)
- Change states via `game.state_manager.change_state(GameState.NAME)`

### Entity-Component Pattern
Entities inherit from `Entity` base class ([base_entity.py](src/entities/base_entity.py)) providing:
- Position/velocity via `pygame.math.Vector2`
- Rect-based collision detection
- Sprite rendering with `update(dt)` and `render(screen)` lifecycle

### Systems
Game logic is separated into systems in `src/systems/`:
- `InputHandler`: Maps keyboard input to ship movement
- `PhysicsSystem`: Ball movement, wall bounces, paddle bounce calculations
- `CollisionSystem`: Collision detection returning `CollisionResult` dataclass
- `AIController`: Ball trajectory prediction for bot movement

### Singleton Managers
- `AssetManager`: Lazy-loads and caches images/sounds/fonts. Access via `get_asset_manager()`
- `Settings`: Persistent config stored at `~/.space_pong/settings.json`. Access via `get_settings()`

### Constants
All game constants (speeds, dimensions, colors, controls, paths) centralized in [constants.py](src/core/constants.py).

## Key Game Mechanics

- Ships move vertically only, controlled by W/S (P1) or arrows (P2)
- Meteorite bounces at angles based on where it hits the paddle (edge = sharper angle)
- Ball speed increases by 5% on each paddle hit, capped at `BALL_MAX_SPEED`
- Touching the central laser grid awards a point to opponent
- First to `WINNING_SCORE` (default 10) wins

## Language

Codebase uses Spanish for comments, docstrings, and UI text.
