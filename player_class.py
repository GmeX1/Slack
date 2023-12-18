import pygame


class Player(pygame.sprite.Sprite):  # TODO: У игрока нет анимаций :(
    def __init__(self, image, map_mask, pos, *groups):
        super().__init__(*groups)
        # TODO: невидимая пустота считается частью прямоугольника :( Нужно создать прямоугольник по маске для карты
        #  (см. player_idle_mask_new.png) со смещением, чтобы спрайт персонажа не съезжал в бок. Пока что коллизия идёт
        #  по прямоугольнику со спрайта, где персонаж стоит.
        self.image = image
        self.rect = self.image.get_rect().move(pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.map_mask = pygame.mask.from_surface(map_mask)

        self.base_speed = 8
        self.speed = 8
        self.jump_power = -10
        self.direction = pygame.math.Vector2(0, 0)
        self.collisions = {
            'left': False,
            'right': False,
            'top': False,
            'bottom': False
        }

    def jump(self):
        if self.collisions['bottom']:
            self.direction.y = self.jump_power

    def check_horizontal_collisions(self, tiles):
        collided = False
        for sprite in tiles.sprites():
            if self.rect.colliderect(sprite.rect):
                collided = True
                if self.direction.x > 0:
                    self.collisions['right'] = True
                    self.collisions['left'] = False
                    self.rect.right = sprite.rect.left
                elif self.direction.x < 0:
                    self.collisions['right'] = False
                    self.collisions['left'] = True
                    self.rect.left = sprite.rect.right
        if not collided:
            self.collisions['right'] = False
            self.collisions['left'] = False

    def check_vertical_collisions(self, tiles):
        collided = False
        for sprite in tiles.sprites():
            if self.rect.colliderect(sprite.rect):
                collided = True
                if self.direction.y > 0:
                    self.collisions['top'] = False
                    self.collisions['bottom'] = True
                    self.direction.y = 0
                    self.rect.bottom = sprite.rect.top
                elif self.direction.y < 0:
                    self.collisions['top'] = True
                    self.collisions['bottom'] = False
                    self.direction.y = 0
                    self.rect.top = sprite.rect.bottom
        if not collided:
            self.collisions['top'] = False
            self.collisions['bottom'] = False

    def update(self, tiles):
        self.rect.x += self.direction.x * self.speed
        self.check_horizontal_collisions(tiles)
        self.direction.y += 0.2
        self.rect.y += self.direction.y
        self.check_vertical_collisions(tiles)
