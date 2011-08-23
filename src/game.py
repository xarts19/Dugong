#!/usr/bin/env python

"""

"""

import logging

import gamemap
import units

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-23 16:18:33.633299 "

_LOGGER = logging.getLogger('main.game')

class Game(object):
    '''Represents current game state.'''

    def __init__(self):
        _LOGGER.debug('Initializing game map')
        self._map = gamemap.GameMap()
        self._unit_factory = units.UnitFactory()
        self._players = [self._Player()]
        self._players[0].add_unit(self._unit_factory.create_unit('swordsman'))

    @property
    def map_image(self):
        return self._map.get_image()

    @property
    def units(self):
        units = []
        for player in self._players:
            units.append(player.get_units())
        return units

    class _Player(object):

        def __init__(self):
            self._units = []

        def add_unit(self, unit):
            self._units.append(unit)

        def get_units(self):
            return self._units

