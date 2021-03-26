import argparse
import errno
import os
import time
import pandas as pd
from contextlib import contextmanager
from os.path import join, isdir, isfile
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException

state_code = [
    'AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN',
    'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY',
    'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY', 'US']


# code for selenium browser to wait for complete loading
def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 3:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception('Timeout waiting for {}'.format(condition_function.__name__))


@contextmanager
def wait_for_page_load(browser):
    old_page = browser.find_element_by_tag_name('html')

    yield

    def page_has_loaded():
        new_page = browser.find_element_by_tag_name('html')
        return new_page.id != old_page.id

    wait_for(page_has_loaded)


def check_completed_list(repo_dir, state):
    """
        check webpages that were previously dumped
        Args:
            repo_dir (str) : Absolute path to repository directory
            where the runtime log resides

            state (str) : state code (for entire data, it is 'US')
        Returns:
            completed_set (set) : completed school tuples set (tuple: SCH_NAME, LCITY, LZIP)
    """
    completed_set = set()
    try:
        with open(join(repo_dir, state+'_dumpcomp.log'), 'r') as rf:
            for line in rf:
                dumped_school = line.strip('\n').split(',')
                completed_set.add((dumped_school[0], dumped_school[1], dumped_school[2]))
    except IOError:
        print("Nothing completed previously")
        pass

    return completed_set


def isdumped(sch_tuple, completed_set):
    # checks tuple existence in the completed_set
    return True if sch_tuple in completed_set else False


def get_homepage_dump(repo_dir, out_dir, state='US'):
    """
        iterate school CSV file, open its homepage URL and save it as a HTML file
        Args:
            repo_dir (str) : Absolute path to repository directory
            where the school CSV file and previous runtime log resides

            out_dir (str) : Absolute path to output directory
            where the homepage dumps will reside

            state (str) : Two-Letter State Abbreviations (for entire data, it is 'US')
    """
    if state in state_code:
        source_file = join(repo_dir, state+'_Schools_Tableau.csv')
    else:
        print("Invalid state code {} submitted!".format(state))
        return

    completed_set = check_completed_list(repo_dir, state)

    source_csv = pd.read_csv(source_file)
    driver = webdriver.Firefox()

    for row in source_csv.itertuples():
        if isdumped((row.SCH_NAME, row.LCITY, row.LZIP), completed_set):
            continue

        try:
            with wait_for_page_load(driver):
                driver.get(row.WEBSITE)
        except TimeoutException:
            print("Timeout Error while loading {} skipping...".format(row.WEBSITE))
            continue
        except UnexpectedAlertPresentException:
            print("{} - UnexpectedAlertPresent".format(row.WEBSITE))
            try:
                time.sleep(10)
                alert = driver.switch_to.alert
                alert.accept()
            except NoAlertPresentException:
                print("{} - NoAlertPresentException".format(row.WEBSITE))
                time.sleep(10)

        with open(join(repo_dir, state+'_dumpcomp.log'), 'a') as wf:
            wf.write(row.SCH_NAME + ',' + row.LCITY + ',' + str(row.LZIP) + '\n')

        output_file = row.SCH_NAME + '_' + row.LCITY + '_' + str(row.LZIP) + '.html'
        with open(join(out_dir, output_file), 'w') as wf:
            wf.write(driver.page_source)
            wf.flush()

    driver.quit()


if __name__ == '__main__':
    # command-line arguments parsing module
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_dir", help="Path to data directory where source csv file reside")
    parser.add_argument("out_dir", help="Path to webpage dump/save directory")
    parser.add_argument("state", nargs='?', default='US', help="Two-Letter State Abbreviations (default: US)")
    args = parser.parse_args()

    # check the directory and source file
    # raise exception if not found
    if not isdir(args.repo_dir):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.repo_dir)
    if not isdir(args.out_dir):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.out_dir)
    if not isfile(join(args.repo_dir, args.state+'_Schools_Tableau.csv')):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.state+'_Schools_Tableau.csv')
    # execute page dump
    get_homepage_dump(args.repo_dir, args.out_dir, args.state)
