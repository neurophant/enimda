from setuptools import setup
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='enimda',
    version='2.0.0',
    description='Entropy-based image border detection algorithm library',
    long_description=long_description,
    url='https://github.com/embali/enimda/',
    author='Anton Smolin',
    author_email='smolin.anton@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='image border algorithm whitespace enimda',
    py_modules=['enimda'],
    install_requires=['Pillow>=3.3.1'],
)
