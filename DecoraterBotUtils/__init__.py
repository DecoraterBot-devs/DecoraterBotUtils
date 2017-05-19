# coding=utf-8
"""
DecoraterBotUtils
~~~~~~~~~~~~~~~~~~~

Various things to DecoraterBot.

:copyright: (c) 2015-2017 Decorater
:license: MIT, see LICENSE for more details.

"""
from . import BotErrors
from . import utils

# These are external things for DecoraterBot's Core.

__all__ = (dir(BotErrors), utils.__all__)
