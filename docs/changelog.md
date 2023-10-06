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

"version": "0.2.8"
- cleaning up as a potential working version for initial release

22/09/2023
"version": "0.4.2"
- Hardcoded template prior to be 12 Months followed by:
- Many iterations trying to solve
> UnboundLocalError: local variable 'studyBrainReference' referenced before assignment

in Flywheel job log, while working ok when run locally. 

"version": "0.4.2"
- Added ICBM-81 Atlas
- Unbuffered output

"version": "0.4.8"
Rolled back version due to github error ("version": "0.4.7 to 0.4.5)
- Not sure all changes were caught 
- Main update was to catch missing sex in dicom header

28/09/2023

- Image and mask dimensions error is being thrown for some data as the reconstruction has been changed so that it is 1.5mm isotropic. 
- Masks need to be registered to this image not the 0.8mm template. 
- Lots of changes had been made trying to debug which need to be cleaned up. 

Improved masks have been added for cortical and subcortical ROIs

03/10/2023
"version": "0.4.9"

- Mask error may have been due to HD-BET ruining some brains
- Have implemented simple BET
- Function included but not run to resample templates here to 1.5mm
- Current implementation will take the reconstructed brain extracted input, register it to BCP template, it will also take MNI atlas masks and register to same template. These should all be in the same space to run estimates. 

05/10/2023
"version": "0.5.2"

- ROIs have been transformed from MNI to BCP space offline to save computational power
- Back projection from BCP to subject space will be performed for volume estimates
- intermediary outputs are saved for debugging

06/10/2023
 "version": "0.5.4"

 -  "version": "0.5.3" ran succesfully will all outpu
 -  Have moved output masks into work dir so will not be saved out
 -  Introduced a mean intensity output for sanity check of volume calculation
 -  Volume calculation updated to include scaling factor of image dimensions (1.5mm^3 = 3.375)