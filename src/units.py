#!/usr/bin/env python

"""Auto-generated file

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-23 15:04:59.084491 "

import pygame

import utils

class Unit(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = utils.load_image("swordsman.png", -1)
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)


