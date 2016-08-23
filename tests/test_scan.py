import pytest


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('resize', (None, 300))
def test_bordered_partial(fixed_bordered, fast, resize):
    em = fixed_bordered(resize=resize)
    em.scan(rand=0.1, fast=fast)
    assert em.has_borders == True


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('resize', ({'resize': None, 'borders': (4, 4, 4, 4)},
                                    {'resize': 300, 'borders': (5, 4, 4, 5)}))
def test_bordered_full(fixed_bordered, fast, resize):
    em = fixed_bordered(resize=resize['resize'])
    em.scan(rand=1.0, fast=fast)
    assert em.borders == resize['borders']


@pytest.mark.parametrize('fast', (True, False))
@pytest.mark.parametrize('resize', (None, 300))
def test_clear(fixed_clear, fast, resize):
    em = fixed_clear(resize=resize)
    em.scan(rand=0.1, fast=fast)
    assert em.has_borders == False
