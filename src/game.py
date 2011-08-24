#!/usr/bin/env python

"""

"""

import logging

import gamemap
import units
import utils

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-23 16:18:33.633299 "

_LOGGER = logging.getLogger('main.game')

class Game(object):
    '''Represents current game state.'''

    def __init__(self, _map):
        _LOGGER.debug('Initializing game map')
        self._map = _map
        self._unit_factory = units.UnitFactory()
        self._players = [self._Player()]
        self._units = []
        self.load_level(1)

        self.add_unit('swordsman', self._players[0], self._map.tile_at_pos(0, 9))
        self.add_unit('general', self._players[0], self._map.tile_at_pos(5, 0))
        self.add_unit('marksman', self._players[0], self._map.tile_at_pos(0, 0))
        self.add_unit('earthgolem', self._players[0], self._map.tile_at_pos(0, 1))

    def load_level(self, level_num):
        level_name = 'level_' + str(level_num)
        level_info = utils.load_level_info(level_name)
        self._map.load_level(level_info['map'])

    @property
    def units(self):
        return self._units

    def add_unit(self, unit_type, player, tile):
        unit = self._unit_factory.create_unit(unit_type, tile, self)
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

