#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
"""app"""
import math
#import site #http://docs.python.org/library/site.html
import sys
import os
import platform
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
import tempfile
import colorama
import urllib.request
import xml.etree.ElementTree as ET

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")
_path_tmp = os.path.join(tempfile.gettempdir(), "radio")
_path_in = os.path.join(_path_tmp, "hamsql.xml")

def _get_hamsql():
  logger.info("downloading ...")
  url = "https://www.hamqsl.com/solarxml.php"
  urllib.request.urlretrieve(url, _path_in)

def _parse_hamsql():
  root = ET.parse(_path_in).getroot()

  ts_now = datetime.datetime.utcnow().strftime(" %d %b %Y %H%M")
  print(f"UTC time: {ts_now}")
  ts = root.find("solardata/updated").text
  print(f" updated: {ts}")

  print("==")
  flux_index = int(root.find("solardata/solarflux").text)
  a_index = int(root.find("solardata/aindex").text)
  k_index = int(root.find("solardata/kindex").text)
  n_spots = int(root.find("solardata/sunspots").text)
  print(f"SFI: {flux_index}, A: {a_index}, K: {k_index}, spots: {n_spots}")

  print("")
  fo_F2 = float("nan")
  try:
    fo_F2 = float(root.find("solardata/fof2").text)
  except (TypeError, ValueError):
    pass
  if (math.isnan(fo_F2)):
    print(f"fo_F2: {colorama.Fore.RED}UNDEFINED{colorama.Style.RESET_ALL}")
  else:
    print(f"fo_F2: {colorama.Fore.CYAN}{fo_F2}{colorama.Style.RESET_ALL} MHz")
  muf_f = float("nan")
  try:
    muf_f = float(root.find("solardata/muffactor").text)
  except (TypeError, ValueError):
    pass
  if (not math.isnan(muf_f)):
    print(f"MUF_f: {muf_f}")
  MUF = float("nan")
  try:
    MUF = float(root.find("solardata/muf").text)
  except (TypeError, ValueError):
    pass
  if (math.isnan(MUF)):
    print(f"  MUF: {colorama.Fore.RED}UNDEFINED{colorama.Style.RESET_ALL}")
  else:
    print(f"  MUF: {colorama.Fore.YELLOW}{MUF}{colorama.Style.RESET_ALL} MHz")

  print("== HF ==")
  dict_hf = {}
  for el in root.findall("solardata/calculatedconditions/band"):
    if (el.attrib["name"] in dict_hf.keys()):
      dict_hf[el.attrib["name"]][el.attrib["time"]] = el.text
    else:
      dict_hf[el.attrib["name"]] = {el.attrib["time"]: el.text}
  for band_id in dict_hf.keys():
    print(f"  {band_id}", end="")
    for band_time in dict_hf[band_id].keys():
      band_cond = dict_hf[band_id][band_time].upper()
      # yapf: disable
      if (band_cond == "GOOD"):
        print(f" {band_time} - {colorama.Fore.GREEN}{band_cond}{colorama.Style.RESET_ALL}", end="")
      elif (band_cond == "FAIR"):
        print(f" {band_time} - {colorama.Fore.YELLOW}{band_cond}{colorama.Style.RESET_ALL}", end="")
      elif (band_cond == "POOR"):
        print(f" {band_time} - {colorama.Fore.RED}{band_cond}{colorama.Style.RESET_ALL}", end="")
      else:
        print(f" {band_time} - {band_cond}", end="")
      # yapf: enable
    print("")

  print("== VHF ==")
  aurora_lat = float(root.find("solardata/latdegree").text)
  for el in root.findall("solardata/calculatedvhfconditions/phenomenon"):
    band_loc = el.attrib["location"]
    band_cond = el.text
    # yapf: disable
    if (band_cond == "Band Closed"):
      print(f"  {el.attrib['name']: <10} {band_loc: >13} {colorama.Fore.RED}{band_cond}{colorama.Style.RESET_ALL}")
    else:
      print(f"  {el.attrib['name']: <10} {band_loc: >13} {band_cond}")
    # yapf: enable

def mainApp():
  if (platform.system() == "Windows"):
    colorama.just_fix_windows_console()

  if (not os.path.isdir(_path_tmp)):
    os.mkdir(_path_tmp)

  if (not os.path.isfile(_path_in)):
    _get_hamsql()
  else:
    stat_info = os.stat(_path_in)
    delta_t = datetime.datetime.now() - datetime.datetime.fromtimestamp(stat_info.st_mtime)
    if (delta_t.seconds > 3600):
      _get_hamsql()

  _parse_hamsql()

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
