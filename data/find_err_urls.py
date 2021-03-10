from os import listdir
from os.path import join
import csv

repo_dir = '/data/Schools_by_State'
state_code = [
    'AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN',
    'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV',
    'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY']

for state_dir in listdir(repo_dir):
    if state_dir not in state_code:
        continue
    for filename in listdir(join(repo_dir, state_dir, 'result')):
        if not filename.endswith('_Result.csv'):
            continue
        with open(join(repo_dir, state_dir, 'result', filename)) as f:
            reader = csv.reader(f)
            fields = 4
            for row in reader:
                if len(row) != fields:
                    print("{} file {}".format(filename, row))
                    with open(join(repo_dir, 'error_records.txt'), 'a') as wf:
                        wf.write("{} file {}\n".format(filename, row))
