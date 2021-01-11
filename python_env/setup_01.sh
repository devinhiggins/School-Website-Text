#!/bin/bash

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew update
brew upgrade
brew cleanup -s
brew cask cleanup

brew doctor
brew missing

brew install bash

sudo sh -c 'echo "/usr/local/bin/bash" >> /etc/shells'

chsh -s /usr/local/bin/bash

echo "# Load .bashrc if it exists" >> $HOME/.bash_profile
echo "test -f ~/.bashrc && source ~/.bashrc" >> $HOME/.bash_profile
echo "" >> $HOME/.bash_profile

brew install bash-completion ssh-copy-id wget

echo "# Activate bash completion" >> $HOME/.bash_profile
echo "if [ -f $(brew --prefix)/etc/bash_completion ]; then" >> $HOME/.bash_profile
echo "    source $(brew --prefix)/etc/bash_completion" >> $HOME/.bash_profile
echo "fi" >> $HOME/.bash_profile

brew install python
