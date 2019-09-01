#!/usr/bin/env python3

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException
import getopt
import sys

class SIMController:
  def __init__(self):
    self.c = None      # fuck pyscard. seriously.
    pass

  def nextg_apdu(self):
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    obs = ConsoleCardConnectionObserver()
    self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    print("ATR... : %s" % self.cardservice.connection.getATR())
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x08, 0x04, 0x02, 0x2f, 0x00])
    r,sw1,sw2 = self.c.transmit([0x00, 0xc0, 0x00, 0x00, 0x28])
    r,sw1,sw2 = self.c.transmit([0x00, 0xb2, 0x01, 0x04, 0x26])
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x04, 0x04, 0x10, 0xa0, 0x00, 0x00, 0x00, 0x87, 0x10, 0x02, 0xff, 0x33, 0xff, 0xff, 0x89, 0x01, 0x01, 0x01, 0x00])
    r,sw1,sw2 = self.c.transmit([0x00, 0xc0, 0x00, 0x00, 0x3e])
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x00, 0x04, 0x02, 0x6f, 0x07])
    r,sw1,sw2 = self.c.transmit([0x00, 0xc0, 0x00, 0x00, 0x25])
    r,sw1,sw2 = self.c.transmit([0x00, 0xb0, 0x00, 0x00, 0x09])
    authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + [0xaa] * 16 + [0x10] + [0xbb] * 16
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
  print("USAGE TRIGGERED")
  sys.exit(0)

if __name__ == "__main__":
  if len(sys.argv) == 1:
    sc = SIMController()
    sc.nextg_apdu()
    sys.exit(0)
    a = [0x80, 0x10, 0x00, 0x00, 0x1e, 0x10, 0xf7, 0x1f, 0xec, 0xce, 0x1f, 0x9c, 0x00, 0x87, 0x94, 0x00, 0x00, 0x1f, 0xe2, 0x00, 0x00, 0x00, 0x43, 0xe0, 0x00, 0x03, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0c, 0x91, 0x0f, 0x80, 0x12, 0x00, 0x00, 0x0f, 0x12, 0xd0, 0x0d, 0x81, 0x03, 0x01, 0x05, 0x00, 0x82, 0x02, 0x81, 0x82, 0x99, 0x02]
    for i in range(7,len(a)):
      try:
        r,sw1,sw2 = sc.nextg_apdu(a[0:i])
        print("Length %d, result %d:%d:%s" % (i,sw1,sw2,repr(r)))
      except:
        print("Length: %d, crash" % i)
    # f = sc.fuzzFile(True)
    # print(f)
  else:
    try:
      opts, remainder = getopt.getopt(sys.argv[1:],"hm:",["help","mode="])
    except:
      print("Could not getopt.getopt")
      sys.exit(0)
    for opt, arg in opts:
      if opt in ("-h","--help"):
        usage()
