import os
import subprocess
import pandas as pd


# assign directory
ROIs = '/Users/nbourke/GD/atom/unity/fw-gears/fw-ants-vbm/app/templates/subcortical/' 

# creating a dataframe
df = pd.DataFrame({'subject': ['beta'],
                   'session': [1]})

# iterate over files in
# that directory
for region in os.listdir(ROIs):
    f = os.path.join(ROIs, region)
    print(f)
#     # checking if it is a file
#     if os.path.isfile(f):
#         regionName = region.split(".")[0]
#         print(regionName)
                
#         est = 42 #float(subprocess.check_output(["fslstats " + gCorrectedWMSegmentation + " -k " + f + " -M | awk '{print $1}' "],shell=True).decode("utf-8"))

#         df[regionName] = est

# # test csv output
# project_path = '/Users/nbourke/'
# df = pd.DataFrame(df) 
# # df = pd.concat(df, axis=0, ignore_index=True)
# outdir = os.path.join(project_path, 'tmp_vbm_vol.csv')
# df.to_csv(outdir)