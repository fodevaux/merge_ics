# merge_ics
Merge several calendars in ICS format to a single ICS file

# Instructions 

1) List the calendars you with to merge
In this version, the calendar list is provided in a Google Spreadsheet for an easy update.
Example here: https://docs.google.com/spreadsheets/d/1JYbmnCG5gE6OmcNhw_OvnvZ7JCcBsDueAEVgRzENGZA/edit?usp=sharing
Create your own Google Spreadsheet with the calendars you wish to import

2) Connect merge_ics to the Google Spreadsheet
You must authorize merge_ics to connect to this Google Spreadsheet.
Follow the instructions for the "Signed Credentials" method, as described in https://gspread.readthedocs.io/en/latest/oauth2.html
Download your JSON Service Account key copy it to the current folder and rename it "merge-ics-online-secret.json" for example
Go to your spreadsheet and share it with the client_email, as described in the link above

3) Configure the config.txt file
gspread-secret-json-filename: Name of your JSON Service Account key file created above (ex: merge-ics-online-secret.json)
source: share the name of your Google Spreadsheet file
destination: Check destination folder and resulting ics filename
See https://pypi.org/project/merge_ics/ for more info

4) Check your system has the correct Python libraries
Python libraries used: __future__, sys, os, yaml, datetime, requests, icalendar, gspread, oauth2client.service_account 

5) Execute the merge_ics program
Command line: python3 merge_ics.py config.txt

