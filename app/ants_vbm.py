import os, sys
from pathlib import Path
import subprocess
import pandas as pd  
import utils.ROI as ROI
import utils.registration as registration

# Pre-run gears:
# 1. Isotropic reconstruction (CISO)
# 2. Bias correction (N4)
# 3. Brain extraction (SBET)

# Required inputs:
# Age matched templates should be pulled from the template directory (previous module)
# Brain mask should be pulled from the previous module

#  Steps:
# 1. import the necessary packages
# 2. Calculate the warp from individual to template
# 4. Brain mask bias corrected images
# 5. Apply the warp to the ROIs & tissue segmentations
# 6. Calculate the jacobian matrices
# 7. Multiply the aligned images by the jacobian matrix to correct for the effect of the warp
# 8. Calculate the volumes of the tissue segmentations
# 9. Calculate the volumes of the ROIs
# 10. Save the volumes

#  -------------------  The main event -------------------  #

def vbm(subject_label, session_label, target_template, age, patientSex, input, HarvardOxford_Cortical, HarvardOxford_Subcortical, Glasser, Jolly, ICBM81):
    
    print("Input: ", input)
    print("subject_label: ", subject_label)
    print("session_label: ", session_label)
    print("target_template: ", target_template)
    print("HarvardOxford_Cortical: ", HarvardOxford_Cortical)
    print("HarvardOxford_Subcortical: ", HarvardOxford_Subcortical)
    print("Glasser: ", Glasser)
    print("Jolly: ", Jolly)
    print("ICBM81: ", ICBM81)

    # Define output dataframe
    data = [{'subject': subject_label, 'session': session_label}]  
    df = pd.DataFrame(data)

    #  -------------------  Import the necessary packages & variables -------------------  #
    # Set up the paths
    FLYWHEEL_BASE = "/flywheel/v0"
    INPUT_DIR = (FLYWHEEL_BASE + "/input/input/")
    OUTPUT_DIR = (FLYWHEEL_BASE + "/output")
    WORK = (FLYWHEEL_BASE + "/work")
    TEMPLATE = ('/flywheel/v0/app/templates/' + target_template + "/")
 
    # Individual input variables
    for file in os.listdir(INPUT_DIR):
        if file.find("isotropicReconstruction_corrected_sbet_brain.nii.gz")>=0:       
            individualMaskedBrain = (INPUT_DIR + file)
        elif file.find("isotropicReconstruction_corrected_sbet_mask.nii.gz")>=0:
            initialBrainMask = (INPUT_DIR + file)

    print("Initial brain is: ", individualMaskedBrain)   
    print("Initial brain mask is: ", initialBrainMask)

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

    # -----------------  Start processing  -----------------  #

    # 1: Calculate the warp from the individual to the template brain
    # save output as studyBrainReferenceAligned
    print("Calculating warp from individual to template brain...")
    studyAlignedBrainImage = (WORK + "/initialBrainMaskedImage_aligned.nii.gz")
    try:
        result = subprocess.run([antsWarp + studyBrainReference + ", " + individualMaskedBrain + ", 1, 6] -o " + studyAlignedBrainImage + " -i 60x90x45 -r Gauss[3,1] -t SyN[0.25] --use-Histogram-Matching --MI-option 32x16000 --number-of-affine-iterations 10000x10000x10000x10000x10000"], shell=True, check=True) # , text=True , capture_output=True
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
    # Output variables
    print("Aligning tissue segmentations to template...")
    individualWhiteSegmentation = (WORK + "/initialWM.nii.gz")
    individualGraySegmentation = (WORK + "/initialGM.nii.gz")
    individualCSFSegmentation = (WORK + "/initialCSF.nii.gz")
    studyBrainMask = (WORK + "/alignedBrainMask.nii.gz")

    try:
        os.system(antsImageAlign + " " + whitePrior + " " + individualWhiteSegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
        os.system(antsImageAlign + " " + grayPrior + " " + individualGraySegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
        os.system(antsImageAlign + " " + csfPrior + " " + individualCSFSegmentation + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")
    except:
        print("Error in aligning tissue segmentations to template")
        sys.exit(1)

    try:
        subprocess.run([antsImageAlign + " " + initialBrainMask + " " + studyBrainMask + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline"], shell=True, capture_output = True)
    except:
        print("Error in aligning original brain mask to template")
        sys.exit(1) # exit if error

    # --- 4: Use output from bet to mask the tissue segmentations    ---  #  

    print("Masking tissue segmentations...")
    maskedWMSegmentation = (WORK + "/maskedWM.nii.gz")
    maskedGMSegmentation = (WORK + "/maskedGM.nii.gz")
    maskedCSFSegmentation = (WORK + "/maskedCSF.nii.gz")

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

    # --- 6: from the warp field, calculate the various jacobian matrices ---  #

    print("Calculating jacobian matrices...")
    logJacobian = (OUTPUT_DIR + "/logJacobian.nii.gz")
    gJacobian = (OUTPUT_DIR + "/gJacobian.nii.gz")

    antsJacobian = (softwareHome + "CreateJacobianDeterminantImage 3 ")
    try:
        os.system(antsJacobian + " " + brainWarpField + " " + logJacobian + " 1 0")
        os.system(antsJacobian + " " + brainWarpField + " " + gJacobian + " 0 1")
    except:
        print("Error in calculating jacobian matrices")
        sys.exit(1)

    # --- 7: multiply the aligned images by the jacobian matrix to correct for the effect of the warp ---  #

    print("Multiplying aligned images by jacobian matrix...")
    logCorrectedWMSegmentation = (OUTPUT_DIR + "/WM_corr.nii")
    logCorrectedGMSegmentation = (OUTPUT_DIR + "/GM_corr.nii")
    logCorrectedCSFSegmentation = (OUTPUT_DIR + "/CSF_corr.nii")
    try:
        os.system(antsMath + " " + logCorrectedWMSegmentation + " m " + maskedWMSegmentation + " " + logJacobian)
        os.system(antsMath + " " + logCorrectedGMSegmentation + " m " + maskedGMSegmentation + " " + logJacobian)
        os.system(antsMath + " " + logCorrectedCSFSegmentation + " m " + maskedCSFSegmentation + " " + logJacobian)
    except:
        print("Error in calculating logJacobian")
        sys.exit(1)

    gCorrectedWMSegmentation = (OUTPUT_DIR + "/WM_gcorr.nii")
    gCorrectedGMSegmentation = (OUTPUT_DIR + "/GM_gcorr.nii")
    gCorrectedCSFSegmentation = (OUTPUT_DIR + "/CSF_gcorr.nii")
    try:
        os.system(antsMath + " " + gCorrectedWMSegmentation + " m " + maskedWMSegmentation + " " + gJacobian)
        os.system(antsMath + " " + gCorrectedGMSegmentation + " m " + maskedGMSegmentation + " " + gJacobian)
        os.system(antsMath + " " + gCorrectedCSFSegmentation + " m " + maskedCSFSegmentation + " " + gJacobian)
    except:
        print("Error in calculating gJacobian")
        sys.exit(1)
    
    # --- 8: Calculate the volumes of the tissue segmentations ---  #

    print("Calculating tissue volumes...")

    # subprocess with check_output runs a shell command and returns the output as a byte string, which is then decoded into a string (.decode("utf-8")
    # We then convert the string to a float for calculations

    # Calculate the volumes of the tissue segmentations
    seg_vol_wm = float(subprocess.check_output(["fslstats " + gCorrectedWMSegmentation + " -k " + maskedWMSegmentation + " -V | awk '{print $1}' "], shell=True).decode("utf-8"))
    seg_vol_gm = float(subprocess.check_output(["fslstats " + gCorrectedGMSegmentation + " -k " + maskedGMSegmentation + " -V | awk '{print $1}' "], shell=True).decode("utf-8"))
    seg_vol_csf = float(subprocess.check_output(["fslstats " + gCorrectedCSFSegmentation + " -k " + maskedCSFSegmentation + " -V | awk '{print $1}' "], shell=True).decode("utf-8"))

    # Calculate the mean intensities
    mi_wm = float(subprocess.check_output(["fslstats " + gCorrectedWMSegmentation + " -k " + maskedWMSegmentation + " -M | awk '{print $1}' "], shell=True).decode("utf-8"))
    mi_gm = float(subprocess.check_output(["fslstats " + gCorrectedGMSegmentation + " -k " + maskedGMSegmentation + " -M | awk '{print $1}' "], shell=True).decode("utf-8"))
    mi_csf = float(subprocess.check_output(["fslstats " + gCorrectedCSFSegmentation + " -k " + maskedCSFSegmentation + " -M | awk '{print $1}' "], shell=True).decode("utf-8"))

    # Calculate the volumes by multiplying the mean intensity by the volume & scaling by image dimensions (1.5mm^3)
    wm_vol = seg_vol_wm * mi_wm * 1.5 * 1.5 * 1.5
    gm_vol = seg_vol_gm * mi_gm * 1.5 * 1.5 * 1.5
    csf_vol = seg_vol_csf * mi_csf * 1.5 * 1.5 * 1.5

    print("WM volume: ", wm_vol)
    print("GM volume: ", gm_vol)
    print("CSF volume: ", csf_vol)

    # assign values to lists. 
    data = [{'subject': subject_label, 'session': session_label, 'age': age, 'sex': patientSex, 'wm_vol': wm_vol, 'gm_vol': gm_vol, 'csf_vol': csf_vol}]  
    # Creates DataFrame.  
    df = pd.DataFrame(data)
    df.to_csv(index=False, path_or_buf=OUTPUT_DIR + '/volumes.csv')


    # Backup of mean intensity calculation
    BackupData = [{'subject': subject_label, 'session': session_label, 'age': age, 'sex': patientSex, 'wm_vol': mi_wm, 'gm_vol': mi_gm, 'csf_vol': mi_csf}]  
    # Creates DataFrame.  
    Backup_df = pd.DataFrame(BackupData)
    Backup_df.to_csv(index=False, path_or_buf=OUTPUT_DIR + '/MI.csv')

    # --- 9: Calculate warps from MNI to BCP template ---  #
    # registration.MNI2BCP(studyBrainReference, WORK)
 
    # --- 10: ROI registration ---  #

    if HarvardOxford_Subcortical == True:
        df, Backup_df = ROI.run_subcortical(FLYWHEEL_BASE, WORK, antsImageAlign, individualMaskedBrain, gCorrectedGMSegmentation, GM_mask, brainAffineField, brainInverseWarpField, df, Backup_df)
 
    if HarvardOxford_Cortical == True:
        df, Backup_df = ROI.run_cortical(FLYWHEEL_BASE, WORK, antsImageAlign, individualMaskedBrain, gCorrectedGMSegmentation, GM_mask, brainAffineField, brainInverseWarpField, df, Backup_df)

    if Glasser == True:
        print("Sorry, Glasser 2016 atlas is not yet implemented")
    
    if ICBM81 == True:
        df, Backup_df = ROI.run_ICBM81(FLYWHEEL_BASE, WORK, antsImageAlign, individualMaskedBrain, gCorrectedWMSegmentation,  WM_mask, brainAffineField, brainInverseWarpField, df, Backup_df)


    # -----------------  Save the volumes  -----------------  #

    df.to_csv(index=False, path_or_buf=OUTPUT_DIR + '/volumes.csv')
    print("Volumes saved to: ", OUTPUT_DIR + '/volumes.csv')

    Backup_df.to_csv(index=False, path_or_buf=OUTPUT_DIR + '/MI.csv')

    #  tmp save ROIs to sanity check registration
    try:
        subprocess.run(["cp " + WORK + "/BCC_Aligned.nii.gz " + OUTPUT_DIR + "/BCC_Aligned.nii.gz"], shell=True, capture_output = True)	
        subprocess.run(["cp " + WORK + "/lh_Frontal_Orbital_Cortex_Aligned.nii.gz " + OUTPUT_DIR + "/lh_Frontal_Orbital_Cortex_Aligned.nii.gz"], shell=True, capture_output = True)	
        subprocess.run(["cp " + WORK + "/Left_Caudate_Aligned.nii.gz " + OUTPUT_DIR + "/Left_Caudate_Aligned.nii.gz"], shell=True, capture_output = True)	
    except:
        print("Error in copying ROIs")