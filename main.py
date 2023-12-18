import pygame
import os
import sys
from level_class import Level
from player_class import Player

pygame.init()
pygame.display.set_caption('Slack')
info = pygame.display.Info()
# screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
screen = pygame.display.set_mode((info.current_w - 100, info.current_h - 100))  # На время тестов лучше оконный режим


def load_image(name, colorkey=None):
    path = ['data']
    if '\\' in name:
        [path.append(i) for i in name.split('\\')]
    else:
        path.append(name)
    fullname = os.path.join(*path)

    if not os.path.isfile(fullname):
        print(f"File '{fullname}' not found")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


if __name__ == '__main__':
    all_sprites = pygame.sprite.Group()
    level = Level(load_image('maps\\test_lvl.png'), 'test_lvl', screen)
    player = Player(load_image('player/player_idle.png'), load_image('player/player_idle_mask.png'),
                    level.get_player_spawn(),
                    all_sprites)

    run = True
    clock = pygame.time.Clock()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()

        # TODO: Имеется мелкий баг: движение влево приоритетнее. (Попробуй зажать вправо и затем нажать влево.
        #  Потом наоборот. Разница на лицо)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.direction.x = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.direction.x = 1
        else:
            player.direction.x = 0
        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            player.jump()

        all_sprites.update(tiles=level.tiles)
        level.scroll(player)
        screen.fill((0, 0, 0))
        level.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()
