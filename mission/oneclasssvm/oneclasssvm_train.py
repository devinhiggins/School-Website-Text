import argparse
import re
from os.path import join
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import OneClassSVM
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
import joblib


def document_prep(data_dir, excel_file):
    """
    Prepare training/testing documents from excel sheets
    that contain human collected mission statements

    Args:
        data_dir (str): Path to excel sheets

        excel_file (str): file name of excel sheets

    Returns:
        list[str]: Cleaned & Prepped documents list
    """
    excel_df = pd.read_excel(join(data_dir, excel_file))
    missions = excel_df['mission']
    processed_doc_list = []

    for mission in missions:
        mission_prep = re.sub('[^A-Za-z0-9 ]+', '', mission)

        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(mission_prep)

        filtered_sentence = [w for w in word_tokens if w not in stop_words]

        temp_doc = ""
        for token in filtered_sentence:
            temp_doc += token + ' '

        processed_doc_list.append(temp_doc)

    return processed_doc_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()  # command-line arguments parsing module
    parser.add_argument("data_dir", help="Path to data directory where input file reside")
    parser.add_argument("train_data", help="CSV formatted data file used for training")
    parser.add_argument("test_data", help="CSV formatted data file used for testing")
    args = parser.parse_args()

    data_dir = args.data_dir
    train_data = args.train_data
    test_data = args.test_data

    train_doc_list = document_prep(data_dir, train_data)
    train_bin_list = [1 for i in range(len(train_doc_list))]
    test_doc_list = document_prep(data_dir, test_data)
    test_bin_list = [1 for i in range(len(test_doc_list))]

    # create TFIDF vector, train, transform, and save vector
    tfidf_vect = TfidfVectorizer()

    # learn voca and idf using training dataset
    train_tfidf = tfidf_vect.fit_transform(train_doc_list)

    # transform documents to doc-term matrix using voca and doc frequencies learned by fit_transform
    test_tfidf = tfidf_vect.transform(test_doc_list)

    # save TFIDF model for later use
    joblib.dump(tfidf_vect, join(data_dir, 'tfidfvect.joblib'))

    model = OneClassSVM(gamma='auto')
    model.fit(train_tfidf)

    test_prediction = model.predict(test_tfidf)

    # save OneClassSVM model for later use
    joblib.dump(model, join(data_dir, 'oneclasssvm.joblib'))

    # save train score log
    with open(join(data_dir, 'train.log'), 'w') as wf:
        wf.write('Precision: {}\n'.format(precision_score(test_bin_list, test_prediction)))
        wf.write('Recall: {}\n'.format(recall_score(test_bin_list, test_prediction)))
        wf.write('F1 Score: {}\n'.format(f1_score(test_bin_list, test_prediction)))
        wf.write('Accuracy: {}\n'.format(accuracy_score(test_bin_list, test_prediction)))
