#!/usr/bin/env python

"""Auto-generated file

"""

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
        assert unit_type in unit_types, "No such unit type: %s" % unit_type

        # init info from type
        type_info = unit_types[unit_type]
        image = type_info['image']
        if 'images' in type_info:
            images = type_info['images'].split(',')
        else:
            images = [image]
        #defence = type_info['defence']
        #speed = type_info['speed']
        #heal = type_info['heal']
        unit = Unit(unit_type, image, images, tile, owner)
        return unit

class Unit(pygame.sprite.Sprite):

    def __init__(self, unit_type, image, images, tile, owner):
        pygame.sprite.Sprite.__init__(self)
        self._type = unit_type
        self._image = utils.AnimatedImage(static=image, animated=images)
        self.rect = self._image.get_rect()
        self._owner = owner
        self._tile = tile
        self._set_tile_owner()
        self.rect.topleft = tile.coord

    @property
    def image(self):
        return self._image()

    def _set_tile_owner(self):
        self._tile.owner = self._owner

    def update(self, t):
        '''Redirect call to animated image.'''
        self._image.update()
