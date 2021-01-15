import argparse
import errno
import re
import time
from contextlib import contextmanager
from os import strerror
from os.path import isdir, isfile, join

import joblib
import numpy as np
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from outlier_sites import outliers


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


parser = argparse.ArgumentParser()  # command-line arguments parsing module
parser.add_argument("data_dir", help="Path to data directory where input file reside")
parser.add_argument("source_data", help="CSV formatted source file")
parser.add_argument("model_dir", help="Path to model directory where trained classifier model reside")
parser.add_argument("split_index", help="Split index (k-fold) of the classifier model")
args = parser.parse_args()

data_dir = args.data_dir
source_file = args.source_data
model_dir = args.model_dir
split_idx = args.split_index

tfidf_model = 'tfidfvect' + split_idx + '.joblib'
rfclf_model = 'rfclf' + split_idx + '.joblib'
output_file = source_file[:-4] + '_Result.csv'

if not isdir(data_dir):  # check the validity of arguments
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), data_dir)
elif not isdir(model_dir):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), model_dir)
elif not isfile(join(data_dir, source_file)):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), source_file)
elif not isfile(join(model_dir, tfidf_model)):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), tfidf_model)
elif not isfile(join(model_dir, rfclf_model)):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), rfclf_model)

processed_schools = set()
try:
    # check if completed list exists and import data
    # in order to avoid re-processing same schools
    with open(join(data_dir, output_file), 'r') as rf:
        for line in rf:
            processed_school = line.strip('\n').split(',')
            processed_schools.add((processed_school[0], processed_school[1], processed_school[2]))
    print("{} school has been processed previously".format(len(processed_schools)))
except IOError:
    # if file does not exists then the program
    # catches the exception and moves on
    print("No school has been processed")

with open(join(data_dir, source_file), 'r') as rf:
    school_set = set()
    for line in rf:
        tmp_school = line.strip('\n').split(',')
        if tmp_school[0] == 'SCH_NAME' or len(tmp_school) < 3:
            print("Error: " + tmp_school[0], flush=True)
            continue

        if (tmp_school[0], tmp_school[1], tmp_school[2]) in processed_schools:
            # pass if the school has been already processed
            continue

        school_set.add((tmp_school[0], tmp_school[1], tmp_school[2]))

print("Processing {} schools starts now".format(len(school_set)), flush=True)


def prepare_document_list(browser, search_url_list):
    doc_list = []

    for search_url in search_url_list:
        try:
            with wait_for_page_load(browser):
                browser.get(search_url)
            time.sleep(3)
        except Exception:
            print("Page load exception (prepare_doclist):", search_url)
            continue

        page_source = browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        temp_document = ''
        for elem in soup.text.strip().split("\n"):
            if elem.strip('\t') != '' and elem.strip('\t') != ' ':
                # text_list.append(elem.strip('\t'))
                temp_document += elem.strip('\t') + ' '

        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(temp_document)

        filtered_sentence = [w for w in word_tokens if w not in stop_words]

        document = ''
        for tok in filtered_sentence:
            document += tok + ' '

        doc_list.append(document)

    return doc_list


def classify_school_page(doc_list):
    # use TFIDF vector and RF classifier to classify
    # school homepage and returns prediction result list
    x_test = np.array(doc_list)

    # load tfidf model
    tfidf_vect = joblib.load(join(model_dir, tfidf_model))
    # transform new documents to doc-term matrix
    x_test_tfidf = tfidf_vect.transform(x_test)

    # load Random Forest model
    rfclf = joblib.load(join(model_dir, rfclf_model))
    # predict new documents
    prediction = rfclf.predict(x_test_tfidf)
    # return prediction result
    return prediction


def evaluate_school_candidate_urls(browser, candidate_urls):
    document_list = prepare_document_list(browser, candidate_urls)
    if len(document_list) == 0:
        return []

    classification_result = classify_school_page(document_list)

    positive_idx = []
    for idx in range(len(classification_result)):
        if classification_result[idx] == 1:
            positive_idx.append(idx)

    if len(positive_idx) != 0:
        return [candidate_urls[idx] for idx in positive_idx]
    else:
        return []


school_idx = 0
driver = webdriver.Firefox()

for school in school_set:
    school_idx += 1
    school_name = school[0]
    school_city = school[1]
    school_zip = school[2]

    search_query = school_name + ' ' + school_city + ' ' + school_zip
    try:
        with wait_for_page_load(driver):
            driver.get('https://www.google.com')
    except TimeoutException:
        print("Timeout Error Wait and try again!")
        time.sleep(10)
        with wait_for_page_load(driver):
            driver.get('https://www.google.com')

    search_box = driver.find_element_by_name('q')
    search_box.clear()
    search_box.send_keys(search_query)
    time.sleep(3)

    search_box.send_keys(Keys.RETURN)
    time.sleep(10)

    html_src = driver.page_source

    result_start = re.search(r'Search Results', html_src).start() \
        if re.search(r'Search Results', html_src) is not None else -1
    if result_start != -1:
        html_src = html_src[html_src.index('Search Results') + 14:]

    extra_result_start = re.search(r'Searches related', html_src).start() \
        if re.search(r'Searches related', html_src) is not None else -1
    if extra_result_start != -1:
        html_src = html_src[:html_src.index('Searches related')]

    search_soup = BeautifulSoup(html_src, 'html.parser')

    blacklist = ['header', 'script', 'style']

    for bl in blacklist:
        while search_soup.find(bl) is not None:
            search_soup.find(bl).extract()

    while search_soup.find(id='search') is not None:
        search_soup.find(id='search').extract()

    alink_array = []

    for alink in search_soup.find_all('a'):
        href_link = alink.get('href')
        fp_flag = False

        if href_link is None or href_link == '':
            continue

        if href_link.startswith('http://webcache') or href_link.startswith('https://webcache'):
            continue

        if href_link in alink_array or '/watch?' in href_link:
            continue

        if not href_link.startswith('http'):
            continue

        for fp in outliers:
            if fp in href_link:
                fp_flag = True
                break
        if fp_flag is True:
            continue

        alink_array.append(href_link)

    positive_urls = evaluate_school_candidate_urls(driver, alink_array)
    print(positive_urls)

    if len(positive_urls) == 0:
        with open(join(data_dir, output_file), 'a') as af:
            af.write(school_name + ',' + school_city + ','
                     + school_zip + ',' + "None" + '\n')
            print(str(school_idx) + ',' + school_name + ',' + school_city + ','
                  + school_zip + ',' + "None", flush=True)
            af.flush()
    else:
        for idx in range(len(alink_array)):
            if idx == 0:
                with open(join(data_dir, output_file), 'a') as af:
                    af.write(school_name + ',' + school_city + ','
                             + school_zip + ',' + alink_array[idx] + '\n')
                    af.flush()
                    print(str(school_idx) + ',' + school_name + ',' + school_city + ','
                          + school_zip + ',' + alink_array[idx], flush=True)

driver.quit()
print("DONE")
