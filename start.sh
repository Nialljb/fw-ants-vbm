#!/bin/env bash 
. $FSLDIR/etc/fslconf/fsl.sh
echo "FSLOUTPUTTYPE set to $FSLOUTPUTTYPE"
python3 -u /flywheel/v0/run.py


