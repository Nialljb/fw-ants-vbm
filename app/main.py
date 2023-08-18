import string, os, sys


# a) pull template from SDK




#  Aim:
#  Tissue segmentations & ROIs in subject space (already registered to BCP)

# 1. import the necessary packages
# 2. Calculate the warp from individual to template
# 3. Brain mask bias corrected images
# 3. Apply the warp to the ROIs & tissue segmentations

# hd-bet
# Need to multiply brain masks with ROIs as medial inferior regions, including cortico-spinal tracts, are not included in the brain mask

# hd-bet run on BCP template
templatesDirectory = home+"/3MonthRef"
studyHeadReference = templatesDirectory+"/BCP-03M-T2.nii.gz"
studyBrainReference = templatesDirectory+"/BCP-03M-T2-BET.nii.gz"
studyBrainMask = templatesDirectory+"/BCP-03M-T2-BET_mask.nii.gz"
biasCorrImage = home+"/input/sub-01/isotropicReconstruction_corrected.nii.gz"
studyReference_brain=studyBrainReference


softwareHome = "/opt/ANTs/bin/"
antsN4 = softwareHome+"N4BiasFieldCorrection -d 3 -t -v -i "
antsWarp = softwareHome+"ANTS 3 -G -m CC["
antsMIWarp = softwareHome+"ANTS 3 -G -m MI["
antsImageAlign = softwareHome+"WarpImageMultiTransform 3 "


# 0: Extract brain mask from the template
BET=softwareHome+"hd-bet"
os.system(BET+"-i "+studyHeadReference+" -o "+studyBrainReference) # No GPU: -device cpu -mode fast -tta 0
# NEED TO CHECK THE OUTPUT NAMES


# 1: Mask the bias corrected input image with the template brain mask
individualMaskedBrain=home+"/input/sub-01/isotropicReconstruction_corrected_masked.nii.gz"
# os.system("fslmaths "+biasCorrImage+" -mul "+studyBrainMask+" "+individualMaskedBrain)

# 2: Calculate the warp from the individual to the template brain
studyAlignedBrainImage=home+"/input/sub-01/isotropicReconstruction_corrected_masked_aligned.nii.gz"
# os.system(antsWarp+studyReference_brain+", "+individualMaskedBrain+", 1, 6] -o "+studyAlignedBrainImage+" -i 60x90x45 -r Gauss[3,1] -t SyN[0.25] --use-Histogram-Matching --MI-option 32x16000 --number-of-affine-iterations 10000x10000x10000x10000x10000")

# These calculated from step 2 or 3???

vbmAnalysisDirectory = home+"/input/sub-01/"
brainWarpField = vbmAnalysisDirectory+"/isotropicReconstruction_corrected_masked_alignedWarp.nii.gz"
brainAffineField = vbmAnalysisDirectory+"/isotropicReconstruction_corrected_masked_alignedAffine.txt"
brainInverseWarpField = vbmAnalysisDirectory+"/isotropicReconstruction_corrected_masked_alignedInverseWarp.nii.gz"

# 3: Perform the warp on the individual brain image to align it to the template
alignedBrainImage = home+"/input/sub-01/isotropicReconstruction_to_brainReferenceAligned.nii.gz"
# os.system(antsImageAlign+" "+individualMaskedBrain+" "+alignedBrainImage+" -R "+studyReference_brain+" "+brainWarpField+" "+brainAffineField+" --use-BSpline")	


# 4: now align the individual white matter, gray matter, and csf maps to the brain template
#  Take the template priors and align them to the individual space
#  Then, use the warp field to align the individual segmentations to the template space

# Input variables from the previous warp step
alignedToStudyTemplateWM = vbmAnalysisDirectory+"/WM_to_brainReferenceAligned.nii.gz"
alignedToStudyTemplateGM = vbmAnalysisDirectory+"/GM_to_brainReferenceAligned.nii.gz"
alignedToStudyTemplateCSF = vbmAnalysisDirectory+"/CSF_to_brainReferenceAligned.nii.gz"

# Input variables (priors)
whitePrior = templatesDirectory+"/BCP-03M-WM.nii.gz"
grayPrior = templatesDirectory+"/BCP-03M-GM.nii.gz"
csfPrior = templatesDirectory+"/BCP-03M-CSF.nii.gz"

# Output variables
individualWhiteSegmentation = vbmAnalysisDirectory+"/initialWM.nii.gz"
individualGraySegmentation = vbmAnalysisDirectory+"/initialGM.nii.gz"
individualCSFSegmentation = vbmAnalysisDirectory+"/initialCSF.nii.gz"

os.system(antsImageAlign+" "+whitePrior+" "+individualWhiteSegmentation+" -R "+biasCorrImage+" -i "+brainAffineField+" "+brainInverseWarpField+" --use-BSpline")
os.system(antsImageAlign+" "+grayPrior+" "+individualGraySegmentation+" -R "+biasCorrImage+" -i "+brainAffineField+" "+brainInverseWarpField+" --use-BSpline")
os.system(antsImageAlign+" "+csfPrior+" "+individualCSFSegmentation+" -R "+biasCorrImage+" -i "+brainAffineField+" "+brainInverseWarpField+" --use-BSpline")

# 5: Use output from hd-bet to mask the tissue segmentations
brainMask=home+"hd-bet output" # link from SDK
maskedWMSegmentation=vbmAnalysisDirectory+"/maskedWM.nii.gz"
maskedGMSegmentation=vbmAnalysisDirectory+"/maskedGM.nii.gz"
maskedCSFSegmentation=vbmAnalysisDirectory+"/maskedCSF.nii.gz"

os.system("fslmaths" + individualWhiteSegmentation +" -mas "+ brainMask + maskedWMSegmentation)
os.system("fslmaths" + individualGraySegmentation +" -mas "+ brainMask + maskedGMSegmentation)
os.system("fslmaths" + individualCSFSegmentation +" -mas "+ brainMask + maskedCSFSegmentation)

# 6: from the warp field, calculate the various jacobian matrices
logJacobian = vbmAnalysisDirectory+"/logJacobian.nii.gz"
gJacobian = vbmAnalysisDirectory+"/gJacobian.nii.gz"

antsJacobian = softwareHome+"CreateJacobianDeterminantImage 3 "
# os.system(antsJacobian+brainWarpField+" "+logJacobian+" 1 0")
# os.system(antsJacobian+brainWarpField+" "+gJacobian+" 0 1")

# 7: multiply the aligned images by the jacobian matrix to correct for the effect of the warp
logCorrectedWMSegmentation = vbmAnalysisDirectory+"/studyWM_corr.nii"
logCorrectedGMSegmentation = vbmAnalysisDirectory+"/studyGM_corr.nii"
logCorrectedCSFSegmentation = vbmAnalysisDirectory+"/studyCSF_corr.nii"

antsMath = softwareHome+"ImageMath 3 "
os.system(antsMath + logCorrectedWMSegmentation +" m " + maskedWMSegmentation + " " + logJacobian)
os.system(antsMath + logCorrectedGMSegmentation +" m " + alignedToStudyTemplateGM + " " + logJacobian)
os.system(antsMath + logCorrectedCSFSegmentation +" m " + alignedToStudyTemplateCSF + " " + logJacobian)

gCorrectedWMSegmentation = vbmAnalysisDirectory+"/studyWM_gcorr.nii"
gCorrectedGMSegmentation = vbmAnalysisDirectory+"/studyGM_gcorr.nii"
gCorrectedCSFSegmentation = vbmAnalysisDirectory+"/studyCSF_gcorr.nii"

os.system(antsMath + gCorrectedWMSegmentation + " m " + maskedWMSegmentation + " " + gJacobian)
os.system(antsMath + gCorrectedGMSegmentation + " m " + alignedToStudyTemplateGM + " " + gJacobian)
os.system(antsMath + gCorrectedCSFSegmentation + " m " + alignedToStudyTemplateCSF + " " + gJacobian)

# Setup in a seperate module
os.system("fslstats" + gCorrectedWMSegmentation + " -V | awk '{print $1}' > " + vbmAnalysisDirectory + "/WMvol.txt")  
os.system("fslstats" + gCorrectedGMSegmentation + " -V | awk '{print $1}' > " + vbmAnalysisDirectory + "/GMvol.txt")
os.system("fslstats" + gCorrectedCSFSegmentation + " -V | awk '{print $1}' > " + vbmAnalysisDirectory + "/CSFvol.txt")


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
