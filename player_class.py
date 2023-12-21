import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, image, map_mask, pos, walk=False, *groups):
        super().__init__(*groups)
        # TODO: невидимая пустота считается частью прямоугольника :( Чтобы не создавать кучу отдельных изображений для
        #  коллизий, я (Максим) позже переделаю изображения персонажа, сразу вырезав пустоту
        self.frames = []
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
            'left_x': 0,
            'right': False,
            'right_x': 0,
            'top': False,
            'bottom': False,
        }

    def jump(self):
        if self.collisions['bottom']:
            self.direction.y = self.jump_power

    def check_horizontal_collisions(self, tiles):
        for sprite in tiles.sprites():
            if self.rect.colliderect(sprite.rect):
                if self.direction.x > 0:
                    self.collisions['right'] = True
                    self.collisions['right_x'] = sprite.rect.left
                    self.rect.right = sprite.rect.left
                elif self.direction.x < 0:
                    self.collisions['left'] = True
                    self.collisions['left_x'] = sprite.rect.right
                    self.rect.left = sprite.rect.right

        if self.collisions['right'] and (self.rect.right < self.collisions['right_x'] or self.direction.x < 0):
            self.collisions['right'] = False
        if self.collisions['left'] and (self.rect.left > self.collisions['left_x'] or self.direction.x > 0):
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

    def cut_sheet(self, sheet, columns, rows, animation_index):
        image = list()
        frame_width = sheet.get_width() // columns
        frame_height = sheet.get_height() // rows
        rect = pygame.Rect(0, frame_height * animation_index + 1, frame_width, frame_height)
        for i in range(columns):
            frame_location = (rect.w * i, 0)
            image.append(sheet.subsurface(pygame.Rect(frame_location, rect.size)))
        self.frames.append(image)

    def update_anim(self, name):
        if name == 'right':
            self.cur_frame += self.animation_speed
            self.cur_frame %= len(self.frames[0])
            self.image = self.frames[0][int(self.cur_frame)]
        elif name == 'left':
            self.cur_frame += self.animation_speed
            self.cur_frame %= len(self.frames[1])
            self.image = self.frames[1][int(self.cur_frame)]
        else:
            self.cur_frame = 0
        if name == 'idle_r':
            self.image = self.frames[2]
        elif name == 'idle_l':
            self.image = self.frames[3]

        # TODO: К сожалению, во время прыжка и ходьбы одновременно коллизии ломаются. Пока что не знаю, как фиксить
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
        # elif self.collisions['right']:
        #     self.rect = self.image.get_rect(right=self.rect.right)
        #     print(self.rect)
        # elif self.collisions['left']:
        #     self.rect = self.image.get_rect(left=self.rect.left)
        # else:
        #     self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, tiles):
        self.rect.x += self.direction.x * self.speed
        self.check_horizontal_collisions(tiles)
        self.direction.y += 0.2
        self.rect.y += self.direction.y
        self.check_vertical_collisions(tiles)
