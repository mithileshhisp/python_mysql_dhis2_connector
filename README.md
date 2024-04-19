### Create Enrollments into DHIS2 from mysql connection

#### Required Libraries

- `mysql-connector-python`
- `requests`
- `pandas`
- `pip install pandas`
- `pip install openpyxl`


- `1) sudo apt-get install python-pip`
- `2) sudo apt-get install python-pip`
- `3) pip install mysql-connector-python requests pandas`
- `4) pip install pandas`
- `5) pip install openpyxl`

#### Installation

```bash
pip install mysql-connector-python requests pandas
```

#### Usage

1. Clone the repository.
2. Navigate to the project directory.
3. Run the main script:

```bash
python main_script.py
```

`@reboot sudo -u dhis /var/dhis/tomcat-amrit/bin/startup.sh
`19 16 * * * /bin/bash /home/psmri/mysql_dhis2_connector_amrti-104/python.sh >> /home/psmri/cronlogs104Enrollment.txt 2>&1`
`14 16 * * * /bin/bash /home/psmri/mysql_dhis2_connector_amrti-104/pythonEvent104.sh >> /home/psmri/event104cronlogs.txt 2>&1`

`make .sh file to executive`
`chmod +x pythonEvent104.sh (edited)`

### Author

- **mithileshhisp** - [GitHub Profile](https://github.com/mithileshhisp)