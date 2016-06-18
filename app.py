from os import listdir
from os.path import join, isfile

from enimda import ENIMDA


SOURCE_CLEAR_PATH = './images/source/clear'         # Sources without border
SOURCE_BORDERED_PATH = './images/source/bordered'   # Bordered sources

DETECTED_CLEAR_PATH = './images/detected/clear'         # No border results
DETECTED_BORDERED_PATH = './images/detected/bordered'   # Bordered results


# Source files - clear and bordered, sorted alphabetically
source_clear_files = sorted(_ for _ in listdir(SOURCE_CLEAR_PATH)
                            if isfile(join(SOURCE_CLEAR_PATH, _)))
source_bordered_files = sorted(_ for _ in listdir(SOURCE_BORDERED_PATH)
                               if isfile(join(SOURCE_BORDERED_PATH, _)))


# Process bordered images
rate = 0
for index, name in enumerate(source_bordered_files):
    image = ENIMDA(path=join(SOURCE_BORDERED_PATH, name), mode='L', resize=300)
    image.scan(threshold=0.5, indent=0.25)
    rate += int(image.has_borders)
    image.save(path=join(DETECTED_BORDERED_PATH, name), outline=True)
    print(index, name, image.has_borders, image.borders)

print(rate / len(source_bordered_files))

# Process clear images
rate = 0
for index, name in enumerate(source_clear_files):
    image = ENIMDA(path=join(SOURCE_CLEAR_PATH, name), mode='L', resize=300)
    image.scan(threshold=0.5, indent=0.25)
    rate += int(image.has_borders)
    image.save(path=join(DETECTED_CLEAR_PATH, name), outline=True)
    print(index, name, image.has_borders, image.borders)

print(rate / len(source_clear_files))
