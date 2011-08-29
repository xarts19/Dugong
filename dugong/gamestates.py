#!/usr/bin/env python

"""Auto-generated file

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-25 16:01:50.179836 "

import logging

import pygame
import pygame.locals as pl
MOUSE_LEFT = 1

import gamemap
import units
import game
import utils

_LOGGER = logging.getLogger('main.gamestates')

class GameStateManager(object):

    def __init__(self):
        self._states = {"MainMenu" : _MainMenu(self),
                            "Game" : _Game(self),
                      "InGameMenu" : _InGameMenu(self),
                       }
        self.state = "MainMenu"
        self._menu_transition = 0

    def handle_events(self, events):
        return self._states[self.state].handle_events(events)

    def get_rendered_screen(self):
        self._states[self.state].update()
        image = self._transition()
        if not image:
            image = self._states[self.state].get_image()
        return image

    def _transition(self):
        '''Cool transition effect.'''
        if self.state == "InGameMenu" and self._menu_transition < 32:
            if self._menu_transition < 31:
                self._menu_transition += 1
            game_image = self._states["Game"].get_image()
            menu_image = self._states["InGameMenu"].get_image()
            game_image.set_alpha(255 - self._menu_transition * 5)
            menu_image.set_alpha(self._menu_transition * 6)
        elif self.state == "Game" and self._menu_transition > 0:
            self._menu_transition -= 1
            game_image = self._states["Game"].get_image()
            menu_image = self._states["InGameMenu"].get_image()
            game_image.set_alpha(255 - self._menu_transition * 5)
            menu_image.set_alpha(self._menu_transition * 6)
        else:
            return None
        image = pygame.Surface(utils.SCREEN_SIZE)
        image.blit(game_image, (0, 0))
        image.blit(menu_image, (0, 0))
        return image

class _MainMenu(object):

    def __init__(self, state_manager):
        _LOGGER.debug("Creating main menu")
        self._state_manager = state_manager
        self._init_graphics()

    def _init_graphics(self):
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

    def get_image(self):
        return self._image


class _Game(object):

    def __init__(self, state_manager):
        _LOGGER.debug("Creating game")
        self._state_manager = state_manager
        self._init_game()
        self._init_graphics()

    def _init_game(self):
        self._game = game.Game()


    def _init_graphics(self):
        self._background = utils.load_image('game_background.jpg',
                                            size=utils.SCREEN_SIZE)
        # calculate map shift from the edge of the screen
        size = utils.SCREEN_SIZE
        w, h = self._game.get_map_size()
        self._shift = (size[0] - w) / 2, (size[1] - h) / 2

    def handle_events(self, events):
        """Return false to stop the event loop and end the game."""
        for event in events:
            if event.type == pl.QUIT:
                self._state_manager.state = "InGameMenu"
            elif event.type == pl.MOUSEBUTTONUP:
                if event.button == MOUSE_LEFT:
                    self._game.click_event(self._to_map_coords(pygame.mouse.get_pos()))
            elif event.type == pl.KEYDOWN:
                if event.key == pl.K_ESCAPE:
                    if not self._game.cancel_event():
                        self._state_manager.state = "InGameMenu"
        return True

    def update(self):
        self._game.mouseover_event(self._to_map_coords(pygame.mouse.get_pos()))
        self._game.update(pygame.time.get_ticks())

    def _render_image(self):
        # draw screen
        self._background.blit(self._game.render_image(),
                              self._from_map_coords((0, 0)))
        return self._background

    def _to_map_coords(self, pos):
        '''Correction to coords due to drawing the map in the center.'''
        return pos[0] - self._shift[0], pos[1] - self._shift[1]

    def _from_map_coords(self, pos):
        '''Backwards correction.'''
        return pos[0] + self._shift[0], pos[1] + self._shift[1]

    def get_image(self):
        return self._render_image()


class _InGameMenu(object):

    def __init__(self, state_manager):
        _LOGGER.debug("Creating in game menu")
        self._state_manager = state_manager
        self._init_graphics()
        self._exit_flag = False

    def _init_graphics(self):
        self._background = pygame.Surface((utils.SCREEN_SIZE))
        self._image = pygame.Surface((utils.SCREEN_SIZE))
        self._background = utils.load_image('in_game_menu.jpg',
                                            size=utils.SCREEN_SIZE)
        menu_items = (("Resume game", self._resume_game),
                      ("Exit game", self._exit_game),
                      )
        self._menu = _Menu(menu_items)

    def _render_image(self):
        self._image.fill((0,0,0,155))
        self._image.blit(self._background, (0, 0))
        self._menu.draw(self._image)
        return self._image

    def _resume_game(self):
        self._state_manager.state = "Game"

    def _exit_game(self):
        self._exit_flag = True

    def handle_events(self, events):
        if self._exit_flag:
            return False
        for event in events:
            if event.type == pl.QUIT:
                return False
            elif event.type == pl.MOUSEBUTTONUP:
                if event.button == MOUSE_LEFT:
                    self._menu.execute()
            elif event.type == pl.KEYDOWN:
                if event.key == pl.K_ESCAPE:
                    self._resume_game()
        return True

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self._menu.check_selected(mouse_pos)

    def get_image(self):
        return self._render_image()

class _Menu(object):

    def __init__(self, entries, color=(255, 0, 0), select_color=(0, 0, 255)):
        self._font = pygame.font.Font(pygame.font.get_default_font(), 36)
        self.color = color
        self.select_color = select_color
        self._items = []
        for name, fnc in entries:
            self._items.append(self.MenuItem(name, fnc, self._font))

        # find total height of menus to know how far from top to start
        # drawing
        # also need to know width of the biggest menu entry to place
        # at the center of x
        max_w = 0
        total_h = 0
        for entry in self._items:
            w, h = entry.size
            total_h += h + 10
            if w > max_w: max_w = w
        scr_w, scr_h = utils.SCREEN_SIZE
        # find starting coord for x and y
        self.topleft = (scr_w - max_w) / 2, (scr_h - total_h) / 2

    def draw(self, image):
        '''Draw every entry.'''
        x, y = self.topleft
        for entry in self._items:
            color = self.select_color if entry.selected else self.color
            entry.rect = x, y
            image.blit(entry.render(color), (x, y))
            y += entry.size[1]

    def check_selected(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        for entry in self._items:
            x, y = entry.rect
            w, h = entry.size
            if 0 < mouse_x - x < w and 0 < mouse_y - y < h:
                entry.selected = True
            else:
                entry.selected = False

    def execute(self):
        for entry in self._items:
            if entry.selected:
                entry.fnc()
                return

    class MenuItem(object):

        def __init__(self, name, fnc, font):
            self._font = font
            self.name = name
            self.fnc = fnc
            self.rect = 0, 0
            self.selected = False
            image = self._font.render(name, True, (0, 0, 0))
            self.size = image.get_size()

        def render(self, color, antialias=True):
            image = self._font.render(self.name, antialias, color)
            return image

