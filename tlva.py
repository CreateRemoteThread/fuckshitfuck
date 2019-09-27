#!/usr/bin/env python3

import scipy
import scipy.stats
import support.filemanager
import getopt
import sys
import numpy as np
import warnings
import matplotlib.pyplot as plt

CONFIG_FILE = None

def do_tlva(fn):
  cf = [0xAA] * 16
  df = support.filemanager.load(fn)
  tlva_fixed_traces = []
  tlva_random_traces = []
  for i in range(0,len(df['traces'])):
    if np.array_equal(df['data'][i],cf):
      tlva_fixed_traces.append(df['traces'][i])
    else:
      tlva_random_traces.append(df['traces'][i])
  print("Fixed traces count: %d" % len(tlva_fixed_traces))
  print("Random traces count: %d" % len(tlva_random_traces))
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    ttrace = scipy.stats.ttest_ind(tlva_fixed_traces,tlva_random_traces,axis=0,equal_var=False)[0]
  return np.nan_to_num(ttrace)

if __name__ == "__main__":
  optlist, args = getopt.getopt(sys.argv[1:],"f:",[])
  for arg, value in optlist:
    if arg == "-f":
      CONFIG_FILE = value
  tt = do_tlva(CONFIG_FILE)
  plt.plot(tt)
  plt.show()
