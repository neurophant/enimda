ENIMDA
======

Entropy-based image border detection algorithm: finds out if your image has
borders or whitespaces around and helps you to trim border providing whitespace
offsets for every side of a picture, supports animated GIFs.

|pypi| |travisci|

.. |pypi| image:: https://badge.fury.io/py/enimda.svg
    :target: https://badge.fury.io/py/enimda
    :alt: pypi version
.. |travisci| image:: https://travis-ci.org/embali/enimda.svg?branch=master
    :target: https://travis-ci.org/embali/enimda
    :alt: travis ci build status

Algorithm (simplified)
----------------------

For each side of the image starting from top, rotating image counterclockwise
to keep side of interest on top:

* Get upper block 25% of image height
* Get lower block with the same height as the upper one
* Calculate entropy for both blocks and their difference
* Make upper block 1px less
* Repeat from p.2 until we hit image edge
* Border is between blocks with entropy difference maximum

.. image:: https://raw.githubusercontent.com/embali/enimda/master/algorithm.gif
    :alt: Sliding from center to edge - searching for maximum entropy difference
    :width: 300
    :height: 300

Requirements
------------

Python 3.5+

Setup
-----

.. code-block:: bash
    
    python-3.6 -m venv .env
    source .env/bin/activate
    pip install enimda

Usage
-----

Find if image has borders:

.. code-block:: python

    from enimda import ENIMDA


    # Load target image
    em = ENIMDA(fp='test.jpg')

    # Scan for borders with high precision
    borders = em.scan(fast=False)

    # Print found image borders (tuple): top, right, bottom, left
    print(borders)

Demo
----

For demo please refer to `ENIMDA Demo <https://github.com/embali/enimda-demo/>`_

Also it lives at `Picture Instruments <http://picinst.com/>`_ as 'Remove borders'
instrument

Tests
-----

Run tests: py.test
