import os
import sqlite3

import pygame

from scripts import database_create, load_image
from small_logic_classes import Camera


def set_effects_volume():
    volume = db.cursor().execute('SELECT value FROM settings WHERE name="effect_volume"').fetchone()
    if not volume:
        volume = 0.5
    else:
        volume = volume[0] / 100

    for key in sounds.keys():
        sounds[key].set_volume(volume)

    volume = volume - 0.25
    if volume < 0:
        volume = 0.05
    for sound in steps_1:
        sound.set_volume(volume)


def get_stats():
    out = {
        'level': db.cursor().execute('SELECT value FROM settings WHERE name="level"').fetchone(),
        'hp': db.cursor().execute('SELECT value FROM settings WHERE name="hp"').fetchone(),
        'rage': db.cursor().execute('SELECT value FROM settings WHERE name="rage"').fetchone(),
        'max_combo': db.cursor().execute('SELECT value FROM settings WHERE name="max_combo"').fetchone(),
        'live_time': db.cursor().execute('SELECT value FROM settings WHERE name="live_time"').fetchone(),
        'kills': db.cursor().execute('SELECT value FROM settings WHERE name="kills"').fetchone(),
    }
    exists = True
    for key in out.keys():
        if out[key]:
            out[key] = out[key][0]
        else:
            exists = False
            if key == 'hp':
                val = 5
            else:
                val = 0
            out[key] = val
            db.cursor().execute(f'INSERT INTO settings (name, value) VALUES("{key}",{val})')
    if not exists:
        db.commit()
    return out


def reset_stats():
    for key in stats.keys():
        if key == 'hp':
            db.cursor().execute(f'UPDATE settings SET name="{key}", value=5 WHERE name="{key}"')
            stats[key] = 5
        else:
            db.cursor().execute(f'UPDATE settings SET name="{key}", value=0 WHERE name="{key}"')
            stats[key] = 0
        db.commit()


def save_stats():
    for key in stats.keys():
        db.cursor().execute(f'UPDATE settings SET name="{key}", value={stats[key]} WHERE name="{key}"')
        db.commit()


def steps_init(folder):
    out = list()
    for file in os.listdir(os.path.join('data', 'sounds', folder)):
        out.append(pygame.mixer.Sound(f'data\\sounds\\{folder}\\{file}'))
    return out


pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(18)

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

stats = get_stats()
