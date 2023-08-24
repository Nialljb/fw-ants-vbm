import os, sys
from pathlib import Path

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

def run_main(subject, session):
    # Set up the paths
    FLYWHEEL_BASE = "/flywheel/v0"
    INPUT_DIR = (FLYWHEEL_BASE + "/input/input/")
    OUTPUT_DIR = (FLYWHEEL_BASE + "/output")
    TEMPLATE_DIR = (FLYWHEEL_BASE + "/template")
    CONFIG_FILE = (FLYWHEEL_BASE + "/config.json")
    WORK = (FLYWHEEL_BASE + "/work")


    targetDir = Path(WORK) # To rglob
    for filepath in targetDir.rglob('BCP-??M-T2.nii.gz'):
        studyBrainReference = str(filepath)
        break
    for filepath in targetDir.rglob('BCP-??M-GM.nii.gz'):
        grayPrior = str(filepath)
        break
    for filepath in targetDir.rglob('BCP-??M-WM.nii.gz'):
        whitePrior = str(filepath)
        break
    for filepath in targetDir.rglob('BCP-??M-CSF.nii.gz'):
        csfPrior = str(filepath)
        break

    print("ref is: ", studyBrainReference)

    individualMaskedBrain = (INPUT_DIR + "/isotropicReconstruction_corrected_hdbet.nii.gz")
    studyBrainMask = (INPUT_DIR + "/isotropicReconstruction_corrected_hdbet_mask.nii.gz")
     
    print("input brain is: ", individualMaskedBrain)


    #  Set up the software
    softwareHome = "/opt/ants/bin/"
    antsN4 = softwareHome + "N4BiasFieldCorrection -d 3 -t -v -i "
    antsWarp = softwareHome + "ANTS 3 -G -m CC["
    antsMIWarp = softwareHome + "ANTS 3 -G -m MI["
    antsImageAlign = softwareHome + "WarpImageMultiTransform 3 "
    antsMath = softwareHome + "ImageMath 3 "

 
    # -----------------  Start processing  -----------------  #

    # 1: Calculate the warp from the individual to the template brain
    # save output as studyBrainReferenceAligned
    print("Calculating warp from individual to template brain...")
    studyAlignedBrainImage = (WORK + "/isotropicReconstruction_corrected_masked_aligned.nii.gz")
    os.system(antsWarp + studyBrainReference + ", " + individualMaskedBrain + ", 1, 6] -o " + studyAlignedBrainImage + " -i 60x90x45 -r Gauss[3,1] -t SyN[0.25] --use-Histogram-Matching --MI-option 32x16000 --number-of-affine-iterations 10000x10000x10000x10000x10000")

    # Define variables from warp calculation in step 1
    brainWarpField = (WORK + "/isotropicReconstruction_corrected_masked_alignedWarp.nii.gz")
    brainAffineField = (WORK + "/isotropicReconstruction_corrected_masked_alignedAffine.txt")
    brainInverseWarpField = (WORK + "/isotropicReconstruction_corrected_masked_alignedInverseWarp.nii.gz")

    # 2: Perform the warp on the individual brain image to align it to the template
    print("Aligning individual brain to template...")
    alignedBrainImage = (WORK + "/isotropicReconstruction_to_brainReferenceAligned.nii.gz")
    os.system(antsImageAlign + " " + individualMaskedBrain + " " + alignedBrainImage + " -R " + studyBrainReference + " " + brainWarpField + " " + brainAffineField + " --use-BSpline")	

    # 3: now align the individual white matter, gray matter, and csf maps to the brain template
    #  Take the template priors and align them to the individual space

    # Output variables
    print("Aligning tissue segmentations to template...")
    individualWhiteSegmentation = (WORK + "/initialWM.nii.gz")
    individualGraySegmentation = (WORK + "/initialGM.nii.gz")
    individualCSFSegmentation = (WORK + "/initialCSF.nii.gz")

    os.system(antsImageAlign + " " + whitePrior + " " + individualWhiteSegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
    os.system(antsImageAlign + " " + grayPrior + " " + individualGraySegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
    os.system(antsImageAlign + " " + csfPrior + " " + individualCSFSegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")

    # 4: Use output from hd-bet to mask the tissue segmentations
    print("Masking tissue segmentations...")
    maskedWMSegmentation = (WORK + "/maskedWM.nii.gz")
    maskedGMSegmentation = (WORK + "/maskedGM.nii.gz")
    maskedCSFSegmentation = (WORK + "/maskedCSF.nii.gz")

    os.system("fslmaths " + individualWhiteSegmentation + " -mas " + studyBrainMask + " " + maskedWMSegmentation)
    os.system("fslmaths " + individualGraySegmentation + " -mas " + studyBrainMask + " " + maskedGMSegmentation)
    os.system("fslmaths " + individualCSFSegmentation + " -mas " + studyBrainMask + " " + maskedCSFSegmentation)

    # 6: from the warp field, calculate the various jacobian matrices
    print("Calculating jacobian matrices...")
    logJacobian = (WORK + "/logJacobian.nii.gz")
    gJacobian = (WORK + " /gJacobian.nii.gz")

    antsJacobian = (softwareHome + "CreateJacobianDeterminantImage 3 ")
    os.system(antsJacobian + " " + brainWarpField + " " + logJacobian + " 1 0")
    os.system(antsJacobian + " " + brainWarpField + " " + gJacobian + " 0 1")

    # 7: multiply the aligned images by the jacobian matrix to correct for the effect of the warp
    print("Multiplying aligned images by jacobian matrix...")
    logCorrectedWMSegmentation = (WORK + "/studyWM_corr.nii")
    logCorrectedGMSegmentation = (WORK + "/studyGM_corr.nii")
    logCorrectedCSFSegmentation = (WORK + "/studyCSF_corr.nii")


    os.system(antsMath + " " + logCorrectedWMSegmentation + " m " + maskedWMSegmentation + " " + logJacobian)
    os.system(antsMath + " " + logCorrectedGMSegmentation + " m " + maskedWMSegmentation + " " + logJacobian)
    os.system(antsMath + " " + logCorrectedCSFSegmentation + " m " + maskedWMSegmentation + " " + logJacobian)

    gCorrectedWMSegmentation = (WORK + "/studyWM_gcorr.nii")
    gCorrectedGMSegmentation = (WORK + "/studyGM_gcorr.nii")
    gCorrectedCSFSegmentation = (WORK + "/studyCSF_gcorr.nii")

    try:
        os.system(antsMath + " " + gCorrectedWMSegmentation + " m " + maskedWMSegmentation + " " + gJacobian)
        os.system(antsMath + " " + gCorrectedGMSegmentation + " m " + maskedWMSegmentation + " " + gJacobian)
        os.system(antsMath + " " + gCorrectedCSFSegmentation + " m " + maskedWMSegmentation + " " + gJacobian)
    except:
        print("Error in calculating gJacobian")
        sys.exit(1)

    # 8: Calculate the volumes of the tissue segmentations
    print("Calculating tissue volumes...")
    # Setup in a seperate module

    os.system("echo subject, session > " + WORK + "/demo.txt; echo " + subject + ", " + session + " >> " + WORK + "/demo.txt")  
    os.system("echo WM > " + WORK + "/WMvol.txt; fslstats " + gCorrectedWMSegmentation + " -V | awk '{print $1}' >> " + WORK + "/WMvol.txt")  
    os.system("echo GM > " + WORK + "/GMvol.txt; fslstats " + gCorrectedGMSegmentation + " -V | awk '{print $1}' >> " + WORK + "/GMvol.txt")
    os.system("echo CSV > " + WORK + "/CSVvol.txt; fslstats " + gCorrectedCSFSegmentation + " -V | awk '{print $1}' >> " + WORK + "/CSFvol.txt")
    os.system('paste -d "," '  + WORK + '/demo.txt ' + WORK + '/WMvol.txt ' + WORK + '/GMvol.txt ' + WORK + '/CSFvol.txt > ' + OUTPUT_DIR + '/volumes.csv')
