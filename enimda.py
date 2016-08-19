from random import randint

from PIL import Image, ImageDraw
import numpy as np


__author__ = 'Anton Smolin'
__copyright__ = 'Copyright (C) 2016 Anton Smolin'
__license__ = 'MIT'
__version__ = '1.1.0'


def _entropy(*, signal=None):
    """
    Calculate entropy for 1D numpy array
    """
    propab = [np.size(signal[signal == i]) / (1.0 * signal.size)
              for i in list(set(signal))]

    return np.sum([p * np.log2(1.0 / p) for p in propab])


class ENIMDA:
    __initial = None
    __converted = None
    __borders = None

    def __init__(self, *, image=None):
        """
        Load Pillow Image instance
        """
        self.__initial = image.copy()
        self.__converted = image.copy().convert('L')

        return None

    def scan(self, *, threshold=0.5, indent=0.25, rand=1.0, fast=True):
        """
        Find borders:
            - fast or precise: fast is only one iteration of possibly iterable
              full scan
            - use rand to use only random <rand> percent of columns to scan
        """
        arr = np.array(self.__converted)
        borders = []
        rand = int(1.0 / rand) if 0.0 < rand < 1.0 else None

        # For every side of an image
        for side in range(4):
            # Rotate array counter-clockwise to keep side of interest on top
            rot = np.rot90(arr, k=side)
            h, w = rot.shape

            # Skip some columns
            if rand is not None:
                arrs = []
                for i in range(0, w - rand, rand + 1):
                    r = randint(i, i + rand)
                    arrs.append(rot[0: h, r: r + 1])
                rot = np.hstack(arrs)
                h, w = rot.shape

            # Iterative detection
            border = 0
            while True:
                # Find not-null starting point
                for start in range(border + 1, int(indent * h) + 1):
                    if _entropy(
                            signal=rot[border: start, 0: w].flatten()) > 0.0:
                        break

                # Find sub-border
                subborder = 0
                delta = threshold
                for center in reversed(range(start, int(indent * h) + 1)):
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

        self.__borders = tuple(borders)

        return None

    def outline(self):
        """
        Outline image borders with dotted lines
        """
        if self.__initial.mode in ('1', 'L', 'I', 'F'):
            black = 0
            white = 255
        else:
            black = (0, 0, 0)
            white = (255, 255, 255)

        w, h = self.__initial.size
        draw = ImageDraw.Draw(self.__initial)

        if self.__borders[0] > 0:
            for i in range(0, w):
                fill = white if i % 2 == 0 else black
                draw.point((i, self.__borders[0]), fill=fill)

        if self.__borders[1] > 0:
            for i in range(0, h):
                fill = white if i % 2 == 0 else black
                draw.point((w - 1 - self.__borders[1], i), fill=fill)

        if self.__borders[2] > 0:
            for i in range(0, w):
                fill = white if i % 2 == 0 else black
                draw.point((i, h - 1 - self.__borders[2]), fill=fill)

        if self.__borders[3] > 0:
            for i in range(0, h):
                fill = white if i % 2 == 0 else black
                draw.point((self.__borders[3], i), fill=fill)

        return None

    def crop(self):
        """
        Crop an image - cut all borders/whitespace
        """
        w, h = self.__initial.size
        left = self.__borders[3]
        upper = self.__borders[0]
        right = w - self.__borders[1]
        lower = h - self.__borders[2]
        self.__initial = self.__initial.crop((left, upper, right, lower))

        return None

    @property
    def has_borders(self):
        """
        Flag is true if image has any borders
        """
        return any(self.__borders)

    @property
    def borders(self):
        """
        Get borders (tuple)
        """
        return self.__borders

    @property
    def image(self):
        """
        Get initial outlined or cropped image
        """
        return self.__initial
