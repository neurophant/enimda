import os

import pytest

from enimda import ENIMDA


@pytest.fixture
def current():
    def func(sub):
        return os.path.join(os.path.dirname(__file__), sub)
    return func


@pytest.fixture
def image(current):
    def func(path, **kwargs):
        return ENIMDA(fp=current(path), **kwargs)
    return func


@pytest.fixture
def fixed_bordered(image):
    def func(**kwargs):
        return image('fixed/bordered.jpg', **kwargs)
    return func


@pytest.fixture
def fixed_clear(image):
    def func(**kwargs):
        return image('fixed/clear.jpg')
    return func


@pytest.fixture
def anima_bordered(image):
    def func(**kwargs):
        return image('anima/bordered.gif')
    return func


@pytest.fixture
def anima_clear(image):
    def func(**kwargs):
        return image('anima/clear.gif')
    return func
