#!/usr/bin/env python3

import sys
import getopt
import sys
import uuid
import time
import random
import numpy as np
import support.filemanager

fe = None
drv = None

def acquireInterface(interfacename):
  global fe
  try:
    exec("from frontends.%s import CaptureInterface; fe = CaptureInterface()" % interfacename,globals())
  except:
    print("Unable to acquire interface '%s'" % interfacename)
    fe = None

def acquireDriver(interfacename):
  global drv
  try:
    exec("from drivers.%s import DriverInterface; drv = DriverInterface()" % interfacename,globals())
  except:
    print("Unable to acquire driver '%s'" % interfacename)
    drv = None

def usage():
  print("Usage code goes here.")
 
def runCaptureTask():
  global fe,drv
  fe.init()
  drv.init(fe)
  CONFIG_TRACECOUNT = 5
  CONFIG_SAMPLECOUNT = 5000
  traces = np.zeros((CONFIG_TRACECOUNT,CONFIG_SAMPLECOUNT),np.float32)
  data = np.zeros((CONFIG_TRACECOUNT,16),np.uint8)         # RAND
  data_out = np.zeros((CONFIG_TRACECOUNT,16),np.uint8)     # AUTN
  for i in range(0,5):
    (next_rand, next_autn) = drv.drive()
    time.sleep(0.5)
    dataA = fe.capture()
    traces[i:] = dataA
    data[i:] = next_rand
    data_out[i:] = next_autn
  support.filemanager.save("./lol123",traces=traces,data=data,data_out=data_out)   

if __name__ == "__main__":
  print("capturebuddy")
  optlist, args = getopt.getopt(sys.argv[1:],"ha:d:s:",["help","acquire=","driver=","set="])
  for arg,value in optlist:
    if arg in ("-h","--help"):
      usage()
      sys.exit(0)
    elif arg in ("-a","--acquire"):
      acquireInterface(value)
    elif arg in ("-d","--driver"):
      acquireDriver(value)
    elif arg in ("-s","--set"):
      setConfiguration(opt)
    else:
      print("Sorry, not implemented yet")
      sys.exit(0)
  if fe is None:
    print("No acquisition frontend, bye!")
    sys.exit(0)
  elif drv is None:
    print("No driver backend, bye!")
    sys.exit(0)
  while True:
    cmd = input(" > ").lstrip().rstrip()
    if cmd in ("q","quit"):
      print("bye!")
      sys.exit(0)
    elif cmd in ("r","run"):
      runCaptureTask()
    else:
      print("Unknown command %s" % cmd)
 
