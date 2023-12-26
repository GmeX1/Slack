import sqlite3

import pygame
import os
import sys

from level_class import Level, Camera
from player_class import Player
from menu_class import Menu, Pause
from scripts import database_create, show_fps

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
    all_sprites = pygame.sprite.Group()
    camera = Camera(screen)
    level = Level(load_image('maps\\test_lvl.png'), 'test_lvl', screen, camera)
    player = Player(load_image('player\\idle\\idle_r.png'), level.get_player_spawn(),
                    level.get_story_mode(),
                    all_sprites, camera)
    player.import_anims(load_image)
    camera.set_max((level.image.get_width(), level.image.get_height()))
    camera.get_map_image(level.image)

    cur = db.cursor()
    fps_switch = cur.execute(f'SELECT value FROM settings WHERE name="show_fps"').fetchall()[0][0]

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
                    fps_switch = cur.execute(f'SELECT value FROM settings WHERE name="show_fps"').fetchall()[0][0]

        all_sprites.update(tiles=level.tiles)
        screen.fill((0, 0, 0))
        camera.draw_offset(player)
        if fps_switch:
            show_fps(screen, clock)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()
    return False


if __name__ == '__main__':
    if not os.path.exists(os.path.join('data', 'db', 'gamedata.db')):
        db = database_create()
    else:
        db = sqlite3.connect('data\\db\\gamedata.db')
    pause = Pause(screen, db)
    menu = Menu(screen, db)
    menu.start()
    answer = start_game()
    while answer:
        menu.start()
        answer = start_game()
