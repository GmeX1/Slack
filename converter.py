from PIL import Image


def split_image(image_path):
    image = Image.open(image_path)
    width, height = image.size
    rectangles = list()

    for x in range(width):
        for y in range(height):
            pixel_color = image.getpixel((x, y))

            left = x
            right = x
            top = y
            bottom = y

            for dx in range(left - 1, -1, -1):
                if image.getpixel((dx, y)) == pixel_color:
                    left = dx
                else:
                    break

            for dx in range(right + 1, width):
                if image.getpixel((dx, y)) == pixel_color:
                    right = dx
                else:
                    break

            for dy in range(top - 1, -1, -1):
                if all(image.getpixel((x, dy)) == pixel_color for x in range(left, right + 1)):
                    top = dy
                else:
                    break

            for dy in range(bottom + 1, height):
                if all(image.getpixel((x, dy)) == pixel_color for x in range(left, right + 1)):
                    bottom = dy
                else:
                    break

            if (pixel_color, (left, top, right, bottom)) not in rectangles and pixel_color != (255, 255, 255, 255):
                for rect in rectangles:
                    if pixel_color == rect[0]:
                        inter_x = set(range(left, right)).intersection(set(range(rect[1][0], rect[1][2])))
                        inter_y = set(range(top, bottom)).intersection(set(range(rect[1][1], rect[1][3])))
                        if len(inter_x) != 0 and len(inter_y) != 0:
                            break
                else:
                    rectangles.append((pixel_color, (left, top, right, bottom)))
    return rectangles


rectangles = split_image("data/test.png")
for color, rectangle in rectangles:
    print(f"({color}, {rectangle})")
