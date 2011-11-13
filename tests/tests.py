# -*- coding: utf-8 -*-

import os
from unittest import TestCase, main
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.append(PROJECT_ROOT)

from example_bot import (
        ExampleScreen,
        ExampleBot
        )
import Image

log = logging.getLogger('screen_bot:core')
#log.setLevel(logging.DEBUG)


def get_image(image_name):
    path = os.path.join(PROJECT_ROOT, 'img', image_name)
    image = Image.open(path)
    return image.convert(mode='RGB')

class FindGameTestCase(TestCase):
    def test_is_game(self):
        pic = get_image('screen_area_test.png').load()
        assert ExampleScreen().match_screen(pic, x=0, y=0)

    def test_find_screen(self):
        pix = get_image('screen_test.png').load()
        screen_pos = ExampleScreen().find_screen(pix)
        assert screen_pos == (20, 63), screen_pos

    def test_init_screen(self):
        ExampleScreen.init_screen()


class ExampleBotTestCase(TestCase):
    def test_init_screen(self):
        bot = ExampleBot()
        bot.init_screen()
        assert bot.screen.x == 18, bot.screen.x
        assert bot.screen.y == 30, bot.screen.y

    def test_is_center_point_aviable(self):
        pic = get_image('screen_area_test.png').load()
        bot = ExampleBot()
        bot.set_game_screen(0, 0)
        assert bot.is_center_point_aviable(pic)


if __name__ == '__main__':
    main()
