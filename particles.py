import pygame
from numpy import cos, pi, sin
from numpy.random import randint, uniform


class BloodParticle(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        size = randint(2, 7)
        self.image = pygame.Surface((size, size))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect().move(pos)

        self.half_width = self.rect.width / 2
        self.half_height = self.rect.height / 2
        self.radius = self.half_width
        self.shrink_speed = uniform(0.0005, 0.05)
        self.direction = pygame.math.Vector2(randint(-2, 3), randint(-5, 1))

    def update(self, **kwargs):
        self.image.fill((0, 0, 0))
        pygame.draw.circle(
            self.image,
            (255, 25, 25),
            (self.half_width, self.half_height),
            self.radius
        )

        self.rect.x += self.direction.x
        self.rect.y += self.direction.y

        self.direction.y += 0.2
        self.radius -= self.shrink_speed
        if self.radius <= 0:
            self.kill()


class SparkParticle(pygame.sprite.Sprite):
    # TODO: Возможно стоит добавить beat sync?
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
        self.func = sin if randint(0, 2) else cos

        self.half_width = self.rect.width / 2
        self.half_height = self.rect.height / 2

    def update(self, **kwargs):
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


class DashFX:
    class BaseSprite(pygame.sprite.Sprite):
        def __init__(self, image, pos, *groups):
            super().__init__(*groups)
            self.image = image
            self.rect = image.get_rect().move(pos)
            self.opacity = 255

        def lower_opacity(self):
            self.opacity -= 3.5
            if self.opacity < 0:
                self.kill()
            else:
                self.image.set_alpha(self.opacity)

    def __init__(self, camera):
        self.images = list()
        self.camera = camera
        self.image = None
        self.start_pos = None
        self.end_pos = None

    def set_start(self, image, pos):
        self.image = image
        self.image.set_alpha(255)
        self.start_pos = pos
        # self.images.append(DashFX.BaseSprite(image, pos, self.camera))

    def set_end(self, pos):
        self.end_pos = pos
        max_offset_x = self.end_pos[0] - self.start_pos[0]
        max_offset_y = self.end_pos[1] - self.start_pos[1]
        for i in range(10):
            if i > 0:
                pos = (self.start_pos[0] + (max_offset_x / 10) * i, self.start_pos[1] + (max_offset_y / 10) * i)
            else:
                pos = (self.start_pos[0], self.start_pos[1])
            self.images.append(DashFX.BaseSprite(self.image, pos, self.camera))
        self.start_pos = self.end_pos = self.image = None

    def clear_effect(self):
        self.images.clear()

    def draw(self):
        if len(self.images) > 0:
            for image in self.images:
                image.lower_opacity()
                if not image.alive():
                    self.images.remove(image)
