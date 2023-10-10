import os
import numpy as np
np.set_printoptions(precision=4, suppress=True)
import nibabel as nib

data_path = '/Users/nbourke/Desktop/'
example_ni1 = os.path.join(data_path, 'isotropicReconstruction_corrected_sbet_brain.nii.gz')
n1_img = nib.load(example_ni1)
n1_img

pixdim = (n1_img.header['pixdim'])

scaleFactor = pixdim[0] * pixdim[1] * pixdim[2]
print(scaleFactor)