import pygame

from init import db


class Music:
    def __init__(self):
        self.volume = db.cursor().execute('SELECT value FROM settings WHERE name="music_volume"').fetchone()[0] / 100
        pygame.mixer.music.load(f'data\\music\\main_layer.wav')
        pygame.mixer.music.set_volume(self.volume)
        self.layer_1 = {
            'channel': pygame.mixer.Channel(0),
            'sound': pygame.mixer.Sound(f'data\\music\\layer_1.wav'),
            'volume': 0
        }
        self.layer_2 = {
            'channel': pygame.mixer.Channel(1),
            'sound': pygame.mixer.Sound(f'data\\music\\layer_2.wav'),
            'volume': 0
        }
        self.layer_3 = {
            'channel': pygame.mixer.Channel(2),
            'sound': pygame.mixer.Sound(f'data\\music\\layer_3.wav'),
            'volume': 0
        }

        self.layer_1['channel'].set_volume(0)
        self.layer_2['channel'].set_volume(0)
        self.layer_3['channel'].set_volume(0)

        pygame.mixer_music.play(-1)
        self.layer_1['channel'].play(self.layer_1['sound'], -1)
        self.layer_2['channel'].play(self.layer_2['sound'], -1)
        self.layer_3['channel'].play(self.layer_3['sound'], -1)

    def pause(self):
        pygame.mixer.music.pause()
        self.layer_1['channel'].pause()
        self.layer_2['channel'].pause()
        self.layer_3['channel'].pause()

    def resume(self):
        pygame.mixer.music.unpause()
        self.layer_1['channel'].unpause()
        self.layer_2['channel'].unpause()
        self.layer_3['channel'].unpause()

    def update_volume(self):
        self.volume = db.cursor().execute('SELECT value FROM settings WHERE name="music_volume"').fetchone()[0] / 100
        pygame.mixer.music.set_volume(self.volume)

    def check_combo(self, combo):
        if combo > 1:
            if self.layer_1['volume'] < self.volume:
                self.layer_1['volume'] += 0.0005
                if self.layer_1['volume'] > self.volume:
                    self.layer_1['volume'] = self.volume
                self.layer_1['channel'].set_volume(self.layer_1['volume'])
            if combo > 2:
                if self.layer_2['volume'] < self.volume:
                    self.layer_2['volume'] += 0.0005
                    if self.layer_2['volume'] > self.volume:
                        self.layer_2['volume'] = self.volume
                    self.layer_2['channel'].set_volume(self.layer_2['volume'])
            if combo > 4:
                if self.layer_3['volume'] < self.volume:
                    self.layer_3['volume'] += 0.0005
                    if self.layer_3['volume'] > self.volume:
                        self.layer_3['volume'] = self.volume
                    self.layer_3['channel'].set_volume(self.layer_3['volume'])
        else:
            if self.layer_1['volume'] > 0:
                self.layer_1['volume'] -= 0.0005
                if self.layer_1['volume'] < 0:
                    self.layer_1['volume'] = 0
                self.layer_1['channel'].set_volume(self.layer_1['volume'])
            if self.layer_2['volume'] > 0:
                self.layer_2['volume'] -= 0.0005
                if self.layer_2['volume'] < 0:
                    self.layer_2['volume'] = 0
                self.layer_2['channel'].set_volume(self.layer_2['volume'])
            if self.layer_3['volume'] > 0:
                self.layer_3['volume'] -= 0.0005
                if self.layer_3['volume'] < 0:
                    self.layer_3['volume'] = 0
                self.layer_3['channel'].set_volume(self.layer_3['volume'])
