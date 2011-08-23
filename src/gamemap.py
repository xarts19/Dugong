#!/usr/bin/env python

"""Auto-generated file

"""

import os
import logging

import pygame
import pygame.locals as pl

import utils

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-22 12:40:17.689062 "

_LOGGER = logging.getLogger('main.map')

class GameMap(object):
    '''Stores map image and array. Loads levels.'''

    def __init__(self):
        self._TILE_SIZE = utils.TILE_SIZE
        self._level = None
        self._image = None
        self.load_level(1)

    def get_image(self):
        '''Return complete map image'''
        assert self._image != None
        return self._image

    def load_level(self, level_num):
        '''Reinitialize map with new level.'''
        level_name = 'level_' + str(level_num)
        level_info = utils.load_level_info(level_name)
        self._level = self._init_level(level_info)
        self._image = self._generate_image(self._level)

    def _init_level(self, level_info):
        '''Return level object (2d array) read from file'''
        level = []
        tile_factory = _TileFactory()
        # create tiles from level definition
        for row in level_info:
            tile_row = []
            for item in row:
                tile_type = item[0]
                tile_owner = item[1] if item[1] else None
                tile_row.append(tile_factory.create_tile(tile_type, tile_owner))
            level.append(tile_row)
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
        self._tile_types = utils.load_tile_types()

    def create_tile(self, tile_type=None, owner=None):
        '''Returns tile instance with attributes for provided type.'''
        assert tile_type in self._tile_types
        type_info = self._tile_types[tile_type]
        image = type_info['image']
        defence = type_info['defence']
        speed = type_info['speed']
        heal = type_info['heal']
        tile = Tile(tile_type=tile_type, image=image, defence=defence,
                    speed=speed, heal=heal, owner=owner)
        return tile


class Tile(object):
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



