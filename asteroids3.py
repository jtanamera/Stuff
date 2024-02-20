import pygame
import random
import sys

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Initialize pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Avoider")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Spaceship parameters
SPACESHIP_WIDTH = 50
SPACESHIP_HEIGHT = 50
SPACESHIP_SPEED = 5

# Level, timer, and lives
level = 1
timer = 300
lives = 3
clock = pygame.time.Clock()

# Load images
spaceship_img = pygame.image.load("spaceship.png")
spaceship_img = pygame.transform.scale(spaceship_img, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))

asteroid_img = pygame.image.load("asteroid.png")

# Spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = spaceship_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -SPACESHIP_SPEED
        if keys[pygame.K_RIGHT]:
            self.speed_x = SPACESHIP_SPEED
        self.rect.x += self.speed_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

# Asteroid class
class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = asteroid_img
        self.image = pygame.transform.scale(self.image, (random.randint(25, 75), random.randint(25, 75)))  # Random size
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.uniform(1, 8) * (1 + level * 0.1)  # Increase speed by 10% each level

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.uniform(1, 8) * (1 + level * 0.1)  # Increase speed by 10% each level
            self.image = pygame.transform.scale(self.image, (random.randint(25, 75), random.randint(25, 75)))  # Random size

# Create sprite groups
all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

# Start screen
font = pygame.font.SysFont(None, 64)
start_text = font.render("Press SPACE to start", True, WHITE)
start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Game over screen
game_over_text = font.render("Game Over", True, RED)
game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Main game loop
start_screen = True
game_over = False
running = True
while running:
    if start_screen:
        SCREEN.fill(BLACK)
        SCREEN.blit(start_text, start_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                start_screen = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start_screen = False
    elif game_over:
        SCREEN.fill(BLACK)
        SCREEN.blit(game_over_text, game_over_rect)
        pygame.display.flip()
        pygame.time.wait(10000)  # Wait for 10 seconds
        game_over = False
        start_screen = True
        level = 1
        lives = 3
        all_sprites.empty()
        asteroids.empty()
        all_sprites.add(Spaceship())
    else:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        all_sprites.update()

        # Spawn asteroids
        if len(asteroids) < 5 + int(level * 0.5):  # Increase number of asteroids by 10% each level
            asteroid = Asteroid()
            all_sprites.add(asteroid)
            asteroids.add(asteroid)

        # Collision detection with asteroids
        hits = pygame.sprite.spritecollide(all_sprites.sprites()[0], asteroids, False)
        if hits:
            lives -= 1
            if lives <= 0:
                game_over = True
            else:
                timer = 300
                all_sprites.empty()
                asteroids.empty()
                all_sprites.add(Spaceship())

        # Draw
        SCREEN.fill(BLACK)
        all_sprites.draw(SCREEN)

        # Level, timer, and lives display
        font = pygame.font.SysFont(None, 36)
        text_level = font.render(f"Level: {level}", True, WHITE)
        text_timer = font.render(f"Time left: {timer}", True, WHITE)
        text_lives = font.render(f"Lives: {lives}", True, WHITE)
        SCREEN.blit(text_level, (10, 10))
        SCREEN.blit(text_timer, (10, 50))
        SCREEN.blit(text_lives, (10, 90))

        # Update timer
        if timer <= 0:
            level += 1
            timer = 300
        else:
            timer -= 1

        pygame.display.flip()
        clock.tick(60)

pygame.quit()
sys.exit()
