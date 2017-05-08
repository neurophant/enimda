from random import randint, shuffle
from math import log2
from collections import Counter

from PIL import Image, ImageSequence


__author__ = 'Anton Smolin'
__copyright__ = 'Copyright (C) 2016-2017 Anton Smolin'
__license__ = 'MIT'
__version__ = '2.0.0'


def __entropy(*, signal):
    """Calculate entropy

    :param signal: 2D signal
    :returns: entropy"""

    signal = tuple(value for line in signal for value in line)
    counts = dict(Counter(signal))
    probs = (counts[value] / len(signal) for value in set(signal))

    return sum(prob * log2(1.0 / prob) for prob in probs)


def __randoms(*, count, limit=None):
    """Get random indexes

    :param count: items count
    :param limit: limits items count if exceeds this (default None)
    :returns: set of indexes"""

    randoms = list(range(count))

    if limit is None:
        return set(randoms)

    shuffle(randoms)

    return set(randoms[:limit])


class ENIMDA:
    """ENIMDA class"""

    __multiplier = 1.0
    __frames = []

    def __init__(self, *, fp, size=None, frames=None, rows=0.25, columns=None):
        """Load image

        :param fp: path to file or file object
        :param size: image will be resized to this size if exceeds it
                     (default None)
        :param frames: max frames for GIFs (default None)
        :returns: None"""

        with Image.open(fp) as image:
            frame_count = 0
            while True:
                frame_count += 1
                try:
                    image.seek(frame_count)
                except EOFError:
                    break
            frame_set = __randoms(count=frame_count, limit=frames)

        with Image.open(fp) as image:
            for frame_index in range(frame_count):
                try:
                    image.seek(frame_index)
                except EOFError:
                    break

                if frame_index not in frame_set:
                    continue

                frame = image.copy()
                if size is not None and \
                        (size < image.width or size < image.height):
                    frame.thumbnail(size)
                    self.__multiplier = max((image.width / frame.width,
                                             image.height / frame.height))
                frame = frame.convert('L')

                sides = []
                for side_index in range(4):
                    side = frame.copy()
                    if side_index:
                        side = side.rotate(side_index * 90)

                    row_count = 2 * int(rows * side.height)
                    column_set = __randoms(count=side.width, limit=columns)
                    side = side.crop((0, 0, side.width, row_count))
                    data = list(side.getdata())

                    lines = [[data[row_index * side.width + column_index]
                              for column_index in range(side.width)
                              if column_index in column_set]
                             for row_index in range(row_count)]
                    sides.append({'width': side.width,
                                  'height': side.height,
                                  'lines': lines})

                self.__frames.append(sides)

    def __scan(self, *, frame, threshold=0.5, fast=True):
        """Find borders for frame

        :param frame: frame
        :param threshold: algorithm agressiveness (default 0.5)
        :param fast: only one iteration will be used (default True)
        :returns: tuple of border offsets"""

        borders = []

        for side in frame:
            border = 0

            while True:
                subborder = 0
                delta = threshold
                for center in \
                        reversed(range(border + 1, side['height'] / 2 + 1)):
                    upper = _entropy(signal=side['lines'][border:center])
                    lower = _entropy(signal=side['lines'][center:2 * center - border])
                    diff = upper / lower if lower != 0.0 else delta

                    if diff < delta and diff < threshold:
                        subborder = center
                        delta = diff

                if subborder == 0 or border == subborder:
                    break

                border = subborder

                if fast:
                    break

            borders.append(border)

        return tuple(borders)

    def scan(self, *, threshold=0.5, fast=True):
        """Find borders for all frames

        :param threshold: algorithm agressiveness (default 0.5)
        :param fast: only one iteration will be used (default True)
        :returns: tuple of border offsets"""

        borders = [self.__scan(frame=frame, threshold=threshold, fast=fast)
                   for frame in self.__frames]

        return tuple(min(border[side] for border in borders)
                     for side in range(4))
