#!/usr/bin/env python

"""
Creates map image given map definition.
"""

import logging

import pygame

import os
import utils
from utils import RES_MANAGER

_LOGGER = logging.getLogger('main.mapimagegen')

def create_level_image(level, level_info):
    '''Return image of whole level built from tiles.'''
    _LOGGER.debug("Creating level image from description")
    season = level_info['season']
    tile_width = tile_height = utils.TILE_SIZE
    map_width = len(level[0]) * tile_width
    map_height = len(level) * tile_height
    image = pygame.Surface((map_width, map_height))
    # blit each tile to image
    background = RES_MANAGER.get(':'.join([season,
                                         level_info['background'], 'default.png']))
    for i, row in enumerate(level):
        for j, tile in enumerate(row):
            if tile:
                tile_image = None
                # select proper image
                if tile.type == 'road':
                    # select proper road part: crossroad,
                    # straight_road
                    tile_image = select_road_block((i, j), level, season)
                elif tile.type == 'water':
                    tile_image = select_water_block((i, j), level, season)
                elif tile.type == 'bridge':
                    tile_image = select_bridge_block((i, j), level, season)
                else:
                    name = 'default.png'
                    image_name = ':'.join([season, tile.type, name])
                    tile_image = RES_MANAGER.get(image_name)
                # blit land image as background
                image.blit(background, tile.coord)
                # blit specific image for tile
                image.blit(tile_image, tile.coord)
    return image


def select_road_block(coords, level, season):
    '''Select proper road part: crossroad, straight road, turn, branch.'''
    name = 'default.png'
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
    R = ['road', 'bridge', 'castle', 'house', 'border']
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
    full_name = ':'.join([season, 'road', name])
    return RES_MANAGER.get(full_name, rotate=rotate)


def select_water_block(coords, level, season):
    name = 'default.png'
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
    R = ['water', 'bridge', 'border']
    if N.type in R and S.type in R and W.type in R and E.type in R:
        name = 'open.png'
    elif W.type in R and S.type in R and N.type in R:
        name = 'shore.png'
    elif W.type in R and E.type in R and S.type in R:
        name = 'shore.png'
        rotate = 90
    elif S.type in R and E.type in R and N.type in R:
        name = 'shore.png'
        rotate = 180
    elif W.type in R and E.type in R and N.type in R:
        name = 'shore.png'
        rotate = 270
    elif W.type in R and S.type in R:
        name = 'bay.png'
    elif E.type in R and S.type in R:
        name = 'bay.png'
        rotate = 90
    elif E.type in R and N.type in R:
        name = 'bay.png'
        rotate = 180
    elif W.type in R and N.type in R:
        name = 'bay.png'
        rotate = 270
    elif N.type in R and S.type in R:
        name = 'river.png'
    elif W.type in R and E.type in R:
        name = 'river.png'
        rotate = 90
    full_name = ':'.join([season, 'water', name])
    return RES_MANAGER.get(full_name, rotate=rotate)


def select_bridge_block(coords, level, season):
    name = 'default.png'
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
    R = ['road', 'bridge', 'border']
    if W.type in R and E.type in R:
        name = 'default.png'
        rotate = 0
    elif N.type in R and S.type in R:
        name = 'default.png'
        rotate = 90
    full_name = ':'.join([season, 'bridge', name])
    return RES_MANAGER.get(full_name, rotate=rotate)

