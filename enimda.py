from random import randint, shuffle
from math import ceil

from PIL import Image, ImageDraw
import numpy as np
from images2gif import writeGif


__author__ = 'Anton Smolin'
__copyright__ = 'Copyright (C) 2016 Anton Smolin'
__license__ = 'MIT'
__version__ = '1.1.3'


def _entropy(*, signal):
    """
    Calculate entropy for 1D numpy array

    Keyword arguments:
    signal -- 1D numpy array
    """
    propab = [np.size(signal[signal == i]) / (1.0 * signal.size)
              for i in list(set(signal))]

    return np.sum([p * np.log2(1.0 / p) for p in propab])


def _randoms(*, count, paginate, limit=None):
    """
    Get paginated random indexes

    Keyword arguments:
    count -- items count
    paginate -- items per page
    limit -- limits page count if exceeds this (default None)
    """
    randoms_ = []
    pages = count // paginate
    remainder = count % paginate
    _ololo = []
    for page in range(pages):
        randoms_.append(randint(page * paginate, (page + 1) * paginate - 1))
    if remainder:
        randoms_.append(randint(pages * paginate,
                                pages * paginate + remainder - 1))
    if limit is not None:
        shuffle(randoms_)
        randoms_ = randoms_[:limit]

    return tuple(randoms_)


class ENIMDA:
    """
    ENIMDA class
    """
    __duration = None
    __loop = None
    __initial = None
    __multiplier = 1.0
    __converted = None
    __borders = None
    __processed = None

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

    def __init__(self, *,
                 file_,
                 minimize=None,
                 frames=1.0,
                 max_frames=None):
        """
        Load image

        Keyword arguments:
        file_ -- path to file or StringIO/BytesIO
        minimize -- image will be resized to this size (default None)
        frames -- random frames usage percentage (GIFs) (default 1.0)
        max_frames -- max frames for GIFs (default None)
        """

        # Animation properties
        with Image.open(file_) as image:
            total = 0
            if 'loop' in image.info:
                self.__duration = image.info.get('duration', 100) / 1000
                self.__loop = image.info.get('loop', 0)
                try:
                    while True:
                        total += 1
                        image.seek(total)
                except EOFError:
                    pass
            else:
                total += 1

        # Frame limitations for initial and converted
        ri = _randoms(count=total, paginate=1, limit=max_frames)
        paginate = round(1.0 / frames) if 0.0 < frames < 1.0 else 1
        rc = _randoms(count=total, paginate=paginate, limit=max_frames)

        with Image.open(file_) as image:
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
            try:
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
                    image.seek(image.tell() + 1)
                    current += 1
            except EOFError:
                pass

        return None

    def __scan_frame(self, *,
                     frame=0,
                     threshold=0.5,
                     indent=0.25,
                     stripes=1.0,
                     max_stripes=None,
                     fast=True):
        """
        Find borders for frame

        Keyword arguments:
        frame -- frame index (default 0)
        threshold -- algorithm agressiveness (default 0.5)
        indent -- starting point in percent of width/height (default 0.25)
        stripes -- random stripes usage coefficient (default 1.0)
        max_stripes -- max stripes for processing (default None)
        fast -- True - only one iteration will be used (default True)
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
            for r in _randoms(
                    count=w,
                    paginate=paginate,
                    limit=max_stripes):
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

    def scan(self, *,
             threshold=0.5,
             indent=0.25,
             stripes=1.0,
             max_stripes=None,
             fast=True):
        """
        Find borders for all frames

        Keyword arguments:
        threshold -- algorithm agressiveness (default 0.5)
        indent -- starting point in percent of width/height (default 0.25)
        stripes -- random stripes usage coefficient (default 1.0)
        max_stripes -- max stripes for processing (default None)
        fast -- True - only one iteration will be used (default True)
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

        self.__processed = []
        for frame in self.__initial:
            processed = frame.copy()
            draw = ImageDraw.Draw(processed)

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

            self.__processed.append(processed)

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

        self.__processed = []
        for frame in self.__initial:
            self.__processed.append(
                frame
                .copy()
                .crop((left, upper, right, lower)))

        return None

    def save(self, *, file_):
        """
        Save an image

        Keyword arguments:
        file_ -- path to file ot StringIO/BytesIO
        """
        if len(self.__processed) == 1:
            self.__processed[0].save(file_)
        else:
            writeGif(file_, self.__processed, duration=self.__duration,
                     repeat=self.__loop)

        return None
