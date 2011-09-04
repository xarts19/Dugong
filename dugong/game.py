#!/usr/bin/env python

"""
All game logic and constraints is here.
"""

import logging

import random
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

    def __init__(self, level_info):
        _LOGGER.debug('Initializing game map')
        self._unit_factory = units.UnitFactory()
        self._players = Players([])
        # create map
        self._map = gamemap.GameMap(level_info)
        self._selection = Selection(self._map, self._players)
        self._image = pygame.Surface(self.get_map_size())
        # load units
        for i, units_info in enumerate(level_info['units']):
            player = Player(str(i))
            self._players.add(player)
            self._init_units(units_info, player)

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

    def kill_unit(self, unit):
        unit.tile.unit = None
        self._players.kill(unit)
        _LOGGER.debug("Unit killed: %s", unit)

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

    def _attack(self, attacker, attacked):
        '''Compute attack result'''
        # check attack type
        melee = True
        if abs(attacker.tile.pos[0] - attacked.tile.pos[0]) \
                + abs(attacker.tile.pos[1] - attacked.tile.pos[1]) > 1:
            melee = False
        # calculate damage to attacked
        damage = int(random.choice(range(*attacker.attack)) * (attacker.health / 100.0))
        damage_to_attacked = max(0, damage - attacked.defence - attacked.tile.defence)
        if melee and attacked.health - damage_to_attacked > 0:
            # calculate damage to attacker
            damage = int(random.choice(range(*attacked.attack)) \
                * (attacked.health - damage_to_attacked) / 100.0)
            damage_to_attacker = max(0, damage - attacker.defence - attacker.tile.defence)
        else:
            damage_to_attacker = 0
        attacker.attackes -= 1
        attacker.moves_left = 0
        # show cut scene
        self._attack_params = melee, attacker, attacked, damage_to_attacker, damage_to_attacked
        return self._attack_params

    def finish_attack(self):
        melee, attacker, attacked, damage_to_attacker, damage_to_attacked = self._attack_params
        attacked.health -= damage_to_attacked
        if attacked.health <= 0:
            self.kill_unit(attacked)
        if melee:
            attacker.health -= damage_to_attacker
            if attacker.health <= 0:
                self.kill_unit(attacker)

    def cancel_event(self):
        '''Return True if smth was canceled'''
        if self._selection.selected_tile:
            self._selection.unselect()
            return True
        else:
            return False

    def click_event(self, pos):
        '''Deside what to do on mouse click on particular tile.'''
        self.mouseover_event(pos)
        # try to select unit
        if self._selection.can_select():
            self._selection.select()
        # try to move if reachable
        elif self._selection.can_move():
            self._selection.move()
            self._selection.unselect()
        # try to attack if has enemy unit
        elif self._selection.can_attack():
            res = self._attack(self._selection.selected_tile.unit,
                               self._selection.pointed_tile.unit)
            self._selection.unselect()
            return 'attack', res
        return None

    def mouseover_event(self, pos):
        '''Highlight tile with the mouse.'''
        return self._selection.highlight(pos)


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

    def kill(self, unit):
        for player in self.players:
            player.remove(unit)

class Player(pygame.sprite.RenderUpdates):
    '''Container for units.'''

    def __init__(self, name):
        super(Player, self).__init__()
        self.name = name

    def draw(self, surf):
        for sprite in self:
             image = sprite.image
             rect = sprite.rect
             if isinstance(image, (list, tuple,)):
                 for i in image:
                     surf.blit(i, rect)
             else:
                 surf.blit(image, rect)


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
        return self.gather_status_info()

    def can_select(self):
        return (self.pointed_tile and self.pointed_tile.unit \
                    and self.pointed_tile.unit in self._players.current) \
            or (self.pointed_tile.type == 'castle' \
                    and self.pointed_tile.owner is self._players.current)

    def can_attack(self):
        return self.selected_tile and self.pointed_tile.unit \
            and self.pointed_tile.unit not in self._players.current \
            and self.selected_tile.unit.can_attack(self.pointed_tile.unit)

    def can_move(self):
        return self.selected_tile and self.reachable(self.pointed_tile)

    def reachable(self, tile):
        '''Unit can get to that tile in one turn.'''
        if self._reachable:
            return tile in self._reachable
        else:
            return False

    def select(self):
        '''Immediately view reachable tiles for selected unit.'''
        # self._cycle_selection() between castle and unit if
        # selectiong same tile
        self._reachable = self._map.get_reachable(self.pointed_tile)
        self.selected_tile = self.pointed_tile

    def _find_path(self):
        orig = self.selected_tile
        dest = self.pointed_tile
        self._path = self._map.find_path(orig, dest)

    def move(self):
        self.selected_tile.unit.move(self._path)

    def unselect(self):
        self.selected_tile = None

    def draw(self, image):
        if self.pointed_tile:
            if self.can_select():
                image.blit(self._green_image, self.pointed_tile.coord)
            # pointing to enemy unit
            elif self.can_attack():
                image.blit(self._target_image, self.pointed_tile.coord)
            # pointing to reachable tile
            elif self.can_move():
                image.blit(self._green_image, self.pointed_tile.coord)
                self._draw_path(image)
            # pointing to unreachable tile
            elif not self.can_move():
                image.blit(self._red_image, self.pointed_tile.coord)
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

    def gather_status_info(self):
        info = {}
        info['player'] = self._players.current.name
        info['unit'] = self.pointed_tile.unit
        info['tile'] = self.pointed_tile
        return info

