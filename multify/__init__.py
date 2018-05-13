# -*- coding:utf-8 -*-
"""
Multify

Just another email notifier library.
"""
import os.path as path
import sys

from gmail import ByGMail


__version__ = '0.0.1'
__author__ = 'Daniel J. Umpierrez'
__license__ = 'MIT'

BASE_DIR = path.dirname(path.dirname(__file__))
sys.path.append(BASE_DIR)

# global debug flag
DEBUG = True

__all__ = ['__version__', '__author__', '__license__', 'DEBUG', 'BASE_DIR', 'ByGMail']
