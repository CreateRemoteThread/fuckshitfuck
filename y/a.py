#!/usr/bin/env python3

from picoscope import ps2000a
import matplotlib as mpl
import numpy as np
import sys
import support
import getopt
import time

mpl.use("Agg")
import matplotlib.pyplot as plt
CONFIG_SAMPLECOUNT = 400000
CONFIG_SAMPLERATE = 60000000
CONFIG_CAPTURES = 5

CONFIG_THRESHOLD = 0.2
CONFIG_BACKOFF = 0.2

CONFIG_FPREFIX = None

if __name__ == "__main__":
  print(" Project STARRYNIGHT ")
  print("---------------------")
  opts, remainder = getopt.getopt(sys.argv[1:],"c:t:",["count=","train="])
  for opt, arg in opts:
    if opt in ("-c","--count"):
      if arg in ("inf","infinite"):
        CONFIG_CAPTURES = None
      else:
        CONFIG_CAPTURES = int(arg)
    elif opt in ("-t","--train"):
      CONFIG_FPREFIX = arg
  ps = ps2000a.PS2000a()
  ps.setChannel('A','DC',VRange=0.5,VOffset=0.0,enabled=True,BWLimited=False,probeAttenuation=10.0)
  (freq,maxSamples) = ps.setSamplingFrequency(CONFIG_SAMPLERATE,CONFIG_SAMPLECOUNT)
  print(" > Asked for %d Hz, got %d Hz" % (CONFIG_SAMPLERATE, freq))
  if CONFIG_FPREFIX != None:
    print(" > Configured in training mode with prefix %s" % CONFIG_FPREFIX)
  ps.setSimpleTrigger('A',CONFIG_THRESHOLD,'Rising',enabled=True)
  i = 0
  nCount = 0
  nMax = CONFIG_CAPTURES
  while (nMax is None) or (nCount < nMax):
    ps.runBlock()
    ps.waitReady()
    data = ps.getDataV('A',CONFIG_SAMPLECOUNT,returnOverflow=False)
    if float(max(data[0:100]) < float(CONFIG_THRESHOLD)):
      print("Automatic trigger, keep waiting... (%f < %f)" % (max(data[0:100]),CONFIG_THRESHOLD))
      continue
    print("Threshold reached, saving...")
    if CONFIG_FPREFIX is None:
      np.save("floss/%d.npy" % nCount,data)
      time.sleep(CONFIG_BACKOFF)
      print("Resuming capture...")
    else:
      np.save("toothpicks/%s-%d.npy" % (CONFIG_FPREFIX,nCount),data)
    nCount += 1
  print("Captured %d samples, task complete." % nCount)
  sys.exit(0)
