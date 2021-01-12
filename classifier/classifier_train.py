import argparse
import errno
from os import strerror
from os.path import isdir, join

import joblib
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold

from classifier.document_prep import document_prep

parser = argparse.ArgumentParser()  # command-line arguments parsing module
parser.add_argument("pos_dir_or_file", help="Path to school homepage dump directory or list file")
parser.add_argument("neg_dir_or_file", help="Path to none-school webpage dump directory or list file")
parser.add_argument("model_dir", help="Path to a directory where trained classifier model will reside")
args = parser.parse_args()

pos_dir_or_file = args.pos_dir_or_file
neg_dir_or_file = args.neg_dir_or_file
model_dir = args.model_dir

if not isdir(pos_dir_or_file):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), pos_dir_or_file)
elif not isdir(neg_dir_or_file):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), neg_dir_or_file)
elif not isdir(model_dir):
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), model_dir)

# process dirs and generate pos & neg doc list
pos_doc_list, neg_doc_list = document_prep(pos_dir_or_file, neg_dir_or_file)

if pos_doc_list is None or pos_doc_list == []:
    raise RuntimeError("Empty positive document list!")
elif neg_doc_list is None or neg_doc_list == []:
    raise RuntimeError("Empty negative document list!")

# create total doc list and binary list
total_document_list = pos_doc_list + neg_doc_list
binary_list = [1 for i in range(len(pos_doc_list))] + [0 for i in range(len(neg_doc_list))]
print("{0} positive docs and {1} negative docs imported".format(len(pos_doc_list), len(neg_doc_list)))

# create NP Array
X_document_nparr = np.array(total_document_list)
y_binary_nparr = np.array(binary_list)

# utilize Stratified K-Folds cross-validator
tfidf_skf = StratifiedKFold(n_splits=10)
tfidf_skf.get_n_splits(X_document_nparr, y_binary_nparr)

# exploit TF-IDF vectorization and train Random Forest
# classifier with Stratified 10-fold cross-validation
fold_index = 0
total_precision = 0.0
total_recall = 0.0
total_f1 = 0.0
total_accuracy = 0.0

for tfidf_train_index, tfidf_test_index in tfidf_skf.split(X_document_nparr, y_binary_nparr):
    # print training and test dataset indexes
    print("TRAIN:", tfidf_train_index, "TEST:", tfidf_test_index)
    X_train, X_test = X_document_nparr[tfidf_train_index], X_document_nparr[tfidf_test_index]
    y_train, y_test = y_binary_nparr[tfidf_train_index], y_binary_nparr[tfidf_test_index]

    # create TFIDF vector, train, transform, and save vector
    tfidf_vect = TfidfVectorizer()
    # learn voca and idf using training dataset
    X_train_tfidf = tfidf_vect.fit_transform(X_train)
    # transform documents to doc-term matrix using voca and doc frequencies learned by fit_transform
    X_test_tfidf = tfidf_vect.transform(X_test)
    # save TFIDF model for later use
    joblib.dump(tfidf_vect, join(model_dir, 'tfidfvect'+str(fold_index)+'.joblib'))

    # create Random Forest classifier, train, predict and save
    rfclf = RandomForestClassifier()
    # train classifier with train dataset
    rfclf.fit(X_train_tfidf, y_train)
    # predict test dataset
    prediction = rfclf.predict(X_test_tfidf)
    # save Random Forest classifier
    joblib.dump(rfclf, join(model_dir, 'rfclf' + str(fold_index) + '.joblib'))
    # compare result
    comparision = [(a, b) for (a, b) in zip(y_binary_nparr[tfidf_test_index], prediction)]

    # add to the total score to calculate average when finished
    total_precision += precision_score(y_binary_nparr[tfidf_test_index], prediction)
    total_recall += recall_score(y_binary_nparr[tfidf_test_index], prediction)
    total_f1 += f1_score(y_binary_nparr[tfidf_test_index], prediction)
    total_accuracy += accuracy_score(y_binary_nparr[tfidf_test_index], prediction)

    # print out the score
    print("Precision:", precision_score(y_binary_nparr[tfidf_test_index], prediction))
    print("Recall:", recall_score(y_binary_nparr[tfidf_test_index], prediction))
    print("Accuracy:", accuracy_score(y_binary_nparr[tfidf_test_index], prediction))
    print("F1:", f1_score(y_binary_nparr[tfidf_test_index], prediction))
    # print("Raw Comparision:", comparision)
    print(str(fold_index), "-split finished")
    print("=========================================")

    # increase fold-index
    fold_index += 1

# print averaged score
print("Avg. Precision:", total_precision/10)
print("Avg. Recall:", total_recall/10)
print("Avg. F1:", total_f1/10)
print("Avg. Accuracy", total_accuracy/10)
