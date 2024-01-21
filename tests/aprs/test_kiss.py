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
import radio_scripts.aprs.kiss

class TestAPRSKISS_base(unittest.TestCase):
  cwd = ""
  lclDir = ""

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
    # TODO:
    #radio_scripts.aprs.kiss.mkFrame("")

    lstB = bytearray(
        b"\xc0\x00\x82\xa0\x88\xaebj\xe0\xac\x8af\xac\xa0\xa8\xf4\xac\x8af\x9e\x86\xa4\xe4\xae\x92\x88\x8ad@a\x03\xf0T#75,12,114,171,0,0,00000000\xc0\xc0\x00\x82\xa0\x88\xaebj\xe0\xac\x8af\xac\xa0\xa8t\xac\x8ad\xa4\x8a\x90\xe8\xac\x8af\x9e\x86\xa4\xe4\xae\x92\x88\x8ad@a\x03\xf0T#75,12,114,171,0,0,00000000\xc0"
    )
    lst_frames = radio_scripts.aprs.kiss.splitFrames(lstB)
    [dstAddr, srcAddr, routing, content] = radio_scripts.aprs.kiss.parseFrame(lst_frames[0])
    self.assertEqual(dstAddr, "APDW15")
    self.assertEqual(srcAddr, "VE3VPT-10")
    self.assertEqual(routing, "VE3OCR-2,WIDE2*")
    self.assertEqual(content, "T#75,12,114,171,0,0,00000000")

    [dstAddr, srcAddr, routing, content] = radio_scripts.aprs.kiss.parseFrame(lst_frames[1])
    self.assertEqual(dstAddr, "APDW15")
    self.assertEqual(srcAddr, "VE3VPT-10")
    self.assertEqual(routing, "VE2REH-4,VE3OCR-2,WIDE2*")
    self.assertEqual(content, "T#75,12,114,171,0,0,00000000")
