import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, image, map_mask, pos, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect().move(pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.map_mask = pygame.mask.from_surface(map_mask)

        self.speed = 10
        self.jump_power = -8
        self.direction = pygame.math.Vector2(0, 0)

        self.on_ground = True
        self.on_tile = True

    def jump(self):
        self.direction.y = self.jump_power

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.direction.y += 0.2
        self.rect.y += self.direction.y
