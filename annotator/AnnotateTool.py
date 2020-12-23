import sys
import tkinter
from time import sleep
from tkinter import ttk
from selenium import webdriver
from jhp import extract_school_name_city_zip, safe_get, search_alink_extract, extract_national_school_name_city_zip

BYPASS_SCHOOL_LIST = "/Users/jhp/MSU/project/schooltext/jhp/data/national1_dump/NationalByPassed.csv"
COMPLETED_SCHOOL_LIST = "/Users/jhp/MSU/project/schooltext/jhp/data/national1_dump/NationalNewDone.csv"
POS_PATH_SAVE = '/Users/jhp/MSU/project/schooltext/jhp/data/national1_dump/pos_pages/'
NEG_PATH_SAVE = '/Users/jhp/MSU/project/schooltext/jhp/data/national1_dump/neg_pages/'


class Annotate:
    school_name_city_zip_list = \
        extract_national_school_name_city_zip("/Users/jhp/MSU/project/schooltext/jhp/data/NationalNew.csv")
    annotated_school_names = set()
    try:
        with open(COMPLETED_SCHOOL_LIST, 'r') as rf:
            for line in rf:
                annotated_school_names.add(line.strip('\n').split(',')[0])
    except IOError:
        print("Nothing completed")
        pass
    try:
        with open(BYPASS_SCHOOL_LIST, 'r') as rf:
            for line in rf:
                annotated_school_names.add(line.strip('\n').split(',')[0])
    except IOError:
        print("Nothing bypassed")
        pass

    school_idx = 0
    # bypassed_school_list = []

    search_idx = None
    google_search_url_list = []

    browser = webdriver.Firefox()
    while True:
        if school_name_city_zip_list[school_idx][0] in annotated_school_names:
            if school_idx < len(school_name_city_zip_list) - 1:
                school_idx += 1
                continue
            else:
                print("All Done")
                browser.quit()
                sys.exit()

        query_str = ''
        for elem in school_name_city_zip_list[school_idx]:
            query_str += elem + ' '
        print("school name: {} start".format(school_name_city_zip_list[school_idx][0]))
        res, google_search_url_list = search_alink_extract(browser, query_str)

        if res:
            search_idx = 0
            safe_get(browser, google_search_url_list[search_idx])
            sleep(5)
            # print(browser.page_source.encode("utf-8"))
            break
        else:
            print("strange query {} returned no result".format(query_str))
            school_idx += 1


# refresh selenium with current index
def refresh_browser():
    if Annotate.search_idx is not None:
        Annotate.browser.get(Annotate.google_search_url_list[Annotate.search_idx])
    else:
        while True:
            if Annotate.school_name_city_zip_list[Annotate.school_idx][0] in Annotate.annotated_school_names:
                Annotate.school_idx += 1
                continue
            Annotate.query_str = ''
            for elem in Annotate.school_name_city_zip_list[Annotate.school_idx]:
                Annotate.query_str += elem + ' '
            print("school name: {} start".format(Annotate.school_name_city_zip_list[Annotate.school_idx][0]))
            res, Annotate.google_search_url_list = search_alink_extract(Annotate.browser, Annotate.query_str)

            if res:
                Annotate.search_idx = 0
                safe_get(Annotate.browser, Annotate.google_search_url_list[Annotate.search_idx])
                break
            else:
                write_result(BYPASS_SCHOOL_LIST)
                Annotate.school_idx += 1
                # Annotate.bypassed_school_list.append(Annotate.query_str)


def is_done_already(school_name):
    if school_name in Annotate.annotated_school_names:
        return True
    else:
        return False


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
    elif Annotate.school_idx < len(Annotate.school_name_city_zip_list) - 1:
        write_result(BYPASS_SCHOOL_LIST)
        # Annotate.bypassed_school_list.append(Annotate.query_str)
        Annotate.school_idx += 1
        Annotate.search_idx = None
    else:
        print("All Done")
        Annotate.browser.quit()
        # with open(BYPASS_SCHOOL_LIST, 'w') as wf:
        #     for item in Annotate.bypassed_school_list:
        #         wf.write(item + '\n')
        #         wf.flush()
        sys.exit()
    refresh_browser()


def get_file_name_from_url(url):
    if url[-1] == "/":
        url = url[:-1]

    if "http://" in url:
        url = url.replace('http://', '')
    elif "https://" in url:
        url = url.replace('https://', '')

    url = url.replace("/", "_").strip()
    if len(url) > 250:
        url = url[:250]
    return url + ".html"


def write_result(file_name):
    result_str = ''
    for elem in Annotate.school_name_city_zip_list[Annotate.school_idx]:
        result_str += elem + ','

    result_str += (Annotate.browser.current_url + '\n') if file_name == COMPLETED_SCHOOL_LIST else 'None\n'

    with open(file_name, 'a') as wf:
        wf.write(result_str)
        wf.flush()

    Annotate.annotated_school_names.add(Annotate.school_name_city_zip_list[Annotate.school_idx][0])


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
        with open(POS_PATH_SAVE + get_file_name_from_url(current_url), 'wb') as wf:
            wf.write(Annotate.browser.page_source.encode('utf-8'))
            wf.flush()
        write_result(COMPLETED_SCHOOL_LIST)
        if Annotate.school_idx < len(Annotate.school_name_city_zip_list) - 1:
            Annotate.school_idx += 1
            Annotate.search_idx = None
            refresh_browser()
        else:
            print("All Done")
            Annotate.browser.quit()
            sys.exit()

    elif func == 'neg':  # negative page
        with open(NEG_PATH_SAVE + get_file_name_from_url(current_url), 'wb') as wf:
            wf.write(Annotate.browser.page_source.encode('utf-8'))
        next_url()
    # elif func == 'done':


def answer(flag):
    """
        intractive with user (e.g., Replace with new annotation?)
    """
    print(flag)


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

root.mainloop()
