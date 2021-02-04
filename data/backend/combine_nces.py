import argparse
import csv
import pandas as pd
from os.path import join

keep_variables = {
    'SCHOOL_YEAR',
    'STATENAME',
    'SCH_NAME',
    'LEA_NAME',
    'ST_SCHID',
    'NCESSCH',
    'SCHID',
    'LSTREET1',
    'LSTREET2',
    'LSTREET3',
    'LCITY',
    'LSTATE',
    'LZIP',
    'WEBSITE',
    'SY_STATUS_TEXT',
    'SCH_TYPE_TEXT',
    'CHARTER_TEXT',
    'LEVEL'
}

# command-line arguments parsing module
parser = argparse.ArgumentParser()
parser.add_argument("data_dir", help="Path to data directory where input files reside")
parser.add_argument("source_data", help="CSV formatted finalized school URL list")
parser.add_argument("nces_data", help="CSV formatted NCES data")
args = parser.parse_args()

data_dir = args.data_dir
source_file = args.source_data
nces_file = args.nces_data

output_file = source_file.split('_')[0] + '_MongoDB.csv'

# read NCES data
nces_csv = pd.read_csv(join(data_dir, nces_file))
school_year_df = nces_csv['SCHOOL_YEAR']
statename_df = nces_csv['STATENAME']
sch_name_df = nces_csv['SCH_NAME']
lea_name_df = nces_csv['LEA_NAME']
st_schid_df = nces_csv['ST_SCHID']
ncessch_df = nces_csv['NCESSCH']
schid_df = nces_csv['SCHID']
lstreet1_df = nces_csv['LSTREET1']
lstreet2_df = nces_csv['LSTREET2']
lstreet3_df = nces_csv['LSTREET3']
lcity_df = nces_csv['LCITY']
lstate_df = nces_csv['LSTATE']
lzip_df = nces_csv['LZIP']
# website_df = nces_csv['WEBSITE']
sy_status_text_df = nces_csv['SY_STATUS_TEXT']
sch_type_text_df = nces_csv['SCH_TYPE_TEXT']
charter_text_df = nces_csv['CHARTER_TEXT']
level_df = nces_csv['LEVEL']

# read prediction result data
result_csv = pd.read_csv(join(data_dir, source_file), header=None)
res_sch_name_df = result_csv[0]
res_lcity_df = result_csv[1]
res_lzip_df = result_csv[2]
res_website_df = result_csv[3]

# write header
with open(join(data_dir, output_file), 'a', newline='') as wf:
    writer = csv.writer(wf)
    writer.writerow(['SCHOOL_YEAR', 'STATENAME', 'SCH_NAME', 'LEA_NAME', 'ST_SCHID', 'NCESSCH', 'SCHID', 'LSTREET1',
                     'LSTREET2', 'LSTREET3', 'LCITY', 'LSTATE', 'LZIP', 'WEBSITE', 'SY_STATUS_TEXT', 'SCH_TYPE_TEXT',
                     'CHARTER_TEXT', 'LEVEL'])

# website dataframe
# website_df = pd.DataFrame(columns=['WEBSITE'])

for idx in range(len(sch_name_df)):
    # find matching from result file and extract index
    website_idx = result_csv[(result_csv[0] == sch_name_df[idx]) & (result_csv[1] == lcity_df[idx]) &
                             (result_csv[2] == lzip_df[idx])].index[0]

    # append website url to dataframe
    # website_df = website_df.append({'WEBSITE': res_website_df[website_idx]}, ignore_index=True)

    # write to output file
    with open(join(data_dir, output_file), 'a', newline='') as wf:
        writer = csv.writer(wf)
        writer.writerow([school_year_df[idx], statename_df[idx], sch_name_df[idx], lea_name_df[idx], st_schid_df[idx],
                        ncessch_df[idx], schid_df[idx], lstreet1_df[idx], lstreet2_df[idx], lstreet3_df[idx],
                        lcity_df[idx], lstate_df[idx], lzip_df[idx], res_website_df[website_idx],
                        sy_status_text_df[idx], sch_type_text_df[idx], charter_text_df[idx], level_df[idx]])
