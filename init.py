import os
import sqlite3

import pygame

from scripts import database_create


def set_effects_volume():
    volume = db.cursor().execute('SELECT value FROM settings WHERE name="effect_volume"').fetchone()[0] / 100
    for key in sounds.keys():
        sounds[key].set_volume(volume)


pygame.mixer.pre_init(44100, -16, 1, 512)
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
}
set_effects_volume()
