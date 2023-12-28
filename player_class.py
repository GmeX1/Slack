import pygame
from scripts import make_anim_list
from numpy import random
import time


class Entity(pygame.sprite.Sprite):
    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        placeholder = 1  # Это типа вместо None, чтобы вставить хотя бы какие-то цифры

        self.frames = dict()
        self.cur_frame = 0
        self.animation_speed = placeholder

        self.image = image
        self.rect = self.image.get_rect().move(pos)
        self.map_rect = pygame.Rect(pos, (placeholder, self.rect.height))
        self.mask = pygame.mask.from_surface(self.image)

        self.base_speed = placeholder
        self.speed = self.base_speed
        self.jump_power = 10
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
            'idle_r': load_func(),
            'idle_l': load_func(None),
            'walk_r': make_anim_list(load_func, None),
            'walk_l': make_anim_list(load_func, None, True)
        }

    def jump(self):
        if self.collisions['bottom']:
            self.direction.y = self.jump_power

    def check_horizontal_collisions(self, tiles):
        for sprite in tiles.sprites():
            if self.map_rect.colliderect(sprite.rect):
                if self.direction.x > 0:
                    self.collisions['right'] = True
                    self.collisions['collision_x'] = sprite.rect.left
                    self.map_rect.right = sprite.rect.left
                elif self.direction.x < 0:
                    self.collisions['left'] = True
                    self.collisions['collision_x'] = sprite.rect.right
                    self.map_rect.left = sprite.rect.right

        if self.collisions['right'] and self.map_rect.right > self.collisions['collision_x']:
            self.collisions['right'] = False
        if self.collisions['left'] and self.map_rect.left < self.collisions['collision_x']:
            self.collisions['left'] = False

    def check_vertical_collisions(self, tiles):
        for sprite in tiles.sprites():
            if self.map_rect.colliderect(sprite.rect):
                if self.direction.y > 0:
                    self.collisions['bottom'] = True
                    self.direction.y = 0
                    self.map_rect.bottom = sprite.rect.top
                elif self.direction.y < 0:
                    self.collisions['top'] = True
                    self.direction.y = 0
                    self.map_rect.top = sprite.rect.bottom

        if self.collisions['bottom'] and self.direction.y < 0:
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

        # TODO: посмотри на ходьюу влево и на ходьбу вправо. Вроде я отцентровал X, но это вообще не помогло(
        self.rect = self.image.get_rect(midbottom=self.map_rect.midbottom)

    def update(self, **kwargs):
        self.map_rect.x += self.direction.x * self.speed
        self.check_horizontal_collisions(kwargs['tiles'])
        self.direction.y += 0.2
        self.map_rect.y += self.direction.y
        self.check_vertical_collisions(kwargs['tiles'])


class Player(Entity):
    def __init__(self, image, pos, walk=False, *groups):
        super().__init__(image, pos, *groups)
        self.animation_speed = 0.15 if walk else 0.15 * 4
        self.walk_mode = walk
        self.last_keys = 100
        self.map_rect = pygame.Rect(pos, (25, self.rect.height))

        self.start_time = time.time()
        self.elapsed_time = 0
        self.last_shift_time = 0

        self.base_speed = 8 if not self.walk_mode else 2
        self.speed = self.base_speed
        self.jump_power = -6 if not self.walk_mode else -3

    def import_anims(self, load_func):
        self.frames = {
            'idle_r': load_func('player\\idle\\idle_r.png'),
            'idle_l': load_func('player\\idle\\idle_l.png'),
            'walk_r': make_anim_list(load_func, 'player\\walk'),
            'walk_l': make_anim_list(load_func, 'player\\walk', True)
        }

    def get_keys(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            if self.last_keys == pygame.K_d:
                self.update_anim('left')
                self.direction.x = -1
            if self.last_keys == pygame.K_a:
                self.update_anim('right')
                self.direction.x = 1
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.update_anim('left')
            self.direction.x = -1
            self.last_keys = pygame.K_a
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.update_anim('right')
            self.direction.x = 1
            self.last_keys = pygame.K_d
        else:
            if self.last_keys == pygame.K_a:
                self.update_anim('idle_l')
            elif self.last_keys == pygame.K_d:
                self.update_anim('idle_r')
            self.direction.x = 0
        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.jump()
        if keys[pygame.K_LSHIFT] and time.time() - self.last_shift_time > 2:
            if self.direction.x == 1:
                self.map_rect.x *= 1.5
            elif self.direction.x == -1:
                self.map_rect.x /= 1.5
            self.last_shift_time = time.time()

    def update(self, **kwargs):
        self.map_rect.x += self.direction.x * self.speed
        self.check_horizontal_collisions(kwargs['tiles'])
        self.direction.y += 0.2
        self.map_rect.y += self.direction.y
        self.check_vertical_collisions(kwargs['tiles'])
        self.elapsed_time = int(time.time() - self.start_time)
        self.get_keys()


class Bullet(Entity):
    def __init__(self, image, pos, last, initiator, *groups):
        super().__init__(image, pos, *groups)
        self.check_for = 'player' if initiator == 'enemy' else 'enemy'
        self.map_rect = self.rect.copy()
        self.base_speed = 50
        self.direction.x = -1 if last < 100 else 1

    def kill_entity(self, enemies):
        if pygame.sprite.spritecollide(self, enemies, True, collided=pygame.sprite.collide_mask):
            self.kill()

    def update(self, **kwargs):
        self.map_rect.x += self.base_speed * self.direction.x
        # Поскольку у пули анимаций нет, то просто переписываем координаты с прямоугольника карты на прямоугольник
        # изображения. С врагом пока что аналогично, потому что там тоже нет анимаций (пока что)
        self.rect.x = self.map_rect.x

        if self.check_for == 'enemy':
            self.kill_entity(kwargs['enemies'])
        else:
            pass  # Если враги будут стрелять, то пригодится

        self.kill_entity(kwargs['enemies'])
        self.check_horizontal_collisions(kwargs['tiles'])
        # Я думаю, что возможен вариант диагональных пуль. Потом посмотрим, как пойдёт, но было бы неплохо такое сделать
        self.check_vertical_collisions(kwargs['tiles'])
        if self.collisions['right'] or self.collisions['left']:
            self.kill()


class Enemy(Entity):
    def __init__(self, image, pos, live, player, *groups):
        super().__init__(image, pos, *groups)
        self.image.fill((255, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.map_rect = self.rect.copy()

        self.base_speed = 2
        self.speed = self.base_speed

        self.standing_time = 0
        self.choose_direction()
        self.time_to_change_direction = random.uniform(1, 4)
        self.live = live
        self.player = player
        self.attack = None
        self.last_direction_x = 0

    def choose_direction(self):
        self.direction.x = random.choice([-1, 1])

    def check_time_event(self):
        # Не виду смысла подвязывать настоящее время, т.к если игрок свернёт игру, то получитсья баг
        self.standing_time += 1 / 100
        if self.standing_time >= self.time_to_change_direction:
            self.choose_direction()
            self.standing_time = 2
            self.time_to_change_direction = random.uniform(1, 4)
            self.chech_player()

    def chech_player(self):
        if abs(self.player.map_rect.x - self.map_rect.x) < 250:
            if self.player.map_rect.x < self.map_rect.x:
                self.direction.x = -1
                self.standing_time = 0
                return True

            elif self.player.map_rect.x > self.map_rect.x:
                self.direction.x = 1
                self.standing_time = 0
                return True

    def update(self, **kwargs):
        if self.chech_player():
            self.map_rect.x += self.direction.x * self.speed
            self.rect.x = self.map_rect.x
            self.check_horizontal_collisions(kwargs['tiles'])

            self.direction.y += 0.2
            self.map_rect.y += self.direction.y
            self.rect.x = self.map_rect.x
            self.check_vertical_collisions(kwargs['tiles'])
        else:
            self.check_time_event()
            self.map_rect.x += self.direction.x * self.speed
            self.rect.x = self.map_rect.x
            self.check_horizontal_collisions(kwargs['tiles'])

            self.direction.y += 0.2
            self.map_rect.y += self.direction.y
            self.rect.x = self.map_rect.x
            self.check_vertical_collisions(kwargs['tiles'])

            if self.collisions['left'] or self.collisions['right']:
                self.direction.x = 0
