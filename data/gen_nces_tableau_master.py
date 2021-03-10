import glob
import pandas as pd
from os import chdir

output_dir = '/Users/jhp/Projects/MSU/schooltext/data/Final'

chdir(output_dir)
all_tableau_file = [i for i in glob.glob('*{}'.format('_Tableau.csv'))]
all_nces_file = [i for i in glob.glob('*{}'.format('_NCES_Done.csv'))]

master_dic = {'Tableau': all_tableau_file, 'NCES': all_nces_file}

for key in master_dic.keys():
    try:
        combined_result_csv = pd.concat([pd.read_csv(f) for f in master_dic[key]], ignore_index=True)
        print('{} - Total records: {}'.format(key, len(combined_result_csv)))
        combined_result_csv.to_csv('US_Schools_' + key + '.csv', index=False)
    except ValueError:
        print("ERROR: Check the result files list: {}".format(master_dic[key]))
        exit(-1)
