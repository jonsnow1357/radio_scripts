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

logger = logging.getLogger("lib")

def convertStringNonPrint(s):
  if (isinstance(s, bytes) or isinstance(s, bytearray)):
    s = s.decode("utf-8", errors="ignore")

  if (not isinstance(s, str)):
    msg = "NOT a string: {}".format(s)
    logger.error(msg)
    raise RuntimeError(msg)

  return s.replace("\r", "<CR>").replace("\n", "<LF>")\
      .replace("\f", "<FF>").replace("\b", "<BS>").replace("\t", "<TAB>")\
      .replace("\x1B", "<ESC>")
