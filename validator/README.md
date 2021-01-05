## Validation Tool

Validation tool allows you to easily mark true positive and false positive school homepages from classification results. 

- Unlike Annotation Tool, this tool only checks classification result (No Google Search)
- Produces True Positive result file and False Positive result file in the CSV format



### Example Usage

Requires ***TWO*** arguments

- **data_dir** (str): Absolute path to data directory where input CSV file resides
  - True Positive (Correct Homepage) list will be generated here (if it does not exist) in the form of "[source file name]_TP.csv"
  - False Positive (Incorrect Homepage) list will be generated here (if it does not exist) in the form of [source file name]_FP.csv
- **source_data** (str): Name of CSV formatted source file
  - CSV file is expected to have NO HEADER and adhere to following format: 
    - [School Name],[City],[zipcode],[Predicted School Homepage URL]

If either of them is missing, program shows error messages with usage

```bash
$ python validator_v1.py
usage: validator_v1.py [-h] data_dir source_data
AnnotateTool.py: error: the following arguments are required: data_dir, source_data

$ python validator_v1.py -h
usage: validator_v1.py [-h] data_dir source_data

positional arguments:
  data_dir     Path to data directory where input source file reside
  source_data  CSV formatted source file (output of the classification tool)

optional arguments:
  -h, --help   show this help message and exit
```

If the data directory does not exists and/or source file does not exists program terminates and throws error

```bash
$ python validator_v1.py /this/is/the/way ihavespoken.csv
Traceback (most recent call last):
  File "/Users/jhp/Projects/MSU/schooltext/validator/validator_v1.py", line 45, in <module>
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), data_dir)
FileNotFoundError: [Errno 2] No such file or directory: '/this/is/the/way'
```

If all requirements are met program starts by opening a Firefox browser and performing a Google search. Tk GUI will appear once initial tasks are completed

```bash
$ python validator_v1.py /Users/jhp/Projects/MSU/schooltext/jhp/data/national1_dump NationalNew_Done.csv
TP not-completed previously
FP not-completed previously
```

**Tk GUI**

![Tk GUI](images/tkgui.png)

User may stop at any point by clicking `Quit` button or simply by killing the browser & GUI and resume by starting program again. The application is designed to check for processed schools before starting the annotation task



### Requirement

- Python 3.6 or higher, with Tk GUI toolkit (Tkinter)

  - ***Tkinter known issues***

    - **Ubuntu**

      Although Tkinter is shipped with Python 3.x, if you install Python 3.x through apt and pyenv it does not include `tkinter` and import statement will fail. Please install tk using following command:

      ```bash
      $ sudo apt install python3-tk
      ```

    - **macOS 10.15 Catalina** or higher

      If you use `homebrew` ([link](https://brew.sh/)) to manage your Python 3.x environment, you should be good to go; however if you use `asdf` ([link](https://asdf-vm.com/#/)) or `pyenv` to manage your Python 3.x environment(s), you probably would experience following error

      ```python
      ModuleNotFoundError: No module named '_tkinter'
      ```

       TL;DR You need to remove existing Python 3.x and set the environment variables mentioned in `tcl-tk` caveats and this [GitHub comment](https://github.com/pyenv/pyenv/issues/1375#issuecomment-533182043) when installing new Python 3.x.

      1. Remove existing Python 3.x

         ```bash
         $ asdf plugin remove python
         ```

         OR

         ```bash
         $ pyenv uninstall 3.8.6
         ```

         

      2. Ensure you have the latest `tcl-tk` via `homebrew` and then pay attention to its caveats:

      ```bash
      $ brew install tcl-tk
      $ brew info tcl-tk
      tcl-tk: stable 8.6.10 (bottled) [keg-only]
      ...
      ==> Caveats
      tcl-tk is keg-only, which means it was not symlinked into /usr/local,
      because tk installs some X11 headers and macOS provides an (older) Tcl/Tk.
      
      If you need to have tcl-tk first in your PATH run:
        echo 'export PATH="/usr/local/opt/tcl-tk/bin:$PATH"' >> ~/.zshrc
      
      For compilers to find tcl-tk you may need to set:
        export LDFLAGS="-L/usr/local/opt/tcl-tk/lib"
        export CPPFLAGS="-I/usr/local/opt/tcl-tk/include"
      
      For pkg-config to find tcl-tk you may need to set:
        export PKG_CONFIG_PATH="/usr/local/opt/tcl-tk/lib/pkgconfig"
      ...
      ```

      You'll also need to know about pyenv's `PYTHON_CONFIGURE_OPTS`, `--with-tcltk-includes`, and `--with-tcltk-libs` (`asdf` Python uses `pyenv` under the hood thus same option applies)

      3. Re-install Python 3.x with the environment variables

      ```bash
      $ env \
        PATH="$(brew --prefix tcl-tk)/bin:$PATH" \
        LDFLAGS="-L$(brew --prefix tcl-tk)/lib" \
        CPPFLAGS="-I$(brew --prefix tcl-tk)/include" \
        PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig" \
        CFLAGS="-I$(brew --prefix tcl-tk)/include" \
        PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk)/include' --with-tcltk-libs='-L$(brew --prefix tcl-tk)/lib -ltcl8.6 -ltk8.6'" \
        asdf install python 3.8.6 (pyenv install 3.8.6)
      ```

      

- Firefox browser and `geckodriver`

  - `geckodriver` may be downloaded from its GitHub repo ([link](https://github.com/mozilla/geckodriver/releases))

  - ***macOS 10.15 Catalina*** or higher

    Due to the requirement from Apple that all programs must be notarized, geckodriver will not work on Catalina if you manually download it through another notarized program such as your browser. Instead please use Homebrew ([link](https://brew.sh/)) to install `geckodriver`

    ```bash
    $ brew install geckodriver
    ```

    

- Additional python packages

  ```bash
  $ pip install -r requirements.txt
  ```

  

