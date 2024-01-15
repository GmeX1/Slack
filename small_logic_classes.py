import os

import pygame

# from numpy.random import randint
from scripts import split_image, load_image


class Level:
    def __init__(self, level_name, camera, surface):
        self.image = load_image(f'maps\\{level_name}.png')
        self.surface = surface
        self.tiles = pygame.sprite.Group()

        # Подгрузка тайлов из файла имя_карты.tiles, либо свежая генерация с последующим сохранением в файл.
        # Синим цветом на маске обозначена точка спавна игрока.
        # Жёлтым цветом на маске обозначен режим игры (сюжетный или основной)
        # Красным цветом на маске обозначены враги
        if not os.path.isfile(os.path.join(*['data', 'maps'], f'{level_name}.tiles')):
            print('По какой-то причине тайлы отсутствуют, генерация...')
            rects = split_image(f'data/maps/{level_name}_mask.png')
            open(f'data/maps/{level_name}.tiles', mode='w').write(str(rects))
        else:
            rects = eval(open(f'data/maps/{level_name}.tiles', mode='r').read())

        self.player_spawn_pos = rects.pop(rects.index(list(filter(lambda x: x[0] == (0, 0, 255, 255), rects))[0]))
        self.player_spawn_pos = self.player_spawn_pos[1][:2]

        # Режим карты, необходим для определения переключателя ходьба/бег у игрока
        self.story_mode = list(filter(lambda x: x[0] == (255, 255, 0, 255), rects))
        if self.story_mode:
            rects.pop(rects.index(self.story_mode[0]))
            self.story_mode = True
        else:
            self.story_mode = False

        self.enemies_pos = list(filter(lambda x: x[0] == (255, 0, 0, 255), rects))
        if self.enemies_pos:
            self.enemies_pos = list(map(lambda x: rects.pop(rects.index(x))[1][:2], self.enemies_pos))
        else:
            self.enemies_pos = None

        [Tile(i[0], *i[1], self.tiles, camera) for i in rects]

    def get_enemies_pos(self):
        return self.enemies_pos

    def get_story_mode(self):
        return self.story_mode

    def get_player_spawn(self):
        return self.player_spawn_pos


class Camera(pygame.sprite.Group):
    def __init__(self, surface):
        super().__init__()
        self.surface = surface
        self.pre_surface = pygame.Surface(self.surface.get_size())

        self.offset = pygame.math.Vector2(0, 0)
        self.maximum = (float('inf'), float('inf'))

        self.resize_coef = 1
        self.map_image = None
        self.map_rect = None
        self.borders = {
            'left': self.surface.get_width() / 4,
            'right': self.surface.get_width() / 4 * 3,
            'top': self.surface.get_height() / 4,
            'bottom': self.surface.get_height() / 4 * 3
        }
        self.pos_rect = pygame.Rect(
            self.borders['left'],
            self.borders['top'],
            self.borders['right'] - self.borders['left'],
            self.borders['bottom'] - self.borders['top']
        )

    def get_map_image(self, image):
        self.map_image = image
        self.map_rect = self.map_image.get_rect()
        if self.map_image.get_height() < self.surface.get_height():
            self.resize_coef = self.surface.get_height() / self.map_image.get_height()
            if self.resize_coef > 2:
                self.resize_coef = 2
            self.borders = {
                'left': self.surface.get_width() * self.resize_coef / 4,
                'right': self.surface.get_width() * self.resize_coef / 4 * 3,
                'top': self.surface.get_height() * self.resize_coef / 4,
                'bottom': self.surface.get_height() * self.resize_coef / 4 * 3
            }
            self.pos_rect = pygame.Rect(
                self.borders['left'],
                self.borders['top'],
                self.borders['right'] - self.borders['left'],
                self.borders['bottom'] - self.borders['top']
            )
        self.maximum = (image.get_width() * self.resize_coef, image.get_height() * self.resize_coef)

    def draw_offset(self, player):
        if player.map_rect.left < self.pos_rect.left:
            self.pos_rect.left = player.map_rect.left
        elif player.map_rect.right > self.pos_rect.right:
            self.pos_rect.right = player.map_rect.right

        if player.map_rect.top < self.pos_rect.top:
            self.pos_rect.top = player.map_rect.top
        elif player.map_rect.bottom > self.pos_rect.bottom:
            self.pos_rect.bottom = player.map_rect.bottom

        if self.maximum[0] - self.borders['left'] < self.pos_rect.right:
            self.pos_rect.right = self.maximum[0] - self.borders['left']
        if self.maximum[1] - self.borders['top'] < self.pos_rect.bottom:
            self.pos_rect.bottom = self.maximum[1] - self.borders['top']

        self.offset.x = self.pos_rect.left - self.borders['left']
        self.offset.y = self.pos_rect.top - self.borders['top']

        if self.offset.x < 0:
            self.offset.x = 0
        if self.offset.y < 0:
            self.offset.y = 0

        if self.map_image:
            pos = self.map_rect.topleft - self.offset
            self.pre_surface.blit(self.map_image, pos)

        for sprite in self.sprites():
            if hasattr(sprite, 'map_rect'):
                pos = sprite.map_rect.topleft - self.offset
            else:
                pos = sprite.rect.topleft - self.offset
            if sprite.__class__ != Tile:
                # Небольшая проверка для оптимизации (Culling)
                if (pos[0] < self.surface.get_width() and pos[1] < self.surface.get_height()
                        and pos[0] + sprite.image.get_width() > -1 and pos[1] + sprite.image.get_height() > -1):
                    self.pre_surface.blit(sprite.image, pos)

        # Если комната слишком маленькая, то будет производиться ресайз
        if self.resize_coef != 1:
            rescaled_surface = pygame.transform.scale(
                self.pre_surface,
                (self.pre_surface.get_width() * self.resize_coef, self.pre_surface.get_height() * self.resize_coef)
            )
            rescaled_rect = rescaled_surface.get_rect()
            self.surface.blit(rescaled_surface, rescaled_rect)
        else:
            self.surface.blit(self.pre_surface, (0, 0))


class Tile(pygame.sprite.Sprite):
    def __init__(self, color, left, top, right, bottom, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((right - left, bottom - top))
        self.image.fill(color)
        # self.image.fill((randint(0, 256), randint(0, 256), randint(0, 256)))
        # Заполнение выше необязательно. Необходимо для удобной визуальной отладки
        self.rect = self.image.get_rect(topleft=(left, top))

    def update(self, xy):
        self.rect = self.rect.move(xy)
