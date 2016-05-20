from os import listdir
from os.path import join, isfile

from PIL import Image, ImageDraw
import numpy as np


IMAGE_SIZE = 500    # Resize minimum side of image to this with aspect ratio
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
    propab = [np.size(signal[signal == i]) / (1.0 * len(signal))
              for i in list(set(signal))]
    return np.sum([p * np.log2(1.0 / p) for p in propab])


def scan(im):
    """
    Scan if image has borders at the top, right, bottom and left
    """
    w = im.size[0]
    h = im.size[1]

    # Top
    center_ = None
    diff_ = None
    for center in reversed(range(1, h // 4 + 1)):
        upper = tuple(im.getpixel((x, y))
                      for x in range(w)
                      for y in range(center))
        lower = tuple(im.getpixel((x, y))
                      for x in range(w)
                      for y in range(center, 2 * center))
        diff = entropy(upper) / entropy(lower)
        if center_ is None or diff_ is None:
            center_ = center
            diff_ = diff
        if diff < diff_:
            center_ = center
            diff_ = diff
    top = diff_ < MEDIAN and center_ < h // 4, center_, diff_

    # Right
    center_ = None
    diff_ = None
    for center in reversed(range(1, w // 4 + 1)):
        upper = tuple(im.getpixel((x, y))
                      for x in range(w - center, w)
                      for y in range(h))
        lower = tuple(im.getpixel((x, y))
                      for x in range(w - 2 * center, w - center)
                      for y in range(h))
        diff = entropy(upper) / entropy(lower)
        if center_ is None or diff_ is None:
            center_ = center
            diff_ = diff
        if diff < diff_:
            center_ = center
            diff_ = diff
    right = diff_ < MEDIAN and center_ < w // 4, center_, diff_

    # Bottom
    center_ = None
    diff_ = None
    for center in reversed(range(1, h // 4 + 1)):
        upper = tuple(im.getpixel((x, y))
                      for x in range(w)
                      for y in range(h - center, h))
        lower = tuple(im.getpixel((x, y))
                      for x in range(w)
                      for y in range(h - 2 * center, h - center))
        diff = entropy(upper) / entropy(lower)
        if center_ is None or diff_ is None:
            center_ = center
            diff_ = diff
        if diff < diff_:
            center_ = center
            diff_ = diff
    bottom = diff_ < MEDIAN and center_ < h // 4, center_, diff_

    # Left
    center_ = None
    diff_ = None
    for center in reversed(range(1, w // 4 + 1)):
        upper = tuple(im.getpixel((x, y))
                      for x in range(center)
                      for y in range(h))
        lower = tuple(im.getpixel((x, y))
                      for x in range(center, 2 * center)
                      for y in range(h))
        diff = entropy(upper) / entropy(lower)
        if center_ is None or diff_ is None:
            center_ = center
            diff_ = diff
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
    w = im.size[0]
    h = im.size[1]

    draw = ImageDraw.Draw(im)

    if top is not None:
        draw.line(((0, top, ), (w, top, ), ), fill=0, width=3)
        draw.line(((0, top, ), (w, top, ), ), fill=255, width=1)

    if right is not None:
        draw.line(((w - right, 0, ), (w - right, h, ), ), fill=0, width=3)
        draw.line(((w - right, 0, ), (w - right, h, ), ), fill=255, width=1)

    if bottom is not None:
        draw.line(((0, h - bottom, ), (w, h - bottom, ), ), fill=0, width=3)
        draw.line(((0, h - bottom, ), (w, h - bottom, ), ), fill=255, width=1)

    if left is not None:
        draw.line(((left, 0, ), (left, h, ), ), fill=0, width=3)
        draw.line(((left, 0, ), (left, h, ), ), fill=255, width=1)

    return


# Process bordered images
for index, name in enumerate(source_bordered_files):
    im = converted(join(SOURCE_BORDERED_PATH, name))
    res = scan(im)
    outline(
        im,
        res[0][1] if res[0][0] else None,
        res[1][1] if res[1][0] else None,
        res[2][1] if res[2][0] else None,
        res[3][1] if res[3][0] else None)
    im.save(join(DETECTED_BORDERED_PATH, name))
    im.close()

    print(index, name, res)

# Process clear images
for index, name in enumerate(source_clear_files):
    im = converted(join(SOURCE_CLEAR_PATH, name))
    res = scan(im)
    outline(
        im,
        res[0][1] if res[0][0] else None,
        res[1][1] if res[1][0] else None,
        res[2][1] if res[2][0] else None,
        res[3][1] if res[3][0] else None)
    im.save(join(DETECTED_CLEAR_PATH, name))
    im.close()

    print(index, name, res)
