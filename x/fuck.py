#!/usr/bin/env python3

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException
import getopt
import sys
import uuid
from picoscope import ps2000a
import random
import numpy as np

class SIMController:
  def __init__(self):
    self.c = None      # fuck pyscard. seriously.
    pass

  def french_apdu(self,rand=None,autn=None,debug=False):
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    if debug:
      obs = ConsoleCardConnectionObserver()
      self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    # print(" !!! USING SHORTER SSTIC2018 PAPER APDU SEQUENCE !!!")
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x08, 0x04, 0x02, 0x2f, 0x00])
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x00,0x00] + [sw2])
    r,sw1,sw2 = self.c.transmit([0x00,0xB2,0x01,0x04] + [r[7]])
    r,sw1,sw2 = self.c.transmit([0x00,0xA4,0x04,0x04] + list(r[3:4 + r[3]]))
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x01,0x04] + [sw2])
    if rand is None and autn is None:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + [0xaa] * 16 + [0x10] + [0xbb] * 16
    else:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + rand + [0x10] + autn
    r,sw1,sw2 = self.c.transmit(authcmd)

  def nextg_apdu(self,rand=None,autn=None,debug=False):
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    if debug:
      obs = ConsoleCardConnectionObserver()
      self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    # print("ATR... : %s" % self.cardservice.connection.getATR())
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x08, 0x04, 0x02, 0x2f, 0x00])
    r,sw1,sw2 = self.c.transmit([0x00, 0xc0, 0x00, 0x00, 0x28])
    r,sw1,sw2 = self.c.transmit([0x00, 0xb2, 0x01, 0x04, 0x26])
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x04, 0x04, 0x10, 0xa0, 0x00, 0x00, 0x00, 0x87, 0x10, 0x02, 0xff, 0x33, 0xff, 0xff, 0x89, 0x01, 0x01, 0x01, 0x00])
    r,sw1,sw2 = self.c.transmit([0x00, 0xc0, 0x00, 0x00, 0x3e])
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x00, 0x04, 0x02, 0x6f, 0x07])
    r,sw1,sw2 = self.c.transmit([0x00, 0xc0, 0x00, 0x00, 0x25])
    r,sw1,sw2 = self.c.transmit([0x00, 0xb0, 0x00, 0x00, 0x09])
    if rand is None and autn is None:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + [0xaa] * 16 + [0x10] + [0xbb] * 16
    else:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + rand + [0x10] + autn
    r,sw1,sw2 = self.c.transmit(authcmd)

  def fuzzFile(self,observer=False):
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    if observer:
      obs = ConsoleCardConnectionObserver()
      self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    print("ATR... : %s" % self.cardservice.connection.getATR())
    print("Brute forcing...")
    out = ""
    for i in range(0,0xFF):
      for x in range(0,0xFF):
        response, sw1, sw2 = self.cardservice.connection.transmit([0x00,0xA4,0x08,0x04,0x02, i,x])
        if sw1 == 0x61:
          out += "Valid APDU from MF: %02x::%02x\n" % (i,x)
    return out

def usage():
  print("MILENAGE Power Trace Acquisition Utility")
  print(" -h: show this message")
  print(" -r: set sample rate (default 100MS)")
  print(" -n: set number of samples (default 100,000)")
  print(" -c: set number of traces (default 1000)")
  print(" -o: set vertical offset (default: 0.0)")
  print(" -w: set output file (default: [UUID].npz)")
  sys.exit(0)

CONFIG_SAMPLERATE = 64000000
CONFIG_SAMPLECOUNT = 500000
CONFIG_TRACECOUNT = 1000
CONFIG_ANALOGOFFSET = 0.0
CONFIG_WRITEFILE = "%s.npz" % uuid.uuid4()
VRANGE_PRIMARY = 0.05

if __name__ == "__main__":
  optlist, args = getopt.getopt(sys.argv[1:],"hr:n:c:o:w:",["help","samplerate=","samples=","count=","offset=","write_file="])
  for arg,value in optlist:
    if arg in ("-h","--help"):
      usage()
    elif arg in ("-r","--samplerate"):
      CONFIG_SAMPLERATE = int(value)
    elif arg in ("-n","--samples"):
      CONFIG_SAMPLECOUNT = int(value)
    elif arg in ("-c","--count"):
      CONFIG_TRACECOUNT = int(value)
    elif arg in ("-o","--offset"):
      CONFIG_ANALOGOFFSET = float(value)
    elif arg in ("-w","--write_file"):
      CONFIG_WRITEFILE = value
    else:
      print("Unknown argument: %s" % arg)
      sys.exit(0)
  print("-- Configuration Block --")
  print("-- Sample Rate: %d" % CONFIG_SAMPLERATE)
  print("-- Sample Count: %d" % CONFIG_SAMPLECOUNT)
  print("-- Trace Count: %d" % CONFIG_TRACECOUNT)
  print("-- Analog Offset: %f" % CONFIG_ANALOGOFFSET)
  print("-- Write File: %s" % CONFIG_WRITEFILE)
  x = input(" >>> CONFIRM Y/N <<< ")
  if x.rstrip() not in ["Y","y"]:
    print("Declined by user. Exiting program now")
    sys.exit(0)
  sc = SIMController()
  if CONFIG_TRACECOUNT == 1:
    print(" >> YOU MUST MANUALLY CAPTURE ON YOUR SCOPE <<") 
    print(" >> NO SCOPE AUTOMATION ON C = 1 <<") 
    next_rand = [random.randint(0,255) for _ in range(16)]
    next_autn = [random.randint(0,255) for _ in range(16)]
    str_rand = "".join(["%02x" % _ for _ in next_rand])
    str_autn = "".join(["%02x" % _ for _ in next_autn])
    print("%s:%s" % (str_rand,str_autn))
    # /configure?io=412&clk=13255.
    # /configure?io=412&clk=170000 (for "close" to first round)
    sc.french_apdu(next_rand,next_autn,debug=True)
    sys.exit(0)
  else:
    print(" >> Initializing numpy bullshit")
    traces = np.zeros((CONFIG_TRACECOUNT,CONFIG_SAMPLECOUNT),np.float32)
    data = np.zeros((CONFIG_TRACECOUNT,16),np.uint8)         # RAND
    data_out = np.zeros((CONFIG_TRACECOUNT,16),np.uint8)     # AUTN
    print(" >> Initializing picoscope")
    ps = ps2000a.PS2000a()
    ps.setChannel('A','DC',VRange=VRANGE_PRIMARY,VOffset=CONFIG_ANALOGOFFSET,enabled=True,BWLimited=False)
    ps.setChannel('B','DC',VRange=7.0,VOffset=0.0,enabled=True,BWLimited=False)
    nSamples = CONFIG_SAMPLECOUNT
    (freq,maxSamples) = ps.setSamplingFrequency(CONFIG_SAMPLERATE,nSamples)
    print("Actual sampling frequency: %d Hz" % freq)
    for i in range(0,CONFIG_TRACECOUNT):
      next_rand = [random.randint(0,255) for _ in range(16)]
      next_autn = [random.randint(0,255) for _ in range(16)]
      str_rand = "".join(["%02x" % _ for _ in next_rand])
      str_autn = "".join(["%02x" % _ for _ in next_autn])
      print("[%06d] %s:%s" % (i,str_rand,str_autn))
      ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=2000,enabled=True)
      ps.runBlock()
      sc.french_apdu(next_rand,next_autn)
      ps.waitReady()
      dataA = ps.getDataV('A',CONFIG_SAMPLECOUNT,returnOverflow=False)
      traces[i:] = dataA
      data[i:] = next_rand
      data_out[i:] = next_autn
    np.savez(CONFIG_WRITEFILE,traces=traces,data=data,data_out=data_out,freq=[freq])
