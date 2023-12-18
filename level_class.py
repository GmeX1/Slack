import os
import pygame
from converter import split_image
from tile_class import Tile


class Level:
    def __init__(self, image, level_name, surface):
        self.image = image
        self.pos = [0, 0]
        self.surface = surface
        self.tiles = pygame.sprite.Group()
        self.scroll_xy = (0, 0)

        # Подгрузка тайлов из файла имя_карты.tiles, либо свежая генерация с последующим сохранением в файл.
        # Синим цветом на маске обозначена точка спавна игрока.
        if not os.path.isfile(os.path.join(*['data', 'maps'], f'{level_name}.tiles')):
            # text = pygame.font.SysFont('Times New Roman', 100, True)
            # render = text.render('ЗАГРУЗКА...', True, (255, 0, 0))
            # self.surface.blit(
            #    render,
            #    (surface.get_width() / 2 - render.get_width() / 2, surface.get_height() / 2 - render.get_height() / 2))
            # TODO: Из-за того, что подгрузка тайлов происходит в ините, кадр не обновляется и таблички с загрузкой
            #  не видно. Нужно как-то переработать механизм так, чтобы можно было визуально оповестить о создании тайлов

            rects = split_image(f'data/maps/{level_name}_mask.png')
            open(f'data/maps/{level_name}.tiles', mode='w').write(str(rects))
        else:
            rects = eval(open(f'data/maps/{level_name}.tiles', mode='r').read())
        self.player_spawn_pos = rects.pop(rects.index(list(filter(lambda x: x[0] == (0, 0, 255, 255), rects))[0]))
        self.player_spawn_pos = self.player_spawn_pos[1][:2]
        [Tile(i[0], *i[1], self.tiles) for i in rects]

    def get_player_spawn(self):
        return self.player_spawn_pos

    def scroll(self, player):
        # TODO: Карочи, здесь проверяется положение игрока и создаётся смещение карты и тайлов, если игрок преодолевает
        #  определённый порог. Надо сделать отдельно ещё смещение камеры по Y по аналогии. Я закомментировал свой код,
        #  но он не работает должным образом. Почини пжлст.
        player_x = player.rect.centerx  # TODO: если спамить вправо или влево, можно преодолеть порог :(
        player_y = player.rect.centery
        if player_x < self.surface.get_width() / 6 and player.direction.x < 0:
            self.scroll_xy = (player.base_speed, self.scroll_xy[1])
            player.speed = 0
        elif player_x > (self.surface.get_width() / 6) * 5 and player.direction.x > 0:
            self.scroll_xy = (-player.base_speed, self.scroll_xy[1])
            player.speed = 0
        else:
            self.scroll_xy = (0, self.scroll_xy[1])
            player.speed = player.base_speed

        # if player_y < self.surface.get_height() / 6 and player.direction.y < 0:
        #     self.scroll_xy = (self.scroll_xy[0], -player.direction.y)
        #     # player.direction.y = 0
        # elif player_y > (self.surface.get_height() / 6) * 5 and player.direction.y > 0:
        #     self.scroll_xy = (self.scroll_xy[0], -player.direction.y)
        #     # player.direction.y = 0
        # else:
        #     self.scroll_xy = (self.scroll_xy[0], 0)

    def update(self):
        self.tiles.update(self.scroll_xy)
        self.pos[0] += self.scroll_xy[0]
        self.pos[1] += self.scroll_xy[1]

        # self.surface.blit(self.image, self.pos)  # Если надо отрисовать карту
        self.tiles.draw(self.surface)  # Если надо отрисовать сами тайлы
