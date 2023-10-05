import flywheel
import os
import json
import pandas as pd
from datetime import datetime
import re
import subprocess

#  Module to identify the correct template use for the subject VBM analysis based on age at scan
#  Need to get subject identifiers from inside running container in order to find the correct template from the SDK

def get_demo():

    # Read config.json file
    p = open('/flywheel/v0/config.json')
    config = json.loads(p.read())

    # Read API key in config file
    api_key = (config['inputs']['api-key']['key'])
    fw = flywheel.Client(api_key=api_key)
    gear = 'sbet'
    
    # Get the input file id
    input_file_id = (config['inputs']['input']['hierarchy']['id'])
    print("input_file_id is : ", input_file_id)
    input_container = fw.get(input_file_id)

    # Get the session id from the input file id
    # & extract the session container
    session_id = input_container.parents['session']
    session_container = fw.get(session_id)
    session = session_container.reload()
    print("subject label: ", session.subject.label)
    print("session label: ", session.label)
    session_label = session.label
    subject_label = session.subject.label

    #  -----------------  Get the hd-bet output  -----------------  #

    # Any analyses on this session will be stored as a list:
    analyses = session.analyses
    # print(analyses)

    # If there are no analyses containers, we know that this gear was not run
    if len(analyses) == 0:
        run = 'False'
        status = 'NA'
        print('No analysis containers')
    else:

        matches = [asys for asys in analyses if asys.gear_info.get('name') == gear]
        # print(matches)
        # If there are no matches, the gear didn't run
        if len(matches) == 0:
            run = 'False'
            status = 'NA'
        # If there is one match, that's our target
        elif len(matches) == 1:
            run = 'True'
            status = matches[0].job.get('state')
            # print(status)
            
            for file in matches[0].files:                
                if file.name == 'isotropicReconstruction_corrected_sbet_mask.nii.gz':
                    brain_mask = file
                    print("Found ", file.name)

                    download_dir = ('/flywheel/v0/input/input/')
                    if not os.path.exists(download_dir):
                        os.mkdir(download_dir)
                    download_path = download_dir + '/' + file.name
                    file.download(download_path)

        # If there are more than one matches (due to reruns), take the most recent run.
        # This behavior may be modified to whatever suits your needs
        else:
            last_run_date = max([asys.created for asys in matches])
            last_run_analysis = [asys for asys in matches if asys.created == last_run_date]

            # There should only be one exact match
            last_run_analysis = last_run_analysis[0]

            run = 'True'
            status = last_run_analysis.job.get('state')

            for file in last_run_analysis.files:
                # print(file)                
                if file.name == 'isotropicReconstruction_corrected_sbet_mask.nii.gz':
                    brain_mask = file
                    print("Found ", file.name)

                    download_dir = ('/flywheel/v0/input/input/')
                    if not os.path.exists(download_dir):
                        os.mkdir(download_dir)
                    download_path = download_dir + '/' + file.name
                    file.download(download_path)

    # -------------------  Get the subject age & matching template  -------------------  #

    # get the T2w axi dicom acquisition from the session
    # Should contain the DOB in the dicom header
    # Some projects may have DOB removed, but may have age at scan in the subject container

    for acq in session_container.acquisitions.iter():
        # print(acq.label)
        acq = acq.reload()
        if 'T2' in acq.label and 'AXI' in acq.label and 'Segmentation' not in acq.label: 
            for file_obj in acq.files: # get the files in the acquisition
                # Screen file object information & download the desired file
                if file_obj['type'] == 'dicom':
                    
                    dicom_header = fw._fw.get_acquisition_file_info(acq.id, file_obj.name)

                    if 'PatientSex' in dicom_header.info:
                        PatientSex = dicom_header.info["PatientSex"]
                    else:
                        PatientSex = "NA"
                
                    # print("PatientSex: ", PatientSex)

                    if 'PatientBirthDate' in dicom_header.info:
                        # Get dates from dicom header
                        dob = dicom_header.info['PatientBirthDate']
                        seriesDate = dicom_header.info['SeriesDate']
                        # Calculate age at scan
                        age = (datetime.strptime(seriesDate, '%Y%m%d')) - (datetime.strptime(dob, '%Y%m%d'))
                        age = age.days
                    elif session.age != None: 
                        # 
                        print("Checking session infomation label...")
                        # print("session.age: ", session.age) 
                        age = int(session.age / 365 / 24 / 60 / 60) # This is in seconds
                    elif 'PatientAge' in dicom_header.info:
                        print("No DOB in dicom header or age in session info! Trying PatientAge from dicom...")
                        age = dicom_header.info['PatientAge']
                        # Need to drop the 'D' from the age and convert to int
                        age = re.sub('\D', '', age)
                        age = int(age)
                    else:
                        print("No age at scan in session info label! Ask PI...")
                        age = 0

                    if age == 0:
                        print("No age at scan - skipping")
                        exit(1)
                    # Make sure age is positive
                    elif age < 0:
                        age = age * -1
                    # print("age: ", age)
        
    target_template = '12Month'
    # print("target_template: ", target_template)

    Template = '/flywheel/v0/app/templates/'+ target_template
    print(Template)
    # os.system('cp -r '+Template+' /flywheel/v0/work/')
    subprocess.run(['cp -r '+Template+' /flywheel/v0/work/'], shell=True, check=True)
    print("Demographics: ", subject_label, session_label, target_template, age, PatientSex)
    return subject_label, session_label, target_template, age, PatientSex