#!/usr/bin/python

import sys
import math
import matplotlib.pyplot as plt

KEY = "\x2b\x7e\x15\x16\x28\xae\xd2\xa6"
PT  = "\xff\xff\xff\xff\xff\xff\xff\xff"

KEY_EXP = "".join([bin(ord(x))[2:].rjust(8,"0") for x in KEY])
PT_EXP = "".join([bin(ord(x))[2:].rjust(8,"0") for x in PT])

PC1TAB = [56, 48, 40, 32, 24, 16,  8, 0, 57, 49, 41, 33, 25, 17, 9,  1, 58, 50, 42, 34, 26, 18, 10,  2, 59, 51, 43, 35, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13,  5, 60, 52, 44, 36, 28, 20, 12,  4, 27, 19, 11, 3]
PC2TAB = [13, 16, 10, 23,  0,  4, 2, 27, 14,  5, 20,  9, 22, 18, 11,  3, 25,  7, 15,  6, 26, 19, 12,  1, 40, 51, 30, 36, 46, 54, 29, 39, 50, 44, 32, 47, 43, 48, 38, 55, 33, 52, 45, 41, 49, 35, 28, 31]
IPTAB = [57, 49, 41, 33, 25, 17, 9,  1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7, 56, 48, 40, 32, 24, 16, 8,  0, 58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6]

ETAB = [31,  0,  1,  2,  3,  4, 3,  4,  5,  6,  7,  8, 7,  8,  9, 10, 11, 12,11, 12, 13, 14, 15, 16,15, 16, 17, 18, 19, 20,19, 20, 21, 22, 23, 24,23, 24, 25, 26, 27, 28, 27, 28, 29, 30, 31,  0]


  # The (in)famous S-boxes
SBOX = [
    # S1
    [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7,
     0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8,
     4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0,
     15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],

    # S2
    [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10,
     3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5,
     0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15,
     13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],

    # S3
    [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8,
     13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1,
     13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7,
     1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],

    # S4
    [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15,
     13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9,
     10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4,
     3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],

    # S5
    [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9,
     14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6,
     4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14,
     11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],

    # S6
    [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11,
     10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8,
     9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6,
     4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],

    # S7
    [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1,
     13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6,
     1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2,
     6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],

    # S8
    [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7,
     1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2,
     7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8,
     2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
]



# 7 bits - miss the last one.
def __expand_key(in_str):
  return [ord(i) - ord('0') for i in "".join([bin(ord(x))[2:-1].rjust(7,"0") for x in in_str])]


def expand_data(in_str):
  return [ord(i) - ord('0') for i in "".join([bin(ord(x))[2:].rjust(8,"0") for x in in_str])]

def expand_data_npz(in_str):
  return [int(i) for i in "".join([bin(x)[2:].rjust(8,"0") for x in in_str])]

def permute(table,blk):
  return list(map(lambda x: blk[x], table))

def __create_subkeys(blk):
  Kn = []
  i = 0
  L = blk[:28]
  R = blk[28:]
  L.append(L[0])
  del L[0]
  R.append(R[0])
  del R[0]
  return permute(PC2TAB,L+R)

def mapToInteger(in_s):
  in_r = in_s[::-1]
  out = 0
  for ix in range(0,6):
    i = int(ix)
    out += math.pow(2,i) * in_r[i]
  return out

def convertToSboxIndex(in_int):
  in_bin = [int(b) for b in bin(in_int)[2:].rjust(8,"0")]
  out_bin = [in_bin[2],in_bin[7],in_bin[3],in_bin[4],in_bin[5],in_bin[6]]
  return int(mapToInteger(out_bin))

class desIntermediateValue:
  def __init__(self):
    pass

  def preprocess(self,MyPT):
    d = permute(IPTAB,expand_data_npz(MyPT))
    d_ex = permute(ETAB,d[32:])
    self.d_ex = [d_ex[i:i+6] for i in xrange(0,len(d_ex),6)]

  def generateSbox(self,byte_posn,key):
    tmp_d = int(mapToInteger(self.d_ex[byte_posn]))
    tmp_d ^= int(key) 
    tmp_d_bin = [ord(b) - ord("0") for b in bin(tmp_d)[2:].rjust(6,"0")]
    m = (tmp_d_bin[0] << 1) + tmp_d_bin[5]
    n = (tmp_d_bin[1] << 3) + (tmp_d_bin[2] << 2) + (tmp_d_bin[3] << 1) + tmp_d_bin[4]
    return SBOX[byte_posn][(m << 4) + n]

if __name__ == "__main__":
  expand_data_npz = expand_data
  d = desIntermediateValue()
  d.preprocess(PT)
  for i in range(0,48):
    print "Key candidate %02x: Sbox output: %02x" % (i,d.generateSbox(0,i))
