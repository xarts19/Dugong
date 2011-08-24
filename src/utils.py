#!/usr/bin/env python

"""Auto-generated file

"""

import os
import logging
import ConfigParser as cparser

import pygame
import pygame.locals as pl
import pygame.transform as pytrans

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-23 15:06:07.704924 "

_LOGGER = logging.getLogger('main.utils')
GAME_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
IMAGES_DIR = os.path.join(GAME_DIR, 'images')
DESCR_DIR = os.path.join(GAME_DIR, 'descr')
TILE_SIZE = 50


def load_image(name, colorkey=None):
    '''Load image. Uses red box as fallback.'''
    fullname = os.path.join(IMAGES_DIR, name)
    # if image wasn't found, use red box as fallback
    try:
        image = pygame.image.load(fullname)
        w, h = image.get_size()
        image = pytrans.scale(image, (TILE_SIZE, TILE_SIZE))
    except pygame.error, message:
        _LOGGER.exception("Can't load image: %s", message)
        image = pygame.Surface((50, 50))
        image.fill((255, 0, 0, 255))
        colorkey = None
    # convert for faster blitting
    if os.path.splitext(name)[0] == '.png':
        image = image.convert_alpha()
    else:
        image = image.convert()
    # optionally set transparent color
    # if -1 is passes as color, use first pixel
    if colorkey is not None:
        if colorkey is (-1):
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pl.RLEACCEL)
    return image

def load_level_info(name, levels_file='levels'):
    '''Return level object (2d array) read from file'''
    level = {}
    # read level info from file, create corresponding
    # objects and store them in 2d arrays
    path = os.path.join(DESCR_DIR, levels_file)
    config = cparser.RawConfigParser()
    config.read(path)

    def parse(option):
        level[option] = []
        for line in config.get(name, option).split('\n'):
            row = []
            for item in line:
                row.append(item)
            level[option].append(row)

    # parse all options in needed level
    for option in config.options(name):
        parse(option)
        # all rows should be the same size
        if False in [len(level[option][i]) == len(level[option][i + 1])
                     for i in range(len(level[option]) - 1)]:
            _LOGGER.exception('not all rows in %s %s have same width', name, option)

    return level

def load_tile_types(filename='tile_types'):
    '''Return tile types dict read from config file.'''
    tiles_info = _load_config(filename)
    return tiles_info

def load_unit_types(filename='unit_types'):
    '''Return unit types dict read from config file.'''
    units_info = _load_config(filename)
    return units_info

def _load_config(filename):
    path = os.path.join(DESCR_DIR, filename)
    config = cparser.RawConfigParser()
    config.read(path)
    sections = {}
    for section in config.sections():
        options = {}
        for option in config.options(section):
            options[option] = config.get(section, option)
        if 'imagename' in options:
            options['image'] = load_image(options['imagename'])
        sections[section] = options
    return sections

class AnimatedImage(object):

    def __init__(self, static, animated, fps = 30):
        self._image = static
        self._images = animated
        self._current = self._image
        self._animated = False

    def __call__(self):
        return self._current

    def get_rect(self):
        return self._current.get_rect()

    def update(self, t):
        if self._animated:
            if t - self._last_update > self._delay:
                self._frame += 1
                if self._frame >= len(self._images):
                    self._frame = 0
                self.image = self._images[self._frame]
                self._last_update = t

    def start_animation(self):
        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self._animated = True
        self._current = self._images[0]
        self._start = pygame.time.get_ticks()
        self._delay = 1000 / fps
        self._last_update = 0
        self._frame = 0
        self.update(self._start)

    def stop_animation(self):
        self._animated = False
        self._current = self._image
