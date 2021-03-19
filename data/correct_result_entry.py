import glob
from os import chdir
from os.path import join
import pandas as pd

repo_dir = '/Users/jhp/Projects/MSU/schooltext/data/Schools_by_State'
source_log_file = 'no_pos_records.csv'
state_code = 'PR'

chdir(join(repo_dir, state_code, 'result'))
all_result_file = [i for i in glob.glob('*{}'.format('_Result.csv'))]
print('all result files: {}'.format(all_result_file))

log_csv = pd.read_csv(join(repo_dir, source_log_file))
print(log_csv[log_csv['STATE'] == state_code].count())

match_count = 0
for result_file in all_result_file:
    result_csv = pd.read_csv(result_file, header=None, names=['SCH_NAME', 'LCITY', 'LZIP', 'WEBSITE'])
    mod_flag = False
    print('File: ', result_file)

    for row in result_csv.itertuples():
        # print('Result CSV Row: {}, {}, {}'.format(row.SCH_NAME, row.LCITY, row.LZIP))
        match_df = log_csv.loc[(log_csv['SCH_NAME'] == row.SCH_NAME) & (log_csv['LCITY'] == row.LCITY)
                               & (log_csv['LZIP'] == row.LZIP)]

        if len(match_df) == 0:
            # print("Not matched")
            continue
        else:
            print("Matched: ", match_df[['SCH_NAME', 'LCITY', 'LZIP']])
            result_csv.at[row.Index, 'WEBSITE'] = 'None'
            mod_flag = True
            match_count += 1

    if mod_flag is True:
        result_csv.to_csv(join(repo_dir, state_code, 'result', result_file), index=False, header=False)

print('Match Count: ', match_count)
