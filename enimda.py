from os import listdir
from os.path import join, isfile
import operator

from PIL import Image, ImageDraw
import numpy as np


IMAGE_SIZE = 300    # Resize minimum side of image to this with aspect ratio
CONVERT_MODE = 'L'  # Grayscale (default)
SIDE_COUNT = 4

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


def scan(im, sides=None):
    """
    Scan if image has borders at the top, right, bottom and left
    """
    if sides is None:
        sides = tuple(s for s in range(SIDE_COUNT))

    arr = np.array(im)
    res = []

    for side in range(SIDE_COUNT):
        if side not in sides:
            res.append((False, 0, ))
        else:
            rot = np.rot90(arr, k=side)
            h, w = rot.shape

            med = 0
            delta = MEDIAN
            for center in reversed(range(1, h // 4 + 1)):
                upper = entropy(rot[0: center, 0: w].flatten())
                lower = entropy(rot[center: 2 * center, 0: w].flatten())
                diff = upper / lower if lower != 0.0 else MEDIAN
                if diff < delta:
                    med = center
                    delta = diff
            has = delta < MEDIAN and med < h // 4
            res.append((has, med, ))

    # Results
    has = any(tuple(res[s][0] for s in range(SIDE_COUNT)))

    left = res[3][1] - 1 if res[3][0] else 0
    upper = res[0][1] - 1 if res[0][0] else 0
    right = im.size[0] - res[1][1] - 1 if res[1][0] else im.size[0] - 1
    lower = im.size[1] - res[2][1] - 1 if res[2][0] else im.size[1] - 1
    im = im.crop((left, upper, right, lower, ))

    sides = tuple(s for s in range(SIDE_COUNT) if res[s][0])
    meds = tuple(res[s][1] if res[s][0] else 0 for s in range(SIDE_COUNT))

    return has, im, sides, meds


def detect(im):
    has = True
    sides = None
    meds = (0, 0, 0, 0, )
    while True:
        has, crop, sides, adds = scan(im, sides=sides)
        if not has:
            break
        im = crop
        meds = tuple(map(operator.add, meds, adds))

    return has, im, sides, meds


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
    has, crop, sides, meds = detect(im)
    outline(im, *meds)
    im.save(join(DETECTED_BORDERED_PATH, name))
    im.close()
    rate += int(has)
    print(index, name, has, meds)
print(rate / len(source_bordered_files))

# Process clear images
rate = 0
for index, name in enumerate(source_clear_files):
    im = converted(join(SOURCE_CLEAR_PATH, name))
    has, crop, sides, meds = detect(im)
    outline(im, *meds)
    im.save(join(DETECTED_CLEAR_PATH, name))
    im.close()
    rate += int(has)
    print(index, name, has, meds)
print(rate / len(source_clear_files))
