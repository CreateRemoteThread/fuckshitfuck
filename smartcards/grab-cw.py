#!/usr/bin/env python3

import chipwhisperer as cw
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException
import random
import numpy as np
import support.filemanager
import time

class SIMController:
  def __init__(self):
    self.c = None      # fuck pyscard. seriously.
    pass

  def french_apdu(self,rand=None,autn=None,scope=None,debug=False):
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    if debug:
      obs = ConsoleCardConnectionObserver()
      self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x08, 0x04, 0x02, 0x2f, 0x00])
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x00,0x00] + [sw2])
    r,sw1,sw2 = self.c.transmit([0x00,0xB2,0x01,0x04] + [r[7]])
    r,sw1,sw2 = self.c.transmit([0x00,0xA4,0x04,0x04] + list(r[3:4 + r[3]]))
    scope.arm()
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x00,0x00] + [sw2])
    if rand is None and autn is None:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + [0xaa] * 16 + [0x10] + [0xbb] * 16
    else:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + rand + [0x10] + autn
    r,sw1,sw2 = self.c.transmit(authcmd)

sc = SIMController()
print("Initializing ChipWhisperer")
scope = cw.scope(scope_type = cw.scopes.OpenADC)
scope.default_setup()
scope.gain = 25
scope.adc.samples = 24000
scope.adc.basic_mode = "rising_edge"
scope.trigger.triggers = "tio4"

CONFIG_TRACECOUNT = 2
CONFIG_SAMPLECOUNT = 24000

print("Setting up structures")
traces = np.zeros((CONFIG_TRACECOUNT,CONFIG_SAMPLECOUNT),np.float32)
data = np.zeros((CONFIG_TRACECOUNT,16),np.uint8)         # RAND
data_out = np.zeros((CONFIG_TRACECOUNT,16),np.uint8)     # AUTN

print("Begin main capture loop")
for i in range(0,CONFIG_TRACECOUNT):
  next_rand = [random.randint(0,255) for _ in range(16)]
  next_autn = [random.randint(0,255) for _ in range(16)]
  # scope.arm()
  sc.french_apdu(next_rand,next_autn,scope)
  scope.capture()
  dataA = scope.get_last_trace()
  str_rand = "".join(["%02x" % _ for _ in next_rand])
  str_autn = "".join(["%02x" % _ for _ in next_autn])
  print("[%06d] %s:%s" % (i,str_rand,str_autn))
  traces[i:] = dataA
  data[i:] = next_rand
  data_out[i:] = next_autn

support.filemanager.save("./lol123",traces=traces,data=data,data_out=data_out)
