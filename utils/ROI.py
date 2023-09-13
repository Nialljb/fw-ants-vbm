import os
import subprocess

def run_jolly(FLYWHEEL_BASE, OUTPUT_DIR, studyBrainReference, brainWarpField, brainInverseWarpField, wm, wm_mask, df):
    print("Aligning white matter tracts to template...")
    atlas = (FLYWHEEL_BASE + "/app/templates/atlas/wm/MedicolegalTracts")
    for region in os.listdir(atlas):
        f = os.path.join(atlas, region)
        # checking if it is a file
        if os.path.isfile(f):
            regionName = region.split(".")[0]
            print(regionName)  
            if regionName == "":
                continue
            else:
                # 2: Perform the warp on the individual brain image to align it to the template
                print("Aligning ROI...")
                MNIAligned = (OUTPUT_DIR + "/" + regionName + "_Aligned.nii.gz")
                # Run registration
                subprocess.run(["WarpImageMultiTransform 3 " + f + " " + MNIAligned + " -R " + studyBrainReference + " " + brainWarpField + " " + brainInverseWarpField +" --use-BSpline"], shell=True, check=True)	
                subprocess.run(["fslmaths " + MNIAligned + " -mul " + wm_mask + " " + MNIAligned], shell=True, check=True)	

                # Calculate volume
                est = float(subprocess.check_output(["fslstats " + wm + " -k " + MNIAligned + " -M | awk '{print $1}' "],shell=True).decode("utf-8"))
                mask_vol = float(subprocess.check_output(["fslstats " + wm + " -k " + MNIAligned + " -V | awk '{print $1}' "],shell=True).decode("utf-8"))
                volume = int(est * mask_vol)
                df[regionName] = volume
    return df

def run_subcortical(FLYWHEEL_BASE, OUTPUT_DIR, studyBrainReference, brainWarpField, brainInverseWarpField, gm, gm_mask, df):
    print("Aligning white matter tracts to template...")
    atlas = (FLYWHEEL_BASE + "/app/templates/atlas/gm/subcortical")
    for region in os.listdir(atlas):
        f = os.path.join(atlas, region)
        # checking if it is a file
        if os.path.isfile(f):
            regionName = region.split(".")[0]
            print(regionName)  
            if regionName == "":
                continue
            else:
                # 2: Perform the warp on the individual brain image to align it to the template
                print("Aligning ROI...")
                MNIAligned = (OUTPUT_DIR + "/" + regionName + "_Aligned.nii.gz")
                # Run registration
                subprocess.run(["WarpImageMultiTransform 3 " + f + " " + MNIAligned + " -R " + studyBrainReference + " " + brainWarpField + " " + brainInverseWarpField +" --use-BSpline"], shell=True, check=True)	
                subprocess.run(["fslmaths " + MNIAligned + " -mul " + gm_mask + " " + MNIAligned], shell=True, check=True)	

                # Calculate volume
                est = float(subprocess.check_output(["fslstats " + gm + " -k " + MNIAligned + " -M | awk '{print $1}' "],shell=True).decode("utf-8"))
                mask_vol = float(subprocess.check_output(["fslstats " + gm + " -k " + MNIAligned + " -V | awk '{print $1}' "],shell=True).decode("utf-8"))
                volume = int(est * mask_vol)
                df[regionName] = volume
    return df