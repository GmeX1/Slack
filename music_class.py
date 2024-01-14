import pygame

from init import db


class Music:
    def __init__(self, level_num):
        music_volume = db.cursor().execute('SELECT value FROM settings WHERE name="music_volume"').fetchone()[0] / 100
        pygame.mixer.music.load(f'data\\music\\{level_num}\\main_layer.wav')
        layer_1 = pygame.mixer.Channel(0)  # TODO: Завернуть в класс
        layer_1_sound = pygame.mixer.Sound(f'data\\music\\{level_num}\\layer_1.wav')
        layer_1.set_volume(0)
        layer_2 = pygame.mixer.Channel(1)
        layer_2_sound = pygame.mixer.Sound(f'data\\music\\{level_num}\\layer_2.wav')
        layer_2.set_volume(0)
        layer_3 = pygame.mixer.Channel(2)
        layer_3_sound = pygame.mixer.Sound(f'data\\music\\{level_num}\\layer_3.wav')
        layer_3.set_volume(0)

        pygame.mixer_music.play(-1)
        layer_1.play(layer_1_sound, -1)
        layer_2.play(layer_2_sound, -1)
        layer_3.play(layer_3_sound, -1)
