#!/usr/bin/env python

"""Auto-generated file

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-22 12:40:17.689062 "

import os
import sys

GAME_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
IMAGES_DIR = os.path.join(GAME_DIR, 'images')
LEVELS_DIR = os.path.join(GAME_DIR, 'levels')

class Map(object):

    def __init__(self):

        self._level_name = "level_1"
        self._level = self._load_level(self.level_name)
        self._image = self._generate_image(self._level)

    def get_cell_type(self, x, y):
        pass

    def get_image(self):
        assert self._image != None
        return self._image


    def _load_level(self, name):
        pass

    def _generate_image(self, level):
        pass

    def _load_images(self):
        pass
