import string, os, sys, re, glob

# Pre-run gears:
# 1. Isotropic reconstruction (CISO)
# 2. Bias correction (N4)
# 3. Brain extraction (HD-BET)

# Required inputs:
# Age matched templates should be pulled from the template directory (previous module)
# Brain mask should be pulled from the previous module

#  Steps:
# 1. import the necessary packages
# 2. Calculate the warp from individual to template
# 4. Brain mask bias corrected images
# 5. Apply the warp to the ROIs & tissue segmentations
# 6. Calculate the jacobian matrices

#  -------------------  Import the necessary packages & variables -------------------  #

# Set up the paths
FLYWHEEL_BASE = "/flywheel/v0"
INPUT_DIR = os.path.join(FLYWHEEL_BASE, "input")
OUTPUT_DIR = os.path.join(FLYWHEEL_BASE, "output")
TEMPLATE_DIR = os.path.join(FLYWHEEL_BASE, "template")
CONFIG_FILE = os.path.join(FLYWHEEL_BASE, "config.json")
WORK = os.path.join(FLYWHEEL_BASE, "work")

# Set up the variables
# studyHeadReference = templateDir + "/target/"
targetDir = os.path.join(WORK, "/target/")

for file in targetDir:
    if re.search("BCP-.*M-T2.nii.gz", file):
        studyBrainReference = file
        break
    if re.search("BCP-.*M-GM.nii.gz", file):
        grayPrior = file
        break
    if re.search("BCP-.*M-WM.nii.gz", file):
        whitePrior = file
        break
    if re.search("BCP-.*M-CSF.nii.gz", file):
        csfPrior = file
        break

# for file in glob.glob(targetDir, 'BCP-??M-T2.nii.gz'):
#     studyBrainReference = file
#     break
# Input variables (priors)
# whitePrior = TEMPLATE_DIR + "/BCP-03M-WM.nii.gz"
# grayPrior = TEMPLATE_DIR + "/BCP-03M-GM.nii.gz"
# csfPrior = TEMPLATE_DIR + "/BCP-03M-CSF.nii.gz"

# studyBrainReference = os.path.join(TEMPLATE_DIR, "/target/BCP-*M-T2.nii.gz")
# re.search("BCP-.*M-T2.nii.gz", studyBrainReference)
individualMaskedBrain = os.path.join(INPUT_DIR, "/isotropicReconstruction_corrected_hdbet.nii.gz")
studyBrainMask = os.path.join(INPUT_DIR, "/isotropicReconstruction_corrected_hdbet_mask.nii.gz")

#  Set up the software
softwareHome = "/opt/ANTs/bin/"
antsN4 = softwareHome+"N4BiasFieldCorrection -d 3 -t -v -i "
antsWarp = softwareHome+"ANTS 3 -G -m CC["
antsMIWarp = softwareHome+"ANTS 3 -G -m MI["
antsImageAlign = softwareHome+"WarpImageMultiTransform 3 "
antsMath = softwareHome+"ImageMath 3 "

# -----------------  Start processing  -----------------  #

# 1: Calculate the warp from the individual to the template brain
# save output as studyBrainReferenceAligned
studyAlignedBrainImage = WORK + "/isotropicReconstruction_corrected_masked_aligned.nii.gz"
os.system(antsWarp + studyBrainReference + ", " + individualMaskedBrain + ", 1, 6] -o " + studyAlignedBrainImage + " -i 60x90x45 -r Gauss[3,1] -t SyN[0.25] --use-Histogram-Matching --MI-option 32x16000 --number-of-affine-iterations 10000x10000x10000x10000x10000")

# Define variables from warp calculation in step 1
brainWarpField = WORK + "/isotropicReconstruction_corrected_masked_alignedWarp.nii.gz"
brainAffineField = WORK + "/isotropicReconstruction_corrected_masked_alignedAffine.txt"
brainInverseWarpField = WORK + "/isotropicReconstruction_corrected_masked_alignedInverseWarp.nii.gz"

# 2: Perform the warp on the individual brain image to align it to the template
alignedBrainImage = WORK + "/isotropicReconstruction_to_brainReferenceAligned.nii.gz"
os.system(antsImageAlign + " " + individualMaskedBrain + " " + alignedBrainImage + " -R " + studyBrainReference + " " + brainWarpField + " " + brainAffineField + " --use-BSpline")	

# 3: now align the individual white matter, gray matter, and csf maps to the brain template
#  Take the template priors and align them to the individual space

# Output variables
individualWhiteSegmentation = WORK + "/initialWM.nii.gz"
individualGraySegmentation = WORK + "/initialGM.nii.gz"
individualCSFSegmentation = WORK + "/initialCSF.nii.gz"

os.system(antsImageAlign + " " + whitePrior + " " + individualWhiteSegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
os.system(antsImageAlign + " " + grayPrior + " " + individualGraySegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
os.system(antsImageAlign + " " + csfPrior + " " + individualCSFSegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")

# 4: Use output from hd-bet to mask the tissue segmentations
maskedWMSegmentation = WORK + "/maskedWM.nii.gz"
maskedGMSegmentation = WORK + "/maskedGM.nii.gz"
maskedCSFSegmentation = WORK + "/maskedCSF.nii.gz"

os.system("fslmaths" + individualWhiteSegmentation + " -mas " + studyBrainMask + maskedWMSegmentation)
os.system("fslmaths" + individualGraySegmentation + " -mas " + studyBrainMask + maskedGMSegmentation)
os.system("fslmaths" + individualCSFSegmentation + " -mas " + studyBrainMask + maskedCSFSegmentation)

# 6: from the warp field, calculate the various jacobian matrices
logJacobian = WORK + "/logJacobian.nii.gz"
gJacobian = WORK + " /gJacobian.nii.gz"

antsJacobian = softwareHome + "CreateJacobianDeterminantImage 3 "
os.system(antsJacobian + brainWarpField + " " + logJacobian + " 1 0")
os.system(antsJacobian + brainWarpField + " " + gJacobian + " 0 1")

# 7: multiply the aligned images by the jacobian matrix to correct for the effect of the warp
logCorrectedWMSegmentation = WORK + "/studyWM_corr.nii"
logCorrectedGMSegmentation = WORK + "/studyGM_corr.nii"
logCorrectedCSFSegmentation = WORK + "/studyCSF_corr.nii"


os.system(antsMath + logCorrectedWMSegmentation + " m " + maskedWMSegmentation + " " + logJacobian)
os.system(antsMath + logCorrectedGMSegmentation + " m " + alignedToStudyTemplateGM + " " + logJacobian)
os.system(antsMath + logCorrectedCSFSegmentation + " m " + alignedToStudyTemplateCSF + " " + logJacobian)

gCorrectedWMSegmentation = WORK + "/studyWM_gcorr.nii"
gCorrectedGMSegmentation = WORK + "/studyGM_gcorr.nii"
gCorrectedCSFSegmentation = WORK + "/studyCSF_gcorr.nii"

os.system(antsMath + gCorrectedWMSegmentation + " m " + maskedWMSegmentation + " " + gJacobian)
os.system(antsMath + gCorrectedGMSegmentation + " m " + alignedToStudyTemplateGM + " " + gJacobian)
os.system(antsMath + gCorrectedCSFSegmentation + " m " + alignedToStudyTemplateCSF + " " + gJacobian)

# Setup in a seperate module
os.system("fslstats" + gCorrectedWMSegmentation + " -V | awk '{print $1}' > " + OUTPUT_DIR + "/WMvol.txt")  
os.system("fslstats" + gCorrectedGMSegmentation + " -V | awk '{print $1}' > " + OUTPUT_DIR + "/GMvol.txt")
os.system("fslstats" + gCorrectedCSFSegmentation + " -V | awk '{print $1}' > " + OUTPUT_DIR + "/CSFvol.txt")

