import subprocess

def MNI2BCP(BCP, OUTPUT_DIR):
    MNI = '/flywheel/v0/app/templates/MNI152_T1_1mm_brain.nii.gz'
    subprocess.run(['antsRegistrationSyNQuick.sh -f ' + BCP + ' -m ' + MNI + ' -t s -o ' + OUTPUT_DIR + '/mniTobcp_'])

