#!/usr/bin/env python

"""Auto-generated file

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-25 16:01:50.179836 "

import logging
from functools import partial

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
        self.states = [_MainMenu(self)]
        self._levels = utils.load_levels_info()
        self._transition_info = (1, False, 0, None, self.states[-1].get_image())

    def handle_events(self, events):
        return self.states[-1].handle_events(events)

    def get_rendered_screen(self):
        self.states[-1].update()
        image = self._transition()
        if not image:
            image = self.states[-1].get_image()
        return image

    def get_levels(self):
        return self._levels.keys()

    def game(self, name):
        _LOGGER.debug("Initializing level '%s'", name)
        self.states.append(_Game(self, level_info=self._levels[name]))

    def main_menu(self):
        self.states = self.states[:1]
        #self._menu_transition = 0
        #self._states["Game"].get_image().set_alpha(255)

    def back(self):
        self.states.pop()

    def skip(self):
        self.states.pop()
        self.states[-1].finish()

    def pause(self):
        cutscene = isinstance(self.states[-1], _Attack)
        self.states.append(_InGameMenu(self, cutscene))

    def attack(self, *args):
        self.states.append(_Attack(self, *args))

    def finish_attack(self):
        self.states.pop()
        self.states[-1].finish_attack()

    def _transition(self):
        '''Cool transition effect.'''
        image = None
        last_state, trans, step, prev_image, curr_image = self._transition_info
        #print self._transition_info
        if last_state != len(self.states):
            last_state = len(self.states)
            trans = True
            step = 0
            prev_image = curr_image
            curr_image = self.states[-1].get_image()

        if trans:
            curr_image = self.states[-1].get_image()
            prev_image.set_alpha(255 - step * 5)
            curr_image.set_alpha(step * 6)
            step += 1
            if step == 32:
                trans = False
            image = pygame.Surface(utils.SCREEN_SIZE)
            image.blit(prev_image, (0, 0))
            image.blit(curr_image, (0, 0))

        self._transition_info = (last_state, trans, step, prev_image, curr_image)
        return image


class _Game(object):

    def __init__(self, state_manager, level_info):
        _LOGGER.debug("Creating game")
        self._state_manager = state_manager
        self._game = game.Game(level_info)
        self._background = utils.load_image('game_background.jpg',
                                            size=utils.SCREEN_SIZE)
        self.screen_position = [0, 0]

    def get_levels(self):
        return self._game.get_levels()

    def load_level(self, name):
        self._game.load_level(name)

    def handle_events(self, events):
        """Return false to stop the event loop and end the game."""
        for event in events:
            if event.type == pl.QUIT:
                self._state_manager.pause()
            elif event.type == pl.MOUSEBUTTONUP:
                if event.button == MOUSE_LEFT:
                    res = self._game.click_event(self._to_map_coords(pygame.mouse.get_pos()))
                    if res:
                        if res[0] == 'attack':
                            self._state_manager.attack(*res[1])
            elif event.type == pl.KEYDOWN:
                if event.key == pl.K_ESCAPE:
                    if not self._game.cancel_event():
                        self._state_manager.pause()
        return True

    def finish_attack(self):
        self._game.finish_attack()

    def update(self):
        self.move_view(pygame.mouse.get_pos())
        self._game.mouseover_event(self._to_map_coords(pygame.mouse.get_pos()))
        self._game.update(pygame.time.get_ticks())

    def move_view(self, mouse):
        if 5 < mouse[0] < 75 and self._to_map_coords((0, 0))[0] > 0:
            self.screen_position[0] += utils.SCROLL_SPEED

        elif utils.SCREEN_SIZE[0] - 75 < mouse[0] < utils.SCREEN_SIZE[0] - 5 \
                and self._from_map_coords(self._game.get_map_size())[0] > utils.SCREEN_SIZE[0]:
            self.screen_position[0] -= utils.SCROLL_SPEED

        if 5 < mouse[1] < 75 and self._to_map_coords((0, 0))[1] > 0:
            self.screen_position[1] += utils.SCROLL_SPEED

        elif utils.SCREEN_SIZE[1] - 75 < mouse[1] < utils.SCREEN_SIZE[1] - 5 \
                and self._from_map_coords(self._game.get_map_size())[1] > utils.SCREEN_SIZE[1]:
            self.screen_position[1] -= utils.SCROLL_SPEED

    def _render_image(self):
        # draw screen
        self._background.blit(self._game.render_image(),
                              self._from_map_coords((0, 0)))
        return self._background

    def _get_shift(self):
        # calculate map shift from the edge of the screen
        size = utils.SCREEN_SIZE
        w, h = self._game.get_map_size()
        view = self.screen_position
        shift = (size[0] - w) / 2 + view[0], (size[1] - h) / 2 + view[1]
        return shift

    def _to_map_coords(self, pos):
        '''Correction to coords due to drawing the map in the center.'''
        shift = self._get_shift()
        return pos[0] - shift[0], pos[1] - shift[1]

    def _from_map_coords(self, pos):
        '''Backwards correction.'''
        shift = self._get_shift()
        return pos[0] + shift[0], pos[1] + shift[1]

    def get_image(self):
        return self._render_image()


class _Attack(object):

    def __init__(self, state_manager, melee, attacker, attacked, damage_to_attacker, damage_to_attacked):
        self._state_manager = state_manager
        self._image = pygame.Surface((utils.SCREEN_SIZE))
        #self.attacker = attacker
        #self.attacked = attacked
        #self.melee = melee
        #self.


    def handle_events(self, events):
        """Return false to stop the event loop and end the game."""
        for event in events:
            if event.type == pl.QUIT:
                self._state_manager.pause()
            elif event.type == pl.KEYDOWN:
                if event.key == pl.K_ESCAPE:
                    self._state_manager.pause()
        return True

    def finish(self):
        self._state_manager.finish_attack()

    def update(self):
        #TODO: add animation
        #self.finish()
        pass

    def get_image(self):
        return self._image


class _MenuState(object):

    def __init__(self, state_manager, background):
        self._state_manager = state_manager
        self._image = pygame.Surface((utils.SCREEN_SIZE))
        self._background = utils.load_image(background,
                                            size=utils.SCREEN_SIZE)
        self._menus = []
        self._init_menu()

    def _init_menu(self):
        _LOGGER.warning("Calling stub method _init_menu of %s", self)

    def _render_image(self):
        self._image.fill((0,0,0,155))
        self._image.blit(self._background, (0, 0))
        self._menus[-1].draw(self._image)
        return self._image

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self._menus[-1].check_selected(mouse_pos)

    def get_image(self):
        return self._render_image()


class _MainMenu(_MenuState):

    def __init__(self, state_manager):
        super(_MainMenu, self).__init__(state_manager, 'main_menu.jpg')
        _LOGGER.debug("Creating main menu")
        self._exit_flag = False

    def _init_menu(self):
        menu_items = (("Select level", self._select_menu),
                      ("Exit game", self._exit_game),
                      )
        self._menus.append(_Menu(menu_items))

    def _select_menu(self):
        menu_items = []
        levels = self._state_manager.get_levels()
        for level in levels:
            load = partial(self._load_level, name=level)
            menu_items.append((level, load))
        menu_items.append(("Back", self._back))
        self._menus.append(_Menu(menu_items))

    def _load_level(self, name):
        self._state_manager.game(name)
        self._menus.pop()

    def _exit_game(self):
        self._exit_flag = True

    def _back(self):
        self._menus.pop()

    def handle_events(self, events):
        if self._exit_flag:
            return False
        for event in events:
            if event.type == pl.QUIT:
                return False
            elif event.type == pl.MOUSEBUTTONUP:
                if event.button == MOUSE_LEFT:
                    self._menus[-1].execute()
        return True


class _InGameMenu(_MenuState):

    def __init__(self, state_manager, cutscene=False):
        self._cutscene = cutscene
        super(_InGameMenu, self).__init__(state_manager, 'in_game_menu.jpg')
        _LOGGER.debug("Creating in game menu")
        self._exit_flag = False

    def _init_menu(self):
        menu_items = [("Resume", self._back),
                      ("Main menu", self._main_menu),
                      ("Exit game", self._exit_game),
                      ]
        if self._cutscene:
            menu_items.insert(1, ("Skip", self._skip))
        self._menus.append(_Menu(menu_items))

    def _main_menu(self):
        self._state_manager.main_menu()

    def _skip(self):
        self._state_manager.skip()

    def _back(self):
        self._state_manager.back()

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
                    self._menus[-1].execute()
            elif event.type == pl.KEYDOWN:
                if event.key == pl.K_ESCAPE:
                    self._back()
        return True


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

