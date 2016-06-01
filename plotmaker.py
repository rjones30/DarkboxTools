#!/usr/bin/python
#
# plotmaker.py - pyroot macro for generating standard plots of dark box
#                pulse height distributions for a bunch of 30 fibers.
#                Results are stored in the histos directory where the
#                web interfaces to fiberQA expects to find them.
#
# author: richard.t.jones at uconn.edu
# version: february 5, 2016
#

gainPC = 0.45
counts_per_pixel = 4096. / 400 * gainPC

import subprocess
import sys
import os
import re
import math

from ROOT import *

def usage():
   print "Usage: plotmaker.py <run_number>"
   sys.exit(1)

def get_conditions(run):
   conditions = {}
   runcond = os.path.dirname(sys.argv[0]) + "/runcond.py"
   response = subprocess.Popen([runcond, str(run)], stdout=subprocess.PIPE).communicate()[0]
   for cond in response.split('\n'):
      m1 = re.match(r" *([^ ]+) level = +([.0-9]+) .*", cond)
      if m1:
         conditions[m1.group(1)] = float(m1.group(2))
         print "just loaded condition for var", m1.group(1), "as", m1.group(2)
   return conditions

def plot(run):
   rootfile = "data/simple_{0:03d}.root".format(run)
   f = TFile(rootfile)
   if not f.IsOpen():
      print "Input file", rootfile, "not found, cannot continue."
      sys.exit(1)
   c1 = TCanvas("c1","C1",20,20,400,400);

   # These temperature correction factors were derived from a study by James McIntyre
   # and reported to me [rtj] in an email dated May 19, 2016.

   if "Tpreamp1" in conditions:
      tcorr1 = math.exp(0.101 * (conditions["Tpreamp1"] - 25))
   else:
      tcorr1 = 1
   if "Tpreamp2" in conditions:
      tcorr2 = math.exp(0.121 * (conditions["Tpreamp2"] - 25))
   else:
      tcorr2 = 1
   print "Temperature correction factors are", tcorr1, tcorr2

   hdir = "histos/run_" + str(run)
   for oldimg in os.listdir(hdir):
      os.unlink(hdir + "/" + oldimg)

   hist = []
   spigot = [5, 6, 7, 8, 15, 10];
   for chan in range(0, 15):
      qvar = "Q[{0:d}]".format(spigot[chan / 5])
      qcon = "status==0x{0:x}01".format(chan + 1)
      qnot = "status==0x{0:x}01".format(((chan + 1) % 11) + 5)
      if v792.Draw(qvar, qnot) > 0:
         htemp = gROOT.FindObject("htemp")
         pedestal = htemp.GetMean()
         qvar = "(" + qvar + "-" + str(pedestal) + ")*" + \
                                   str(tcorr1) + "/" + str(counts_per_pixel)
         v792.Draw(qvar, qcon)
         htemp = gROOT.FindObject("htemp")
         htemp.SetTitle("fiber {0:d}".format(chan + 1))
         htemp.GetXaxis().SetTitle("pulse height (pixels)")
         htemp.Draw()
         c1.Print("histos/run_{0:03d}/fiber_{1:d}.png".format(run, chan + 1))
      else:
         print "no data received for channel", chan
      qvar2 = "Q[{0:d}]".format(spigot[chan / 5 + 3])
      if v792.Draw(qvar2, qnot) > 0:
         htemp = gROOT.FindObject("htemp")
         pedestal2 = htemp.GetMean()
         qvar2 = "(" + qvar2 + "-" + str(pedestal2) + ")*" + \
                                     str(tcorr2) + "/" + str(counts_per_pixel)
         v792.Draw(qvar2, qcon)
         htemp = gROOT.FindObject("htemp")
         htemp.SetTitle("fiber {0:d}".format(chan + 16))
         htemp.GetXaxis().SetTitle("pulse height (pixels)")
         htemp.Draw()
         c1.Print("histos/run_{0:03d}/fiber_{1:d}.png".format(run, chan + 16))
      else:
         print "no data received for channel", chan

if len(sys.argv) < 2:
   usage()

run = 0
try:
   run = int(sys.argv[1])
except ValueError:
   usage()

conditions = get_conditions(run)
plot(run)
