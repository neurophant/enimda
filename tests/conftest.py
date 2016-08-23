import os

import pytest
from PIL import Image

from enimda import ENIMDA


@pytest.fixture
def fixed_bordered():
    def func(*, resize=None):
        path = os.path.join(os.path.dirname(__file__), 'fixed/bordered.jpg')
        em = ENIMDA(image=Image.open(path), resize=resize)
        return em
    return func


@pytest.fixture
def fixed_clear():
    def func(*, resize=None):
        path = os.path.join(os.path.dirname(__file__), 'fixed/clear.jpg')
        em = ENIMDA(image=Image.open(path), resize=resize)
        return em
    return func


@pytest.fixture
def anim_bordered():
    def func(*, minimize=None):
        path = os.path.join(os.path.dirname(__file__), 'anim/bordered.gif')
        em = ENIMDA(path=path, minimize=minimize)
        return em
    return func
