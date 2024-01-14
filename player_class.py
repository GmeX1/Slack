import pygame
from numpy import random

from particles import BloodParticle
from scripts import make_anim_list


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

        self.hp = 5
        self.base_speed = placeholder
        self.speed = self.base_speed
        self.jump_power = placeholder
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
        # if self.collisions['bottom']: # TODO: Расскомментить, тесты.
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
            self.image = self.frames['walk_r'][int(self.cur_frame)].copy()
        elif name == 'left':
            self.cur_frame += self.animation_speed
            self.cur_frame %= len(self.frames['walk_l'])
            self.image = self.frames['walk_l'][int(self.cur_frame)].copy()
        else:
            self.cur_frame = 0

        if name == 'idle_r':
            self.image = self.frames['idle_r'].copy()
        elif name == 'idle_l':
            self.image = self.frames['idle_l'].copy()

        if name == 'jump_r':
            self.direction.y = self.jump_power
            self.image = self.frames['jump_r'][int(self.cur_frame)].copy()
        elif name == 'jump_l':
            self.direction.y = self.jump_power
            self.image = self.frames['jump_l'][int(self.cur_frame)].copy()

        # TODO: посмотри на ходьбу влево и на ходьбу вправо. Вроде я отцентровал X, но это вообще не помогло(
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
        self.last_keys = 1
        self.map_rect = pygame.Rect(pos, (25, self.rect.height))

        self.kills = 0
        self.inv_time = 0
        self.combo = 0

        self.start_tick = pygame.time.get_ticks()
        self.last_shift_time = 0
        self.dashing = False
        self.raging = False

        self.base_speed = 8 if not self.walk_mode else 2
        self.speed = self.base_speed
        self.base_jump_power = -6 if not self.walk_mode else -3
        self.jump_power = self.base_jump_power

    def boost(self):  # TODO: Сделать уменьшение кулдаунов
        if self.combo > 1 and self.raging:
            mult = self.combo if self.combo < 6 else 7
            self.speed = self.base_speed + self.base_speed * mult * 0.1 + 3
            self.jump_power = self.base_jump_power + self.base_jump_power * mult * 0.1 + 3
            self.inv_time = 1500
        elif self.combo > 1:
            mult = self.combo if self.combo < 6 else 7
            self.speed = self.base_speed + self.base_speed * mult * 0.1
            self.jump_power = self.base_jump_power + self.base_jump_power * mult * 0.1
        elif self.raging:
            self.speed = self.base_speed + 3
            self.jump_power = self.base_jump_power - 3
            self.inv_time = 1500

    def import_anims(self, load_func):
        self.frames = {
            'idle_r': load_func('player\\idle\\idle_r.png'),
            'idle_l': load_func('player\\idle\\idle_l.png'),
            'walk_r': make_anim_list(load_func, 'player\\walk'),
            'walk_l': make_anim_list(load_func, 'player\\walk', True),
            'jump_r': make_anim_list(load_func, 'player\\jump'),
            'jump_l': make_anim_list(load_func, 'player\\jump', True)
        }

    def damage(self, value):
        if self.inv_time <= 0:
            self.hp -= value
            self.inv_time = 1500  # Полторы секунды неуязвимости при получении урона

    def kill_enemy(self):
        self.kills += 1

    def get_keys(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            if self.last_keys == 1:
                self.update_anim('left')
                self.direction.x = -1
            if self.last_keys == -1:
                self.update_anim('right')
                self.direction.x = 1
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.update_anim('left')
            self.direction.x = -1
            self.last_keys = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.update_anim('right')
            self.direction.x = 1
            self.last_keys = 1
        else:
            if self.last_keys == -1:
                self.update_anim('idle_l')
            elif self.last_keys == 1:
                self.update_anim('idle_r')
            self.direction.x = 0

        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            if self.last_keys == 1:
                self.update_anim('jump_r')
            elif self.last_keys == -1:
                self.update_anim('jump_l')

        if keys[pygame.K_LSHIFT] and pygame.time.get_ticks() - self.last_shift_time > 2000:
            if self.last_keys == 1:
                self.direction.x = 1
            elif self.last_keys == -1:
                self.direction.x = -1
                # Настроить под анимцию
            self.speed += 100
            self.dashing = True
            self.last_shift_time = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.last_shift_time <= 2000:
            self.speed = self.base_speed
            self.dashing = False

    def update(self, **kwargs):
        if not self.dashing:
            if self.combo or self.raging:
                self.boost()
            else:
                self.speed = self.base_speed
                self.jump_power = self.base_jump_power
                self.combo = -1

        self.map_rect.x += self.direction.x * self.speed
        self.check_horizontal_collisions(kwargs['tiles'])
        self.direction.y += 0.2
        self.map_rect.y += self.direction.y
        self.check_vertical_collisions(kwargs['tiles'])
        self.get_keys()
        if self.inv_time > 0:
            self.inv_time -= pygame.time.get_ticks() - self.start_tick
            if self.inv_time <= 0:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(100 + (1500 - self.inv_time) / (1500 / 125))
        self.start_tick = pygame.time.get_ticks()


class Bullet(Entity):
    def __init__(self, image, pos, last, initiator, *groups):
        super().__init__(image, pos, *groups)
        self.check_for = 'player' if initiator == 'enemy' else 'enemy'
        self.map_rect = self.rect.copy()
        # TODO: Кажется, придётся либо пулю делать больше, либо делать трассировку попадания :) Если скорость пули
        #  высокая, то она с большим шансом просто "перешагнёт" врага и коллизии формально не будет
        self.base_speed = 10
        self.direction.x = last

    def kill_entity(self, entities):
        if pygame.sprite.spritecollide(self, entities, False):
            if entities.__class__ is pygame.sprite.GroupSingle:
                if pygame.sprite.spritecollide(self, entities, False, collided=pygame.sprite.collide_mask):
                    entities.sprite.damage(1)
                    if entities.sprite.hp <= 0:
                        entities.sprite.kill()
                        self.kill()
                        return True
                    self.kill()
            else:
                for entity in pygame.sprite.spritecollide(self, entities, False, collided=pygame.sprite.collide_mask):
                    entity.hp -= 1
                    [BloodParticle(entity.rect.center, *self.groups()) for _ in range(random.randint(5, 13))]
                    if entity.hp <= 0:
                        entity.kill()
                        self.kill()
                        return True
                    self.kill()
        return False

    def update(self, **kwargs):
        self.map_rect.x += self.base_speed * self.direction.x
        # Поскольку у пули анимаций нет, то просто переписываем координаты с прямоугольника карты на прямоугольник
        # изображения. С врагом пока что аналогично, потому что там тоже нет анимаций (пока что)
        self.rect.x = self.map_rect.x
        if self.check_for == 'enemy':
            answer = self.kill_entity(kwargs['enemies'])
            if answer:
                kwargs['player'].sprite.kill_enemy()
        else:
            self.kill_entity(kwargs['player'])

        self.check_horizontal_collisions(kwargs['tiles'])
        # Я думаю, что возможен вариант диагональных пуль. Потом посмотрим, как пойдёт, но было бы неплохо такое сделать
        self.check_vertical_collisions(kwargs['tiles'])
        if self.collisions['right'] or self.collisions['left']:
            self.kill()


class Enemy(Entity):
    def __init__(self, image, pos, player, built_icon, *groups):
        super().__init__(image, pos, *groups)
        self.image.fill((0, 0, 255))
        self.mask = pygame.mask.from_surface(self.image)
        self.map_rect = self.rect.copy()

        self.hp = 2
        self.base_speed = 2
        self.speed = self.base_speed
        self.built_icon = built_icon
        self.standing_time = 0
        self.choose_direction()
        self.time_to_change_direction = random.uniform(1, 4)
        self.player = player

        self.shoot_timer = pygame.time.get_ticks()

        self.last_direction_x = 1

    def choose_direction(self):
        self.direction.x = random.choice([-1, 1])

    def check_time_event(self):
        self.standing_time += 1 / 100
        if self.standing_time >= self.time_to_change_direction:
            self.choose_direction()
            self.standing_time = 1
            self.time_to_change_direction = random.uniform(1, 4)
            self.check_player()

    def check_player(self):
        if abs(self.player.map_rect.x - self.map_rect.x) < 300 and (self.player.map_rect.y + 50) >= self.map_rect.y:
            if self.player.map_rect.x < self.map_rect.x:
                self.direction.x = -1
                self.standing_time = 0
                return True

            elif self.player.map_rect.x > self.map_rect.x:
                self.direction.x = 1
                self.standing_time = 0
                return True

    def check_last_direction(self):
        if self.direction.x == 1:
            self.last_direction_x = 1
        elif self.direction.x == -1:
            self.last_direction_x = -1

    def enemy_attack(self):
        if abs(self.player.map_rect.x - self.map_rect.x) < 50 and (self.player.map_rect.y + 50) >= self.map_rect.y \
                and pygame.time.get_ticks() - self.shoot_timer > 600:
            Bullet(self.built_icon, self.map_rect.center, self.last_direction_x, 'enemy', *self.groups())

            self.shoot_timer = pygame.time.get_ticks()

    def update(self, **kwargs):
        self.check_last_direction()
        self.enemy_attack()

        if self.check_player():
            self.map_rect.x += self.direction.x * self.speed
            self.rect.x = self.map_rect.x
            self.check_horizontal_collisions(kwargs['tiles'])

            self.direction.y += 0.2
            self.map_rect.y += self.direction.y
            self.rect.y = self.map_rect.y
            self.check_vertical_collisions(kwargs['tiles'])

        else:
            self.check_time_event()
            self.map_rect.x += self.direction.x * self.speed
            self.rect.x = self.map_rect.x
            self.check_horizontal_collisions(kwargs['tiles'])

            self.direction.y += 0.2
            self.map_rect.y += self.direction.y
            self.rect.y = self.map_rect.y
            self.check_vertical_collisions(kwargs['tiles'])
