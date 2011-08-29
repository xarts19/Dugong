#!/usr/bin/env python

"""
All game logic and constraints is here.
"""

import logging

import gamemap
import units
import utils

import pygame
import pygame.locals as pl

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
        self._players = Players([])
        self._selection = Selection(self._map, self._players)
        # FIXME: find where to put this
        self._levels = utils.load_levels_info()
        self.load_level('1')
        # works only after level was loaded (needs to know map size):
        self._init_graphics()

    def _init_graphics(self):
        '''Create surface for map, units and effects.'''
        w, h = self.get_map_size()
        self._image = pygame.Surface((w, h))

    def load_level(self, name):
        '''Load level from file with given number. Init map and units.'''
        level_info = self._levels[name]
        self._map.load_level(level_info)
        for i, units in enumerate(level_info['units']):
            player = Player(str(i))
            self._players.add(player)
            self._init_units(units, player)

    def _init_units(self, units, player):
        '''Create units from level specs for given player.'''
        for unit_type, i, j in units:
            self._add_unit(unit_type, player, self._map.tile_at_pos(i, j))

    def _add_unit(self, unit_type, player, tile):
        '''Add unit to tile, _units and player'''
        unit = self._unit_factory.create_unit(unit_type, tile, player)
        if unit:
            tile.unit = unit
            player.add(unit)

    def get_map_size(self):
        return self._map.image.get_size()

    def update(self, game_ticks):
        '''Update all sprites.'''
        self._players.update(game_ticks)

    def render_image(self):
        '''Blit everything together in the right order.'''
        # draw map
        self._image.blit(self._map.image, (0, 0))
        # draw units
        self._players.draw(self._image)
        # draw cursors
        self._selection.draw(self._image)
        return self._image

    def cancel_event(self):
        '''Return True if smth was canceled'''
        if self._selection.selected_tile:
            self._selection.unselect()
            return True
        else:
            return False

    def click_event(self, pos):
        '''Deside what to do on mouse click on particular tile.'''
        # TODO: check game rules here e. g. its unit belong to current
        # player
        # TODO: check if player want to attack
        self.mouseover_event(pos)
        pointed = self._selection.pointed_tile
        selected = self._selection.selected_tile
        # if smth selected try to cycle selection
        if selected and pointed == selected:
            # self._cycle_selection() between castle and unit
            # castle menu
            # self._castle_menu()
            pass
        # try to move if reachable
        elif selected and self._selection.reachable(pointed):
            self._selection.move()
        # try to attack if has enemy unit
        elif selected and pointed.unit not in self._players.current:
            pass
        # try to select
        elif pointed.unit and pointed.unit in self._players.current:
            self._selection.select()
        elif pointed.type is 'castle' \
                and pointed.owner is self._players.current:
            # castle menu
            # self._castle_menu()
            pass

    def mouseover_event(self, pos):
        '''Highlight tile with the mouse.'''
        self._selection.highlight(pos)


class Players(object):
    '''Container for players.'''

    def __init__(self, players):
        self.players = []
        if players:
            self.players = players
            self.current = players[0]

    def add(self, player):
        if not self.players:
            self.current = player
        self.players.append(player)

    def update(self, game_ticks):
        '''Recursive'''
        for player in self.players:
            player.update(game_ticks)

    def draw(self, image):
        '''Recursive'''
        for player in self.players:
            player.draw(image)

    def __getitem__(self, i):
        return self.players[i]

class Player(pygame.sprite.RenderUpdates):
    '''Container for units.'''

    def __init__(self, name):
        super(Player, self).__init__()
        self.name = name


class Selection():
    """Object responsible for selection of tiles."""

    def __init__(self, _map, players):
        self._map = _map
        self._players = players
        self._green_image = utils.load_image('selection_green_bold.png')
        self._orange_image = utils.load_image('selection_orange_bold.png')
        self._red_image = utils.load_image('selection_red_bold.png')
        self._target_image = utils.load_image('target.png')
        self._reachable_image = utils.load_image('reachable.png')
        self._reachable_image.set_alpha(123)
        self.pointed_tile = None
        self.selected_tile = None
        self._reachable = None
        self._path = None

    def highlight(self, pos):
        '''Determine tile where mouse points.'''
        new_tile = self._map.tile_at_coord(*pos)
        if new_tile and new_tile != self.pointed_tile:
            self.pointed_tile = new_tile

    def reachable(self, tile):
        '''Unit can get to that tile in one turn.'''
        if self._reachable:
            return tile in self._reachable

    def select(self):
        '''Immediately view reachable tiles for selected unit.'''
        self._reachable = self._map.get_reachable(self.pointed_tile)
        self.selected_tile = self.pointed_tile

    def _find_path(self):
        orig = self.selected_tile
        dest = self.pointed_tile
        self._path = self._map.find_path(orig, dest)

    def move(self):
        self.selected_tile.unit.move(self._path)
        # unselect tile
        self.selected_tile = None

    def unselect(self):
        self.selected_tile = None

    def draw(self, image):
        if self.pointed_tile:
            # pointing to enemy unit
            if self.selected_tile and self.pointed_tile.unit \
                    and self.pointed_tile.unit not in self._players.current \
                    and self.selected_tile.unit.can_attack(self.pointed_tile.unit):
                image.blit(self._target_image, self.pointed_tile.coord)
            # pointing to reachable tile
            elif self.selected_tile and self.pointed_tile in self._reachable:
                image.blit(self._green_image, self.pointed_tile.coord)
                self._draw_path(image)
            # pointing to unreachable tile
            elif self.selected_tile and self.pointed_tile not in self._reachable:
                image.blit(self._red_image, self.pointed_tile.coord)
            # no tile selected
            else:
                image.blit(self._green_image, self.pointed_tile.coord)
        if self.selected_tile:
            image.blit(self._orange_image, self.selected_tile.coord)
            for tile in self._reachable:
                image.blit(self._reachable_image, tile.coord)

    def _draw_path(self, image):
        '''Draw dots on the map for current path.'''
        self._find_path()
        if self._path.size() < 2:
            _LOGGER.exception("Failed to find path.")
            return
        points = self._path.pixels()
        color = (255, 0, 0)
        pygame.draw.lines(image, color, False, points, 3)

