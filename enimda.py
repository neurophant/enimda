from random import randint, shuffle
from math import ceil

from PIL import Image, ImageDraw
import numpy as np
from images2gif import GifWriter


__author__ = 'Anton Smolin'
__copyright__ = 'Copyright (C) 2016 Anton Smolin'
__license__ = 'MIT'
__version__ = '1.1.6'


def _entropy(*, signal):
    """Calculate entropy

    :param signal: 1D numpy array
    :returns: entropy
    """
    prob = (np.size(signal[signal == i]) / signal.size for i in set(signal))

    return np.sum(p * np.log2(1.0 / p) for p in prob)


def _randoms(*, count, paginate, limit=None):
    """Get paginated random indexes

    :param count: items count
    :param paginate: items per page
    :param limit: limits page count if exceeds this (default None)
    :returns: tuple of indexes
    """
    randoms = []

    pages = count // paginate
    for page in range(pages):
        randoms.append(randint(page * paginate, (page + 1) * paginate - 1))
    remainder = count % paginate
    if remainder:
        randoms.append(randint(pages * paginate,
                               pages * paginate + remainder - 1))

    if limit is not None:
        shuffle(randoms)
        randoms = randoms[:limit]

    return tuple(randoms)


class ENIMDA:
    """ENIMDA class"""
    __format = None
    __duration = None
    __loop = None
    __initial = None
    __multiplier = 1.0
    __converted = None
    __borders = None
    __processed = None

    @property
    def borders(self):
        """Borders"""
        return tuple(
            round(self.__multiplier * min(b[i] for b in self.__borders))
            for i in range(4))

    @property
    def has_borders(self):
        """Image has any borders on any frame"""
        return any(self.borders)

    def __init__(self, *, fp, minimize=None, frames=1.0, max_frames=None):
        """Load image

        :param fp: path to file or file object
        :param minimize: image will be resized to this size (default None)
        :param frames: random frames usage percentage (GIFs) (default 1.0)
        :param max_frames: max frames for GIFs (default None)
        :returns: None
        """

        # Common properties
        with Image.open(fp) as image:
            self.__format = image.format
            self.__duration = image.info.get('duration', 100) / 1000
            try:
                self.__loop = int(image.info.get('loop', 0))
            except TypeError:
                self.__loop = 0
            total = 0
            while True:
                total += 1
                try:
                    image.seek(total)
                except EOFError:
                    break

        # Frame limitations for initial and converted
        ri = _randoms(count=total, paginate=1, limit=max_frames)
        paginate = round(1.0 / frames) if 0.0 < frames < 1.0 else 1
        rc = _randoms(count=total, paginate=paginate, limit=max_frames)

        with Image.open(fp) as image:
            # Calculate minified size and multiplier
            if minimize is not None:
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
                    minimize = None

            # Initial and converted frames
            self.__initial = []
            self.__converted = []
            current = 0
            while True:
                if current in ri:
                    self.__initial.append(image.copy())
                if current in rc:
                    if minimize is not None:
                        self.__converted.append(
                            image
                            .copy()
                            .resize((width, height))
                            .convert('L'))
                    else:
                        self.__converted.append(
                            image
                            .copy()
                            .convert('L'))
                try:
                    image.seek(current + 1)
                except EOFError:
                    break
                current += 1

        return None

    def __scan_frame(self, *, frame=0, threshold=0.5, indent=0.25, stripes=1.0,
                     max_stripes=None, fast=True):
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

    def scan(self, *, threshold=0.5, indent=0.25, stripes=1.0,
             max_stripes=None, fast=True):
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

    def outline(self):
        """Outline image borders with dotted lines"""
        if self.__initial[0].mode in ('1', 'L', 'I', 'F', 'P'):
            black = 0
            white = 255
        else:
            black = (0, 0, 0)
            white = (255, 255, 255)

        w, h = self.__initial[0].size

        self.__processed = []
        for frame in self.__initial:
            processed = frame.copy()
            draw = ImageDraw.Draw(processed)

            for side in range(4):
                if self.borders[side] > 0:
                    for i in range(0, h if side % 2 else w):
                        fill = white if i % 2 == 0 else black
                        if side == 0:
                            coords = (i, self.borders[side])
                        elif side == 1:
                            coords = (w - 1 - self.borders[side], i)
                        elif side == 2:
                            coords = (i, h - 1 - self.borders[side])
                        elif side == 3:
                            coords = (self.borders[side], i)
                        draw.point(coords, fill=fill)

            self.__processed.append(processed)

        return None

    def crop(self):
        """Crop an image - cut borders/whitespace"""
        w, h = self.__initial[0].size
        left = self.borders[3]
        upper = self.borders[0]
        right = w - self.borders[1]
        lower = h - self.borders[2]

        self.__processed = []
        for frame in self.__initial:
            self.__processed.append(
                frame
                .copy()
                .crop((left, upper, right, lower)))

        return None

    def save(self, *, fp):
        """Save an image

        :param fp: path to file or file object
        :returns: None
        """
        if len(self.__processed) == 1:
            self.__processed[0].save(fp, format=self.__format)
        else:
            gifWriter = GifWriter()
            gifWriter.transparency = False
            args = (
                self.__processed,
                [self.__duration] * len(self.__processed),
                self.__loop,
                [(0, 0)] * len(self.__processed),
                [1] * len(self.__processed))
            if isinstance(fp, str):
                with open(fp, 'wb') as fp:
                    gifWriter.writeGifToFile(fp, *args)
            else:
                gifWriter.writeGifToFile(fp, *args)

        return None
