from setuptools import setup
from setuptools.extension import Extension
import sys

requirements = []

version = '0.0.1'

if sys.platform != 'cygwin':
    BotErrors = Extension('BotErrors', ['BotErrors.c'])
else:
    BotErrors = Extension('BotErrors',
                               library_dirs=['/usr/local/bin'],
                               sources=['BotErrors.c'])


if not version:
    raise RuntimeError('version is not set')

try:
    with open('README.rst') as f:
        readme = f.read()
except FileNotFoundError:
    readme = ""

setup(name='BotErrors',
      author='Decorater',
      author_email='seandhunt_7@yahoo.com',
      url='https://github.com/DecoraterBot-devs/BotErrors',
      bugtrack_url='https://github.com/DecoraterBot-devs/BotErrors/issues',
      version=version,
      packages=None,
      ext_modules=[BotErrors],
      license='MIT',
      description='This package is for bringing Errors to DecoraterBot.',
      long_description=readme,
      maintainer_email='seandhunt_7@yahoo.com',
      download_url='https://github.com/DecoraterBot-devs/BotErrors',
      include_package_data=True,
      install_requires=requirements,
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
