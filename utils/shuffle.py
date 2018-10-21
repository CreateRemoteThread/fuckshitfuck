#!/usr/bin/python

import sys
import getopt
import numpy as np

if __name__ == "__main__":
  file = None
  r,args = getopt.getopt(sys.argv[1:],"hf:",["help","file="])
  for opt,arg in r:
    if opt in ("-h","help"):
      usage()
      sys.exit(0)
    elif opt in ("-f","--file"):
      usage()
      sys.exit(0)
