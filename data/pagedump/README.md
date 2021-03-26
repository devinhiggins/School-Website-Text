# School Homepage Dump/Save

This tool aims to iterate over classification result CSV file, open each URL and save each school homepage as a HTML file.

- May be able to specify target state explicitly, otherwise it would look for entire U.S. school sheet
- Utilizes Tableau result file (e.g., AK_Schools_Tableau.csv)

### Example Usage

------


Requires ***THREE*** arguments

- **repo_dir** (str) : Absolute path to repository directory
  - School CSV file should be present in this directory
  - Previous runtime log may be present if tool has been excuted previously
    - These logs contains those schools that have already been dumped/saved
- **out_dir** (str) : Absolute path to output directory
  - School homepage will be saved in this directory as a HTML file
    - Format: SCH NAME_LCITY_LZIP.html
- **state** (str) : Optional Two-Letter State Abbreviations (by default this value is set as US)

> NOTE: if any of them (excluding state) is missing, program shows error messages with usage information.

```bash
$ python get_webpage_dump.py
usage: get_webpage_dump.py [-h] repo_dir out_dir [state]
get_webpage_dump.py: error: the following arguments are required: repo_dir, out_dir

$ python get_webpage_dump.py -h
usage: get_webpage_dump.py [-h] repo_dir out_dir [state]

positional arguments:
  repo_dir    Path to data directory where source csv file reside
  out_dir     Path to webpage dump/save directory
  state       Two-Letter State Abbreviations (default: US)

optional arguments:
  -h, --help  show this help message and exit
```

> NOTE: If any of the directories and/or files do not exist, program terminates and throws error

```bash
$ python get_webpage_dump.py /data/dir /data/dir
Traceback (most recent call last):
  File "/Users/jhp/Projects/MSU/schooltext/data/pagedump/get_webpage_dump.py", line 135, in <module>
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.repo_dir)
FileNotFoundError: [Errno 2] No such file or directory: '/data/dir'

$ python get_webpage_dump.py ~/Desktop ~/Desktop
Traceback (most recent call last):
  File "/Users/jhp/Projects/MSU/schooltext/data/pagedump/get_webpage_dump.py", line 139, in <module>
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.state+'_Schools_Tableau.csv')
FileNotFoundError: [Errno 2] No such file or directory: 'US_Schools_Tableau.csv'
```

> NOTE: Since this may be a long process, it is highly recommended that you execute this in the background preferably through screen (Linux/macOS) type of command

> NOTE: Following command example pipe std/err output to a log file and run it in the background

```bash
$ python get_webpage_dump.py /source/dir /output/dir MI >& run.log &
```

### Requirements

------

- Python 3.6 or higher

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

