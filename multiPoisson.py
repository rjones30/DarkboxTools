#
# multiPoisson.py - computes the frequency distribution of a multi-Poisson
#                   model based on two means, lamda[0] and lamda[1], using
#                   a Monte Carlo procedure.
#
# author: richard.t.jones at uconn.edu
# version: february 5, 2016

lamda = [1., 1.]

import math
from ROOT import *

def mcgen(n=10000, seed=469359):
   rangen = TRandom(seed)
   hist = TH1F("multiP", "multi-Poisson distribution",
               200, 0, 2 * lamda[0] * lamda[1])
   for i in range(0, n):
      n1 = rangen.Poisson(lamda[0])
      n2 = rangen.Poisson(n1 * lamda[1])
      hist.Fill(float(n2));
   return hist
