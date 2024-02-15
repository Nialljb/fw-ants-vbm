import subprocess
import os, sys

# Steps required
# input data could be in any atlas space, initial registration needs to be done to a specified template
# The tissue priors and ROIs are in BCP space, so we need to first align input data to BCP space, back propagate the priors and ROIs to the input space, and then segment the input data
# Finally, we need need to register the input, priors, and ROIs to the desired(specified) template space. 
# In infants this will be the BCP template, in adults this will be the MNI template


def initalWarp(studyBrainReference, individualMaskedBrain, WORK):

    # ---  Set up the software ---  #

    softwareHome = "/opt/ants/bin/"
    antsWarp = softwareHome + "ANTS 3 -G -m CC["
    antsImageAlign = softwareHome + "WarpImageMultiTransform 3 "
    antsMath = softwareHome + "ImageMath 3 "

    # Create a warp field to align the individual brain to the template
    brainWarpField = (WORK + '/brainWarpField.nii.gz')
    brainAffineField = (WORK + '/brainAffineField.nii.gz')
    brainInverseWarpField = (WORK + '/brainInverseWarpField.nii.gz')

    # Does this work???
    # subprocess.run(['antsRegistrationSyNQuick.sh -d 3 -f ' + template + ' -m ' + studyBrainReference + ' -o ' + WORK + '/brain'], shell=True, capture_output = True)
    # return brainWarpField, brainAffineField, brainInverseWarpField

# 1: Calculate the warp from the individual to the template brain
    # save output as studyBrainReferenceAligned
    print("Calculating warp from individual to template brain...")
    studyAlignedBrainImage = (WORK + "/initialBrainMaskedImage_aligned.nii.gz")
    try:
        result = subprocess.run([antsWarp + studyBrainReference + ", " + individualMaskedBrain + ", 1, 6] -o " + studyAlignedBrainImage + " -i 60x90x45 -r Gauss[3,1] -t SyN[0.25] --use-Histogram-Matching --MI-option 32x16000 --number-of-affine-iterations 10000x10000x10000x10000x10000"], shell=True, check=True) 
    except:
        print("*Error in calculating warp*")
        print(result.stderr)
        sys.exit(1)

    # Define variables from warp calculation in step 1
    brainWarpField = (WORK + "/initialBrainMaskedImage_alignedWarp.nii.gz")
    brainAffineField = (WORK + "/initialBrainMaskedImage_alignedAffine.txt")
    brainInverseWarpField = (WORK + "/initialBrainMaskedImage_alignedInverseWarp.nii.gz")

    # --- 2: Perform the warp on the individual brain image to align it to the template ---  #

    print("Aligning individual brain to template...")
    alignedBrainImage = (WORK + "/isotropicReconstruction_to_brainReferenceAligned.nii.gz")
    try:
        os.system(antsImageAlign + " " + individualMaskedBrain + " " + alignedBrainImage + " -R " + studyBrainReference + " " + brainWarpField + " " + brainAffineField + " --use-BSpline")	
    except:
        print("Error in aligning individual brain to template")
        sys.exit(1)

    # --- 3: now align the individual white matter, gray matter, and csf priors to the individual brain using reverse warp ---  #

    #  Take the template priors and align them to the individual space
    print("Aligning tissue segmentations to template...")
    studyBrainMask = (WORK + "/alignedBrainMask.nii.gz")

    try:
        subprocess.run([antsImageAlign + " " + initialBrainMask + " " + studyBrainMask + " -R " + studyBrainReference + " " + brainWarpField + " " + brainAffineField + " --use-BSpline"], shell=True, capture_output = True)
    except:
        print("Error in aligning original brain mask to template")
        sys.exit(1) # exit if error

    # --- 4: Use output from bet to mask the tissue segmentations    ---  #  

    print("Masking tissue segmentations...")
    # segmentations already in template space so copy them over
    individualWhiteSegmentation = (WORK + "/initialWM.nii.gz")
    individualGraySegmentation = (WORK + "/initialGM.nii.gz")
    individualCSFSegmentation = (WORK + "/initialCSF.nii.gz")
    maskedWMSegmentation = (WORK + "/maskedWM.nii.gz")
    maskedGMSegmentation = (WORK + "/maskedGM.nii.gz")
    maskedCSFSegmentation = (WORK + "/maskedCSF.nii.gz")

    # Already in template space so no need to warp them as this may introduce errors
    os.system("cp "+whitePrior+" "+individualWhiteSegmentation)
    os.system("cp "+grayPrior+" "+individualGraySegmentation)
    os.system("cp "+csfPrior+" "+individualCSFSegmentation)
    try:
        os.system("fslmaths " + individualWhiteSegmentation + " -mas " + studyBrainMask + " " + maskedWMSegmentation)
        os.system("fslmaths " + individualGraySegmentation + " -mas " + studyBrainMask + " " + maskedGMSegmentation)
        os.system("fslmaths " + individualCSFSegmentation + " -mas " + studyBrainMask + " " + maskedCSFSegmentation)
    except:
        print("Error in masking tissue segmentations")
        sys.exit(1)

    # --- 5: Threshold the tissue segmentations to create eroded binary masks ---  #

    GM_mask = (OUTPUT_DIR + "/GM_mask.nii.gz")
    WM_mask = (OUTPUT_DIR + "/WM_mask.nii.gz")
    subprocess.run(["fslmaths " + maskedGMSegmentation + " -thr 0.3 -bin " + GM_mask], shell=True, capture_output=True)
    subprocess.run(["fslmaths " + maskedWMSegmentation + " -thr 0.3 -bin " + WM_mask], shell=True, capture_output=True)
