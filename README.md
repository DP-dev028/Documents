# Realistic Flappy Bird Clone

A polished Flappy Bird clone made with Pygame, featuring realistic physics, animations, and visual effects.

![Flappy Bird](https://i.imgur.com/2NpYTLw.png)

## Features

- **Smooth Animations**
  - Wing flapping animation
  - Dynamic bird rotation based on velocity
  - Seamless scrolling background and ground

- **Visual Effects**
  - Screen shake on impacts
  - Particle effects for collisions
  - Score popup animations
  - Fade effects

- **Game Mechanics**
  - Physics-based movement
  - Collision detection
  - Progressive difficulty
  - High score system

- **Polish**
  - Sound effects with volume control
  - Smooth animations
  - Visual feedback for all actions
  - Game over screen with restart option

## Requirements

- Python 3.x
- Pygame

## Installation

1. Clone this repository:
```bash
git clone https://github.com/DP-dev028/Flappy-Bird-in-Python.git
cd Flappy-Bird-in-Python
```

2. Install Pygame:
```bash
pip install pygame
```

3. Make sure you have the required assets in the correct folders:
   - `graphics/` folder: bird-1.png, bird-2.png, pipe_top.png, pipe_bottom.png, ground.png, background.png
   - `sounds/` folder: jump.wav, score.wav, hit.wav, die.wav

## How to Play

1. Run the game:
```bash
python main.py
```

2. Controls:
   - Press SPACE to make the bird flap/jump
   - Press R to restart after game over
   - Close window to quit

## Game Features Explained

### Bird Physics
- Gravity affects the bird's movement
- Jumping gives upward velocity
- Bird rotates based on velocity direction

### Visual Effects
- **Screen Shake**: Occurs on collisions with pipes or ground
- **Particle Effects**: 
  - Green particles when hitting pipes
  - Brown particles when hitting ground
- **Score Popups**: Floating numbers appear when scoring points

### Sound Effects
- Jump sound when flapping
- Scoring sound when passing pipes
- Impact sound on collisions
- Death sound when game over

## Credits

- Original Flappy Bird game by Dong Nguyen
- Pygame implementation with enhanced features and effects

## License

This project is open source and available under the MIT License.


