import csv
from os.path import join

nces_dir = "/Users/jhp/Projects/MSU/schooltext/data/NCES/19-20/Temp"
nces_file = "ccd_sch_029_1920_w_0a_040420.csv"

with open(join(nces_dir, nces_file), encoding='ISO8859') as rf:
    nces_csv = csv.DictReader(rf)
    outputs = {}
    for row in nces_csv:
        state = row['LSTATE']
        if state not in outputs:
            fout = open(join(nces_dir, '{}_Schools_NCES.csv'.format(state)), 'w')
            dw = csv.DictWriter(fout, fieldnames=nces_csv.fieldnames)
            dw.writeheader()
            outputs[state] = fout, dw
        outputs[state][1].writerow(row)

    for fout, _ in outputs.values():
        fout.close()
