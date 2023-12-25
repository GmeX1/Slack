import pygame
import os
import sys

from level_class import Level
from player_class import Player
from menu_class import Menu, Pause

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


def start_game():
    pause = Pause(screen)
    all_sprites = pygame.sprite.Group()
    level = Level(load_image('maps\\test_lvl_3.png'), 'test_lvl_3', screen)
    player = Player(load_image('player\\idle\\idle_r.png'), level.get_player_spawn(),
                    level.get_story_mode(),
                    all_sprites)
    player.import_anims(load_image)

    run = True
    clock = pygame.time.Clock()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause.set_last_frame(screen.copy())
                    menu_open = pause.start()
                    if menu_open:
                        return 'menu'

        all_sprites.update(tiles=level.tiles)
        level.scroll(player)
        screen.fill((0, 0, 0))
        level.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()
    return False


if __name__ == '__main__':
    menu = Menu(screen)
    menu.start()
    answer = start_game()
    while answer:
        menu.start()
        answer = start_game()
