import os
import sqlite3
from PIL import Image, ImageDraw
from numpy.random import randint
from pygame import transform


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


def make_anim_list(load_func, path, flip=False):
    """Функция для получения списка поверхностей из определённой директории"""
    anim_list = []
    for _, __, image_files in os.walk('data\\' + path):
        for image in image_files:
            anim_list.append(transform.flip(load_func(f'{path}\\' + image), flip_x=flip, flip_y=False))
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
