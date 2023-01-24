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

logger = logging.getLogger("lib")

def mkMessage(toCall, msg, mId=""):
  if (len(toCall) > 9):
    _to = toCall[:9]
  else:
    _to = toCall
  _msg = msg.replace("|", "").translate({'|': '', '~': '', '{': ''})
  if (len(msg) > 67):
    _msg = msg[:67]
  else:
    _msg = msg
  if (len(mId) == 0):
    return ":{: <9}:{}".format(_to, _msg)
  else:
    return ":{: <9}:{}\{{:0<5}".format(_to, _msg)

def mkBulletin(bId, msg):
  if (len(bId) > 1):
    _id = bId[0]
  else:
    _id = bId
  _msg = msg.replace("|", "").translate({'|': '', '~': '', '{': ''})
  if (len(msg) > 67):
    _msg = msg[:67]
  else:
    _msg = msg
  return ":BLN{}     :{}".format(_id, _msg)

def mkStatus(text):
  _text = text.replace("|", "").translate({'|': '', '~': ''})
  if (len(text) > 62):
    _text = text[:62]
  else:
    _text = text
  return ">{}".format(_text)

def mkPositionNoTS(lat, long, comment):
  if (len(comment) > 43):
    _comment = comment[:43]
  else:
    _comment = comment
  return "={}/{}Q{}".format(lat, long, _comment)
