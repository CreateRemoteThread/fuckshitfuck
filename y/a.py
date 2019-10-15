#!/usr/bin/env python3

from picoscope import ps2000a
import matplotlib as mpl
import numpy as np
import sys
import support
import getopt

mpl.use("Agg")
import matplotlib.pyplot as plt
CONFIG_SAMPLECOUNT = 1000000
CONFIG_SAMPLERATE = 124999999
CONFIG_CAPTURES = None

if __name__ == "__main__":
  print(" Project STARRYNIGHT")
  print("---------------------")
  opts, remainder = getopt.getopt(sys.argv[1:],"c:r:n:",["count=","samplerate=","numsamples="])
  for opt, arg in opts:
    if opt in ("-c","--count"):
      if arg in ("inf","infinite"):
        CONFIG_CAPTURES = None
      else:
        CONFIG_CAPTURES = int(arg)
    elif opt in ("-r","--samplerate"):
      CONFIG_SAMPLERATE = int(arg)
    elif opt in ("-n","--numsamples"):
      CONFIG_SAMPLECOUNT = int(arg)
  ps = ps2000a.PS2000a()
  ps.setChannel('A','DC',VRange=2.0,VOffset=0.0,enabled=True,BWLimited=False,probeAttenuation=10.0)
  (freq,maxSamples) = ps.setSamplingFrequency(CONFIG_SAMPLERATE,CONFIG_SAMPLECOUNT)
  print(" > Asked for %d Hz, got %d Hz" % (CONFIG_SAMPLERATE, freq))
  ps.setSimpleTrigger('A',0.15,'Rising',timeout_ms=100,enabled=True)
  i = 0
  nCount = 0
  nMax = 1
  while nCount < nMax:
    ps.runBlock()
    ps.waitReady()
    data = ps.getDataV('A',CONFIG_SAMPLECOUNT,returnOverflow=False)
    if CONFIG_CAPTURES == 1:
      print("Requested 1 capture, saving to save.npy")
      np.save("save.npy",data)
    p = support.find_local_maxima(data)
    x = support.snd2(p) # tbh all we need is the first.
    if x == []:
      np.save("badsamples/%d.npy" % i,data)
      i += 1
    lol2 = support.map_delay(x)
    print(lol2)
    if CONFIG_CAPTURES == None:
      nCount = 0
    else:
      nCount += 1
