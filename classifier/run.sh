#!/bin/bash
# Virtualenvwrapper settings:
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_VIRTUALENV=/home/schooltext/.local/bin/virtualenv
source ~/.local/bin/virtualenvwrapper.sh
workon schooltext

echo start UT250
echo $(date)
python classification.py /home/schooltext/Projects/MSU/schooltext/data UT_Schools_250.csv /home/schooltext/Projects/MSU/schooltext/model 6 >& run1_3.log
echo end UT250
echo $(date)

echo start UT500
echo $(date)
python classification.py /home/schooltext/Projects/MSU/schooltext/data UT_Schools_500.csv /home/schooltext/Projects/MSU/schooltext/model 6 >& run2_3.log
echo end UT500
echo $(date)

echo start UT750
echo $(date)
python classification.py /home/schooltext/Projects/MSU/schooltext/data UT_Schools_750.csv /home/schooltext/Projects/MSU/schooltext/model 6 >& run3_3.log
echo end UT750
echo $(date)

echo start UT1000
echo $(date)
python classification.py /home/schooltext/Projects/MSU/schooltext/data UT_Schools_1000.csv /home/schooltext/Projects/MSU/schooltext/model 6 >& run4_3.log
echo end UT1000
echo $(date)

echo start UTLast
echo $(date)
python classification.py /home/schooltext/Projects/MSU/schooltext/data UT_Schools_Last.csv /home/schooltext/Projects/MSU/schooltext/model 6 >& run5_3.log
echo end UTLast
echo $(date)

echo start AK250
echo $(date)
python classification.py /home/schooltext/Projects/MSU/schooltext/data AK_Schools_250.csv /home/schooltext/Projects/MSU/schooltext/model 6 >& run6_3.log
echo end AK250
echo $(date)

echo start AK508
echo $(date)
python classification.py /home/schooltext/Projects/MSU/schooltext/data AK_Schools_508.csv /home/schooltext/Projects/MSU/schooltext/model 6 >& run7_3.log
echo end AK508
echo $(date)

echo DONE
