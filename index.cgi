#!/bin/bash
#
# index.cgi - browser interface script to the fiberQA-sequencer
#
# author: richard.t.jones at uconn.edu
# version: april 26, 2014

histos=histos
run=`ls -t $histos | head -n1 | awk -F_ '{print $2}'`

if echo $QUERY_STRING | grep -q 'run=' ; then
    run=`echo $QUERY_STRING | awk -F= '{print $2}'`
elif [[ "$QUERY_STRING" != "" ]]; then
    echo "Content-type: text/html"
    echo
    echo "<html>"
    echo "<head>"
    echo "<title>FiberQA Data Collector and Analyzer</title>"
    echo "</head>"
    echo "<body>"
    echo "<h1 align=\"center\">FiberQA Data Collector and Analyzer</h1>"
    echo "<p align=\"center\"><font size=\"+3\">"
    if [[ "$QUERY_STRING" == "newrun" ]]; then
        if [[ -d newrun-underway ]]; then
            when=`ls -ld newrun-underway | awk '{print $6,$7",",$8}'`
            echo "A run is already underway, started $when."
        elif [[ -d newrun-requested ]]; then
            when=`ls -ld newrun-requested | awk '{print $6,$7",",$8}'`
            echo "A run has already been requested, queued $when."
            echo "<br/>Click"
            echo "<a href=\"$SCRIPT_NAME?cancel\">here</a> to cancel request"
        else
            mkdir newrun-requested
            echo "New run request submitted, click"
            echo "<a href=\"$SCRIPT_NAME?status\">here</a> for status."
        fi
    elif [[ "$QUERY_STRING" == "cancel" ]]; then
        if [[ -d newrun-underway ]]; then
            when=`ls -ld newrun-underway | awk '{print $6,$7",",$8}'`
            echo "A run is already underway, started $when,"
            echo "<br/>It is too late to cancel, let it finish."
        elif [[ -d newrun-requested ]]; then
            rmdir newrun-requested
            echo "Run request has been cancelled."
        else
            echo "No run request queued, nothing to cancel."
        fi
    elif [[ "$QUERY_STRING" == "status" ]]; then
        if [[ -d newrun-underway ]]; then
            when=`ls -ld newrun-underway | awk '{print $6,$7",",$8}'`
            echo "A run is underway, started $when."
        elif [[ -d newrun-requested ]]; then
            when=`ls -ld newrun-requested | awk '{print $6,$7",",$8}'`
            echo "A run has been requested, queued $when."
            echo "<br/>Click"
            echo "<a href=\"$SCRIPT_NAME?cancel\">here</a> to cancel request"
        else
            echo "Last requested run $run is complete, click"
            echo "<a href=\"$SCRIPT_NAME\">here</a> to see results."
        fi
    fi
    echo "</font></p>"
    echo "</body>"
    echo "</html>"
    exit
fi

./runcond.py $run >/tmp/oput
date=`awk '/^run [0-9]* started/{print $4,$5,$6,$7,$8}' /tmp/oput`

Tchip_level=`awk '/Tchip *= */{print $3}' /tmp/oput`
Tchip_error=`awk '/Tchip *= */{print $5}' /tmp/oput`
Tchip_unit=`awk '/Tchip *= */{print $6}' /tmp/oput`
Tchip_color=`awk '/Tchip *= */{if ($3 > 15 && $3 < 40 && $5 < 1) {print "black"} else {print "red"}}' /tmp/oput`
Tchip_text="<font color=\"$Tchip_color\">$Tchip_level &plusmn; $Tchip_error $Tchip_unit</font>"

pos5V_level=`awk '/+5V level *= */{print $4}' /tmp/oput`
pos5V_error=`awk '/+5V level *= */{print $6}' /tmp/oput`
pos5V_unit=`awk '/+5V level *= */{print $7}' /tmp/oput`
pos5V_color=`awk '/+5V level *= */{if ($4 > 4.90 && $4 < 5.10 && $6 < 0.05) {print "black"} else {print "red"}}' /tmp/oput`
pos5V_text="<font color=\"$pos5V_color\">$pos5V_level &plusmn; $pos5V_error $pos5V_unit</font>"

neg5V_level=`awk '/-5V level *= */{print $4}' /tmp/oput`
neg5V_error=`awk '/-5V level *= */{print $6}' /tmp/oput`
neg5V_unit=`awk '/-5V level *= */{print $7}' /tmp/oput`
neg5V_color=`awk '/-5V level *= */{if ($4 > -5.10 && $4 < -4.90 && $6 < 0.05) {print "black"} else {print "red"}}' /tmp/oput`
neg5V_text="<font color=\"$neg5V_color\">$neg5V_level &plusmn; $neg5V_error $neg5V_unit</font>"

FPGApower_level=`awk '/FPGA power *= */{print $4}' /tmp/oput`
FPGApower_error=`awk '/FPGA power *= */{print $6}' /tmp/oput`
FPGApower_unit=`awk '/FPGA power *= */{print $7}' /tmp/oput`
FPGApower_color=`awk '/FPGA power *= */{if ($4 > 1.15 && $4 < 1.25 && $6 < 0.01) {print "black"} else {print "red"}}' /tmp/oput`
FPGApower_text="<font color=\"$FPGApower_color\">$FPGApower_level &plusmn; $FPGApower_error $FPGApower_unit</font>"

pos3_3V_level=`awk '/+3.3V level *= */{print $4}' /tmp/oput`
pos3_3V_error=`awk '/+3.3V level *= */{print $6}' /tmp/oput`
pos3_3V_unit=`awk '/+3.3V level *= */{print $7}' /tmp/oput`
pos3_3V_color=`awk '/+3.3V level *= */{if ($4 > 3.2 && $4 < 3.4 && $6 < 0.01) {print "black"} else {print "red"}}' /tmp/oput`
pos3_3V_text="<font color=\"$pos3_3V_color\">$pos3_3V_level &plusmn; $pos3_3V_error $pos3_3V_unit</font>"

gainmode_level=`awk '/gainmode *= */{print $3}' /tmp/oput`
gainmode_error=`awk '/gainmode *= */{print $5}' /tmp/oput`
gainmode_unit=`awk '/gainmode *= */{print $6}' /tmp/oput`
gainmode_color=`awk '/gainmode *= */{if ($3 > 4.90 && $3 < 5.10 && $5 < 0.01) {print "black"}
                                    else if ($3 > 9.90 && $3 < 10.10 && $5 < 0.01) {print "green"}
                                    else {print "black"}}' /tmp/oput`
gainmode_text="<font color=\"$gainmode_color\">$gainmode_level &plusmn; $gainmode_error $gainmode_unit</font>"

Vsumref1_level=`awk '/Vsumref1 level *= */{print $4}' /tmp/oput`
Vsumref1_error=`awk '/Vsumref1 level *= */{print $6}' /tmp/oput`
Vsumref1_unit=`awk '/Vsumref1 level *= */{print $7}' /tmp/oput`
Vsumref1_color=`awk '/Vsumref1 level *= */{if ($4 > 4.0 && $4 < 4.2 && $6 < 0.02) {print "black"} else {print "red"}}' /tmp/oput`
Vsumref1_text="<font color=\"$Vsumref1_color\">$Vsumref1_level &plusmn; $Vsumref1_error $Vsumref1_unit</font>"

Vsumref2_level=`awk '/Vsumref2 level *= */{print $4}' /tmp/oput`
Vsumref2_error=`awk '/Vsumref2 level *= */{print $6}' /tmp/oput`
Vsumref2_unit=`awk '/Vsumref2 level *= */{print $7}' /tmp/oput`
Vsumref2_color=`awk '/Vsumref2 level *= */{if ($4 > 4.0 && $4 < 4.2 && $6 < 0.02) {print "black"} else {print "red"}}' /tmp/oput`
Vsumref2_text="<font color=\"$Vsumref2_color\">$Vsumref2_level &plusmn; $Vsumref2_error $Vsumref2_unit</font>"

VDAChealth_level=`awk '/VDAChealth level *= */{print $4}' /tmp/oput`
VDAChealth_error=`awk '/VDAChealth level *= */{print $6}' /tmp/oput`
VDAChealth_unit=`awk '/VDAChealth level *= */{print $7}' /tmp/oput`
VDAChealth_color=`awk '/VDAChealth level *= */{if ($4 > 12.9 && $4 < 13.1 && $6 < 0.05) {print "black"} else {print "red"}}' /tmp/oput`
VDAChealth_text="<font color=\"$VDAChealth_color\">$VDAChealth_level &plusmn; $VDAChealth_error $VDAChealth_unit</font>"

TDAC_level=`awk '/TDAC level *= */{print $4}' /tmp/oput`
TDAC_error=`awk '/TDAC level *= */{print $6}' /tmp/oput`
TDAC_unit=`awk '/TDAC level *= */{print $7}' /tmp/oput`
TDAC_color=`awk '/TDAC level *= */{if ($4 > 10 && $4 < 40 && $6 < 1) {print "black"} else {print "red"}}' /tmp/oput`
TDAC_text="<font color=\"$TDAC_color\">$TDAC_level &plusmn; $TDAC_error $TDAC_unit</font>"

Tpreamp1_level=`awk '/Tpreamp1 level *= */{print $4}' /tmp/oput`
Tpreamp1_error=`awk '/Tpreamp1 level *= */{print $6}' /tmp/oput`
Tpreamp1_unit=`awk '/Tpreamp1 level *= */{print $7}' /tmp/oput`
Tpreamp1_color=`awk '/Tpreamp1 level *= */{if ($4 > 10 && $4 < 40 && $6 < 1) {print "black"} else {print "red"}}' /tmp/oput`
Tpreamp1_text="<font color=\"$Tpreamp1_color\">$Tpreamp1_level &plusmn; $Tpreamp1_error $Tpreamp1_unit</font>"

Tpreamp2_level=`awk '/Tpreamp2 level *= */{print $4}' /tmp/oput`
Tpreamp2_error=`awk '/Tpreamp2 level *= */{print $6}' /tmp/oput`
Tpreamp2_unit=`awk '/Tpreamp2 level *= */{print $7}' /tmp/oput`
Tpreamp2_color=`awk '/Tpreamp2 level *= */{if ($4 > 10 && $4 < 40 && $6 < 1) {print "black"} else {print "red"}}' /tmp/oput`
Tpreamp2_text="<font color=\"$Tpreamp2_color\">$Tpreamp2_level &plusmn; $Tpreamp2_error $Tpreamp2_unit</font>"

normfact_level=`awk '/normalization level *= */{print $4}' /tmp/oput`
normfact_error=`awk '/normalization level *= */{print $6}' /tmp/oput`
normfact_unit=`awk '/normalization level *= */{print $7}' /tmp/oput`
normfact_color=`awk '/normalization level *= */{if ($4 > 2000 && $4 < 2500 && $6 < 100) {print "black"} else {print "red"}}' /tmp/oput`
normfact_text="<font color=\"$normfact_color\">$normfact_level &plusmn; $normfact_error $normfact_unit</font>"

#rm /tmp/oput

cat <<EOI
Content-type: text/html

<html>
<head>
<title>FiberQA Data Analysis Results for Run $run</title>
</head>
<body>
<h1 align="center">FiberQA Data Analysis Results for Run $run</h1>
<p align="center"><font size="+1">$date</font></p>

<table align="center">
<tr><td align="right">FPGA power</td><td align="right" width="140">$FPGApower_text</td>
    <td width="200" align="right">gainmode</td><td align="right" width="140">$gainmode_text</td>
    <td width="200" align="right">T chip</td><td align="right" width="140">$Tchip_text</td>
</tr>
<tr><td align="right">+5V power</td><td align="right">$pos5V_text</td>
    <td align="right">Vsumref[1]</td><td align="right">$Vsumref1_text</td>
    <td align="right">T preamp[1]</td><td align="right"> $Tpreamp1_text</td>
</tr>
<tr><td align="right">-5V power</td><td align="right">$neg5V_text</td>
    <td align="right">Vsumref[2]</td><td align="right"> $Vsumref2_text</td>
    <td align="right">T preamp[2]</td><td align="right"> $Tpreamp2_text</td>
</tr>
<tr><td align="right">+3.3V power</td><td align="right"> $pos3_3V_text</td>
    <td align="right">VDAChealth</td><td align="right">$VDAChealth_text</td>
    <td align="right">T DAC</td><td align="right">$TDAC_text</td>
</tr>
</table>
<p align="center">relative pulse normalization $normfact_text</p>

<hr/>
<p align="center"><font size="+2">
Front half-bundle, viewing the scintillating fiber with dark box open
</font></p>
<table align="center">
<tr>
 <td><img src="$histos/run_$run/fiber_15.png"/></td>
 <td><img src="$histos/run_$run/fiber_10.png"/></td>
 <td><img src="$histos/run_$run/fiber_5.png"/></td>
</tr><tr>
 <td><img src="$histos/run_$run/fiber_14.png"/></td>
 <td><img src="$histos/run_$run/fiber_9.png"/></td>
 <td><img src="$histos/run_$run/fiber_4.png"/></td>
</tr><tr>
 <td><img src="$histos/run_$run/fiber_13.png"/></td>
 <td><img src="$histos/run_$run/fiber_8.png"/></td>
 <td><img src="$histos/run_$run/fiber_3.png"/></td>
</tr><tr>
 <td><img src="$histos/run_$run/fiber_12.png"/></td>
 <td><img src="$histos/run_$run/fiber_7.png"/></td>
 <td><img src="$histos/run_$run/fiber_2.png"/></td>
</tr><tr>
 <td><img src="$histos/run_$run/fiber_11.png"/></td>
 <td><img src="$histos/run_$run/fiber_6.png"/></td>
 <td><img src="$histos/run_$run/fiber_1.png"/></td>
</tr><tr>
</table>

<hr/>
<p align="center"><font size="+2">
Back half-bundle, viewing the scintillating fiber with dark box open
</font></p>
<table align="center">
<tr>
 <td><img src="$histos/run_$run/fiber_30.png"/></td>
 <td><img src="$histos/run_$run/fiber_25.png"/></td>
 <td><img src="$histos/run_$run/fiber_20.png"/></td>
</tr><tr>
 <td><img src="$histos/run_$run/fiber_29.png"/></td>
 <td><img src="$histos/run_$run/fiber_24.png"/></td>
 <td><img src="$histos/run_$run/fiber_19.png"/></td>
</tr><tr>
 <td><img src="$histos/run_$run/fiber_28.png"/></td>
 <td><img src="$histos/run_$run/fiber_23.png"/></td>
 <td><img src="$histos/run_$run/fiber_18.png"/></td>
</tr><tr>
 <td><img src="$histos/run_$run/fiber_27.png"/></td>
 <td><img src="$histos/run_$run/fiber_22.png"/></td>
 <td><img src="$histos/run_$run/fiber_17.png"/></td>
</tr><tr>
 <td><img src="$histos/run_$run/fiber_26.png"/></td>
 <td><img src="$histos/run_$run/fiber_21.png"/></td>
 <td><img src="$histos/run_$run/fiber_16.png"/></td>
</tr><tr>
</table>
</body>
</html>
EOI
