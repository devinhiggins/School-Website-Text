import re
import time
from contextlib import contextmanager
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
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


def safe_get(browser, url):
    try:
        with wait_for_page_load(browser):
            browser.get(url)
    except WebDriverException:
        print(url, " NOT AVAILABLE")


def get_file_name_from_url(url):
    if url[-1] == "/":
        url = url[:-1]

    if "http://" in url:
        url = url.replace('http://', '')
    elif "https://" in url:
        url = url.replace('https://', '')

    url = re.sub('[^A-Za-z0-9.]+', '', url)
    # url = url.replace("/", "_").replace('?', '_').strip()
    if len(url) > 240:
        url = url[:240]
    return url + ".html"


def search_alink_extract(browser, search_query):

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

    if len(alink_array) == 0:
        return False, "A Link Set Empty"
    else:
        return True, alink_array
