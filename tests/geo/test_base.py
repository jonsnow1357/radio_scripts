#!/usr/bin/env python
# template: unittest
# SPDX-License-Identifier: GPL-3.0-or-later
"""unit testing for ..."""

#import site #http://docs.python.org/library/site.html
import sys
import os
import platform
import logging
import logging.config
#import re
#import time
import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv
import unittest
import json

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")
import radio_scripts.geo.base

class TestGeo_base(unittest.TestCase):
  cwd = None
  lclDir = None

  @classmethod
  def setUpClass(cls):
    cls.cwd = os.getcwd()
    cls.lclDir = os.path.dirname(os.path.realpath(__file__))  # folder where this file is
    os.chdir(cls.lclDir)
    logger.info("CWD: {}".format(os.getcwd()))

  @classmethod
  def tearDownClass(cls):
    os.chdir(cls.cwd)
    logger.info("CWD: {}".format(os.getcwd()))

  def setUp(self):
    print("")
    self.inFolder = os.path.join(self.lclDir, "files")
    self.outFolder = os.path.join(self.lclDir, "data_out")
    if (not os.path.isdir(self.outFolder)):
      os.makedirs(self.outFolder)

  def tearDown(self):
    pass

  #@unittest.skip("")
  def test_base(self):
    lat = radio_scripts.geo.base.dms2signed(45, 25, 30)
    self.assertEqual(lat, 45.425)
    long = radio_scripts.geo.base.dms2signed(75, 41, 55)
    self.assertEqual(long, 75.698611)
    res = radio_scripts.geo.base.maidenhead(lat, (-1.0 * long))
    self.assertEqual(res, "FN25dk")

    res = radio_scripts.geo.base.maidenhead(48.14666, 11.60833)
    self.assertEqual(res, "JN58td")
    res = radio_scripts.geo.base.maidenhead(-34.91, -56.21166)
    self.assertEqual(res, "GF15vc")
    res = radio_scripts.geo.base.maidenhead(38.92, -77.065)
    self.assertEqual(res, "FM18lw")
    res = radio_scripts.geo.base.maidenhead(-41.28333, 174.745)
    self.assertEqual(res, "RE78ir")
    res = radio_scripts.geo.base.maidenhead(41.714775, -72.727260)
    self.assertEqual(res, "FN31pr")
    res = radio_scripts.geo.base.maidenhead(37.413708, -122.1073236)
    self.assertEqual(res, "CM87wj")
