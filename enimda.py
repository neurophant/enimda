from os import listdir
from os.path import join, isfile
import operator

from PIL import Image, ImageDraw
import numpy as np


IMAGE_SIZE = 300    # Resize min side of image to this one keeping aspect ratio
CONVERT_MODE = 'L'  # Grayscale mode (default)
SIDE_COUNT = 4      # Count of image sides

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
    Get PIL image converted to pre-set mode and size keeping its original
    aspect ratio
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
    Calculate entropy for 1D numpy array
    """
    signal = np.array(signal)
    propab = [np.size(signal[signal == i]) / (1.0 * signal.size)
              for i in list(set(signal))]

    return np.sum([p * np.log2(1.0 / p) for p in propab])


def scan(im):
    """
    Scan if image has borders at the top, right, bottom and left
    """
    arr = np.array(im)
    meds = []

    for side in range(SIDE_COUNT):
        # Rotate array counter-clockwise to keep side of interest on top
        rot = np.rot90(arr, k=side)
        h, w = rot.shape    # Array size

        med = 0
        delta = MEDIAN
        for center in reversed(range(1, h // 4 + 1)):
            upper = entropy(rot[0: center, 0: w].flatten())

            if upper == 0.0:
                med = center
                break

            lower = entropy(rot[center: 2 * center, 0: w].flatten())
            diff = upper / lower if lower != 0.0 else delta

            if diff < delta and diff < MEDIAN:
                med = center
                delta = diff

        meds.append(med)

    # Border offsets and cropped image
    # If calculated offset is 0 - use original size
    w, h = im.size
    left = meds[3]
    upper = meds[0]
    right = w - 1 - meds[1]
    lower = h - 1 - meds[2]
    im = im.crop((left, upper, right, lower, ))

    return meds, im


def detect(im, iterative=False):
    """
    Iterative border detection
    iterative=True - find border offsets with high precision (slow)
    iterative=False - detect if image has any borders (fast)
    """
    w, h = im.size
    meds = (0, 0, 0, 0, )

    while True:
        adds, crop = scan(im)

        if not any(adds):
            break

        im = crop
        meds = tuple(map(operator.add, meds, adds))

        if not iterative:
            break

    return (meds[0] if meds[0] < h // 4 else 0,
            meds[1] if meds[1] < w // 4 else 0,
            meds[2] if meds[2] < h // 4 else 0,
            meds[3] if meds[3] < w // 4 else 0), im


def outline(im, top, right, bottom, left):
    """
    Draw cut-lines
    """
    w, h = im.size
    draw = ImageDraw.Draw(im)

    if top > 0:
        draw.line(((0, top + 1, ), (w - 1, top + 1, ), ), fill=0, width=3)
        draw.line(((0, top + 1, ), (w - 1, top + 1, ), ), fill=255, width=1)

    if right > 0:
        draw.line(((w - 2 - right, 0, ), (w - 2 - right, h - 1, ), ), fill=0,
                  width=3)
        draw.line(((w - 2 - right, 0, ), (w - 2 - right, h - 1, ), ), fill=255,
                  width=1)

    if bottom > 0:
        draw.line(((0, h - 2 - bottom, ), (w - 1, h - 2 - bottom, ), ), fill=0,
                  width=3)
        draw.line(((0, h - 2 - bottom, ), (w - 1, h - 2 - bottom, ), ),
                  fill=255, width=1)

    if left > 0:
        draw.line(((left + 1, 0, ), (left + 1, h - 1, ), ), fill=0, width=3)
        draw.line(((left + 1, 0, ), (left + 1, h - 1, ), ), fill=255, width=1)

    return


# Process bordered images
rate = 0
for index, name in enumerate(source_bordered_files):
    im = converted(join(SOURCE_BORDERED_PATH, name))

    meds, _ = detect(im)
    outline(im, *meds)

    im.save(join(DETECTED_BORDERED_PATH, name))
    im.close()

    rate += int(any(meds))
    print(index, name, meds)

print(rate / len(source_bordered_files))

# Process clear images
rate = 0
for index, name in enumerate(source_clear_files):
    im = converted(join(SOURCE_CLEAR_PATH, name))

    meds, _ = detect(im)
    outline(im, *meds)

    im.save(join(DETECTED_CLEAR_PATH, name))
    im.close()

    rate += int(any(meds))
    print(index, name, meds)

print(rate / len(source_clear_files))
