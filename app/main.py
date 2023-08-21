import string, os, sys

# Pre-run gears:
# 1. Isotropic reconstruction (CISO)
# 2. Bias correction (N4)
# 3. Brain extraction (HD-BET)


# a) pull template from SDK

#  Aim:
#  Tissue segmentations & ROIs in subject space (already registered to BCP)

#  Steps:
# 1. import the necessary packages
# 2. Calculate the warp from individual to template
# 4. Brain mask bias corrected images
# 5. Apply the warp to the ROIs & tissue segmentations
# 6. Calculate the jacobian matrices

# Set up the paths
FLYWHEEL_BASE = "/flywheel/v0"
INPUT_DIR = os.path.join(FLYWHEEL_BASE, "input")
OUTPUT_DIR = os.path.join(FLYWHEEL_BASE, "output")
TEMPLATE_DIR = os.path.join(FLYWHEEL_BASE, "template")
CONFIG_FILE = os.path.join(FLYWHEEL_BASE, "config.json")
WORK = os.path.join(FLYWHEEL_BASE, "work")

# Set up the variables
# studyHeadReference = templateDir + "/target/"
studyBrainReference = os.path.join(TEMPLATE_DIR, "/target/BCP-*M-T2.nii.gz")
individualMaskedBrain = os.path.join(INPUT_DIR, "/isotropicReconstruction_corrected_hdbet.nii.gz")
studyBrainMask = os.path.join(INPUT_DIR, "/isotropicReconstruction_corrected_hdbet_mask.nii.gz")

#  Set up the software
softwareHome = "/opt/ANTs/bin/"
antsN4 = softwareHome+"N4BiasFieldCorrection -d 3 -t -v -i "
antsWarp = softwareHome+"ANTS 3 -G -m CC["
antsMIWarp = softwareHome+"ANTS 3 -G -m MI["
antsImageAlign = softwareHome+"WarpImageMultiTransform 3 "


# # 0: Extract brain mask from the template
# BET=softwareHome+"hd-bet"
# os.system(BET+"-i "+studyHeadReference+" -o "+studyBrainReference) # No GPU: -device cpu -mode fast -tta 0
# # NEED TO CHECK THE OUTPUT NAMES


# 1: (DEPRICATED) Mask the bias corrected input image with the template brain mask
# individualMaskedBrain = FLYWHEEL_BASE + "/input/sub-01/isotropicReconstruction_corrected_masked.nii.gz"
# os.system("fslmaths "+biasCorrImage+" -mul "+studyBrainMask+" "+individualMaskedBrain)

# 2: Calculate the warp from the individual to the template brain
# save output as studyBrainReferenceAligned
studyAlignedBrainImage = WORK + "/isotropicReconstruction_corrected_masked_aligned.nii.gz"
os.system(antsWarp + studyBrainReference + ", " + individualMaskedBrain + ", 1, 6] -o " + studyAlignedBrainImage + " -i 60x90x45 -r Gauss[3,1] -t SyN[0.25] --use-Histogram-Matching --MI-option 32x16000 --number-of-affine-iterations 10000x10000x10000x10000x10000")

# Define variables from warp calculation in step 2
brainWarpField = WORK + "/isotropicReconstruction_corrected_masked_alignedWarp.nii.gz"
brainAffineField = WORK + "/isotropicReconstruction_corrected_masked_alignedAffine.txt"
brainInverseWarpField = WORK + "/isotropicReconstruction_corrected_masked_alignedInverseWarp.nii.gz"

# 3: Perform the warp on the individual brain image to align it to the template
alignedBrainImage = WORK + "/isotropicReconstruction_to_brainReferenceAligned.nii.gz"
os.system(antsImageAlign + " " + individualMaskedBrain + " " + alignedBrainImage + " -R " + studyBrainReference + " " + brainWarpField + " " + brainAffineField + " --use-BSpline")	


# 4: now align the individual white matter, gray matter, and csf maps to the brain template
#  Take the template priors and align them to the individual space
#  Then, use the warp field to align the individual segmentations to the template space

# Input variables from the previous warp step
alignedToStudyTemplateWM = WORK + "/WM_to_brainReferenceAligned.nii.gz"
alignedToStudyTemplateGM = WORK + "/GM_to_brainReferenceAligned.nii.gz"
alignedToStudyTemplateCSF = WORK + "/CSF_to_brainReferenceAligned.nii.gz"

# Input variables (priors)
whitePrior = TEMPLATE_DIR + "/BCP-03M-WM.nii.gz"
grayPrior = TEMPLATE_DIR + "/BCP-03M-GM.nii.gz"
csfPrior = TEMPLATE_DIR + "/BCP-03M-CSF.nii.gz"

# Output variables
individualWhiteSegmentation = WORK + "/initialWM.nii.gz"
individualGraySegmentation = WORK + "/initialGM.nii.gz"
individualCSFSegmentation = WORK + "/initialCSF.nii.gz"

os.system(antsImageAlign + " " + whitePrior + " " + individualWhiteSegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
os.system(antsImageAlign + " " + grayPrior + " " + individualGraySegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
os.system(antsImageAlign + " " + csfPrior + " " + individualCSFSegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")

# 5: Use output from hd-bet to mask the tissue segmentations
brainMask = FLYWHEEL_BASE + "hd-bet output" # link from SDK
maskedWMSegmentation = WORK + "/maskedWM.nii.gz"
maskedGMSegmentation = WORK + "/maskedGM.nii.gz"
maskedCSFSegmentation = WORK + "/maskedCSF.nii.gz"

os.system("fslmaths" + individualWhiteSegmentation +" -mas "+ brainMask + maskedWMSegmentation)
os.system("fslmaths" + individualGraySegmentation +" -mas "+ brainMask + maskedGMSegmentation)
os.system("fslmaths" + individualCSFSegmentation +" -mas "+ brainMask + maskedCSFSegmentation)

# 6: from the warp field, calculate the various jacobian matrices
logJacobian = WORK+"/logJacobian.nii.gz"
gJacobian = WORK+"/gJacobian.nii.gz"

antsJacobian = softwareHome+"CreateJacobianDeterminantImage 3 "
# os.system(antsJacobian+brainWarpField+" "+logJacobian+" 1 0")
# os.system(antsJacobian+brainWarpField+" "+gJacobian+" 0 1")

# 7: multiply the aligned images by the jacobian matrix to correct for the effect of the warp
logCorrectedWMSegmentation = WORK+"/studyWM_corr.nii"
logCorrectedGMSegmentation = WORK+"/studyGM_corr.nii"
logCorrectedCSFSegmentation = WORK+"/studyCSF_corr.nii"

antsMath = softwareHome+"ImageMath 3 "
os.system(antsMath + logCorrectedWMSegmentation +" m " + maskedWMSegmentation + " " + logJacobian)
os.system(antsMath + logCorrectedGMSegmentation +" m " + alignedToStudyTemplateGM + " " + logJacobian)
os.system(antsMath + logCorrectedCSFSegmentation +" m " + alignedToStudyTemplateCSF + " " + logJacobian)

gCorrectedWMSegmentation = WORK+"/studyWM_gcorr.nii"
gCorrectedGMSegmentation = WORK+"/studyGM_gcorr.nii"
gCorrectedCSFSegmentation = WORK+"/studyCSF_gcorr.nii"

os.system(antsMath + gCorrectedWMSegmentation + " m " + maskedWMSegmentation + " " + gJacobian)
os.system(antsMath + gCorrectedGMSegmentation + " m " + alignedToStudyTemplateGM + " " + gJacobian)
os.system(antsMath + gCorrectedCSFSegmentation + " m " + alignedToStudyTemplateCSF + " " + gJacobian)

# Setup in a seperate module
os.system("fslstats" + gCorrectedWMSegmentation + " -V | awk '{print $1}' > " + WORK + "/WMvol.txt")  
os.system("fslstats" + gCorrectedGMSegmentation + " -V | awk '{print $1}' > " + WORK + "/GMvol.txt")
os.system("fslstats" + gCorrectedCSFSegmentation + " -V | awk '{print $1}' > " + WORK + "/CSFvol.txt")


# # initilal wm is template segmentation in subject space
# # threshold at 0.5
# fslmaths initialWM.nii.gz -thr 0.5 bin.nii.gz
# # make binary mask
# fslmaths bin.nii.gz -bin binMask
# # erode the mask
# fslmaths binMask.nii.gz -ero erobinMask
# # apply the mask to the initial segmentation
# fslmaths initialWM.nii.gz -mas erobinMask.nii.gz maskedWMSegmentation
# # change the file type
# fslchfiletype NIFTI maskedWMSegmentation.nii.gz
# # calculate the log jacobian of maskedWMSegmentation
# ImageMath 3 logCorrWM.nii.gz m maskedWMSegmentation.nii.gz logJacobian.nii.gz
