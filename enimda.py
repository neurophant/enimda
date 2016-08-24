from copy import deepcopy
from random import randint
from io import BytesIO

from PIL import Image, ImageDraw
from wand.image import Image as WandImage
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


def _ranges(*, count, paginate, limit=None):
    """
    Get page-like ranges for random generation
    """
    if limit is not None:
        total = count // paginate + int(bool(count % paginate))
        if total > limit:
            paginate = round(count / limit)
    ranges_ = []
    pages = count // paginate
    remainder = count % paginate
    for page in range(pages):
        ranges_.append((page * paginate, (page + 1) * paginate - 1))
    if remainder:
        ranges_.append((pages * paginate,
                        pages * paginate + remainder - 1))

    return tuple(ranges_)


def _wand_path(*, file_):
    if isinstance(file_, str):
        return {'filename': file_}
    else:
        return {'file': file_}


class ENIMDA:
    """
    ENIMDA class
    """
    __file = None
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
    def borders(self):
        """
        Get borders (tuple)
        """
        return tuple(
            round(self.__multiplier *
                  min(border[i] for border in self.__borders))
            for i in range(4))

    @property
    def has_borders(self):
        """
        Flag is true if image has any borders on any frame
        """
        return any(self.borders)

    def __init__(self, *, file_=None, minimize=None, frames=1.0,
                 max_frames=None):
        """
        Load image
        """
        self.__file = file_

        # Animation flag and frame count
        with Image.open(file_) as image:
            self.__animated = 'loop' in image.info
            if self.animated:
                self.__frames = 0
                try:
                    while True:
                        self.__frames += 1
                        image.seek(image.tell() + 1)
                except EOFError:
                    pass

        # Initial frames
        with Image.open(file_) as image:
            if self.animated:
                frames = round(1.0 / frames) if 0.0 < frames < 1.0 else None
                self.__initial = []

                if frames is not None:
                    # Limited frame count
                    ranges = tuple(
                        randint(*r)
                        for r in ranges_(count=self.frames, paginate=frames,
                                         limit=max_frames))
                    frame = 0
                    try:
                        while True:
                            if frame in ranges:
                                self.__initial.append(image.copy())
                            image.seek(image.tell() + 1)
                            frame += 1
                    except EOFError:
                        pass
                else:
                    # All frames
                    try:
                        while True:
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
                    height = round(minimize * image.height / image.width)
                    self.__multiplier = image.width / width
                elif image.width < image.height:
                    width = round(minimize * image.width / image.height)
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
        stripes = round(1.0 / stripes) if 0.0 < stripes < 1.0 else None

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

    def scan(self, *, threshold=0.5, indent=0.25, stripes=1.0, fast=True):
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

        for f in range(len(self.__converted)):
            borders.append(self.__scan_frame(
                frame=f, threshold=threshold, indent=indent,
                stripes=stripes, fast=fast))

        self.__borders = tuple(borders)

    def outline(self):
        """
        Outline image borders with dotted lines
        """
        if self.__initial[0].mode in ('1', 'L', 'I', 'F', 'P'):
            black = 0
            white = 255
        else:
            black = (0, 0, 0)
            white = (255, 255, 255)

        w, h = self.__initial[0].size

        self.__processed = self.__initial[0].copy()
        draw = ImageDraw.Draw(self.__processed)

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
        w, h = self.__initial[0].size
        left = self.borders[3]
        upper = self.borders[0]
        right = w - self.borders[1]
        lower = h - self.borders[2]

        if self.__animated:
            self.__processed = WandImage(**_wand_path(file_=self.__file))
            self.__processed.crop(left, upper, right, lower)
        else:
            self.__processed = self.__initial[0].copy()\
                .crop((left, upper, right, lower))

        return None

    def save(self, *, file_):
        """
        Save an image
        """
        if isinstance(self.__processed, Image.Image):
            self.__processed.save(file_)
        elif isinstance(self.__processed, WandImage):
            self.__processed.save(**_wand_path(file_=file_))

        return None
