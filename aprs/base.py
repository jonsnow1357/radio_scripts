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

def getDHMTime():
  dt = datetime.datetime.now(datetime.timezone.utc)
  return "{}{}{}z".format(dt.day, dt.hour, dt.minute)

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

def mkPositionNoTS(lat, long, comment):
  if (len(comment) > 43):
    _comment = comment[:43]
  else:
    _comment = comment
  return "={}/{}Q{}".format(lat, long, _comment)
