#!/usr/bin/env python
# template: library
# SPDX-License-Identifier: GPL-3.0-or-later
"""library for APRS"""

#import site #http://docs.python.org/library/site.html
import sys
import os
#import platform
import logging
import re
#import time
#import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv
import configparser

logger = logging.getLogger("lib")

import radio_scripts.geo.base as geoBase

def _parsePosition(lstPos):
  if ((re.match(geoBase.regexLatDMS_APRS, lstPos[0]) is not None)
      and (re.match(geoBase.regexLongDMS_APRS, lstPos[1]) is not None)):
    return lstPos

  try:
    lat = float(lstPos[0])
    res = geoBase.signed2dms(lat)
    if (lat > 0.0):
      _lat = "{:0>2}{:0>2}.{:0>2}N".format(res[0], res[1], res[2])
    else:
      _lat = "{:0>2}{:0>2}.{:0>2}S".format(res[0], res[1], res[2])
    long = float(lstPos[1])
    res = geoBase.signed2dms(long)
    if (long > 0.0):
      _long = "{:0>3}{:0>2}.{:0>2}E".format(res[0], res[1], res[2])
    else:
      _long = "{:0>3}{:0>2}.{:0>2}W".format(res[0], res[1], res[2])
    return [_lat, _long]
  except ValueError:
    msg = "INCORRECT coordinates: {}".format(lstPos)
    logger.error(msg)
    raise RuntimeError(msg)

class APRSConfig(object):

  def __init__(self):
    self.conn = ""
    self.mycall = "NOCALL"
    self.filters = {}
    self.position = {}
    self.object = {}
    self.telemetry = {}

  def _parsePosition(self):
    if ("coordinates" not in self.position.keys()):
      msg = "[position] DOES NOT HAVE coordinates"
      logger.error(msg)
      raise RuntimeError(msg)

    tmp = self.position["coordinates"].split()
    if (len(tmp) != 2):
      msg = "[position] INCORRECT coordinates"
      logger.error(msg)
      raise RuntimeError(msg)
    self.position["coordinates"] = tmp
    self.position["coordinates"] = _parsePosition(self.position["coordinates"])

    if ("symbol" not in self.position.keys()):
      self.position["symbol"] = "TBD"

  def _parseObject(self):
    if ("coordinates" not in self.object.keys()):
      msg = "[object] DOES NOT HAVE coordinates"
      logger.error(msg)
      raise RuntimeError(msg)

    if ("name" not in self.object.keys()):
      msg = "[object] INCORRECT name"
      logger.error(msg)
      raise RuntimeError(msg)

    tmp = self.object["coordinates"].split()
    if (len(tmp) != 2):
      msg = "[object] INCORRECT coordinates"
      logger.error(msg)
      raise RuntimeError(msg)
    self.object["coordinates"] = tmp
    self.object["coordinates"] = _parsePosition(self.object["coordinates"])

    if ("symbol" not in self.object.keys()):
      self.object["symbol"] = "TBD"

  def _parseTelemetry(self):
    if (len(self.telemetry) > 5):
      msg = "[telemetry] TOO MANY values"
      logger.error(msg)
      raise RuntimeError(msg)

    for k, v in self.telemetry.items():
      if (re.match(r"ANA[1-5]", k) is None):
        msg = "[telemetry] INCORRECT key: {}".format(k)
        logger.error(msg)
        raise RuntimeError(msg)
      tmp = v.split(" ")
      if (len(tmp) != 5):
        msg = "[telemetry] INCORRECT value: {}".format(v)
        logger.error(msg)
        raise RuntimeError(msg)
      self.telemetry[k] = tmp

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

    #print("DBG", list(cfgObj.keys()))
    if ("filter" in cfgObj.keys()):
      self.filters.update(cfgObj["filter"].items())

    if ("position" in cfgObj.keys()):
      self.position.update(cfgObj["position"].items())
      self._parsePosition()

    if ("object" in cfgObj.keys()):
      self.object.update(cfgObj["object"].items())
      self._parseObject()

    if ("telemetry" in cfgObj.keys()):
      self.telemetry.update(cfgObj["telemetry"].items())
      self._parseTelemetry()

  def showInfo(self):
    logger.info("connection: '{}'".format(self.conn))
    logger.info("my_call: '{}'".format(self.mycall))
    if (len(self.filters) > 0):
      logger.info("-- {:d} filter(s)".format(len(self.filters)))
      for k in sorted(self.filters.keys()):
        logger.info("  '{}': {}".format(k, self.filters[k]))

    if (len(self.position) > 0):
      logger.info("-- position")
      for k in sorted(self.position.keys()):
        logger.info("  {}: {}".format(k, self.position[k]))

    if (len(self.object) > 0):
      logger.info("-- object")
      for k in sorted(self.object.keys()):
        logger.info("  {}: {}".format(k, self.object[k]))

    if (len(self.telemetry) > 0):
      logger.info("-- telemetry")
      for k in sorted(self.telemetry.keys()):
        logger.info("  {}: {}".format(k, self.telemetry[k]))
