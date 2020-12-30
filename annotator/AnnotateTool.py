import errno
import os
import sys
import tkinter
import argparse
import pandas as pd
from pathlib import Path
from time import sleep
from tkinter import ttk
from selenium import webdriver
from Tools import safe_get, search_alink_extract, get_file_name_from_url

"""
    Annotation Tool
    
    Args:
        data_dir (str) : Absolute path to data directory where 
            input CSV file resides. 
        
            "pos_pages" & "neg_pages" dir will be created if not found 
            and page dumps will be stored in those directory respectively
            
            Completed list will be generated here (if it does not exist)
            in the form of "[source file name]_Done.csv"
            
            Not Found list will be generated here (if it does not exist)
            in the form of [source file name]_None.csv
        
        source_data (str) : Name of CSV formatted source file
            CSV file is expected to have NO HEADER and adhere 
            to following format: [School Name],[City],[zipcode]  
"""

# command-line arguments parsing module
parser = argparse.ArgumentParser()
parser.add_argument("data_dir", help="Path to data directory where input file reside")
parser.add_argument("source_data", help="CSV formatted source file")
args = parser.parse_args()

data_dir = args.data_dir
source_file = args.source_data

# check the directory and source file
# raise exception if not found
if not os.path.isdir(data_dir):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), data_dir)
if not os.path.isfile(os.path.join(data_dir, source_file)):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), source_file)

# create directories for page dump
positive_pages_dir = os.path.join(data_dir, 'pos_pages')
Path(positive_pages_dir).mkdir(parents=True, exist_ok=True)
negative_pages_dir = os.path.join(data_dir, 'neg_pages')
Path(negative_pages_dir).mkdir(parents=True, exist_ok=True)

completed_school_list_file = os.path.join(data_dir, source_file[:-4] + '_Done.csv')
notfound_school_list_file = os.path.join(data_dir, source_file[:-4] + '_None.csv')


class Annotate:
    # set of schools that were already processed
    # each element is in the following tuple form
    # (school_name, school_city, school_zipcode)
    processed_schools = set()
    try:
        # check if completed list exists and import data
        # in order to avoid re-processing same schools
        with open(completed_school_list_file, 'r') as rf:
            for line in rf:
                annotated_school = line.strip('\n').split(',')
                processed_schools.add((annotated_school[0], annotated_school[1], annotated_school[2]))
    except IOError:
        # if file does not exists then the program
        # catches the exception and moves on
        print("Nothing completed previously")
        pass

    try:
        # check if not-found list exists and import data
        # in order to avoid re-processing same schools
        with open(notfound_school_list_file, 'r') as rf:
            for line in rf:
                notfound_school = line.strip('\n').split(',')
                processed_schools.add((notfound_school[0], notfound_school[1], notfound_school[2]))
    except IOError:
        # if file does not exists then the program
        # catches the exception and moves on
        print("Nothing Not-Founded previously")
        pass

    # process source data to prep for Google Search
    input_csv = pd.read_csv(os.path.join(data_dir, source_file), header=None)
    school_name = input_csv[0]
    school_city = input_csv[1]
    school_zipcode = input_csv[2].astype(str)
    search_query = school_name + ',' + school_city + ',' + school_zipcode

    school_idx = 0
    search_idx = None
    google_search_url_list = []

    # start the Firefox browser
    browser = webdriver.Firefox()
    while True:
        if (school_name[school_idx], school_city[school_idx], school_zipcode[school_idx]) in processed_schools:
            # check if the school has been processed
            if school_idx < len(school_name) - 1:
                school_idx += 1
                continue
            else:
                print("All Done")
                browser.quit()
                sys.exit()

        print("school name: {} start".format(school_name[school_idx]))
        # perform Google Search and Extract Search Result Links
        # source code resides in the separate file "Tools.py"
        res, google_search_url_list = search_alink_extract(browser, search_query[school_idx].replace(',', ' '))

        if res:
            # if valid Google search results are retrieved
            # Start processing result links
            search_idx = 0
            safe_get(browser, google_search_url_list[search_idx])
            sleep(5)
            # print(browser.page_source.encode("utf-8"))
            break
        else:
            # if query does not results search results then
            # print error and move on to next school
            print("Strange query {} returned no result".format(search_query[school_idx].replace(',', ' ')))
            school_idx += 1


# refresh selenium browser with current index
def refresh_browser():
    if Annotate.search_idx is not None:
        Annotate.browser.get(Annotate.google_search_url_list[Annotate.search_idx])
    else:
        while True:
            if (Annotate.school_name[Annotate.school_idx], Annotate.school_city[Annotate.school_idx], Annotate.school_zipcode[Annotate.school_idx]) in Annotate.processed_schools:
                Annotate.school_idx += 1
                continue

            print("school name: {} start".format(Annotate.school_name[Annotate.school_idx]))
            res, Annotate.google_search_url_list = \
                search_alink_extract(Annotate.browser, Annotate.search_query[Annotate.school_idx].replace(',', ' '))

            if res:
                Annotate.search_idx = 0
                safe_get(Annotate.browser, Annotate.google_search_url_list[Annotate.search_idx])
                break
            else:
                write_result(notfound_school_list_file)
                Annotate.school_idx += 1


def prev_url():
    """
        browse prev. school search result page
        from the list if it is beginning of
        the list then just refresh same page
    """
    if Annotate.search_idx > 0:
        Annotate.search_idx -= 1
    else:
        Annotate.search_idx = 0
    refresh_browser()


def next_url():
    """
        browse next school search result page
        from the list if no more in the list then
        move on to next school
    """
    if Annotate.search_idx < len(Annotate.google_search_url_list) - 1:
        Annotate.search_idx += 1
    elif Annotate.school_idx < len(Annotate.school_name) - 1:
        write_result(notfound_school_list_file)
        Annotate.school_idx += 1
        Annotate.search_idx = None
    else:
        print("All Done")
        Annotate.browser.quit()
        sys.exit()

    refresh_browser()


def write_result(file_name):
    result_str = Annotate.search_query[Annotate.school_idx]
    result_str += ',' + (Annotate.browser.current_url + '\n') if file_name == completed_school_list_file else ',None\n'

    with open(file_name, 'a') as wf:
        wf.write(result_str)
        wf.flush()

    Annotate.processed_schools.add((Annotate.school_name[Annotate.school_idx], Annotate.school_city[Annotate.school_idx], Annotate.school_zipcode[Annotate.school_idx]))


def mark(func):
    """
        mark the current page as "YES/NO"
        and store in YES/NO Dir
        soup=Annotate.browser.getContent()
    """
    current_url = Annotate.browser.current_url
    print('Current Page:', current_url)
    print("Mark the current page as ", func)

    if func == 'pos':  # positive page
        with open(os.path.join(positive_pages_dir, get_file_name_from_url(current_url)), 'wb') as wf:
            wf.write(Annotate.browser.page_source.encode('utf-8'))
            wf.flush()
        write_result(completed_school_list_file)

        if Annotate.school_idx < len(Annotate.school_name) - 1:
            Annotate.school_idx += 1
            Annotate.search_idx = None
            refresh_browser()
        else:
            print("All Done")
            Annotate.browser.quit()
            sys.exit()

    elif func == 'neg':  # negative page
        with open(os.path.join(negative_pages_dir, get_file_name_from_url(current_url)), 'wb') as wf:
            wf.write(Annotate.browser.page_source.encode('utf-8'))
            wf.flush()
        next_url()


# quit application
def quit_app():
    root.destroy()
    Annotate.browser.quit()


root = tkinter.Tk()
root.geometry('300x300')
# refresh_browser()
style = ttk.Style()
style.configure('Wild.TButton',
                background='black',
                foreground='white',
                highlightthickness='20',
                font=('Helvetica', 30, 'bold'))

# define style of buttons
style.map("C.TButton",
          foreground=[('pressed', 'red'), ('active', 'blue')],
          background=[('pressed', '!disabled', 'black'), ('active', 'white')]
          )

# define buttons with their call_backs
# add additional buttons if you need it
prev_btn = ttk.Button(text="Previous URL",
                      style="C.TButton",
                      command=lambda: prev_url()).pack()

next_btn = ttk.Button(text="Next URL",
                      style="C.TButton",
                      command=lambda: next_url()).pack()

ref_btn = ttk.Button(text="Positive",
                     style="C.TButton",
                     command=lambda: mark('pos')).pack()

false_btn = ttk.Button(text="Negative",
                       style="C.TButton",
                       command=lambda: mark('neg')).pack()

quit_btn = ttk.Button(text="Quit",
                      style="C.TButton",
                      command=lambda: quit_app()).pack()

root.mainloop()
