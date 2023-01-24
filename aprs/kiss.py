#!/usr/bin/env python
# template: library
# SPDX-License-Identifier: GPL-3.0-or-later
"""library for KISS protocol"""

#import site #http://docs.python.org/library/site.html
import sys
import os
#import platform
import logging
#import re
#import time
#import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv

logger = logging.getLogger("lib")

KISS_FEND = 0xC0  # Frame start/end marker
KISS_FESC = 0xDB  # Escape character
KISS_TFEND = 0xDC  # If after an escape, means there was an 0xC0 in the source message
KISS_TFESC = 0xDD  # If after an escape, means there was an 0xDB in the source message

def _ax25_encode_addr(callsign):
  if ("-" not in callsign):
    msg = "INCORRECT callsign for APRS '{}'".format(callsign)
    logger.error(msg)
    raise RuntimeError(msg)

  call, ssid = callsign.split("-")
  ssid = int(ssid)
  if ((ssid < 0) or (ssid > 15)):
    msg = "INCORRECT SSID for APRS '{}'".format(callsign)
    logger.error(msg)
    raise RuntimeError(msg)

  call = f"{call:<6}".upper()
  #logger.info(f"ADDR: '{call}' - {ssid}")
  res = [(ord(c) << 1) for c in call] + [(int(ssid) << 1) | 0b01100000]
  #logger.info(f"ADDR: {[hex(c) for c in res]}")
  return res

def _escape_frame(msg):
  res = [KISS_FEND, 0x00]
  for b in msg:
    if (b == KISS_FEND):
      res += [KISS_FESC, KISS_TFEND]
    elif (b == KISS_FESC):
      res += [KISS_FESC, KISS_TFESC]
    else:
      res += [b]
  res += [KISS_FEND]
  return bytearray(res)

def mkFrame(dstAddr, srcAddr, routing, content):
  if ("-" not in dstAddr):
    dstAddr += "-0"
  dst_addr = _ax25_encode_addr(dstAddr)
  if ("-" not in srcAddr):
    srcAddr += "-7"
  src_addr = _ax25_encode_addr(srcAddr)
  #print("DBG dst", [hex(t) for t in dst_addr])
  #print("DBG src", [hex(t) for t in src_addr])
  frame = (dst_addr + src_addr)

  via = routing.split(",")
  if (len(via) == 1):
    tmp = _ax25_encode_addr(via[0])
    tmp[6] |= 0b01100001  # last address has the HDLC bit set
    frame += tmp
  elif (len(via) == 2):
    tmp = _ax25_encode_addr(via[0])
    frame += tmp
    tmp = _ax25_encode_addr(via[1])
    tmp[6] |= 0b01100001  # last address has the HDLC bit set
    frame += tmp
  frame += [0x03, 0xF0]  # ctrl field = 0x03 (UI), protocol ID = 0xF0 (none)

  msg = [ord(c) for c in content]
  frame += msg
  kiss_frame = _escape_frame(frame)
  #print("DBG", kiss_frame)
  return kiss_frame
