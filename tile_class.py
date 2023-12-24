import pygame
from numpy.random import randint


class Tile(pygame.sprite.Sprite):
    def __init__(self, color, left, top, right, bottom, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((right - left, bottom - top))
        # self.image.fill(color)
        self.image.fill((randint(0, 256), randint(0, 256), randint(0, 256)))
        # Заполнение выше необязательно. Необходимо для удобной визуальной отладки
        self.rect = self.image.get_rect(topleft=(left, top))

    def update(self, xy):
        self.rect = self.rect.move(xy)
