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

#import math
#import csv
# _ANY_ more imports

logger = logging.getLogger("lib")
# _ANY_ more pyauto* imports

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
#
# def usage():
#   print 'This script takes two arguments, decimal latitude and longitude.'
#   print 'Example for Newington, Connecticut (W1AW):'
#   print 'python base.py 41.714775 -72.727260'
#   print 'returns: FN31pr'
#
# def test():
#   # First four test examples are from "Conversion Between Geodetic and Grid Locator Systems",
#   # by Edmund T. Tyson N5JTY QST January 1989
#   test_data = (
#       ('Munich', (48.14666, 11.60833), 'JN58td'),
#       ('Montevideo', (-34.91, -56.21166), 'GF15vc'),
#       ('Washington, DC', (38.92, -77.065), 'FM18lw'),
#       ('Wellington', (-41.28333, 174.745), 'RE78ir'),
#       ('Newington, CT (W1AW)', (41.714775, -72.727260), 'FN31pr'),
#       ('Palo Alto (K6WRU)', (37.413708, -122.1073236), 'CM87wj'),
#   )
#   print 'Running self test\n'
#   passed = True
#   for name, latlon, grid in test_data:
#     print 'Testing %s at %f %f:' % (name, latlon[0], latlon[1])
#     test_grid = to_grid(latlon[0], latlon[1])
#     if test_grid != grid:
#       print 'Failed ' + test_grid + ' should be ' + grid
#       passed = False
#     else:
#       print 'Passed ' + test_grid
#   print ''
#   if passed: print 'Passed!'
#   else: print 'Failed!'
#
# def main(argv=None):
#   if argv is None: argv = sys.argv
#   if len(argv) != 3:
#     usage()
#     print ''
#     test()
#   else:
#     print to_grid(float(argv[1]), float(argv[2]))
#
# main()
