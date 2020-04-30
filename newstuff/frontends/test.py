#!/usr/bin/env python3

import sys

class CaptureInterface():
  def __init__(self):
    print("Acquisition frontend ready")

  def arm(self):
    print("Acquisition frontend armed")
  
  def disarm(self):
    print("Acquisition frontend disarmed")

    
