#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
"""monitor APRS packets on a TNC"""

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
import aprslib

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")
logcomms = logging.getLogger("comms")

import radio_scripts.base.comm
import radio_scripts.aprs.config
import radio_scripts.aprs.stats

_appConfig = radio_scripts.aprs.config.APRSConfig()
_appStats = radio_scripts.aprs.stats.APRSStats()
_APRS_filter = None

def _select_filter():
  global _APRS_filter

  for k, v in _appConfig.filters.items():
    if (cliArgs["filter"] == k):
      _APRS_filter = v
  if (_APRS_filter is None):
    logger.warning("Please specify a filter")
    logger.warning("Existing filters are:\n  {}".format("\n  ".join(
        _appConfig.filters.keys())))

  logger.info(f"using APRS filter '{_APRS_filter}'")

def mainApp():
  logger.info(f"using aprslib {aprslib.version_info}")
  _appConfig.readCfg(cliArgs["cfg"])
  if (cliArgs["list"]):
    _appConfig.showInfo()
    return

  _select_filter()
  _appStats.thldFrom = 3
  _appStats.thldTo = 3

  conn = radio_scripts.base.comm.CommInterface(_appConfig.conn)
  conn.eom = "\n"
  conn.open()

  reply = conn.read()
  logger.info(reply[0])
  reply = conn.query(f"user NOCALL pass -1 vers pyAPRSClient 0 filter {_APRS_filter}")
  logger.info(reply[0])

  while (True):
    try:
      reply = conn.read()
      if (not reply[0].startswith("#")):
        packet = aprslib.parse(reply[0])
        #print(f"DBG '{reply[0]}'")
        logger.info(f"{packet['from']: <9} -> {packet['to']: <9} {packet['format']}")
        _appStats.update(packet)
    except radio_scripts.base.comm.CommTimeoutException:
      pass
    except KeyboardInterrupt:
      break
    except (aprslib.ParseError, aprslib.UnknownFormat) as ex:
      logger.warning(ex)
      logger.warning(reply[0])

  conn.close()
  _appStats.showInfo()

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
  appCfgPath = os.path.join(appDir, (modName + ".cfg"))
  #print("[{}] {}".format(modName, appDir))
  #print("[{}] {}".format(modName, appCfgPath))
  #os.chdir(appDir)

  #pyauto_base.misc.changeLoggerName("{}.log".format(modName))

  appDesc = ""
  parser = argparse.ArgumentParser(description=appDesc)
  #parser.add_argument("action", help="action",
  #                    choices=("info", ""))
  parser.add_argument("-f", "--cfg", default=appCfgPath, help="configuration file path")
  parser.add_argument("-l",
                      "--list",
                      action="store_true",
                      default=False,
                      help="list config file options")
  parser.add_argument("-t", "--filter", default="", help="filter name")
  #parser.add_argument("-x", "--extra",
  #                    choices=("", ""),
  #                    help="extra parameters")

  cliArgs = vars(parser.parse_args())
  #logger.info(cliArgs)

  #parser.print_help()
  mainApp()
