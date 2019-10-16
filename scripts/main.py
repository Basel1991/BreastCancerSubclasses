import pandas as pd
import xlrd
import xlwt

import numpy as np
import matplotlib.pyplot as plt
import xlsxwriter

import os
import glob
import sys

import scipy.misc
from skimage import io
import warnings

import shutil
from functions.load import encoder
warnings.filterwarnings("ignore")
print(sys.executable)
pd.options.display.precision=5


#---------------------------------------------------------------------------------
# reading excel files first
study_path = '/home/basel/Datasets/OPTIMAM/METADATA/study_IMAGE.xlsx'
lesion_path = '/home/basel/Datasets/OPTIMAM/METADATA/lesion_IMAGE.xlsx'
NBSS_path = '/home/basel/Datasets/OPTIMAM/METADATA/NBSS.xlsx'


all_study = pd.read_excel(study_path)
all_lesion = pd.read_excel(lesion_path)
all_NBSS = pd.read_excel(NBSS_path)

print(len(all_study), ' studies')
print(len(all_lesion),' lesions')
print(len(all_NBSS), ' NBSS')

#---------------------------------------------------------------------------------filtering images and lesions

# setting the filtering rules
cond1 = all_study['PresentationIntentType']=='FOR PRESENTATION'
cond2 = all_study['ManufacturersModelName']=='Lorad Selenia'

cond3 = all_study['BatchID']==1
cond4 = all_study['Manufacturer']== 'HOLOGIC, Inc.'

cond5 = all_study['EstimatedRadiographicMagnificationFactor']==1.0
cond6 = all_study['XRayTubeCurrent']==100.0

filtered_studies = all_study[cond1 & cond2 & cond4& cond5& cond6]

print(len(filtered_studies), ' filtered images')

# filtering the lesions
image_ids = filtered_studies['ImageSOPIUID']

lesion_image_indices = all_lesion['ImageSOPIUID'].isin(image_ids)

filtered_lesions = all_lesion[lesion_image_indices]
print(len(all_lesion), 'all lesions', len(filtered_lesions), 'filtered lesions')

filtered_NBSS = all_NBSS[all_NBSS['LesionID'].isin(filtered_lesions['LesionID'])]
print(len(all_NBSS), ' all NBSS', len(filtered_NBSS), ' filtered NBSS')


#---------------------------------------------------------------------------------# Validating and saving lesions
# read lesion ids one by one
dst_folder = '/home/basel/Datasets/OPTIMAM2'
src_folder = '/home/basel/Datasets/OPTIMAM/Lesions/1Les'
counter, miss_counter, undefined_hor_counter = 0, 0, 0

for index in range(len(filtered_NBSS)):

    lesion_id = filtered_NBSS.iloc[index]['LesionID']

    record_of_interest = filtered_lesions[filtered_lesions['LesionID'] == lesion_id]
    batches, patients, image_ids = record_of_interest['BatchID'], record_of_interest['ClientID'], \
                                   record_of_interest['ImageSOPIUID']
    print('-' * 40)
    print('lesion ', lesion_id)

    # coding the subclass
    code = encoder(filtered_NBSS.iloc[index]['HER2ReceptorStatus'], filtered_NBSS.iloc[index]['HormoneERStatus'] \
                   , filtered_NBSS.iloc[index]['HormonePRStatus'])

    # if one hormone or more is/are undefined, skip the image
    if code==-1:
        undefined_hor_counter += 1
        continue

    dst_subfolder = os.path.join(dst_folder, str(code))

    for batch, patient, image_id in zip(batches, patients, image_ids):
        # print(batch, '\n', patient, '\n', image_id)

        src_file_prefix = '_'.join([str(batch), str(patient), image_id, str(lesion_id)])

        src_file = glob.glob(os.path.join(src_folder, src_file_prefix + '*'))

        # copy the lesion to the corresponding folder
        if len(src_file) > 0:
            for source in src_file:
                print(source, 'is being copied')
                shutil.copy(source, dst_subfolder)
                counter += 1
        else:
            print(src_file_prefix, ' unfound')
            miss_counter += 1

print('Completed: ', counter, 'missing: ', str(miss_counter), 'undefined hormone: ', undefined_hor_counter)


