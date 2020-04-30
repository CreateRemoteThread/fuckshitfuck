#!/usr/bin/env python3

import sys
import getopt
import sys
import uuid
import random
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
    else:
      print("Unknown command %s" % cmd)
  
