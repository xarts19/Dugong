#!/usr/bin/env python

"""Auto-generated file

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-22 12:40:17.689062 "

import os
import sys
import logging

import pygame
import pygame.locals as pl
import pygame.transform as pytrans

LOGGER = logging.getLogger('main.map')
GAME_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
IMAGES_DIR = os.path.join(GAME_DIR, 'images')
LEVELS_DIR = os.path.join(GAME_DIR, 'levels')

class GameMap(object):

    def __init__(self):

        self._CELL_SIZE = 50
        self._images = self._load_images()
        self._level_name = "level_1"
        self._level = self._load_level(self._level_name)
        self._image = self._generate_image(self._level)

    def get_cell_type(self, pixel_x, pixel_y):
        x, y = self._to_cell_xy(pixel_x, pixel_y)
        return self_level[y][x]

    def get_image(self):
        assert self._image != None
        return self._image


    def _load_level(self, name):
        level = []
        allowed_cell_types = ('l','w','b','f','m','r')
        for line in open(os.path.join(LEVELS_DIR, name)):
            row = []
            for item in line.rstrip():
                if item in allowed_cell_types:
                    row.append(item)
                else:
                    row.append('r')
                    LOGGER.exception('unrecognized cell type in %s: %s', name, item)
            level.append(row)
        return level

    def _generate_image(self, level):
        pass

    def _load_images(self):
        images = dict.fromkeys(['land', 'forest', 'road', 'water', 'bridge', 'mountain'], None)
        for image in images.keys():
            images[image] = self._load_image(image+'.jpg')

    def _load_image(self, name, colorkey=None):
        '''Load image. Uses red box as fallback.'''
        fullname = os.path.join(IMAGES_DIR, name)
        try:
            image = pygame.image.load(fullname)
            image = pytrans.scale(image, (self._CELL_SIZE, self._CELL_SIZE))
        except pygame.error, message:
            LOGGER.exception("Can't load image: %s", message)
            image = pygame.Surface((50, 50))
            image.fill((255, 0, 0, 255))
            colorkey = None
        image = image.convert()
        if colorkey is not None:
            if colorkey is (-1):
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pl.RLEACCEL)
        return image

    def _to_cell_xy(self, pixel_x, pixel_y):
        return pixel_x / self._CELL_SIZE, pixel_y / self._CELL_SIZE

