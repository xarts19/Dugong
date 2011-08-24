#!/usr/bin/env python

"""

"""

import logging

import gamemap
import units
import utils

import pygame

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-23 16:18:33.633299 "

_LOGGER = logging.getLogger('main.game')

class Game(object):
    '''Represents current game state.'''

    def __init__(self, _map, selection):
        _LOGGER.debug('Initializing game map')
        self._map = _map
        self._selection = selection
        self._unit_factory = units.UnitFactory()
        self._players = [self._Player(), self._Player()]
        self._units = []
        self.load_level(1)

    def load_level(self, level_num):
        level_name = 'level_' + str(level_num)
        level_info = utils.load_level_info(level_name)
        self._map.load_level(level_info['map'])
        self._init_units(level_info['units_1'], self._players[0])
        self._init_units(level_info['units_2'], self._players[1])

    def _init_units(self, level_units, player):
        for i, row in enumerate(level_units):
            for j, unit_type in enumerate(row):
                if unit_type != '.':
                    self.add_unit(unit_type, player, self._map.tile_at_pos(i, j))

    @property
    def units(self):
        return self._units

    def add_unit(self, unit_type, player, tile):
        unit = self._unit_factory.create_unit(unit_type, tile, player)
        tile.unit = unit
        self._units.append(unit)
        player.add_unit(unit)


    class _Player(object):

        def __init__(self):
            self._units = []

        def add_unit(self, unit):
            self._units.append(unit)

        def get_units(self):
            return self._units


class Selection(pygame.sprite.Sprite):
    """Object responsible for selection of tiles."""

    def __init__(self, _map):
        self._map = _map
        self._green_image = utils.load_image('selection_green_bold.png')
        self._orange_image = utils.load_image('selection_orange_bold.png')
        self._pointed_tile = None
        self._selected_tile = None

    def mouse(self, pos):
        '''Determine tile where mouse points.'''
        self._pointed_tile = self._map.tile_at_coord(*pos)

    def select_or_move(self, pos):
        '''Determine tile that needs to be selected.'''
        # TODO: check game rules here e. g. its unit belong to current player
        if self._map.tile_at_coord(*pos).unit:
            self._selected_tile = self._map.tile_at_coord(*pos)

    def unselect(self):
        self._selected_tile = None

    def draw(self, image):
        if self._pointed_tile:
            image.blit(self._green_image, self._pointed_tile.coord)
        if self._selected_tile:
            image.blit(self._orange_image, self._selected_tile.coord)