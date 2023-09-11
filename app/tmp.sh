
atlasDir=/Users/nbourke/GD/atom/unity/fw-gears/fw-ants-vbm/app/templates/atlas/
input=/Users/nbourke/Desktop/hyperfine-vbm-0.1.1-64e78a4322539ce3f11df1b6/work/GM_gcorr.nii
base=/Users/nbourke/GD/atom/unity/fw-gears/fw-ants-vbm
ref=/Users/nbourke/GD/atom/unity/fw-gears/fw-ants-vbm/app/templates/18Month/BCP-18M-T2.nii.gz
wd=/Users/nbourke/GD/atom/unity/fw-gears/fw-ants-vbm/app/test/


# if output folder doesn't exist, create it
if [ ! -d ${wd}/atlas ]; then
    mkdir ${wd}/atlas
fi

# antsRegistrationSyNQuick.sh -f $input -m ${base}/app/templates/mni_icbm152_t1_tal_nlin_sym_09a.nii -t s -o ${wd}/atlas/mni2bcp_

# for region in `ls ${atlasDir}/gm/subcortical/`
#     do
#     echo ${region}
#     tmpName=`basename ${region}` 
#     regionName=`echo ${tmpName} | sed 's/.nii.gz//g'`
#     printf "region: ${regionName}\n"

#     antsApplyTransforms -d 3 -i ${atlasDir}/gm/subcortical/${region} -r ${input} -t ${wd}/atlas/mni2bcp_1Warp.nii.gz -t ${wd}/atlas/mni2bcp_0GenericAffine.mat -n GenericLabel -o ${wd}/atlas/BCP_${region}
# done

for ROI in `ls ${wd}/atlas/`;
    do
    printf "ROI: ${ROI}\n"
    meanIntesnity=`fslstats ${input} -k ${wd}/atlas/${ROI} -M | awk '{print $1}'`
    maskVolume=`fslstats ${input} -k ${wd}/atlas/${ROI} -V | awk '{print $1}'`
    ROI_Volume=`echo "${meanIntesnity} * ${maskVolume}" | bc`
    printf "ROI Volume: ${ROI_Volume}\n"
done