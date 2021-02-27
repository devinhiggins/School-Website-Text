# School Homepage Classification

School homepage classification aims to find correct school homepages from Google Search results using natural language processing (NLP) and machine learning (ML) techniques.  

### Process Overview

------

![Process Overview](images/proc_overview.png)

#### 1. Train Classifier

This component uses both school homepage (positive) and other non-school webpage (negative) dumps to prep text data training [Random Forest (RF) classifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html). [Stratified 10-fold cross validation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html) is used to avoid overfitting.

#### 2.a. Iterate School List and Perform Google Search

This component exploits [Selenium](https://selenium-python.readthedocs.io/) web automation technique to perform Google Search using school name, school city, and school zip code extracted from [National Center for Education Statistics](https://nces.ed.gov/) (NCES).

#### 2.b. Apply Classifier and Predict School Homepage

This component extracts text from the candidate webpages retrieved from Google Search result and apply same NLP techniques to prep text. Once texts are prepped for all webpages, pre-trained RF classifier is utilized to predict School Homepage.

### Example Usage

------

#### 1. Train Classifier

Requires ***THREE*** arguments

- **pos_dir_or_file** (str): Absolute path to school homepage (positive) dump directory or list file
- **neg_dir_or_file** (str): Absolute path to non-school webpage (negative) dump directory or list file
- **model_dir** (str): Absolute path to the output directory where trained classifier will reside

> NOTE: If any of them is missing, program shows error messages with usage.

```bash
$ python classifier_train.py
usage: classifier_train.py [-h] pos_dir_or_file neg_dir_or_file model_dir
classifier_train.py: error: the following arguments are required: pos_dir_or_file, neg_dir_or_file, model_dir

$ python classifier_train.py -h
usage: classifier_train.py [-h] pos_dir_or_file neg_dir_or_file model_dir

positional arguments:
  pos_dir_or_file  Path to school homepage dump directory or list file
  neg_dir_or_file  Path to none-school webpage dump directory or list file
  model_dir        Path to a directory where trained classifier model will reside

optional arguments:
  -h, --help       show this help message and exit
```

> NOTE: If any of the directory and/or file does not exist, program terminates and throws error

```bash
$ python classifier_train.py /hello/world /this/is /the/way
Traceback (most recent call last):
  File "/Users/jhp/MSU/schooltext/classifier/classifier_train.py", line 26, in <module>
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), pos_dir_or_file)
FileNotFoundError: [Errno 2] No such file or directory: '/hello/world'
```

> NOTE: Successful execution will display Precision, Recall, Accuracy, and F1 score for each k-fold and program terminates with the average of each score.

```bash
$ python classifier_train.py /schooltext/pos_pages /schooltext/neg_pages /schooltext/model
279 positive docs and 325 negative docs imported

(...)

Precision: 0.896551724137931
Recall: 0.9629629629629629
Accuracy: 0.9333333333333333
F1: 0.9285714285714286
9 -split finished
=========================================
Avg. Precision: 0.9468692874504889
Avg. Recall: 0.9784391534391534
Avg. F1: 0.9615468410412887
Avg. Accuracy 0.9635519125683061
```

#### 2. School Homepage Classification

Requires ***FOUR*** arguments

- **data_dir** (str): Absolute path to data directory where input CSV file resides
  - Classification result will be stored in this directory in the form of "[source file name]_Result.csv"
- **source_data** (str): Name of the CSV formatted source file
  - CSV file is expected in following format:
    - [School Name], [School City], [School Zip Code]
- **model_dir** (str): Absolute path to classifier model directory where pre-trained classifier resides
- **split_index** (int): Specific classifier model choice among k-fold splits.
  - Refer to Precision, Recall, Accuracy, and F1 score of each model and choose specific model index
  - Stats of the pre-trained models can be found here

> NOTE: if any of them is missing, program shows error messages with usage information.

```bash
$ python classification.py
usage: classification.py [-h] data_dir source_data model_dir split_index
classification.py: error: the following arguments are required: data_dir, source_data, model_dir, split_index

$ python classification.py -h
usage: classification.py [-h] data_dir source_data model_dir split_index

positional arguments:
  data_dir     Path to data directory where input file reside
  source_data  CSV formatted source file
  model_dir    Path to model directory where trained classifier model reside
  split_index  Split index (k-fold) of the classifier model

optional arguments:
  -h, --help   show this help message and exit
```

> NOTE: If any of the directories and/or files do not exist, program terminates and throws error

```bash
$ python classification.py /data/dir source.csv /model/dir 3
Traceback (most recent call last):
  File "/Users/jhp/Projects/MSU/schooltext/classifier/classification.py", line 61, in <module>
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), data_dir)
FileNotFoundError: [Errno 2] No such file or directory: '/data/dir'
```

> NOTE: Since this is a long process, it is highly recommended that you execute this in the background preferably through screen (Linux/macOS) type of command

> NOTE: Following command example pipe std/err output to a log file and run it in the background

```bash
$ python classification.py /data/dir source.csv /model/dir 2 >& run.log &
```

### Requirements

------

- Python 3.6 or higher

- [NLTK Data](https://www.nltk.org/data.html) (stopwords)

  > NOTE: Downloading all items in NLTK data can take long. You may use either one of the methods below to avoid this issue.

  - Python Shell

  ```python
  import nltk
  nltk.download('stopwords')
  nltk.download('punkt')
  ```

  - Bash command-line

  ```bash
  $ python -m nltk.downloader stopwords punkt
  ```

- Firefox browser and geckodriver

  - `geckodriver` may be downloaded from its [GitHub repository](https://github.com/mozilla/geckodriver/releases).

  - ***macOS 10.15 Catalina*** or higher

    Due to the requirement from Apple that all programs must be notarized, geckodriver will not work on macOS Catalina or higher if you manually download it through another notarized program such as your browser. Instead please use [Homebrew](https://brew.sh/) to install `geckodriver`

    ```bash
    $ brew install geckodriver
    ```

- Additional python packages

  ```bash
  $ pip install -r requirements.txt
  ```

### Recommended Environment

------

Since active classification task could easily take 6+ hrs depending on the size of the school list, it is advisable that the classification task to be run on elsewhere other than your own machine. In following instruction, we provision a virtual machine (VM) in Azure cloud environment to run our classification task.

1. Setup Azure VM with Ubuntu 18.04 LTS image

- Follow instruction in [AzureVM markdown](AzureVM.md) document in the current folder

2. Setup RDP access on Azure Ubuntu VM

- Follow instruction in [UbuntuRDP markdown](UbuntuRDP.md) document in the current folder

3. Setup Python DEV environment on Azure Ubuntu VM

- Follow instruction in [PythonEnvSetup markdown](PythonEnvSetup.md) document in the current folder

