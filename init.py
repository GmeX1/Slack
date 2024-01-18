import os
import sqlite3

import pygame
from scripts import database_create, load_image
from small_logic_classes import Camera


def set_effects_volume():
    volume = db.cursor().execute('SELECT value FROM settings WHERE name="effect_volume"').fetchone()[0] / 100
    for key in sounds.keys():
        sounds[key].set_volume(volume)

    volume = volume - 0.25
    if volume < 0:
        volume = 0.05
    for sound in steps_1:
        sound.set_volume(volume)


def steps_init(folder):
    out = list()
    for file in os.listdir(os.path.join('data', 'sounds', folder)):
        out.append(pygame.mixer.Sound(f'data\\sounds\\{folder}\\{file}'))
    return out


pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
# TODO: Превышает лимит каналов
pygame.mixer.set_num_channels(12)

pygame.display.set_caption('Slack')
info = pygame.display.Info()
# screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
screen = pygame.display.set_mode((info.current_w - 100, info.current_h - 100))  # На время тестов лучше оконный режим
bullet_icon = load_image('bullet\\bullet.png')

camera = Camera(screen)
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()

if not os.path.exists(os.path.join('data', 'db', 'gamedata.db')):
    db = database_create()
else:
    db = sqlite3.connect('data\\db\\gamedata.db')

sounds = {
    'click': pygame.mixer.Sound('data\\sounds\\click.wav'),
    'hover': pygame.mixer.Sound('data\\sounds\\hover.wav'),
    'shoot': pygame.mixer.Sound('data\\sounds\\shoot.wav'),  # Пока что звук один, ибо оружий как таковых нет
    'death_screen': pygame.mixer.Sound('data\\sounds\\death_screen.wav'),
    'rage_on': pygame.mixer.Sound('data\\sounds\\rage_activate.wav')
}
steps_1 = steps_init('steps_floor')

set_effects_volume()
