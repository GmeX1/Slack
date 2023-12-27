import pygame
from scripts import make_anim_list


class UI:
    def __init__(self, screen, size, hp_icon, load_func):
        self.screen = screen
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.surface.convert_alpha()
        # self.surface.set_colorkey((0, 0, 0, 0))
        self.hp_icon = hp_icon
        self.destroy_anim = {
            'draw': False,
            'frame': -1,
            'images': make_anim_list(load_func, 'icons\\hp_no_fire')
        }
        self.hp_amount = 0

    def set_hp(self, amount):
        self.hp_amount = amount
        self.surface.fill((0, 0, 0, 0))

    def remove_hp(self):
        self.destroy_anim['frame'] = 0
        self.hp_amount -= 1

    def draw(self):
        self.surface.fill((0, 0, 0, 0))
        if self.destroy_anim['frame'] != -1:
            self.destroy_anim['frame'] += 0.2
            if int(self.destroy_anim['frame']) >= len(self.destroy_anim['images']):
                self.destroy_anim['frame'] = -1
            else:
                self.surface.blit(
                    self.destroy_anim['images'][int(self.destroy_anim['frame'])],
                    (10 * (self.hp_amount + 1) + self.hp_icon.get_width() * self.hp_amount - 3, 5))
        elif self.destroy_anim['frame'] >= len(self.destroy_anim['images']):
            self.destroy_anim['frame'] = -1

        for i in range(self.hp_amount):
            self.surface.blit(self.hp_icon, (10 * (i + 1) + self.hp_icon.get_width() * i, 10))

        self.screen.blit(self.surface, (0, 0))
