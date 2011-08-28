#!/usr/bin/env python

"""Auto-generated file

"""

import sys
import logging

import pygame

import utils


__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-23 15:04:59.084491 "

_LOGGER = logging.getLogger('main.units')

class UnitFactory(object):
    '''Manages creation of different unit types.

    Use create_unit method.
    '''

    def __init__(self):
        self._unit_types = utils.load_unit_types()
        # same dict but with keys as shortnames
        self._unit_types_short = {}
        for name, unit in self._unit_types.items():
            self._unit_types_short[unit['shortname']] = unit

    def create_unit(self, unit_type, tile, owner=None):
        '''Returns tile instance with attributes for provided type.'''
        # check what dict use: with shortnames or normal names
        if len(unit_type) > 1:
            unit_types = self._unit_types
        else:
            unit_types = self._unit_types_short

        # check if such type exist
        if unit_type not in unit_types:
            _LOGGER.exception("No such unit type: %s", unit_type)
            return None

        # init info from type
        type_info = unit_types[unit_type]
        image = type_info['image']
        if 'animation' in type_info:
            images = type_info['animation']
        else:
            images = [image]
        #defence = type_info['defence']
        #speed = type_info['speed']
        #heal = type_info['heal']
        max_moves = float(type_info['max_moves'])
        _range = int(type_info['range'])
        name = type_info['name']
        unit_class = getattr(sys.modules[__name__], name.capitalize(), Unit)
        unit = unit_class(unit_type, image, images, tile, owner, max_moves, _range)
        return unit

class Unit(pygame.sprite.Sprite):

    def __init__(self, unit_type, image, images, tile, owner, max_moves, _range):
        pygame.sprite.Sprite.__init__(self)
        self._type = unit_type
        self._owner = owner
        self._tile = tile
        self._set_tile_owner()
        self._image = utils.AnimatedImage(static=image, animated=images, coord=tile.coord)
        self.rect = self._image.get_rect()
        self.moves_left = max_moves
        self.max_moves = max_moves
        self.range = _range

    def can_attack(self, unit):
        i, j = self.tile.pos
        i2, j2 = unit.tile.pos
        return abs(i - i2) + abs(j - j2) <= self.range

    @property
    def image(self):
        return self._image()

    @property
    def tile(self):
        return self._tile

    @tile.setter
    def tile(self, value):
        self._tile = value

    def _set_tile_owner(self):
        self._tile.owner = self._owner

    def update(self, t):
        '''Redirect call to animated image.'''
        self._image.update(t)
        self.rect = self._image.get_rect()

    def move(self, path):
        self._image.start_animation(path)

class Catapult(Unit):

    def __init__(self, *args):
        Unit.__init__(self, *args)

    def can_attack(self, unit):
        i, j = self.tile.pos
        i2, j2 = unit.tile.pos
        return 1 < abs(i - i2) + abs(j - j2) <= self.range

