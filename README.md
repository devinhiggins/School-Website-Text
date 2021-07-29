# School Text

School Text project aims to capture K-12 schools' mission statements to analyze if it is aligned with district's mission and conduct other analysis on top of it.

### Getting started

For your convenience, each tool has a separate set of packages list that you can choose to install instead of one, large package list. To get started with a specific tool, see the `README.md` file located in the specific tool's folder.

You can also find entire package list in the `project root` directory.

### Process Overview

------

![Process Overview](images/proc_overview.png)

#### 1. Identify School Homepage URL

In this process, we first focus on annotating *positive* (i.e., school homepage) page and *negative* (i.e., other webpage from Google search result) page in order to collect data for the classifier training. This step may be achieved by pure human effort or with the help of [Annotator Tool](https://gitlab.msu.edu/adsdatascience/schooltext/-/tree/master/annotator).

After enough data is collected, we then proceed to [School Homepage Classification](https://gitlab.msu.edu/adsdatascience/schooltext/-/tree/master/classifier). In this process, we use annotated data to build classifier model and use it on Google search results to find correct school homepage for each school.

Once classification is done, [Validatior Tool](https://gitlab.msu.edu/adsdatascience/schooltext/-/tree/master/validator) may be used to check the classifier's prediction results and further improve classifier by retraining with the newly collected school homepage data

#### 2. Find & Extract Mission Statement (within School Homepage)

In this process, we first [build One-Class SVM model](https://gitlab.msu.edu/adsdatascience/schooltext/-/tree/master/mission/oneclasssvm) using the human-collected mission statements  (i.e., positive data only) from K-12 schools in two different states namely AZ and NJ. 

We then utilize the model with various heuristics and insights we learned from qualitative researches conducted on analyzing K-12 schools mission statements, to [detert and extract mission statements](https://gitlab.msu.edu/adsdatascience/schooltext/-/tree/master/mission) within the school homepages.

#### 3. Data visualization via Tableau

In this process, Tableau is utilized to visualize the underlying data that is the final result of the above procedures. Please click [here](https://vis.test.itservices.msu.edu/t/PublicResearch/views/SchoolTextDashboard/SchoolTextDashboard?:iid=1) to access the visualization *(MSU VPN is required)* 


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

- [spaCy](https://spacy.io/) language model ([en_core_web_lg](https://spacy.io/models/en#en_core_web_lg))

  ```bash
  $ python -m spacy download en_core_web_lg
  ```

- Firefox browser and geckodriver

  - `geckodriver` may be downloaded from its [GitHub repository](https://github.com/mozilla/geckodriver/releases).

  - ***macOS 10.15 Catalina*** or higher

    Due to the requirement from Apple that all programs must be notarized, geckodriver will not work on macOS Catalina or higher if you manually download it through another notarized program such as your browser. Instead please use [Homebrew](https://brew.sh/) to install `geckodriver`

    ```bash
    $ brew install geckodriver
    ```

- Additional python packages (please refer to the each README for specific procedure)

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

### License

------

Released under the Apache License 2.0