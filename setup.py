from setuptools import setup
from setuptools.extension import Extension
import sys


def get_requirements(remove_links=True):
    """
    lists the requirements to install.
    """
    requirements = []
    try:
        with open('requirements.txt') as f:
            requirements = f.read().splitlines()
    except Exception as ex:
        with open('DecoraterBotUtils.egg-info\requires.txt') as f:
            requirements = f.read().splitlines()
    if remove_links:
        for requirement in requirements:
            # git/subversion/mercurial repository url.
            if requirement.startswith("git+") or \
                requirement.startswith("svn+") or \
                requirement.startswith("hg+"):
                requirements.remove(requirement)
    return requirements


def get_links():
    """
    gets URL Dependency links.
    """
    links_list = get_requirements(remove_links=False)
    for link in links_list:
        # git/subversion/mercurial repository url.
        if not link.startswith("git+") or not \
            link.startswith("svn+") or not \
            link.startswith("hg+"):
            links_list.remove(link)
    return links_list


def get_version():
    """
    returns version.
    """
    return '0.0.1'


def get_extensions():
    """
    lists the extensions to build with an compiler.
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


if not get_version():
    raise RuntimeError('version is not set')

try:
    with open('README.rst') as f:
        readme = f.read()
except FileNotFoundError:
    readme = ""

setup(name='DecoraterBotUtils',
      author='Decorater',
      author_email='seandhunt_7@yahoo.com',
      url='https://github.com/DecoraterBot-devs/DecoraterBotUtils',
      bugtrack_url='https://github.com/DecoraterBot-devs/DecoraterBotUtils/issues',
      version=get_version(),
      packages=['DecoraterBotUtils'],
      ext_modules=get_extensions(),
      license='MIT',
      description='This package is for bringing various things to DecoraterBot.',
      long_description=readme,
      maintainer_email='seandhunt_7@yahoo.com',
      download_url='https://github.com/DecoraterBot-devs/DecoraterBotUtils',
      include_package_data=True,
      install_requires=get_requirements(),
      dependency_links=get_links(),
      platforms='Any',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ]
)
