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

Usage
-----

Find if image has any borders:

.. code-block:: python

    from enimda import ENIMDA


    # Open target image, convert it to grayscale and resize too 300 px
    image = ENIMDA(path='test.jpg', mode='L', resize=300)
    # Scan for borders existence
    image.scan(threshold=0.5, indent=0.25)
    # Save image with outlined borders for demonstration
    image.save(path='test-outlined.jpg', outline=True)
    # Print found image borders (tuple)
    print(image.borders)

Detect borders with high precision (iterative):

.. code-block:: python

    from enimda import ENIMDA


    # Open target image, convert it to grayscale and resize too 300 px
    image = ENIMDA(path='test.jpg', mode='L', resize=300)
    # Detect borders
    image.detect(threshold=0.5, indent=0.25)
    # Save image with outlined borders for demonstration
    image.save(path='test-outlined.jpg', outline=True)
    # Print found image borders (tuple)
    print(image.borders)
