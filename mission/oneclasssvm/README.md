# One-Class SVM for Text Classification

Classification models are usually based on training using both positive and negative examples (just like the basic SVM paradigm suggests); however in our quest to mission statement extraction, we are interested in using *only* positive examples that is about 4K human collected mission statements.

### Train, Test, and Save One-Class SVM

Requires ***THREE*** arguments

- **data_dir** (str): Path to data directory where data source files reside

- **train_data** (str): CSV formatted data file that will be used for training

- **test_data** (str): CSV formatted data file that will be used for testing

> NOTE: data_dir will be used to store trained model and its score log

```bash
$ python oneclasssvm_train.py
usage: oneclasssvm_train.py [-h] data_dir train_data test_data
oneclasssvm_train.py: error: the following arguments are required: data_dir, train_data, test_data

$ python oneclasssvm_train.py -h
usage: oneclasssvm_train.py [-h] data_dir train_data test_data

positional arguments:
  data_dir    Path to data directory where input file reside
  train_data  CSV formatted data file used for training
  test_data   CSV formatted data file used for testing

optional arguments:
  -h, --help  show this help message and exit
```

> NOTE: If any of the directory and/or file does not exist, program terminates and throws error

```bash
$ python oneclasssvm_train.py /hello/world helloworld.csv helloworld.csv
Traceback (most recent call last):
  File "/Users/jhp/Projects/MSU/schooltext/mission/oneclasssvm/oneclasssvm_train.py", line 61, in <module>
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), data_dir)
FileNotFoundError: [Errno 2] No such file or directory: '/hello/world'
```

Upon successful execution, program stores trained model in the data_dir as well as generates logfile that contains model score such as Precision, Recall, Accuracy and F1.
