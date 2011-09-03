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
SCROLL_SPEED = 3

def load_configs():
    _LOGGER.debug('Loading configs')
    from configs import config
    global SCREEN_SIZE
    global TILE_SIZE
    global SCROLL_SPEED
    SCREEN_SIZE = config.graphics['screen_mode']
    TILE_SIZE = config.graphics['tile_size']
    SCROLL_SPEED = config.graphics['scroll_speed']


def load_levels_info():
    '''Format info a little, check for integrity and return levels info.'''
    _LOGGER.debug("Loading levels data")
    from configs.levels import LEVELS
    # transform to more friendly for game format
    # format map from multiline string to 2d array of letters
    levels_info = LEVELS
    for name, level in levels_info.items():
        level['map'] = [list(line.lstrip().rstrip()) for line in level['map'].split('\n')]
        # all rows should be the same size
        for row in level['map']:
            if len(row) != len(level['map'][0]):
                _LOGGER.exception('not all rows in map "%s" have same width', name)
    return levels_info


def load_tile_types():
    '''Return tile types dict read from config file.'''
    _LOGGER.debug("Loading tiles data")
    from configs.tiletypes import TILE_TYPES
    return TILE_TYPES


def load_unit_types(filename='unit_types'):
    '''Return unit types dict read from config file.'''
    _LOGGER.debug("Loading units data")
    from configs.unittypes import UNIT_TYPES
    return UNIT_TYPES


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
    _LOGGER.debug("Creating level image from description")
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
    # border object to substitute for missing boundary cells
    class Border(object):
        def __init__(self):
            self.type = 'border'
    # 4 relevant cells
    N = level[i - 1][j] if i > 0 else Border()
    S = level[i + 1][j] if i < len(level) - 1 else Border()
    W = level[i][j - 1] if j > 0 else Border()
    E = level[i][j + 1] if j < len(level[i]) - 1 else Border()
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
    else:
        name = '1.png'
    full_name = os.path.join(season, 'road', name)
    return load_image(full_name, rotate=rotate)

