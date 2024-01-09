import numpy as np
np.set_printoptions(precision=4, suppress=True)
import nibabel as nib

def scaleFactor(input):
    """Calculates the scale factor for the input image
    Parameters
    ----------
    input : str
        Path to the input image
    Returns
    -------
    scaleFactor : float
        Scale factor to correct output volume estimates
    """
    n1_img = nib.load(input)
    pixdim = (n1_img.header['pixdim'])

    print("pixdim is: ", pixdim)
    scaleFactor = pixdim[1] * pixdim[2] * pixdim[3]
    # 0 index may be wrong

    print("scaleFactor is: ", scaleFactor)
    print("1.5mm^3 is: ", 1.5*1.5*1.5)
    return scaleFactor