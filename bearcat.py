#!/usr/bin/env python3
# template: app_log
# SPDX-License-Identifier: GPL-3.0-or-later
"""app"""

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
import argparse
import serial
import json
import csv

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")

class AppConfig(object):

  def __init__(self):
    self.dirRead = "read"
    self.dirWrite = "write"

  def init(self):
    if (not os.path.isdir(self.dirRead)):
      os.mkdir(self.dirRead)
    if (not os.path.isdir(self.dirWrite)):
      os.mkdir(self.dirWrite)

appCfg = AppConfig()

class Channel(object):

  def __init__(self):
    self.idx = 0
    self.freq = 0  # integer, in Hz
    self.tag = None
    self.modulation = None
    self.squelch_code = None
    self.delay = None
    self.lockout = None
    self.priority = None

  def __str__(self):
    return "CH {}, '{}', {} Hz, {}".format(self.idx, self.tag, self.freq, self.modulation)

  def init(self, idx, freq, tag, modulation, squelch_code):
    if (not isinstance(idx, int)):
      raise RuntimeError
    if (idx <= 0):
      raise RuntimeError
    if (not isinstance(freq, int)):
      raise RuntimeError
    if (freq < 0):
      raise RuntimeError
    if (not isinstance(tag, str)):
      raise RuntimeError
    if (not isinstance(modulation, str)):
      raise RuntimeError
    if (not isinstance(squelch_code, int)):
      raise RuntimeError

    self.idx = idx
    self.freq = freq
    self.tag = tag
    self.modulation = modulation
    self.squelch_code = squelch_code
    self.delay = 2
    self.lockout = 0
    self.priority = 0

_mdl_BC125AT = "BC125AT"

class BC125AT(object):

  def __init__(self):
    self.dev = None
    self.baudrate = 115200
    self.timeout = 0.05
    self.eos = "\r"
    self.eom = "\r"
    self.model = _mdl_BC125AT
    self.nCh = 500
    self._conn = None
    self._config = {}

  def _saveChannels_json(self, lstCh, fPath):
    with open(fPath, "w") as fOut:
      fOut.write("[\n")
      for i in range(len(lstCh)):
        fOut.write("  {}{}\n".format(json.dumps(lstCh[i].__dict__), "" if
                                     (i == (len(lstCh) - 1)) else ","))
      fOut.write("]\n")
    logger.info("{} written".format(fPath))

  def _saveChannels_csv(self, lstCh, fPath):
    lstKeys = ("index", "freq", "tag", "modulation", "squelch_code", "delay", "lockout",
               "priority")
    with open(fPath, "w") as fOut:
      csvOut = csv.writer(fOut, lineterminator="\n")
      csvOut.writerow(lstKeys)
      for ch in lstCh:
        csvOut.writerow([
            ch.idx, ch.freq, ch.tag, ch.modulation, ch.squelch_code, ch.delay, ch.lockout,
            ch.priority
        ])
    logger.info("{} written".format(fPath))

  def _loadChannels_json(self):
    dirOut = "channels_in"
    fPath = os.path.join(dirOut, (self.model + ".json"))

    if (not os.path.isfile(fPath)):
      raise RuntimeError

    lstCh = []
    res = json.load(open(fPath))
    for val in res:
      ch = Channel()
      ch.__dict__.update(val)
      lstCh.append(ch)

    return lstCh

  def read(self):
    res = self._conn.read_until(self.eom).decode()
    return res.strip(self.eom)

  def write(self, cmd):
    self._conn.write((cmd + self.eos).encode())

  def query(self, cmd):
    self.write(cmd)
    return self.read()

  def connect(self):
    self._conn = serial.Serial(port=self.dev, baudrate=self.baudrate, timeout=self.timeout)
    if (not self._conn.isOpen()):
      raise RuntimeError

    res = self.query("MDL")
    res = res.split(",")[1]
    if (res != self.model):
      msg = "model MISMATCH: expected '{}', found '{}'".format(self.model, res)
      logger.error(msg)
      raise RuntimeError(msg)
    res = self.query("VER")
    logger.info("FW {}".format(res.split()[1]))

  def disconnect(self):
    if (self._conn is None):
      return
    self._conn.close()

  def readConfig(self):
    res = self.query("PRG")
    if (res != "PRG,OK"):
      raise RuntimeError

    logger.info("reading configuration ...")
    # TODO:

    res = self.query("EPG")
    if (res != "EPG,OK"):
      raise RuntimeError

  def readChannels(self):
    res = self.query("PRG")
    if (res != "PRG,OK"):
      raise RuntimeError

    logger.info("reading channels ...")
    lstCh = []
    for i in range(1, (self.nCh + 1)):
      #for i in range(1, 51):
      res = self.query("CIN,{}".format(i))
      res = res.split(",")

      ch = Channel()
      ch.init(int(res[1]), (int(res[3]) * 100), res[2], res[4], int(res[5]))
      ch.delay = int(res[6])
      ch.lockout = int(res[7])
      ch.priority = int(res[8])
      lstCh.append(ch)

    res = self.query("EPG")
    if (res != "EPG,OK"):
      raise RuntimeError

    logger.info("read {} channel(s)".format(len(lstCh)))
    self._saveChannels_json(
        lstCh, os.path.join(appCfg.dirRead, "{}_channels.json".format(self.model)))
    self._saveChannels_csv(
        lstCh, os.path.join(appCfg.dirRead, "{}_channels.csv".format(self.model)))

  def writeChannels(self):
    lstCh = self._loadChannels_json()
    bCheck = True
    for ch in lstCh:
      if (len(ch.tag) > 16):
        msg = "INCORRECT tag for {}".format(ch)
        logger.error(msg)
        bCheck = False
    if (not bCheck):
      raise RuntimeError

    res = self.query("PRG")
    if (res != "PRG,OK"):
      raise RuntimeError

    logger.info("writing channels ...")
    for ch in lstCh:
      new = "CIN,{},{},{:08d},{},{},{},{},{}".format(ch.idx, ch.tag, (ch.freq // 100),
                                                     ch.modulation, ch.squelch_code,
                                                     ch.delay, ch.lockout, ch.priority)
      res = self.query("CIN,{}".format(ch.idx))
      if (new != res):
        res = self.query(new)
        if (res != "CIN,OK"):
          raise RuntimeError

    res = self.query("EPG")
    if (res != "EPG,OK"):
      raise RuntimeError

def mainApp():
  appCfg.init()

  if (cliArgs["model"] == _mdl_BC125AT):
    scanner = BC125AT()
    scanner.dev = cliArgs["dev"]
  else:
    raise RuntimeError

  t0 = datetime.datetime.now()

  try:
    scanner.connect()
    if (cliArgs["action"] == "show"):
      pass
    elif (cliArgs["action"] == "cfg"):
      scanner.readConfig()
    elif (cliArgs["action"] == "get"):
      scanner.readChannels()
    elif (cliArgs["action"] == "set"):
      scanner.writeChannels()
    else:
      raise RuntimeError
  finally:
    scanner.disconnect()

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

  appDesc = ""  # _REGEX_  appDesc = \".*\"
  parser = argparse.ArgumentParser(description=appDesc)
  parser.add_argument("model", help="scanner model", choices=(_mdl_BC125AT, ))
  parser.add_argument("dev", help="COM port/device")
  parser.add_argument("action", help="action", choices=("show", "get", "set", "cfg"))
  #parser.add_argument("-f", "--cfg", default=appCfgPath,
  #                    help="configuration file path")
  #parser.add_argument("-l", "--list", action="store_true", default=False,
  #                    help="list config file options")
  #parser.add_argument("-x", "--extra",
  #                    choices=("", ""),
  #                    help="extra parameters")

  cliArgs = vars(parser.parse_args())
  #logger.info(cliArgs)

  #parser.print_help()
  mainApp()
