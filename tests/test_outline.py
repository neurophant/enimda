import os


def test_fixed_bordered_outline(fixed_bordered):
    em = fixed_bordered(minimize=200)
    em.scan(stripes=0.1, fast=True)
    em.outline()
    path = os.path.join(os.path.dirname(__file__), 'fixed/outlined.jpg')
    em.save(file_=path)
    assert em.has_borders == True


def test_anima_bordered_outline(anima_bordered):
    em = anima_bordered(minimize=200, frames=0.1, max_frames=10)
    em.scan(stripes=0.1, fast=True)
    em.outline()
    path = os.path.join(os.path.dirname(__file__), 'anima/outlined.gif')
    em.save(file_=path)
    assert em.has_borders == True
