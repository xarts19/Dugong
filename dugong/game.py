#!/usr/bin/env python

"""
All game logic and constraints is here.
"""

import logging
import random

import pygame
import pygame.locals as pl

import gamemap
import units
import utils
import mapimagegen


__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-23 16:18:33.633299 "

LOGGER = logging.getLogger('main.game')

class Game(object):
    '''Represents current game state.'''

    def __init__(self, level_info):
        LOGGER.debug('Initializing game map')
        self._unit_factory = units.UnitFactory()
        self.players = Players([])
        # create map
        self.map = gamemap.GameMap(level_info)
        self.selection = Selection(self.map, self.players)
        # load units
        for i, units_info in enumerate(level_info['units']):
            player = Player(str(i))
            self.players.add(player)
            self._init_units(units_info, player)

    def _init_units(self, units, player):
        '''Create units from level specs for given player.'''
        for unit_type, i, j in units:
            self._add_unit(unit_type, player, self.map.tile_at_pos(i, j))

    def _add_unit(self, unit_type, player, tile):
        '''Add unit to tile, _units and player'''
        unit = self._unit_factory.create_unit(unit_type, tile, player)
        if unit:
            tile.unit = unit
            tile.owner = player
            player.add(unit)

    def update(self, game_ticks):
        '''Update all sprites.'''
        self.players.update(game_ticks)
        self.selection.update()

    def _attack(self, attacker, attacked):
        '''Compute attack result'''
        damage_to_attacked = attacker.attack(attacked)
        if attacked.is_alive():
            damage_to_attacker = attacked.riposte(attacker)
        else:
            damage_to_attacker = None
        # show cut scene
        self._attack_params = attacker, attacked, damage_to_attacker, damage_to_attacked
        return self._attack_params

    def end_turn(self):
        for unit in self.players.current:
            unit.end_turn()
        self.players.next()
        self.selection.unselect()

    def cancel_event(self):
        '''Return True if smth was canceled'''
        if self.selection.selected_tile:
            self.selection.unselect()
            return True
        else:
            return False

    def click_event(self, pos):
        '''Deside what to do on mouse click on particular tile.'''
        self.mouseover_event(pos)
        # try to select unit
        if self.selection.can_select():
            self.selection.select()
        # try to move if reachable
        elif self.selection.can_move():
            self.selection.move()
            self.selection.unselect()
        # try to attack if has enemy unit
        elif self.selection.can_attack():
            res = self._attack(self.selection.selected_tile.unit,
                               self.selection.pointed_tile.unit)
            self.selection.unselect()
            return 'attack', res
        return None

    def mouseover_event(self, pos):
        '''Highlight tile with the mouse.'''
        return self.selection.highlight(pos)


class Players(object):
    '''Container for players.'''

    def __init__(self, players):
        self.players = []
        self.current = None
        if players:
            self.players = players
            self._cur = 0
            self.current = players[0]

    def add(self, player):
        if not self.players:
            self.current = player
            self._cur = 0
        self.players.append(player)

    def next(self):
        self._cur += 1
        if self._cur == len(self.players):
            self._cur = 0
        self.current = self.players[self._cur]

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

    def update(self, *args):
        for unit in self:
            is_alive = unit.update(*args)
            if not is_alive:
                unit.kill()
                self.remove(unit)


class Selection():
    """Object responsible for selection of tiles."""
    # Selection statuses:
    NOTHING, TARGET, MOVE, SELECT = range(4)

    def __init__(self, _map, players):
        self._map = _map
        self._players = players

        self.pointed_tile = None
        self.status = self.NOTHING
        self.selected_tile = None
        self.reachable = None
        self.attackable = None
        self.path = None

    def update(self):
        if self.pointed_tile:
            # pointing to selectable tile
            if self.can_select():
                self.status = self.SELECT
            # pointing to enemy unit
            elif self.can_attack():
                self.status = self.TARGET
            # pointing to reachable tile
            elif self.can_move():
                self.status = self.MOVE
            # pointing to unreachable tile
            elif not self.can_move():
                self.status = self.NOTHING

    def highlight(self, pos):
        '''Determine tile where mouse points.'''
        new_tile = self._map.tile_at_pos(*pos)
        if new_tile and new_tile != self.pointed_tile:
            self.pointed_tile = new_tile
            if self.selected_tile:
                self._find_path()
        return self.gather_status_info()

    def can_select(self):
        return (self.pointed_tile and self.pointed_tile.unit \
                    and self.pointed_tile.unit in self._players.current) \
            or (self.pointed_tile.type == 'castle' \
                    and self.pointed_tile.owner is self._players.current)

    def can_attack(self):
        return self.selected_tile and self.pointed_tile.unit \
            and self.selected_tile.unit.can_attack(self.pointed_tile.unit)

    def can_move(self):
        return self.selected_tile and self._is_reachable(self.pointed_tile)

    def _is_reachable(self, tile):
        '''Unit can get to that tile in one turn.'''
        if self.reachable:
            return tile in self.reachable
        else:
            return False

    def select(self):
        '''Immediately view reachable tiles for selected unit.'''
        # self._cycle_selection() between castle and unit if
        # selectiong same tile
        self.reachable = self._map.get_reachable(self.pointed_tile)
        self.attackable = self._map.get_attackable(self.pointed_tile)
        self.selected_tile = self.pointed_tile

    def _find_path(self):
        orig = self.selected_tile
        dest = self.pointed_tile
        self.path = self._map.find_path(orig, dest)

    def move(self):
        self.selected_tile.unit.move(self.path)

    def unselect(self):
        self.selected_tile = None

    def gather_status_info(self):
        info = {}
        info['player'] = self._players.current
        if self.pointed_tile:
            info['unit'] = self.pointed_tile.unit
            info['tile'] = self.pointed_tile
        else:
            info['unit'] = None
            info['tile'] = None
        return info


class GameRenderer(object):

    def __init__(self, game_instance, metrics):
        self.game = game_instance
        self.metrics = metrics
        level, level_info = self.game.map.get_info()
        self.map_image = mapimagegen.create_level_image(level, level_info, metrics)
        self.image = pygame.Surface(self.map_image.get_size())

        self._green_image = utils.RES_MANAGER.get('selection_green_bold.png')
        self._orange_image = utils.RES_MANAGER.get('selection_orange_bold.png')
        self._red_image = utils.RES_MANAGER.get('selection_red_bold.png')
        self._target_image = utils.RES_MANAGER.get('target.png')
        self._reachable_image = utils.RES_MANAGER.get('reachable.png')
        self._reachable_image.set_alpha(100)
        self._attackable_image = utils.RES_MANAGER.get('attackable.png')
        self._attackable_image.set_alpha(100)

    def get_size(self):
        return self.image.get_size()

    def render(self):
        '''Blit everything together in the right order.'''
        # draw map
        self.image.blit(self.map_image, (0, 0))
        # draw units
        for player in self.game.players:
            for unit in player:
                unit.renderer.render(self.image, self.metrics.tiles_to_pixels)
        # draw cursors
        self.draw_selection(self.image)
        return self.image

    def draw_selection(self, image):
        sel = self.game.selection
        p_t = sel.pointed_tile
        s_t = sel.selected_tile
        if p_t:
            p_t_c = self.metrics.tiles_to_pixels(p_t.pos)
            if sel.status == sel.NOTHING:
                image.blit(self._red_image, p_t_c)
            elif sel.status == sel.TARGET:
                image.blit(self._target_image, p_t_c)
            elif sel.status == sel.SELECT:
                image.blit(self._green_image, p_t_c)
            elif sel.status == sel.MOVE:
                image.blit(self._green_image, p_t_c)
                self.draw_path(image)
        if s_t:
            s_t_c = self.metrics.tiles_to_pixels(s_t.pos)
            image.blit(self._orange_image, s_t_c)
            for tile in sel.reachable:
                c = self.metrics.tiles_to_pixels(tile.pos)
                image.blit(self._reachable_image, c)
            for tile in sel.attackable:
                c = self.metrics.tiles_to_pixels(tile.pos)
                image.blit(self._attackable_image, c)

    def draw_path(self, image):
        '''Draw dots on the map for current path.'''
        path = self.game.selection.path
        if path.size() < 2:
            return
        points = self.pixels(path.tiles)
        color = (255, 0, 0)
        pygame.draw.lines(image, color, False, points, 3)

    def pixels(self, tiles):
        '''List of coords of pixels of each tile in path.'''
        return [[v + utils.TILE_SIZE / 2 for v in self.metrics.tiles_to_pixels(tile.pos)]
                                         for tile in tiles]


