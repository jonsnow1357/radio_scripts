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
import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv

logger = logging.getLogger("lib")

import radio_scripts.geo.base

_SYM_48_TBD = ["/", "Q"]

_symbol = _SYM_48_TBD

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
  res = radio_scripts.geo.base.signed2dms(lat)
  if (lat > 0.0):
    _lat = "{:0>2}{:0>2}.{:0>2}N".format(res[0], res[1], res[2])
  else:
    _lat = "{:0>2}{:0>2}.{:0>2}S".format(res[0], res[1], res[2])
  res = radio_scripts.geo.base.signed2dms(long)
  if (long > 0.0):
    _long = "{:0>3}{:0>2}.{:0>2}E".format(res[0], res[1], res[2])
  else:
    _long = "{:0>3}{:0>2}.{:0>2}W".format(res[0], res[1], res[2])

  if (len(comment) > 43):
    _comment = comment[:43]
  else:
    _comment = comment

  if (bTS):
    return "@{}{}{}{}{}{}".format(getDHMTime(), _lat, _symbol[0], _long, _symbol[1],
                                  _comment)
  else:
    return "!{}{}{}{}{}".format(_lat, _symbol[0], _long, _symbol[1], _comment)
