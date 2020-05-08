#!/usr/bin/python

import numpy as np
import sys
import os
import time
import functools
import re

import roslib
import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String

import timeout
import Tkinter as tk
import ttk
from rtk_tools import dictlib

rospy.init_node("report",anonymous=True)
Config={
  "width":800,
  "altitude":"-24",
  "font":{
    "family":"System",
    "size":10
  },
  "color":{
    "background": "#00FF00",
    "label": ("#FFFFFF","#555555"),
    "ok": ("#000000","#CCCCCC"),
    "ng": ("#FF0000","#CCCCCC")
  },
  "format":'{:.3g}'
}
Values={}

def to_report(dat):
  global Values
  print "report",dat
  if "recipe" in Config:
    if len(Values["recipe"][0].cget("text"))==0:
      rp=rospy.get_param(Config["recipe"])
      Values["recipe"][0].configure(text=rp)
  for k,v in dat.items():
    if k in Values:
      Values[k][0].configure(text=str(Config["format"].format(v[0])))
      if(v[1]==0):
        Values[k][0].configure(foreground=okcolor[0])
        Values[k][0].configure(background=okcolor[1])
      else:
        Values[k][0].configure(foreground=ngcolor[0])
        Values[k][0].configure(background=ngcolor[1])
  return
def cb_report(s):
  print "str",type(s.data)
  ss=s.data[-1:-1]
  print ss
  dic=eval(s.data)
  timeout.set(functools.partial(to_report,dic),0)

def to_update():
  global Values
  for row in Values.values():
    for i in range(len(row)-1,0,-1):
      row[i].configure(text=row[i-1].cget("text"))
    row[0].configure(text="")
    row[0]["text"]=""
  return
def cb_update(s):
  timeout.set(to_update,0)

##############
def parse_argv(argv):
  args={}
  for arg in argv:
    tokens = arg.split(":=")
    if len(tokens) == 2:
      key = tokens[0]
      if re.match(r'\([ ]*([0-9.]+,[ ]*)*[0-9.]+[ ]*\)$',tokens[1]):
        # convert tuple-like-string to tuple
        args[key]=eval(tokens[1])
        continue
      args[key]=tokens[1]
  return args

####ROS Init####
rospy.init_node("report",anonymous=True)
try:
  conf=rospy.get_param("/config/report")
except:
  conf={}
try:
  dictlib.merge(Config,conf)
except Exception as e:
  print "get_param exception:",e.args

dictlib.merge(Config,parse_argv(sys.argv))

if "recipe" in Config:
  Config["keys"].insert(0,"recipe")
  Config["labels"].insert(0,"recipe")

####sub pub
rospy.Subscriber("/report",String,cb_report)
rospy.Subscriber("/report/update",Bool,cb_update)

####Layout####
font=(Config["font"]["family"],Config["font"]["size"],"normal")
bgcolor=Config["color"]["background"]
lbcolor=Config["color"]["label"]
okcolor=Config["color"]["ok"]
ngcolor=Config["color"]["ng"]

root=tk.Tk()
root.title("Report")
root.geometry(str(Config["width"])+"x100+0"+Config["altitude"])
frame=tk.Frame(root,bd=2,background=bgcolor)
frame.pack(fill='x',anchor='n',expand=1)

Values={}
for n,s in enumerate(Config["labels"]):
  frame.columnconfigure(n,weight=1)
  label=ttk.Label(frame,text=s,font=font,foreground=lbcolor[0],background=lbcolor[1],anchor='c')
  label.grid(row=0,column=n,padx=1,pady=1,sticky='nsew')
  k=Config["keys"][n]
  Values[k]=[]
  for i in range(4):
    label=ttk.Label(frame,font=font,foreground=okcolor[0],background=okcolor[1],anchor='e')
    label.grid(row=i+1,column=n,padx=1,pady=1,sticky='nsew')
    label.configure(text='')
    Values[k].append(label)

#if len(Displays)>0: timeout.set(functools.partial(cb_display,0),1)

while not rospy.is_shutdown():
  timeout.update()
  root.update()
  time.sleep(1)
