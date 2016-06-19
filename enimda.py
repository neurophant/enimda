import operator

from PIL import Image, ImageDraw
import numpy as np


__author__ = 'Anton Smolin'
__copyright__ = 'Copyright (C) 2016 Anton Smolin'
__license__ = 'MIT'
__version__ = '1.0.0b3'


class ENIMDA:
    __SIDE_COUNT = 4

    __image = None
    __threshold = None
    __indent = None

    __borders = None

    def __init__(self, *, path=None, mode='L', resize=None):
        """
        Preprocess image for further manipulations
        """
        self.__image = Image.open(path).convert(mode)

        if resize is not None:
            w, h = self.__image.size
            w, h = (int(resize * w / h), resize, ) if w > h\
                else (resize, int(resize * h / w), )
            self.__image = self.__image.resize((w, h))

        return

    def __entropy(self, *, signal=None):
        """
        Calculate entropy for 1D numpy array
        """
        signal = np.array(signal)
        propab = [np.size(signal[signal == i]) / (1.0 * signal.size)
                  for i in list(set(signal))]

        return np.sum([p * np.log2(1.0 / p) for p in propab])

    def scan(self, *, threshold=None, indent=None):
        """
        Scan if image has any borders
        """
        arr = np.array(self.__image)
        borders = []

        for side in range(self.__SIDE_COUNT):
            # Rotate array counter-clockwise to keep side of interest on top
            rot = np.rot90(arr, k=side)
            h, w = rot.shape    # Array size

            border = 0
            delta = threshold
            for center in reversed(range(1, int(indent * h) + 1)):
                upper = self.__entropy(signal=rot[0: center, 0: w].flatten())

                if upper == 0.0:
                    border = center
                    break

                lower = self.__entropy(
                    signal=rot[center: 2 * center, 0: w].flatten())
                diff = upper / lower if lower != 0.0 else delta

                if diff < delta and diff < threshold:
                    border = center
                    delta = diff

            borders.append(border)

        self.__borders = tuple(borders)

        return

    def detect(self, *, threshold=None, indent=None):
        """
        Precision border detection
        """
        image = self.__image
        w, h = image.size
        borders = (0, 0, 0, 0, )

        while True:
            self.scan(threshold=threshold, indent=indent)

            if not any(self.__borders):
                break

            borders = tuple(map(operator.add, borders, self.__borders))
            self.__crop()

        self.__image = image
        self.__borders = (
            borders[0] if borders[0] < int(indent * h) else 0,
            borders[1] if borders[1] < int(indent * w) else 0,
            borders[2] if borders[2] < int(indent * h) else 0,
            borders[3] if borders[3] < int(indent * w) else 0, )

        return

    @property
    def borders(self):
        return self.__borders

    @property
    def has_borders(self):
        return any(self.__borders)

    def __outline(self):
        """
        Draw cut-lines
        """
        w, h = self.__image.size
        draw = ImageDraw.Draw(self.__image)

        if self.__borders[0] > 0:
            draw.line(((0, self.__borders[0] + 1, ),
                       (w - 1, self.__borders[0] + 1, ), ), fill=0, width=3)
            draw.line(((0, self.__borders[0] + 1, ),
                       (w - 1, self.__borders[0] + 1, ), ), fill=255, width=1)

        if self.__borders[1] > 0:
            draw.line(((w - 2 - self.__borders[1], 0, ),
                       (w - 2 - self.__borders[1], h - 1, ), ),
                      fill=0, width=3)
            draw.line(((w - 2 - self.__borders[1], 0, ),
                       (w - 2 - self.__borders[1], h - 1, ), ),
                      fill=255, width=1)

        if self.__borders[2] > 0:
            draw.line(((0, h - 2 - self.__borders[2], ),
                       (w - 1, h - 2 - self.__borders[2], ), ),
                      fill=0, width=3)
            draw.line(((0, h - 2 - self.__borders[2], ),
                       (w - 1, h - 2 - self.__borders[2], ), ),
                      fill=255, width=1)

        if self.__borders[3] > 0:
            draw.line(((self.__borders[3] + 1, 0, ),
                       (self.__borders[3] + 1, h - 1, ), ), fill=0, width=3)
            draw.line(((self.__borders[3] + 1, 0, ),
                       (self.__borders[3] + 1, h - 1, ), ), fill=255, width=1)

        return

    def __crop(self):
        """
        Border offsets and cropped image
        If calculated offset is 0 - use original size
        """
        w, h = self.__image.size
        left = self.__borders[3]
        upper = self.__borders[0]
        right = w - 1 - self.__borders[1]
        lower = h - 1 - self.__borders[2]
        self.__image = self.__image.crop((left, upper, right, lower, ))

        return

    def save(self, *, path=None, outline=False, crop=False):
        if outline:
            self.__outline()
        if crop:
            self.__crop()

        self.__image.save(path)

        return
