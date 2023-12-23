import pygame
from sys import exit as sys_exit
from numpy.random import randint, uniform


class Menu:
    # TODO: Связать меню с БД
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

    def start(self):
        lowest_fps = 101

        particles = pygame.sprite.Group()
        self.show = True
        clock = pygame.time.Clock()
        while self.show:
            if randint(0, 11) > 8 and len(particles) < 300:
                # if len(particles) < 5000:  # Тесты производительности
                SparkParticle(
                    (randint(20, self.surface.get_width() - 19), self.surface.get_height()),
                    particles)

            mouse_click_pos = (-1, -1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print(lowest_fps)
                    pygame.quit()
                    sys_exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.show = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_click_pos = event.pos

            self.surface.fill((0, 0, 0))
            particles.update()
            particles.draw(self.surface)
            for button in self.buttons:
                button.update()
                if mouse_click_pos != (-1, -1) and button.click(mouse_click_pos):
                    self.handle_click(button)
                if button.hover:
                    for layer, layer_offset in button.get_layers():
                        pos = [*button.get_relative_pos()]
                        pos[0] += layer_offset
                        self.surface.blit(layer, pos)
                self.surface.blit(button.render, button.get_relative_pos())

            fps = clock.get_fps()
            if fps != 0:
                lowest_fps = min(lowest_fps, clock.get_fps())
            pygame.display.flip()
            clock.tick(100)


class SparkParticle(pygame.sprite.Sprite):
    """На данный момент рандомизация работает через numpy. Стандартная библиотека random иногда вызывает заметные
    пропасти в FPS. Думаю, что numpy ещё очень сильно пригодится. Если он больше нигде не будет использоваться,
    то я всё-таки предпочту random"""

    # TODO: Добавить волновое движение частицы
    # TODO: Добавить уменьшение частицы с ходом времени

    def __init__(self, pos, *groups):
        super().__init__(*groups)
        size = randint(4, 11)
        self.image = pygame.Surface((size, size))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect().move(pos)

        self.speed_y = uniform(1, 4)

        self.half_width = self.rect.width / 2
        self.half_height = self.rect.height / 2

    def update(self):
        self.image.fill((0, 0, 0))
        opacity = randint(160, 256)

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
        if self.rect.top + self.rect.height < 0:
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
