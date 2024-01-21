#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
"""monitor APRS packets on TNC"""

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
import aprslib

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")
logcomms = logging.getLogger("comms")

import radio_scripts.base.comm
import radio_scripts.aprs.base
import radio_scripts.aprs.config
import radio_scripts.aprs.kiss
import radio_scripts.aprs.stats

_appConfig = radio_scripts.aprs.config.APRSConfig()
_appStats = radio_scripts.aprs.stats.APRSStats()
_csv_path = os.path.join(".", "data_out", "aprs.csv")

def _log_start():
  if (not os.path.isdir("data_out")):
    os.mkdir("data_out")
  if (not os.path.isfile(_csv_path)):
    logger.info("creating {}".format(_csv_path))
    with open(_csv_path, "w") as f_out:
      csv_out = csv.writer(f_out, lineterminator="\n")
      csv_out.writerow(["timestamp", "format", "FROM", "TO", "comment"])

def _log_packet(packet):
  global _csv_path

  ts = datetime.datetime.now()
  _csv_path = os.path.join(
      ".", "data_out", "{:04d}-{:02d}-{:02d}_aprs.csv".format(ts.year, ts.month, ts.day))
  _log_start()

  # logger.info(packet)
  logger.info(f"{packet['from']: <9} -> {packet['to']: <9} {packet['format']}")
  comment = ""
  if (packet["format"].startswith("pos")):
    if ("comment" in packet.keys()):
      logger.info(f"  comment: {packet['comment']}")
    if ("weather" in packet.keys()):
      logger.info(f"  weather: {packet['weather']}")
      comment = f"temp {packet['weather']['temperature']}"
  elif (packet["format"] == "beacon"):
    logger.info(f"  text: {packet['text']}")
    comment = packet["text"]
  elif (packet["format"] == "object"):
    logger.info(f"  object: {packet['object_format']},{packet['comment']}")
    comment = f"{packet['object_format']},{packet['comment']}"
  elif (packet["format"] == "status"):
    logger.info(f"  status: {packet['status']}")
    comment = packet["status"]
  elif (packet["format"] == "message"):
    if ("message_text" in packet.keys()):
      logger.info(f"  message to {packet['addresse']}: {packet['message_text']}")
    else:
      logger.info(f"  message to {packet['addresse']}: {packet['response']}")
    comment = packet["addresse"]

  with open(_csv_path, "a") as f_out:
    csv_out = csv.writer(f_out, lineterminator="\n")
    csv_out.writerow([
        ts.strftime("%Y-%m-%dT%H%M%S"), packet["format"], packet["from"], packet["to"],
        comment
    ])

def _log_error(strFrom, strTo, strComment):
  global _csv_path

  ts = datetime.datetime.now()
  _csv_path = os.path.join(
      ".", "data_out", "{:04d}-{:02d}-{:02d}_aprs.csv".format(ts.year, ts.month, ts.day))
  _log_start()

  with open(_csv_path, "a") as f_out:
    csv_out = csv.writer(f_out, lineterminator="\n")
    csv_out.writerow([ts.strftime("%Y-%m-%dT%H%M%S"), "ERROR", strFrom, strTo, strComment])

def mainApp():
  global _csv_path

  logger.info(f"using aprslib {aprslib.version_info}")
  _appConfig.readCfg(cliArgs["cfg"])
  if (cliArgs["list"]):
    _appConfig.showInfo()
    return
  _appStats.thldFrom = 4
  _appStats.thldTo = 4

  conn = radio_scripts.base.comm.CommInterface(_appConfig.conn)
  #conn.eom = "\n"
  conn.open()

  ts = datetime.datetime.now()
  _csv_path = os.path.join(
      ".", "data_out", "{:04d}-{:02d}-{:02d}_aprs.csv".format(ts.year, ts.month, ts.day))
  _log_start()

  try:
    while (True):
      try:
        res = conn.readRaw("", bBytes=True)
      except radio_scripts.base.comm.CommTimeoutException as ex:
        logger.warning(ex)
        continue
      if (len(res) == 0):
        continue

      lst_frames = radio_scripts.aprs.kiss.splitFrames(res)
      for frm in lst_frames:
        dst_addr = ""
        src_addr = ""
        routing = ""
        content = ""
        raw_pkt = ""
        try:
          [dst_addr, src_addr, routing, content] = radio_scripts.aprs.kiss.parseFrame(frm)
          if (routing == ""):
            raw_pkt = "{}>{}:{}".format(src_addr, dst_addr, content)
          else:
            raw_pkt = "{}>{},{}:{}".format(src_addr, dst_addr, routing, content)
          if (content.strip("\n\r") == ""):
            _log_error(src_addr, dst_addr, "empty message")
            continue
          #print("DBG", raw_pkt)
          #logger.info("{}>{}".format(src_addr, dst_addr))
          packet = aprslib.parse(raw_pkt)
          _log_packet(packet)
          _appStats.update(packet)
        except radio_scripts.aprs.kiss.KISSException as ex:
          logger.warning(str(ex) + " (KISS)")
          logger.warning(frm)
          _log_error(src_addr, dst_addr, "decode")
          pass
        except (aprslib.exceptions.ParseError, aprslib.exceptions.UnknownFormat) as ex:
          logger.warning(str(ex) + " (parse)")
          logger.warning(frm)
          _log_error(src_addr, dst_addr, "parse")
          pass
      time.sleep(0.5)
  except KeyboardInterrupt:
    pass

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
  appCfgPath = os.path.join(appDir, "aprs.cfg")
  #print("[{}] {}".format(modName, appDir))
  #print("[{}] {}".format(modName, appCfgPath))
  #os.chdir(appDir)

  #pyauto_base.misc.changeLoggerName("{}.log".format(modName))

  appDesc = ""
  parser = argparse.ArgumentParser(description=appDesc)
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
