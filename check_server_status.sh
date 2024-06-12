#!/bin/bash

# Navigate to the directory where main.py is located
cd /home/psmri/check_server_status

# Activate virtual environment if needed (replace 'venv/bin/activate' with your venv path)
# source venv/bin/activate

# Run the main.py script
python3 check_server_status.py

# Deactivate virtual environment if activated
# deactivate

# Navigate for saans
##cd /var/odk-dhis2-saans
##python3 main.py
