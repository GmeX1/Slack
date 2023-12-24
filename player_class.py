import pygame
from scripts import make_anim_list


class Player(pygame.sprite.Sprite):
    def __init__(self, image, pos, walk=False, *groups):
        super().__init__(*groups)
        self.frames = dict()
        self.cur_frame = 0
        self.animation_speed = 0.15 if walk else 0.15 * 4
        self.walk_mode = walk

        self.image = image
        self.rect = self.image.get_rect().move(pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.base_speed = 8 if not self.walk_mode else 2
        self.speed = self.base_speed
        self.jump_power = -6 if not self.walk_mode else -3
        self.direction = pygame.math.Vector2(0, 0)
        self.collisions = {
            'left': False,
            'right': False,
            'top': False,
            'bottom': False,
            'collision_x': 0
        }

    def import_anims(self, load_func):
        self.frames = {
            'idle_r': load_func('player\\idle\\idle_r.png'),
            'idle_l': load_func('player\\idle\\idle_l.png'),
            'walk_r': make_anim_list(load_func, 'player\\walk'),
            'walk_l': make_anim_list(load_func, 'player\\walk', True)
        }

    def jump(self):
        if self.collisions['bottom']:
            self.direction.y = self.jump_power

    # TODO: Обнаружил баг, при котором во время прыжка игрок может начать немного проходить сквозь стены
    def check_horizontal_collisions(self, tiles):
        for sprite in tiles.sprites():
            if self.rect.colliderect(sprite.rect):
                if self.direction.x > 0:
                    self.collisions['right'] = True
                    self.collisions['collision_x'] = sprite.rect.left
                    self.rect.right = sprite.rect.left
                elif self.direction.x < 0:
                    self.collisions['left'] = True
                    self.collisions['collision_x'] = sprite.rect.right
                    self.rect.left = sprite.rect.right

        if self.collisions['right'] and self.rect.right > self.collisions['collision_x']:
            self.collisions['right'] = False
        if self.collisions['left'] and self.rect.left < self.collisions['collision_x']:
            self.collisions['left'] = False

    def check_vertical_collisions(self, tiles):
        for sprite in tiles.sprites():
            if self.rect.colliderect(sprite.rect):
                if self.direction.y > 0:
                    self.collisions['bottom'] = True
                    self.direction.y = 0
                    self.rect.bottom = sprite.rect.top
                elif self.direction.y < 0:
                    self.collisions['top'] = True
                    self.direction.y = 0
                    self.rect.top = sprite.rect.bottom

        if self.collisions['bottom'] and self.direction.y < 0 or self.direction.y > 1:
            self.collisions['bottom'] = False
        if self.collisions['top'] and self.direction.y > 0:
            self.collisions['top'] = False

    def update_anim(self, name):
        if name == 'right':
            self.cur_frame += self.animation_speed
            self.cur_frame %= len(self.frames['walk_r'])
            self.image = self.frames['walk_r'][int(self.cur_frame)]
        elif name == 'left':
            self.cur_frame += self.animation_speed
            self.cur_frame %= len(self.frames['walk_l'])
            self.image = self.frames['walk_l'][int(self.cur_frame)]
        else:
            self.cur_frame = 0
        if name == 'idle_r':
            self.image = self.frames['idle_r']
        elif name == 'idle_l':
            self.image = self.frames['idle_l']

        # Часть коллизий закомментирована, поскольку у персонажа не хватает анимаций.
        if self.collisions['bottom'] and self.collisions['right']:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.collisions['bottom'] and self.collisions['left']:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.collisions['bottom']:
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif self.collisions['top'] and self.collisions['right']:
            self.rect = self.image.get_rect(topright=self.rect.topright)
        elif self.collisions['top'] and self.collisions['left']:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        elif self.collisions['top']:
            self.rect = self.image.get_rect(midtop=self.rect.midtop)

    def update(self, tiles):
        self.rect.x += self.direction.x * self.speed
        self.check_horizontal_collisions(tiles)
        self.direction.y += 0.2
        self.rect.y += self.direction.y
        self.check_vertical_collisions(tiles)
