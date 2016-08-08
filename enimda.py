from PIL import Image, ImageDraw
import numpy as np


__author__ = 'Anton Smolin'
__copyright__ = 'Copyright (C) 2016 Anton Smolin'
__license__ = 'MIT'
__version__ = '1.0.0b4'


def entropy(*, signal=None):
    """
    Calculate entropy for 1D numpy array
    """
    signal = np.array(signal)
    propab = [np.size(signal[signal == i]) / (1.0 * signal.size)
              for i in list(set(signal))]

    return np.sum([p * np.log2(1.0 / p) for p in propab])


class ENIMDA:
    __borders = None

    @property
    def borders(self):
        return self.__borders

    def __init__(self, *, image=None, file_=None,
                 threshold=0.5, indent=0.25, fast=True):
        """
        Read image from file or buffer (file_)
        Or load already read Pillow Image instance (image)
        """
        if image is not None:
            im = image.copy().convert('L')
        else:
            im = Image.open(file_).convert('L')

        arr = np.array(im)
        borders = []

        for side in range(4):
            # Rotate array counter-clockwise to keep side of interest on top
            rot = np.rot90(arr, k=side)
            h, w = rot.shape    # Array size

            border = 0
            while True:
                # Find not-null starting point
                for start in range(border + 1, int(indent * h) + 1):
                    if entropy(signal=rot[border: start, 0: w].flatten()) > 0.0:
                        break

                # Find sub-border
                subborder = 0
                delta = threshold
                for center in reversed(range(start, int(indent * h) + 1)):
                    upper = entropy(signal=rot[border: center, 0: w].flatten())
                    lower = entropy(signal=rot[center: 2 * center, 0: w].flatten())
                    diff = upper / lower if lower != 0.0 else delta

                    if diff < delta and diff < threshold:
                        subborder = center
                        delta = diff

                if subborder == 0:
                    break

                border = subborder

                if fast:
                    break

            borders.append(border)

        self.__borders = tuple(borders)

        return None
