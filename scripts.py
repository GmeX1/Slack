import os
import sqlite3
import sys

import pygame
from PIL import Image, ImageDraw
from numpy.random import randint


def show_fps(screen, clock):
    font = pygame.font.Font('data\\fonts\\better-vcr.ttf', 48)
    screen.blit(font.render(str(round(clock.get_fps())), True, (255, 255, 255)), (5, 5))


def database_create():
    database = sqlite3.connect('data\\db\\gamedata.db')
    cur = database.cursor()
    cur.execute('''
        CREATE TABLE settings (
        id    INTEGER PRIMARY KEY ASC AUTOINCREMENT
                      UNIQUE
                      NOT NULL,
        name  TEXT    UNIQUE
                      NOT NULL,
        value INTEGER NOT NULL
        );''')
    database.commit()
    return database


def time_convert(msecs):
    hours, remaining = divmod(msecs, 3600000)
    minutes, remaining = divmod(remaining, 60000)
    seconds, remaining = divmod(remaining, 1000)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'


def load_image(name, colorkey=None):
    path = ['data']
    if '\\' in name:
        [path.append(i) for i in name.split('\\')]
    else:
        path.append(name)
    fullname = os.path.join(*path)

    if not os.path.isfile(fullname):
        print(f"File '{fullname}' not found")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def generate_tiles():
    for path, _, files in os.walk('data\\maps'):
        for file in files:
            if file.endswith('.png') and '_mask' not in file:
                filename = file.split(".")[0]
                if not os.path.isfile(os.path.join(path, f'{filename}.tiles')):
                    rects = split_image(f'data/maps/{filename}_mask.png')
                    open(f'data/maps/{filename}.tiles', mode='w').write(str(rects))


def delete_all_tiles():
    for path, _, files in os.walk('data\\maps'):
        for file in files:
            if file.endswith('.tiles'):
                os.remove(os.path.join(path, file))


def make_anim_list(path, flip=False):
    """Функция для получения списка поверхностей из определённой директории"""
    anim_list = []
    for _, __, image_files in os.walk('data\\' + path):
        image_files.sort()
        for image in image_files:
            anim_list.append(pygame.transform.flip(load_image(f'{path}\\' + image), flip_x=flip, flip_y=False))
    return anim_list


def split_image(image_path, draw=False):
    """
    С помощью PIl проходим по пикселям и выделяем оттуда все НЕбелые прямоугольники, содержаие только 1 цвет.
    При стандартном запуске на выходе получаем список с прямоугольниками в формате:
        (цвет, (левый x, верхний y, правый x, нижний y)
    При включённой переменной "draw" также создаётся изображение rectangles.png, отображающее все прямоугольники,
    найденные в маске
    """

    image = Image.open(image_path)
    width, height = image.size
    rectangles = list()
    pixels = image.load()

    for x in range(width):
        for y in range(height):
            pixel_color = pixels[x, y]
            if pixel_color == (255, 255, 255, 255):
                continue

            flag = False
            for rect in rectangles:
                if pixel_color == rect[0]:
                    if x in range(rect[1][0], rect[1][2] + 1) and y in range(rect[1][1], rect[1][3] + 1):
                        flag = True
                        break
            if flag:
                continue

            left = x
            right = x
            top = y
            bottom = y

            for dx in range(left - 1, -1, -1):
                if pixels[dx, y] == pixel_color:
                    left = dx
                else:
                    break

            for dx in range(right + 1, width):
                if pixels[dx, y] == pixel_color:
                    right = dx
                else:
                    break

            for dy in range(top - 1, -1, -1):
                if all(pixels[x, dy] == pixel_color for x in range(left, right + 1)):
                    top = dy
                else:
                    break

            for dy in range(bottom + 1, height):
                if all(pixels[x, dy] == pixel_color for x in range(left, right + 1)):
                    bottom = dy
                else:
                    break

            if (pixel_color, (left, top, right, bottom)) not in rectangles and pixel_color != (255, 255, 255, 255):
                for rect in rectangles:
                    if pixel_color == rect[0]:
                        inter = right <= rect[1][0] or left >= rect[1][2] or top <= rect[1][3] or bottom >= rect[1][1]
                        if not inter:
                            break
                else:
                    rectangles.append((pixel_color, (left, top, right, bottom)))
    if draw:
        image_new = Image.new('RGBA', (width, height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image_new)
        for rect in rectangles:
            draw.rectangle(rect[1], fill=(randint(0, 256), randint(0, 256), randint(0, 256), 255))
        image_new.save('data/rectangles.png')
    return rectangles
