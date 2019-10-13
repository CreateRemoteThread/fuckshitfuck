#!/usr/bin/env python3

from picoscope import ps2000a
import matplotlib as mpl
import numpy as np
import sys

mpl.use("Agg")
CONFIG_SAMPLECOUNT = 1000000

if __name__ == "__main__":
  print("SUPER SECRET TEST PROJECT")
  if len(sys.argv) == 3:
    print("Wrong arguments")
    sys.exit(0)
  ps = ps2000a.PS2000a()
  ps.setChannel('A','DC',VRange=2.0,VOffset=0.0,enabled=True,BWLimited=False,probeAttenuation=10.0)
  ps.setSamplingFrequency(124999999,CONFIG_SAMPLECOUNT)
  ps.setSimpleTrigger('A',1.0,'Rising',timeout_ms=2000,enabled=True)
  ps.runBlock()
  ps.waitReady()
  data = ps.getDataV('A',CONFIG_SAMPLECOUNT,returnOverflow=False)
  import matplotlib.pyplot as plt
  plt.plot(data)
  plt.savefig(sys.argv[1])
  np.save(sys.argv[2],data)
