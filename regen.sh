#!/bin/bash

evtfile="data/simple_$1.evt.0"
if [[ -r $evtfile ]]; then
    source /home/halld/setup.sh
    ./treemaker $evtfile || exit 1
    run=`echo $evtfile | sed 's/^.*simple_\([0-9]*\).evt.0/\\1/'`
    mkdir histos/run_$run || exit 1
    chgrp prod histos/run_$run || exit 1
    chmod g+w histos/run_$run || exit 1
    export DISPLAY=:23
    echo Successful collection of run $run
    ./plotmaker.py $run
    echo Successful collection and analysis of run $run
    rm -rf newrun-requested newrun-underway
else
	echo "bad file $evtfile"
fi

