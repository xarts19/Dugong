#!/usr/bin/env python

"""Auto-generated file

"""

import logging

import pygame

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

    @property
    def image(self):
        '''Return complete map image'''
        assert self._image != None
        return self._image

    def load_level(self, level_map):
        '''Reinitialize map with new level.'''
        self._level = self._init_level(level_map)
        self._image = self._generate_image(self._level)

    def _init_level(self, level_map):
        '''Return level object (2d array) read from file'''
        level = []
        tile_factory = _TileFactory()
        # create tiles from level definition
        for i, row in enumerate(level_map):
            tile_row = []
            for j, tile_type in enumerate(row):
                tile_row.append(tile_factory.create_tile(tile_type, (j, i)))
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
                image.blit(tile.image, tile.coord)
        return image

    def tile_at_coord(self, x, y):
        '''Return tile object at pixel coords.'''
        i = y / self._TILE_SIZE
        j = x / self._TILE_SIZE
        return self.tile_at_pos(i, j)

    def tile_at_pos(self, i, j):
        '''Return tile object at matrix coords.'''
        assert len(self._level) > i and len(self._level[i]) > j, \
            "Accesing tile outside of bounds: (%s, %s)" % (i, j)
        return self._level[i][j]


class _TileFactory(object):
    '''Manages creation of different tile types.

    Use create_tile method.
    '''

    def __init__(self):
        self._tile_types = utils.load_tile_types()
        # same dict but with keys as shortnames
        self._tile_types_short = {}
        for name, tile in self._tile_types.items():
            self._tile_types_short[tile['shortname']] = tile

    def create_tile(self, tile_type, pos):
        '''Returns tile instance with attributes for provided type.'''
        # check what dict use: with shortnames or normal names
        if len(tile_type) > 1:
            tile_types = self._tile_types
        else:
            tile_types = self._tile_types_short

        # check if such type exist
        assert tile_type in tile_types, "No such tile type: %s" % tile_type

        # init info from type
        type_info = tile_types[tile_type]
        tile_type = type_info['name']
        image = type_info['image']
        defence = int(type_info['defence'])
        speed = int(type_info['speed'])
        heal = int(type_info['heal'])
        # create tile
        tile = Tile(tile_type, image, defence, speed, heal, pos)
        return tile


class Tile(object):
    '''Single game tile. Stores attributes and image.'''

    def __init__(self, tile_type, image, defence, speed, heal, pos):
        self.type = tile_type
        self._image = image
        self.defence = defence
        self.speed = speed
        self.heal = heal
        self._owner = None
        self._pos = pos
        self._coord = tuple([v * utils.TILE_SIZE for v in pos])
        self._unit = None

    def selectable(self):
        '''We can only select unit or castle to buy units.'''
        return self._unit or self.type is 'castle'

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value

    @property
    def unit(self):
        '''Unit that is situated in this tile, or None if its empty.'''
        return self._unit

    @unit.setter
    def unit(self, value):
        assert not self.unit, \
               "Tile at (%s, %s) already occupied." % (self.pos)
        self._unit = value

    @property
    def image(self):
        return self._image

    @property
    def pos(self):
        return self._pos

    @property
    def coord(self):
        return self._coord



