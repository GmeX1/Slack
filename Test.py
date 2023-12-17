import pygame
import sys

# Инициализация Pygame
pygame.init()

# Размеры экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h), pygame.FULLSCREEN)
pygame.display.set_caption("Slack")


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Загрузка своего спрайта
        self.image = pygame.image.load("data/player_idle.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT // 2
        self.velocity_y = 0
        self.gravity = 1
        self.on_ground = False
        self.on_platform = False

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Проверка находится ли игрок на земле
        if self.rect.y > SCREEN_HEIGHT - self.rect.height:
            self.rect.y = SCREEN_HEIGHT - self.rect.height
            self.velocity_y = 0
            self.on_ground = True


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

# Создание игрока и платформ
player = Player()
all_sprites.add(player)

platform1 = Platform(100, 500, 200, 20)
platform2 = Platform(400, 400, 200, 20)
platform3 = Platform(-200, 400, 200, 20)
platforms.add(platform1, platform2, platform3)
all_sprites.add(platform1, platform2, platform3)

# Переменные камеры
camera_x = 0
camera_y = 0

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and pygame.K_LALT:
                running = False
                sys.exit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player.rect.x -= 5
    if keys[pygame.K_d]:
        player.rect.x += 5
    if keys[pygame.K_SPACE] and (player.on_ground or player.on_platform):
        player.velocity_y = -15
        player.on_platform = False
        player.on_ground = False

    all_sprites.update()

    camera_x = player.rect.x - SCREEN_WIDTH // 2
    camera_y = player.rect.y - SCREEN_HEIGHT // 2

    # Проверка столкновения игрока с платформами
    hits = pygame.sprite.spritecollide(player, platforms, False)
    for platform in hits:
        if player.velocity_y > 0:
            player.rect.y = platform.rect.y - player.rect.height
            player.velocity_y = 0
            player.on_platform = True
    screen.fill(BLACK)

    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y - camera_y))

    pygame.display.flip()

    clock.tick(120)
