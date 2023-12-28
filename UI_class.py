import pygame
from scripts import make_anim_list


class UI:
    def __init__(self, screen, size, load_func):
        self.screen = screen
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.surface.convert_alpha()
        self.hp_icon = load_func('icons\\hp_bigger.png')
        self.destroy_anim = {
            'draw': False,
            'frame': -1,
            'images': make_anim_list(load_func, 'icons\\hp_no_fire')
        }
        self.hp_amount = 0
        self.kills = 0
        self.rage_value = 0
        self.blink = 0
        self.deplete = False
        self.overlay = pygame.transform.smoothscale(load_func('overlay\\vignette.png'), size)
        self.overlay_opacity = 0

    def set_hp(self, amount):
        self.hp_amount = amount
        self.surface.fill((0, 0, 0, 0))

    def add_rage(self, value):
        self.rage_value += value
        if self.rage_value >= 100:
            self.rage_value = 100
            self.blink = 255

    def activate_rage(self):
        if self.rage_value == 100:
            self.deplete = True
            self.overlay_opacity = 1

    def remove_hp(self):
        if self.hp_amount > 0:
            self.destroy_anim['frame'] = 0
            self.hp_amount -= 1

    def draw(self):
        self.surface.fill((0, 0, 0, 0))

        # ОВЕРЛЕЙ
        if self.deplete:
            if 0 < self.overlay_opacity < 255:
                self.overlay_opacity += 5
            elif self.overlay_opacity > 255:
                self.overlay_opacity = 255

            self.rage_value -= 0.1
            if self.rage_value <= 0:
                self.rage_value = 0
                self.deplete = False

        if not self.deplete and self.overlay_opacity > 0:
            self.overlay_opacity -= 5

        if self.deplete or self.overlay_opacity > 0:
            self.overlay.set_alpha(self.overlay_opacity)
            self.surface.blit(self.overlay, (0, 0))

        # ОЗ
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

        # РЕЙДЖ БАР
        if self.blink > 0:
            self.blink -= 5

        pygame.draw.rect(
            self.surface,
            (255, self.blink, self.blink),
            (10, self.hp_icon.get_height() + 20, self.rage_value * 2, 15)
        )
        pygame.draw.rect(self.surface, (255, 255, 255), (10, self.hp_icon.get_height() + 20, 200, 15), 2)

        # ВЫВОД НА ЭКРАН
        self.screen.blit(self.surface, (0, 0))
