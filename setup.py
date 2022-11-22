from setuptools import setup, Extension
import sys


def get_extensions():
    """
    lists the extensions to build with a compiler.
    """
    if sys.platform != 'cygwin':
        BotErrors = Extension(
            'DecoraterBotUtils.BotErrors',
            sources=['DecoraterBotUtils/BotErrors.c'])
    else:
        BotErrors = Extension(
            'DecoraterBotUtils.BotErrors',
            library_dirs=['/usr/local/bin'],
            sources=['DecoraterBotUtils/BotErrors.c'])
    return [BotErrors]


setup_args = dict(
    ext_modules=get_extensions())

setup(**setup_args)
