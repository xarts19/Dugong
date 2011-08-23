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

    def create_unit(self, unit_type=None, owner=None):
        '''Returns tile instance with attributes for provided type.'''
        assert unit_type in self._unit_types
        type_info = self._unit_types[unit_type]
        image = type_info['image']
        #defence = type_info['defence']
        #speed = type_info['speed']
        #heal = type_info['heal']
        unit = Unit(unit_type=unit_type, image=image)
        return unit

class Unit(pygame.sprite.Sprite):

    def __init__(self, unit_type, image):
        pygame.sprite.Sprite.__init__(self)
        self._type = unit_type
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (50, 50)


