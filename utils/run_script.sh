#!/bin/bash
source /home/debian/data/.venv/bin/activate
python3 /home/debian/smalczyk-stock/utils/other_data.py daily
python3 /home/debian/smalczyk-stock/utils/yahoo_data.py daily
