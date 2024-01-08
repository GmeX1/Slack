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

        self.combo_font = pygame.font.Font('data\\fonts\\facon.otf', 90)
        self.combo_font_shadow = pygame.font.Font('data\\fonts\\facon.otf', 100)
        self.combo_shadow_shift = pygame.math.Vector2()
        self.combo_anim_stage = 0
        self.combo = 0
        self.combo_timer = 0
        self.blink_combo = 0
        self.kills = 0

        self.rage_value = 0
        self.blink_rage = 0
        self.deplete = False
        self.overlay = pygame.transform.smoothscale(load_func('overlay\\vignette.png'), size)
        self.overlay_opacity = 0

    def kill(self, rage):
        self.kills += 1
        self.add_rage(rage)
        self.combo += 1
        if self.combo:
            self.blink_combo = 255
            self.combo_timer = pygame.time.get_ticks()

    def set_hp(self, amount):
        self.hp_amount = amount
        self.surface.fill((0, 0, 0, 0))

    def add_rage(self, value):
        self.rage_value += value
        if self.rage_value >= 100:
            self.rage_value = 100
            self.blink_rage = 255

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
        pygame.draw.rect(
            self.surface,
            (255, self.blink_rage, self.blink_rage),
            (10, self.hp_icon.get_height() + 20, self.rage_value * 2, 15)
        )
        pygame.draw.rect(self.surface, (255, 255, 255), (10, self.hp_icon.get_height() + 20, 200, 15), 2)

        if self.blink_rage > 0:
            self.blink_rage -= 5

        # КОМБО
        if self.combo:
            if pygame.time.get_ticks() - self.combo_timer > 5000:
                self.combo_timer = 0
                self.combo = 0
                self.combo_shadow_shift.x = self.combo_shadow_shift.y = 0
                self.combo_anim_stage = 0

            if self.combo > 1:
                text = self.combo_font.render(f'{self.combo}X', True,
                                              (200, self.blink_combo, self.blink_combo))
                text_shadow = self.combo_font_shadow.render(f'{self.combo}X', True,
                                                            (self.combo, self.blink_combo, self.blink_combo))
                self.surface.blit(
                    text_shadow,
                    (self.screen.get_width() - text_shadow.get_width() - 10 + self.combo_shadow_shift.x,
                     self.combo_shadow_shift.y)
                )
                self.surface.blit(
                    text,
                    (self.screen.get_width() - text.get_width() / 2 - text_shadow.get_width() / 2 - 10,
                     5)
                )
                if self.combo_anim_stage == 0:
                    self.combo_shadow_shift.y -= 0.2
                    if self.combo_shadow_shift.y < -3:
                        self.combo_shadow_shift.y = -3
                        self.combo_anim_stage = 1
                elif self.combo_anim_stage == 1:
                    self.combo_shadow_shift.x += 0.2
                    if self.combo_shadow_shift.x > 5:
                        self.combo_shadow_shift.x = 5
                        self.combo_anim_stage = 2
                elif self.combo_anim_stage == 2:
                    self.combo_shadow_shift.y += 0.2
                    if self.combo_shadow_shift.y > 3:
                        self.combo_shadow_shift.y = 3
                        self.combo_anim_stage = 3
                elif self.combo_anim_stage == 3:
                    self.combo_shadow_shift.x -= 0.2
                    if self.combo_shadow_shift.x < 0:
                        self.combo_shadow_shift.x = 0
                        self.combo_anim_stage = 0

        if self.blink_combo > 0:
            self.blink_combo -= 5

        # ВЫВОД НА ЭКРАН
        self.screen.blit(self.surface, (0, 0))
