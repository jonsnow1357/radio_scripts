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
#import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv
import argparse

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")
logcomms = logging.getLogger("comms")

import radio_scripts.base.comm
import radio_scripts.aprs.base
import radio_scripts.aprs.config
import radio_scripts.aprs.kiss

_appConfig = radio_scripts.aprs.config.APRSConfig()

VIA = "WIDE1-1,WIDE2-1"

def mainApp():
  _appConfig.readCfg(cliArgs["cfg"])
  if (cliArgs["list"]):
    _appConfig.showInfo()
    return

  conn = radio_scripts.base.comm.CommInterface(_appConfig.conn)
  #conn.eom = "\n"
  conn.open()

  data = radio_scripts.aprs.base.mkStatus(cliArgs["status"])
  #print("DBG", data)

  kiss_frame = radio_scripts.aprs.kiss.mkFrame("BEACON", _appConfig.mycall, VIA, data)
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
  parser.add_argument("status", help="status", nargs="?", default="APRS status")
  parser.add_argument("-f", "--cfg", default=appCfgPath, help="configuration file path")
  parser.add_argument("-l",
                      "--list",
                      action="store_true",
                      default=False,
                      help="list config file options")
  #parser.add_argument("-x", "--extra",
  #                    choices=("", ""),
  #                    help="extra parameters")

  cliArgs = vars(parser.parse_args())
  #logger.info(cliArgs)

  #parser.print_help()
  mainApp()
