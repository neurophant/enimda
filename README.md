# ENIMDA

ENtropy-based IMage border Detection Algorithm: find out if your image has
borders or whitespaces around and helps you to trim border from your image by
providing approximate whitespace offsets for every side of a picture.


## Algorithm

For each side of the image strating from top, clockwise:
- Get upper block with 25% height of the dimension opposite to current side
- Get lower block with the same height as the upper one (50% of image total)
- Calculate their entropy for the both blocks
- Find their entropies difference
- Make upper block 1px less
- Repeat from p.2 until we hit image side
- Get maximum (minimum) of the entropies difference
- Here we have a border center if it lies closer to the edge rather than to the 
center of image and entropies difference is lower than pre-set median


## Prerequisites

- Ubuntu 16.04


## Dependencies

- Python 3.5+
- Pillow
- NumPy


## Install Python 3.5+

```
sudo add-apt-repository ppa:fkrull/deadsnakes

sudo apt-get update

sudo apt-get install python3.5 python3.5-venv python3.5-dev
```

## Setup environment and packages

```
pyvenv-3.5 .env

source .env/bin/activate

pip install -r requirements.txt
```


## Run

```
python enimda.py
```


## Examples

Within the **source** folder you will find source images - with border (bordered)
and without (clear)
In the **detected** folder there are the results of source images processing - 
each image has its borders outlined for visual demonstration
