import os, sys
from pathlib import Path
import subprocess
import pandas as pd  


#  -------------------  Import the necessary packages & variables -------------------  #
# Set up the paths
target_template="12Month"

FLYWHEEL_BASE = "/Users/nbourke/GD/atom/unity/fw-gears/fw-ants-vbm"
individualMaskedBrain = (FLYWHEEL_BASE + "/app/templates/MNI/MNI152_T1_1mm_brain.nii.gz")
OUTPUT_DIR = (FLYWHEEL_BASE + "/app/templates/MNI")
WORK = (FLYWHEEL_BASE + "/work")
TEMPLATE = (FLYWHEEL_BASE + "/app/templates/" + target_template + "/")

# set template priors
templatePath = Path(TEMPLATE) # To rglob
print("templatePath is: ", templatePath)
for filepath in templatePath.rglob('BCP-??M-T2.nii.gz'):
    studyBrainReference = str(filepath)
    print("studyBrainReference is: ", studyBrainReference)
    break
for filepath in templatePath.rglob('BCP-??M-GM.nii.gz'):
    grayPrior = str(filepath)
    print("grayPrior is: ", grayPrior)
    break
for filepath in templatePath.rglob('BCP-??M-WM.nii.gz'):
    whitePrior = str(filepath)
    print("whitePrior is: ", whitePrior)
    break
for filepath in templatePath.rglob('BCP-??M-CSF.nii.gz'):
    csfPrior = str(filepath)
    print("csfPrior is: ", csfPrior)
    break
print("ref is: ", studyBrainReference)


# ---  Set up the software ---  #

softwareHome = "/opt/ants/bin/"
antsWarp = softwareHome + "ANTS 3 -G -m CC["
antsImageAlign = softwareHome + "WarpImageMultiTransform 3 "
antsMath = softwareHome + "ImageMath 3 "

studyAlignedBrainImage = (OUTPUT_DIR + "/initialBrainMaskedImage_aligned.nii.gz")
# try:
#     result = subprocess.run([antsWarp + studyBrainReference + ", " + individualMaskedBrain + ", 1, 6] -o " + studyAlignedBrainImage + " -i 60x90x45 -r Gauss[3,1] -t SyN[0.25] --use-Histogram-Matching --MI-option 32x16000 --number-of-affine-iterations 10000x10000x10000x10000x10000"], shell=True, check=True) # , text=True , capture_output=True
# except:
#     print("*Error in calculating warp*")
#     print(result.stderr)
#     sys.exit(1)

# Define variables from warp calculation in step 1
brainWarpField = (OUTPUT_DIR + "/initialBrainMaskedImage_alignedWarp.nii.gz")
brainAffineField = (OUTPUT_DIR + "/initialBrainMaskedImage_alignedAffine.txt")
brainInverseWarpField = (OUTPUT_DIR + "/initialBrainMaskedImage_alignedInverseWarp.nii.gz")

# --- 2: Perform the warp on the individual brain image to align it to the template ---  #

print("Aligning individual brain to template...")
alignedBrainImage = (OUTPUT_DIR + "/isotropicReconstruction_to_brainReferenceAligned.nii.gz")
# try:
#     os.system(antsImageAlign + " " + individualMaskedBrain + " " + alignedBrainImage + " -R " + studyBrainReference + " " + brainWarpField + " " + brainAffineField + " --use-BSpline")	
# except:
#     print("Error in aligning individual brain to template")
#     sys.exit(1)

# # --- 3: now align the individual white matter, gray matter, and csf priors to the individual brain using reverse warp ---  #

# #  Take the template priors and align them to the individual space
# # Output variables
# print("Aligning tissue segmentations to template...")
individualWhiteSegmentation = (OUTPUT_DIR + "/initialWM.nii.gz")
individualGraySegmentation = (OUTPUT_DIR + "/initialGM.nii.gz")
individualCSFSegmentation = (OUTPUT_DIR + "/initialCSF.nii.gz")
# studyBrainMask = (OUTPUT_DIR + "/alignedBrainMask.nii.gz")

# try:
#     os.system(antsImageAlign + " " + whitePrior + " " + individualWhiteSegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
#     os.system(antsImageAlign + " " + grayPrior + " " + individualGraySegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
#     os.system(antsImageAlign + " " + csfPrior + " " + individualCSFSegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
# except:
#     print("Error in aligning tissue segmentations to template")
#     sys.exit(1)


# --- 4: Use output from bet to mask the tissue segmentations    ---  #  

print("Masking tissue segmentations...")
maskedWMSegmentation = (OUTPUT_DIR + "/maskedWM.nii.gz")
maskedGMSegmentation = (OUTPUT_DIR + "/maskedGM.nii.gz")
maskedCSFSegmentation = (OUTPUT_DIR + "/maskedCSF.nii.gz")

# try:
#     os.system("fslmaths " + individualWhiteSegmentation + " -mas " + studyBrainMask + " " + maskedWMSegmentation)
#     os.system("fslmaths " + individualGraySegmentation + " -mas " + studyBrainMask + " " + maskedGMSegmentation)
#     os.system("fslmaths " + individualCSFSegmentation + " -mas " + studyBrainMask + " " + maskedCSFSegmentation)
# except:
#     print("Error in masking tissue segmentations")
#     sys.exit(1)

# --- 5: Threshold the tissue segmentations to create eroded binary masks ---  #

GM_mask = (OUTPUT_DIR + "/MNI-GM.nii.gz")
WM_mask = (OUTPUT_DIR + "/MNI-WM.nii.gz")
CSF_mask = (OUTPUT_DIR + "/MNI-CSF.nii.gz")
os.system("fslmaths " + individualGraySegmentation + " -thr 0.3 -bin " + GM_mask)
subprocess.run(["fslmaths " + individualWhiteSegmentation + " -thr 0.3 -bin " + WM_mask], shell=True, capture_output=True)
subprocess.run(["fslmaths " + individualCSFSegmentation + " -thr 0.3 -bin " + CSF_mask], shell=True, capture_output=True)
