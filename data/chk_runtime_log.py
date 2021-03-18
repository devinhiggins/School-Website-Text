import glob
from os import listdir, chdir
from os.path import join

repo_dir = '/Users/jhp/Projects/MSU/schooltext/data/Schools_by_State'

state_code = [
    'AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN',
    'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV',
    'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY']

for state_dir in listdir(repo_dir):
    if state_dir not in state_code:
        continue

    for log_dir in listdir(join(repo_dir, state_dir, 'result')):
        if not log_dir.startswith('log'):
            continue

        chdir(join(repo_dir, state_dir, 'result', log_dir))
        all_log_files = [i for i in glob.glob('run*.log*')]
        print('{} state - {}'.format(state_dir, all_log_files))
        with open(join(repo_dir, 'logs_per_state.log'), 'a') as wf:
            wf.write('{} state - {}'.format(state_dir, all_log_files))


        for logfile in all_log_files:
            with open(logfile, 'r') as rf:
                for line in rf:
                    if line.startswith('positive list:  []'):
                        # print('current line: {}'.format(line))
                        # print('next line: {}'.format(next(rf)))
                        with open(join(repo_dir, 'no_pos_records.log'), 'a') as wf:
                            wf.write('{},{},{},{}'.format(state_dir, log_dir, logfile, next(rf)))
