#!/usr/bin/env python3

import sys
import dessupport # need more beer to refactor this piece of shit

DEFAULT_AES_SBOX = [99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118,202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192,183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21,4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117,9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132,83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207,208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168,81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210,205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115,96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219,224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121,231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8,186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138,112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158,225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223,140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22]

class AES_SboxOut_HW:
  def __init__(self):
    self.keyLength = 16
    self.fragmentMax = 256

  def loadPlaintextArray(self,pt):
    print("Loading plaintext array for AES SBox Out HW Attack...")
    self.pt = pt

  def loadCiphertextArray(self,ct):
    self.ct = ct

  def genIVal(self,tnum,bnum,kguess):
    global DEFAULT_AES_SBOX
    return bin(DEFAULT_AES_SBOX[self.pt[tnum,bnum]  ^ kguess]).count("1")

  def genIValRaw(self,tnum,bnum,kguess):
    global DEFAULT_AES_SBOX
    return DEFAULT_AES_SBOX[self.pt[tnum,bnum]  ^ kguess]

class DES_SboxOut_HW:
  def __init__(self):
    self.keyLength = 8  
    self.fragmentMax = 64

  def loadPlaintextArray(self,plaintexts):
    print("Loading plaintext array for DES SBox Out HW Attack")
    self.pt = plaintexts
    self.desManager = {}
    trace_count = plaintexts[:,0].size
    print("Pre-scheduling %d keys, this might take a while..." % trace_count)
    for tnum in range(0,trace_count):
      self.desManager[tnum] = dessupport.desIntermediateValue()
      self.desManager[tnum].preprocess(plaintexts[tnum])

  def loadCiphertextArray(self,ct):
    self.ct = ct

  def genIVal(self,tnum,bnum,kguess):
    return bin(self.desManager[tnum].generateSbox(bnum,kguess)).count("1")

  def genIValRaw(self,tnum,bnum,kguess):
    return self.desManager[tnum].generateSbox(bnum,kguess)

def usage():
  print("")
  print("You MUST specify a leakage model, typically with -a")
  print("Valid models are:")
  print(" - AES_SboxOut_HW")
  print(" - DES_SboxOut_HW")
  print("")

def fetchModel(modeltype):
  if modeltype == "AES_SboxOut_HW":
    return AES_SboxOut_HW()
  elif modeltype == "DES_SboxOut_HW":
    return DES_SboxOut_HW()
  else:
    usage()
    sys.exit(0)

if __name__ == "__main__":
  print("ATTACK MODEL TESTING, DO NOT CALL DIRECTLY.")
