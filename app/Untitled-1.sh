
dir=/Users/nbourke/GD/atom/unity/fw-gears/fw-ants-vbm/app/templates/atlas/cortical
for file in `ls $dir`; 
    do
    prefix=`echo $file | cut -d'_' -f1`
    suffix=`echo $file | cut -d'_' -f4-`
    newname=${prefix}_${suffix}
    # print $newname
    mv $dir/$file $dir/$newname
done
