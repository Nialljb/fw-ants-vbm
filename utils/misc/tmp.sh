
# Drop Aligned suffix from files
wd=/Users/nbourke/GD/atom/unity/fw-gears/fw-ants-vbm/app/templates/atlas/BCP
for tissue in `ls $wd`;
    do
    for masks in `ls $wd/$tissue`;
        do
        for roi in `ls $wd/$tissue/$masks`;
            do
            # echo $wd/$tissue/$masks/$roi
            # echo $wd/$tissue/$masks/${roi%_Aligned*}.nii.gz
            mv $wd/$tissue/$masks/$roi $wd/$tissue/$masks/${roi%_Aligned*}.nii.gz
        done       
    done
done

