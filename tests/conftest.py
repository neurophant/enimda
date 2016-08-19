from os import path

import pytest
from PIL import Image

from enimda import ENIMDA


@pytest.fixture
def image():
    def func(path_, *, resize=None):
        im = Image.open(path_)
        if resize is not None:
            w, h = im.size
            w, h = (int(resize * w / h), resize) if w > h \
                else (resize, int(resize * h / w))
            im = im.resize((w, h))
        return im
    return func


@pytest.fixture
def bordered(image):
    def func(*, resize=None):
        em = ENIMDA(
            image=image(path.join(path.dirname(__file__), 'bordered.jpg'),
                        resize=resize))
        return em
    return func


@pytest.fixture
def clear(image):
    def func(*, resize=None):
        em = ENIMDA(
            image=image(path.join(path.dirname(__file__), 'clear.jpg'),
                        resize=resize))
        return em
    return func
