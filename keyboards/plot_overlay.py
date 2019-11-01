#!/usr/bin/env python3

import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.io
from scipy.signal import butter,lfilter, freqz
import numpy as np
import sys
import glob
from scipy import signal
import support

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: ./plotlite.py <savegame>")
    sys.exit(0)
  df = glob.glob(sys.argv[1]+"*")
  fig,(ax1,ax2) = plt.subplots(2,1)
  for fn in df:
    print(fn)
    data = np.load(fn)
    data0_slice = data[0][0:75000]
    data1_slice = data[1][0:75000]
    # f1,Pxx_spec1 = signal.welch(data0_slice,124999999,'flattop',1024,scaling='spectrum')
    # f2,Pxx_spec2 = signal.welch(data1_slice,124999999,'flattop',1024,scaling='spectrum')
    # print(np.sqrt(f1))
    ax1.plot(support.block_preprocess_function(data0_slice))
    ax2.plot(support.block_preprocess_function(data1_slice))
  plt.show()
