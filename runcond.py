#!/usr/bin/python
#
# runcond.py - script to scan through fiberQA_cron.log for a given run
#              and report the information reported in the S (status)
#              packets by the front-end Vbias control board.
#
# author: richard.t.jones at uconn.edu
# version: july 12, 2014

import sys
import os
import re
import math

def Usage():
   print "Usage: runcond.py <run_number>"
   exit(1)

q_packet_log = ""

if sys.argv[1] == "-f":
   del(sys.argv[1])
   q_packet_log = sys.argv[1]
   del(sys.argv[1])

if len(sys.argv) < 2:
   Usage()
else:
   run_number = sys.argv[1]

if q_packet_log != "":
   cronlogfile = "runcond.log"
   cronlog = open(cronlogfile, "w")
   cronlog.write("New run starting now\n")
   cronlog.write("Trace of query packets during above sequences was:\n")
   qlog = open(q_packet_log, "r")
   run = -1
   for line in qlog:
      cronlog.write(line)
      packet = line.split()
      if (len(packet) == 30 or len(packet) == 40) and re.match("..53", packet[7]):
         run += 1
         cronlog.write("End of query packets\n")
         cronlog.write("Successful collection and analysis of run %s\n" % run)
         cronlog.write("New run starting now\n")
         cronlog.write("Trace of query packets during above sequences was:\n")
   cronlog.close()
else:
   cronlogfile = re.sub("runcond.py$", "", sys.argv[0]) + "fiberQA_cron.log"

cronlog = open(cronlogfile, "r")

for line in cronlog:
   run = -1
   norm = [0, 0]
   Tchip = [0, 0, 0]
   Achip = []
   for chan in range(16):
      Achip.append([0, 0, 0])
   m = re.match(r"New run starting (.*)", line)
   if m:
      date = m.group(1)
      requestor = "unknown"
   m2 = re.match(r"This run was requested by (.*)", line)
   if m2:
      requestor = m2.group(1)
   if re.match("Trace of query packets during above sequences was:", line):
      q_packet_count = 0
      for line in cronlog:
         if re.match("End of query packets", line):
            break
         packet = line.split()
         if (len(packet) == 30 or len(packet) == 40) and re.match("..53", packet[7]):
            q_packet_count += 1
            # ignore the first packet because some levels (eg. DAQhealth)
            # may not yet have reached their plateau after being set
            if q_packet_count == 1 and q_packet_log == "":
               continue
            T = int(packet[8], 16)
            Tchip[0] += 1.0
            Tchip[1] += T
            Tchip[2] += T*T
            for chan in range(16):
               A = int(packet[9+chan], 16)
               Achip[chan][0] += 1.0
               Achip[chan][1] += A
               Achip[chan][2] += A*A
      for line in cronlog:
         m = re.match("New run starting (.*)", line)
         if m:
            date = m.group(1)
            requestor = "unknown"
            run = -1
            break
         m = re.match("normalization pulse height mean = ([0-9.]+), rms = ([0-9.]+)", line)
         if m:
            norm[0] = float(m.group(1))
            norm[1] = float(m.group(2))
         m = re.match("Successful collection and analysis of run ([0-9]+)", line)
         if m:
            run = m.group(1)
            break
   if run != run_number:
      continue
   elif Tchip[0] > 0:
      Tmean = Tchip[1]/Tchip[0]
      Tvari = Tchip[2]/Tchip[0] - Tmean*Tmean
      Amean = []
      Avari = []
      for chan in range(16):
         Amean.append(Achip[chan][1]/Achip[chan][0])
         Avari.append(Achip[chan][2]/Achip[chan][0] - Amean[chan]*Amean[chan])

      # Vbias board temperature chip T(Celcius) = Tchip_value / 4
      Tmean_cb = Tmean/4.
      Trms_cb = math.sqrt(Tvari)/4.

      # Vbias board +5V power(V) = ADC[0]*1.005 * 2*Vref/2^12
      Vref = 2.5
      pos5V_level = Amean[2]*1.005 * 2*Vref/4096
      pos5V_rms = math.sqrt(Avari[2])*1.005 * 2*Vref/4096

      # Vbias board -5V power(V) = ADC[0]*1.001 * 2*Vref/2^12 * (R1+R2)/R2 -
      #                            (+5V power) * (R1/R2)
      # where Vref=2.5V, R1=100kOhm, R2=33.2kOhm
      R1 = 100.0e3
      R2 = 33.2e3
      neg5V_level = Amean[0]*1.001 * 2*Vref/4096 * (R1+R2)/R2 - pos5V_level * (R1/R2)
      neg5V_rms = math.sqrt(Avari[0])*1.001 * 2*Vref/4096 * (R1+R2)/R2

      # +3.3 power(V) = ADC[1]*1.005 * 2*Vref/2^12
      pos3_3V_level = Amean[1]*1.005 * 2*Vref/4096
      pos3_3V_rms = math.sqrt(Avari[1])*1.005 * 2*Vref/4096

      # VFPGApower(V) = ADC[3]*1.005 * 2*Vref/2^12
      VFPGApower_level = Amean[3]*1.005 * 2*Vref/4096
      VFPGApower_rms = math.sqrt(Avari[3])*1.005 * 2*Vref/4096

      # Vsumref1(V) = ADC[9]*1.005 * 2*Vref/2^12
      # Vsumref2(V) = ADC[12]*1.005 * 2*Vref/2^12
      Vsumref1_level = Amean[9]*1.005 * 2*Vref/4096
      Vsumref1_rms = math.sqrt(Avari[9])*1.005 * 2*Vref/4096
      Vsumref2_level = Amean[12]*1.005 * 2*Vref/4096
      Vsumref2_rms = math.sqrt(Avari[12])*1.005 * 2*Vref/4096

      # Vgainmode(V) = ADC[10]*2.018 * 2*Vref/4096
      Vgainmode_level = Amean[10]*2.018 * 2*Vref/4096
      Vgainmode_rms = math.sqrt(Avari[10])*2.018 * 2*Vref/4096

      # Vtherm1(V) = ADC[11]*1.005 * 2*Vref/4096
      # Vtherm2(V) = ADC[15]*1.005 * 2*Vref/4096
      Vtherm1_level = Amean[11]*1.005 * 2*Vref/4096
      Vtherm1_rms = math.sqrt(Avari[11])*1.005 * 2*Vref/4096
      Vtherm2_level = Amean[15]*1.005 * 2*Vref/4096
      Vtherm2_rms = math.sqrt(Avari[15])*1.005 * 2*Vref/4096

      # VDACtemp(V) = ADC[13]*1.005 * 2*Vref/4096
      VDACtemp_level = Amean[13]*1.005 * 2*Vref/4096
      VDACtemp_rms = math.sqrt(Avari[13])*1.005 * 2*Vref/4096

      # VDAChealth(V) = ADC[14]*40.50 * 2*Vref/4096
      VDAChealth_level = Amean[14]*40.50 * 2*Vref/4096
      VDAChealth_rms = math.sqrt(Avari[14])*40.50 * 2*Vref/4096

      # TDAC(Celcius) = TDAC_ref + (+5Vpower - VDACtemp - Vf_DACdiode)/Tcoef_DACdiode
      TDAC_ref = 25
      Vf_DACdiode = 0.650
      Tcoef_DACdiode = -0.0022
      TDAC_level = TDAC_ref + (pos5V_level - VDACtemp_level - Vf_DACdiode)/Tcoef_DACdiode
      TDAC_rms = VDACtemp_rms/abs(Tcoef_DACdiode)

      # Tpreamp1(Celcius) = c0 + c1*Vtherm1 + c2*Vtherm1^2 + c3*Vtherm1^3 + c4*Vtherm1^4
      # Tpreamp2(Celcius) = c0 + c1*Vtherm2 + c2*Vtherm2^2 + c3*Vtherm2^3 + c4*Vtherm2^4
      thermister_const = [142.973, -34.6419, 2.62172, -0.167948, 0.00531447]
      Vtherm1_log = math.log(100*(pos5V_level - Vtherm1_level)/(Vtherm1_level+1e-30))
      Vtherm1_plog = math.log(100*(pos5V_level - (Vtherm1_level + Vtherm1_rms))/ \
                                                  (Vtherm1_level + Vtherm1_rms + 1e-30))
      Tpreamp1_level = ((((thermister_const[4])*Vtherm1_log + \
                           thermister_const[3])*Vtherm1_log + \
                           thermister_const[2])*Vtherm1_log + \
                           thermister_const[1])*Vtherm1_log + \
                           thermister_const[0]
      Tpreamp1_rms = ((((thermister_const[4])*Vtherm1_plog + \
                         thermister_const[3])*Vtherm1_plog + \
                         thermister_const[2])*Vtherm1_plog + \
                         thermister_const[1])*Vtherm1_plog + \
                         thermister_const[0] - Tpreamp1_level
      Vtherm2_log = math.log(100*(pos5V_level - Vtherm2_level)/(Vtherm2_level+1e-30))
      Vtherm2_plog = math.log(100*(pos5V_level - (Vtherm2_level + Vtherm2_rms))/ \
                                                 (Vtherm2_level + Vtherm2_rms+1e-30))
      Tpreamp2_level = ((((thermister_const[4])*Vtherm2_log + \
                           thermister_const[3])*Vtherm2_log + \
                           thermister_const[2])*Vtherm2_log + \
                           thermister_const[1])*Vtherm2_log + \
                           thermister_const[0]
      Tpreamp2_rms = ((((thermister_const[4])*Vtherm2_plog + \
                         thermister_const[3])*Vtherm2_plog + \
                         thermister_const[2])*Vtherm2_plog + \
                         thermister_const[1])*Vtherm2_plog + \
                         thermister_const[0] - Tpreamp2_level

      print "run", run, "started", date
      print "run requestor", requestor
      print "  Tchip = ", "%.2f" % Tmean_cb, "+/-", "%.2f" % Trms_cb, "C"
      print "  +5V level = ", "%.3f" % pos5V_level, "+/-", "%.3f" % pos5V_rms, "V"
      print "  -5V level = ", "%.3f" % neg5V_level, "+/-", "%.3f" % neg5V_rms, "V"
      print "  +3.3V level = ", "%.3f" % pos3_3V_level, "+/-", "%.3f" % pos3_3V_rms, "V"
      print "  FPGA power = ", "%.3f" % VFPGApower_level, "+/-", "%.3f" % VFPGApower_rms, "V"
      print "  gainmode = ", "%.3f" % Vgainmode_level, "+/-", "%.3f" % Vgainmode_rms, "V"
      print "  Vsumref1 level = ", "%.3f" % Vsumref1_level, "+/-", "%.3f" % Vsumref1_rms, "V"
      print "  Vsumref2 level = ", "%.3f" % Vsumref2_level, "+/-", "%.3f" % Vsumref2_rms, "V"
      print "  VDAChealth level = ", "%.3f" % VDAChealth_level, "+/-", "%.3f" % VDAChealth_rms, "V"
      print "  TDAC level = ", "%.2f" % TDAC_level, "+/-", "%.2f" % TDAC_rms, "C"
      print "  Tpreamp1 level = ", "%.2f" % Tpreamp1_level, "+/-", "%.2f" % Tpreamp1_rms, "C"
      print "  Tpreamp2 level = ", "%.2f" % Tpreamp2_level, "+/-", "%.2f" % Tpreamp2_rms, "C"
      print "  normalization level = ", "%.1f" % norm[0], "+/-", "%.1f" % norm[1]

cronlog.close()
if q_packet_log != "":
   os.remove("runcond.log")
