#!/usr/bin/env python3


class DriverInterface():
  def __init__(self):
    self.config = {}
    pass

  def init(self):
    pass

  def doOneIteration(self,in_text):
    return (in_text,out_text)
    
