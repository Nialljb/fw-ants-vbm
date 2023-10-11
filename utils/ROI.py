import os
import subprocess

def run_ICBM81(FLYWHEEL_BASE, WORK, antsImageAlign, individualMaskedBrain, wm, wm_mask, brainAffineField, brainInverseWarpField, df, Backup_df):
    print("Aligning white matter tracts to template...")
    atlas = (FLYWHEEL_BASE + "/app/templates/atlas/BCP/wm/ICBM-81")
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
                print("Back projecting ROI to subject space...")
                try:
                    ROIAligned = (WORK + "/" + regionName + "_Aligned.nii.gz")
                    # Run registration
                    subprocess.run([antsImageAlign + " " + f + " " + ROIAligned + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline"], shell=True, capture_output = True)
                    subprocess.run(["fslmaths " + ROIAligned + " -mul " + wm_mask + " " + ROIAligned], shell=True, check = True)	

                    # Calculate volume
                    est = float(subprocess.check_output(["fslstats " + wm + " -k " + ROIAligned + " -M | awk '{print $1}' "], shell=True).decode("utf-8"))
                    mask_vol = float(subprocess.check_output(["fslstats " + wm + " -k " + ROIAligned + " -V | awk '{print $1}' "], shell=True).decode("utf-8"))
                    volume = est * mask_vol * 1.5 * 1.5 * 1.5
                    df[regionName] = volume
                    print(regionName, ":", volume, "mm3")

                    Backup_df[regionName] = est

                except:
                    print("Error with ROI: ", regionName)
    return df, Backup_df

def run_subcortical(FLYWHEEL_BASE, WORK, antsImageAlign, individualMaskedBrain, gm, gm_mask, brainAffineField, brainInverseWarpField, df, Backup_df):
    print("Aligning grey matter subcortical ROIs to template...")
    atlas = (FLYWHEEL_BASE + "/app/templates/atlas/BCP/gm/subcortical")

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
                print("Back projecting ROI to subject space...")
                ROIAligned = (WORK + "/" + regionName + "_Aligned.nii.gz")
                try:
                    # Run registration (subcortical ROIs require thresholding)
                    subprocess.run([antsImageAlign + " " + f + " " + ROIAligned + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline"], shell=True, capture_output = True)
                    # subprocess.run(["fslmaths " + ROIAligned + " -thr 0.7 " + ROIAligned], shell=True, capture_output = True)	
                    subprocess.run(["fslmaths " + ROIAligned + " -mul " + gm_mask + " " + ROIAligned], shell=True, check = True)	
                
                    # Calculate volume
                    est = float(subprocess.check_output(["fslstats " + gm + " -k " + ROIAligned + " -M | awk '{print $1}' "], shell=True).decode("utf-8"))
                    mask_vol = float(subprocess.check_output(["fslstats " + gm + " -k " + ROIAligned + " -V | awk '{print $1}' "], shell=True).decode("utf-8"))
                    volume = est * mask_vol * 1.5 * 1.5 * 1.5
                    df[regionName] = volume
                    print(regionName, ":", volume, "mm3")

                    Backup_df[regionName] = est
                except:
                    print("Error with ROI: ", regionName)
    return df, Backup_df


def run_cortical(FLYWHEEL_BASE, WORK, antsImageAlign, individualMaskedBrain, gm, gm_mask, brainAffineField, brainInverseWarpField, df, Backup_df):
    print("Aligning grey matter cortical ROIs to subject...")
    atlas = (FLYWHEEL_BASE + "/app/templates/atlas/BCP/gm/cortical")
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
                print("Back projecting ROI to subject space...")
                try:
                    ROIAligned = (WORK + "/" + regionName + "_Aligned.nii.gz")
                    # Run registration
                    subprocess.run([antsImageAlign + " " + f + " " + ROIAligned + " -R " + individualMaskedBrain + " -i " + brainAffineField + " " + brainInverseWarpField + " --use-BSpline"], shell=True, capture_output = True)
                    subprocess.run(["fslmaths " + ROIAligned + " -thr 0.7 " + ROIAligned], shell=True, capture_output = True)
                    subprocess.run(["fslmaths " + ROIAligned + " -mul " + gm_mask + " " + ROIAligned], shell=True, check=True)	
                
                    # Calculate volume
                    est = float(subprocess.check_output(["fslstats " + gm + " -k " + ROIAligned + " -M | awk '{print $1}' "], shell=True).decode("utf-8"))
                    mask_vol = float(subprocess.check_output(["fslstats " + gm + " -k " + ROIAligned + " -V | awk '{print $1}' "], shell=True).decode("utf-8"))
                    volume = est * mask_vol * 1.5 * 1.5 * 1.5
                    df[regionName] = volume
                    print(regionName, ":", volume, "mm3")
                    Backup_df[regionName] = est
                except:
                    print("Error with ROI: ", regionName)
    return df, Backup_df