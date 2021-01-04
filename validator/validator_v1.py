import argparse
import sys
import time
import pandas as pd
import csv
import errno
from contextlib import contextmanager
from os import strerror
from os.path import join, isdir, isfile
from tkinter import messagebox, Tk, Label
from tkinter.ttk import Button
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

"""
    Validation Tool

    Args:
        data_dir (str) : Absolute path to data directory where 
            input CSV file resides. 

            True Positive list will be generated here (if it does not exist)
            in the form of "[source file name]_TP.csv"

            False Positive list will be generated here (if it does not exist)
            in the form of [source file name]_FP.csv

        source_data (str) : Name of CSV formatted source file from Classification Tool
            CSV file is expected to have NO HEADER and adhere 
            to following format: [School Name],[City],[zipcode],[Homepage URL]  
"""

# command-line arguments parsing module
parser = argparse.ArgumentParser()
parser.add_argument("data_dir", help="Path to data directory where input source file reside")
parser.add_argument("source_data", help="CSV formatted source file (output of the classification tool)")
args = parser.parse_args()

data_dir = args.data_dir
source_file = args.source_data

# check the directory and source file
# raise exception if not found
if not isdir(data_dir):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), data_dir)
if not isfile(join(data_dir, source_file)):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), source_file)

tp_schools_file = join(data_dir, source_file[:-4] + '_TP.csv')
fp_schools_file = join(data_dir, source_file[:-4] + '_FP.csv')

input_csv = pd.read_csv(join(data_dir, source_file), header=None)

school = input_csv[0]
city = input_csv[1]
zipcode = input_csv[2].astype(str)
urls = input_csv[3]
query = school + ', ' + city + ', ' + zipcode

index = 0
processed_schools = set()
# check if TP & FP exists from previous run
try:
    with open(tp_schools_file, 'r') as rf:
        line_no = 0
        for line in rf:
            line_no += 1
            tp_school = line.strip('\n').split(',')
            processed_schools.add((tp_school[0], tp_school[1], tp_school[2]))
        print("{} TP records have been done previously".format(line_no))
except IOError:
    # if file does not exists then the program
    # catches the exception and moves on
    print("TP not-completed previously")
    pass
try:
    with open(fp_schools_file, 'r') as rf:
        line_no = 0
        for line in rf:
            line_no += 1
            fp_school = line.strip('\n').split(',')
            processed_schools.add((fp_school[0], fp_school[1], fp_school[2]))
        print("{} FP records have been done previously".format(line_no))
except IOError:
    # if file does not exists then the program
    # catches the exception and moves on
    print("FP not-completed previously")
    pass

driver = webdriver.Firefox()


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


def is_processed(school_name, school_city, school_zipcode):
    # check if this school has been processed
    return True if (school_name, school_city, school_zipcode) in processed_schools else False


def append_records(filename):
    with open(filename, 'a', newline='') as fw:
        writer = csv.writer(fw)
        writer.writerow([school[index], city[index], zipcode[index], urls[index]])


def next_url():
    global index
    if index < len(urls) - 1:  # continue as normal if in parameter
        index += 1  # update index we are on
        query_label.config(text='{}'.format(query[index]))

        while is_processed(school[index], city[index], zipcode[index]):
            # check if the school has been processed already
            if index < len(urls) - 1:
                # iterate to find school that has not been processed yet
                index += 1
            else:
                # no more entries / prevent index out of range
                messagebox.showinfo('Attention', 'No more entries, closing program')
                quit_click()
        # open url in the browser
        try:
            with wait_for_page_load(driver):
                driver.get('{}'.format(urls[index]))
            time.sleep(3)
        except TimeoutException:
            print("Timeout Error wait and try again!")
            time.sleep(10)
            with wait_for_page_load(driver):
                driver.get('{}'.format(urls[index]))
            time.sleep(3)
        return index  # remember our index

    if (index + 1) >= len(urls):  # this is a check if there are any more entries
        messagebox.showinfo('Attention', 'No more entries, closing program')
        quit_click()


def yes_click():
    # mark true positive
    append_records(tp_schools_file)
    next_url()


def no_click():
    # mark false positive
    append_records(fp_schools_file)
    next_url()


def quit_click():  # closes out the application
    driver.quit()
    sys.exit()


while is_processed(school[index], city[index], zipcode[index]):
    # check if the school has been processed already
    if index < len(urls) - 1:
        index += 1
    else:
        # no more entries / prevent index out of range
        messagebox.showinfo('Attention', 'No more entries, closing program')
        quit_click()

try:
    # load initial school
    with wait_for_page_load(driver):
        driver.get('{}'.format(urls[index]))
    time.sleep(3)
except TimeoutException:
    print("Timeout Error Wait and try again!")
    time.sleep(10)
    with wait_for_page_load(driver):
        driver.get('{}'.format(urls[index]))
    time.sleep(3)

# Tk GUI part
root = Tk()

query_label = Label(root, text='{}'.format(query[index]))  # reads query label
query_label.pack()

yes_button = Button(root, text='Yes', command=yes_click)
yes_button.pack()

no_button = Button(root, text='No', command=no_click)
no_button.pack()

quit_button = Button(root, text='Quit', command=quit_click)
quit_button.pack()

root.mainloop()
