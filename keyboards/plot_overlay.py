#!/usr/bin/env python3

import random
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.io
from scipy.signal import butter,lfilter, freqz
import numpy as np
import sys
import glob
import getopt
from scipy import signal
import support

colorChart = {}
availColors = ['b','g','r','c','m','y','k']

def getColorPrefix(fn):
  global colorChart
  prefix = fn.split("/")[1]
  prefix = prefix.split("-")[0]
  if prefix in colorChart.keys():
    return (prefix,colorChart[prefix])
  else:
    global availColors
    colorChart[prefix] = random.choice(availColors)
    availColors.remove(colorChart[prefix])
    return (prefix,colorChart[prefix])

CONFIG_ALPHA = []

if __name__ == "__main__":
  if len(sys.argv) < 2:
    usage()
    # print("usage: ./plotlite.py <savegame>")
    sys.exit(0)
  df = []
  opts,remainder = getopt.getopt(sys.argv[1:],"f:a:",["file=","alpha="])
  for opt, arg in opts:
    if opt in ("-f","--file"):
      df += glob.glob(arg + "*")
    elif opt in ("-a","--alpha"):
      CONFIG_ALPHA.append(arg)
  # for a in sys.argv[1:]:
  #   df += glob.glob(a+"*")
  fig,(ax1,ax2) = plt.subplots(2,1)
  for fn in df:
    print(fn)
    data = np.load(fn)
    (p,c) = getColorPrefix(fn)
    lm = support.findLocalMaxima(data[0])
    for nomnom in lm:
      print(support.findReallyLocalMaxima(support.block_preprocess_function(data[0][nomnom+1000:nomnom+support.CONFIG_MAX_PULSEWIDTH]))) 
      print(support.findReallyLocalMaxima(support.block_preprocess_function(data[1][nomnom+1000:nomnom+support.CONFIG_MAX_PULSEWIDTH]))) 
    data0_slice = data[0][0:75000]
    data1_slice = data[1][0:75000]
    if p in CONFIG_ALPHA:
      ax1.plot(support.block_preprocess_function(data0_slice),label=p,color=c,alpha=0.5)
      ax2.plot(support.block_preprocess_function(data1_slice),label=p,color=c,alpha=0.5)
    else:
      ax1.plot(support.block_preprocess_function(data0_slice),label=p,color=c)
      ax2.plot(support.block_preprocess_function(data1_slice),label=p,color=c)
  ax1.legend()
  ax2.legend()
  plt.show()
