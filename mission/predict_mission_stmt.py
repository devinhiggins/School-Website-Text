import re
import time
import traceback
from os.path import join
import joblib
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, \
    InvalidSessionIdException, InvalidArgumentException

from selenium_pageload import wait_for_page_load


def predict_mission_stmt(url_list, model_directory, tfidf_file, ocsvm_file):
    """
    
    """
    print('Predict mission stmt start', flush=True)

    # load pre-trained TF-IDF vector & One-class SVM model
    tfidf_vect = joblib.load(join(model_directory, tfidf_file))
    model = joblib.load(join(model_directory, ocsvm_file))

    # fork separate selenium obj. for this process
    # this choice was made to prevent main selenium driver
    # crashing due to fragile nature of this process visiting
    # various links which may cause browser to hang or crash
    browser = webdriver.Firefox()

    candidate_text_list = []
    for href_url in url_list:  # iterate URL list to capture texts
        page_source = ''
        print("Opening URL - {}".format(href_url), flush=True)
        try:
            with wait_for_page_load(browser):
                browser.get(href_url)
            time.sleep(3)
        except Exception:
            print("Page load exception: {}".format(href_url), flush=True)
            traceback.print_exc()
            browser.quit()  # destroy selenium browser
            browser = webdriver.Firefox()  # re-fork selenium browser
            time.sleep(10)
            try:
                with wait_for_page_load(browser):  # try to reload the URL
                    browser.get(href_url)
                time.sleep(3)
            except Exception:
                print("Page load exception: {}".format(href_url), flush=True)
                traceback.print_exc()
                browser.quit()  # 2nd try failed - pass URL & reset browser
                browser = webdriver.Firefox()
                continue
        try:
            page_source = browser.page_source  # retrieve page source
        except UnexpectedAlertPresentException:  # encounter alert on the page
            print("{} - UnexpectedAlertPresent".format(href_url), flush=True)
            try:
                time.sleep(10)
                alert = browser.switch_to.alert  # click accept
                alert.accept()
            except NoAlertPresentException:  # if alert disappears automatically
                print("{} - NoAlertPresentException".format(href_url), flush=True)
                time.sleep(10)
                try:
                    page_source = browser.page_source  # try again
                except Exception:
                    traceback.print_exc()  # 2nd failure pass URL
                    continue
        except InvalidSessionIdException:
            print("ERROR: predict_mission_stmt - browser.page_source", flush=True)
            traceback.print_exc()
            continue
        except InvalidArgumentException:
            print("{}-InvalidArgumentException: unexpected end of hex escape has occurred".format(href_url), flush=True)
            traceback.print_exc()
            continue
        except Exception:  # catch any unusual exception
            print("browser.page_source failed eventually", flush=True)
            traceback.print_exc()
            browser.quit()  # reset browser
            browser = webdriver.Firefox()
            continue

        # covert page source to beautifulsoup obj. in order to parse HTML
        soup = BeautifulSoup(page_source, 'html.parser')

        blacklist = ['header', 'script', 'style', 'a']  # remove irrelevant codes
        for bl in blacklist:
            while soup.find(bl) is not None:
                soup.find(bl).extract()
        try:
            texts = soup.body.text  # extract only text of body of HTML
        except AttributeError:
            print('ERROR: predict_candidate_text - soup.body.text', flush=True)
            traceback.print_exc()
            continue

        org_txt_list = []  # keep initial prepped text for analysis purposes
        processed_txt_list = []  # completely prepped text stored here
        for text in texts.strip().split('\n'):  # separate text by newline
            # prep text by keeping alphanumeric chars and blank space
            text_prep = re.sub('[^A-Za-z0-9 ]+', '', text)
            # if prepped text is None, empty or just numbers and blank spaces then pass
            if (text_prep is None) or (text_prep == '') or re.match("^[0-9 ]+$", text_prep):
                continue
            org_txt_list.append(text_prep)

            stop_words = set(stopwords.words('english'))  # load English stop-words
            word_tokens = word_tokenize(text_prep)  # tokenize prepped text

            filtered_sentence = [w for w in word_tokens if w not in stop_words]  # remove stop words

            temp_doc = ""
            for token in filtered_sentence:
                temp_doc += token + ' '
            processed_txt_list.append(temp_doc)

        try:
            # use TF-IDF vector
            test_tfidf = tfidf_vect.transform(processed_txt_list)
        except ValueError:
            print("ERROR tfidf_vect.transform:", flush=True)
            traceback.print_exc()
            print("Original Text List: {}".format(org_txt_list), flush=True)
            print("Processed Text List: {}".format(processed_txt_list), flush=True)
            continue

        # use One-Class SVM to predict
        prediction = model.predict(test_tfidf)

        # add positive prediction to the candidate list
        for idx in range(len(prediction)):
            if prediction[idx] == 1:
                candidate_text_list.append(org_txt_list[idx])

    browser.quit()  # destroy browser
    return candidate_text_list  # return positively predicted text list
