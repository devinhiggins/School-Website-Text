import time
from collections import deque

from selenium import webdriver

from deny_vip_list import is_deny_listed, has_priority, is_filtered, traverse_req
from selenium_pageload import wait_for_page_load
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, UnexpectedAlertPresentException


def extract_candidate_urls(browser, sch_url, vip_keys=None, label_dic=None):
    """
    From the school homepage, extract all candidate URLs
    that would be visited in order to check for mission stmt.

    This function may be used to capture all link labels
    in order to analyze what labels to filter so that we could
    reduce the number of candidate links. To do so, pass empty
    dictionary for label_dic parameter

    Args:
        browser (WebDriver): Webdriver instance used to open webpage URLs

        sch_url (str): School homepage URL

        vip_keys (list[str], default=None): List of keywords that warrant a visit when traversing further is triggered

        label_dic (dict{str:int}, default=None): Expects empty dictionary, capturing 'link label':'occurrence'

    Returns:
        dequeue[str]: Queue of candidate URLs

        boolean: a flag that denotes URL being updated or not

        str: (updated) school url
    """
    print('{} - Extract Candidate URL Start'.format(sch_url), flush=True)
    url_changed = False
    try:
        with wait_for_page_load(browser):  # load school homepage
            browser.get(sch_url)
        time.sleep(3)
    except Exception:
        print("ERROR: 1st Page load exception (extract_candidate_urls/browser.get): {}".format(sch_url), flush=True)
        print("Try with HTTP")  # trying with http often result auto-forwarding to new URL
        try:
            with wait_for_page_load(browser):  # load school homepage
                browser.get(sch_url.replace('https', 'http'))
            time.sleep(3)
        except Exception:
            print("ERROR: 2nd Page load exception (extract_candidate_urls/browser.get): {}".format(sch_url), flush=True)
            return [], url_changed, sch_url

        url_changed = True
        sch_url = browser.current_url

    try:
        a_tag_list = browser.find_elements_by_xpath('//a')  # get all the a-tag elements
    except StaleElementReferenceException:
        print("find_element_by_xpath_a stale element exception", flush=True)
        return [], url_changed, sch_url
    except TimeoutException:
        print("find_element_by_xpath_a timeout exception", flush=True)
        return [], url_changed, sch_url
    except UnexpectedAlertPresentException:
        print("find_element_by_xpath_a unexpected alert present exception", flush=True)
        return [], url_changed, sch_url

    href_url_queue = deque()  # deque is used to facilitate left insertion to denote priority

    for a_tag in a_tag_list:  # iterate a-tags
        try:
            # pass if a-tag is not visible
            if not a_tag.is_displayed():
                continue
        except StaleElementReferenceException:
            print("Checking A-tag is_displayed stale element exception", flush=True)
            continue
        except UnexpectedAlertPresentException:
            print("Checking A-tag is_displayed unexpected alert present exception", flush=True)
            continue
        except TimeoutException:
            print("Checking A-tag is_displayed Timeout Exception", flush=True)
            continue

        try:
            # extract href link & link label
            href_val = a_tag.get_attribute('href')
            href_text = a_tag.text
        except StaleElementReferenceException:
            print("href value extraction stale element exception", flush=True)
            continue

        # check if href link & label value is None
        if (href_val is None) or (href_val == ''):
            continue
        if (href_text is None) or (href_text == ''):
            continue

        # if vip keywords are passed to vip_keys parameter
        # this process checks for those keywords from the label
        if vip_keys is not None:
            for elem in vip_keys:
                if (elem in href_text) or (elem.lower() in href_text.lower()):
                    href_url_queue.appendleft(href_val)  # insert left to denote higher priority
        else:
            # remove deny listed URLs
            if is_deny_listed(href_val):
                continue
            # remove filtered label
            if is_filtered(href_text):
                continue
            # Check for duplicate
            if href_val in href_url_queue:
                continue

            if has_priority(href_text):  # if URL label has priority keywords
                href_url_queue.appendleft(href_val)  # insert left
                if traverse_req(href_text):  # check if it triggers traversing down further
                    driver2 = webdriver.Firefox()
                    print('{} - {}: Traverse Activated'.format(href_text, href_val), flush=True)
                    # calling itself with the vip keywords so that same function would
                    # only check for link labels with vip keywords
                    vip_urls = extract_candidate_urls(driver2, href_val, vip_keys=['mission', 'overview'])
                    driver2.quit()
                    if len(vip_urls) != 0:  # if vip URLs exist
                        for vip_url in vip_urls:
                            href_url_queue.appendleft(vip_url)  # insert left
            else:
                href_url_queue.append(href_val)  # regular candidates inserted right

        if label_dic is not None:  # if empty dict is passed to label_dic, capture label texts
            if href_text.lower() in label_dic.keys():
                label_dic[href_text.lower()] += 1
            else:
                label_dic[href_text.lower()] = 1

    # return list(href_url_queue)
    return href_url_queue, url_changed, sch_url
