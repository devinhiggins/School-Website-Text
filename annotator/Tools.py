import json
import re
import shutil
import time
from contextlib import contextmanager
from os import makedirs, listdir
from os.path import join, exists
from pprint import pprint

from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException


# START: Code for waiting until contents are fully loaded
from selenium.webdriver.common.keys import Keys


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
# END: Code for waiting until contents are fully loaded


def safe_get(browser, url):
    try:
        with wait_for_page_load(browser):
            browser.get(url)
    except WebDriverException:
        print(url, " NOT AVAILABLE")


def search_alink_extract(browser, search_query, url_key=None):

    with wait_for_page_load(browser):
        browser.get('http://www.google.com')

    search_box = browser.find_element_by_name('q')
    search_box.clear()
    search_box.send_keys(search_query)
    time.sleep(3)
    # search_box.submit()
    search_box.send_keys(Keys.RETURN)
    time.sleep(10)

    html_src = browser.page_source
    # browser.quit()

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
    # alink_set = set()
    for alink in search_soup.find_all('a'):
        href_link = alink.get('href')

        if href_link is None or href_link == '':
            continue

        if href_link.startswith('http://webcache') or href_link.startswith('https://webcache'):
            continue

        if href_link in alink_array or '/watch?' in href_link:
            continue

        if not href_link.startswith('http'):
            continue

        alink_array.append(href_link)
        # alink_set.add(href_link)
        # if url_key is not None and url_key in href_link:
        #     alink_array.append(href_link)

    if len(alink_array) == 0:
        return False, "A Link Set Empty"
    else:
        return True, alink_array


def extract_school_url(csv_file):
    school_url_list = []
    with open(csv_file, 'rb') as rf:
        line_num = 0
        for bline in rf:
            try:
                line = bline.decode()
            except UnicodeDecodeError as e:
                print(e)
                print(bline)
                line_num += 1
                continue
            school_data_list = line.strip().strip('\n').split(',')
            line_num += 1
            for school_data in school_data_list:
                if "http" in school_data:
                    print(line_num, school_data, parse_url(school_data))
                    school_url_list.append(school_data)

    return school_url_list


def extract_school_name(csv_file):
    school_name_list = []
    with open(csv_file, 'r') as rf:
        line_num = 0
        for line in rf:
            if line_num == 0:
                line_num += 1
                continue
            school_data_list = line.strip().strip('\n').split(',')
            line_num += 1
            print(line_num, school_data_list[1])
            school_name_list.append(school_data_list[1])
    return school_name_list


def extract_school_name_city_zip(csv_file):
    school_name_city_zip_list = []
    with open(csv_file, 'r') as rf:
        line_num = 0
        for line in rf:
            if line_num == 0:
                line_num += 1
                continue
            school_data_list = line.strip().strip('\n').split(',')
            line_num += 1
            print(line_num, school_data_list[1], school_data_list[3], school_data_list[4])
            school_name_city_zip_list.append([school_data_list[1], school_data_list[3], school_data_list[4]])
    return school_name_city_zip_list


def parse_url(raw_url):
    url_elem = raw_url.strip().split('/')
    parsed_url = ''
    for idx in range(len(url_elem)):
        if 'http' in url_elem[idx]:
            continue
        elif url_elem[idx] == '':
            continue
        else:
            parsed_url += url_elem[idx] if parsed_url == '' else '_'+url_elem[idx]

    return parsed_url


def dump_school_frontpage(url_list, dump_dir):
    assert isinstance(url_list, list), "Input data must be list format"

    if not exists(dump_dir):
        makedirs(dump_dir)

    browser = webdriver.Firefox()
    for url in url_list:
        try:
            with wait_for_page_load(browser):
                browser.get(url)
        except WebDriverException:
            print(url, " NOT AVAILABLE")
            continue
        try:
            browser.find_element_by_xpath('//a[@class="disable"]').click()
        except NoSuchElementException:
            pass

        time.sleep(10)
        html_src = browser.page_source
        with open(join(dump_dir, parse_url(url)+'.html'), 'w') as wf:
            wf.write(html_src)
        # browser.close()
    browser.quit()


def check_keyword_in_html(repository):
    for file_name in listdir(repository):
        if not file_name.endswith(".html"):
            continue

        with open(join(repository, file_name), 'r') as rf:
            try:
                contents = rf.read()
            except UnicodeDecodeError as e:
                print(file_name, " bypassed")
                continue

        soup = BeautifulSoup(contents, 'lxml')
        body = soup.body
        # print(body)

        for tag in body.select('script'):
            tag.decompose()
        for tag in body.select('style'):
            tag.decompose()
        # print(body)
        # blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style']

        text = body.get_text(separator='\n').lower()
        # print(text)
        keyword_list = ['mission', 'value', 'vision', 'goal']
        for keyword in keyword_list:
            if keyword in text:
                shutil.copy2(join(repository, file_name),
                             '/Users/jhp/MSU/project/schooltext/jhp/data/national_dump/key_pages')
                break


def process_national_data(csv_file):
    school_name_city_zip_url_list = []
    with open(csv_file, 'r') as rf:
        line_num = 0
        for line in rf:
            if line_num == 0:
                line_num += 1
                continue
            school_data_list = line.strip().strip('\n').split(',')
            line_num += 1
            print(line_num, school_data_list[0], school_data_list[1], school_data_list[2], school_data_list[3])
            if school_data_list[3] == '99' or school_data_list[3] == 'na':
                with open('/Users/jhp/MSU/project/schooltext/jhp/data/NationalUnable.csv', 'a') as wf:
                    list_str = school_data_list[0] + ',' + school_data_list[1] + ',' + school_data_list[2] + ',' \
                               + school_data_list[3] + '\n'
                    wf.write(list_str)
            elif school_data_list[3] == '' or school_data_list[3] == ' ':
                with open('/Users/jhp/MSU/project/schooltext/jhp/data/NationalNew.csv', 'a') as wf:
                    list_str = school_data_list[0] + ',' + school_data_list[1] + ',' + school_data_list[2] + ',' \
                               + school_data_list[3] + '\n'
                    wf.write(list_str)
            else:
                with open('/Users/jhp/MSU/project/schooltext/jhp/data/NationalDone.csv', 'a') as wf:
                    list_str = school_data_list[0] + ',' + school_data_list[1] + ',' + school_data_list[2] + ',' \
                               + school_data_list[3] + '\n'
                    wf.write(list_str)


def extract_national_school_name_city_zip(csv_file):
    school_name_city_zip_list = []
    with open(csv_file, 'r') as rf:
        line_num = 0
        for line in rf:
            # if line_num == 0:
            #     line_num += 1
            #     continue
            school_data_list = line.strip().strip('\n').split(',')
            line_num += 1
            print(line_num, school_data_list[0], school_data_list[1], school_data_list[2])
            school_name_city_zip_list.append([school_data_list[0], school_data_list[1], school_data_list[2]])
    return school_name_city_zip_list


def extract_mission_stmt(csv_file):
    stop_words = set(stopwords.words('english'))
    worddic_freq = {}
    with open(csv_file, 'r') as rf:
        for line in rf:
            line.strip().strip('\n')
            if line == 'na':
                continue
            word_tokens = word_tokenize(line)

            filtered_sentence = [w for w in word_tokens if w not in stop_words]

            for fw in filtered_sentence:
                try:
                    worddic_freq[fw] += 1
                except KeyError:
                    worddic_freq[fw] = 1
    worddic_freq = {k: v for k, v in sorted(worddic_freq.items(), key=lambda item: item[1], reverse=True)}
    print(worddic_freq)

# process_national_data('/Users/jhp/MSU/project/schooltext/jhp/data/NationalLevelShotList.csv')

# def extract_text_from_html(html_page):
#     with open(html_page, 'r') as rf:
#         soup = BeautifulSoup(rf, 'html.parser')
#     body = soup.find('body').
#
#     output = ''
#     blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style']
#


# school_urls = extract_school_url("/Users/jhp/MSU/project/schooltext/jhp/data/sc_dump/SOUTHCAROLINASchoolList.csv")
# school_names = extract_school_name("/Users/jhp/MSU/Projects/schooltext/jhp/data/HAWAIISchoolList.csv")
# school_name_city_zips = extract_school_name_city_zip("/Users/jhp/MSU/Projects/schooltext/jhp/data/HAWAIISchoolList.csv")
# dump_school_frontpage(school_urls, '/Users/jhp/MSU/project/schooltext/jhp/data/sc_dump/pos_pages')
# check_keyword_in_html('/Users/jhp/MSU/project/schooltext/jhp/data/national_dump/pos_pages')
# extract_mission_stmt('/Users/jhp/MSU/project/schooltext/jhp/data/national_dump/NationalMissionExtraction2.csv')