from setuptools import setup
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='enimda',
    version='1.1.4',
    description='Entropy-based image border detection algorithm',
    long_description=long_description,
    url='https://github.com/embali/enimda/',
    author='Anton Smolin',
    author_email='smolin.anton@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='image border detection',
    py_modules=['enimda'],
    install_requires=['numpy>=1.11.1', 'Pillow>=3.3.1'],
    dependency_links=['https://github.com/embali/images2gif/tarball/master#egg=images2gif-1.0.0'],
)
