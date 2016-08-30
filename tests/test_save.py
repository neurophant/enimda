from io import BytesIO


def test_fixed_buff(fixed_clear):
    em = fixed_clear(minimize=200)
    em.scan(stripes=0.1, fast=True)
    em.crop()
    buff = BytesIO()
    em.save(fp=buff)
    assert len(buff.getvalue()) == 42046


def test_anima_buff(anima_clear):
    em = anima_clear(minimize=200)
    em.scan(stripes=0.1, fast=True)
    em.crop()
    buff = BytesIO()
    em.save(fp=buff)
    assert len(buff.getvalue()) == 1673519


def test_fixed_file(fixed_clear, current):
    em = fixed_clear(minimize=200)
    em.scan(stripes=0.1, fast=True)
    em.crop()
    em.save(fp=current('fixed/saved.jpg'))
    assert True


def test_anima_file(anima_clear, current):
    em = anima_clear(minimize=200)
    em.scan(stripes=0.1, fast=True)
    em.crop()
    em.save(fp=current('anima/saved.gif'))
    assert True
