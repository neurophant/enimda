import pytest


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('minimize', (None, 200))
def test_fixed_bordered_partial(fixed_bordered, fast, minimize):
    em = fixed_bordered(minimize=minimize)
    em.scan(stripes=0.1, fast=fast)
    assert em.has_borders == True


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('minimize', (
    {'minimize': None, 'borders': (4, 4, 4, 4)},
    {'minimize': 200, 'borders': (5, 4, 4, 5)}))
def test_fixed_bordered_full(fixed_bordered, fast, minimize):
    em = fixed_bordered(minimize=minimize['minimize'])
    em.scan(fast=fast)
    assert em.borders == minimize['borders']


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('minimize', (None, 200))
def test_fixed_clear(fixed_clear, fast, minimize):
    em = fixed_clear(minimize=minimize)
    em.scan(stripes=0.1, fast=fast)
    assert em.has_borders == False


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('minimize', (None, 200))
def test_anima_bordered_partial(anima_bordered, fast, minimize):
    em = anima_bordered(minimize=minimize)
    em.scan(stripes=0.1, fast=fast)
    assert em.has_borders == True


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('minimize', (None, 200))
def test_anima_bordered_frames_partial(anima_bordered, fast, minimize):
    em = anima_bordered(minimize=minimize, frames=0.1, max_frames=10)
    em.scan(stripes=0.1, fast=fast)
    assert em.has_borders == True


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('minimize', (None, 200))
def test_anima_bordered_frames_partial_max(anima_bordered, fast, minimize):
    em = anima_bordered(minimize=minimize, frames=0.1, max_frames=10)
    em.scan(stripes=0.1, max_stripes=10, fast=fast)
    assert em.has_borders == True


@pytest.mark.parametrize('params', (
    {'fast': True, 'minimize': None, 'borders': (12, 72, 9, 80)},
    {'fast': False, 'minimize': None, 'borders': (22, 85, 16, 85)},
    {'fast': True, 'minimize': 200, 'borders': (12, 72, 9, 80)},
    {'fast': False, 'minimize': 200, 'borders': (22, 85, 16, 85)}))
def test_anima_bordered_full(anima_bordered, params):
    em = anima_bordered(minimize=params['minimize'])
    em.scan(fast=params['fast'])
    assert em.borders == params['borders']


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('minimize', (None, 200))
def test_anima_clear(anima_clear, fast, minimize):
    em = anima_clear(minimize=minimize, frames=0.1, max_frames=10)
    em.scan(stripes=0.1, fast=fast)
    assert em.has_borders == False
