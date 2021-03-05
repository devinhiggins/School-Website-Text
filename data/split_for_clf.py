from os import listdir
from os.path import join

import pandas as pd

source_dir = '/Users/jhp/Projects/MSU/schooltext/data/NCES/19-20/Temp'

for input_file in listdir(source_dir):
    if not input_file.endswith('.csv'):
        continue

    number_lines = sum(1 for row in (open(join(source_dir, input_file))))
    print(number_lines)
    row_limit = 250

    for idx in range(1, number_lines, row_limit):
        df = pd.read_csv(join(source_dir, input_file), header=None, usecols=[4, 23, 25], nrows=row_limit, skiprows=idx)

        output_csv = input_file[:-8] + str(idx+249) + '.csv'
        df.to_csv(join(source_dir, output_csv), index=False, header=False, mode='a', chunksize=row_limit)
