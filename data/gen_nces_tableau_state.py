import glob
import pandas as pd
from os import listdir, chdir
from os.path import join

repo_dir = '/Users/jhp/Projects/MSU/schooltext/data/Schools_by_State'
output_dir = '/Users/jhp/Projects/MSU/schooltext/data/Final'

tableau_variables = [
    'SCHOOL_YEAR', 'STATENAME', 'SCH_NAME', 'LEA_NAME', 'ST_SCHID',
    'NCESSCH', 'SCHID', 'LSTREET1', 'LSTREET2', 'LSTREET3',
    'LCITY', 'LSTATE', 'LZIP', 'WEBSITE', 'SY_STATUS_TEXT',
    'SCH_TYPE_TEXT', 'CHARTER_TEXT', 'LEVEL']

state_code = [
    'AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN',
    'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV',
    'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY']

for state_dir in listdir(repo_dir):
    if state_dir not in state_code:
        continue

    chdir(join(repo_dir, state_dir, 'result'))
    all_result_file = [i for i in glob.glob('*{}'.format('_Result.csv'))]
    print(all_result_file)

    try:
        combined_result_csv = pd.concat([pd.read_csv(f, header=None, names=['SCH_NAME', 'LCITY', 'LZIP', 'WEBSITE'])
                                         for f in all_result_file], ignore_index=True)
        # print(combined_result_csv)
        print('{} state - {}'.format(state_dir, len(combined_result_csv)))
        # combined_result_csv.to_csv("temp.csv", index=False)
    except ValueError:
        print("ERROR: Check the result files list: {}".format(all_result_file))
        exit(-1)

    nces_file_name = state_dir + '_Schools_NCES.csv'
    nces_out_file = nces_file_name[:-4] + '_Done.csv'
    tableau_out_file = nces_file_name[:-9] + '_Tableau.csv'

    nces_csv = pd.read_csv(join(repo_dir, state_dir, nces_file_name), header=0)

    for row in nces_csv.itertuples():
        # print("The row website: {}".format(row.WEBSITE))
        try:
            website_idx = combined_result_csv[(combined_result_csv['SCH_NAME'] == row.SCH_NAME) &
                                              (combined_result_csv['LCITY'] == row.LCITY) &
                                              (combined_result_csv['LZIP'] == row.LZIP)].index[0]
        except IndexError:
            print(row.SCH_NAME, row.LCITY, row.LZIP)
            print(combined_result_csv[(combined_result_csv['SCH_NAME'] == row.SCH_NAME) &
                                      (combined_result_csv['LCITY'] == row.LCITY) &
                                      (combined_result_csv['LZIP'] == row.LZIP)])
            exit(-1)
        # print("Website Index: {}".format(website_idx))
        # print("Website Value: {}".format(combined_result_csv.at[website_idx, 'WEBSITE']))
        try:
            nces_csv.at[row.Index, 'WEBSITE'] = combined_result_csv.at[website_idx, 'WEBSITE']
        except ValueError:
            nces_csv['WEBSITE'] = nces_csv['WEBSITE'].astype(str)
            nces_csv.at[row.Index, 'WEBSITE'] = combined_result_csv.at[website_idx, 'WEBSITE']

    nces_csv.to_csv(join(output_dir, nces_out_file), index=False)
    nces_csv.to_csv(join(output_dir, tableau_out_file), index=False, columns=tableau_variables)
