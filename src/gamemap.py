#!/usr/bin/env python

"""Auto-generated file

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-22 12:40:17.689062 "

import os
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
    '''Stores map image and array. Loads levels.'''

    def __init__(self):
        self._TILE_SIZE = TILE_SIZE
        self._level_name = "level_1"
        self._level = self._load_level(self._level_name)
        self._image = self._generate_image(self._level)

    def get_image(self):
        '''Return complete map image'''
        assert self._image != None
        return self._image

    def load_level(self, level_num):
        '''Reinitialize map with new level.'''
        pass

    def _load_level(self, name):
        '''Return level object (2d array) read from file'''
        level = []
        tile_factory = _TileFactory()
        # read level info from file, create corresponding
        # objects and store them in 2d array
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

        # all rows should be the same size
        if False in [len(level[i]) == len(level[i + 1])
                     for i in range(len(level) - 1)]:
            LOGGER.exception('not all rows in %s have same width', name)
        return level

    def _generate_image(self, level):
        '''Return image of whole level built from tiles.'''
        tile_width = tile_height = self._TILE_SIZE
        map_width = len(level[0]) * tile_width
        map_height = len(level) * tile_height
        image = pygame.Surface((map_width, map_height))
        # blit each tile to image
        for i, row in enumerate(level):
            for j, tile in enumerate(row):
                image.blit(tile.get_image(), (j * tile_width, i * tile_height))
        return image

    def _to_tile_xy(self, pixel_x, pixel_y):
        '''Convert pixel coords to tile coords.'''
        return pixel_x / self._TILE_SIZE, pixel_y / self._TILE_SIZE

    def _tile_at_xy(self,  pixel_x, pixel_y):
        '''Return tile object at pixel coords.'''
        return self._level[pixel_y / self._TILE_SIZE][pixel_x / self._TILE_SIZE]


class _TileFactory(object):
    '''Manages creation of different tile types.

    Use create_tile method.
    '''

    def __init__(self):
        self._tile_types = self._load_tile_types()

    def _load_tile_types(self, filename='tile_types'):
        '''Return tile types dict read from config file.'''
        path = os.path.join(IMAGES_DIR, filename)
        config = ConfigParser.RawConfigParser()
        config.read(path)
        types = config.sections()
        tile_types = {}
        for tile_type in types:
            tile_info = {}
            tile_info['imagename'] = config.get(tile_type, 'imagename')
            tile_info['defence'] = config.get(tile_type, 'defence')
            tile_info['speed'] = config.get(tile_type, 'speed')
            tile_info['heal'] = config.get(tile_type, 'heal')
            tile_types[tile_type] = tile_info
        return tile_types

    def create_tile(self, tile_type=None, owner=None):
        '''Returns tile instance with attributes for provided type.'''
        type_info = self._tile_types[tile_type]
        image = _load_image(type_info['imagename'])
        defence = type_info['defence']
        speed = type_info['speed']
        heal = type_info['heal']
        tile = _Tile(tile_type=tile_type, image=image, defence=defence,
                     speed=speed, heal=heal, owner=owner)
        return tile


class _Tile(object):
    '''Single game tile. Stores attributes and image.'''

    def __init__(self, tile_type, image, defence, speed, heal, owner):
        self.type = tile_type
        self.image = image
        self.defence = defence
        self.speed = speed
        self.heal = heal
        self.owner = owner
        self.unit = None

    def get_contained_unit(self):
        '''Unit that is situated in this tile, or None if its empty.'''
        return self.unit

    def has_unit(self):
        '''True if unit is situated here.'''
        return self.unit is not None

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
