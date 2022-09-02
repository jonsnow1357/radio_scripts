#!/usr/bin/env python
# template: library
# SPDX-License-Identifier: GPL-3.0-or-later
"""library"""

#import site #http://docs.python.org/library/site.html
import sys
import os
#import platform
import logging
#import re
#import time
#import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv

logger = logging.getLogger("lib")

class Channel(object):

  def __init__(self):
    self.idx = 0
    self.freq = 0  # integer, in Hz
    self.tag = None
    self.modulation = None
    self.squelch_code = None
    self.delay = None
    self.lockout = None
    self.priority = None

  def __str__(self):
    return "CH {}, '{}', {} Hz, {}".format(self.idx, self.tag, self.freq, self.modulation)

  def init(self, idx, freq, tag, modulation, squelch_code):
    if (not isinstance(idx, int)):
      raise RuntimeError
    if (idx <= 0):
      raise RuntimeError
    if (not isinstance(freq, int)):
      raise RuntimeError
    if (freq < 0):
      raise RuntimeError
    if (not isinstance(tag, str)):
      raise RuntimeError
    if (not isinstance(modulation, str)):
      raise RuntimeError
    if (not isinstance(squelch_code, str)):
      raise RuntimeError

    self.idx = idx
    self.freq = freq
    self.tag = tag
    self.modulation = modulation
    self.squelch_code = squelch_code
    self.delay = 2
    self.lockout = 0
    self.priority = 0
