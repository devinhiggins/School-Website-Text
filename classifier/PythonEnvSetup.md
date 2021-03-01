# Azure Ubuntu VM for Classification (3/3)

This instruction deals with setting up a Python 3 programming environment on Azure Ubuntu 18.04 VM

> NOTE: In order to complete this instruction, you should have a non-root user with sudo privileges on Azure Ubuntu 18.04 VM.

**1. Update and Upgrade Ubuntu VM to ensure Python 3 shipped with the system is up-to-date**

```bash
$ sudo apt update
$ sudo apt upgrade
```

**2. Install pip**

pip is a Python package manager. It is able to install, uninstall, update, and manage libraries or modules for Python projects

```bash
$ sudo apt install python3-pip
```

Once pip is installed, Python packages can be installed by typing:

```bash
$ pip3 install -U [Python package name]
```

**3. (Optional) Install Additional Tools**

This is optional step to install packages and development tools to ensure a robust programming environment

```bash
$ sudo apt install build-essential libssl-dev libffi-dev python3-dev
```

**4. Install virtualenv and virtualenvwrapper to setup a virtual environment**

>  NOTE: Virtual environment enables an isolated space on the Azure Ubuntu VM for Python projects, ensuring that each of your projects can have have its own set of dependencies that won't disrupt any of other projects.

```bash
$ pip3 install -U virtualenv virtualenvwrapper
```

**5. Create a folder where virtual environments will be stored. May be named anything but here we use conventional name `.virtualenvs`**

```bash
$ mkdir -p ~/.virtualenvs
```

**6. Add following lines to `.bashrc` file in the home folder in order to properly set envrionment variables for virtualenv and virtualenvwrapper**

```bash
$ echo "" >> ~/.bashrc
$ echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
$ echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
$ echo "export VIRTUALENVWRAPPER_VIRTUALENV=/home/schooltext/.local/bin/virtualenv" >> ~/.bashrc
$ echo "source ~/.local/bin/virtualenvwrapper.sh" >> ~/.bashrc
```

**7. Activate these changes by typing**

```bash
$ source .bashrc
```

**8. Create a virtual environment**

```bash
$ mkvirtualenv schooltext
created virtual environment CPython3.6.9.final.0-64 in 530ms
  creator CPython3Posix(dest=/home/schooltext/.virtualenvs/schooltext, clear=False, no_vcs_ignore=False, global=False)
  seeder FromAppData(download=False, pip=bundle, setuptools=bundle, wheel=bundle, via=copy, app_data_dir=/home/schooltext/.local/share/virtualenv)
    added seed packages: pip==20.3.3, setuptools==51.3.3, wheel==0.36.2
  activators BashActivator,CShellActivator,FishActivator,PowerShellActivator,PythonActivator,XonshActivator
virtualenvwrapper.user_scripts creating /home/schooltext/.virtualenvs/schooltext/bin/predeactivate
virtualenvwrapper.user_scripts creating /home/schooltext/.virtualenvs/schooltext/bin/postdeactivate
virtualenvwrapper.user_scripts creating /home/schooltext/.virtualenvs/schooltext/bin/preactivate
virtualenvwrapper.user_scripts creating /home/schooltext/.virtualenvs/schooltext/bin/postactivate
virtualenvwrapper.user_scripts creating /home/schooltext/.virtualenvs/schooltext/bin/get_env_details
(schooltext) schooltext@SchoolTextVM:~$
```

> NOTE: Virtual environment name may be any name of your preference. Once virtual environment is created by `mkvirtualenv`, it is automatically activated; however if it is not activated use next command to activate it.

**9. Activate virtual environment**

```bash
$ workon schooltext
(schooltext) schooltext@SchoolTextVM:~$
```

>  NOTE: Once virtual environment is created, you will only use this command and the next command to activate or deactivate a virtual environment 

**10. Test virtual environment**

```bash
(schooltext) schooltext@SchoolTextVM:~$ python --version
Python 3.6.9

(schooltext) schooltext@SchoolTextVM:~$ pip --version
pip 20.3.3 from /home/schooltext/.virtualenvs/schooltext/lib/python3.6/site-packages/pip (python 3.6)
```

> NOTE: Within the virtual environment, you can use the command `python` instead of `python3`, and `pip` instead of `pip3` if you would prefer. If you intend to use Python 3 on your machine outside of an environment, you will need to use the `python3` and `pip3` commands exclusively.

**11. Deactivate virtual environment**

```bash
(schooltext) schooltext@SchoolTextVM:~$ deactivate
$
```

