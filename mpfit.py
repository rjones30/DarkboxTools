#!/usr/bin/env python
#
# mpfit.py - script for fitting the multi-peak spectra
#            from dark rate runs taken with the DarkBox
#            in high gain mode.
#
# author: richard.t.jones at uconn.edu
# version: february 8, 2018

from ROOT import *
import numpy
import math
import re

gain_pC = 400. / 4096 # pC/count
gain_ratio = 18;
spigot = [5,6,7,11,12,13]
qmin = -40
qmax = 250
pmin = -50
pmax = 50

interactive_fit = 0

slope = [0]*30
Vintercept = [0]*30

darkbox_setVbias_conf = "/home/halld/online/TAGMutilities/setVbias.conf"

G_pC = [0] * 30

def pedmodel(var, par):
   """
   Model for the pedestal peak lineshape taken with the CAEN v792 QDC
   module integrating dark mode pulses from the UConn sipm preamp board
   operating in high gain mode.
      var[0] = pulse charge (pC)
      par[0] = sigma of central gaussian
      par[1] = height of central gaussian
      par[2] = height of left-side tail
      par[3] = length of left-side tail
      par[4] = height of right-side tail
      par[5] = length of right-side tail
      par[6] = global offset in q
   """
   q = var[0] - par[6]
   try:
      pm = par[1] * math.exp(-0.5 * q**2 / par[0]**2)
      if q < 0:
         pm -= par[3] * var[0] * math.exp(q / par[2])
      else:
         pm += par[4] * var[0] * math.exp(-q / par[5])
   except:
      print "math fault at var[0]=", var[0],
      print "par=", par[0], par[1], par[2], par[3], par[4], par[5]
      pm = 0
   return pm

def mpmodel(var, par):
   """
   Model for the multi-peak distributions taken with the CAEN v792 QDC
   module integrating dark mode pulses from the UConn sipm preamp board
   operating in high gain mode.
      var[0] = pulse charge (pC)
      par[0] = sigma of central gaussian
      par[1] = height of central gaussian
      par[2] = height of left-side tail
      par[3] = length of left-side tail
      par[4] = height of right-side tail
      par[5] = length of right-side tail
      par[6] = charge per pixel (counts)
      par[7] = norm of 1 peak
      par[8] = norm of 2 peak
      par[9] = norm of 3 peak
      par[10] = zero offset in q (counts)
   """
   q = var[0] - par[10]
   ppar = [par[0], par[1], par[2], par[3], par[4], par[5], 0]
   mpm = pedmodel([q], ppar)
   mpm += par[7] * pedmodel([(q - par[6])/2**0.5], ppar)
   mpm += par[8] * pedmodel([(q - 2*par[6])/3**0.5], ppar)
   mpm += par[9] * pedmodel([(q - 3*par[6])/4**0.5], ppar)
   return mpm

def mpfit(h1):
   """
   Fit histogram h1 to mpmodel in two stages:
     1) fit the pedestal to a double-gaussian lineshape
     2) fit the multi-peak spectrum using a sum of this basic lineshape,
        shifted and rescaled.
   """
   global pmin
   global pmax
   global interactive_fit
   c1.SetLogy()
   ymax = h1.GetMaximum()
   f1 = TF1("f1", pedmodel, pmin, pmax, 7)
   f1.SetParameters(3, ymax, ymax/10, 10, ymax/100, 20, -0.5)
   res1 = h1.Fit(f1, "s", "", pmin, pmax)
   par = res1.GetParams()
   f2 = TF1("f2", mpmodel, qmin, qmax, 11)
   f2.SetParameters(par[0], par[1], par[2], par[3], par[4], par[5],
                    40, .1, .01, .001, par[6])
   if interactive_fit:
      c1.Update()
      ans = raw_input("   pmin=" + str(pmin) + " ? ")
      if len(ans) > 0:
         pmin = float(ans)
      ans = raw_input("   pmax=" + str(pmax) + " ? ")
      if len(ans) > 0:
         pmax = float(ans)
      for i in range(0,11):
         ans = raw_input("   par[" + str(i) + "]=" +
                         str(f2.GetParameter(i)) + " ? ")
         if len(ans) > 0:
            f2.SetParameter(i, float(ans))
   res2 = h1.Fit(f2, "s", "", qmin, qmax)
   if res2.IsValid():
      interactive_fit = 0
      return res2
   else:
      c1.Update()
      ans = raw_input("bad fit: go interactive (enter) or quit (q)? ")
      if len(ans) > 0 and ans[0] == 'q':
         return res2
      interactive_fit = 1
      return mpfit(h1)

def dofits(runfile):
   """
   Open runfile created from a dark pulse run of the Dark Box by treemaker,
   generate single-pixel pulse charge spectra for each sipm channel, and
   store the fit results in a global array.
   """
   global interactive_fit
   try:
      f1 = TFile(runfile)
      v792=f1.Get("v792")
      if v792 and v792.GetEntries() < 1000:
         print "mpfit.dofits warning - insufficient statistics",
         print "in input file", runfile, ", giving up."
         return 0
   except:
      print "mpfit.dofits error - error reading tree from", runfile
      return 0
   hped = TH1D("hped", "", 1000, 0, 1000)
   global hfit
   hfit = [0] * 30
   ioffset = 0
   for i in range(0, 99999):
      chan = i + ioffset
      if chan > 14:
         break
      qvar = "Q[{0:d}]".format(spigot[chan / 5])
      qcon = "status==0x{0:x}01".format(chan + 1)
      qovfl = qvar + "<4096"
      qnot = "status==0x{0:x}01".format(((chan + 1) % 11) + 5)
      hped.Reset()
      if v792.Draw(qvar + ">>hped", qnot) > 0:
         pedestal = hped.GetXaxis().GetBinCenter(hped.GetMaximumBin())
         qvar = qvar + "-" + str(pedestal)
         name = "h" + str(chan)
         title = "fiber position " + str(chan)
         hfit[chan] = TH1D(name, title, 300, -50, 250)
         v792.Draw(qvar + ">>" + name, qcon + "&&" + qovfl)
         res = mpfit(hfit[chan])
         G_pC[chan] = res.Value(6)
         c1.Update()
         ans = raw_input("fiber # to fit, " +
                         "p to print, " +
                         "i to interact, " +
                         "or enter to continue, q to quit: ")
         try:
            n = int(ans)
         except:
            if len(ans) > 0 and ans[0] == 'q':
               break
            elif len(ans) > 0 and ans[0] == 'p':
               c1.Print(name + ".png")
               continue
            elif len(ans) > 0 and ans[0] == 'i':
               ioffset -= 1
               interactive_fit = 1
               continue
            else:
               continue
         ioffset = n - i - 1
      else:
         print "no data received for channel", chan
   ioffset = 0
   for i in range(0, 99999):
      chan = i + ioffset
      if chan > 14:
         break
      qvar = "Q[{0:d}]".format(spigot[chan / 5 + 3])
      qcon = "status==0x{0:x}01".format(chan + 1)
      qovf = qvar + "<4096"
      qnot = "status==0x{0:x}01".format(((chan + 1) % 11) + 5)
      hped.Reset()
      if v792.Draw(qvar + ">>hped", qnot) > 0:
         pedestal = hped.GetXaxis().GetBinCenter(hped.GetMaximumBin())
         qvar = qvar + "-" + str(pedestal)
         name = "h" + str(chan + 15)
         title = "fiber position " + str(chan + 15)
         hfit[chan + 15] = TH1D(name, title, 300, -50, 250)
         v792.Draw(qvar + ">>" + name, qcon + "&&" + qovfl)
         res = mpfit(hfit[chan + 15])
         G_pC[chan + 15] = res.Value(6)
         c1.Update()
         ans = raw_input("fiber # to fit, " +
                         "p to print, " +
                         "i to interact, " +
                         "or enter to continue, q to quit: ")
         try:
            n = int(ans)
         except:
            if len(ans) > 0 and ans[0] == 'q':
               break
            elif len(ans) > 0 and ans[0] == 'p':
               c1.Print(name + ".png")
               continue
            elif len(ans) > 0 and ans[0] == 'i':
               ioffset -= 1
               interactive_fit = 1
               continue
            else:
               continue
         ioffset = n - i - 16
      else:
         print "no data received for channel", chan + 15

def linfit(datfile):
   """
   Open datfile created from the results of several dark pulse runs
   at different -g values and fit the single-pixel charge to a linear
   function of the bias voltage. The datfile should be in multi-column
   format, with column headings in the following form:
   fiber   -g <G1>   -g <G2>   -g <G3> ...
   """
   global slope
   global Vintercept
   loadVbias(darkbox_setVbias_conf)
   gval = []
   for line in open(datfile):
      if re.match(r"^ *fiber ", line):
         headings = line.split()
         i = 1
         while i < len(headings):
            if headings[i] == "-g":
               i += 1
               gval.append(float(headings[i]))
               i += 1
      elif re.match(r"^ *[0-9]", line):
         values = line.split()
         fiber = int(values[0])
         row = fiber % 5 + 1
         col = int(fiber / 5) + 1
         i = 1
         xval = []
         yval = []
         while i < len(values):
            x = gval[i-1] / setVbias_gain[row][col]
            xval.append(x + setVbias_threshold[row][col])
            y = float(values[i])
            yval.append(y * gain_pC / gain_ratio)
            i += 1
         graph = TGraphErrors(len(xval), 
                              numpy.array(xval, dtype=float),
                              numpy.array(yval, dtype=float),
                              numpy.array([0]*len(yval), dtype=float),
                              numpy.array([0.01]*len(yval), dtype=float))
         res = graph.Fit("pol1", "s")
         graph.SetMinimum(0)
         graph.SetTitle("fiber " + str(fiber))
         graph.Draw("AP")
         if res.IsValid():
            b = res.Value(0)
            m = res.Value(1)
            slope[fiber] = m
            Vintercept[fiber] = -b / m
         c1.Update()
         raw_input("ok? ")

def loadVbias(setVbias_conf):
   """
   Reads an existing setVbias.conf file (pathname passed in setVbias_conf)
   and saves the contents in a set of global 2d arrays named as follows.
    setVbias_board[row][column] = "board" column (int)
    setVbias_channel[row][column] = "channel" column (int)
    setVbias_threshold[row][column] = "threshold" column (V)
    setVbias_gain[row][column] = "gain" column ((pF/pixel)
    setVbias_yield[row][column] = "yield" column (pixel/hit/V)
   """
   global setVbias_board
   global setVbias_channel
   global setVbias_threshold
   global setVbias_gain
   global setVbias_yield
   setVbias_board = {row : {} for row in range(0,6)}
   setVbias_channel = {row : {} for row in range(0,6)}
   setVbias_threshold = {row : {} for row in range(0,6)}
   setVbias_gain = {row : {} for row in range(0,6)}
   setVbias_yield = {row : {} for row in range(0,6)}
   for line in open(setVbias_conf):
      try:
         grep = re.match(r"  *([0-9a-fA-F]+)  *([0-9]+)  *([0-9]+)  *([0-9]+) " +
                         r" *([0-9.]+)  *([0-9.]+)  *([0-9.]+) *", line)
         if grep:
            row = int(grep.group(4))
            column = int(grep.group(3))
            setVbias_board[row][column] = int(grep.group(1), 16)
            setVbias_channel[row][column] = int(grep.group(2))
            setVbias_threshold[row][column] = float(grep.group(5))
            setVbias_gain[row][column] = float(grep.group(6))
            setVbias_yield[row][column] = float(grep.group(7))
      except:
         continue

