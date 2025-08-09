# Realistic Flappy Bird using Pygame and external assets
import pygame
import sys
import random
import os
import math

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 100
PIPE_GAP = 150
PIPE_DISTANCE = 250
BIRD_START_POS = (100, 300)

# Asset paths
GRAPHICS_PATH = os.path.join(os.path.dirname(__file__), "graphics")
SOUNDS_PATH = os.path.join(os.path.dirname(__file__), "sounds")

# Initialize Pygame mixer for sounds
pygame.mixer.init()


def load_image(name):
    image = pygame.image.load(os.path.join(GRAPHICS_PATH, name)).convert_alpha()
    # Scale images to more reasonable sizes
    if name.startswith(
        "bird"
    ):  # Handle all bird-related images (bird-1.png, bird-2.png)
        return pygame.transform.scale(image, (40, 30))
    elif name.startswith("pipe"):
        return pygame.transform.scale(image, (52, 320))
    elif name == "ground.png":
        return pygame.transform.scale(image, (SCREEN_WIDTH, GROUND_HEIGHT))
    elif name == "background.png":
        return pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    return image


def load_sound(name):
    try:
        sound = pygame.mixer.Sound(os.path.join(SOUNDS_PATH, name))
        sound.set_volume(0.3)  # Set a reasonable volume
        return sound
    except:  # noqa: E722
        print(f"Could not load sound: {name}")
        return None


class Bird:
    def __init__(self):
        # Load two animation frames for wing positions
        self.frames = [
            load_image("bird-1.png"),
            load_image("bird-2.png"),
        ]  # Up and down wing positions
        self.frame_index = 0
        self.animation_speed = 0.15  # Adjust speed of wing flapping (lower = faster)
        self.animation_time = 0
        self.flap_up = True  # Track flap direction

        self.original_image = self.frames[0]
        self.rect = self.original_image.get_rect(center=BIRD_START_POS)
        self.velocity = 0
        self.gravity = 0.5
        self.jump_force = -8
        self.alive = True
        self.angle = 0
        self.max_angle = 30  # Maximum rotation angle

    def jump(self):
        if self.alive:
            self.velocity = self.jump_force
            self.angle = self.max_angle  # Point upward when jumping
            if Game.instance and Game.instance.jump_sound:
                Game.instance.jump_sound.play()

    def update(self):
        self.velocity += self.gravity
        self.rect.y += int(self.velocity)

        # Update wing flapping animation
        if self.alive:
            self.animation_time += 1
            if self.animation_time >= self.animation_speed * 60:  # 60 FPS
                self.animation_time = 0
                if self.flap_up:
                    self.frame_index = 1  # Wings down
                else:
                    self.frame_index = 0  # Wings up
                self.flap_up = not self.flap_up  # Switch direction
                self.original_image = self.frames[self.frame_index]

        # Update rotation based on velocity
        if self.velocity < 0:  # Going up
            self.angle = self.max_angle
        else:  # Falling
            self.angle = max(self.angle - 4, -90)  # Gradually rotate downward

        # Prevent bird from going off the top
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0

    def draw(self, screen):
        # Rotate the bird image
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        # Keep the center position while rotating
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect)


class Pipe:
    def __init__(self, x):
        self.image_top = load_image("pipe_top.png")
        self.image_bottom = load_image("pipe_bottom.png")
        self.x = x
        self.height = random.randint(
            100, SCREEN_HEIGHT - GROUND_HEIGHT - PIPE_GAP - 100
        )
        self.passed = False

    def get_rects(self):
        rect_top = self.image_top.get_rect(midbottom=(self.x, self.height))
        rect_bottom = self.image_bottom.get_rect(
            midtop=(self.x, self.height + PIPE_GAP)
        )
        return rect_top, rect_bottom

    def update(self):
        self.x -= 2

    def draw(self, screen):
        rect_top, rect_bottom = self.get_rects()
        screen.blit(self.image_top, rect_top)
        screen.blit(self.image_bottom, rect_bottom)


class Particle:
    def __init__(self, x, y, color=(255, 255, 255)):
        self.x = x
        self.y = y
        # Ensure color is a tuple of exactly 3 integers
        if isinstance(color, tuple) and len(color) >= 3:
            self.color = (int(color[0]), int(color[1]), int(color[2]))
        else:
            self.color = (255, 255, 255)
        self.size = random.randint(3, 6)  # Slightly larger particles
        angle = random.uniform(0, 2 * 3.14159)  # Random direction
        speed = random.uniform(4, 8)  # Faster particles
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.lifetime = random.randint(30, 50)  # Longer lifetime
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity effect
        self.lifetime -= 1
        self.alpha = int((self.lifetime / 40) * 255)  # Fade out
        return self.lifetime > 0

    def draw(self, screen):
        if self.alpha > 0:
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            # Create color with alpha, ensuring all values are integers
            try:
                color_with_alpha = (
                    min(255, max(0, int(self.color[0]))),
                    min(255, max(0, int(self.color[1]))),
                    min(255, max(0, int(self.color[2]))),
                    min(255, max(0, int(self.alpha))),
                )
                pygame.draw.circle(
                    surface,
                    color_with_alpha,
                    (self.size // 2, self.size // 2),
                    self.size // 2,
                )
                screen.blit(surface, (int(self.x), int(self.y)))
            except (TypeError, IndexError):
                pass  # Skip drawing if color is invalid


class Ground:
    def __init__(self):
        self.image = load_image("ground.png")
        self.x = 0
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.x -= 2
        if self.x <= -SCREEN_WIDTH:
            self.x = 0

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        screen.blit(self.image, (self.x + SCREEN_WIDTH, self.y))


class ScorePopup:
    def __init__(self, x, y, score):
        self.x = x
        self.y = y
        self.score = score
        self.alpha = 255  # For fade out effect
        self.lifetime = 60  # Number of frames the popup will live
        self.velocity_y = -2  # Moving upward
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

    def update(self):
        self.y += self.velocity_y
        self.lifetime -= 1
        # Fade out gradually
        self.alpha = int((self.lifetime / 60) * 255)
        return self.lifetime > 0

    def draw(self, screen):
        score_text = f"+{self.score}"
        text_surface = self.font.render(score_text, True, (255, 255, 255))
        # Create a copy with alpha
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((255, 255, 255, self.alpha))
        text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(text_surface, (self.x - text_surface.get_width() // 2, self.y))


class Game:
    instance = None
    HIGHSCORE_FILE = "highscore.txt"

    def __init__(self):
        Game.instance = self
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird - Realistic")
        self.clock = pygame.time.Clock()
        self.background = load_image("background.png")
        self.ground = Ground()
        self.bird = Bird()
        self.pipes = []
        self.score = 0

        # Score popup list
        self.score_popups = []

        # Particle effects
        self.particles = []

        # Screen shake properties
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset = [0, 0]
        self.high_score = self.load_high_score()
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24, bold=True)

        # Load sound effects
        self.jump_sound = load_sound("jump.wav")
        self.score_sound = load_sound("score.wav")
        self.hit_sound = load_sound("hit.wav")
        self.die_sound = load_sound("die.wav")

        self.spawn_pipe()
        self.game_over = False

    def spawn_pipe(self):
        if not self.pipes or self.pipes[-1].x < SCREEN_WIDTH - PIPE_DISTANCE:
            self.pipes.append(Pipe(SCREEN_WIDTH + 50))

    def reset(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.particles = []  # Clear particles
        self.score_popups = []  # Clear score popups
        self.shake_offset = [0, 0]  # Reset screen shake
        self.shake_duration = 0
        self.spawn_pipe()
        self.game_over = False

    def load_high_score(self):
        try:
            with open(self.HIGHSCORE_FILE, "r") as f:
                return int(f.read())
        except:  # noqa: E722
            return 0

    def save_high_score(self):
        with open(self.HIGHSCORE_FILE, "w") as f:
            f.write(str(self.high_score))

    def start_screen_shake(self, duration=10, intensity=5):
        self.shake_duration = duration
        self.shake_intensity = intensity

    def update_screen_shake(self):
        if self.shake_duration > 0:
            self.shake_duration -= 1
            self.shake_offset = [
                random.randint(-self.shake_intensity, self.shake_intensity),
                random.randint(-self.shake_intensity, self.shake_intensity),
            ]
        else:
            self.shake_offset = [0, 0]

    def spawn_particles(self, x, y, count=20, color=(255, 255, 255)):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def check_collision(self):
        if self.game_over:
            return

        bird_rect = self.bird.rect
        # Ground collision
        if bird_rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            self.bird.alive = False
            self.game_over = True
            self.start_screen_shake(15, 8)  # Stronger shake for ground impact
            # Spawn impact particles
            self.spawn_particles(bird_rect.centerx, bird_rect.bottom, 30, (139, 69, 19))
            # Update high score if the current score is higher
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            if self.hit_sound:
                self.hit_sound.play()
            if self.die_sound:
                self.die_sound.play()

        # Pipe collision
        for pipe in self.pipes:
            rect_top, rect_bottom = pipe.get_rects()
            if bird_rect.colliderect(rect_top) or bird_rect.colliderect(rect_bottom):
                self.bird.alive = False
                self.game_over = True
                self.start_screen_shake(12, 6)  # Medium shake for pipe collision
                # Spawn impact particles at collision point
                collision_x = bird_rect.centerx
                collision_y = bird_rect.centery
                # Brighter green particles with more count and multiple colors for pipe debris
                self.spawn_particles(
                    collision_x, collision_y, 20, (0, 255, 0)
                )  # Bright green
                self.spawn_particles(
                    collision_x, collision_y, 15, (144, 238, 144)
                )  # Light green
                self.spawn_particles(
                    collision_x, collision_y, 15, (0, 200, 0)
                )  # Medium green
                # Update high score if the current score is higher
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                if self.hit_sound:
                    self.hit_sound.play()
                if self.die_sound:
                    self.die_sound.play()

    def update_score(self):
        for pipe in self.pipes:
            if not pipe.passed and pipe.x < self.bird.rect.centerx:
                pipe.passed = True
                self.score += 1
                # Create a score popup at the bird's position
                self.score_popups.append(
                    ScorePopup(
                        self.bird.rect.centerx,
                        self.bird.rect.centery - 30,  # Slightly above the bird
                        1,
                    )
                )
                if self.score_sound:
                    self.score_sound.play()

    def update(self):
        if not self.game_over:
            self.bird.update()
            self.ground.update()
            for pipe in self.pipes:
                pipe.update()
            # Remove off-screen pipes
            self.pipes = [pipe for pipe in self.pipes if pipe.x > -80]
            self.spawn_pipe()
            self.check_collision()
            self.update_score()

            # Update score popups and remove finished ones
            self.score_popups = [popup for popup in self.score_popups if popup.update()]

        # Always update particles (even during game over)
        self.particles = [particle for particle in self.particles if particle.update()]

        # Always update screen shake
        self.update_screen_shake()

    def draw(self):
        # Apply screen shake offset to all game elements
        shake_x, shake_y = self.shake_offset
        self.screen.blit(self.background, (shake_x, shake_y))
        for pipe in self.pipes:
            pipe_top, pipe_bottom = pipe.get_rects()
            pipe_top.x += shake_x
            pipe_top.y += shake_y
            pipe_bottom.x += shake_x
            pipe_bottom.y += shake_y
            self.screen.blit(pipe.image_top, pipe_top)
            self.screen.blit(pipe.image_bottom, pipe_bottom)

        ground_rect = self.ground.image.get_rect(
            topleft=(self.ground.x + shake_x, self.ground.y + shake_y)
        )
        self.screen.blit(self.ground.image, ground_rect)
        ground_rect_2 = self.ground.image.get_rect(
            topleft=(self.ground.x + SCREEN_WIDTH + shake_x, self.ground.y + shake_y)
        )
        self.screen.blit(self.ground.image, ground_rect_2)

        bird_rect = self.bird.rect.copy()
        bird_rect.x += shake_x
        bird_rect.y += shake_y
        rotated_image = pygame.transform.rotate(
            self.bird.original_image, self.bird.angle
        )
        rotated_rect = rotated_image.get_rect(center=bird_rect.center)
        self.screen.blit(rotated_image, rotated_rect)

        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw score popups
        for popup in self.score_popups:
            popup.draw(self.screen)

        # Draw current score
        score_surf = self.font.render(str(self.score), True, (255, 255, 255))
        self.screen.blit(
            score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 30)
        )

        # Draw high score
        high_score_surf = self.small_font.render(
            f"High Score: {self.high_score}", True, (255, 215, 0)
        )
        self.screen.blit(high_score_surf, (10, 10))

        if self.game_over:
            # Draw game over message
            over_surf = self.font.render("Game Over! Press R", True, (255, 0, 0))
            self.screen.blit(
                over_surf,
                (
                    SCREEN_WIDTH // 2 - over_surf.get_width() // 2,
                    SCREEN_HEIGHT // 2 - 40,
                ),
            )

            # Draw new high score message if achieved
            if self.score > self.high_score:  # Changed from >= to >
                new_record_surf = self.small_font.render(
                    "New High Score!", True, (255, 215, 0)
                )
                self.screen.blit(
                    new_record_surf,
                    (
                        SCREEN_WIDTH // 2 - new_record_surf.get_width() // 2,
                        SCREEN_HEIGHT // 2 + 10,
                    ),
                )
        pygame.display.update()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.bird.jump()
                if event.key == pygame.K_r and self.game_over:
                    self.reset()


def main():
    game = Game()
    while True:
        game.handle_input()
        game.update()
        game.draw()
        game.clock.tick(60)


if __name__ == "__main__":
    main()
