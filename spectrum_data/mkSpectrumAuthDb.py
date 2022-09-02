#!/usr/bin/env python3
# template: app_log
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Converts csv file from
http://www.ic.gc.ca/engineering/SMS_TAFL_Files/TAFL_LTAF.zip
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
#import argparse
import csv
import dataset

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")

_dirRead = os.path.join("data_in", "spectrum_auth")
_dirReadSupport = "support"
_dirWrite = "data_out"
_dbOut = os.path.join(_dirWrite, "canada_auth.sqlite")

def _hardcoded_data():
  lstKeys = ("code", "en", "fr")

  for f in os.listdir(_dirReadSupport):
    if (not f.endswith(".csv")):
      continue
    with dataset.connect("sqlite:///{}".format(_dbOut)) as db:
      tblName = f[:-4]
      table = db[tblName]
      logger.info("table {}".format(tblName))
      with open(os.path.join(_dirReadSupport, f), "r") as fIn:
        csvIn = csv.reader(fIn)
        for row in csvIn:
          table.insert(dict(zip(lstKeys, row)))

def mainApp():
  if (not os.path.isdir(_dirWrite)):
    os.mkdir(_dirWrite)
  else:
    if (os.path.isfile(_dbOut)):
      os.remove(_dbOut)

  t0 = datetime.datetime.now()

  _hardcoded_data()

  fPath = os.path.join(_dirRead, "TAFL_LTAF.csv")
  tblName = "TAFL_LTAF"
  logger.info("convert {} to {}:{}".format(fPath, _dbOut, tblName))
  lstKeys = ("Function", "Freq", "FRI", "Reg_Service", "Comm_Type", "Conformity",
             "Freq_Alloc_Name", "Ch", "ICN", "A/D", "BW", "Emmision", "Modulation",
             "Filtration", "ERP", "TX_Pow", "Losses", "Analog_Cap", "Digital_Cap",
             "RX_Unfaded_Lvl", "RX_BER_Lvl", "Ant_Mfr", "Ant_Model", "Ant_Gain",
             "Ant_Pattern", "Ant_Beam", "Ant_FtoB", "Ant_Polarization", "Ant_Height",
             "Ant_Azimuth", "Ant_Elevation", "Sta_Location", "Sta_Licensee",
             "Sta_Call_Sign", "Sta_Type", "Sta_ITU_Type", "Sta_Cost", "Sta_Cnt",
             "Sta_Reference", "Sta_Province", "Sta_Lat", "Sta_Long", "Sta_Elevation",
             "Sta_Height", "Sta_Congestion", "Sta_Radius", "Sta_Sattelite", "Auth_No",
             "Auth_Service", "Auth_Subservice", "Auth_Lic_Type", "Auth_Status", "Auth_Date",
             "Acct_No", "Acct_Licensee", "Acct_Address", "Bcst_Op_Sts", "Bcst_Class",
             "Bcst_H_Pwr", "Bcst_V_Pwr", "Bcst_StandBy")
  with dataset.connect("sqlite:///{}".format(_dbOut)) as db:
    table = db[tblName]
    with open(fPath, "r") as fIn:
      csvIn = csv.reader(fIn)
      for row in csvIn:
        table.insert(dict(zip(lstKeys, row)))
        if ((csvIn.line_num % 10000) == 0):
          logger.info("read {} line(s)".format(csvIn.line_num))
      logger.info("{} line(s) added to db".format(csvIn.line_num))

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
