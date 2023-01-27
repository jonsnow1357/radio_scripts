#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
"""APRS client"""

#import site #http://docs.python.org/library/site.html
import sys
import os
#import platform
import logging
import logging.config
import re
#import time
#import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv
import argparse
import aprslib
import configparser

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")
logcomms = logging.getLogger("comms")

import radio_scripts.base.comm

_dictFromStats = {}
_dictToStats = {}
_URL = None
_APRS_filter = None

def _config():
  global _URL, _APRS_filter

  fPath = os.path.realpath(cliArgs["cfg"])
  logger.info("using config file: {}".format(fPath))

  cfgObj = configparser.ConfigParser()
  cfgObj.optionxform = str  # will be case sensitive
  cfgObj.read(fPath, encoding="utf-8")

  if ("conn" in cfgObj["default"].keys()):
    _URL = cfgObj["default"]["conn"]
  else:
    msg = "server connection NOT DEFINED"
    logger.error(msg)
    raise RuntimeError(msg)

  for k, v in cfgObj["filter"].items():
    if (cliArgs["filter"] == k):
      _APRS_filter = v
  if (_APRS_filter is None):
    logger.warning("Please specify a filter")
    logger.warning("Existing filters are:\n  {}".format("\n  ".join(
        cfgObj["filter"].keys())))

  logger.info(f"using APRS filter '{_APRS_filter}'")

def _updateStats(packet):
  if (packet["from"] in _dictFromStats.keys()):
    _dictFromStats[packet["from"]] += 1
  else:
    _dictFromStats[packet["from"]] = 1
  if (packet["to"] in _dictToStats.keys()):
    _dictToStats[packet["to"]] += 1
  else:
    _dictToStats[packet["to"]] = 1

_THR_FROM = 3
_THR_TO = 3

def _showStats():
  res = dict([(k, v) for k, v in _dictFromStats.items() if (v > _THR_FROM)])
  if (len(res) > 0):
    logger.info("FROM stats (> {} msg):".format(_THR_FROM))
    for k, v in res.items():
      logger.info(f"  {k: <9} - {v} message(s)")

  res = dict([(k, v) for k, v in _dictToStats.items() if (v > _THR_TO)])
  if (len(res) > 0):
    logger.info("TO stats (> {} msg):".format(_THR_TO))
    for k, v in res.items():
      logger.info(f"  {k: <9} - {v} message(s)")

def mainApp():
  logger.info(f"using aprslib {aprslib.version_info}")
  _config()

  conn = radio_scripts.base.comm.CommInterface(_URL)
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
        _updateStats(packet)
    except radio_scripts.base.comm.CommTimeoutException:
      pass
    except KeyboardInterrupt:
      break
    except (aprslib.ParseError, aprslib.UnknownFormat) as ex:
      logger.warning(ex)
      logger.warning(reply[0])

  conn.close()
  _showStats()

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
  parser.add_argument("-l", "--filter", default="", help="filter name")
  #parser.add_argument("-l", "--list", action="store_true", default=False,
  #                    help="list config file options")
  #parser.add_argument("-x", "--extra",
  #                    choices=("", ""),
  #                    help="extra parameters")

  cliArgs = vars(parser.parse_args())
  #logger.info(cliArgs)

  #parser.print_help()
  mainApp()
