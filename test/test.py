#!/usr/bin/env python

"""Auto-generated file

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-25 14:09:03.019252 "

from pymock import *
import unittest
import sys
sys.path.insert(0, '../')

import pygame

from dugong.gamemap import GameMap
from dugong.gamestates import GameStateManager

class TestGameMap(unittest.TestCase):

    def setUp(self):
        self.game_map = GameMap()
        self.game_map.load_level([['r','w'], ['l','m']])

    def test_tile_at_pos(self):
        self.assertEqual(self.game_map.tile_at_pos(0,0).type, 'road') # Tile type is not a road.
        self.assertEqual(self.game_map.tile_at_pos(0,1).type, 'water') # Tile type is not a water.
        self.assertEqual(self.game_map.tile_at_pos(1,0).type, 'land') # Tile type is not a land.
        self.assertEqual(self.game_map.tile_at_pos(1,1).type, 'mountain') # Tile type is not a mountain.

    def test_tile_at_coord(self):
        self.assertEqual(self.game_map.tile_at_coord(0,0).type, 'road') # Tile type is not a road.
        self.assertEqual(self.game_map.tile_at_coord(10,10).type, 'road') # Tile type is not a road.

    def test_find_path_begin_end(self):
        orig, dest = self.game_map.tile_at_pos(0, 0), self.game_map.tile_at_pos(1, 1)
        path = self.game_map.find_path(orig, dest)
        self.assertEqual(path[0], orig) # Path doesn't start at the given start tile
        self.assertEqual(path[-1], dest) # Path doesn't end at the given end tile
        self.assertEqual(len(path), 3) # Path is of the wrong length

    def test_find_path_one_tile(self):
        orig, dest = self.game_map.tile_at_pos(0, 0), self.game_map.tile_at_pos(0, 0)
        path = self.game_map.find_path(orig, dest)
        self.assertEqual(path[0], orig) # Path doesn't contain given tile
        self.assertEqual(len(path), 1) # Path is of the wrong length

class TestGameStateManager(unittest.TestCase):

    def test_default_state(self):
        manager = GameStateManager()
        self.assertEqual(manager.state, "MainMenu") # Default state is not Main Menu

    def test_get_rendered_screen_surface(self):
        manager = GameStateManager()
        screen = manager.get_rendered_screen()
        self.assertTrue(isinstance(screen, pygame.Surface)) # Not valid pygame.Surface returned

    def test_update_and_get_image_is_called(self):
        # holds all mock objects
        mocker = Controller()
        # mock object to be used in tested routine instead of real thing
        mocked_game_state = mocker.mock()
        # record exactly how mock object should be used in tested routine
        mocked_game_state.update()
        mocked_game_state.get_image((500, 500))
        # prepare it for real use
        mocker.replay()
        # init states
        manager = GameStateManager()
        manager.state = "Mock"
        manager._states["Mock"] = mocked_game_state
        # call tested routine
        screen = manager.get_rendered_screen((500, 500))
        # test if it was used right
        mocker.verify()

class TestGameStateMainMenu(unittest.TestCase):

    def setUp(self):
        self.manager = GameStateManager()
        self.manager.state = "MainMenu"

    def test_handle_events_exits(self):
        events = [pygame.event.Event(pygame.locals.QUIT)]
        res = self.manager.handle_events(events)
        self.assertEqual(res, False) # Game doesn't exit from main menu

class TestGameStateGame(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.manager = GameStateManager()
        self.manager.state = "Game"

    def test_get_rendered_screen_surface(self):
        screen = self.manager.get_rendered_screen()
        self.assertTrue(isinstance(screen, pygame.Surface)) # Not valid pygame.Surface returned

    def test_get_rendered_screen_correct_size(self):
        screen = self.manager.get_rendered_screen((500, 500))
        self.assertEqual(screen.get_size(), (500, 500)) # Returned image should be of correct size

    def test_handle_events_changes_state(self):
        events = [pygame.event.Event(pygame.locals.QUIT)]
        res = self.manager.handle_events(events)
        self.assertEqual(res, True, "Game exit from game state")
        self.assertEqual(self.manager.state, "InGameMenu") # Game doesn't exit to ingame menu

class TestGameStateInGameMenu(unittest.TestCase):

    def setUp(self):
        self.manager = GameStateManager()
        self.manager.state = "InGameMenu"


if __name__=="__main__":
    unittest.main()
