#!/usr/bin/env python

"""
Creates map image given map definition.
"""

import logging

import pygame

import os
import utils
from utils import RES_MANAGER

LOGGER = logging.getLogger('main.mapimagegen')

def create_level_image(level, level_info, metrics):
    '''Return image of whole level built from tiles.'''
    LOGGER.debug("Creating level image from description")
    season = level_info['season']
    map_width = len(level[0]) * utils.TILE_SIZE
    map_height = len(level) * utils.TILE_SIZE
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
                image.blit(background, metrics.tiles_to_pixels(tile.pos))
                # blit specific image for tile
                image.blit(tile_image, metrics.tiles_to_pixels(tile.pos))
    return image


def select_road_block(coords, level, season):
    '''Select proper road part: crossroad, straight road, turn, branch.'''
    name = 'default.png'
    rotate = 0
    i, j = coords
    # 4 relevant cells
    N = level[i - 1][j].type if i > 0 else 'border'
    S = level[i + 1][j].type if i < len(level) - 1 else 'border'
    W = level[i][j - 1].type if j > 0 else 'border'
    E = level[i][j + 1].type if j < len(level[i]) - 1 else 'border'
    R = ['road', 'bridge', 'castle', 'house', 'border']
    if sides_match([N, S, W, E], [], R):
        name = 'crossroad.png'
    # branch
    elif sides_match([N, S, W], [E], R):
        name = 'branch.png'
    elif sides_match([E, S, W], [N], R):
        name = 'branch.png'
        rotate = 90
    elif sides_match([N, S, E], [W], R):
        name = 'branch.png'
        rotate = 180
    elif sides_match([N, E, W], [S], R):
        name = 'branch.png'
        rotate = 270
    # straight
    elif sides_match([N, S], [W, E], R):
        name = 'vertical.png'
    elif sides_match([W, E], [N, S], R):
        name = 'horizontal.png'
    # turn
    elif sides_match([W, N], [E, S], R):
        name = 'turn.png'
    elif sides_match([W, S], [E, N], R):
        name = 'turn.png'
        rotate = 90
    elif sides_match([S, E], [N, W], R):
        name = 'turn.png'
        rotate = 180
    elif sides_match([E, N], [W, S], R):
        name = 'turn.png'
        rotate = 270
    full_name = ':'.join([season, 'road', name])
    return RES_MANAGER.get(full_name, rotate=rotate)


def select_water_block(coords, level, season):
    name = 'default.png'
    rotate = 0
    i, j = coords
    # 4 relevant cells
    N = level[i - 1][j].type if i > 0 else 'border'
    S = level[i + 1][j].type if i < len(level) - 1 else 'border'
    W = level[i][j - 1].type if j > 0 else 'border'
    E = level[i][j + 1].type if j < len(level[i]) - 1 else 'border'
    R = ['water', 'bridge', 'border']
    if sides_match([N, S, W, E], [], R):
        name = 'open.png'
    elif sides_match([N, S, W], [E], R):
        name = 'shore.png'
    elif sides_match([S, W, E], [N], R):
        name = 'shore.png'
        rotate = 90
    elif sides_match([N, S, E], [W], R):
        name = 'shore.png'
        rotate = 180
    elif sides_match([N, W, E], [S], R):
        name = 'shore.png'
        rotate = 270
    elif sides_match([S, W], [N, E], R):
        name = 'bay.png'
    elif sides_match([S, E], [W, N], R):
        name = 'bay.png'
        rotate = 90
    elif sides_match([N, E], [W, S], R):
        name = 'bay.png'
        rotate = 180
    elif sides_match([N, W], [S, E], R):
        name = 'bay.png'
        rotate = 270
    elif sides_match([N, S], [E, W], R):
        name = 'river.png'
    elif sides_match([W, E], [N, S], R):
        name = 'river.png'
        rotate = 90
    full_name = ':'.join([season, 'water', name])
    return RES_MANAGER.get(full_name, rotate=rotate)


def select_bridge_block(coords, level, season):
    name = 'default.png'
    rotate = 0
    i, j = coords
    # 4 relevant cells
    N = level[i - 1][j].type if i > 0 else 'border'
    S = level[i + 1][j].type if i < len(level) - 1 else 'border'
    W = level[i][j - 1].type if j > 0 else 'border'
    E = level[i][j + 1].type if j < len(level[i]) - 1 else 'border'
    R = ['road', 'bridge', 'border']
    if sides_match([W, E], [N, S], R):
        name = 'default.png'
        rotate = 0
    elif sides_match([N, S], [W, E], R):
        name = 'default.png'
        rotate = 90
    full_name = ':'.join([season, 'bridge', name])
    return RES_MANAGER.get(full_name, rotate=rotate)

def sides_match(matched, unmatched, match_list):
    matched_corresponds = all([t in match_list for t in matched])
    unmatched_corresponds = not any([t in match_list for t in unmatched])
    return unmatched_corresponds and matched_corresponds

