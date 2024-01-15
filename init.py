import os
import sqlite3

import pygame

from scripts import database_create


def set_effects_volume():
    volume = db.cursor().execute('SELECT value FROM settings WHERE name="effect_volume"').fetchone()[0] / 100
    for key in sounds.keys():
        sounds[key].set_volume(volume)

    volume = volume - 0.25
    if volume < 0:
        volume = 0
    for sound in steps_1:
        sound.set_volume(volume)
    for sound in steps_2:
        sound.set_volume(volume)


def steps_init(folder):
    out = list()
    for file in os.listdir(os.path.join('data', 'sounds', folder)):
        out.append(pygame.mixer.Sound(f'data\\sounds\\{folder}\\{file}'))
    return out


pygame.mixer.pre_init(44100, -16, 8, 512)
pygame.init()

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
steps_2 = steps_init('steps_tile')
set_effects_volume()
