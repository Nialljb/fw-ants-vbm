import subprocess

def resamplingTemplate(studyBrainReference, grayPrior, whitePrior, csfPrior, WORK):
    resampledTemplate = (WORK + '/resampled_template.nii.gz')
    resampledGray = (WORK + '/resampled_gray.nii.gz')
    resampledWhite = (WORK + '/resampled_white.nii.gz')
    resampledCSF = (WORK + '/resampled_csf.nii.gz')

    subprocess.run(['ResampleImageBySpacing 3 ' + studyBrainReference + resampledTemplate + ' 1.5 1.5 1.5'], shell=True, capture_output = True)
    subprocess.run(['ResampleImageBySpacing 3 ' + grayPrior + resampledGray + ' 1.5 1.5 1.5'], shell=True, capture_output = True)
    subprocess.run(['ResampleImageBySpacing 3 ' + whitePrior + resampledWhite + ' 1.5 1.5 1.5'], shell=True, capture_output = True)
    subprocess.run(['ResampleImageBySpacing 3 ' + csfPrior + resampledCSF + ' 1.5 1.5 1.5'], shell=True, capture_output = True)
    
    return resampledTemplate, resampledGray, resampledWhite, resampledCSF

def MNI2BCP(BCP, WORK):
    MNI = '/flywheel/v0/app/templates/MNI152_T1_1mm_brain.nii.gz'
    OUT = (WORK + '/mni2bcp_')
    OUTPUT_DEBUG = '/flywheel/v0/output/mni2bcp_'

    print('BCP: ' + BCP)
    print('MNI: ' + MNI)
    print('OUT: ' + OUT)
    subprocess.run(['antsRegistrationSyNQuick.sh -f ' + BCP + ' -m ' + MNI + ' -t s -o ' + OUTPUT_DEBUG], shell=True, capture_output = True)

