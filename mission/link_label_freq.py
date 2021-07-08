import time
import re
import pandas as pd
from os.path import join
from selenium import webdriver
from mission.candidate_urls import extract_candidate_urls


def link_label_freq(data_dir, sch_url_file, sch_name_file=None):
    """
    Extract all href link labels from school homepages and
    mission statement candidate pages to analyze frequency
    (i.e., occurence) so that we could derive filtering for
    certain link labels that occur frequently but not relevant

    Args:
        data_dir (str): Path to data sheets

        sch_url_file (str): CSV formatted file that contains school homepage URL
                            (both tableau file or NCES file works)

        sch_name_file (str): file that contains name of schools in which
                             user is interested (expects one name per line)

    Returns:
        dict[str:int]: Python dict that has link name and its frequency pair
    """
    start_time = time.time()
    print("Start Time: {}".format(start_time), flush=True)

    link_label_dict = {}
    sch_name_set = set()
    driver = webdriver.Firefox()
    school_idx = 0

    if sch_name_file is not None:  # if user passes specific interested school list
        with open(join(data_dir, sch_name_file), 'r') as rf:
            for line in rf:
                tmp_name = line.strip('\n')
                sch_name_set.add(tmp_name)

    url_csv = pd.read_csv(sch_url_file)  # read school URL csv file
    for row in url_csv.itertuples():  # iterate school URLs
        # if only specific set of schools are interested
        if (len(sch_name_set) != 0) and (row.SCH_NAME not in sch_name_set):
            continue

        school_idx += 1
        # process school homepage
        href_urls = extract_candidate_urls(driver, row.WEBSITE, vip_keys=None, label_dic=link_label_dict)
        # check number of candidate urls
        print('{} - {} links'.format(row.SCH_NAME, len(href_urls)))

        if school_idx % 10 == 0:  # everytime 10 schools are processed, write to a file and log execution time
            # this is due to significantly high number of exceptions/failures
            # Any port in a storm, you know.
            print('# of processed Schools: {} / Execution Time: {}'.format(school_idx, (time.time()-start_time)))
            with open(join(data_dir, 'href_link_freq.csv'), 'w') as cf:
                for k, v in link_label_dict.items():  # write label and its frequency to a CSV formatted file
                    prep_key = re.sub('[^A-Za-z0-9 ]+', '', k)
                    cf.write(prep_key + ',' + str(v) + '\n')

    driver.quit()
    return link_label_dict
