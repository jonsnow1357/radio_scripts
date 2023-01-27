#!/usr/bin/env python
# template: library
# SPDX-License-Identifier: GPL-3.0-or-later
"""library for APRS"""

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
import configparser

logger = logging.getLogger("lib")

class APRSConfig(object):

  def __init__(self):
    self.conn = ""
    self.mycall = "NOCALL"
    self.filters = {}

  def readCfg(self, fPath):
    fPath = os.path.realpath(fPath)
    logger.info("using config file: {}".format(fPath))

    cfgObj = configparser.ConfigParser()
    cfgObj.optionxform = str  # will be case sensitive
    cfgObj.read(fPath, encoding="utf-8")

    if ("conn" in cfgObj["default"].keys()):
      self.conn = cfgObj["default"]["conn"]
    else:
      msg = "server connection NOT DEFINED"
      logger.error(msg)
      raise RuntimeError(msg)

    if ("mycall" in cfgObj["default"].keys()):
      self.mycall = cfgObj["default"]["mycall"]
    else:
      msg = "MYCALL NOT DEFINED"
      logger.warning(msg)

    if ("filter" in cfgObj.keys()):
      self.filters.update(cfgObj["filter"].items())

  def showInfo(self):
    logger.info("connection: '{}'".format(self.conn))
    logger.info("my_call: '{}'".format(self.mycall))
    logger.info("-- {:d} filter(s)".format(len(self.filters)))
    for k in sorted(self.filters.keys()):
      logger.info("  '{}': {}".format(k, self.filters[k]))
