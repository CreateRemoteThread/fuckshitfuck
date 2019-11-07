#!/usr/bin/env python3

from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import glob
import os
import numpy as np

GLOBAL_DATA = None
CONFIG_FPREFIX = None
STATE_POSN = 0
label_current_sample = None
current_guess = None
ax1 = None
ax2 = None
fig = None

def redraw_plots():
  global CONFIG_FPREFIX,STATE_POSN,ax1,fig,current_guess,ax2
  ax1.cla()
  ax2.cla()
  cg_val = current_guess.get()
  if "-" not in cg_val:
    cg_val = cg_val + "-"
  cg_all = glob.glob("toothpicks/%s*.npy" % cg_val)
  if len(cg_all) == 0 and cg_val != "None":
    print("No toothpick for %s" % cg_val)
  for fn in cg_all:
    # print(fn)
    data = np.load(fn)
    ax1.plot(abs(data[0][:75000]),c='b',alpha=0.3)
    ax2.plot(abs(data[1][:75000]),c='b',alpha=0.3)
  data = np.load("%s/%d.npy" % (CONFIG_FPREFIX,STATE_POSN))
  ax1.plot(abs(data[0][:75000]),c='r')
  ax2.plot(abs(data[1][:75000]),c='r')
  fig.canvas.draw_idle()

def next_sample():
  global CONFIG_FPREFIX, STATE_POSN
  if os.path.isfile("%s/%d.npy" % (CONFIG_FPREFIX,STATE_POSN + 1)):
    STATE_POSN = STATE_POSN + 1
  else:
    print("Can't set STATE_POSN %d" % (STATE_POSN + 1))
  label_current_sample.config(text="%s/%d.npy" % (CONFIG_FPREFIX,STATE_POSN))
  redraw_plots()

def prev_sample():
  global CONFIG_FPREFIX, STATE_POSN,ax1
  if os.path.isfile("%s/%d.npy" % (CONFIG_FPREFIX,STATE_POSN - 1)):
    STATE_POSN = STATE_POSN - 1
  else:
    print("Can't set STATE_POSN %d" % (STATE_POSN - 1))
  label_current_sample.config(text="%s/%d.npy" % (CONFIG_FPREFIX,STATE_POSN))
  redraw_plots()

def start(data_array,fprefix):
  global STATE_POSN,label_current_sample,current_guess,CONFIG_FPREFIX,ax1,fig,GLOBAL_DATA,ax2
  CONFIG_FPREFIX = fprefix
  GLOBAL_DATA = data_array
  top = Tk()
  top.title("Duct-Tape Signal Viewer v0.1")
  fig = plt.Figure()
  # fig,ax1 = plt.subplots(1)
  chart_control = FigureCanvasTkAgg(fig,master=top)
  chart_control.get_tk_widget().pack(side=TOP,expand=1,fill=BOTH)
  # this has to be a subplot of the figure
  # and NOT as subplot from the mpl root
  # because computers make sense.
  ax1 = fig.add_subplot(211)
  ax2 = fig.add_subplot(212)
  ctrl_frame = Frame(top)
  button_prev_sample = Button(ctrl_frame,text="<",command=prev_sample)
  button_prev_sample.pack(side=LEFT)
  label_current_sample = Label(ctrl_frame,text="%s/%d.npy" % (fprefix,STATE_POSN))
  label_current_sample.pack(side=LEFT,expand=1)
  button_next_sample = Button(ctrl_frame,text=">",command=next_sample)
  button_next_sample.pack(side=RIGHT)
  ctrl_frame.pack(side=BOTTOM,fill="x")
  ctrl_frame2 = Frame(top)
  label_current_guess = Label(ctrl_frame2,text="Guess: ")
  label_current_guess.pack(side=LEFT)
  current_guess = Entry(ctrl_frame2)
  current_guess.insert(0,"None")
  current_guess.pack(side=LEFT,fill="x",expand=1)
  button_next_guess = Button(ctrl_frame2,text="Try it!",command=redraw_plots)
  button_next_guess.pack(side=RIGHT)
  ctrl_frame2.pack(side=BOTTOM,fill="x")
  top.mainloop()
