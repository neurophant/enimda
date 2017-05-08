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

    :param signal: 1D signal tuple
    :returns: entropy"""

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
                row_count = round(rows * frame.height)
                column_set = __randoms(count=frame.width, limit=columns)
                frame = frame.crop((0, 0, frame.width, row_count)).convert('L')
                data = list(frame.getdata())

                frame_ = []
                for row_index in range(row_count):
                    row_ = []
                    for column_index in range(frame.width):
                        if column_index not in column_set:
                            continue

                        row_.append(
                            data[row_index * frame.width + column_index])
                    frame_.append(row_)
                self.__frames.append(frame_)

    def __scan_frame(self, *, frame=0, threshold=0.5, fast=True):
        """Find borders for frame

        :param frame: frame index (default 0)
        :param threshold: algorithm agressiveness (default 0.5)
        :param indent: starting point in percent of width/height (default 0.25)
        :param stripes: random stripes usage coefficient (default 1.0)
        :param max_stripes: max stripes for processing (default None)
        :param fast: only one iteration will be used (default True)
        :returns: tuple of border offsets
        """
        arr = np.array(self.__converted[frame])
        borders = []
        paginate = round(1.0 / stripes) if 0.0 < stripes < 1.0 else 1

        # For every side of an image
        for side in range(4):
            # Rotate array counter-clockwise to keep side of interest on top
            rot = np.rot90(arr, k=side)
            h, w = rot.shape

            # Skip some columns
            arrs = []
            for r in _randoms(count=w, paginate=paginate, limit=max_stripes):
                arrs.append(rot[0: h, r: r + 1])
            rot = np.hstack(arrs)
            h, w = rot.shape

            # Iterative detection
            border = 0
            while True:
                # Find not-null starting point
                for start in range(border + 1, round(indent * h) + 1):
                    if _entropy(
                            signal=rot[border: start, 0: w].flatten()) > 0.0:
                        break

                # Find sub-border
                subborder = 0
                delta = threshold
                for center in reversed(range(start, round(indent * h) + 1)):
                    upper = _entropy(
                        signal=rot[border: center, 0: w].flatten())
                    lower = _entropy(
                        signal=rot[center: 2 * center - border, 0: w]
                        .flatten())
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
        :param indent: starting point in percent of width/height (default 0.25)
        :param stripes: random stripes usage coefficient (default 1.0)
        :param max_stripes: max stripes for processing (default None)
        :param fast: only one iteration will be used (default True)
        :returns: None
        """
        borders = []

        for f in range(len(self.__converted)):
            borders.append(self.__scan_frame(
                frame=f,
                threshold=threshold,
                indent=indent,
                stripes=stripes,
                max_stripes=max_stripes,
                fast=fast))

        self.__borders = tuple(borders)

        return None
