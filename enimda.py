import operator

from PIL import Image, ImageDraw
import numpy as np


__author__ = 'Anton Smolin'
__copyright__ = 'Copyright (C) 2016 Anton Smolin'
__license__ = 'MIT'
__version__ = '1.0.0b4'


class ENIMDA:
    __SIDE_COUNT = 4        # Top, right, bottom, left

    __image = None          # Pillow Image instance
    __miltiplier = None     # How image size changed during resize
    __borders = None        # Image borders tuple

    @property
    def image(self):
        """
        Pillow Image instance
        """
        return self.__image

    @property
    def multiplier(self):
        """
        Image multiplier
        """
        return self.__multiplier

    @property
    def has_borders(self):
        """
        Boolean flag which shows if image has any borders
        """
        return any(self.__borders)

    @property
    def borders(self):
        """
        Image borders tuple
        """
        return tuple(int(border * self.__multiplier)
                     for border in self.__borders)

    def __init__(self, *, image=None, file_=None, mode='L', resize=None):
        """
        Read image from file or buffer (file_)
        Or load already read Pillow Image instance (image)
        Preprocess it for further manipulations (mode, resize)
        """
        if image is not None:
            self.__image = image
        else:
            self.__image = Image.open(file_).convert(mode)

        if resize is None:
            self.__multiplier = 1.0
        else:
            w, h = self.__image.size
            w, h, self.__multiplier = \
                (int(resize * w / h), resize, h / resize) if w > h\
                else (resize, int(resize * h / w), w / resize)
            self.__image = self.__image.resize((w, h))

        return None

    def __entropy(self, *, signal=None):
        """
        Calculate entropy for 1D numpy array
        """
        signal = np.array(signal)
        propab = [np.size(signal[signal == i]) / (1.0 * signal.size)
                  for i in list(set(signal))]

        return np.sum([p * np.log2(1.0 / p) for p in propab])

    def __outline(self):
        """
        Draw cut-lines
        """
        w, h = self.__image.size
        draw = ImageDraw.Draw(self.__image)

        if self.__borders[0] > 0:
            draw.line(((0, self.__borders[0] + 1),
                       (w - 1, self.__borders[0] + 1)), fill=0, width=3)
            draw.line(((0, self.__borders[0] + 1),
                       (w - 1, self.__borders[0] + 1)), fill=255, width=1)

        if self.__borders[1] > 0:
            draw.line(((w - 2 - self.__borders[1], 0),
                       (w - 2 - self.__borders[1], h - 1)),
                      fill=0, width=3)
            draw.line(((w - 2 - self.__borders[1], 0),
                       (w - 2 - self.__borders[1], h - 1)),
                      fill=255, width=1)

        if self.__borders[2] > 0:
            draw.line(((0, h - 2 - self.__borders[2]),
                       (w - 1, h - 2 - self.__borders[2])),
                      fill=0, width=3)
            draw.line(((0, h - 2 - self.__borders[2]),
                       (w - 1, h - 2 - self.__borders[2])),
                      fill=255, width=1)

        if self.__borders[3] > 0:
            draw.line(((self.__borders[3] + 1, 0),
                       (self.__borders[3] + 1, h - 1)), fill=0, width=3)
            draw.line(((self.__borders[3] + 1, 0),
                       (self.__borders[3] + 1, h - 1)), fill=255, width=1)

        return None

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
        self.__image = self.__image.crop((left, upper, right, lower))

        return None

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

        return None

    def detect(self, *, threshold=None, indent=None):
        """
        Precision border detection
        """
        image = self.__image
        w, h = image.size
        borders = (0, 0, 0, 0)

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
            borders[3] if borders[3] < int(indent * w) else 0)

        return None

    def save(self, *, file_=None, outline=False, crop=False, **kwargs):
        """
        Save result image to file or buffer
        """
        if outline:
            self.__outline()
        if crop:
            self.__crop()

        self.__image.save(file_, **kwargs)

        return None
