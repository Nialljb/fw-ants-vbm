# Changelog

18/08/2023
"version": "0.0.1"

Initial build
- SDK metadata.py script made to find mathcing template
  
To do:
- include template segmentations
- pull HD-BET mask

24/08/2023
"version": "0.0.6"
- pulls HD-BET mask
- matches to BCP template
- draft of main.py to test

"version": "0.0.7"
- added test_fsl as output not configured correctly 

"version": "0.1.0"
- changed entrypoint to config fsl before running

25/08/2023
"version": "0.1.2"

- found rouge space in jocobian calculation which was causing failure
- created pabndas dataframe for output that includes mask volume, mean intensities and estimated volume

* There is a log error at the end which is unclear...

08/09/2023
Trying to include ROIs estimations (Should be moved to seperate module - to allow flexibility in selecing atlas)
* ANTs not installed on personal computer so need to follow up with debugging 

11/09/2023
"version": "0.1.5"
**beta** uploaded to test the following
- inlcuded shell script to change dimensions of masks in an atlas folder to match the individual
- volume estimation using the registered masks in main VMB script
- subprocess.run may be better than os.system and try/catch statements should run as expected 

14/09/2023
"version": "0.2.6"

MUCH trial and error debugging..
- Should be a working beta version (will save ALL outputs - will remove all ROI masks after sanity checking)
- Cortical masks included
- Subcortical are thresholded (0.7), Thalamus & Caudated still too liberal, may need to threshold seperatly. 

"version": "0.2.7"
- More ways of catching age
