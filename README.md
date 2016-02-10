# DarkboxTools - tools for reading scintillating fiber light yields from the pulser dark box in UConn Physics lab 402

## Authors

* Richard Jones, University of Connecticut, Storrs, CT

## Description

UConn Physics lab 402 is equipped with a dark box for testing scintillating fibers to be used in the GlueX tagger microscope (TAGM) detector. The fibers have square cross sections of transverse dimension 2mm and are arranged in rectangular blocks 3 wide x 5 high. Two such blocks are fixed to an aluminum block called a "popsicle stick", arranged in a side-by-side staggered configuration collectively called a fiber bundle. The block closest to the access panel of the dark box is called the front block, and the other is called the back block. The darkbox electronics are configured to permit simultaneous readout of all 30 fibers in a bundle. A laser diode is mounted in the top of the darkbox and coupled to a fast pulser circuit that generates a self-triggered sequence of electronic pulses of width ~1ns fwhm at a rate of roughly 100 kHz. The electronic signals are coupled through a backplane to a connector panel on the back side of the darkbox, where lemo cables are connected to carry the signals to the data acquisition (DAq) electronics. The DAq consists of a VME crate equipped with a readout controller (ROC), a trigger interface board (TI), a discriminator (Disc), and a charge-integrating ADC (qADC).

The purpose of DarkboxTools is to provide a simple web browser interface for doing pulser scans and reporting the results in the form of pulse height histograms for each fiber. A diffuser is mounted between the laser diode and the fiber bundle to help ensure that all fibers receive an equal intensity of light in a given pulse. The CODA data acquisition system from Jefferson Lab is used to collect integrated charge data from each pulse for each fiber. Together with the fiber pulse heights, the feedback pulse height from a photodiode integrated together with the laser diode is also digitized in case pulse intensity variations might contribute to the total spread in observed pulse heights. DarkboxTools is designed around the CODA-inspired idea of a "run", which is a single unbroken sequence of events associated with the firing of the pulser. Each event contains the following data:

1. q[0]..q[4] - individual pulse heights from fibers 1-5 (first in the bundle of 30)
2. q[5] - summed pulse heights from fibers 1-5
3. q[6] - summed pulse heights from fibers 6-10
4. q[7] - summed pulse heights from fibers 11-15
5. q[8] - summed pulse heights from fibers 16-20
6. q[15] - summed pulse heights from fibers 21-25
7. q[10] - summed pulse heights from fibers 26-30
8. q[11] - normalization pulse height from pulser feedback diode
9. status - bias voltage configuration status word (see below)

As the above list indicates, only the light output from the first 5 fibers in the bundle can be accessed individually. However, by selectively turning off all of the bias voltages except for one in each set of 5, one can perform a scan to measure the individual response of each fiber. The status word in each event carries the information about which of the fibers is fully biased at the time the event occurred. The meaning of the status words are listed below.
1. 0x0 - all Vbias voltages are off
2. 0x101 - only fibers 1 and 16 are lit
3. 0x201 - only fibers 2 and 17 are lit
4. 0x201 - only fibers 3 and 18 are lit
5. 0x201 - only fibers 4 and 19 are lit
6. 0x201 - only fibers 5 and 20 are lit
7. 0x201 - only fibers 6 and 21 are lit
8. 0x201 - only fibers 7 and 22 are lit
9. 0x201 - only fibers 8 and 23 are lit
10. 0x201 - only fibers 9 and 24 are lit
11. 0x201 - only fibers 10 and 25 are lit
12. 0x201 - only fibers 11 and 26 are lit
13. 0x201 - only fibers 12 and 27 are lit
14. 0x201 - only fibers 13 and 28 are lit
15. 0x201 - only fibers 14 and 29 are lit
16. 0x201 - only fibers 15 and 30 are lit
16. 0xff1 - Vbias values are changing, do not use

## Quick start guide

DarkboxTools consists of several components that make up the web interface to CODA and the associated analysis components.

1. **index.cgi** - copy this cgi script into a dedicated directory within the document tree of an apache web server, andmake sure that the directory has ExecCGI permissions. This directory should have write permissions granted to the apache user, and should have a folders named histos and data inside, also enabled for writing. CODA should be configured to output its event files in the data directory.
2. **fiberQA_cron.sh** - this script needs to be customized to the location chosen for index.cgi above. Normally this bash script should sit in the same directory, but need not be owned or executable by the apache user. Instead, it should be owned and executable by a user who has set up automatic ssh login on the ROC and who owns a dedicated vnc session which will play host to the CODA data acquisition system windows. It should have execute permission for this user only, and should be executed automatically (eg. using cron) at regular intervals, such as every minute. The user who owns this script also needs to have write permission to the directory in which it sits, and in its subdirectories.
2. **fiberQA_sequences.sh** - this script also needs to be customized to work with the local CODA environment. Normally it should be installed in the same directory as fiberQA_cron.sh and be owned by the same user. This script does all of the choreography for starting and stopping runs with CODA, scanning through the Vbias sequence, and then analyzing the data and generating the plots after the data have been acquired.
3. **treemaker** - called by fiberQA_sequences.sh to read the CODA event data in evio format (expected to be stored in the data directory) and write out the data in a root tree (also stored in the data directory).
4. **plotmaker.py** - reads the root tree created by treemaker, and generates plots of pulse height for display by index.cgi

## History

This library was developed for use with the dark box fiber testing setup at UConn.  It was packaged into a repository because it may also be useful for running bias calibrations at Jefferson Lab.

## Release history

Initial release on November 21, 2015.

## Usage synopsis

Direct the web browser to http://your-apache-server/your-darkbox-folder/index.cgi?newrun. The query string "?newrun" triggers a fresh execution of fiberQA_sequencer.sh the next time fiberQA_cron.sh runs. As soon as the start_new_run request is received, accessing the above url results in a message indicating that a new run is pending, and any further such requests are blocked. Once fiberQA_cron.sh sees the request and starts fiberQA_sequencer.sh, the message returned to the web browser changes to indicate that a new run is in progress. Once the run finishes and the data analysis is completing, the page changes to a display of the pulse height histograms acquired during the latest run. To see the results from a previous run, replace the ?newrun query string with ?run=NNN where NNN is the number of a past run. If this run exists in the record of prior runs, the results from that run are displayed.

## Dependencies

This package has been tested on a Centos 6 apache server, with a VME system and a ROC running CODA 2.6 version.

## Building instructions

Simply cd to the top-level project directory and type "make".

## Documentation

Just this README.

## Troubleshooting

You are on your own here, but a good place to start in case of problems would be try running the fiberQA_sequencer.sh script from the command line. It writes enough information to stdout that you should be abl to follow its progress.

## Bugs

Please report to the author richard.t.jones at uconn.edu in case of problems.

## Contact the authors

Contact the author richard.t.jones at uconn.edu for more information.
