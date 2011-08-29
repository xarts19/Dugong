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
        self._level = None
        self._image = None
        self._tile_factory = _TileFactory()

    def __repr__(self):
        occupied_tiles = []
        for row in self._level:
            for tile in row:
                if tile.unit:
                    occupied_tiles.append(repr(tile))
        return '\n'.join(occupied_tiles)

    @property
    def image(self):
        '''Return complete map image'''
        return self._image

    def load_level(self, level_info):
        '''Reinitialize map with new level.'''
        self._level = _init_level(level_info['map'], self._tile_factory)
        self._image = utils._create_level_image(self._level, level_info)

    def tile_at_coord(self, x, y):
        '''Return tile object at pixel coords.'''
        i = y / utils.TILE_SIZE
        j = x / utils.TILE_SIZE
        return self.tile_at_pos(i, j)

    def tile_at_pos(self, i, j):
        '''Return tile object at matrix coords.'''
        if len(self._level) > i and len(self._level[i]) > j \
                and i >= 0 and j >= 0:
            return self._level[i][j]
        else:
            # "Accesing tile outside of bounds: (%s, %s)", i, j
            return None

    def get_reachable(self, orig):
        '''Get cell that is reachable in one step by unit at this tile.'''

        def dive(i, j, moves):
            if moves < 0:
                return []
            # this tile is reachable
            reachable = [self.tile_at_pos(i, j)]
            # try each direction
            for di, dj in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                tile = self.tile_at_pos(i + di, j + dj)
                if tile:
                    moves_left = moves - tile.pass_cost
                    if tile.type is not 'water' and not tile.unit and moves_left >= 0:
                        reachable.extend(dive(i + di, j + dj, moves_left))
            return reachable

        # general case
        i, j = orig.pos
        moves = orig.unit.moves_left
        tiles = dive(i, j, moves)

        # flying units
        # swimming units

        # find reachable
        reachable = []
        for tile in tiles:
            if tile != orig and tile not in reachable:
                reachable.append(tile)
        return reachable

    def find_path(self, orig, dest):
        '''Return list of neighbour tiles that unit needs to traverse
        and if path is valid for this unit.
        Orig and dest is included.
        '''

        def find(start_i, start_j, moves, dest):
            '''Breadth first search for path from i, j to dest.'''
            final_path = None
            # add starting tile to fring
            #fringe = [Path(start_i, start_j)]
            fringe = fringe = [([(start_i, start_j)], moves)]
            while len(fringe) > 0:
                path = fringe[0]
                del fringe[0]
                for di, dj in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    i, j = path[0][-1]
                    tile = self.tile_at_pos(i + di, j + dj)
                    if tile:
                        moves_left = path[1] - tile.pass_cost
                        if tile.type is not 'water' and not tile.unit and moves_left >= 0:
                            if tile is dest:
                                final_path = path[0] + [(i + di, j + dj)]
                                fringe = []
                                break
                            fringe.append((path[0]+[(i + di, j + dj)], moves_left))
            return [self.tile_at_pos(i, j) for i, j in final_path]

        moves = orig.unit.moves_left
        path = find(orig.pos[0], orig.pos[1], moves, dest)
        return path

class Path(object):

    def __init__(self, start_tile):
        self.tiles = [start_tile]
        self.pixels = None
        self.cost = None

# helper function for GameMap class
def _init_level(level_map, tile_factory):
    '''Construct 2d array of Tiles from 2d array of tile types.'''
    level = []
    # create tiles from level definition
    for i, row in enumerate(level_map):
        tile_row = []
        for j, tile_type in enumerate(row):
            tile_row.append(tile_factory.create_tile(tile_type, (i, j)))
        level.append(tile_row)
    return level


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
        if tile_type not in tile_types:
            _LOGGER.exception("No such tile type: %s", tile_type)
            return None

        # init info from type
        type_info = tile_types[tile_type]
        tile_type = type_info['name']
        defence = int(type_info['defence'])
        pass_cost = float(type_info['pass_cost'])
        heal = int(type_info['heal'])
        # create tile
        tile = Tile(tile_type, defence, pass_cost, heal, pos)
        return tile


class Tile(object):
    '''Single game tile. Stores attributes and image.'''

    def __init__(self, tile_type, defence, pass_cost, heal, pos):
        self.type = tile_type
        self.defence = defence
        self.pass_cost = pass_cost
        self.heal = heal
        self._owner = None
        self._pos = pos
        self._coord = pos[1] * utils.TILE_SIZE, pos[0] * utils.TILE_SIZE
        self._unit = None

    def __repr__(self):
        return "Tile at (%s, %s)" % self._pos

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
        if value is not None and self.unit:
            _LOGGER.exception("Tile at %s already occupied.", self.pos)
        self._unit = value

    @property
    def pos(self):
        return self._pos

    @property
    def coord(self):
        return self._coord



