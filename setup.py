from setuptools import setup, Extension
import sys


def get_extensions():
    """
    lists the extensions to build with a compiler.
    """
    if sys.platform != 'cygwin':
        BotErrors = Extension(
            'DecoraterBotUtils.BotErrors', [
                'DecoraterBotUtils/BotErrors.c'])
    else:
        BotErrors = Extension(
            'DecoraterBotUtils.BotErrors',
            library_dirs=['/usr/local/bin'],
            sources=['DecoraterBotUtils/BotErrors.c'])
    return [BotErrors]


setup_args = dict(
    ext_modules=get_extensions(),
    dependency_links=[
        "git+https://github.com/IzunaDevs/TinyURL.git@indev",
        "git+https://github.com/IzunaDevs/consolechange.git",
        "git+https://github.com/IzunaDevs/dbapi.git",
    ],
)

setup(**setup_args)
