import os
import subprocess

def run_jolly(FLYWHEEL_BASE, WORK, OUTPUT_DIR, studyBrainReference, wm, wm_mask, df):
    print("Aligning white matter tracts to template...")
    atlas = (FLYWHEEL_BASE + "/app/templates/atlas/wm/MedicolegalTracts")
    for region in os.listdir(atlas):
        f = os.path.join(atlas, region)
        # checking if it is a file
        if os.path.isfile(f):
            regionName = region.split(".")[0]
            print("ROI: ", regionName)  
            if regionName == "":
                continue
            else:
                # 2: Perform the warp on the individual brain image to align it to the template
                print("Warping...")
                MNI_WARP = (WORK + "/mni2bcp_1Warp.nii.gz")
                MNI_AFFINE = (WORK + "/mni2bcp_0GenericAffine.mat")
                MNIAligned = (WORK + "/" + regionName + "_Aligned.nii.gz")
                # Run registration
                subprocess.run(['antsApplyTransforms -d 3 -i ' + f + ' -r ' + studyBrainReference + ' -t ' + MNI_WARP + ' -t ' + MNI_AFFINE + ' -n GenericLabel -o ' + MNIAligned], shell=True, capture_output = True)
                subprocess.run(["fslmaths " + MNIAligned + " -mul " + wm_mask + " " + MNIAligned], shell=True, capture_output = True)	

                # Calculate volume
                est = float(subprocess.check_output(["fslstats " + wm + " -k " + MNIAligned + " -M | awk '{print $1}' "], shell=True).decode("utf-8"))
                mask_vol = float(subprocess.check_output(["fslstats " + wm + " -k " + MNIAligned + " -V | awk '{print $1}' "], shell=True).decode("utf-8"))
                volume = int(est * mask_vol)
                df[regionName] = volume
                print(regionName, ":", volume, "mm3")
    return df

def run_ICBM81(FLYWHEEL_BASE, WORK, OUTPUT_DIR, studyBrainReference, wm, wm_mask, df):
    print("Aligning white matter tracts to template...")
    atlas = (FLYWHEEL_BASE + "/app/templates/atlas/wm/ICBM-81")
    for region in os.listdir(atlas):
        f = os.path.join(atlas, region)
        # checking if it is a file
        if os.path.isfile(f):
            regionName = region.split(".")[0]
            print("ROI: ", regionName)  
            if regionName == "":
                continue
            else:
                # 2: Perform the warp on the individual brain image to align it to the template
                print("Warping...")
                MNI_WARP = (WORK + "/mni2bcp_1Warp.nii.gz")
                MNI_AFFINE = (WORK + "/mni2bcp_0GenericAffine.mat")
                MNIAligned = (WORK + "/" + regionName + "_Aligned.nii.gz")
                # Run registration
                subprocess.run(['antsApplyTransforms -d 3 -i ' + f + ' -r ' + studyBrainReference + ' -t ' + MNI_WARP + ' -t ' + MNI_AFFINE + ' -n GenericLabel -o ' + MNIAligned], shell=True, capture_output = True)
                subprocess.run(["fslmaths " + MNIAligned + " -mul " + wm_mask + " " + MNIAligned], shell=True, capture_output = True)	

                # Calculate volume
                est = float(subprocess.check_output(["fslstats " + wm + " -k " + MNIAligned + " -M | awk '{print $1}' "], shell=True).decode("utf-8"))
                mask_vol = float(subprocess.check_output(["fslstats " + wm + " -k " + MNIAligned + " -V | awk '{print $1}' "], shell=True).decode("utf-8"))
                volume = int(est * mask_vol)
                df[regionName] = volume
                print(regionName, ":", volume, "mm3")
    return df


def run_subcortical(FLYWHEEL_BASE, WORK, OUTPUT_DIR, studyBrainReference, gm, gm_mask, df):
    print("Aligning grey matter subcortical ROIs to template...")
    atlas = (FLYWHEEL_BASE + "/app/templates/atlas/gm/subcortical")
    for region in os.listdir(atlas):
        f = os.path.join(atlas, region)
        # checking if it is a file
        if os.path.isfile(f):
            regionName = region.split(".")[0]
            print("ROI: ", regionName)  
            if regionName == "":
                continue
            else:
                # 2: Perform the warp on the individual brain image to align it to the template
                print("Warping...")
                MNI_WARP = (WORK + "/mni2bcp_1Warp.nii.gz")
                MNI_AFFINE = (WORK + "/mni2bcp_0GenericAffine.mat")
                MNIAligned = (WORK + "/" + regionName + "_Aligned.nii.gz")

                # Run registration (subcortical ROIs require thresholding)
                subprocess.run(['antsApplyTransforms -d 3 -i ' + f + ' -r ' + studyBrainReference + ' -t ' + MNI_WARP + ' -t ' + MNI_AFFINE + ' -n GenericLabel -o ' + MNIAligned], shell=True, capture_output = True)
                subprocess.run(["fslmaths " + MNIAligned + " -thr 0.7 " + MNIAligned], shell=True, capture_output = True)	
                subprocess.run(["fslmaths " + MNIAligned + " -mul " + gm_mask + " " + MNIAligned], shell=True, capture_output = True)	
            
                # Calculate volume
                est = float(subprocess.check_output(["fslstats " + gm + " -k " + MNIAligned + " -M | awk '{print $1}' "], shell=True).decode("utf-8"))
                mask_vol = float(subprocess.check_output(["fslstats " + gm + " -k " + MNIAligned + " -V | awk '{print $1}' "], shell=True).decode("utf-8"))
                volume = int(est * mask_vol)
                df[regionName] = volume
                print(regionName, ":", volume, "mm3")
    return df

#  individualMaskedBrain  brainAffineField  brainInverseWarpField

def run_cortical(FLYWHEEL_BASE, WORK, OUTPUT_DIR, studyBrainReference, gm, gm_mask, df):
    print("Aligning grey matter cortical ROIs to subject...")
    atlas = (FLYWHEEL_BASE + "/app/templates/atlas/gm/cortical")
    for region in os.listdir(atlas):
        f = os.path.join(atlas, region)
        # checking if it is a file
        if os.path.isfile(f):
            regionName = region.split(".")[0]
            print("ROI: ", regionName)  
            if regionName == "":
                continue
            else:
                # 2: Perform the warp on the individual brain image to align it to the template
                print("Warping...")
                MNI_WARP = (WORK + "/mni2bcp_1Warp.nii.gz")
                MNI_AFFINE = (WORK + "/mni2bcp_0GenericAffine.mat")
                MNIAligned = (WORK + "/" + regionName + "_Aligned.nii.gz")
                individualAligned = (WORK + "/" + regionName + "_individualAligned.nii.gz")
                # Run registration
                # subprocess.run(["WarpImageMultiTransform 3 " + f + " " + MNIAligned + " -R " + studyBrainReference + " " + brainWarpField + " " + brainAffineField +" --use-BSpline"], shell=True, check=True)	
                subprocess.run(['antsApplyTransforms -d 3 -i ' + f + ' -r ' + studyBrainReference + ' -t ' + MNI_WARP + ' -t ' + MNI_AFFINE + ' -n GenericLabel -o ' + MNIAligned], shell=True, check=True)
                subprocess.run(['WarpImageMultiTransform 3 ' + MNIAligned + " " + individualAligned + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline")

                subprocess.run(["fslmaths " + MNIAligned + " -mul " + gm_mask + " " + MNIAligned], shell=True, check=True)	
            
                # Calculate volume
                est = float(subprocess.check_output(["fslstats " + gm + " -k " + MNIAligned + " -M | awk '{print $1}' "], shell=True).decode("utf-8"))
                mask_vol = float(subprocess.check_output(["fslstats " + gm + " -k " + MNIAligned + " -V | awk '{print $1}' "], shell=True).decode("utf-8"))
                volume = int(est * mask_vol)
                df[regionName] = volume
                print(regionName, ":", volume, "mm3")
    return df