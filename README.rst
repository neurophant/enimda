ENIMDA
======

ENtropy-based IMage border Detection Algorithm: finds out if your image has borders or whitespaces around and helps you to trim border providing whitespace offsets for every side of a picture.

Algorithm
---------

For each side of the image starting from the top, clockwise:

* Get upper block with 25% height (indent) of the dimension opposite to current side
* Get lower block with the same height as the upper one (50% of image total)
* Calculate entropy for both blocks
* Find their entropies difference
* Make upper block 1px less
* Repeat from p.2 until we hit image edge
* Get maximum (minimum) of the entropies difference
* Here we have a border center if it lies closer to the edge rather than to the center of image and entropies difference is lower than pre-set threshold

Requirements
------------

Python 3.5+

Setup
-----

.. code-block:: bash
    
    pip install enimda

Usage
-----

Find if image has any borders:

.. code-block:: python

    from PIL import Image

    from enimda import ENIMDA


    # Load target image
    em = ENIMDA(file_='test.jpg')

    # Scan for borders with high precision
    em.scan(fast=False)

    # Save image with outlined borders for demonstration
    em.outline()
    em.save(file_='outlined.jpg')

    # Print found image borders (tuple)
    print(em.borders)

Demo
----

For demonstration please refer to `ENIMDA Demo <https://github.com/embali/enimda-demo/>`_

Tests
-----

Run tests: py.test
