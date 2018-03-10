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

qmin = -10
qmax = 1000
gainPC = 0.45
counts_per_pixel = 4096. / 400 * gainPC
spigot = {(0, 1350): [5, 6, 7, 8, 15, 10],
          (1351, 999999): [5, 6, 7, 11, 12, 13]}

illumfactor = [1.098923296, 0.990691590, 0.977094900,
               0.922227637, 0.864488052, 1.057581770,
               0.879137287, 0.816446074, 0.696973847,
               0.629783932, 0.925561932, 0.832048925,
               0.800264880, 0.746910921, 0.677498668,

               0.855195988, 0.871927962, 0.877830427,
               0.932024365, 0.985493368, 0.878583292,
               0.897849013, 0.915511920, 0.959503139,
               1.015711175, 0.907068148, 0.918134200,
               0.948502848, 0.983828750, 1.047791781]

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
   logfile = "textlogs/run_{0:03d}.txt".format(run)
   if os.path.isfile(logfile):
      os.remove(logfile)
   textlog = open(logfile, "w")
   runcond = os.path.dirname(sys.argv[0]) + "/runcond.py"
   response = subprocess.Popen([runcond, str(run)], stdout=subprocess.PIPE).communicate()[0]
   for cond in response.split('\n'):
      textlog.write(cond + "\n")
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
   logfile = "textlogs/run_{0:03d}.txt".format(run)
   textlog = open(logfile, "a")
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
   textlog.write("Temperature correction factors are {0:f}, {1:f}\n".format(tcorr1, tcorr2))
   textlog.write("\n fiber      pedestal        entries           mean          sigma      mean_corr     sigma_corr\n")

   hdir = "histos/run_" + str(run)
   for oldimg in os.listdir(hdir):
      os.unlink(hdir + "/" + oldimg)

   hist = []
   for chan in range(0, 15):
      qvar = "Q[{0:d}]".format(qdc_channel(run, chan / 5 + 1))
      qcon = "status==0x{0:x}01".format(chan + 1)
      qovfl = qvar + "<4096"
      qnot = "status==0x{0:x}01".format(((chan + 1) % 11) + 5)
      hq = gROOT.FindObject("hq")
      if hq:
         hq.Delete()
      nbins = int((qmax - qmin) * counts_per_pixel / tcorr1)
      hq = TH1D("hq", "", nbins, qmin, qmax)
      if v792.Draw(qvar + ">>hq", qnot) > 0:
         pedestal = hq.GetXaxis().GetBinCenter(hq.GetMaximumBin())
         qvar = "(" + qvar + "-" + str(pedestal) + ")*" + \
                                   str(tcorr1) + "/" + str(counts_per_pixel)
         v792.Draw(qvar + ">>hq", qcon + "&&" + qovfl)
         qpeak = hq.GetXaxis().GetBinCenter(hq.GetMaximumBin())
         if qpeak < 25:
            qpeak = 25
            c1.SetLogy(1)
         else:
            c1.SetLogy(0)
         nbins = int((2*qpeak + 10) * counts_per_pixel / tcorr1)
         nbins /= 10 if qpeak > 25 else 1
         hq.Delete()
         hq = TH1D("hq", "", nbins, -10, 2*qpeak)
         v792.Draw(qvar + ">>hq", qcon + "&&" + qovfl)
         mean = hq.GetMean()
         sigma = hq.GetRMS()
         entries = hq.GetEntries()
         textlog.write("{0:5d}{1:15f}{2:15f}{3:15f}{4:15f}{5:15f}{6:15f}\n"
                .format(chan + 1, pedestal, entries, mean, sigma,
                        mean * illumfactor[chan],
                        sigma * illumfactor[chan]))
         hq.SetTitle("fiber {0:d}".format(chan + 1))
         hq.GetXaxis().SetTitle("pulse height (pixels)")
         hq.Draw()
         c1.Print("histos/run_{0:03d}/fiber_{1:d}.png".format(run, chan + 1))
      else:
         print "no data received for channel", chan
   for chan in range(0, 15):
      qvar = "Q[{0:d}]".format(qdc_channel(run, chan / 5 + 4))
      qcon = "status==0x{0:x}01".format(chan + 1)
      qovf = qvar + "<4096"
      qnot = "status==0x{0:x}01".format(((chan + 1) % 11) + 5)
      hq = gROOT.FindObject("hq")
      if hq:
         hq.Delete()
      nbins = int((qmax - qmin) * counts_per_pixel / tcorr2)
      hq = TH1D("hq", "", nbins, qmin, qmax)
      if v792.Draw(qvar + ">>hq", qnot) > 0:
         pedestal = hq.GetXaxis().GetBinCenter(hq.GetMaximumBin())
         qvar = "(" + qvar + "-" + str(pedestal) + ")*" + \
                                   str(tcorr2) + "/" + str(counts_per_pixel)
         v792.Draw(qvar + ">>hq", qcon + "&&" + qovf)
         qpeak = hq.GetXaxis().GetBinCenter(hq.GetMaximumBin())
         if qpeak < 25:
            qpeak = 25
            c1.SetLogy(1)
         else:
            c1.SetLogy(0)
         nbins = int((2*qpeak + 10) * counts_per_pixel / tcorr2)
         nbins /= 10 if qpeak > 25 else 1
         hq.Delete()
         hq = TH1D("hq", "", nbins, -10, 2*qpeak)
         v792.Draw(qvar + ">>hq", qcon + "&&" + qovfl)
         mean = hq.GetMean()
         sigma = hq.GetRMS()
         entries = hq.GetEntries()
         textlog.write("{0:5d}{1:15f}{2:15f}{3:15f}{4:15f}{5:15f}{6:15f}\n"
                .format(chan + 16, pedestal, entries, mean, sigma,
                        mean * illumfactor[chan + 15], 
                        sigma * illumfactor[chan + 15]))
         hq.SetTitle("fiber {0:d}".format(chan + 16))
         hq.GetXaxis().SetTitle("pulse height (pixels)")
         hq.Draw()
         c1.Print("histos/run_{0:03d}/fiber_{1:d}.png".format(run, chan + 16))
      else:
         print "no data received for channel", chan

def qdc_channel(run, column):
   """
   Look up which qdc input channel is occupied by the sum output from column for this run.
   """
   for key in spigot:
      if run >= key[0] and run <= key[1]:
         return spigot[key][column - 1]
   print "Error in qdc_channel: run number {0} not found in spigot table."
   return 0

if len(sys.argv) < 2:
   usage()

run = 0
try:
   run = int(sys.argv[1])
except ValueError:
   usage()

conditions = get_conditions(run)
plot(run)
