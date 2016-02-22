#!/bin/bash
#
# fiberQA_cron.sh - cron shell script that checks for new run requests
#                   in the fiberQA home directory, and if found, runs
#                   the fiberQA_sequencer script to collect a round of
#                   fiber measurements, then launches the analyzer to
#                   analyze the data into root histograms and invokes
#                   root to plot them.
#
# author: richard.t.jones at uconn.edu
# version: april 26, 2014

# connect to the ssh-agent for this user
hostname=`hostname`
if [[ -r ~/.ssh-agent-$hostname ]]; then
    source ~/.ssh-agent-$hostname >/dev/null
fi

base=`dirname $0`
if [[ -d $base/newrun-requested ]]; then
    mkdir $base/newrun-underway >/dev/null 2>&1
    if [[ $? != 0 ]]; then
        exit 0
    fi
    oldfile=`ls -t $base/data/*.evt.0 | head -n1`

#   here is where the data collection starts
    exec >> $base/fiberQA_cron.log 2>&1
    if [[ -r $base/newrun-requested/requestor ]]; then
        requestor=`cat $base/newrun-requested/requestor`
    else
        requestor=Anonymous
    fi
    echo
    echo "New run starting" `date`
    echo "This run was requested by $requestor"
    cd $base
    ./fiberQA_sequencer.sh :23

#   check that data file exists and has expected size
    evtfile=`ls -t $base/data/*.evt.0 | head -n1`
    if [[ "$evtfile" == "$oldfile" ]]; then
        echo "No event file for the new run was found, aborting script!"
        rmdir $base/newrun-underway
        exit 1
    elif [[ `ls -l $evtfile | awk '{print $5}'` < 1000000000 ]]; then
        echo "Event file for the new run was found, but looks too short, aborting script!"
        rmdir $base/newrun-underway
        exit 1
    fi

#    analyze the event data file
    source /home/halld/setup.sh
    ./treemaker $evtfile || exit 1
    run=`echo $evtfile | sed 's/^.*simple_\([0-9]*\).evt.0/\\1/'`
    mkdir histos/run_$run || exit 1
    export DISPLAY=:23
    ./plotmaker.py $run
    echo Successful collection and analysis of run $run
    rm -rf newrun-requested newrun-underway
fi
