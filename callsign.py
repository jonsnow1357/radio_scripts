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
import twill.browser
import twill.commands
import lxml.html

logging.config.fileConfig("logging.cfg")
logger = logging.getLogger("app")

def _getCallsingInfo_CA(callsign):
  logger.info("going to Industry Canada")
  twill.browser.go("https://apc-cap.ic.gc.ca/pls/apc_anon/query_amat_cs$.startup")
  # for f in twill.commands.showforms():
  #   print("DBG", f)
  twill.commands.fv("2", "P_CALLSIGN", callsign)
  twill.commands.submit()

  url_details = None
  for link in twill.commands.showlinks():
    if ("callsign.QueryViewByKey" in link.url):
      url_details = "https://apc-cap.ic.gc.ca/pls/apc_anon/{}".format(link.url)
  if (url_details is None):
    logger.error("callsign NOT FOUND")
    return {}

  #print("DBG", url_details)
  logger.info("going to details page")
  twill.browser.go(url_details)
  #print("DBG", twill.browser.html)
  tree = lxml.html.fromstring(twill.browser.html)
  ret_callsign = tree.xpath("/html/body/main/div[3]/table/tr[1]/td")[0].text.strip()
  if (ret_callsign != callsign):
    #logger.error(f"{ret_callsign} != {callsign}")
    logger.error("callsign NOT MATCHED")
    return {}

  # yapf:disable
  address = "{}, {}, {}, {}".format(tree.xpath("/html/body/main/div[3]/table/tr[3]/td")[0].text.strip(),
                                    tree.xpath("/html/body/main/div[3]/table/tr[4]/td")[0].text.strip(),
                                    tree.xpath("/html/body/main/div[3]/table/tr[5]/td")[0].text.strip(),
                                    tree.xpath("/html/body/main/div[3]/table/tr[6]/td")[0].text.strip(),
                                    )
  address = address.strip(", ")
  res = {"callsign": callsign,
         "name": tree.xpath("/html/body/main/div[3]/table/tr[2]/td")[0].text.strip(),
         "address": address,
         "country": "CA",
         "qualifications": tree.xpath("/html/body/main/div[3]/table/tr[7]/td")[0].text.strip(),
         }
  # yapf: enable
  return res

def _getCallsingInfo_US(callsign):
  logger.info("going to FCC")
  twill.browser.go("https://wireless2.fcc.gov/UlsApp/UlsSearch/searchAmateur.jsp")
  # for f in twill.commands.showforms():
  #   print("DBG", f)
  twill.commands.fv("1", "ulsCallSign", callsign)
  twill.commands.submit()

  url_details = None
  for link in twill.commands.showlinks():
    if ("license.jsp?licKey" in link.url):
      url_details = "https://wireless2.fcc.gov/UlsApp/UlsSearch/{}".format(link.url)
  if (url_details is None):
    logger.error("callsign NOT FOUND")
    return {}

  #print("DBG", url_details)
  logger.info("going to details page")
  twill.browser.go(url_details)
  #print("DBG", twill.browser.html)
  tree = lxml.html.fromstring(twill.browser.html)
  # yapf: disable
  ret_callsign = tree.xpath("/html/body/table[4]/tr/td[2]/div/table[2]/tr[2]/td/table/tr[1]/td[2]")[0].text.strip()
  # yapf: enable
  if (ret_callsign != callsign):
    #logger.error(f"{ret_callsign} != {callsign}")
    logger.error("callsign NOT MATCHED")
    return {}

  # yapf: disable
  tmp = tree.xpath("/html/body/table[4]/tr/td[2]/div/table[2]/tr[4]/td/table/tr[3]/td[1]")[0].text_content().strip().split("\n")
  name = tmp[0]
  address = ", ".join(tmp[1:])
  address = address.strip(", ")
  res = {"callsign": callsign,
         "name": name,
         "address": address,
         "country": "US",
         "qualifications": tree.xpath("/html/body/table[4]/tr/td[2]/div/table[2]/tr[6]/td/table/tr[1]/td[2]")[0].text_content().strip(),
         }
  # yapf: enable
  return res

def _getCallsingInfo_other(callsign):
  logger.info("going to hamcall.net")
  twill.browser.go("https://hamcall.net/call")
  # for f in twill.commands.showforms():
  #   print("DBG", f)
  twill.commands.fv("2", "callsign", callsign)
  twill.commands.submit()

  #print("DBG", twill.browser.html)
  tree = lxml.html.fromstring(twill.browser.html)
  print("DBG", tree.xpath("/html/body/b[1]")[0].text.strip())
  for e in tree.xpath("/html/body/b[2]")[0]:
    print("DBG", e.text)
  # yapf: disable
  res = {"callsign": callsign,
         "name": "",
         "address": "",
         "city": "",
         "province": "",
         "postal_code": "",
         "country": "",
         "qualifications": "",
         }
  # yapf: enable
  return res

def getCallsingInfo(callsign):
  """
  Returns information abaout a callsign
  :param callsign:
  :return: dictionary of {"callsign": ... , "name": ... , "address": ... , "qualifications": ... }
  """
  callsign = callsign.upper()
  logger.info(f"loking up callsign '{callsign}'")
  res = {}

  if (re.match(r"^V(A[1-7]|E[0-9]|O[12]|Y[0-2])[A-Z]{2,3}$", callsign) is not None):
    return _getCallsingInfo_CA(callsign)
  elif (re.match(r"^([KNW][A-Z]|AL|AH)[0-9][A-Z]{1,3}$", callsign) is not None):
    return _getCallsingInfo_US(callsign)
  else:
    return _getCallsingInfo_other(callsign)

def mainApp():
  res = getCallsingInfo(cliArgs['callsign'])
  if (len(res) > 0):
    for k, v in res.items():
      print(f"{k:>14}: {v}")

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

  appDesc = "serach callsign information"
  parser = argparse.ArgumentParser(description=appDesc)
  #parser.add_argument("action", help="action",
  #                    choices=("info", ""))
  parser.add_argument("callsign", help="callsign")
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
