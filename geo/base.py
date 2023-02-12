#!/usr/bin/env python
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

import math
#import csv

logger = logging.getLogger("lib")

_grid_upper = "ABCDEFGHIJKLMNOPQRSTUVWX"
_grid_lower = "abcdefghijklmnopqrstuvwx"

def dms2signed(degree, minute, second):
  """
  :param degree:
  :param minute:
  :param second:
  :return:
  """
  if ((degree < 0.0) or (degree > 179.0)):
    raise NotImplementedError
  if ((minute < 0.0) or (minute > 60.0)):
    raise NotImplementedError
  if ((second < 0.0) or (second > 60.0)):
    raise NotImplementedError

  return round(float(degree) + float(minute / 60.0) + float(second / 3600.0), 6)

def signed2dms(value):
  if ((value < -180.0) or (value > 180.0)):
    raise NotImplementedError

  tmp = [math.fabs(v) for v in math.modf(value)]
  degree = int(tmp[1])
  tmp = [math.fabs(v) for v in math.modf(60.0 * tmp[0])]
  minute = int(tmp[1])
  tmp = [math.fabs(v) for v in math.modf(60.0 * tmp[0])]
  second = int(tmp[1])
  return [degree, minute, second]

def maidenhead(dec_lat, dec_lon):
  """
  Convert latitude and longitude to Maidenhead grid locators.

  Arguments are in signed decimal latitude and longitude. For example,
  the location of my QTH Palo Alto, CA is: 37.429167, -122.138056 or
  in degrees, minutes, and seconds: 37° 24' 49" N 122° 6' 26" W

  written by Walter Underwood K6WRU
  Found on https://ham.stackexchange.com/questions/221/how-can-one-convert-from-lat-long-to-grid-square

  :param dec_lat:
  :param dec_lon:
  :return: Maidenhead string
  """
  if not (-180 <= dec_lon < 180):
    sys.stderr.write('longitude must be -180<=lon<180, given %f\n' % dec_lon)
    sys.exit(32)
  if not (-90 <= dec_lat < 90):
    sys.stderr.write('latitude must be -90<=lat<90, given %f\n' % dec_lat)
    sys.exit(33)  # can't handle north pole, sorry, [A-R]

  adj_lat = dec_lat + 90.0
  adj_lon = dec_lon + 180.0

  grid_lat_sq = _grid_upper[int(adj_lat / 10)]
  grid_lon_sq = _grid_upper[int(adj_lon / 20)]

  grid_lat_field = str(int(adj_lat % 10))
  grid_lon_field = str(int((adj_lon / 2) % 10))

  adj_lat_remainder = (adj_lat - int(adj_lat)) * 60
  adj_lon_remainder = ((adj_lon) - int(adj_lon / 2) * 2) * 60

  grid_lat_subsq = _grid_lower[int(adj_lat_remainder / 2.5)]
  grid_lon_subsq = _grid_lower[int(adj_lon_remainder / 5)]

  return grid_lon_sq + grid_lat_sq + grid_lon_field + grid_lat_field + grid_lon_subsq + grid_lat_subsq
