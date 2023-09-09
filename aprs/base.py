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
import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv

logger = logging.getLogger("lib")

import radio_scripts.geo.base as geoBase

_SYM_PRI_02_DIGIPEATER = ["/", "#"]
_SYM_PRI_12_HOME = ["/", "-"]
_SYM_PRI_27_MOTORCYCLE = ["/", "<"]
_SYM_PRI_29_CAR = ["/", ">"]
_SYM_ALT_30_INFO = ["\\", "?"]
_SYM_PRI_34_CANOE = ["/", "C"]
_SYM_PRI_48_TBD = ["/", "Q"]
_SYM_PRI_56_SAILBOAT = ["/", "Y"]
_SYM_PRI_58_JOGGER = ["/", "["]
_SYM_PRI_65_BICYCLE = ["/", "b"]
_SYM_PRI_82_POWER_BOAT = ["/", "s"]
_SYM_PRI_74_SUV = ["/", "k"]
_SYM_PRI_84_TRUCK = ["/", "u"]
_SYM_PRI_85_VAN = ["/", "v"]
_dictSymbols = {
    "digipeter": _SYM_PRI_02_DIGIPEATER,
    "home": _SYM_PRI_12_HOME,
    "motorcycle": _SYM_PRI_27_MOTORCYCLE,
    "car": _SYM_PRI_29_CAR,
    "info": _SYM_ALT_30_INFO,
    "sailboat": _SYM_PRI_56_SAILBOAT,
    "jogger": _SYM_PRI_58_JOGGER,
    "bicycle": _SYM_PRI_65_BICYCLE,
    "powerboat": _SYM_PRI_82_POWER_BOAT,
    "SUV": _SYM_PRI_74_SUV,
    "truck": _SYM_PRI_84_TRUCK,
    "val": _SYM_PRI_85_VAN,
}

_symbol = _SYM_PRI_48_TBD

def setSymbol(symName):
  global _symbol

  try:
    _symbol = _dictSymbols[symName]
  except KeyError:
    msg = "INCORRECT symbol - should be one of:\n  {}".format(_dictSymbols.keys())
    logger.error(msg)
    raise RuntimeError()

def getDHMTime():
  dt = datetime.datetime.now(datetime.timezone.utc)
  return "{:0>2}{:0>2}{:0>2}z".format(dt.day, dt.hour, dt.minute)

def mkMessage(toCall, msg, mId=""):
  if (len(toCall) > 9):
    _to = toCall[:9]
  else:
    _to = toCall
  _msg = msg.translate(str.maketrans("", "", "|~{"))
  if (len(msg) > 67):
    _msg = _msg[:67]
  if (len(mId) == 0):
    return ":{: <9}:{}".format(_to, _msg)
  else:
    return ":{: <9}:{}\{{:0<5}".format(_to, _msg)

def mkBulletin(bId, msg):
  if (len(bId) > 1):
    _id = bId[0]
  else:
    _id = bId
  _msg = msg.translate(str.maketrans("", "", "|~{"))
  if (len(msg) > 67):
    _msg = _msg[:67]
  return ":BLN{}     :{}".format(_id, _msg)

def mkStatus(text, bTS=False):
  _text = text.translate(str.maketrans("", "", "|~"))
  if (bTS and (len(_text) < 55)):
    _text = getDHMTime() + _text
  elif (len(text) > 62):
    _text = _text[:62]
  return ">{}".format(_text)

def mkPositionNoTS(lat, long, comment, bTS=False):
  if (re.match(geoBase.regexLatDMS_APRS, lat) is None):
    logger.error("INCORRECT latitude format: {}".format(lat))
    return
  if (re.match(geoBase.regexLongDMS_APRS, long) is None):
    logger.error("INCORRECT longitude format: {}".format(long))
    return

  if (len(comment) > 43):
    _comment = comment[:43]
  else:
    _comment = comment

  if (bTS):
    return "@{}{}{}{}{}{}".format(getDHMTime(), lat, _symbol[0], long, _symbol[1], _comment)
  else:
    return "!{}{}{}{}{}".format(lat, _symbol[0], long, _symbol[1], _comment)

def mkObject(name, lat, long, comment, bLive=True):
  if (re.match(geoBase.regexLatDMS_APRS, lat) is None):
    logger.error("INCORRECT latitude format: {}".format(lat))
    return
  if (re.match(geoBase.regexLongDMS_APRS, long) is None):
    logger.error("INCORRECT longitude format: {}".format(long))
    return

  if (len(name) > 9):
    _name = name[:9]
  else:
    _name = "{:<9}".format(name)

  if (len(comment) > 43):
    _comment = comment[:43]
  else:
    _comment = comment

  if (bLive):
    return ";{}*{}{}{}{}{}{}".format(_name, getDHMTime(), lat, _symbol[0], long, _symbol[1],
                                     _comment)
  else:
    return ";{}_{}{}{}{}{}{}".format(_name, getDHMTime(), lat, _symbol[0], long, _symbol[1],
                                     _comment)
