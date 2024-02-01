#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
"""app"""

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

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")

_dictModCarrier = {
    "A": "AM (double sideband)",
    "B": "Independent sideband (1 signal for each sideband)",
    "C": "Vestigial sideband",
    "D": "AM + (FM | PM)",
    "F": "FM",
    "G": "PM",
    "H": "SSB with full carrier",
    "J": "SSB with suppressed carrier",
    "K": "PAM (pulse-amplitude)",
    "L": "PWM (pulse-width)",
    "M": "PPM (pulse-position)",
    "N": "Unmodulated carrier",
    "P": "Sequence of pulses without modulation",
    "Q": "Sequence of pulses, with phase or frequency modulation in each pulse",
    "R": "SSB with reduced or variable carrier",
    "V": "Combination of pulse modulation methods",
    "W": "Combination of any of the above",
    "X": "None of the above",
}
_dictModSignal = {
    "0": "No modulating signal",
    "1": "1 digital ch, no subcarrier",
    "2": "1 digital ch, using a subcarrier",
    "3": "1 analog ch",
    "7": "1+ digital ch",
    "8": "1+ analog ch",
    "9": "Combination of analog and digital channels",
    "X": "None of the above",
}
_dictInfo = {
    "A": "Aural telegraphy",
    "B": "Electronic telegraphy",
    "C": "Facsimile (still images)",
    "D": "Data transmission, telemetry or telecommand (remote control)",
    "E": "Telephony",
    "F": "Video",
    "N": "No transmitted information (other than existence of the signal)",
    "W": "Combination of any of the above",
    "X": "None of the above",
}
_dictInfoDetails = {
    "A": "Two-condition code, elements vary in quantity and duration",
    "B": "Two-condition code, elements fixed in quantity and duration",
    "C":
    "Two-condition code, elements fixed in quantity and duration, error-correction included",
    "D": "Four-condition code, one condition per \"signal element\"",
    "E": "Multi-condition code, one condition per \"signal element\"",
    "F": "Multi-condition code, one character represented by one or more conditions",
    "G": "Monophonic broadcast-quality sound",
    "H": "Stereophonic or quadraphonic broadcast-quality sound",
    "J": "Commercial-quality sound (non-broadcast)",
    "K": "Commercial-quality sound—frequency inversion and-or \"band-splitting\" employed",
    "L":
    "Commercial-quality sound, independent FM signals, such as pilot tones, used to control the demodulated signal",
    "M": "Greyscale images or video",
    "N": "Full-color images or video",
    "W": "Combination of two or more of the above",
    "X": "None of the above",
}
_dictMultiplex = {
    "C": "Code-division (excluding spread spectrum)",
    "F": "Frequency-division",
    "N": "None used / not multiplexed",
    "T": "Time-division",
    "W": "Combination of Frequency-division and Time-division",
    "X": "None of the above",
}

def _decode(bw, base, opt):
  #print("DBG", bw, "/", base, "/", opt)
  bw_val = None
  if (bw != ""):
    # yapf: disable
    if (re.match(r"[1-9]([0-9HKMG][0-9][0-9]|[0-9][0-9HKMG][0-9]|[0-9][0-9][0-9HKMG])", bw) is None):
      msg = "INCORRECT string (BW)"
      logger.error(msg)
      raise RuntimeError(msg)
    # yapf: enable
    if ("H" in bw):
      bw_val = float(bw.replace("H", "."))
    elif ("K" in bw):
      bw_val = float(bw.replace("K", "."))
    elif ("M" in bw):
      bw_val = float(bw.replace("M", "."))
    elif ("G" in bw):
      bw_val = float(bw.replace("G", "."))
    else:
      msg = "INCORRECT string (BW)"
      logger.error(msg)
      raise RuntimeError(msg)

  print(f"    {base[0]} - {_dictModCarrier[base[0]]}")
  print(f"    {base[1]} - {_dictModSignal[base[1]]}")
  print(f"    {base[2]} - {_dictInfo[base[2]]}")
  if (bw_val is not None):
    if ("H" in bw):
      print(f"   BW - {round(bw_val, 3)} Hz")
    elif ("K" in bw):
      print(f"   BW - {round(bw_val, 3)} kHz")
    elif ("M" in bw):
      print(f"   BW - {round(bw_val, 3)} MHz")
    elif ("G" in bw):
      print(f"   BW - {round(bw_val, 3)} GHz")
    else:
      msg = "INCORRECT string (BW)"
      logger.error(msg)
      raise RuntimeError(msg)
  if (opt != ""):
    print(f"    {opt[0]} - {_dictInfoDetails[opt[0]]}")
    print(f"    {opt[1]} - {_dictMultiplex[opt[1]]}")

def mainApp():
  _et = cliArgs["et"].replace(" ", "").upper()
  if (len(_et) == 3):
    bw = ""
    base = _et
    opt = ""
  elif (len(_et) == 7):
    bw = _et[0:4]
    base = _et[4:7]
    opt = ""
  elif (len(_et) == 9):
    bw = _et[0:4]
    base = _et[4:7]
    opt = _et[7:9]
  else:
    msg = "INCORRECT string"
    logger.error(msg)
    raise RuntimeError(msg)

  _decode(bw, base, opt)

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

  appDesc = "decode emission type"
  parser = argparse.ArgumentParser(description=appDesc)
  #parser.add_argument("action", help="action",
  #                    choices=("info", ""))
  parser.add_argument("et", help="emmision type (no spaces)")
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
