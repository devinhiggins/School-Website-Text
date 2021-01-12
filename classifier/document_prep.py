import errno
from os import listdir, strerror
from os.path import join, isdir, isfile

from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords


def document_prep(pos_dir_or_file, neg_dir_or_file, param_type='dir'):
    """
    Prepare training documents from html repository directory
    or csv formatted list of homepage urls

    Args:
        pos_dir_or_file (str): Path to school homepage dump directory or list file.

        neg_dir_or_file (str): Path to none-school webpage dump directory or list file.

        param_type (str, default='dir'): Parameter type "dir" or "list"

    Returns:
        list[str], list[str]: Positive and Negative document list respectively
    """
    if param_type == 'dir':
        if not isdir(pos_dir_or_file) or not isdir(neg_dir_or_file):
            raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), pos_dir_or_file + " & " + neg_dir_or_file)
        pos_doc_list = process_html_dir(pos_dir_or_file)
        neg_doc_list = process_html_dir(neg_dir_or_file)
    elif param_type == 'list':
        if not isfile(pos_dir_or_file) or not isfile(neg_dir_or_file):
            raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), pos_dir_or_file + " & " + neg_dir_or_file)
        pos_doc_list = process_html_list(pos_dir_or_file)
        neg_doc_list = process_html_list(neg_dir_or_file)
    else:
        raise TypeError("Incorrect type specified! - Please choose \"dir\" or \"list\"")

    return pos_doc_list, neg_doc_list


def process_html_list(list_file):
    """
    Prepare training document lists from csv formatted url list

    Arg:
        list_file (str): Path to csv file

    Returns:
        list[str]: Tokenized and cleaned document list
    """
    processed_doc_list = []
    print("TO DO ITEM: ", list_file)
    return processed_doc_list


def process_html_dir(repo_dir):
    """
    Prepare training document lists from html repository directory

    Arg:
        repo_dir (str): Path to webpage source dump directory

    Returns:
        list[str]: Tokenized and cleaned document list
    """
    processed_doc_list = []

    for filename in listdir(repo_dir):
        if not filename.endswith('.html'):
            continue

        try:
            with open(join(repo_dir, filename), 'r') as rf:
                soup = BeautifulSoup(rf, 'html.parser')
        except FileNotFoundError:
            print("ERROR ", filename)
            continue

        temp_document = ""
        for elem in soup.text.strip().split("\n"):
            if elem.strip('\t') != '' and elem.strip('\t') != ' ':
                temp_document += elem.strip('\t') + ' '

        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(temp_document)

        filtered_sentence = [w for w in word_tokens if w not in stop_words]

        temp_document = ""
        for token in filtered_sentence:
            temp_document += token + ' '

        processed_doc_list.append(temp_document)

    return processed_doc_list
