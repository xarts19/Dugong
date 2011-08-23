#!/usr/bin/env python

"""Auto-generated file

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-23 15:06:07.704924 "

import os
import logging

import pygame
import pygame.locals as pl
import pygame.transform as pytrans

_LOGGER = logging.getLogger('main.utilities')
GAME_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
IMAGES_DIR = os.path.join(GAME_DIR, 'images')
LEVELS_DIR = os.path.join(GAME_DIR, 'levels')
TILE_SIZE = 50


def _load_image(name, colorkey=None):
    '''Load image. Uses red box as fallback.'''
    fullname = os.path.join(IMAGES_DIR, name)
    try:
        image = pygame.image.load(fullname)
        w, h = image.get_size()
        if w > TILE_SIZE or h > TILE_SIZE:
            image = pytrans.scale(image, (TILE_SIZE, TILE_SIZE))
    except pygame.error, message:
        _LOGGER.exception("Can't load image: %s", message)
        image = pygame.Surface((50, 50))
        image.fill((255, 0, 0, 255))
        colorkey = None
    image = image.convert()
    if colorkey is not None:
        if colorkey is (-1):
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pl.RLEACCEL)
    return image

def _load_level_info(name):
        '''Return level object (2d array) read from file'''
        level = []
        # read level info from file, create corresponding
        # objects and store them in 2d array
        for line in open(os.path.join(LEVELS_DIR, name)):
            row = []
            for item in line.rstrip():
                if item == 'r':
                    row.append(('road', 0))
                elif item == 'l':
                    row.append(('land', 0))
                elif item == 'f':
                    row.append(('forest', 0))
                elif item == 'w':
                    row.append(('water', 0))
                elif item == 'b':
                    row.append(('bridge', 0))
                elif item == 'm':
                    row.append(('mountain', 0))
                elif item == 'h':
                    row.append(('house', 0))
                elif item == '1':
                    row.append(('castle', 1))
                elif item == '2':
                    row.append(('castle', 2))
                else:
                    row.append(('road', 0))
                    _LOGGER.exception('unrecognized tile type in %s: %s',
                                      name, item)
            level.append(row)
        # all rows should be the same size
        if False in [len(level[i]) == len(level[i + 1])
                     for i in range(len(level) - 1)]:
            _LOGGER.exception('not all rows in %s have same width', name)
        return level
