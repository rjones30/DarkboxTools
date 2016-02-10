#!/bin/bash
#
# fiberQA_sequencer.sh - a bash script to start up a new data acquisition
#                        run using the CODA run gui, execute a sequence of
#                        Vbias settings on the SiPM preamplifiers, end the
#                        run, and launch analysis of the data collected.
#
# usage: bash> fiberQA_sequencer.sh <X11_display>
#    where <X11_display> is the value of the DISPLAY environment variable
#    that you would use to send X11 commands to the desired screen.
#
# example: bash> fiberQA_sequencer.sh :23
#
# author: richard.t.jones at uconn.edu
# version: april 23, 2014
#
# Notes:
#
# 1. Besides a running X11 server, two other tools must be installed
#    in order for the script to run.  Both are available as standard
#    linux packages and can be installed using the local package manager.
#    Each of these are assumed to exist within the user's shell PATH.
#	a. xdotool - general tool for simulating mouse and keyboard
#                    control events in a X11 environment.
#	b. xclip - general tool for reading from and writing into the
#                  paste buffer in a X11 environment.
#
# 2. The fiberQA_sequencer script works by automatically doing mouse clicks
#    that would be required to start up a CODA data acquisition run using
#    the standard rcGui.  As such, it assumes a certain geometry of the
#    rcGui window, as well as the way xterm windows pop up on the user's
#    desktop.  To accommodate random changes in either of these, the
#    script supports a "calibration" mode.  To calibrate, try
#	bash> fiberQA_sequencer.sh --calibrate <X11_display>
#    The screen calibration below was carried out on a X11 display
#    of dimensions 1900x1080.

# these settings may be customized
step1X=501
step1Y=173
step2X=502
step2Y=193
step3X=514
step3Y=205
step4X=571
step4Y=207
step5X=635
step5Y=208
step6X=693
step6Y=205
stopX=757
stopY=204
killX=1510
killY=152

# these are system preferences
master_winX=100
master_winY=100
master_winWidth=400
master_winHeight=300
master_winMidX=`expr $master_winWidth / 2 + $master_winX`
master_winMidY=`expr $master_winHeight / 2 + $master_winY`
coda_host=halldtrg5.phys.uconn.edu
coda_user=halld
coda_ssh_key=~/.ssh/coda_daq_key
TAGMutilities=/home/halld/online/TAGMutilities

function activate_daq() {
    master_win=
    for winid in `xdotool search --title "Master DAQ Window"`; do
        master_win=$winid
    done
    if [[ -z $master_win ]]; then
        xterm -title "Master DAQ Window" &
        sleep 2 # wait for window to appear, adjust as needed
        master_win=`xdotool getwindowfocus`
        if [[ -z $master_win ]]; then
            echo "Unable to get window focus on master xterm, cannot continue!"
            exit 1
        fi
        xdotool windowmove $master_win $master_winX $master_winY
        xdotool windowsize $master_win $master_winWidth $master_winHeight
        xdotool mousemove $master_winMidX $master_winMidY
        xdotool click 1
        xdotool type "ssh -X -i ~/.ssh/coda_daq_key halld@halldtrg5.phys.uconn.edu
"
        xdotool type "scripts/start_daq.sh
"
        sleep 60 # wait for daq to load
        rcgui_win=`xdotool getactivewindow`
        if [[ "$rcgui_win" = "" ]]; then
            echo "Error - unable to open CODA rcgui session" >&2
            exit 2
        fi
    fi
    resp=`xdotool windowactivate $rcgui_win 2>&1`
    [[ $resp = "" ]]
    echo $rcgui_win
}

function calibrate() {
    echo
    echo "Calibration procedure for fiberQA_sequencer.sh is starting."
    echo "If running this script in a terminal within your X11 display,"
    echo "please move it to the right so that it remains visible when"
    echo "the other windows pop up.  DO NOT move any of the automatic"
    echo "windows using the mouse because they all need to pop up in"
    echo "exactly the same place on the screen each time."
    echo
    echo -n "Press <enter> when ready:"
    read resp
    activate_daq
    echo
    echo "A new CODA rcgui window should have appeared on the screen."
    echo "Go to the left-most pulldown menu "Platform" and hover the"
    echo "mouse over where you would click to reveal the menu."
    echo
    echo -n "Press return to continue:"
    read resp
    loc=`xdotool getmouselocation`
    step1X=`echo $loc | awk -F'[ :]' '{print $2}'`
    step1Y=`echo $loc | awk -F'[ :]' '{print $4}'`
    xdotool mousemove $step1X $step1Y
    xdotool click 1
    echo
    echo "The Platform menu should now be displayed on the screen."
    echo "Hover the mouse over the "connect" menu item."
    echo
    echo -n "Press return to continue:"
    read resp
    loc=`xdotool getmouselocation`
    step2X=`echo $loc | awk -F'[ :]' '{print $2}'`
    step2Y=`echo $loc | awk -F'[ :]' '{print $4}'`
    xdotool mousemove $step2X $step2Y
    xdotool click 1
    echo
    echo "The configure button should be illuminated shortly."
    echo "As soon as it appears, hover the mouse over the middle of"
    echo "the button, but do not click it."
    echo
    echo -n "Press <enter> when ready:"
    read resp
    loc=`xdotool getmouselocation`
    step3X=`echo $loc | awk -F'[ :]' '{print $2}'`
    step3Y=`echo $loc | awk -F'[ :]' '{print $4}'`
    xdotool mousemove $step3X $step3Y
    xdotool click 1
    echo
    echo "The download button should be illuminated shortly."
    echo "As soon as it appears, hover the mouse over the middle of"
    echo "the button, but do not click it."
    echo
    echo -n "Press <enter> when ready:"
    read resp
    loc=`xdotool getmouselocation`
    step4X=`echo $loc | awk -F'[ :]' '{print $2}'`
    step4Y=`echo $loc | awk -F'[ :]' '{print $4}'`
    xdotool mousemove $step4X $step4Y
    xdotool click 1
    echo
    echo "The prestart button should be illuminated shortly."
    echo "As soon as it appears, hover the mouse over the middle of"
    echo "the button, but do not click it."
    echo
    echo -n "Press <enter> when ready:"
    read resp
    loc=`xdotool getmouselocation`
    step5X=`echo $loc | awk -F'[ :]' '{print $2}'`
    step5Y=`echo $loc | awk -F'[ :]' '{print $4}'`
    xdotool mousemove $step5X $step5Y
    xdotool click 1
    echo
    echo "The start button should be illuminated shortly."
    echo "As soon as it appears, hover the mouse over the middle of"
    echo "the button, but do not click it."
    echo
    echo -n "Press <enter> when ready:"
    read resp
    loc=`xdotool getmouselocation`
    step6X=`echo $loc | awk -F'[ :]' '{print $2}'`
    step6Y=`echo $loc | awk -F'[ :]' '{print $4}'`
    xdotool mousemove $step6X $step6Y
    xdotool click 1
    echo
    echo "Now a new run should begin in the DAQ.  Wait until"
    echo "events start accummulating in the counts window, then"
    echo "hover the mouse over the stop button."
    echo
    echo -n "Press <enter> when ready:"
    read resp
    loc=`xdotool getmouselocation`
    stopX=`echo $loc | awk -F'[ :]' '{print $2}'`
    stopY=`echo $loc | awk -F'[ :]' '{print $4}'`
    xdotool mousemove $stopX $stopY
    xdotool click 1
    echo
    echo "As soon as the run has ended and the controllers have"
    echo "all returned to the downloaded state, hover the mouse"
    echo "over the X in the upper right corner of the rcgui window"
    echo "but do not click on it."
    echo
    echo -n "Press <enter> when ready:"
    read resp
    loc=`xdotool getmouselocation`
    killX=`echo $loc | awk -F'[ :]' '{print $2}'`
    killY=`echo $loc | awk -F'[ :]' '{print $4}'`
    xdotool mousemove $killX $killY
    xdotool click 1
    sleep 2
    for n in 1 2 3 4 5 6 7; do
        xdotool key ctrl+c
        sleep 1
    done
    xdotool key ctrl+d
    sleep 1
    xdotool key ctrl+d
    echo
    echo "The rcgui window should have gone away, and all of the miniature"
    echo "xterms too.  If so, everything is correct, and you should copy/paste"
    echo "the settings below into the header of the fiberQA_sequencer.sh script,"
    echo "replacing the defaults."
    echo 
    echo step1X=$step1X
    echo step1Y=$step1Y
    echo step2X=$step2X
    echo step2Y=$step2Y
    echo step3X=$step3X
    echo step3Y=$step3Y
    echo step4X=$step4X
    echo step4Y=$step4Y
    echo step5X=$step5X
    echo step5Y=$step5Y
    echo step6X=$step6X
    echo step6Y=$step6Y
    echo stopX=$stopX
    echo stopY=$stopY
    echo killX=$killX
    echo killY=$killY
}

# make sure all necessary tools are available
for tool in xdotool xclip; do
    if [[ ! -x `which $tool` ]]; then
        echo "Required tool $tool not found in the user PATH" >&2
        exit 1
    fi
done

# parse command arguments
if [[ "$1" = "--calibrate" ]]; then
    shift
    export DISPLAY=$1
    calibrate
    exit 0
elif [[ $# != 1 ]]; then
    echo "Usage: fiberQA_sequencer.sh [--calibrate] <X11_display>" >&2
    exit 1
else
    export DISPLAY=$1
fi

# look for an existing master window open to the DAQ frontend,
# if none exists then start a new one
activate_daq
if [[ $? != 0 ]]; then
    echo -n "CODA station session already connected" 
    echo " on display $1"
    echo "Cancel the existing one before trying to create a new one!"
    exit 1
fi

# now step through the clicks to start a run
echo raise platform menu
xdotool mousemove $step1X $step1Y
xdotool click 1
echo select connect
xdotool mousemove $step2X $step2Y
xdotool click 1
sleep 5
echo click configure
xdotool mousemove $step3X $step3Y
xdotool click 1
sleep 20
echo click download
xdotool mousemove $step4X $step4Y
xdotool click 1
sleep 20
echo click prestart
xdotool mousemove $step5X $step5Y
xdotool click 1
sleep 20
echo click start
xdotool mousemove $step6X $step6Y
xdotool click 1
sleep 20

# now carry out the Vbias sequence
$TAGMutilities/do_sequence.sh -L -d 20

# measurement complete, shut it down
echo click stop
xdotool mousemove $stopX $stopY
xdotool click 1
sleep 30
echo kill rcgui window
xdotool mousemove $killX $killY
xdotool click 1
sleep 2
echo kill the rest of the windows
for n in 1 2 3 4 5 6 7; do
    xdotool key ctrl+c
    sleep 1
done
xdotool key ctrl+d
sleep 1
xdotool key ctrl+d

exit 0
