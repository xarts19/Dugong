#!/usr/bin/env python

"""Game window

"""

import sys
import os
import logging
import colorer

try:
    import pygame
    import pygame.locals as pl
except ImportError as ex:
    #LOGGER.exception("%s Failed to load module." % __file__)
    sys.exit("%s Failed to load module. %s" % (__file__, ex))

if not pygame.font: LOGGER.warning('Fonts disabled')
if not pygame.mixer: LOGGER.warning('Sound disabled')

from gamestates import GameStateManager
import utils

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-22 12:23:45.187597 "

LOGGER = logging.getLogger('main.window')

class Window(object):

    def __init__(self):
        """Called when the the GameWindow object is initialized. Initializes
        pygame and sets up our pygame window and other pygame tools."""

        LOGGER.debug('Initializing window')

        # load and set up pygame
        pygame.init()

        # detect display resolution and shrink resolution if needed
        info = pygame.display.Info()
        displ_w, displ_h = info.current_w, info.current_h
        wnd_w, wnd_h = utils.SCREEN_SIZE
        if displ_w < wnd_w or displ_h < wnd_h:
            wnd_w, wnd_h = displ_w - 50, displ_h - 50
            utils.SCREEN_SIZE = wnd_w, wnd_h

        # create our window
        self.window = pygame.display.set_mode(utils.SCREEN_SIZE)

        # initial window position at the center of the screen
        center_x, center_y = (displ_w - wnd_w) / 2, (displ_h - wnd_h) / 2
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(center_x) + ',' + str(center_y)

        # clock for ticking
        self.clock = pygame.time.Clock()

        # set the window title
        pygame.display.set_caption("Ancient Empires")

        # disable mouse
        pygame.mouse.set_visible(1)

        # tell pygame to only pay attention to certain events
        # we want to know if the user hits the X on the window, and we
        # want keys so we can close the window with the esc key
        #pygame.event.set_allowed([])

        self._game_state = GameStateManager()

    def run(self):
        """Runs the game. Contains the game loop that computes and renders
        each frame."""

        LOGGER.debug('Game started')

        running = True
        # run until something tells us to stop
        while running:

            # tick pygame clock
            # you can limit the fps by passing the desired frames per second to tick()
            self.clock.tick(60)

            # update the title bar with our frames per second
            pygame.display.set_caption('Ancient Empires, %d fps' % self.clock.get_fps())

            # standard game loop
            running = self._game_state.handle_events(pygame.event.get())
            image = self._game_state.get_rendered_screen()

            # blit and render the screen
            self.window.blit(image, (0, 0))
            pygame.display.flip()

        LOGGER.debug('Game finished')
