#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
"""monitor APRS packets"""

#import site #http://docs.python.org/library/site.html
import sys
import os
#import platform
import logging
import logging.config
#import re
import time
#import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv
import argparse
import configparser
import aprslib

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")
logcomms = logging.getLogger("comms")

import radio_scripts.base.comm
import radio_scripts.aprs.base
import radio_scripts.aprs.kiss

_URL = None
_MYCALL = None

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

  conn = radio_scripts.base.comm.CommInterface(_URL)
  #conn.eom = "\n"
  conn.open()

  try:
    while (1):
      try:
        res = conn.readRaw("", bBytes=True)
        if (len(res) == 0):
          continue
        lst_frames = radio_scripts.aprs.kiss.splitFrames(res)
        for frm in lst_frames:
          [dstAddr, srcAddr, routing, content] = radio_scripts.aprs.kiss.parseFrame(frm)
          raw_pkt = "{}>{},{}:{}".format(srcAddr, dstAddr, routing, content)
          #logger.info("{}>{}".format(srcAddr, dstAddr))
          #logger.info(raw_pkt)
          packet = aprslib.parse(raw_pkt)
          logger.info(f"{packet['from']: <9} -> {packet['to']: <9} {packet['format']}")
      except radio_scripts.base.comm.CommTimeoutException:
        pass
      except (aprslib.exceptions.ParseError, aprslib.exceptions.UnknownFormat) as ex:
        logger.warning(ex)
        logger.warning(raw_pkt)
        pass
      time.sleep(0.5)
  except KeyboardInterrupt:
    pass

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
  parser.add_argument("dstcall", help="destination call", nargs="?", default="APN000")
  parser.add_argument("message", help="message", nargs="?", default="APRS TEST MESSAGE")
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
