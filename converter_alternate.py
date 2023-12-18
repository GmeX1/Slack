from PIL import Image, ImageDraw
from random import randint
import time


def split_image(image_path, draw=False):
    def draw_rects():
        image_new = Image.new('RGBA', (width, height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image_new)
        for rect in rectangles:
            draw.rectangle(rect[1], fill=(randint(0, 255), randint(0, 255), randint(0, 255), 255))
        image_new.save('data/rectangles.png')

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

            while True:
                inter_x = len(image.crop((left, top, right + 1, bottom)).getcolors())
                inter_y = len(image.crop((left, top, right, bottom + 1)).getcolors())
                if inter_x < 2:
                    right += 1
                if inter_y < 2:
                    bottom += 1
                if inter_x > 1 and inter_y > 1:
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
        draw_rects()
    return rectangles


start_time = time.time()
rectangles = split_image("../../PyGame/copy/data/test_lvl_mask.png", True)
print("--- %s seconds ---" % (time.time() - start_time))
for rect in rectangles:
    print(rect)
