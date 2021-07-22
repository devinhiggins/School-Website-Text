import argparse
import errno
from os import strerror
from os.path import isfile, isdir, join
from datetime import datetime
import pandas as pd
from selenium import webdriver

from mission.check_mission_terms import check_mission_terms
from mission.predict_mission_stmt import predict_mission_stmt
from mission.candidate_urls import extract_candidate_urls

begin_time = datetime.now()  # record start time for the execution time calculation in the end
print("Start Time: {}".format(begin_time), flush=True)

parser = argparse.ArgumentParser()  # command-line arguments parsing module
parser.add_argument("data_dir", help="Path to data directory where input file reside")
parser.add_argument("source_data", help="CSV formatted source file")
parser.add_argument("model_dir", help="Path to model directory where trained OneClassSVM model reside")
args = parser.parse_args()

data_dir = args.data_dir
source_file = args.source_data
model_dir = args.model_dir

tfidf_model = 'tfidfvect.joblib'
ocsvm_model = 'oneclasssvm.joblib'
output_file = source_file[:-4] + '_Result.csv'

if not isdir(data_dir):  # check the validity of arguments
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), data_dir)
elif not isdir(model_dir):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), model_dir)
elif not isfile(join(data_dir, source_file)):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), source_file)
elif not isfile(join(model_dir, tfidf_model)):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), tfidf_model)
elif not isfile(join(model_dir, ocsvm_model)):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), ocsvm_model)

if not isfile(join(data_dir, output_file)):
    with open(join(data_dir, output_file), 'w') as wf:
        wf.write('SCH_NAME,WEBSITE,MISSION\n')
        wf.flush()

processed_schools = set()
try:
    # check if completed list exists and import data
    # in order to avoid re-processing same schools
    processed_csv = pd.read_csv(join(data_dir, output_file))
    for row in processed_csv.itertuples():
        processed_schools.add((row.SCH_NAME, row.WEBSITE))
    print("{} school has been processed previously".format(len(processed_schools)), flush=True)
except IOError:
    # if file does not exists then the program
    # catches the exception and moves on
    print("No school has been processed", flush=True)

data_csv = []
try:
    data_csv = pd.read_csv(join(data_dir, source_file))
except Exception:
    print("Importing school list to process failed exiting...", flush=True)
    exit(-1)

print("Processing {} schools start now".format(len(data_csv)), flush=True)

school_idx = 0
driver = webdriver.Firefox()

for row in data_csv.itertuples():
    school_idx += 1
    print('{}. {} - Processing Start'.format(school_idx, row.SCH_NAME), flush=True)
    if (row.SCH_NAME, row.WEBSITE) in processed_schools:
        print('{}. {} - Already Processed'.format(school_idx, row.SCH_NAME), flush=True)
        continue

    if row.WEBSITE == 'None':
        with open(join(data_dir, output_file), 'a') as af:
            print('{}. {} school URL was {} thus no mission stmt...'.format(school_idx, row.SCH_NAME, row.WEBSITE),
                  flush=True)
            af.write(row.SCH_NAME + ',' + row.WEBSITE + ',' + '' + '\n')
            af.flush()
            elapsed_time = datetime.now() - begin_time
            print("{}. Elapsed Time: {}".format(school_idx, elapsed_time), flush=True)
        continue

    href_urls = extract_candidate_urls(driver, row.WEBSITE)
    print('{} - Candidate URL extracted'.format(row.SCH_NAME), flush=True)
    print('{} URLs: {}'.format(row.SCH_NAME, href_urls), flush=True)
    candidate_text = predict_mission_stmt(href_urls, model_dir, tfidf_model, ocsvm_model)
    print('{} - Candidate Text Predicted'.format(row.SCH_NAME), flush=True)
    print('{} texts: {}'.format(row.SCH_NAME, candidate_text), flush=True)
    mission_results = check_mission_terms(candidate_text)
    print('{} - Mission Terms applied'.format(row.SCH_NAME), flush=True)
    print('{} - Text result: {}'.format(row.SCH_NAME, mission_results), flush=True)

    mission_stmt = ''
    tmp_pt = None
    for key, point in mission_results.items():
        if (tmp_pt is None) and (point != 0):
            tmp_pt = point
            mission_stmt += key + ' '
        elif (tmp_pt is None) and (point == 0):
            print("{} mission stmt not found...".format(row.SCH_NAME), flush=True)
            break
        elif (tmp_pt is not None) and (tmp_pt > point):
            # print("{} mission stmt is {}".format(row.SCH_NAME, mission_stmt), flush=True)
            break
        elif (tmp_pt is not None) and (tmp_pt <= point):
            tmp_pt = point
            mission_stmt += key + ' '
    with open(join(data_dir, output_file), 'a') as af:
        af.write(row.SCH_NAME + ',' + row.WEBSITE + ',' + mission_stmt + '\n')
        af.flush()
        print("{} mission stmt is {}".format(row.SCH_NAME, mission_stmt), flush=True)
        elapsed_time = datetime.now() - begin_time
        print("{}. Elapsed Time: {}".format(school_idx, elapsed_time), flush=True)

driver.quit()
print("{}. DONE".format(school_idx))
