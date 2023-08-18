import flywheel
import os
import pandas as pd
from pathlib import Path
import pathvalidate as pv
from datetime import datetime

#  Module to identify the correct template use for the subject VBM analysis based on age at scan
#  Need to get subject identifiers from inside running container in order to find the correct template from the SDK

# Flywheel API Key
api_key = os.environ.get('FW_CLI_API_KEY')
fw = flywheel.Client(api_key=api_key)


# Get the project - how inside running container?
group_name =  #"global_map"
project_name = # "Malawi (REVAMP)"
project = fw.lookup(f"{group_name}/{project_name}")


# Iterate through all subjects in the project and find the T2 acquisitions
for subject in project.subjects.iter():
    
    # clear inputs for next subject
    inputs = {}
    for session in subject.sessions.iter():
        session = session.reload()
        print("parsing... ", subject.label, session.label)

        # Look at every acquisition in the session
        for acq in session.acquisitions.iter():
            acq = acq.reload()
            for file_obj in acq.files:
                # We only want anatomical Nifti's              
                if file_obj.type == 'nifti' and 'T2' in file_obj.name and 'AXI' in file_obj.name:           
                    input_label = 'axi'
                    inputs[input_label] = file_obj
                if file_obj.type == 'nifti' and 'T2' in file_obj.name and 'COR' in file_obj.name:           
                    input_label = 'cor'
                    inputs[input_label] = file_obj
                if file_obj.type == 'nifti' and 'T2' in file_obj.name and 'SAG' in file_obj.name:           
                    input_label = 'sag'
                    inputs[input_label] = file_obj

                # Get DOB from dicom header and calculate age at scan to determine target template
                if file_obj.type == 'dicom' and 'T2' in file_obj.name and 'AXI' in file_obj.name:

                    # Get DOB from dicom header
                    try:
                        dob = file_obj.info['PatientBirthDate']
                    except:
                        print("No DOB in dicom header")
                        print("Adding to missing report...")
                        report['subject'].append(subject.label)
                        continue
                    
                    # print("dob: ", dob)
                
                    # Get series date from dicom header
                    seriesDate = file_obj.info['SeriesDate']
                    # print("seriesDate: ", seriesDate)
                    
                    # Calculate age at scan
                    age = (datetime.strptime(seriesDate, '%Y%m%d')) - (datetime.strptime(dob, '%Y%m%d'))
                    # Find the target template based on the session label
                    age = age.days
                    # print("age: ", age)

                    # Make sure age is positive
                    if age < 0:
                        age = age * -1

                    # Find the target template based on the age at scan
                    if age < 15:
                        target_template = 'BCP-00M-T2.nii'
                    if age < 45:
                        target_template = 'BCP-01M-T2.nii'
                    elif age < 75:
                        target_template = 'BCP-02M-T2.nii'
                    elif age < 105:
                        target_template = 'BCP-03M-T2.nii' 
                    elif age < 200:
                        target_template = 'BCP-06M-T2.nii' 
                    elif age < 400:
                        target_template = 'BCP-12M-T2.nii'
                    else:
                        print("age is too old - out of expected range")

                    # print("target_template: ", target_template)

