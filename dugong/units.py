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

    def create_unit(self, unit_type, tile, owner=None):
        '''Returns tile instance with attributes for provided type.'''
        unit_types = self._unit_types

        # check if such type exist
        if unit_type not in unit_types:
            _LOGGER.exception("No such unit type: %s", unit_type)
            return None

        # init info from type
        type_info = unit_types[unit_type]

        image = utils.load_image(unit_type + '.png')
        if 'animation' in type_info:
            images = map(load_image, options['animation'].split(','))
        else:
            images = [image]
        unit_class = getattr(sys.modules[__name__], unit_type.capitalize(), Unit)
        unit = unit_class(unit_type, type_info, image, images, tile, owner)
        return unit


class Unit(pygame.sprite.Sprite):

    def __init__(self, unit_type, type_info, image, images, tile, owner):
        super(Unit, self).__init__()
        self._type = unit_type
        self._owner = owner
        self._tile = tile
        self._set_tile_owner()
        self._image = AnimatedImage(static=image, animated=images,
                                          coord=tile.coord)
        self.rect = self._image.get_rect()
        self.moves_left = type_info['max_moves']
        self.max_moves = type_info['max_moves']
        self.max_attacks = 1
        self.attacks = 1
        self.range = type_info['range']
        self.health = 100
        self.attack = type_info['attack']
        self.defence = type_info['defence']

    def __repr__(self):
        return "<%s at %s>" % (self._type, self._tile)

    def can_attack(self, unit):
        i, j = self.tile.pos
        i_2, j_2 = unit.tile.pos
        return abs(i - i_2) + abs(j - j_2) <= self.range and self.attacks > 0

    @property
    def image(self):
        return self._image()

    @property
    def tile(self):
        return self._tile

    @tile.setter
    def tile(self, value):
        self._tile = value

    def get_pass_cost(self, tile):
        if tile.type == 'water':
            return 100
        else:
            return tile.pass_cost

    def _set_tile_owner(self):
        self._tile.owner = self._owner

    def update(self, game_ticks):
        '''Redirect call to animated image.'''
        self._image.update(game_ticks)
        self._image.health = self.health
        self.rect = self._image.get_rect()

    def move(self, path):
        self.moves_left -= path.cost
        dest = path.end()
        self._image.start_animation(path)
        # remove unit from old tile
        self.tile.unit = None
        # assign new tile to unit
        self.tile = dest
        # assign new unit to tile
        dest.unit = self

    def end_turn(self):
        self.moves_left = self.max_moves
        self.attacks = self.max_attacks


class Catapult(Unit):

    def __init__(self, *args):
        super(Catapult, self).__init__(*args)

    def can_attack(self, unit):
        i, j = self.tile.pos
        i_2, j_2 = unit.tile.pos
        return 1 < abs(i - i_2) + abs(j - j_2) <= self.range and self.attacks > 0


class AnimatedImage(object):
    '''Used by units to store image with ability to start traversing
    given path and animate.
    '''

    def __init__(self, static, animated, coord):
        self._font = utils.Writer(10, (255, 0, 0))
        self._image = static
        self._images = animated
        self._current = self._image
        self._animated = False
        self._rect = self._image.get_rect()
        self._rect.topleft = coord
        self.health = 100

    def __call__(self):
        return self._current, self._font.render(str(self.health))

    def get_rect(self):
        return self._rect

    def update(self, t):
        if self._animated:
            if t - self._last_update > self._delay:
                # animate image
                self._frame += 1
                if self._frame >= len(self._images):
                    self._frame = 0
                self._current = self._images[self._frame]
                # move image
                if self._path['current'] == len(self._path['path']) - 1:
                    self._rect.topleft = self._path['path'][-1]
                    self.stop_animation()
                else:
                    self._path['current'] += 1
                    self._rect.topleft = self._path['path'][self._path['current']]
                self._last_update = t
        else:
            self._current = self._image

    def start_animation(self, path, fps=60):
        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self._animated = True
        self._path = create_pixel_path(path)
        self._current = self._images[0]
        #self._start = pygame.time.get_ticks()
        self._delay = 1000 / fps
        self._last_update = 0
        self._frame = 0
        self.update(pygame.time.get_ticks())

    def stop_animation(self):
        self._animated = False


def create_pixel_path(path):
    '''Create path in pixels from path in tiles.'''
    pixel_path = {'current': 0, 'path': []}
    path = straighten_path(path.tiles)
    for tile1, tile2 in zip(path[:-1], path[1:]):
        x1, y1 = tile1.coord
        x2, y2 = tile2.coord
        # WARNINIG: alg works only for 20 steps
        l_x = (x2 - x1) / 100.0
        l_y = (y2 - y1) / 100.0
        for i in range(20):
            delta = abs(abs(i - 10) - 10)
            x1 += delta * l_x
            y1 += delta * l_y
            pixel_path['path'].append((x1, y1))
    pixel_path['path'].append(path[-1].coord)
    return pixel_path


def straighten_path(path):
    '''Join straight segments of the path.'''
    straight_path = [path[0]]
    i = 0
    j = 1
    while j + 1 < len(path):
        x1, y1 = path[i].pos
        x2, y2 = path[j].pos
        x3, y3 = path[j + 1].pos
        if x1 == x2 == x3 or y1 == y2 == y3:
            j += 1
        else:
            straight_path.append(path[j])
            i = j
            j += 1
    straight_path.append(path[-1])
    return straight_path
