#!/usr/bin/python

import sys
import math
import matplotlib.pyplot as plt

KEY = "\x2b\x7e\x15\x16\x28\xae\xd2\xa6"
# PT  = "\xff\xff\xff\xff\xff\xff\xff\xff"
PT  = "\xa2" * 8

KEY_EXP = "".join([bin(ord(x))[2:].rjust(8,"0") for x in KEY])
PT_EXP = "".join([bin(ord(x))[2:].rjust(8,"0") for x in PT])

PC1TAB = [56, 48, 40, 32, 24, 16,  8, 0, 57, 49, 41, 33, 25, 17, 9,  1, 58, 50, 42, 34, 26, 18, 10,  2, 59, 51, 43, 35, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13,  5, 60, 52, 44, 36, 28, 20, 12,  4, 27, 19, 11, 3]
PC2TAB = [13, 16, 10, 23,  0,  4, 2, 27, 14,  5, 20,  9, 22, 18, 11,  3, 25,  7, 15,  6, 26, 19, 12,  1, 40, 51, 30, 36, 46, 54, 29, 39, 50, 44, 32, 47, 43, 48, 38, 55, 33, 52, 45, 41, 49, 35, 28, 31]
IPTAB = [57, 49, 41, 33, 25, 17, 9,  1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7, 56, 48, 40, 32, 24, 16, 8,  0, 58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6]

# IPTAB = [8,  8, 58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6, 64, 56, 48, 40, 32, 24, 16, 8, 57, 49, 41, 33, 25, 17,  9, 1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7]

ETAB = [ 31,  0,  1,  2,  3,  4, 3,  4,  5,  6,  7,  8, 7,  8,  9, 10, 11, 12,11, 12, 13, 14, 15, 16,15, 16, 17, 18, 19, 20,19, 20, 21, 22, 23, 24,23, 24, 25, 26, 27, 28, 27, 28, 29, 30, 31,  0]

SBOX = [
  0xE4, 0xD1, 0x2F, 0xB8, 0x3A, 0x6C, 0x59, 0x07,
  0x0F, 0x74, 0xE2, 0xD1, 0xA6, 0xCB, 0x95, 0x38,
  0x41, 0xE8, 0xD6, 0x2B, 0xFC, 0x97, 0x3A, 0x50,
  0xFC, 0x82, 0x49, 0x17, 0x5B, 0x3E, 0xA0, 0x6D,
  0xF1, 0x8E, 0x6B, 0x34, 0x97, 0x2D, 0xC0, 0x5A,
  0x3D, 0x47, 0xF2, 0x8E, 0xC0, 0x1A, 0x69, 0xB5,
  0x0E, 0x7B, 0xA4, 0xD1, 0x58, 0xC6, 0x93, 0x2F,
  0xD8, 0xA1, 0x3F, 0x42, 0xB6, 0x7C, 0x05, 0xE9,
  0xA0, 0x9E, 0x63, 0xF5, 0x1D, 0xC7, 0xB4, 0x28,
  0xD7, 0x09, 0x34, 0x6A, 0x28, 0x5E, 0xCB, 0xF1,
  0xD6, 0x49, 0x8F, 0x30, 0xB1, 0x2C, 0x5A, 0xE7,
  0x1A, 0xD0, 0x69, 0x87, 0x4F, 0xE3, 0xB5, 0x2C,
  0x7D, 0xE3, 0x06, 0x9A, 0x12, 0x85, 0xBC, 0x4F,
  0xD8, 0xB5, 0x6F, 0x03, 0x47, 0x2C, 0x1A, 0xE9,
  0xA6, 0x90, 0xCB, 0x7D, 0xF1, 0x3E, 0x52, 0x84,
  0x3F, 0x06, 0xA1, 0xD8, 0x94, 0x5B, 0xC7, 0x2E,
  0x2C, 0x41, 0x7A, 0xB6, 0x85, 0x3F, 0xD0, 0xE9,
  0xEB, 0x2C, 0x47, 0xD1, 0x50, 0xFA, 0x39, 0x86,
  0x42, 0x1B, 0xAD, 0x78, 0xF9, 0xC5, 0x63, 0x0E,
  0xB8, 0xC7, 0x1E, 0x2D, 0x6F, 0x09, 0xA4, 0x53,
  0xC1, 0xAF, 0x92, 0x68, 0x0D, 0x34, 0xE7, 0x5B,
  0xAF, 0x42, 0x7C, 0x95, 0x61, 0xDE, 0x0B, 0x38,
  0x9E, 0xF5, 0x28, 0xC3, 0x70, 0x4A, 0x1D, 0xB6,
  0x43, 0x2C, 0x95, 0xFA, 0xBE, 0x17, 0x60, 0x8D,
  0x4B, 0x2E, 0xF0, 0x8D, 0x3C, 0x97, 0x5A, 0x61,
  0xD0, 0xB7, 0x49, 0x1A, 0xE3, 0x5C, 0x2F, 0x86,
  0x14, 0xBD, 0xC3, 0x7E, 0xAF, 0x68, 0x05, 0x92,
  0x6B, 0xD8, 0x14, 0xA7, 0x95, 0x0F, 0xE2, 0x3C,
  0xD2, 0x84, 0x6F, 0xB1, 0xA9, 0x3E, 0x50, 0xC7,
  0x1F, 0xD8, 0xA3, 0x74, 0xC5, 0x6B, 0x0E, 0x92,
  0x7B, 0x41, 0x9C, 0xE2, 0x06, 0xAD, 0xF3, 0x58,
  0x21, 0xE7, 0x4A, 0x8D, 0xFC, 0x90, 0x35, 0x6B
]

# 7 bits - miss the last one.
def __expand_key(in_str):
  return [ord(i) - ord('0') for i in "".join([bin(ord(x))[2:-1].rjust(7,"0") for x in in_str])]


def expand_data(in_str):
  return [ord(i) - ord('0') for i in "".join([bin(ord(x))[2:].rjust(8,"0") for x in in_str])]

def expand_data_npz(in_str):
  l = [int(i) for i in "".join([bin(x)[2:].rjust(8,"0") for x in in_str])]
  return l

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
    self.cumulative = 0
    pass

  def preprocess(self,MyPT):
    d = permute(IPTAB,expand_data_npz(MyPT))
    d_ex = permute(ETAB,d[32:])
    self.d_ex = [d_ex[i:i+6] for i in xrange(0,len(d_ex),6)]

  def generateSbox(self,byte_posn,key):
    tmp_d = int(mapToInteger(self.d_ex[byte_posn]))
    tmp_d ^= int(key) 
    tmp_d_bin = [ord(b) - ord("0") for b in bin(tmp_d)[2:].rjust(6,"0")]
    n = (tmp_d_bin[0] << 5) + (tmp_d_bin[5] << 4) + (tmp_d_bin[1] << 3) + (tmp_d_bin[2] << 2) + (tmp_d_bin[3] << 1) + tmp_d_bin[4]
    x = SBOX[(n >> 1) + (byte_posn * 32)]
    if n % 2 == 1:
      x = x & 0x0F
    else:
      x = x >> 4
    # return x
    if byte_posn == 0:
      return x
    else:
      x_cumulative = self.cumulative << 4
      x_cumulative |= x
      return x_cumulative
      # self.cumulative <<= 4
      # self.cumulative |= x
      # return self.cumulative

  def saveCumulative(self,byte_posn,key):
    self.cumulative = self.generateSbox(byte_posn,key)
  
if __name__ == "__main__":
  expand_data_npz = expand_data
  d = desIntermediateValue()
  d.preprocess(PT)
  for r in range(0,8):
    for i in range(0,48):
      print "Round %d Key candidate %02x: Sbox output: %02x" % (r, i,d.generateSbox(r,i))
