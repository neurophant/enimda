# ENIMDA

ENtropy-based IMage border Detection Algorithm: finds out if your image has
borders or whitespaces around and helps you to trim border from your image by
providing approximate whitespace offsets for every side of a picture.


## Algorithm

For each side of the image starting from the top, clockwise:
- Get upper block with 25% height of the dimension opposite to current side
- Get lower block with the same height as the upper one (50% of image total)
- Calculate entropy for both blocks
- Find their entropies difference
- Make upper block 1px less
- Repeat from p.2 until we hit image edge
- Get maximum (minimum) of the entropies difference
- Here we have a border center if it lies closer to the edge rather than to the 
center of image and entropies difference is lower than pre-set median


## Prerequisites

- Ubuntu 16.04 x64


## Dependencies

- Python 3.5
- Pillow 3.2
- NumPy 1.11


## Install Python 3.5

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

Within the images folder in **source** folder you will find source images - with
border (bordered) and without (clear)

In the **detected** folder there are the results of source images processing - 
each image has its borders outlined for visual demonstration


## Accuracy

Using included examples each resized to 300px for its minimal side and current
median value (0.5), detection rate for  bordered images is 82%, false detection
rate for clear images is 7%


## Performance

With current settings one image is getting processed within 4-5 seconds for
non-iterative mode and 5-15 seconds for iterative mode on Intel® Pentium(R) CPU
2117U @ 1.80GHz × 2 with 4 Gb RAM
