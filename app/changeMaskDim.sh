
# Purpose: change the dimension of the ROIs in MNI to the age matched template
base=/flywheel/v0
wd=${base}/work
ref=${1}
 
#  ------------------  ANTS registration ------------------

echo "registering regions of interest in MNI space to individual..."

# calculate the transform from MNI to the individual
antsRegistrationSyNQuick.sh -f ${ref} -m ${base}/app/templates/mni_icbm152_t1_tal_nlin_sym_09a.nii -t s -o ${wd}/mni2bcp_

# Loop through all the atlases

for tissueDir in `ls ${base}/app/templates/atlas`
    do
    if [ tissueDir == "gm"] ; then
        tissue="gm"
    elif [ tissueDir == "wm" ] ; then
        tissue="wm"

    for atlasDir in `ls ${tissueDir}`
        do
        atlas=`basename ${atlasDir}`
        echo "registering ${atlas} masks..."

        # if output folder doesn't exist, create it
        if [ ! -d ${wd}/atlas/${tissue}/${atlas} ]; then
            mkdir ${wd}/atlas/${tissue}/${atlas}
        fi

        # Register all the ROIs to the reference
        for roi in `ls ${atlasDir}`;
            do
            # echo ${roi}
            input=`basename ${roi}`
            # input=`echo ${input} | sed 's/MNI_//g'`
            # echo ${input}
            antsApplyTransforms -d 3 -i ${roi} -r ${ref} -t ${wd}/mni2bcp_1Warp.nii.gz -t ${wd}/mni2bcp_0GenericAffine.mat -n GenericLabel -o ${wd}/atlas/${tissue}/${atlas}/BCP_${input}
        done
    done
done


