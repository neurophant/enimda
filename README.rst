ENIMDA
======

ENtropy-based IMage border Detection Algorithm: finds out if your image has borders or whitespaces around and helps you to trim border providing whitespace offsets for every side of a picture.

Supports GIF border detection and its cropping.

Algorithm (simplified)
----------------------

For each side of the image starting from top, rotating image counterclockwise
to keep side of interest on top:

* Get upper block 25% height of image
* Get lower block with the same height as the upper one
* Calculate entropy for both blocks
* Find their entropies difference
* Make upper block 1px less
* Repeat from p.2 until we hit image edge
* Get maximum (minimum) of the entropies difference - this is our border

.. image:: https://raw.githubusercontent.com/embali/enimda/master/algorithm.gif
    :alt: Sliding from center to edge - searching for maximum entropies difference
    :width: 300
    :height: 300

Requirements
------------

Python 3.5+

Setup
-----

.. code-block:: bash
    
    pip install https://github.com/embali/images2gif/tarball/master#egg=images2gif-1.0.0
    pip install https://github.com/embali/enimda/tarball/master#egg=enimda-1.1.3

Usage
-----

Find if image has any borders:

.. code-block:: python

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
