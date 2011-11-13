# -*- coding: utf-8 -*-
import os
from itertools import izip, cycle
from time import sleep
import logging


from screen_bot.core import BaseBot, BaseExplorer, Screen, Point, RGB, Color


logging.basicConfig()
log = logging.getLogger('example_bot')
log.setLevel(logging.INFO)


class ExampleScreenshoter(object):
    def screen(self, x1=None, y1=None, x2=None, y2=None):
        import Image
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image = Image.open(os.path.join(root, 'img/screen_test.png'))
        if x1 == None and x2 == None and y1 == None and y2 == None:
            return image
        return image.crop(x1, y1, x2, y2)


class ExampleScreen(Screen):
    height = 50
    width = 50

    def match_screen(self, pix, x, y):
        return Color.match_all_color(pix,
                [
                {'x': x, 'y': y, 'rgb': (0, 0, 0)},
                {'x': x + self.width - 1, 'y': y, 'rgb': (0, 0, 0)},
                {'x': x, 'y': y + self.height - 1, 'rgb': (0, 0, 0)},
                {'x': x + self.width - 1, 'y': y + self.height - 1, 'rgb': (0, 0, 0)},
                ])

    def get_display_size(self):
        return Point(200, 200)


class ExampleBot(BaseBot):
    screen_class = ExampleScreen

    def set_game_screen(self, x, y):
        self.set_screen(self.get_screen_class()(x, y))

    def is_center_point_aviable(self, pix=None):
        pix = pix or self.screen.get_screen_image().load()
        return Color.match_all_color(pix,
                [
                {'x': self.screen.width / 2, 'y': self.screen.height / 2, 'rgb': (0, 0, 0)},
                ])

    def start(self):
        self.init_screen()

def main():
    g = GameBot()
    g.start()

if __name__ == '__main__':
    main()
