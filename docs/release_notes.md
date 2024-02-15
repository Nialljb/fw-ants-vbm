# Release notes


15/02/2024

The values for MNI template are higher than expected. 

    wm_vol	gm_vol	csf_vol	icv_vol
GE	498	738	201	1437
HFC	408	662	189	1260
HFE	394	622	184	1200
                
HFC-MNI	649	1067 418 2134



Harcoded to expect 1.5mm^3 dimensions in the volume estimation calculation. The original reconstructions warped subjects to 0.8mm to match template. This was changed as it didn't make much sense as the best hyperfine resoloution was 1.5mm and was taking extra computational time. 
- vbm run on this original reconstructions will have a massivly overinflated value. 
- Calculating the mean intensity by the GM/WM masks provide sensible results (assumption of 1mm^3?)
- Calculating the mean intensity by the GM/WM masks by the dimensions provides low results (is this a more correct calculation)
- Have made a function in utils that could be used to identify the pixel dimensions and use this to calculate the scaling factor