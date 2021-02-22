#!/usr/bin/env python3
# template: app_log
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Converts DBF files from
http://www.ic.gc.ca/engineering/BC_DBF_FILES/baserad.zip
to a SQLite database
"""

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
#import six
#import argparse
import dbfread
import dataset

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")

_dirRead = os.path.join("data_in", "broadcast")
_dirWrite = "data_out"
_dbOut = os.path.join(_dirWrite, "canada_broadcast.sqlite")

def _toSqlite(fPath):
  tblName = os.path.basename(fPath)[:-4]
  logger.info("convert {} to {}:{}".format(fPath, _dbOut, tblName))

  with dataset.connect("sqlite:///{}".format(_dbOut)) as db:
    table = db[tblName]
    with dbfread.DBF(fPath, encoding="latin1") as dbf:
      for rec in dbf:
        table.insert(rec)

def mainApp():
  if (not os.path.isdir(_dirWrite)):
    os.mkdir(_dirWrite)
  else:
    if (os.path.isfile(_dbOut)):
      os.remove(_dbOut)

  t0 = datetime.datetime.now()

  for f in os.listdir(_dirRead):
    if (not f.lower().endswith(".dbf")):
      continue
    if (f.lower() in ("apatkey.dbf", "city.dbf", "comments.dbf", "contours.dbf",
                      "distbord.dbf", "limcode.dbf", "limcodeextra.dbf", "modcall.dbf")):
      continue
    _toSqlite(os.path.join(_dirRead, f))

  runTime = datetime.datetime.now() - t0
  logger.info("time: {}".format(runTime))

if (__name__ == "__main__"):
  modName = os.path.basename(__file__)
  modName = ".".join(modName.split(".")[:-1])

  #print("[{}] {}".format(modName, sys.prefix))
  #print("[{}] {}".format(modName, sys.exec_prefix))
  #print("[{}] {}".format(modName, sys.path))
  #for arg in sys.argv:
  #  print("[{}] {}".format(modName, arg))

  #appDir = sys.path[0]  # folder where the script was invoked
  #appDir = os.getcwd()  # current folder
  #appCfgPath = os.path.join(appDir, (modName + ".cfg"))
  #print("[{}] {}".format(modName, appDir))
  #print("[{}] {}".format(modName, appCfgPath))
  #os.chdir(appDir)

  #pyauto_base.misc.changeLoggerName("{}.log".format(modName))

  appDesc = ""
  #parser = argparse.ArgumentParser(description=appDesc)
  #parser.add_argument("action", help="action",
  #                    choices=("info", ""))
  #parser.add_argument("-f", "--cfg", default=appCfgPath,
  #                    help="configuration file path")
  #parser.add_argument("-l", "--list", action="store_true", default=False,
  #                    help="list config file options")
  #parser.add_argument("-x", "--extra",
  #                    choices=("", ""),
  #                    help="extra parameters")

  #cliArgs = vars(parser.parse_args())
  #logger.info(cliArgs)

  #parser.print_help()
  mainApp()
