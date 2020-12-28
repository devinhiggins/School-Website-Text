## Annotation Tool

Annotation tool allows you to easily mark positive and negative school homepages from Google Search results. Some of the use cases include, but not limited to

- Initial school homepage gathering for classifier model training
- Finding correct school homepages for those schools with false positive homepages



### Requirement

- Python 3.6 or higher, with Tk GUI toolkit (Tkinter)

  - ***Tkinter*** known issues

    - Ubuntu

      Although Tkinter is shipped with Python 3.x, if you install Python 3.x through apt and pyenv it does not include `tkinter` and import statement will fail. Please install tk using following command:

      ```bash
      $ sudo apt install python3-tk
      ```

    - macOS 10.15 Catalina or higher

      If you use `homebrew` ([link](https://brew.sh/)) to manage your Python 3.x environment, you should be good to go; however if you use `asdf` ([link](https://asdf-vm.com/#/)) or `pyenv` to manage your Python 3.x environment(s), you probably would experience following error

      ```python
      ModuleNotFoundError: No module named '_tkinter'
      ```

       TL;DR You need to remove existing Python 3.x and set the environment variables mentioned in `tcl-tk` caveats and this [GitHub comment](https://github.com/pyenv/pyenv/issues/1375#issuecomment-533182043) when installing new Python 3.x.

      1. Ensure you have the latest `tcl-tk` via `homebrew` and then pay attention to its caveats:

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

  - macOS 10.15 Catalina or higher

    Due to the requirement from Apple that all programs must be notarized, geckodriver will not work on Catalina if you manually download it through another notarized program such as your browser. Instead please use Homebrew ([link](https://brew.sh/)) to install `geckodriver`

    ```bash
    $ brew install geckodriver
    ```

    

- Additional python packages

  ```bash
  $ pip install -r requirements.txt
  ```

  

