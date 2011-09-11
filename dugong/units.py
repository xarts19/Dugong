#!/usr/bin/env python

"""Auto-generated file

"""

import sys
import logging
import random

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
        self._unit_types = utils.RES_MANAGER.get('unit_types')

    def create_unit(self, unit_type, tile, owner=None):
        '''Returns tile instance with attributes for provided type.'''
        unit_types = self._unit_types

        # check if such type exist
        if unit_type not in unit_types:
            _LOGGER.exception("No such unit type: %s", unit_type)
            return None

        # init info from type
        type_info = unit_types[unit_type]

        renderer_class = getattr(sys.modules[__name__], unit_type.capitalize() + 'Renderer', UnitRenderer)
        unit_class = getattr(sys.modules[__name__], unit_type.capitalize(), Unit)
        unit = unit_class(unit_type, type_info, renderer_class, tile, owner)
        return unit


class Unit(pygame.sprite.Sprite):

    def __init__(self, unit_type, type_info, renderer_class, tile, owner):
        super(Unit, self).__init__()
        self.type = unit_type
        self.owner = owner
        self.tile = tile
        self._set_tile_owner()
        self.renderer = renderer_class(self)
        self.moves_left = type_info['max_moves']
        self.max_moves = type_info['max_moves']
        self._max_attacks = 1
        self._attacks = 1
        self._range = type_info['range']
        self.health = 100
        self.attack_damage = type_info['attack']
        self.defence = type_info['defence']
        _LOGGER.debug("Unit created: %s", self)

    def __repr__(self):
        return "<%s at %s>" % (self._type, self._tile)

    def can_attack(self, unit):
        in_range = self.tile.distance(unit.tile) <= self._range
        has_attacks = self._attacks > 0
        is_enemy = unit.owner is not self.owner
        return in_range and has_attacks and is_enemy

    def riposte(self, unit):
        '''Returns damage done or None if can't attack.'''
        if self.tile.distance(unit.tile) > 1:
            return None
        return self.attack(unit, riposte=True)

    def attack(self, unit, riposte=False):
        if not riposte:
            self._attacks -= 1
            self.moves_left = 0
        damage = random.choice(range(*self.attack_damage)) * (self.health / 100.0)
        damage_done = max(0, damage - unit.defence - unit.tile.defence)
        unit.apply_damage(damage_done)
        return damage_done

    def apply_damage(self, damage):
        self.health -= int(damage)

    def is_alive(self):
        return self.health > 0

    def kill(self):
        self.tile.unit = None
        _LOGGER.debug("Unit killed: %s", self)

    def end_turn(self):
        self.moves_left = self.max_moves
        self._attacks = self._max_attacks

    def get_pass_cost(self, tile):
        if tile.type == 'water' or tile.unit:
            return 100
        else:
            return tile.pass_cost

    def _set_tile_owner(self):
        self.tile.owner = self.owner

    def update(self, game_ticks):
        '''Redirect call to animated image.'''
        self.renderer.update(game_ticks)
        return self.is_alive()

    def move(self, path):
        self.moves_left -= path.cost
        dest = path.end()
        self.renderer.move(path)
        # remove unit from old tile
        self.tile.unit = None
        # assign new tile to unit
        self.tile = dest
        # assign new unit to tile
        dest.unit = self


class Catapult(Unit):

    def __init__(self, *args):
        super(Catapult, self).__init__(*args)

    def can_attack(self, unit):
        return super(Catapult, self).can_attack(unit) and self.tile.distance(unit.tile) > 1


class UnitRenderer(object):

    def __init__(self, unit):
        self.unit = unit
        self._orig = StaticImage(utils.RES_MANAGER.get(unit.type + '.png'), unit.tile.pos)
        self.image = self._orig
        self.font = utils.Writer(10, (255, 0, 0))

    def update(self, ticks):
        if isinstance(self.image, StaticImage):
            return
        elif isinstance(self.image, AnimatedImage) and self.image.animated:
            self.image.update(ticks)
        else:
            self.image = self._orig

    def render(self, image, to_pixels_fnc):
        pos = to_pixels_fnc(self.image.get_pos())
        image.blit(self.image.get(), pos)
        image.blit(self.font.render(str(self.unit.health)), pos)

    def move(self, path):
        self.image.set_pos(path.end().pos)
        path = create_pixel_path(path)
        self.image = AnimatedImage([self.image.get()], path)

class StaticImage(object):

    def __init__(self, image, pos):
        self.image = image
        self.pos = pos

    def get(self):
        return self.image

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

class AnimatedImage(object):
    '''Used by units to store image with ability to start traversing
    given path and animate.
    '''

    def __init__(self, animation, path):
        self._images = animation
        self._current = animation[0]
        self._path = path
        self._pos = path['path'][0]
        self.animated = True
        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self._anim_delay = 250   # in milliseconds
        self._move_delay = 20
        self._anim_update = 0
        self._move_update = 0
        self._frame = 0
        self.update(0)

    def update(self, t):
        if self.animated:
            if t - self._anim_update > self._anim_delay:
                # animate image
                self._frame += 1
                if self._frame >= len(self._images):
                    self._frame = 0
                self._current = self._images[self._frame]
                self._anim_update = t
            if t - self._move_update > self._move_delay:
                # move image
                if self._path['current'] == len(self._path['path']) - 1:
                    self._pos = self._path['path'][-1]
                    self.animated = False
                else:
                    self._path['current'] += 1
                    self._pos = self._path['path'][self._path['current']]
                self._move_update = t

    def get(self):
        return self._current

    def get_pos(self):
        return self._pos


def create_pixel_path(path):
    '''Create path in pixels from path in tiles.'''
    pixel_path = {'current': 0, 'path': []}
    path = straighten_path(path.tiles)
    for tile1, tile2 in zip(path[:-1], path[1:]):
        x1, y1 = tile1.pos
        x2, y2 = tile2.pos
        # WARNINIG: alg works only for 20 steps
        l_x = (x2 - x1) / 100.0
        l_y = (y2 - y1) / 100.0
        for i in range(20):
            delta = abs(abs(i - 10) - 10)
            x1 += delta * l_x
            y1 += delta * l_y
            pixel_path['path'].append((x1, y1))
    pixel_path['path'].append(path[-1].pos)
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

