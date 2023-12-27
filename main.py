import pygame
import os
import sys

from level_class import Level, Camera
from player_class import Player, Bullet, Enemy
from menu_class import Menu, Pause

pygame.init()
pygame.display.set_caption('Slack')
info = pygame.display.Info()
life_counter = 3
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


def start_game(run=True):
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    camera = Camera(screen)
    level = Level(load_image('maps\\test_lvl.png'), 'test_lvl', screen, camera)
    player = Player(load_image('player\\idle\\idle_r.png'), level.get_player_spawn(),
                    False,  # TODO: ВЕРНУТЬ СЮЖЕТНЫЙ МАРКЕР level.get_story_mode()
                    all_sprites, camera)

    player.import_anims(load_image)
    camera.set_max((level.image.get_width(), level.image.get_height()))
    camera.get_map_image(level.image)

    [Enemy(pygame.Surface((10, 50)), i, life_counter, player,
           all_sprites, enemies, camera) for i in level.get_enemies_pos()]
    # Здесь создаются враги в позициях, полученных из level.get_enemies_pos()
    # Я пока что выключил сюжетный режим для игрока и сделал бесконечный прыжок для упрощения рабочего процесса

    clock = pygame.time.Clock()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    Bullet(load_image('bullet\\bullet.png'), player.map_rect.center, player.last_keys, 'player',
                           all_sprites, camera)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause.set_last_frame(screen.copy())
                    menu_open = pause.start()
                    if menu_open:
                        return 'menu'
        all_sprites.update(tiles=level.tiles, enemies=enemies)
        screen.fill((0, 0, 0))
        camera.draw_offset(player)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()
    return False


if __name__ == '__main__':
    pause = Pause(screen)
    menu = Menu(screen)
    # menu.start()  # TODO: РАСКОММЕНТИРУЙ, ЭТА ШТУКА ВЫКЛЮЧАЕТ СТАРТ МЕНЮ
    answer = start_game()
    while answer:
        menu.start()
        answer = start_game()
