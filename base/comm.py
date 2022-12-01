#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
"""library for communication interfaces"""

#import site #http://docs.python.org/library/site.html
import sys
import os
#import platform
import logging
import re
import time
import datetime

#sys.path.append("./")
#sys.path.append("../")

#import math
#import csv
import socket

logger = logging.getLogger("lib")
logcomms = logging.getLogger("comms")

import radio_scripts.base.misc

regexIP = r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\." \
          r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
regexSocket = r"^[A-Za-z0-9_\.]+(:[0-9]*)?$"
timeout_net = 1.0

class CommException(Exception):
  pass

class CommTimeoutException(CommException):
  pass

class CommInterfaceInfo(object):

  def __init__(self, strVal):
    self._value = strVal
    self._name = None
    self._host = None  # IPv4, IPv6, FQDN, hostname
    self.port = None
    self.timeout = timeout_net
    self.eos = "\r\n"  # End of String, added after each sent message, seems to work for telnet and UART
    self.eom = ""  # End of Message, expected after each received message

    self._parseValue()

  @property
  def DBG(self):
    return "{}::{}".format("SOCKET", self.host)

  @property
  def INFO(self):
    return "{}://{}@{}:{}".format("socket", "-", self._host, self.port)

  def __str__(self):
    return "{} {}".format(self.__class__.__name__, self.INFO)

  @property
  def value(self):
    return self._value

  @property
  def host(self):
    return self._host

  def _parseValue_socket(self):
    tmp = self._value.split(":")
    if (len(tmp) == 1):
      self._host = tmp[0]
      self.port = 23  # assume telnet if no port
    elif (len(tmp) == 2):
      self._host = tmp[0]
      self.port = int(tmp[1])
    else:
      msg = "INCORRECT {} value: {}".format(self.__class__.__name__, self._value)
      logger.error(msg)
      raise CommException(msg)

  def _parseValue(self):
    """
    parse something like:
      ip[:port]
      hostname[:port]
      devname[:rate]
      protocol://ip[:port]
      protocol://url[:port]
      protocol://user[:password]@ip[:port]
      protocol://user[:password]@url[:port]
    """
    if (not isinstance(self._value, str)):
      msg = "INCORRECT type for value: {}".format(type(self._value))
      logger.error(msg)
      raise CommException(msg)

    #print("DBG", self._value)
    if (re.match(regexSocket, self._value)):
      self._parseValue_socket()
    else:
      msg = "UNRECOGNIZED {} value: {}".format(self.__class__.__name__, self._value)
      logger.error(msg)
      raise CommException(msg)

class CommInterface(object):

  def __init__(self, strConnInfo=None):
    self._connInfo = None
    self._conn = None

    self.interBytePause = 0.0
    self.bCertVerify = True

    if (strConnInfo is not None):
      self.setInfo(strConnInfo)

  @property
  def connection(self):
    return self._conn

  @property
  def info(self):
    return self._connInfo

  @property
  def timeout(self):
    return self._connInfo.timeout

  @timeout.setter
  def timeout(self, val):
    if (isinstance(val, int)):
      self._connInfo.timeout = val

  @property
  def eos(self):
    return self._connInfo.eos

  @eos.setter
  def eos(self, val):
    if (isinstance(val, str)):
      self._connInfo.eos = val

  @property
  def eom(self):
    return self._connInfo.eom

  @eom.setter
  def eom(self, val):
    if (isinstance(val, str)):
      self._connInfo.eom = val

  def __str__(self):
    return str(self._connInfo)

  def setInfo(self, val):
    if (isinstance(val, CommInterfaceInfo)):
      self._connInfo = val
    else:
      self._connInfo = CommInterfaceInfo(val)

  def _openSocket(self):
    logger.info("SOCKET connection {}".format(self._connInfo.INFO))
    self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._conn.settimeout(self._connInfo.timeout)
    try:
      self._conn.connect((self._connInfo.host, self._connInfo.port))
    except socket.timeout as ex:
      msg = "{}: {}".format(self, ex)
      logger.error(msg, exc_info=True)
      raise CommTimeoutException(msg)
    except socket.gaierror as ex:
      msg = "{}: {}".format(self, ex)
      logger.error(msg, exc_info=True)
      raise CommException(msg)
    except Exception as ex:
      msg = "{}: {}".format(self, ex)
      logger.error(msg, exc_info=True)
      raise CommException(msg)

  def open(self):
    self._openSocket()

  def _closeSocket(self):
    if (self._conn is None):
      return

    self._conn.close()
    logger.info("SOCKET connection closed")

  def close(self):
    if (self._conn is None):
      return

    self._closeSocket()

    self._conn = None

  def _readRaw_Socket(self, strEndRead, TOmultiplier=1):
    if (not isinstance(strEndRead, str)):
      raise NotImplementedError  # this should not happen

    tmp_timeout = (TOmultiplier * self._connInfo.timeout)
    reply = ""

    tlim = datetime.timedelta(seconds=tmp_timeout)
    logcomms.info("{}:wait '{}' for {}".format(
        self._connInfo.DBG, radio_scripts.base.misc.convertStringNonPrint(strEndRead),
        tlim))
    t0 = datetime.datetime.now()
    dt = datetime.datetime.now() - t0
    while (dt < tlim):
      ln = bytes()
      try:
        ln = self._conn.recv(1024)
      except socket.timeout as ex:
        #msg = "{}: {}".format(self, ex)
        #logger.error(msg, exc_info=True)
        #raise CommTimeoutException(msg)
        pass
      except socket.error as ex:
        msg = "{}: {}".format(self, ex)
        logger.error(msg, exc_info=True)
        raise CommException(msg)
      reply += ln.decode("utf-8", errors="ignore")
      if ((strEndRead != "") and (reply.endswith(strEndRead))):
        break
      dt = datetime.datetime.now() - t0

    logcomms.info("{}>>'{}'".format(self._connInfo.DBG,
                                    radio_scripts.base.misc.convertStringNonPrint(reply)))
    #logcomms.info("{}:time {}".format(self._connInfo.DBG, dt))
    if ((strEndRead != "") and (dt > tlim)):
      msg = "{}: timeout {}".format(self, dt)
      #logger.error(msg)
      #logger.error(reply)
      raise CommTimeoutException(msg)

    reply = reply.splitlines()
    #reply = [t.strip() for t in reply]  # remove leading/trailing spaces
    reply = [t for t in reply if (t != "")]  # remove empty lines
    return reply

  def readRaw(self, strEndRead, TOmultiplier=1):
    """
    Reads until strEndRead is found or until timeout expires.
    :param strEndRead: string
    :param TOmultiplier: timeout multiplier
    :return: list of strings (ideally lines received)
    """
    if (self._conn is None):
      logger.error("None connection for CommInterface of type: {}".format(
          self._connInfo.type))
      return []

    reply = self._readRaw_Socket(strEndRead, TOmultiplier)

    return reply

  def read(self, TOmultiplier=1):
    return self.readRaw(self.eom, TOmultiplier=TOmultiplier)

  def _writeRaw_Socket(self, strCmd, TOmultiplier=1):
    #logcomms.info("{}<< {}".format(self._connInfo.DBG,
    #                               radio_scripts.base.misc.convertStringNonPrint(strCmd)))

    #t0 = datetime.datetime.now()
    try:
      if (isinstance(strCmd, bytearray)):
        self._conn.sendall(strCmd)
      else:
        self._conn.sendall(strCmd.encode("utf-8"))
    except socket.error as ex:
      msg = "{}: {}".format(self, ex)
      logger.error(msg, exc_info=True)
      raise CommException(msg)
    #logcomms.info("{}:time {}".format(self._connInfo.DBG, datetime.datetime.now() - t0))

  def _writeRaw_UART(self, strCmd, TOmultiplier=1):
    logcomms.info("{}:({: >4})<< {}".format(
        self._connInfo.DBG, len(strCmd),
        radio_scripts.base.misc.convertStringNonPrint(strCmd)))

  def writeRaw(self, strCmd, TOmultiplier=1):
    """
    Writes strCmd.
    :param strCmd: string
    :param TOmultiplier:  timeout multiplier
    :return:
    """
    if (self._conn is None):
      logger.error("None connection for CommInterface of type: {}".format(
          self._connInfo.type))
      return []

    self._writeRaw_Socket(strCmd, TOmultiplier)

  def write(self, strCmd):
    if (isinstance(strCmd, bytearray)):
      return self.writeRaw(strCmd)
    else:
      return self.writeRaw(strCmd + self.eos)

  def _communicate_Socket(self, strCmd, strEndRead, TOmultiplier=1):
    if (len(strCmd) > 0):
      self._writeRaw_Socket(strCmd, TOmultiplier)
    if (strEndRead is None):
      return []
    return self._readRaw_Socket(strEndRead, TOmultiplier)

  def communicate(self, strCmd, strEndRead="", TOmultiplier=1):
    """
    Sends a command and reads until strEndRead is found or until timeout expires.
    If strCmd is empty it does not send anything.
    If strEndRead is None it does not wait for reply.
    If strEndRead is "" it will wait for timeout.
    :param strCmd: string
    :param strEndRead: string
    :param TOmultiplier: timeout multiplier
    :return: list of strings (ideally lines received)
    """
    if (self._conn is None):
      logger.error("None connection for CommInterface of type: {}".format(
          self._connInfo.type))
      return []

    reply = self._communicate_Socket(strCmd, strEndRead, TOmultiplier)

    #if(len(reply) > 0):
    #  res = [t.strip("\n\r") for t in reply]
    #  res = [t for t in res if(t != "")] # strip empty list entries
    #  return res
    return reply

  def query(self, strCmd, TOmultiplier=1):
    return self.communicate((strCmd + self.eos),
                            strEndRead=self.eom,
                            TOmultiplier=TOmultiplier)
