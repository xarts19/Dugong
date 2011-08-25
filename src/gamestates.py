#!/usr/bin/env python

"""Auto-generated file

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-25 16:01:50.179836 "

import gamemap
import units
import game
import utils

import pygame
import pygame.locals as pl

class GameStateManager(object):

    def __init__(self):
        self._states = {"MainMenu" : _MainMenu(self),
                            "Game" : _Game(self),
                      "InGameMenu" : _InGameMenu(self),
                       }
        self.state = "MainMenu"

    def handle_events(self, events):
        return self._states[self.state].handle_events(events)

    def get_rendered_screen(self, size=None):
        if size is None:
            size = utils.SCREEN_SIZE
        self._states[self.state].update()
        image = None
        if self.state == "InGameMenu":
            game_image = self._states["Game"].get_image(size)
            menu_image = self._states["InGameMenu"].get_image(size)
            menu_image.set_alpha(200)
            game_image.blit(menu_image, (0, 0))
            image = game_image
        else:
            image = self._states[self.state].get_image(size)
        return image


class _MainMenu(object):

    def __init__(self, state_manager):
        self._state_manager = state_manager
        self._image = pygame.Surface(utils.SCREEN_SIZE)

    def handle_events(self, events):
        # poll for pygame events
        for event in events:
            if event.type == pl.QUIT:
                return False
        # XXX: redirect to game
        self._state_manager.state = "Game"
        return True

    def update(self):
        pass

    def get_image(self, size):
        return self._image


class _Game(object):

    def __init__(self, state_manager):
        self._state_manager = state_manager
        self._image = pygame.Surface(utils.SCREEN_SIZE)
        self._init_game()

    def _init_game(self):
        self._map = gamemap.GameMap()
        self._selection = game.Selection(self._map)
        self._game = game.Game(self._map, self._selection)
        self._allsprites = pygame.sprite.RenderUpdates(self._game.units)

    def handle_events(self, events):
        """Return false to stop the event loop and end the game."""

        # poll for pygame events
        for event in events:
            if event.type == pl.QUIT:
                self._state_manager.state = "InGameMenu"

            # handle user input
            elif event.type == pl.MOUSEBUTTONUP:
                self._selection.select_or_move(pygame.mouse.get_pos())
            elif event.type == pl.KEYDOWN:
                if event.key == pl.K_ESCAPE:
                    self._selection.unselect()
                else:
                    self._state_manager.state = "InGameMenu"
        return True

    def update(self):
        #
        self._render_image()

    def _render_image(self):
        # TODO: add some background image here
        self._image.fill((255, 225, 255))
        # draw map
        self._image.blit(self._map.image, (0, 0))
        # update units and draw them
        self.draw_units(self._image)
        # draw cursors
        self.draw_selections(self._image)

    def draw_units(self, image):
        self._allsprites.empty()
        self._allsprites.add(self._game.units)
        self._allsprites.update(pygame.time.get_ticks())
        self._allsprites.draw(image)

    def draw_selections(self, image):
        '''Draw selection on the block that mouse points to and currently selected block.'''
        self._selection.mouse(pygame.mouse.get_pos())
        self._selection.draw(image)


    def get_image(self, size):
        # TODO: handle screen resolutions
        return self._image


class _InGameMenu(object):

    def __init__(self, state_manager):
        self._state_manager = state_manager

    def update(self):
        pass

    def get_image(self, size):
        return None

