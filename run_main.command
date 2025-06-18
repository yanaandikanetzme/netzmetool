#!/usr/bin/env bash
cd "/Users/purbajati/Documents/source/NetzmeTool" || exit
pip3 install pyinstaller
pip3 install -r requirements.txt
nohup python3 main.py > /dev/null 2>&1 &
disown
exit
