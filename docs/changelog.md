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