#!/usr/local/bin/bash

echo "Check and update homebrew"
brew update
brew upgrade
brew cleanup -s
brew cask cleanup

brew doctor
brew missing

echo "Install geckodriver"
brew install geckodriver

PIP_REQUIRE_VIRTUALENV="0" pip3 install -U pip setuptools
cd /usr/local/bin
rm -f pip
ln -s $(readlink pip3) pip

PIP_REQUIRE_VIRTUALENV="0" pip3 install -U virtualenv virtualenvwrapper

rm -rf ~/.virtualenv ~/Library/Application\ Support/pip
mkdir -p ~/.virtualenv ~/Library/Application\ Support/pip
echo "[install]" >> ~/Library/Application\ Support/pip/pip.conf
echo "require-virtualenv = true" >> ~/Library/Application\ Support/pip/pip.conf
echo "" >> ~/Library/Application\ Support/pip/pip.conf
echo "[uninstall]" >> ~/Library/Application\ Support/pip/pip.conf
echo "require-virtualenv = true" >> ~/Library/Application\ Support/pip/pip.conf

rm -f ~/.bashrc
echo "gpip(){" >> ~/.bashrc
echo '    PIP_REQUIRE_VIRTUALENV="0" python3 -m pip "$@"' >> ~/.bashrc
echo "}" >> ~/.bashrc

# .bash_profile setup
rm -f ~/.bash_profile
echo "# Terminal Setting" >> ~/.bash_profile
echo 'export PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h:\[\033[33;1m\]\w\[\033[m\]\$ "' >> ~/.bash_profile
echo "export CLICOLOR=1" >> ~/.bash_profile
echo "export LSCOLORS=ExFxBxDxCxegedabagacad" >> ~/.bash_profile
echo "" >> ~/.bash_profile

echo "# Load .bashrc if it exists" >> ~/.bash_profile
echo "test -f ~/.bashrc && source ~/.bashrc" >> ~/.bash_profile
echo "" >> ~/.bash_profile

echo "# Bash-Completion" >> ~/.bash_profile
echo "if [ -f $(brew --prefix)/etc/bash_completion ]; then" >> ~/.bash_profile
echo "    source $(brew --prefix)/etc/bash_completion" >> ~/.bash_profile
echo "fi" >> ~/.bash_profile
echo "" >> ~/.bash_profile

echo "# Alias" >> ~/.bash_profile
echo "alias ls='ls -GFh'" >> ~/.bash_profile
echo "alias ll='ls -GFhlatr'" >> ~/.bash_profile
echo "" >> ~/.bash_profile

echo "# VirtualEnvs" >> ~/.bash_profile
echo "export WORKON_HOME=~/.virtualenvs" >> ~/.bash_profile
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3" >> ~/.bash_profile
echo "export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv" >> ~/.bash_profile
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bash_profile
echo "" >> ~/.bash_profile

source ~/.bash_profile
mkvirtualenv schooltext

workon schooltext
pip install -U pip
pip install -U beautifulsoup4
pip install -U selenium
pip install -U numpy
pip install -U pandas
