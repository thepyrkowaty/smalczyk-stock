#!/bin/bash
source /home/debian/data/.venv/bin/activate
python3 /home/debian/data/other_data.py daily
python3 /home/debian/data/yahoo_data.py daily
