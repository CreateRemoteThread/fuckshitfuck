#!/usr/bin/env python3

import numpy as np
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
  print("Wrong arguments, ./align.py [npy]")
  sys.exit(0)

data_raw = np.load(sys.argv[1])
data = list(map(abs,data_raw))
firstPeak = 0
for i in range(0,len(data)):
  if data[i] > 0.3:
    print("First peak found at %d" % i)
    firstPeak = i
    break

# better chunking method to avoid cases where the edges touch)
def adaptiveChunk(l,n,cutoff=0.1):
  i = 0
  static_len_l = len(l)
  while i < static_len_l:
    data_slice = l[i:i+n]
    if max(data_slice[0:5000]) > cutoff and i > 7500:
      print("Adaptive chunk: slide backward")
      i -= 7500
      continue
    elif max(data_slice[15000:]) > cutoff and len(data_slice) == n:
      print("Adaptive chunk: slide forward")
      i += 7500
      continue
    else:
      i += n
      plt.axvline(x = i,c = 'red')
      yield data_slice

def chunks(l, n):
  """Yield successive n-sized chunks from l."""
  for i in range(0, len(l), n):
    yield l[i:i + n]

firstD = 0

if firstPeak > 10000:
  d_c = adaptiveChunk(data[firstPeak - 10000:],20000)
  firstD = firstPeak - 10000
else:
  d_c = adaptiveChunk(data[firstPeak + 10000:],20000)
  firstD = firstPeak + 10000

def filter_sd(inx):
  if inx > 0.1:
    return 1
  else:
    return 0

x = list(map(max,d_c))
print(x)
print(list(map(filter_sd,x)))

print("Std: %f" % np.std(data[0:10000]))
plt.plot(data)
# while firstD < len(data):
#   firstD += 20000
plt.savefig("1.png")
