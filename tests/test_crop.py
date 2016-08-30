def test_fixed_bordered_crop(fixed_bordered, current):
    em = fixed_bordered(minimize=200)
    em.scan(stripes=0.1, fast=True)
    em.crop()
    em.save(fp=current('fixed/cropped.jpg'))
    assert em.has_borders == True


def test_anima_bordered_crop(anima_bordered, current):
    em = anima_bordered(minimize=200, frames=0.1, max_frames=10)
    em.scan(stripes=0.1, fast=True)
    em.crop()
    em.save(fp=current('anima/cropped.gif'))
    assert em.has_borders == True
