#!/usr/bin/env python

"""Contains utility function such as loading images, concatenationg them,
loading and parsing config files.

"""

import os
import logging

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

# default configs
SCREEN_SIZE = (1280, 720)
TILE_SIZE = 50
SCROLL_SPEED = 3
FPS = 60

class ResourceManager(object):

    def __init__(self):
        self._loaded_resources = {}

    def get(self, res_name, size=None, rotate=0):
        res = None
        if res_name in self._loaded_resources:
            res = self._loaded_resources[res_name]
        else:
            if res_name == 'levels_info':
                res = load_levels_info()
            elif res_name == 'tile_types':
                _LOGGER.debug("Loading tiles data")
                from configs.tiletypes import TILE_TYPES
                res = TILE_TYPES
            elif res_name == 'unit_types':
                _LOGGER.debug("Loading units data")
                from configs.unittypes import UNIT_TYPES
                res = UNIT_TYPES
            else:
                identifiers = res_name.split(':')
                path = os.path.join(*identifiers)
                res = load_image(path)
            self._loaded_resources[res_name] = res

        if size:
            res = pytrans.scale(res, size)
        if rotate:
            res = pygame.transform.rotate(res, rotate)

        return res

RES_MANAGER = ResourceManager()

def load_configs():
    _LOGGER.debug('Loading configs')
    from configs import config
    global SCREEN_SIZE
    global TILE_SIZE
    global SCROLL_SPEED
    global FPS
    try:
        SCREEN_SIZE = config.graphics['screen_mode']
        TILE_SIZE = config.graphics['tile_size']
        SCROLL_SPEED = config.graphics['scroll_speed']
        FPS = config.graphics['fps']
    except KeyError:
        _LOGGER.exception("Config file is broken.")


def load_levels_info():
    '''Format info a little, check for integrity and return levels info.'''
    _LOGGER.debug("Loading levels data")
    from configs.levels import LEVELS, ABBREVIATIONS
    # transform to more friendly for game format
    # format map from multiline string to 2d array of letters
    levels_info = LEVELS
    for name, level in levels_info.items():
        level['map'] = [[ABBREVIATIONS[char] for char in line.lstrip().rstrip()]
                        for line in level['map'].split('\n')]
        # all rows should be the same size
        for row in level['map']:
            if len(row) != len(level['map'][0]):
                _LOGGER.exception('not all rows in map "%s" have same width', name)
    return levels_info


def load_image(name, colorkey=None):
    '''Load image. Uses red box as fallback.'''
    fullname = os.path.join(IMAGES_DIR, name)
    # if image wasn't found, use red box as fallback
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        _LOGGER.exception("Can't load image: %s", message)
        image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        image.fill((255, 0, 0, 255))
        colorkey = None
    try:
        # convert for faster blitting
        if os.path.splitext(name)[0] == '.png':
            image = image.convert_alpha()
        else:
            image = image.convert()
    except:
        _LOGGER.exception('pygame not initialized')
    # optionally set transparent color
    # if -1 is passes as color, use first pixel
    if colorkey is not None:
        if colorkey is (-1):
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pl.RLEACCEL)
    return image


class Writer(object):

    def __init__(self, size, color):
        self.size = size
        self.color = color
        self.antialias = True
        self.font = pygame.font.Font(pygame.font.get_default_font(), self.size)

    def render(self, string, color=None):
        if color:
            return self.font.render(str(string), self.antialias, color)
        else:
            return self.font.render(str(string), self.antialias, self.color)
