#!/usr/bin/env python

"""Contains utility function such as loading images, concatenationg them,
loading and parsing config files.

"""

import os
import logging
import ConfigParser as cparser

import pygame
import pygame.locals as pl
import pygame.transform as pytrans

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-23 15:06:07.704924 "

_LOGGER = logging.getLogger('main.utils')
GAME_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
IMAGES_DIR = os.path.join(GAME_DIR, 'images')
DESCR_DIR = os.path.join(GAME_DIR, 'descr')

# default configs
SCREEN_SIZE = (1280, 720)
TILE_SIZE = 50

def load_configs():
    _LOGGER.debug('Loading configs')
    from conifgs import config
    global SCREEN_SIZE
    global TILE_SIZE
    SCREEN_SIZE = config.graphics['screen_mode']
    TILE_SIZE = config.graphics['tile_size']


def load_levels_info():
    from conifgs import levels
    return levels.get_levels()


def load_tile_types(filename='tile_types', season='summer'):
    '''Return tile types dict read from config file.'''
    tiles_info = _load_config(filename)
    return tiles_info


def load_unit_types(filename='unit_types'):
    '''Return unit types dict read from config file.'''
    units_info = _load_config(filename)
    return units_info


def _load_config(filename, section=None):
    '''Generic function for reading game config files.
    If section is not specified, reads all sections.
    '''
    path = os.path.join(DESCR_DIR, filename)
    config = cparser.RawConfigParser()
    config.read(path)
    sections = {}
    for section in config.sections():
        options = {}
        for option in config.options(section):
            options[option] = config.get(section, option)
        sections[section] = options
    return sections

def load_image(name, colorkey=None, size=(TILE_SIZE, TILE_SIZE), rotate=0):
    '''Load image. Uses red box as fallback.'''
    fullname = os.path.join(IMAGES_DIR, name)
    # if image wasn't found, use red box as fallback
    try:
        image = pygame.image.load(fullname)
        if size:
            image = pytrans.scale(image, size)
        if rotate:
            image = pygame.transform.rotate(image, rotate)
    except pygame.error, message:
        _LOGGER.exception("Can't load image: %s", message)
        image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        image.fill((255, 0, 0, 255))
        colorkey = None
    try:
        # convert for faster blitting
        if os.path.splitext(name)[0] == '.png':
            image = image.convert_alpha()
        else:
            image = image.convert()
    except:
        _LOGGER.exception('pygame not initialized')
    # optionally set transparent color
    # if -1 is passes as color, use first pixel
    if colorkey is not None:
        if colorkey is (-1):
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pl.RLEACCEL)
    return image


def _create_level_image(level, level_info):
    '''Return image of whole level built from tiles.'''
    season = level_info['season']
    tile_width = tile_height = TILE_SIZE
    map_width = len(level[0]) * tile_width
    map_height = len(level) * tile_height
    image = pygame.Surface((map_width, map_height))
    # blit each tile to image
    background = load_image(os.path.join(season,
                                         level_info['background'], '1.png'))
    for i, row in enumerate(level):
        for j, tile in enumerate(row):
            if tile:
                tile_image = None
                # select proper image
                if tile.type == 'road':
                    # select proper road part: crossroad,
                    # straight_road
                    tile_image = select_road_block((i, j), level, season)
                else:
                    name = '1.png'
                    image_name = os.path.join(season, tile.type, name)
                    tile_image = load_image(image_name)
                # blit land image as background
                image.blit(background, tile.coord)
                # blit specific image for tile
                image.blit(tile_image, tile.coord)
    return image


def select_road_block(coords, level, season):
    '''Select proper road part: crossroad, straight road, turn, branch.'''
    name = '1.png'
    rotate = 0
    i, j = coords
    # 5 relevant cells
    N, S, W, E = level[i - 1][j], level[i + 1][j], \
                       level[i][j - 1], level[i][j + 1]
    R = ['road', 'bridge', 'castle', 'house']
    if N.type in R and S.type in R and W.type in R and E.type in R:
        name = 'crossroad.png'
    # branch
    elif N.type in R and W.type in R and S.type in R:
        name = 'branch.png'
    elif E.type in R and S.type in R and W.type in R:
        name = 'branch.png'
        rotate = 90
    elif N.type in R and S.type in R and E.type in R:
        name = 'branch.png'
        rotate = 180
    elif N.type in R and E.type in R and W.type in R:
        name = 'branch.png'
        rotate = 270
    # straight
    elif N.type in R and S.type in R:
        name = 'vertical.png'
    elif W.type in R and E.type in R:
        name = 'horizontal.png'
    # turn
    elif W.type in R and N.type in R:
        name = 'turn.png'
    elif W.type in R and S.type in R:
        name = 'turn.png'
        rotate = 90
    elif S.type in R and E.type in R:
        name = 'turn.png'
        rotate = 180
    elif E.type in R and N.type in R:
        name = 'turn.png'
        rotate = 270
    full_name = os.path.join(season, 'road', name)
    return load_image(full_name, rotate=rotate)

