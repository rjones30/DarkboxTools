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

from ROOT import *
import sys

def usage():
   print "Usage: plotmaker.py <run_number>"
   sys.exit(1)

def plot(run):
   rootfile = "data/simple_{0:03d}.root".format(run)
   f = TFile(rootfile)
   if not f.IsOpen():
      print "Input file", rootfile, "not found, cannot continue."
      sys.exit(1)
   c1 = TCanvas("c1","C1",20,20,400,400);

   hist = []
   spigot = [5, 6, 7, 8, 15, 10];
   for chan in range(0, 15):
      qvar = "Q[{0:d}]".format(spigot[chan / 5])
      qcon = "status==0x{0:x}01".format(chan + 1)
      qnot = "status==0x{0:x}01".format(((chan + 1) % 11) + 5)
      v792.Draw(qvar, qnot)
      htemp = gROOT.FindObject("htemp")
      pedestal = htemp.GetMean()
      qvar = "(" + qvar + "-" + str(pedestal) + ")/" + str(counts_per_pixel)
      v792.Draw(qvar, qcon)
      htemp = gROOT.FindObject("htemp")
      htemp.SetTitle("fiber {0:d}".format(chan + 1))
      htemp.GetXaxis().SetTitle("pulse height (pixels)")
      htemp.Draw()
      c1.Print("histos/run_{0:03d}/fiber_{1:d}.png".format(run, chan + 1))
      qvar2 = "Q[{0:d}]".format(spigot[chan / 5 + 3])
      v792.Draw(qvar2, qnot)
      htemp = gROOT.FindObject("htemp")
      pedestal2 = htemp.GetMean()
      qvar2 = "(" + qvar2 + "-" + str(pedestal2) + ")/" + str(counts_per_pixel)
      v792.Draw(qvar2, qcon)
      htemp = gROOT.FindObject("htemp")
      htemp.SetTitle("fiber {0:d}".format(chan + 16))
      htemp.GetXaxis().SetTitle("pulse height (pixels)")
      htemp.Draw()
      c1.Print("histos/run_{0:03d}/fiber_{1:d}.png".format(run, chan + 16))

if len(sys.argv) < 2:
   usage()

run = 0
try:
   run = int(sys.argv[1])
except ValueError:
   usage()
plot(run)
