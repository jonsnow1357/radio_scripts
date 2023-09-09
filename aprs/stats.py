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

class APRSStats(object):

  def __init__(self):
    self.nPkt = 0
    self.dictFrom = {}
    self.thldFrom = 1
    self.dictTo = {}
    self.thldTo = 1
    self.dictType = {}
    self.thldType = 0

  def update(self, aprsPkt):
    self.nPkt += 1
    if (aprsPkt["from"] in self.dictFrom.keys()):
      self.dictFrom[aprsPkt["from"]] += 1
    else:
      self.dictFrom[aprsPkt["from"]] = 1
    if (aprsPkt["to"] in self.dictTo.keys()):
      self.dictTo[aprsPkt["to"]] += 1
    else:
      self.dictTo[aprsPkt["to"]] = 1
    if (aprsPkt["format"] in self.dictType.keys()):
      self.dictType[aprsPkt["format"]] += 1
    else:
      self.dictType[aprsPkt["format"]] = 1

  def showInfo(self):
    logger.info("total packets: {}".format(self.nPkt))

    res = dict([(k, v) for k, v in self.dictFrom.items() if (v > self.thldFrom)])
    if (len(res) > 0):
      logger.info("FROM stats (> {} msg):".format(self.thldFrom))
      for k, v in res.items():
        logger.info(f"  {k: <9} - {v} message(s)")

    res = dict([(k, v) for k, v in self.dictTo.items() if (v > self.thldTo)])
    if (len(res) > 0):
      logger.info("TO stats (> {} msg):".format(self.thldTo))
      for k, v in res.items():
        logger.info(f"  {k: <9} - {v} message(s)")

    res = dict([(k, v) for k, v in self.dictType.items() if (v > self.thldType)])
    if (len(res) > 0):
      logger.info("TYPE stats (> {} msg):".format(self.thldType))
      for k, v in res.items():
        logger.info(f"  {k: <9} - {v} message(s)")
