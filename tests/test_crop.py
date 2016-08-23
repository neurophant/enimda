import os


def test_fixed_bordered_crop(fixed_bordered):
    em = fixed_bordered(minimize=200)
    em.scan(stripes=0.1, fast=True)
    em.crop()
    path = os.path.join(os.path.dirname(__file__), 'fixed/cropped.jpg')
    em.save(file_=path)
    assert em.has_borders == True


def test_anima_bordered_crop(anima_bordered):
    em = anima_bordered(minimize=200)
    em.scan(frames=0.1, stripes=0.1, fast=True)
    em.crop()
    path = os.path.join(os.path.dirname(__file__), 'anima/cropped.gif')
    em.save(file_=path)
    assert em.has_borders == True
