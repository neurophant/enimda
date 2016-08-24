import os

import pytest

from enimda import ENIMDA


@pytest.fixture
def fixed_bordered():
    def func(**kwargs):
        path = os.path.join(os.path.dirname(__file__), 'fixed/bordered.jpg')
        em = ENIMDA(file_=path, **kwargs)
        return em
    return func


@pytest.fixture
def fixed_clear():
    def func(**kwargs):
        path = os.path.join(os.path.dirname(__file__), 'fixed/clear.jpg')
        em = ENIMDA(file_=path, **kwargs)
        return em
    return func


@pytest.fixture
def anima_bordered():
    def func(**kwargs):
        path = os.path.join(os.path.dirname(__file__), 'anima/bordered.gif')
        em = ENIMDA(file_=path, **kwargs)
        return em
    return func


@pytest.fixture
def anima_clear():
    def func(**kwargs):
        path = os.path.join(os.path.dirname(__file__), 'anima/clear.gif')
        em = ENIMDA(file_=path, **kwargs)
        return em
    return func
