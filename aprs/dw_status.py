#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
"""send APRS status using a TNC"""

#import site #http://docs.python.org/library/site.html
import sys
import os
#import platform
import logging
import logging.config
#import re
#import time
import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv
import argparse
import configparser

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")
logcomms = logging.getLogger("comms")

import radio_scripts.base.comm
import radio_scripts.aprs.base
import radio_scripts.aprs.kiss

_URL = None
_MYCALL = None
VIA = "WIDE1-1,WIDE2-1"

def _config():
  global _URL, _MYCALL

  fPath = os.path.realpath(cliArgs["cfg"])
  logger.info("using config file: {}".format(fPath))

  cfgObj = configparser.ConfigParser()
  cfgObj.optionxform = str  # will be case sensitive
  cfgObj.read(fPath, encoding="utf-8")

  if ("conn" in cfgObj["default"].keys()):
    _URL = cfgObj["default"]["conn"]
  else:
    msg = "TNC connection NOT DEFINED"
    logger.error(msg)
    raise RuntimeError(msg)

  if ("mycall" in cfgObj["default"].keys()):
    _MYCALL = cfgObj["default"]["mycall"]
  else:
    msg = "MYCALL NOT DEFINED"
    logger.error(msg)
    raise RuntimeError(msg)

def mainApp():
  _config()

  #logger.info("{}->{} '{}'".format(_MYCALL, cliArgs["dstcall"], cliArgs["message"]))
  conn = radio_scripts.base.comm.CommInterface(_URL)
  #conn.eom = "\n"
  conn.open()

  data = radio_scripts.aprs.base.mkStatus(cliArgs["status"])
  #print("DBG", data)

  kiss_frame = radio_scripts.aprs.kiss.mkFrame("BEACON", _MYCALL, VIA, data)
  conn.write(kiss_frame)

  conn.close()

if (__name__ == "__main__"):
  modName = os.path.basename(__file__)
  modName = ".".join(modName.split(".")[:-1])

  #print("[{}] {}".format(modName, sys.prefix))
  #print("[{}] {}".format(modName, sys.exec_prefix))
  #print("[{}] {}".format(modName, sys.path))
  #for arg in sys.argv:
  #  print("[{}] {}".format(modName, arg))

  #appDir = sys.path[0]  # folder where the script was invoked
  appDir = os.getcwd()  # current folder
  appCfgPath = os.path.join(appDir, "aprs.cfg")
  #print("[{}] {}".format(modName, appDir))
  #print("[{}] {}".format(modName, appCfgPath))
  #os.chdir(appDir)

  #pyauto_base.misc.changeLoggerName("{}.log".format(modName))

  appDesc = ""
  parser = argparse.ArgumentParser(description=appDesc)
  parser.add_argument("status", help="status", nargs="?", default="APRS node")
  parser.add_argument("-f", "--cfg", default=appCfgPath, help="configuration file path")
  #parser.add_argument("-l", "--list", action="store_true", default=False,
  #                    help="list config file options")
  #parser.add_argument("-x", "--extra",
  #                    choices=("", ""),
  #                    help="extra parameters")

  cliArgs = vars(parser.parse_args())
  #logger.info(cliArgs)

  #parser.print_help()
  mainApp()
