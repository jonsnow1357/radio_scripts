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

class KISSException(Exception):
  pass

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
  return bytearray(res)

def _ax25_decode_addr(lstB):
  #print("DBG", [hex(t) for t in lstB])
  lst_call = [chr(c >> 1) for c in lstB[:-1]]
  ssid = ((lstB[-1] & 0x1F) >> 1)
  #print("DBG", lst_call, ssid)
  call = "".join(lst_call).strip()
  if (ssid == 0):
    if (call.startswith("WIDE")):
      return call + "*"
    else:
      return call
  else:
    return "{}-{}".format(call, ssid)

def _kiss_frame(msg: bytearray) -> bytearray:
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

def _kiss_unframe(msg: bytearray) -> bytearray:
  if ((msg[0] != KISS_FEND) or (msg[1] != 0x00) or (msg[-1] != KISS_FEND)):
    raise KISSException("INCORRECT frame start: {}".format([hex(t) for t in msg]))

  res = []
  bEsc = False
  for b in msg[2:-1]:
    if (b == KISS_FESC):
      bEsc = True
      continue
    if (bEsc):
      if (b == KISS_TFEND):
        res += [KISS_FEND]
      elif (b == KISS_TFESC):
        res += [KISS_FESC]
      else:
        raise KISSException("INCORRECT frame escape: {}".format([hex(t) for t in msg]))
      bEsc = False
      continue
    res += [b]
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
  frame += bytearray([0x03, 0xF0])  # ctrl field = 0x03 (UI), protocol ID = 0xF0 (none)

  msg = bytearray([ord(c) for c in content])
  frame += msg
  kiss_frame = _kiss_frame(frame)
  #print("DBG", kiss_frame)
  return kiss_frame

def splitFrames(lstB):
  #print("DBG", [hex(t) for t in lstB])
  res = []
  idx = -1
  for i, b in enumerate(lstB):
    if (lstB[i] == KISS_FEND):
      if (i == (len(lstB) - 1)):
        res[idx] += [lstB[i]]
        continue
      elif (lstB[i + 1] == 0x00):
        res.append([lstB[i]])
        idx += 1
        continue
    res[idx] += [lstB[i]]
  logger.info("split into {} frame(s)".format(len(res)))
  return res

def parseFrame(kissFrame):
  #print("DBG", [hex(t) for t in kissFrame])
  frame = _kiss_unframe(kissFrame)
  #print("DBG", [hex(t) for t in frame])

  idx = -1
  for i, b in enumerate(frame):
    if ((b == 0x03) and (frame[i + 1]) == 0xF0):
      idx = i
      break
  if (idx == -1):
    raise KISSException("NOT an APRS frame: {}".format([hex(t) for t in frame]))
  content = frame[(idx + 2):].decode(encoding="ascii")
  address = frame[:idx]
  #print("DBG", content)

  if ((len(address) % 7) != 0):
    raise KISSException("NOT an APRS address: {} {}".format([hex(t) for t in address],
                                                            content))
  lst_addr = [address[i:(i + 7)] for i in range(0, len(address), 7)]
  dstAddr = _ax25_decode_addr(lst_addr[0]).strip()
  srcAddr = _ax25_decode_addr(lst_addr[1]).strip()
  routing = ""
  for addr in lst_addr[2:]:
    routing += _ax25_decode_addr(addr)
    routing += ","
  routing = routing[:-1].strip()
  #print("DBG", dstAddr, srcAddr, routing, content)
  return [dstAddr, srcAddr, routing, content]
