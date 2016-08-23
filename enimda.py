from copy import deepcopy
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
    __path = None
    __animated = False
    __frames = None
    __initial = None
    __multiplier = 1.0
    __converted = None
    __borders = None

    def __init__(self, *, path=None, minimize=None):
        """
        Load image
        """
        image = Image.open(path)
        self.__animated = 'loop' in image.info
        if self.__animated:
            self.__frames = 0
            self.__initial = []
            try:
                while True:
                    self.__frames += 1
                    self.__initial.append(image.copy())
                    image.seek(image.tell() + 1)
            except EOFError:
                pass
        else:
            self.__initial = [image.copy()]

        if minimize is not None:
            image = self.__initial[0]
            if image.width > minimize or image.height > minimize:
                if image.width > image.height:
                    width = minimize
                    height = int(minimize * image.height / image.width)
                    self.__multiplier = image.height / height
                elif image.width < image.height:
                    width = int(minimize * image.width / image.height)
                    height = minimize
                    self.__multiplier = image.width / width
                else:
                    width = height = minimize
                    self.__multiplier = image.width / width

        self.__converted = []
        for frame in self.__initial:
            if minimize is not None:
                self.__converted.append(
                    frame.copy().resize((width, height)).convert('L'))
            else:
                self.__converted.append(frame.copy().convert('L'))

        return None

    def __frame(self, *, frame=0, threshold=0.5, indent=0.25, stripes=1.0,
                fast=True):
        """
        Find borders for frame
        """
        arr = np.array(self.__converted[frame])
        borders = []
        stripes = int(1.0 / stripes) if 0.0 < stripes < 1.0 else None

        # For every side of an image
        for side in range(4):
            # Rotate array counter-clockwise to keep side of interest on top
            rot = np.rot90(arr, k=side)
            h, w = rot.shape

            # Skip some columns
            if stripes is not None:
                arrs = []
                if w > stripes:
                    for i in range(0, w - stripes, stripes + 1):
                        r = randint(i, i + stripes)
                        arrs.append(rot[0: h, r: r + 1])
                else:
                    r = randint(0, w - 1)
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

        return tuple(borders)

    def scan(self, *, frames=1.0, threshold=0.5, indent=0.25, stripes=1.0,
             fast=True):
        """
        Find borders for all frames:
            - fast or precise: fast is only one iteration of possibly iterable
              full scan
            - use stripes to use only random <stripes> percent of columns to
              scan
        """
        borders = []
        frames = int(1.0 / frames) if 0.0 < frames < 1.0 else None

        # Skip some frames
        if frames is not None:
            arrs = []
            if self.__frames > frames:
                for i in range(0, self.__frames - frames, frames + 1):
                    r = randint(i, i + frames)
            else:
                r = randint(0, self.__frames - 1)
            rot = np.hstack(arrs)

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
