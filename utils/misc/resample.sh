
path=/Users/nbourke/GD/atom/unity/fw-gears/fw-ants-vbm/app/templates

for tissue in `ls ${path}/atlas/BCP/gm/`
    do
    echo ${tissue} 
    mkdir -p ${path}/atlas/unity/gm/${tissue}/masks
    for roi in `ls ${path}/atlas/BCP/gm/${tissue}`
        do
        echo ${roi} 
        ResampleImageBySpacing 3 ${path}/atlas/BCP/gm/${tissue}/${roi} ${path}/atlas/unity/gm/${tissue}/${roi} 1 1 1 #1.5 1.5 1.5
        fslmaths ${path}/atlas/unity/gm/${tissue}/${roi} -thr 0.5 -bin ${path}/atlas/unity/gm/${tissue}/masks/${roi}
    done
done

for tissue in `ls ${path}/atlas/BCP/wm/`
    do
    echo ${tissue} 
    mkdir -p ${path}/atlas/unity/wm/${tissue}/masks
    for roi in `ls ${path}/atlas/BCP/wm/${tissue}`
        do
        echo ${roi} 
        ResampleImageBySpacing 3 ${path}/atlas/BCP/wm/${tissue}/${roi} ${path}/atlas/unity/wm/${tissue}/${roi} 1 1 1 #1.5 1.5 1.5
        fslmaths ${path}/atlas/unity/wm/${tissue}/${roi} -thr 0.5 -bin ${path}/atlas/unity/wm/${tissue}/masks/${roi}
    done
done



# mkdir -p ${path}/atlas/unity/wm/ICBM-81/
# for roi in `ls ${path}/atlas/BCP/wm/ICBM-81/`
#     do
#     echo ${roi} 
#     ResampleImageBySpacing 3 ${path}/atlas/BCP/wm/ICBM-81/${roi} ${path}/atlas/unity/wm/ICBM-81/${roi} 1.5 1.5 1.5
# done

# mkdir ${path}/atlas/unity/wm/ICBM-81/masks
# for roi in `ls ${path}/atlas/unity/wm/ICBM-81/`
#     do
#     echo ${roi} 
#     fslmaths ${path}/atlas/unity/wm/ICBM-81/${roi} -thr 0.5 -bin ${path}/atlas/unity/wm/ICBM-81/masks/${roi}
# done