#!/usr/bin/env python3

import serial
import time

s = serial.Serial("/dev/ttyUSB0",baudrate=105900,parity=serial.PARITY_EVEN,stopbits=serial.STOPBITS_ONE)
lt = 0

while True:
  while s.inWaiting() > 0:
    print("%f %02x " % (time.time(),ord(s.read(1))))
