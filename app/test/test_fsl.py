import os, sys, subprocess

def test_fsl():
    # import shell environment variable
    
    # check if it is set to NIFTI_GZ
    try:
        TEST_FSL = os.environ["FSLOUTPUTTYPE"]
        if TEST_FSL == "NIFTI_GZ":
            print("FSL output type is set to NIFTI_GZ")
    except:
        print("FSL output type is not set to NIFTI_GZ")
        print("running FSL config file")
        
        os.system(" . $FSLDIR/etc/fslconf/fsl.sh")

        # fslConfig = subprocess.run(["chmod +wrx $FSLDIR/etc/fslconf/fsl.sh; . $FSLDIR/etc/fslconf/fsl.sh"], shell=True, capture_output=True, check=True)
        # print(fslConfig)
        # fslConfig

        subprocess.run(["echo $FSLOUTPUTTYPE"],
                            shell=True,
                            check=True)

        if os.system("echo $FSLOUTPUTTYPE") == "NIFTI_GZ":
            print("FSL output type is now set to NIFTI_GZ")
        else:
            print("FSL output type is still not set to NIFTI_GZ")
            print("Exiting...")
            sys.exit(1)

