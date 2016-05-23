from os import listdir
from os.path import join, isfile

from PIL import Image, ImageDraw
import numpy as np


IMAGE_SIZE = 300    # Resize minimum side of image to this with aspect ratio
CONVERT_MODE = 'L'  # Grayscale (default)

SOURCE_CLEAR_PATH = './images/source/clear'         # Sources without border
SOURCE_BORDERED_PATH = './images/source/bordered'   # Bordered sources

DETECTED_CLEAR_PATH = './images/detected/clear'         # No border results
DETECTED_BORDERED_PATH = './images/detected/bordered'   # Bordered results

# If upper entropy divided by lower entropy is lower than this - assume that
# image has border on the particular side
# Make it lower to exclude monotone cases and higher to crop every image which
# has real content
MEDIAN = 0.5


# Source files - clear and bordered, sorted alphabetically
source_clear_files = sorted(_ for _ in listdir(SOURCE_CLEAR_PATH)
                            if isfile(join(SOURCE_CLEAR_PATH, _)))
source_bordered_files = sorted(_ for _ in listdir(SOURCE_BORDERED_PATH)
                               if isfile(join(SOURCE_BORDERED_PATH, _)))


def converted(path):
    """
    Get PIL image converted to pre-set mode and size
    """
    im = Image.open(path)
    im = im.convert(CONVERT_MODE)

    w, h = im.size
    w, h = (int(IMAGE_SIZE * w / h), IMAGE_SIZE, ) if w > h\
        else (IMAGE_SIZE, int(IMAGE_SIZE * h / w), )
    im = im.resize((w, h))

    return im


def entropy(signal):
    """
    Calculate entropy for 1D array
    """
    signal = np.array(signal)
    propab = [np.size(signal[signal == i]) / (1.0 * signal.size)
              for i in list(set(signal))]
    return np.sum([p * np.log2(1.0 / p) for p in propab])


def scan(im):
    """
    Scan if image has borders at the top, right, bottom and left
    """
    w, h = im.size
    array = np.array(im)

    # Top
    center_ = 0
    diff_ = MEDIAN
    for center in reversed(range(1, h // 4 + 1)):
        upper = entropy(array[0: center, 0: w].flatten())
        lower = entropy(array[center: 2 * center, 0: w].flatten())
        diff = upper / lower if lower != 0.0 else MEDIAN
        if diff < diff_:
            center_ = center
            diff_ = diff
    top = diff_ < MEDIAN and center_ < h // 4, center_, diff_

    # Right
    center_ = 0
    diff_ = MEDIAN
    for center in reversed(range(1, w // 4 + 1)):
        upper = entropy(array[0: h, w - center: w].flatten())
        lower = entropy(array[0: h, w - 2 * center: w - center].flatten())
        diff = upper / lower if lower != 0.0 else MEDIAN
        if diff < diff_:
            center_ = center
            diff_ = diff
    right = diff_ < MEDIAN and center_ < w // 4, center_, diff_

    # Bottom
    center_ = 0
    diff_ = MEDIAN
    for center in reversed(range(1, h // 4 + 1)):
        upper = entropy(array[h - center: h, 0: w].flatten())
        lower = entropy(array[h - 2 * center: h - center, 0: w].flatten())
        diff = upper / lower if lower != 0.0 else MEDIAN
        if diff < diff_:
            center_ = center
            diff_ = diff
    bottom = diff_ < MEDIAN and center_ < h // 4, center_, diff_

    # Left
    center_ = 0
    diff_ = MEDIAN
    for center in reversed(range(1, w // 4 + 1)):
        upper = entropy(array[0: h, 0: center].flatten())
        lower = entropy(array[0: h, center: 2 * center].flatten())
        diff = upper / lower if lower != 0.0 else MEDIAN
        if diff < diff_:
            center_ = center
            diff_ = diff
    left = diff_ < MEDIAN and center_ < w // 4, center_, diff_

    # Return tuple of tuples each contains detection flag, border location
    # and maximum (actually minimum) difference between two entropies
    return top, right, bottom, left


def outline(im, top, right, bottom, left):
    """
    Draw cut-lines
    """
    w, h = im.size
    draw = ImageDraw.Draw(im)

    if top is not None:
        draw.line(((0, top - 1, ), (w - 1, top - 1, ), ), fill=0, width=3)
        draw.line(((0, top - 1, ), (w - 1, top - 1, ), ), fill=255, width=1)

    if right is not None:
        draw.line(((w - right - 1, 0, ), (w - right - 1, h - 1, ), ), fill=0, width=3)
        draw.line(((w - right - 1, 0, ), (w - right - 1, h - 1, ), ), fill=255, width=1)

    if bottom is not None:
        draw.line(((0, h - bottom - 1, ), (w - 1, h - bottom - 1, ), ), fill=0, width=3)
        draw.line(((0, h - bottom - 1, ), (w - 1, h - bottom - 1, ), ), fill=255, width=1)

    if left is not None:
        draw.line(((left - 1, 0, ), (left - 1, h - 1, ), ), fill=0, width=3)
        draw.line(((left - 1, 0, ), (left - 1, h - 1, ), ), fill=255, width=1)

    return


# Process bordered images
rate = 0
for index, name in enumerate(source_bordered_files):
    im = converted(join(SOURCE_BORDERED_PATH, name))
    res = scan(im)
    outline(im, *tuple(res[i][1] if res[i][0] else None for i in range(4)))
    im.save(join(DETECTED_BORDERED_PATH, name))
    im.close()

    print(index, name, res)

    rate += int(any(tuple(res[i][0] for i in range(4))))
print(rate / len(source_bordered_files))

# Process clear images
rate = 0
for index, name in enumerate(source_clear_files):
    im = converted(join(SOURCE_CLEAR_PATH, name))
    res = scan(im)
    outline(im, *tuple(res[i][1] if res[i][0] else None for i in range(4)))
    im.save(join(DETECTED_CLEAR_PATH, name))
    im.close()

    print(index, name, res)

    rate += int(any(tuple(res[i][0] for i in range(4))))
print(rate / len(source_clear_files))
