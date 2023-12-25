import pygame
from sys import exit as sys_exit
from numpy.random import randint, uniform, choice
from numpy import pi, sin, cos


# Pycharm считает, что я не использую cos и sin, но они используются в переменной func у класса SparkParticle


class Menu:
    # TODO: Связать меню с БД
    # TODO: Добавить отображение фпс в настройках?
    def __init__(self, surface):
        self.show = True
        self.surface = surface
        self.font = pygame.font.Font('data\\fonts\\better-vcr.ttf', 72)
        self.buttons = list()
        self.generate_menu()

    def generate_menu(self):
        self.buttons = ['НАЧАТЬ ИГРУ', 'ПРОДОЛЖИТЬ', 'НАСТРОЙКИ', 'ВЫЙТИ']
        for i in range(len(self.buttons)):
            self.buttons[i] = Button(
                self.font,
                self.buttons[i],
                (self.surface.get_width() / 2, self.surface.get_height() / 8 * (i + 3))
            )

    def generate_settings(self):
        self.buttons = ['ГРОМКОСТЬ ЭФФЕКТОВ', 'effect_volume', 'ГРОМКОСТЬ МУЗЫКИ', 'music_volume', 'НАЗАД']
        for i in range(len(self.buttons)):
            if 'volume' in self.buttons[i]:
                self.buttons[i] = ButtonSlider(
                    self.font,
                    self.buttons[i],
                    (self.surface.get_width() / 2, self.surface.get_height() / 8 * (i + 3)),
                )
            else:
                self.buttons[i] = Button(
                    self.font,
                    self.buttons[i],
                    (self.surface.get_width() / 2, self.surface.get_height() / 8 * (i + 3)),
                    False if i != len(self.buttons) - 1 else True
                )

    def handle_click(self, button):
        if button.text in ['НАЧАТЬ ИГРУ', 'ПРОДОЛЖИТЬ']:  # Пока не подключу БД, любая из кнопок просто откроет игру
            self.show = False
            return 'close'
        elif button.text == 'НАСТРОЙКИ':
            self.generate_settings()
        elif button.text == 'ВЫЙТИ':
            pygame.quit()
            sys_exit()
        elif button.text == 'НАЗАД':
            self.generate_menu()
        elif type(button) == ButtonSlider:
            if button.get_click_zone() == 'left':
                button.change_value(-5)
            elif button.get_click_zone() == 'right':
                button.change_value(5)
        return 'working'

    def start(self):
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
                        self.surface.fill((0, 0, 0))
                        render = self.font.render('ЗАГРУЗКА...', True, (255, 255, 255))
                        self.surface.blit(
                            render,
                            (self.surface.get_width() / 2 - render.get_width() / 2,
                             self.surface.get_height() / 2 - render.get_height() / 2)
                        )
                        break
                if button.hover:
                    for layer, layer_offset in button.get_layers():
                        pos = [*button.get_relative_pos()]
                        pos[0] += layer_offset
                        self.surface.blit(layer, pos)
                self.surface.blit(button.render, button.get_relative_pos())
            pygame.display.flip()
            clock.tick(100)


class Pause(Menu):
    def __init__(self, surface):
        super().__init__(surface)
        self.last_frame = self.surface.copy()
        self.last_frame.set_alpha(150)
        self.call_menu = False

    def set_last_frame(self, screen):
        self.last_frame = screen
        self.last_frame.set_alpha(125)

    def generate_menu(self):
        self.buttons = ['ПРОДОЛЖИТЬ', 'НАСТРОЙКИ', 'ВЫЙТИ В МЕНЮ']
        for i in range(len(self.buttons)):
            self.buttons[i] = Button(
                self.font,
                self.buttons[i],
                (self.surface.get_width() / 2, self.surface.get_height() / 8 * (i + 3))
            )

    def handle_click(self, button):
        if button.text == 'ПРОДОЛЖИТЬ':
            self.show = False
        elif button.text == 'НАСТРОЙКИ':
            self.generate_settings()
        elif button.text == 'ВЫЙТИ В МЕНЮ':
            self.call_menu = True
        elif button.text == 'НАЗАД':
            self.generate_menu()
        elif type(button) == ButtonSlider:
            if button.get_click_zone() == 'left':
                button.change_value(-5)
            elif button.get_click_zone() == 'right':
                button.change_value(5)

    def start(self):
        self.show = True
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
            pygame.display.flip()
            clock.tick(100)
        return False


class SparkParticle(pygame.sprite.Sprite):
    # TODO: Возможно стоить добавить beat sync?
    # TODO: Сделать авто-оптимизацию под слабые устройства?
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        size = randint(4, 12)
        self.image = pygame.Surface((size, size))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect().move(pos)

        self.speed_y = uniform(0.5, 2.6)
        self.fade_speed = pos[1] / 255

        self.amplitude = uniform(0.5, 1.5)
        self.phase = uniform(-1.5, 1.5)
        self.func = eval(choice(['sin', 'cos'], size=1)[0])

        self.half_width = self.rect.width / 2
        self.half_height = self.rect.height / 2

    def update(self):
        self.image.fill((0, 0, 0))
        fade = (255 - round(self.rect.y / self.fade_speed))
        opacity = randint(160, 256) - fade

        circle = self.image.copy()
        circle.set_alpha(opacity - 140)

        circle_center = self.image.copy()
        circle_center.set_alpha(opacity)

        pygame.draw.circle(
            circle,
            (119, 64, 59),
            (self.half_width, self.half_height),
            self.half_width
        )
        pygame.draw.circle(
            circle_center,
            (240, 182, 120),
            (self.half_width, self.half_height),
            self.rect.width / 4
        )
        self.image.blit(circle, (0, 0))
        self.image.blit(circle_center, (0, 0))

        self.rect.y -= self.speed_y
        # Гармонические колебания с погрешностью в амплитуде и начальной фазе
        x = self.amplitude * self.func(pi * self.rect.y / 64 + self.phase)
        if round(x) == 0:
            self.amplitude = uniform(0.5, 1.5)
            self.phase += uniform(-0.5, 0.5)
        self.rect.x += x

        if self.rect.bottom < 0:
            self.kill()


class Button:
    def __init__(self, font, text, pos=(0, 0), hover=True):
        self.font = font
        self.text = text
        self.color = (255, 255, 255)
        self.render = self.font.render(self.text, False, self.color)
        self.pos = pos
        self.rect = self.render.get_rect().move(self.get_relative_pos())
        self.hover = hover
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
                self.color = (0, 172, 0)
                self.update_anim()
            else:
                self.anim_offset_x = 0
                self.layers[0][1] = 0
                self.layers[1][1] = 0
                self.color = (255, 255, 255)

        self.render_text()


class ButtonSlider(Button):
    def __init__(self, font, text, pos=(0, 0), hover=True):
        super().__init__(font, text, pos, hover)
        self.value = 50
        self.render = self.font.render(f'< {str(self.value)}% >', False, self.color)
        if self.hover:
            self.anim_offset_x = 0
            self.layers = [
                [self.font.render(f'< {str(self.value)}% >', False, (172, 0, 0)), 0],
                [self.font.render(f'< {str(self.value)}% >', False, (0, 0, 172)), 0]
            ]

    def change_value(self, value):  # В будущем пригодится для реальной связи со звуком
        self.value += value
        if self.value > 100:
            self.value = 100
        elif self.value < 0:
            self.value = 0

    def get_click_zone(self):
        if pygame.mouse.get_pos()[0] < self.rect.centerx:
            return 'left'
        elif pygame.mouse.get_pos()[0] > self.rect.centerx:
            return 'right'
        return 'center'

    def render_text(self):
        self.render = self.font.render(f'< {str(self.value)}% >', False, self.color)
        self.layers[0][0] = self.font.render(f'< {str(self.value)}% >', False, (172, 0, 0))
        self.layers[1][0] = self.font.render(f'< {str(self.value)}% >', False, (0, 0, 172))
        self.rect = self.render.get_rect().move(self.get_relative_pos())
