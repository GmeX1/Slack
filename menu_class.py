from sys import exit as sys_exit

import pygame
from numpy.random import randint

from init import set_effects_volume, sounds, screen,db
from particles import SparkParticle
from scripts import show_fps


class Menu:
    def __init__(self):
        self.db = db
        self.cur = db.cursor()
        self.fps_switch = self.cur.execute(f'SELECT value FROM settings WHERE name="show_fps"').fetchall()
        if not self.fps_switch:
            self.cur.execute(f'INSERT INTO settings (name, value) VALUES("show_fps", 0)')
            self.db.commit()
        else:
            self.fps_switch = self.fps_switch[0][0]

        self.show = True
        self.surface = screen
        self.font_big = pygame.font.Font('data\\fonts\\better-vcr.ttf', 80)
        self.font_medium = pygame.font.Font('data\\fonts\\better-vcr.ttf', 64)
        self.font_small = pygame.font.Font('data\\fonts\\better-vcr.ttf', 52)
        self.buttons = list()
        self.generate_menu()

    def generate_menu(self):
        self.buttons = ['НАЧАТЬ ИГРУ', 'ПРОДОЛЖИТЬ', 'НАСТРОЙКИ', 'ВЫЙТИ']
        for i in range(len(self.buttons)):
            self.buttons[i] = Button(
                self.font_big,
                self.buttons[i],
                (self.surface.get_width() / 2, self.surface.get_height() / 8 * (i + 3))
            )

    def generate_settings(self):
        self.buttons = ['show_fps', 'ГРОМКОСТЬ ЭФФЕКТОВ', 'effect_volume', 'ГРОМКОСТЬ МУЗЫКИ', 'music_volume',
                        'НАЗАД']
        for i in range(len(self.buttons)):
            if 'volume' in self.buttons[i]:
                self.buttons[i] = ButtonSlider(
                    self.buttons[i],
                    self.font_medium,
                    self.buttons[i],
                    (self.surface.get_width() / 2, self.surface.get_height() / 10 * (i + 4)),
                )
            elif self.buttons[i].endswith('fps'):
                self.buttons[i] = ButtonSlider(
                    self.buttons[i],
                    self.font_medium,
                    self.buttons[i],
                    (self.surface.get_width() / 2, self.surface.get_height() / 10 * (i + 4)),
                    True,
                    'СЧЁТЧИК FPS'
                )
            else:
                self.buttons[i] = Button(
                    self.font_medium,
                    self.buttons[i],
                    (self.surface.get_width() / 2, self.surface.get_height() / 10 * (i + 4)),
                    False if i != len(self.buttons) - 1 else True
                )

    def show_loading(self):
        self.surface.fill((0, 0, 0))
        render = self.font_big.render('ЗАГРУЗКА...', True, (255, 255, 255))
        self.surface.blit(
            render,
            (self.surface.get_width() / 2 - render.get_width() / 2,
             self.surface.get_height() / 2 - render.get_height() / 2)
        )

    def handle_click(self, button):
        if button.text in ['НАЧАТЬ ИГРУ', 'ПРОДОЛЖИТЬ']:  # Пока не подключу БД, любая из кнопок просто откроет игру
            self.show = False
            return 'close'
        elif button.text == 'НАСТРОЙКИ':
            self.generate_settings()
        elif button.text == 'ВЫЙТИ':
            self.db.commit()
            pygame.quit()
            sys_exit()
        elif button.text == 'НАЗАД':
            self.db.commit()
            self.generate_menu()
            set_effects_volume()
            self.update_music_volume()
        elif type(button) == ButtonSlider:
            if button.get_click_zone() == 'left':
                button.change_value(-5)
            elif button.get_click_zone() == 'right':
                button.change_value(5)
            self.fps_switch = self.cur.execute(f'SELECT value FROM settings WHERE name="show_fps"').fetchall()[0][0]
        return 'working'

    def update_music_volume(self):
        volume = self.cur.execute('SELECT value FROM settings WHERE name="music_volume"').fetchone()[0] / 100
        pygame.mixer.music.set_volume(volume)

    def start_music(self):
        volume = self.cur.execute('SELECT value FROM settings WHERE name="music_volume"').fetchone()[0] / 100
        pygame.mixer.music.load('data\\music\\menu.wav')
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    def start(self):
        self.start_music()
        particles = pygame.sprite.Group()
        self.show = True
        clock = pygame.time.Clock()
        while self.show:
            if randint(0, 11) > 5 and len(particles) < 800:
                # if len(particles) < 5000:  # Тесты производительности
                SparkParticle(
                    (randint(20, self.surface.get_width() - 19), self.surface.get_height()),
                    particles)

            mouse_click_pos = (-1, -1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys_exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_click_pos = event.pos

            self.surface.fill((0, 0, 0))
            particles.update()
            particles.draw(self.surface)
            for button in self.buttons:
                button.update()
                if mouse_click_pos != (-1, -1) and button.click(mouse_click_pos):
                    if self.handle_click(button) == 'close':
                        self.show_loading()
                        break
                if button.hover:
                    for layer, layer_offset in button.get_layers():
                        pos = [*button.get_relative_pos()]
                        pos[0] += layer_offset
                        self.surface.blit(layer, pos)
                self.surface.blit(button.render, button.get_relative_pos())
            if self.fps_switch:
                show_fps(self.surface, clock)
            pygame.display.flip()
            clock.tick(100)


class Pause(Menu):  # TODO: накладывается один фпс на другой
    def __init__(self):
        super().__init__()
        self.last_frame = self.surface.copy()
        self.last_frame.set_alpha(150)
        self.call_menu = False

    def set_last_frame(self):
        self.last_frame = screen.copy()
        self.last_frame.set_alpha(125)

    def generate_menu(self):
        self.buttons = ['ПРОДОЛЖИТЬ', 'НАСТРОЙКИ', 'ВЫЙТИ В МЕНЮ']
        for i in range(len(self.buttons)):
            self.buttons[i] = Button(
                self.font_big,
                self.buttons[i],
                (self.surface.get_width() / 2, self.surface.get_height() / 8 * (i + 3))
            )

    def handle_click(self, button):
        if button.text == 'ПРОДОЛЖИТЬ':
            self.show = False
        elif button.text == 'НАСТРОЙКИ':
            self.generate_settings()
        elif button.text == 'ВЫЙТИ В МЕНЮ':
            self.db.commit()
            self.call_menu = True
        elif button.text == 'НАЗАД':
            self.db.commit()
            self.generate_menu()
            set_effects_volume()
        elif type(button) == ButtonSlider:
            if button.get_click_zone() == 'left':
                button.change_value(-5)
            elif button.get_click_zone() == 'right':
                button.change_value(5)
            self.fps_switch = self.cur.execute(f'SELECT value FROM settings WHERE name="show_fps"').fetchall()[0][0]

    def start(self):
        self.fps_switch = self.cur.execute(f'SELECT value FROM settings WHERE name="show_fps"').fetchall()[0][0]
        self.call_menu = False
        self.show = True
        self.generate_menu()
        clock = pygame.time.Clock()
        while self.show:
            mouse_click_pos = (-1, -1)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.show = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_click_pos = event.pos

            self.surface.fill((0, 0, 0))
            self.surface.blit(self.last_frame, (0, 0))
            for button in self.buttons:
                button.update()
                if mouse_click_pos != (-1, -1) and button.click(mouse_click_pos):
                    self.handle_click(button)
                    if self.call_menu:
                        self.show = False
                        return True
                if button.hover:
                    for layer, layer_offset in button.get_layers():
                        pos = [*button.get_relative_pos()]
                        pos[0] += layer_offset
                        self.surface.blit(layer, pos)
                self.surface.blit(button.render, button.get_relative_pos())
                if self.fps_switch:
                    show_fps(self.surface, clock)
            pygame.display.flip()
            clock.tick(100)
        return False


class DeathScreen(Menu):
    def __init__(self):
        self.last_frame = screen.copy()
        self.call_menu = False
        self.fade_time = 3000
        self.start_tick = pygame.time.get_ticks()

        self.kills = 0
        self.max_combo = 0
        self.live_time = '00:00:00'

        super().__init__()

    def set_last_frame(self):
        self.last_frame = screen.copy()
        self.fade_time = 3000
        self.start_tick = pygame.time.get_ticks()

    def generate_menu(self):
        self.buttons = ['ВЫ УМЕРЛИ.', f'Врагов убито: {self.kills}', f'Времени прожито: {self.live_time}',
                        f'Максимальное комбо: {self.max_combo}', 'ВОЗРОДИТЬСЯ', 'Я СДАЮСЬ']
        self.buttons[0] = Button(
            self.font_big,
            self.buttons[0],
            (self.surface.get_width() / 2, self.surface.get_height() / 8),
            False
        )
        for i in range(1, len(self.buttons)):
            if i < 4:
                self.buttons[i] = Button(
                    self.font_small,
                    self.buttons[i],
                    (self.surface.get_width() / 2, self.surface.get_height() / 12 * (i + 3)),
                    False
                )
            else:
                self.buttons[i] = Button(
                    self.font_medium,
                    self.buttons[i],
                    (self.surface.get_width() / 2, self.surface.get_height() / 8 * (i + 1.5))
                )

    def set_stats(self, kills, time):
        self.kills = kills
        self.live_time = time
        self.generate_menu()

    def start(self):
        self.fps_switch = self.cur.execute(f'SELECT value FROM settings WHERE name="show_fps"').fetchall()[0][0]
        self.call_menu = False
        self.show = True
        self.generate_menu()
        clock = pygame.time.Clock()
        pygame.mixer.find_channel().play(sounds['death_screen'])
        while self.show:
            mouse_click_pos = (-1, -1)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_click_pos = event.pos

            if self.fade_time > 0:
                self.fade_time -= pygame.time.get_ticks() - self.start_tick
                if self.fade_time <= 0:
                    self.last_frame.set_alpha(0)
                else:
                    self.last_frame.set_alpha(self.fade_time / (3000 / 255))

            self.surface.fill((0, 0, 0))
            self.surface.blit(self.last_frame, (0, 0))

            for button in self.buttons:
                button.update()
                if mouse_click_pos != (-1, -1) and button.click(mouse_click_pos):
                    self.handle_click(button)
                    if self.call_menu:
                        self.show = False
                        return True
                if button.hover:
                    for layer, layer_offset in button.get_layers():
                        pos = [*button.get_relative_pos()]
                        pos[0] += layer_offset
                        self.surface.blit(layer, pos)
                self.surface.blit(button.render, button.get_relative_pos())
                if self.fps_switch:
                    show_fps(self.surface, clock)
            pygame.display.flip()
            clock.tick(100)
        return False

    def handle_click(self, button):
        if button.text == 'ВОЗРОДИТЬСЯ':
            self.show = False
        elif button.text == 'Я СДАЮСЬ':
            self.db.commit()
            self.call_menu = True


class Button:
    def __init__(self, font, text, pos=(0, 0), hover=True):
        self.font = font
        self.text = text
        self.color = (255, 255, 255)
        self.render = self.font.render(self.text, False, self.color)
        self.pos = pos
        self.rect = self.render.get_rect().move(self.get_relative_pos())
        self.hover = hover
        self.is_hovered = False
        if self.hover:
            self.anim_offset_x = 0
            self.layers = [
                [self.font.render(self.text, False, (172, 0, 0)), 0],
                [self.font.render(self.text, False, (0, 0, 172)), 0]
            ]

    def get_layers(self):
        if self.hover:
            return self.layers
        return None

    def get_relative_pos(self):
        return self.pos[0] - self.render.get_width() / 2, self.pos[1]

    def click(self, pos):
        if pygame.Rect(*pos, 1, 1).colliderect(self.rect):
            pygame.mixer.find_channel().play(sounds['click'])
            return True
        return False

    def render_text(self):
        self.render = self.font.render(self.text, False, self.color)

    def update_anim(self):
        self.anim_offset_x += 0.15
        if self.anim_offset_x <= 1:
            if -3.05 < self.layers[0][1] and self.layers[0][1] >= -3.15:
                self.layers[0][1] -= self.anim_offset_x
                self.layers[1][1] += self.anim_offset_x
            else:
                self.layers[0][1] += 0.5
                self.layers[1][1] -= 0.5
        else:
            self.anim_offset_x = 0

    def update(self):
        if self.hover:
            if pygame.Rect(*pygame.mouse.get_pos(), 1, 1).colliderect(self.rect):
                if not self.is_hovered:
                    pygame.mixer.find_channel().play(sounds['hover'])
                    self.is_hovered = True
                self.color = (0, 172, 0)
                self.update_anim()
            else:
                self.is_hovered = False
                self.anim_offset_x = 0
                self.layers[0][1] = 0
                self.layers[1][1] = 0
                self.color = (255, 255, 255)

        self.render_text()


class ButtonSlider(Button):
    def __init__(self, name, font, text, pos=(0, 0), hover=True, draw_slide=''):
        super().__init__(font, text, pos, hover)
        self.db = db
        self.cur = self.db.cursor()
        self.name = name
        self.draw_slide = draw_slide
        self.value_range = range(0, 101) if len(draw_slide) == 0 else (0, 1)
        self.value = self.cur.execute(f'SELECT value FROM settings WHERE name="{self.name}"').fetchall()
        if not self.value:
            self.value = 50 if len(draw_slide) == 0 else 0
            self.cur.execute(f'INSERT INTO settings (name, value) VALUES("{self.name}",{self.value})')
            self.db.commit()
        else:
            self.value = self.value[0][0]

        self.render = self.font.render(f'< {str(self.value)}% >', False, self.color)
        if self.hover:
            self.anim_offset_x = 0
            self.layers = [
                [self.font.render(f'< {str(self.value)}% >', False, (172, 0, 0)), 0],
                [self.font.render(f'< {str(self.value)}% >', False, (0, 0, 172)), 0]
            ]

    def change_value(self, value):
        self.value += value
        if self.value > self.value_range[-1]:
            self.value = self.value_range[-1]
        elif self.value < self.value_range[0]:
            self.value = self.value_range[0]
        self.cur.execute(f'UPDATE settings SET value={self.value} WHERE name="{self.name}"')

    def get_click_zone(self):
        if pygame.mouse.get_pos()[0] < self.rect.centerx:
            return 'left'
        elif pygame.mouse.get_pos()[0] > self.rect.centerx:
            return 'right'
        return 'center'

    def render_text(self):
        if not self.draw_slide:
            self.render = self.font.render(f'< {str(self.value)}% >', False, self.color)
            if self.hover:
                self.layers[0][0] = self.font.render(f'< {str(self.value)}% >', False, (172, 0, 0))
                self.layers[1][0] = self.font.render(f'< {str(self.value)}% >', False, (0, 0, 172))
            self.rect = self.render.get_rect().move(self.get_relative_pos())
        else:
            self.render = self.font.render(f'< {self.draw_slide} >', False, self.color)
            if self.hover:
                self.layers[0][0] = self.font.render(f'< {self.draw_slide} >', False, (172, 0, 0))
                self.layers[1][0] = self.font.render(f'< {self.draw_slide} >', False, (0, 0, 172))
            self.rect = self.render.get_rect().move(self.get_relative_pos())
