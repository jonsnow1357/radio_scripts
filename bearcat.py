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
import time
import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
import csv
import argparse
import serial
import copy
import json

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")
logcomms = logging.getLogger("comms")

import radio_scripts.base as base

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

class ScannerException(Exception):
  pass

_mdl_BC125AT = "BC125AT"

def _getConfig_val(dictionary, msg, key):
  try:
    return dictionary[key]
  except KeyError:
    pass

  tmp = "CANNOT find {} in {}\n  allowed values: {}".format(key, msg,
                                                            list(dictionary.keys()))
  logger.error(tmp)
  raise RuntimeError(tmp)

def _getConfig_key(dictionary, msg, val):
  for k, v in dictionary.items():
    if (val == v):
      return k

  tmp = "CANNOT map {} to {}".format(val, msg)
  logger.error(tmp)
  raise RuntimeError(tmp)

class BC125AT(object):

  def __init__(self):
    self.model = _mdl_BC125AT
    self.nCh = 500
    self.tagSize = 16

    fPath = os.path.join("scanners", (self.model + ".json"))
    tmp = json.load(open(fPath, "r"))

    self.dev = None
    self.conn_speed = tmp["connection"]["speed"]
    self.conn_to = tmp["connection"]["timeout"]
    self.eos = "\r"
    self.eom = "\r"
    self._conn = None
    self.config = {}

    self._map_squelch = tmp["map_squelch"]
    self._map_backlight = tmp["map_backlight"]
    self._map_keypad_beep = tmp["map_keypad_beep"]
    self._map_keypad_lock = tmp["map_keypad_lock"]
    self._map_priority_mode = tmp["map_priority_mode"]

  def _saveChannels_json(self, lstCh, fPath):
    with open(fPath, "w") as fOut:
      fOut.write("[\n")
      for i, ch in enumerate(lstCh):
        tmp = copy.deepcopy(ch.__dict__)  # copy class variables so we can change freq
        tmp["freq"] = round((tmp["freq"] / 1e6), 6)
        tmp["squelch_code"] = _getConfig_key(self._map_squelch, "squelch_code",
                                             tmp["squelch_code"])
        fOut.write("  {}{}\n".format(json.dumps(tmp), "" if
                                     (i == (len(lstCh) - 1)) else ","))
      fOut.write("]\n")
    logger.info("{} written".format(fPath))

  def _saveChannels_csv(self, lstCh, fPath):
    lstKeys = ("idx", "freq", "tag", "modulation", "squelch_code", "delay", "lockout",
               "priority")
    with open(fPath, "w") as fOut:
      csvOut = csv.writer(fOut, lineterminator="\n")
      csvOut.writerow(lstKeys)
      for ch in lstCh:
        freq = round((ch.freq / 1e6), 6)
        squelch_code = _getConfig_key(self._map_squelch, "squelch_code", ch.squelch_code)
        csvOut.writerow([
            ch.idx, freq, ch.tag, ch.modulation, squelch_code, ch.delay, ch.lockout,
            ch.priority
        ])
    logger.info("{} written".format(fPath))

  def _loadChannels_json(self, fPath):
    if (not os.path.isfile(fPath)):
      raise ScannerException

    lstCh = []
    res = json.load(open(fPath))
    for val in res:
      freq = int(val["freq"] * 1e6)
      squelch_code = self._map_squelch[val["squelch_code"]]

      ch = base.Channel()
      ch.init(val["idx"], freq, val["tag"], val["modulation"], squelch_code)
      ch.delay = val["delay"]
      ch.lockout = val["lockout"]
      ch.priority = val["priority"]
      lstCh.append(ch)
      #print("DBG", ch)

    return lstCh

  def _loadChannels_csv(self, fPath):
    if (not os.path.isfile(fPath)):
      raise ScannerException

    lstCh = []
    lstKeys = []
    with open(fPath, "r") as fIn:
      csvIn = csv.reader(fIn)
      for row in csvIn:
        if (lstKeys == []):
          lstKeys = row
        else:
          val = dict(zip(lstKeys, row))
          try:
            idx = int(val["idx"])
          except ValueError:
            continue
          freq = int(float(val["freq"]) * 1e6)
          squelch_code = self._map_squelch[val["squelch_code"]]

          ch = base.Channel()
          ch.init(idx, freq, val["tag"], val["modulation"], squelch_code)
          ch.delay = val["delay"]
          ch.lockout = val["lockout"]
          ch.priority = val["priority"]
          lstCh.append(ch)
          #print("DBG", ch)

    return lstCh

  def _saveConfig_json(self, fPath):
    with open(fPath, "w") as fOut:
      json.dump(self.config, fOut, indent=2)
    logger.info("{} written".format(fPath))

  def _loadConfig_json(self, fPath):
    if (not os.path.isfile(fPath)):
      raise ScannerException

    self.config = json.load(open(fPath))

  def read(self):
    res = self._conn.read_until(self.eom).decode()
    logcomms.info("{}>>>{}".format(self.dev, res))
    return res.strip(self.eom)

  def write(self, cmd):
    logcomms.info("{}<<<{}".format(self.dev, cmd))
    self._conn.write((cmd + self.eos).encode())

  def query(self, cmd, timeout=0):
    self.write(cmd)
    if (timeout > 0.0):
      time.sleep(timeout)
    return self.read()

  def connect(self):
    self._conn = serial.Serial(port=self.dev,
                               baudrate=self.conn_speed,
                               timeout=self.conn_to)
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
    logger.info("reading configuration ...")
    res = self.query("VOL")
    self.config["volume"] = int(res.split(",")[-1])
    res = self.query("SQL")
    self.config["squelch"] = int(res.split(",")[-1])

    res = self.query("PRG")
    if (res != "PRG,OK"):
      raise RuntimeError

    res = self.query("CNT")
    self.config["contrast"] = int(res.split(",")[-1])
    res = self.query("BLT")
    self.config["backlight"] = _getConfig_key(self._map_backlight, "backlight",
                                              res.split(",")[-1])
    res = self.query("WXS")
    self.config["weather"] = {"priority": int(res.split(",")[-1])}
    res = self.query("BSV")
    self.config["charge_time"] = int(res.split(",")[-1])
    res = self.query("KBP")
    self.config["keypad"] = {
        "beep": _getConfig_key(self._map_keypad_beep, "keypad_beep",
                               res.split(",")[-2]),
        "lock": _getConfig_key(self._map_keypad_lock, "keypad_lock",
                               res.split(",")[-1])
    }
    res = self.query("PRI")
    self.config["priority_mode"] = _getConfig_key(self._map_priority_mode, "priority_mode",
                                                  res.split(",")[-1])

    res = self.query("SCG")
    self.config["scan_group"] = res.split(",")[-1]

    res = self.query("EPG")
    if (res != "EPG,OK"):
      raise RuntimeError

    self._saveConfig_json(os.path.join(appCfg.dirRead, "{}_config.json".format(self.model)))

  def writeConfig(self):
    fPath = os.path.join(appCfg.dirWrite, "{}_config.json".format(self.model))
    try:
      self._loadConfig_json(fPath)
    except ScannerException:
      logger.warning("'{}' not found".format(fPath))
      return

    logger.info("writing configuration ...")
    if ("volume" in self.config.keys()):
      res = self.query("VOL,{}".format(self.config["volume"]))
      if (res != "VOL,OK"):
        raise RuntimeError
    if ("squelch" in self.config.keys()):
      res = self.query("SQL,{}".format(self.config["squelch"]))
      if (res != "SQL,OK"):
        raise RuntimeError

    res = self.query("PRG")
    if (res != "PRG,OK"):
      raise RuntimeError

    if ("contrast" in self.config.keys()):
      res = self.query("CNT,{}".format(self.config["contrast"]))
      if (res != "CNT,OK"):
        raise RuntimeError
    if ("backlight" in self.config.keys()):
      tmp = _getConfig_val(self._map_backlight, "backlight", self.config["backlight"])
      res = self.query("BLT,{}".format(tmp))
      if (res != "BLT,OK"):
        raise RuntimeError
    if ("weather" in self.config.keys()):
      tmp_dict = self.config["weather"]
      res = self.query("WXS,{}".format(tmp_dict["priority"]))
      if (res != "WXS,OK"):
        raise RuntimeError
    if ("charge_time" in self.config.keys()):
      res = self.query("BSV,{}".format(self.config["charge_time"]))
      if (res != "BSV,OK"):
        raise RuntimeError
    if ("keypad" in self.config.keys()):
      tmp_dict = self.config["keypad"]
      res = self.query("KBP,{},{}".format(
          _getConfig_val(self._map_keypad_beep, "keypad_beep", tmp_dict["beep"]),
          _getConfig_val(self._map_keypad_lock, "keypad_lock", tmp_dict["lock"])))
      if (res != "KBP,OK"):
        raise RuntimeError
    if ("priority_mode" in self.config.keys()):
      tmp = _getConfig_val(self._map_priority_mode, "priority_mode",
                           self.config["priority_mode"])
      res = self.query("PRI,{}".format(tmp))
      if (res != "PRI,OK"):
        raise RuntimeError

    if ("scan_group" in self.config.keys()):
      res = self.query("SCG,{}".format(self.config["scan_group"]), timeout=0.1)
      if (res != "SCG,OK"):
        raise RuntimeError

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

      ch = base.Channel()
      ch.init(int(res[1]), (int(res[3]) * 100), res[2], res[4], res[5])
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
    try:
      lstCh = self._loadChannels_json(
          os.path.join(appCfg.dirWrite, "{}_channels.json".format(self.model)))
    except ScannerException:
      logger.warning("json file not found, looking for csv")
      lstCh = self._loadChannels_csv(
          os.path.join(appCfg.dirWrite, "{}_channels.csv".format(self.model)))

    bCheck = True
    for ch in lstCh:
      if (len(ch.tag) > self.tagSize):
        msg = "INCORRECT tag for {}".format(ch)
        logger.error(msg)
        bCheck = False
    if (not bCheck):
      raise RuntimeError

    res = self.query("PRG")
    if (res != "PRG,OK"):
      raise RuntimeError

    logger.info("writing channels ...")
    cnt_ch = 0
    for ch in lstCh:
      if (ch.freq == 0):
        res = self.query("CIN,{}".format(ch.idx))
        if (not res.endswith(",,00000000,AUTO,0,2,1,0")):
          res = self.query("DCH,{}".format(ch.idx))
          if (res != "DCH,OK"):
            raise RuntimeError
          cnt_ch += 1
      else:
        if (ch.lockout != "0"):
          logger.warning("{} is locked-out".format(ch))

        new = "CIN,{},{},{:08d},{},{},{},{},{}".format(ch.idx, ch.tag, (ch.freq // 100),
                                                       ch.modulation, ch.squelch_code,
                                                       ch.delay, ch.lockout, ch.priority)
        res = self.query("CIN,{}".format(ch.idx))
        if (res != new):
          res = self.query(new)
          if (res != "CIN,OK"):
            msg = "ERROR at {}".format(ch)
            logger.error(msg)
            raise RuntimeError(msg)
          cnt_ch += 1
    logger.info("updated {} channel(s)".format(cnt_ch))

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
      scanner.writeConfig()
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

  appDesc = ""
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
