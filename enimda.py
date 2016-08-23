from copy import deepcopy
from random import randint

from PIL import Image, ImageDraw
import numpy as np


__author__ = 'Anton Smolin'
__copyright__ = 'Copyright (C) 2016 Anton Smolin'
__license__ = 'MIT'
__version__ = '1.1.1'


def _entropy(*, signal):
    """
    Calculate entropy for 1D numpy array
    """
    propab = [np.size(signal[signal == i]) / (1.0 * signal.size)
              for i in list(set(signal))]

    return np.sum([p * np.log2(1.0 / p) for p in propab])


def _ranges(*, count, paginate):
    """
    Get page-like ranges for random generation
    """
    ranges_ = []
    pages = count // paginate
    remainder = count % paginate
    for page in range(pages):
        ranges_.append((page * paginate, (page + 1) * paginate - 1))
    if remainder:
        ranges_.append((pages * paginate,
                        pages * paginate + remainder - 1))

    return tuple(ranges_)


class ENIMDA:
    """
    ENIMDA class
    """
    __path = None
    __animated = False
    __frames = None
    __initial = None
    __multiplier = 1.0
    __converted = None
    __borders = None
    __processed = None

    @property
    def animated(self):
        """
        Animated flag
        """
        return self.__animated

    @property
    def frames(self):
        """
        Frame count
        """
        return self.__frames

    @property
    def multiplier(self):
        """
        Multiplier property
        """
        return self.__multiplier

    @property
    def borders(self):
        """
        Get borders (tuple)
        """
        return tuple(
            round(self.multiplier *
                  min(border[i] for border in self.__borders))
            for i in range(4))

    @property
    def has_borders(self):
        """
        Flag is true if image has any borders on any frame
        """
        return any(self.borders)

    def __init__(self, *, file_=None, minimize=None):
        """
        Load image
        """
        image = Image.open(file_)
        self.__animated = 'loop' in image.info

        # Initial frames
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

        # If minimization required - recalculate multiplier and new size
        if minimize is not None:
            image = self.__initial[0]
            if image.width > minimize or image.height > minimize:
                if image.width > image.height:
                    width = minimize
                    height = int(minimize * image.height / image.width)
                    self.__multiplier = image.width / width
                elif image.width < image.height:
                    width = int(minimize * image.width / image.height)
                    height = minimize
                    self.__multiplier = image.height / height
                else:
                    width = height = minimize
                    self.__multiplier = image.width / width
            else:
                width, height = image.width, image.height

        # Converted frames
        self.__converted = []
        for frame in self.__initial:
            if minimize is not None:
                self.__converted.append(
                    frame.copy().resize((width, height)).convert('L'))
            else:
                self.__converted.append(frame.copy().convert('L'))

        return None

    def __scan_frame(self, *, frame=0, threshold=0.5, indent=0.25, stripes=1.0,
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
                for i in _ranges(count=w, paginate=stripes):
                    r = randint(*i)
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
            - frames is used for animated images - logics is the same as
              stripes
            - fast or precise: fast is only one iteration of possibly iterable
              full scan
            - use stripes to use only random <stripes> percent of columns to
              scan
        """
        borders = []
        frames = int(1.0 / frames) if 0.0 < frames < 1.0 else None

        if self.animated:
            if frames is not None:
                for i in _ranges(count=self.frames, paginate=frames):
                    r = randint(*i)
                    borders.append(self.__scan_frame(
                        frame=r, threshold=threshold, indent=indent,
                        stripes=stripes, fast=fast))
            else:
                for r in range(self.frames):
                    borders.append(self.__scan_frame(
                        frame=r, threshold=threshold, indent=indent,
                        stripes=stripes, fast=fast))
        else:
            borders.append(self.__scan_frame(
                threshold=threshold, indent=indent, stripes=stripes,
                fast=fast))

        self.__borders = tuple(borders)

    def outline(self):
        """
        Outline image borders with dotted lines
        """
        self.__processed = deepcopy(self.__initial)

        if self.__processed[0].mode in ('1', 'L', 'I', 'F'):
            black = 0
            white = 255
        else:
            black = (0, 0, 0)
            white = (255, 255, 255)

        w, h = self.__processed[0].size

        for frame in self.__processed:
            draw = ImageDraw.Draw(frame)

            if self.borders[0] > 0:
                for i in range(0, w):
                    fill = white if i % 2 == 0 else black
                    draw.point((i, self.borders[0]), fill=fill)

            if self.borders[1] > 0:
                for i in range(0, h):
                    fill = white if i % 2 == 0 else black
                    draw.point((w - 1 - self.borders[1], i), fill=fill)

            if self.borders[2] > 0:
                for i in range(0, w):
                    fill = white if i % 2 == 0 else black
                    draw.point((i, h - 1 - self.borders[2]), fill=fill)

            if self.borders[3] > 0:
                for i in range(0, h):
                    fill = white if i % 2 == 0 else black
                    draw.point((self.borders[3], i), fill=fill)

        return None

    def crop(self):
        """
        Crop an image - cut all borders/whitespace
        """
        self.__processed = deepcopy(self.__initial)

        w, h = self.__processed[0].size
        left = self.borders[3]
        upper = self.borders[0]
        right = w - self.borders[1]
        lower = h - self.borders[2]

        for index, frame in enumerate(self.__processed):
            self.__processed[index] = frame.crop((left, upper, right, lower))

        return None

    def save(self, *, file_):
        """
        Save an image
        """
        if self.animated:
            pass
        else:
            self.__processed[0].save(file_)

        return None
