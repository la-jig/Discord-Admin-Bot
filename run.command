#!/bin/bash

cd "$(dirname "$0")" || exit

clear
python3 -u main.py

echo " "
echo "Process finished with exit code $?"
exit $?