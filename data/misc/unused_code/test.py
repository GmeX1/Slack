import time
from typing import Callable

import numpy as np
from PIL import Image


def sort_pixels(image: Image, value: Callable, condition: Callable, rotation: int = 0) -> Image:
    pixels = np.rot90(np.array(image), rotation)
    values = value(pixels)
    edges = np.apply_along_axis(lambda row: np.convolve(row, [-1, 1], 'same'), 0, condition(values))
    intervals = [np.flatnonzero(row) for row in edges]

    num = 1

    for row, key in enumerate(values):
        order = np.split(key, intervals[row])
        for index, interval in enumerate(order[1:]):
            order[index + 1] = np.argsort(interval) + intervals[row][index]
        order[0] = range(order[0].size)
        order = np.concatenate(order)

        for channel in range(3):
            pixels[row, :, channel] = pixels[row, order.astype('uint32'), channel]
        # if num % 10 == 0:
        #     Image.fromarray(np.rot90(pixels, -rotation)).save(f'out{num}.png')
        num += 1
    return Image.fromarray(np.rot90(pixels, -rotation))

start = time.time()
sort_pixels(Image.open('in2.png'),
            lambda pixels: np.average(pixels, axis=2) / 255,
            lambda lum: (lum > 2 / 6) & (lum < 4 / 6), 1).save('out.png')
print(time.time() - start)
