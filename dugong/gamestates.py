#!/usr/bin/env python

"""Manages game states.

Game state class shoud have following interface:

# Setup and destroy the state
__init__();
cleanup();

# The three important actions within a game loop
handle_events(events_list);
update(game_ticks);
pygame.Surface <- render();

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-25 16:01:50.179836 "

import logging
from functools import partial

import pygame
import pygame.locals as pl
MOUSE_LEFT = 1

import game
import utils
from utils import RES_MANAGER

LOGGER = logging.getLogger('main.gamestates')

class GameStateManager(object):

    def __init__(self):
        self.states = [_MainMenuState(self)]
        self._transition_info = (1, False, 0, None, self.states[-1].render())
        self._continue_game = True

    def handle_events(self, events):
        self.states[-1].handle_events(events)
        return self._continue_game

    def get_rendered_screen(self):
        self.states[-1].update(pygame.time.get_ticks())
        image = self._transition()
        return image

    def push_state(self, state):
        self.states.append(state)

    def pop_state(self):
        self.states[-1].cleanup()
        self.states.pop()

    def exit(self):
        self._continue_game = False

    def main_menu(self):
        self.states = self.states[:1]

    def _transition(self):
        '''Cool transition effect.'''
        image = None
        last_state, trans, step, prev_image, curr_image = self._transition_info

        # state have just changed
        if last_state != len(self.states):
            last_state = len(self.states)
            trans = True
            step = 0
            prev_image = curr_image
            curr_image = self.states[-1].render()

        # state is changing
        if trans:
            transp = int(step * 60.0 / utils.FPS)
            curr_image = self.states[-1].render()
            prev_image.set_alpha(255 - transp * 6)
            curr_image.set_alpha(transp * 6)
            step += 1
            if step == utils.FPS / 2:
                trans = False
            image = pygame.Surface(utils.SCREEN_SIZE)
            image.blit(prev_image, (0, 0))
            image.blit(curr_image, (0, 0))
        else:
            if self.states[-1].is_transparent:
                image = pygame.Surface(utils.SCREEN_SIZE)
                back = self.states[-2].render()
                back.set_alpha(200)
                image.blit(back, (0, 0))
                front = self.states[-1].render()
                front.set_alpha(170)
                image.blit(front, (0, 0))
            else:
                image = self.states[-1].render()
                image.set_alpha(255)

        self._transition_info = (last_state, trans, step, prev_image, curr_image)
        return image


class _GameState(object):

    def __init__(self, state_manager, level_name, level_info):
        LOGGER.debug("Creating game")
        LOGGER.debug("Initializing level '%s'", level_name)
        self.is_transparent = False
        self._state_manager = state_manager
        self._game = game.Game(level_info)

        self._metrics = MetricTransformer()
        self._game_renderer = game.GameRenderer(self._game, self._metrics)
        self._metrics.set_map_size(self._game_renderer.get_size())

        self._name = level_name
        self._background = RES_MANAGER.get('game_background.jpg',
                                            size=utils.SCREEN_SIZE)
        self._statusbar = StatusBar(utils.SCREEN_SIZE)

    def cleanup(self):
        pass

    def handle_events(self, events):
        """Return false to stop the event loop and end the game."""
        for event in events:
            if event.type == pl.QUIT:
                self._pause()
            elif event.type == pl.MOUSEBUTTONUP:
                if event.button == MOUSE_LEFT:
                    if self._statusbar.contains(pygame.mouse.get_pos()):
                        res = self._statusbar.click_event(pygame.mouse.get_pos())
                        if res:
                            if res == 'endturn':
                                self._game.end_turn()
                    else:
                        res = self._game.click_event(self._metrics.screen_to_tiles(pygame.mouse.get_pos()))
                        if res:
                            if res[0] == 'attack':
                                self._state_manager.push_state(_AttackState(self._state_manager, *res[1]))
            elif event.type == pl.KEYDOWN:
                if event.key == pl.K_ESCAPE:
                    if not self._game.cancel_event():
                        self._pause()

    def update(self, game_ticks):
        self.move_view(pygame.mouse.get_pos())
        status_info = self._game.mouseover_event(self._metrics.screen_to_tiles(pygame.mouse.get_pos()))
        self._statusbar.update(status_info)
        self._game.update(game_ticks)

    def render(self):
        # draw screen
        self._background.blit(self._game_renderer.render(),
                              self._metrics.map_topleft())
        self._background.blit(self._statusbar.get_image(),
                              self._statusbar.get_pos())
        return self._background

    def _pause(self):
        self._state_manager.push_state(_InGameMenuState(self._state_manager))

    def move_view(self, mouse):
        if 5 < mouse[0] < 75 and self._metrics.map_is_hidden_at(self._metrics.W):
            self._metrics.move_view(x=utils.SCROLL_SPEED)

        elif 5 < utils.SCREEN_SIZE[0] - mouse[0] < 75 \
                and self._metrics.map_is_hidden_at(self._metrics.E):
            self._metrics.move_view(x=-utils.SCROLL_SPEED)

        if 5 < mouse[1] < 75 and self._metrics.map_is_hidden_at(self._metrics.N):
            self._metrics.move_view(y=utils.SCROLL_SPEED)

        elif  5 < utils.SCREEN_SIZE[1] - mouse[1] < 75 \
                and self._metrics.map_is_hidden_at(self._metrics.S):
            self._metrics.move_view(y=-utils.SCROLL_SPEED)


class _AttackState(object):

    def __init__(self, state_manager, attacker, attacked, damage_to_attacker, damage_to_attacked):
        self.is_transparent = False
        self._state_manager = state_manager
        self._image = pygame.Surface((utils.SCREEN_SIZE))
        self._font = utils.Writer(24, (255, 0, 0))
        skip = self._font.render("Press 's' to skip cut-scene.")
        self._image.blit(skip, (0, 0))

    def cleanup(self):
        pass

    def handle_events(self, events):
        """Return false to stop the event loop and end the game."""
        for event in events:
            if event.type == pl.QUIT:
                self.pause()
            elif event.type == pl.KEYDOWN:
                if event.key == pl.K_ESCAPE:
                    self.pause()
                elif event.key == pl.K_s:
                    self._state_manager.pop_state()

    def update(self, game_ticks):
        #TODO: add animation
        pass

    def render(self):
        return self._image

    def pause(self):
        self._state_manager.push_state(_InGameMenuState(self._state_manager, cutscene=True))


class _MenuState(object):

    def __init__(self, state_manager, background):
        self.is_transparent = False
        self._state_manager = state_manager
        self._image = pygame.Surface((utils.SCREEN_SIZE))
        self._background = RES_MANAGER.get(background,
                                            size=utils.SCREEN_SIZE)
        self._menus = []
        self._init_menu()

    def cleanup(self):
        pass

    def _init_menu(self):
        LOGGER.warning("Calling stub method _init_menu of %s", self)

    def update(self, game_ticks):
        mouse_pos = pygame.mouse.get_pos()
        self._menus[-1].check_selected(mouse_pos)

    def render(self):
        self._image.blit(self._background, (0, 0))
        self._menus[-1].draw(self._image)
        return self._image


class _MainMenuState(_MenuState):

    def __init__(self, state_manager):
        super(_MainMenuState, self).__init__(state_manager, 'main_menu.jpg')
        LOGGER.debug("Creating main menu")
        self._levels = RES_MANAGER.get('levels_info')

    def _init_menu(self):
        menu_items = (("Select level", self._select_menu),
                      ("Exit game", self._back),
                      )
        self._menus.append(_Menu(menu_items))

    def handle_events(self, events):
        for event in events:
            if event.type == pl.QUIT:
                self._back()
            elif event.type == pl.MOUSEBUTTONUP:
                if event.button == MOUSE_LEFT:
                    self._menus[-1].execute()
            elif event.type == pl.KEYDOWN:
                if event.key == pl.K_ESCAPE:
                    self._back()

    def _select_menu(self):
        menu_items = []
        levels = self._levels.keys()
        for level_name, level_info in self._levels.items():
            load = partial(self._load_level, level_name, level_info)
            menu_items.append((level_name, load))
        menu_items.append(("Back", self._back))
        self._menus.append(_Menu(menu_items))

    def _load_level(self, name, info):
        self._state_manager.push_state(_GameState(self._state_manager, name, info))
        self._menus.pop()

    def _back(self):
        if len(self._menus) > 1:
            self._menus.pop()
        else:
            self._state_manager.exit()


class _InGameMenuState(_MenuState):

    def __init__(self, state_manager, cutscene=False):
        self._cutscene = cutscene
        super(_InGameMenuState, self).__init__(state_manager, 'in_game_menu.jpg')
        LOGGER.debug("Creating in game menu")
        self.is_transparent = True

    def _init_menu(self):
        menu_items = [("Resume", self._back),
                      ("Main menu", self._main_menu),
                      ("Exit game", self._exit),
                      ]
        if self._cutscene:
            menu_items.insert(1, ("Skip", self._skip))
        self._menus.append(_Menu(menu_items))

    def handle_events(self, events):
        for event in events:
            if event.type == pl.QUIT:
                self._exit()
            elif event.type == pl.MOUSEBUTTONUP:
                if event.button == MOUSE_LEFT:
                    self._menus[-1].execute()
            elif event.type == pl.KEYDOWN:
                if event.key == pl.K_ESCAPE:
                    self._back()

    def _main_menu(self):
        self._state_manager.main_menu()

    def _skip(self):
        self._state_manager.pop_state()
        self._state_manager.pop_state()

    def _back(self):
        self._state_manager.pop_state()

    def _exit(self):
        self._state_manager.exit()


class _Menu(object):

    def __init__(self, entries, color=(255, 0, 0), select_color=(0, 0, 255)):
        self._items = []
        for name, fnc in entries:
            self._items.append(self.MenuItem(name, fnc, color, select_color))

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
            entry.rect = x, y
            image.blit(entry.render(), (x, y))
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

        def __init__(self, name, fnc, color, sel_color):
            self._font = utils.Writer(36, color)
            self.sel_color = sel_color
            self.name = name
            self.fnc = fnc
            self.rect = 0, 0
            self.selected = False
            image = self._font.render(name)
            self.size = image.get_size()

        def render(self):
            if self.selected:
                return self._font.render(self.name, self.sel_color)
            else:
                return self._font.render(self.name)


class StatusBar(object):

    def __init__(self, scr_size, w=700, h=70):
        self.fontsize = 20
        self.font = utils.Writer(self.fontsize - 4, (255, 0, 0))
        self.background = RES_MANAGER.get('status.png', size=(w, h))
        self.image = pygame.Surface((w, h))
        self.pos = (scr_size[0] - w) / 2, (scr_size[1] - h)
        self.size = w, h
        self.endturn_rect = 0, 0, 0, 0

    def get_image(self):
        return self.image

    def get_pos(self):
        return self.pos

    def contains(self, coords):
        return self.pos[0] <= coords[0] <= self.pos[0] + self.size[0] \
            and self.pos[1] <= coords[1] <= self.pos[1] + self.size[1] \

    def update(self, info):
        if not info:
            return

        self.image.blit(self.background, (0, 0))

        # player info
        x = 10
        player = info['player']
        if player:
            player_str = self.font.render('Player:')
            self.image.blit(player_str, (x, 10))
            playername = self.font.render(player.name)
            self.image.blit(playername, (x, 10 + self.fontsize))

        # unit info
        x = 100
        unit = info['unit']
        if unit:
            self.image.blit(unit.renderer.image.get(), (x, 10))
            health_moves = self.font.render("H: " + str(unit.health) + " M: " + str(unit.moves_left))
            self.image.blit(health_moves, (x + utils.TILE_SIZE + 5, 10))
            attack_defence = self.font.render("A: " + str(unit.attack_damage) + " D: " + str(unit.defence))
            self.image.blit(attack_defence, (x + utils.TILE_SIZE + 5, 10 + self.fontsize))

        # actions
        x = 500
        endturn = self.font.render("End turn")
        self.image.blit(endturn, (x, 10))
        self.endturn_rect = x, 10, x + endturn.get_size()[0], 10 + endturn.get_size()[1]

        # tile info
        x = 600
        tile = info['tile']
        if tile:
            tile_str = self.font.render('Tile:')
            self.image.blit(tile_str, (x, 10))
            type_ = self.font.render(tile.type)
            self.image.blit(type_, (x, 10 + self.fontsize))
            defence = self.font.render("D: " + str(tile.defence))
            self.image.blit(defence, (x, 10 + self.fontsize * 2))

    def click_event(self, pos):
        pos = pos[0] - self.pos[0], pos[1] - self.pos[1]
        if self.endturn_rect[0] < pos[0] < self.endturn_rect[2] \
                and self.endturn_rect[1] < pos[1] < self.endturn_rect[3]:
            return "endturn"
        return None

class MetricTransformer(object):

    N, S, W, E = range(4)

    def __init__(self):
        self.map_size = (0, 0)
        self.screen_pos = [0, 0]

    def set_map_size(self, size):
        self.map_size = size

    def pixels_to_tiles(self, pixels):
        return pixels[1] / utils.TILE_SIZE, pixels[0] / utils.TILE_SIZE

    def tiles_to_pixels(self, tiles):
        return tiles[1] * utils.TILE_SIZE, tiles[0] * utils.TILE_SIZE

    def _get_shift(self):
        # calculate map shift from the edge of the screen
        size = utils.SCREEN_SIZE
        w, h = self.map_size
        view = self.screen_pos
        shift = (size[0] - w) / 2 + view[0], (size[1] - h) / 2 + view[1]
        return shift

    def screen_to_tiles(self, screen):
        '''Correction to coords due to drawing the map in the center.'''
        shift = self._get_shift()
        return self.pixels_to_tiles((screen[0] - shift[0], screen[1] - shift[1]))

    def map_is_hidden_at(self, direction):
        if direction is self.W:
            return self._get_shift()[0] < 0
        elif direction is self.E:
            return self._get_shift()[0] > utils.SCREEN_SIZE[0] - self.map_size[0]
        elif direction is self.N:
            return self._get_shift()[1] < 0
        elif direction is self.S:
            return self._get_shift()[1] > utils.SCREEN_SIZE[1] - self.map_size[1]

    def move_view(self, x=0, y=0):
        self.screen_pos = self.screen_pos[0] + x, self.screen_pos[1] + y

    def map_topleft(self):
        return self._get_shift()
