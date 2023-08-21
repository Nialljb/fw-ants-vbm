import flywheel
import os
import json


#  Module to identify the correct template use for the subject VBM analysis based on age at scan
#  Need to get subject identifiers from inside running container in order to find the correct template from the SDK

# Read config.json file
p = open('/flywheel/v0/config.json')
config = json.loads(p.read())

# Read API key in config file
api_key = (config['inputs']['api-key']['key'])
fw = flywheel.Client(api_key=api_key)

# Get the input file id
input_file_id = (config['inputs']['input']['hierarchy']['id'])
print("input_file_id is : ", input_file_id)
input_container = fw.get(input_file_id)

session_id = input_container.parents['session']
session_container = fw.get(session_id)
session_label = session_container.label
print("session label: ", session_label)

project_id = input_container.parents['project']
project = fw.get_project(project_id)

print("project label: ", project.label)
for session in project.sessions.iter():
    print(session.label)
# session_container = session_container.reload()
# # print(session_container.analyses)

# analyses = session_container.analyses
# print(analyses.analysis)

# for analysis in session_container.analyses():
#         print('%s: %s' % (analysis.id, analysis.label))



# # get the acquisition from the session
# for acq in session_container.acquisitions.iter():
#     # print(acq.label)
#     acq = acq.reload()
#     if 'T2' in acq.label and 'AXI' in acq.label: # restrict to T2 acquisitions
#         for file_obj in acq.files: # get the files in the acquisition
#             # Screen file object information & download the desired file
#             if file_obj['type'] == 'dicom':

#                 # Get DOB from dicom header
#                 try:
#                     dob = file_obj.info['PatientBirthDate']

#                 except:
#                     print("No DOB in dicom header & no age found")
#                     # Alternative workflow to get AGE from subject container??
#                     continue 
                            
#                 # Get series date from dicom header
#                 seriesDate = file_obj.info['SeriesDate']
#                 # print("seriesDate: ", seriesDate)
                
#                 # Calculate age at scan
#                 age = (datetime.strptime(seriesDate, '%Y%m%d')) - (datetime.strptime(dob, '%Y%m%d'))
#                 # Find the target template based on the session label
                
#                 age = age.days
#                 print("age: ", age)

            

#                 # Make sure age is positive
#                 if age < 0:
#                     age = age * -1

#                 # Find the target template based on the age at scan
#                 if age < 15:
#                     target_template = 'BCP-00M-T2.nii'
#                 if age < 45:
#                     target_template = 'BCP-01M-T2.nii'
#                 elif age < 75:
#                     target_template = 'BCP-02M-T2.nii'
#                 elif age < 105:
#                     target_template = 'BCP-03M-T2.nii' 
#                 elif age < 200:
#                     target_template = 'BCP-06M-T2.nii' 
#                 elif age < 400:
#                     target_template = 'BCP-12M-T2.nii'
#                 else:
#                     print("age is too old - out of expected range")
                
#                 print("target_template: ", target_template)
#                 # Pass this into main!!
                

#                 # Template = '/flywheel/v0/app/templates/'+target_template
#                 # print(Template)







#  THIS IS THE PART YOU WANT TO ADAPT TO GET AQUISITION FILES!!!


# import flywheel
# import pandas as pd
# from datetime import datetime

# fw = flywheel.Client()

# # First configure and get the project you'd like to examine:
# project_id = '<PROJECT_ID>'
# project = fw.get_project(project_id)

# # Now configure the gear you're looking for a successful run of.  For now we
# # won't worry about version, we're just interested in the gear name.
# gear = 'grp13-container-export'

# # Create a data dict:
# data_dict = {'subject':[],'session':[],'run':[],'status':[]}


# # Iterate over sessions
# for session in project.sessions.iter():

#     # Because we want information off the sessions's analyses, we need to reload
#     # The container to make sure we have all the metadata.
#     session = session.reload()

#     sub_label = session.subject.label
#     ses_label = session.label

#     # Any analyses on this session will be stored as a list:
#     analyses = session.analyses

#     # If there are no analyses containers, we know that this gear was not run
#     if len(analyses) == 0:
#         run = 'False'
#         status = 'NA'

#     else:

#         # Loop through the analyses
#         matches = [asys for asys in analyses if asys.gear_info.get('name') == gear]

#         # If there are no matches, the gear didn't run
#         if len(matches) == 0:
#             run = 'False'
#             status = 'NA'

#         # If there is one match, that's our target
#         elif len(matches) == 1:
#             run = 'True'
#             status = asys.job.get('state')

#         # If there are more than one matches (due to reruns), take the most recent run.
#         # This behavior may be modified to whatever suits your needs
#         else:
#             last_run_date = max([asys.created for asys in matches])
#             last_run_analysis = [asys for asys in matches if asys.created == last_run_date]

#             # There should only be one exact match
#             last_run_analysis = last_run_analysis[0]

#             run = 'True'
#             status = last_run_analysis.job.get('state')

#     # Populate our data dict - remember that each key in the data dict must be updated
#     # So that the length of our lists stays the same
#     data_dict['subject'].append(sub_label)
#     data_dict['session'].append(ses_label)
#     data_dict['run'].append(run)
#     data_dict['status'].append(status)

# # Now create a data frame
# df = pd.DataFrame.from_dict(data_dict)

# # Append a timestamp to our csv name so it won't overwrite anything when we upload it to flywheel
# time_fmt = '%m_%d_%Y-%H_%M_%S'
# time_string = datetime.now().strftime(time_fmt)
# csv_out = f'{gear}_RunReport_{time_string}.csv'

# df.to_csv(csv_out,index=False)

# project.upload_file(csv_out)

