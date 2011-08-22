#!/usr/bin/env python

"""Auto-generated file

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-22 12:40:17.689062 "

import os
import sys
import logging
import ConfigParser

import pygame
import pygame.locals as pl
import pygame.transform as pytrans

LOGGER = logging.getLogger('main.map')
GAME_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
IMAGES_DIR = os.path.join(GAME_DIR, 'images')
LEVELS_DIR = os.path.join(GAME_DIR, 'levels')
TILE_SIZE = 50


class GameMap(object):

    def __init__(self):

        self._TILE_SIZE = TILE_SIZE
        self._level_name = "level_1"
        self._level = self._load_level(self._level_name)
        self._image = self._generate_image(self._level)

    def get_tile_type(self, pixel_x, pixel_y):
        x, y = self._to_tile_xy(pixel_x, pixel_y)
        return self._level[y][x]

    def get_image(self):
        assert self._image != None
        return self._image

    def load_level(self, level_num):
        pass

    def _load_level(self, name):
        level = []
        tile_factory = _TileFactory()
        for line in open(os.path.join(LEVELS_DIR, name)):
            row = []
            for item in line.rstrip():
                if item == 'r':
                    row.append(tile_factory.create_tile('road'))
                elif item == 'l':
                    row.append(tile_factory.create_tile('land'))
                elif item == 'f':
                    row.append(tile_factory.create_tile('forest'))
                elif item == 'w':
                    row.append(tile_factory.create_tile('water'))
                elif item == 'b':
                    row.append(tile_factory.create_tile('bridge'))
                elif item == 'm':
                    row.append(tile_factory.create_tile('mountain'))
                elif item == 'h':
                    row.append(tile_factory.create_tile('house'))
                elif item == '1':
                    row.append(tile_factory.create_tile('castle', 1))
                elif item == '2':
                    row.append(tile_factory.create_tile('castle', 2))
                else:
                    row.append(tile_factory.create_tile('road'))
                    LOGGER.exception('unrecognized tile type in %s: %s',
                                     name, item)
            level.append(row)

        if False in [len(level[i]) == len(level[i + 1]) 
                     for i in range(len(level) - 1)]:
            LOGGER.exception('not all rows in %s have same width', name)
        return level

    def _generate_image(self, level):
        w = h = self._TILE_SIZE
        width = len(level[0]) * w
        height = len(level) * h
        image = pygame.Surface((width, height))
        for i, row in enumerate(level):
            for j, tile in enumerate(level[i]):
                image.blit(tile.get_image(), (j * w, i * h))
        return image

    def _to_tile_xy(self, pixel_x, pixel_y):
        return pixel_x / self._TILE_SIZE, pixel_y / self._TILE_SIZE


class _TileFactory(object):
    '''Manages creation of different tile types.

    Use create_tile method.
    '''

    def __init__(self):
        self._tile_types = self._load_tile_types()

    def _load_tile_types(self, filename='tile_types'):
        path = os.path.join(IMAGES_DIR, filename)
        config = ConfigParser.RawConfigParser()
        config.read(path)
        types = config.sections()
        tile_types = {}
        for t in types:
            tile = {}
            tile['imagename'] = config.get(t, 'imagename')
            tile['defence'] = config.get(t, 'defence')
            tile['speed'] = config.get(t, 'speed')
            tile['heal'] = config.get(t, 'heal')
            tile_types[t] = tile
        return tile_types

    def create_tile(self, tile_type=None, owner=None):
        '''Returns tile instance with attributes for provided type.'''
        type = self._tile_types[tile_type]
        im = _load_image(type['imagename'])
        de = type['defence']
        sp = type['speed']
        he = type['heal']
        tile = _Tile(type=tile_type, image=im, defence=de,
                     speed=sp, heal=he, owner=owner)
        return tile


class _Tile(object):

    def __init__(self, type, image, defence, speed, heal, owner):
        self.type = type
        self.image = image
        self.defence = defence
        self.speed = speed
        self.heal = heal
        self.owner = owner
        self.unit = None

    def get_contained_unit(self):
        return self.unit

    def has_unit(self):
        return self.unit != None

    def get_image(self):
        return self.image


def _load_image(name, colorkey=None):
    '''Load image. Uses red box as fallback.'''
    fullname = os.path.join(IMAGES_DIR, name)
    try:
        image = pygame.image.load(fullname)
        image = pytrans.scale(image, (TILE_SIZE, TILE_SIZE))
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
