#!/usr/bin/env python3

import os
import sys
import getopt
import support
import numpy as np

CONFIG_TRAINSET = None
CONFIG_FPREFIX = None

# single trace turn peaks into distance
def matchPeaks(raw,trained):
  if len(raw) != len(trained):
    return None

def removeElt(set_in,elt_del):
  x = []
  for i in range(0,len(set_in)):
    if set_in[i] != elt_del:
      x.append(set_in[i])
  return x

def cullWeakest(set_in,cull_count):
  x = set_in
  for i in range(0,cull_count):
    m = min(x,key=lambda t: t[1])
    x = removeElt(x,m)
  return x

CONFIG_PEAK_JITTER = 1000
def matchSet(psetA_,psetB_):
  if len(psetA_) > len(psetB_):
    print("Culling set A")
    psetB = psetB_
    psetA = cullWeakest(psetA_,len(psetA_) - len(psetB_))
  elif len(psetA_) < len(psetB_):
    print("Culling set B: %d" % len(psetB_))
    psetA = psetA_
    psetB = cullWeakest(psetB_,len(psetB_) - len(psetA_))
  else:
    psetA = psetA_
    psetB = psetB_
  print("Lengths: %d %d" % (len(psetA),len(psetB)))
  if len(psetA) != len(psetB):
    print("Cull failed")
    sys.exit(0)
  for i in range(0,len(psetA)):
    (off,val) = psetA[i]
    (off_c,val_c) = psetB[i]
    if abs(off-off_c) > CONFIG_PEAK_JITTER:
      print("Failed: horizontal jitter too large (%d:%d)" % (off,off_c))
      return False
  nc1 = [val for (off,val) in psetA]
  nc2 = [val for (off,val) in psetB]  
  if np.corrcoef(nc1,nc2)[0,1] < 0.9:
    print("Failed: vertical jitter too large")
    return False
  return True

CONFIG_FOCUS = 0

if __name__ == "__main__":
  opts, args = getopt.getopt(sys.argv[1:],"t:f:",["train=","file=","focus="])
  for opt,arg in opts:
    if opt in ("-t","--train"):
      CONFIG_TRAINSET = arg
    elif opt in ("-f","--file"):
      CONFIG_FPREFIX = arg
    elif opt == "--focus":
      CONFIG_FOCUS = int(arg)
  if CONFIG_TRAINSET is None or CONFIG_FPREFIX is None:
    print("This is a trained classifier. You must provide the trainset and the floss")
    sys.exit(0)
  trainset = np.load(CONFIG_TRAINSET)
  i = CONFIG_FOCUS
  bCont = True
  out = []
  while bCont is True:
    fn = "%s/%d.npy" % (CONFIG_FPREFIX,i)
    if not os.path.isfile(fn):
      print("Done!")
      bCont = False
      break
    data = np.load(fn)
    lm = support.findLocalMaxima(data[0])
    for nom in lm:
      c0 = support.block_preprocess_function(data[0][nom+1000:nom+support.CONFIG_MAX_PULSEWIDTH])
      c1 = support.block_preprocess_function(data[1][nom+1000:nom+support.CONFIG_MAX_PULSEWIDTH])
      rlm_channelA = support.findReallyLocalMaxima(c0)
      rlm_channelB = support.findReallyLocalMaxima(c1)
      nextTrace = False
      for (tag,chanAPeaks,chanBPeaks) in trainset:
        print(tag + " : ",end="")
        # matchSet will cull the weakest signals.
        # assume problems are caused by noise, not "ghost peaks".
        if matchSet(rlm_channelA,chanAPeaks) and matchSet(rlm_channelB,chanBPeaks):
          print("Exact match: %s" % tag)
          out.append(tag)
          nextTrace = True
          break
      if nextTrace:
        print("Next trace found, going to next character")
        break
    if nextTrace is False:
      out.append("unknown")
    if CONFIG_FOCUS != 0:
      print("Focused analysis, exiting.")
      print(out)
      sys.exit(0)
    i += 1
  print(out)
