import pytest


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('size', (None, 200))
def test_fixed_bordered_partial(fixed_bordered, fast, size):
    em = fixed_bordered(size=size)
    assert any(em.scan(columns=20, fast=fast))


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('size', ({
    'size': None,
    'borders': (4, 4, 4, 4)
}, {
    'size': 200,
    'borders': (4, 4, 4, 4)
}))
def test_fixed_bordered_full(fixed_bordered, fast, size):
    em = fixed_bordered(size=size['size'])
    assert em.scan(fast=fast) == size['borders']


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('size', (None, 200))
def test_fixed_clear(fixed_clear, fast, size):
    em = fixed_clear(size=size)
    assert not any(em.scan(columns=20, fast=fast))


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('size', (None, 200))
def test_anima_bordered_partial(anima_bordered, fast, size):
    em = anima_bordered(size=size)
    assert any(em.scan(columns=20, fast=fast))


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('size', (None, 200))
def test_anima_bordered_frames_partial(anima_bordered, fast, size):
    em = anima_bordered(size=size, frames=10)
    assert any(em.scan(columns=20, fast=fast))


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('size', (None, 200))
def test_anima_bordered_frames_partial_max(anima_bordered, fast, size):
    em = anima_bordered(size=size, frames=10)
    assert any(em.scan(columns=20, fast=fast))


@pytest.mark.parametrize('params', ({
    'fast': True,
    'size': None,
    'borders': (12, 72, 9, 80)
}, {
    'fast': False,
    'size': None,
    'borders': (22, 85, 16, 85)
}, {
    'fast': True,
    'size': 200,
    'borders': (17, 77, 10, 79)
}, {
    'fast': False,
    'size': 200,
    'borders': (22, 84, 17, 86)
}))
def test_anima_bordered_full(anima_bordered, params):
    em = anima_bordered(size=params['size'])
    assert em.scan(fast=params['fast']) == params['borders']


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('size', (None, 200))
def test_anima_clear(anima_clear, fast, size):
    em = anima_clear(size=size, frames=10)
    assert not any(em.scan(columns=20, fast=fast))
