#!/usr/bin/env python3

import sys
import getopt
import numpy as np

CONFIG_TRAINSET = None
CONFIG_FPREFIX = None

# single trace turn peaks into distance
def matchPeaks(raw,trained):
  if len(raw) != len(trained):
    return None

if __name__ == "__main__":
  opts, args = getopt.getopt(sys.argv[1:],"t:f:",["train=","file="])
  for opt in opts:
    if opt in ("-t","--train"):
      CONFIG_TRAINSET = arg
    elif opt in ("-f","--file"):
      CONFIG_FPREFIX = arg
  if CONFIG_TRAINSET is None or CONFIG_FPREFIX is None:
    print("This is a trained classifier. You must provide the trainset and the floss")
    sys.exit(0)
  trainset = np.load(CONFIG_TRAINSET)
  i = 0
  while bCont is True:
    fn = "%s/%d.npy" % (CONFIG_FPREFIX,i)
    if not os.path.isfile(fn):
      print("Done!")
      bCont = False
      break
    data = np.load(fn)
    lm = support.findLocalMaxima(data[0])
    for nom in lm:
      rlm_channelA = support.findReallyLocalMaxima(support.block_preprocess_function(data[0][nom+1000:nom+support.CONFIG_MAX_PULSEWIDTH]))
      rlm_channelB = support.findReallyLocalMaxima(support.block_preprocess_function(data[1][nom+1000:nom+support.CONFIG_MAX_PULSEWIDTH]))
