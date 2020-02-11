from __future__ import print_function
import sys
import os
import yaml
import datetime

import requests
from icalendar import Calendar, Event

import gspread
from oauth2client.service_account import ServiceAccountCredentials

cals = {}
initiatives = {}
categories = {}
baseaddress = {}
eventcounter = 0

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def countNumbersInString(inputString):
    return sum(list(map(lambda x:1 if x.isdigit() else 0,set(inputString))))

def read_calendar_list(config):
    """ Read Google Sheet file with calendar list """
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    #creds = ServiceAccountCredentials.from_json_keyfile_name(config['gspread-secret-json-filename'], scope)
    creds = ServiceAccountCredentials.from_json_keyfile_name('merge-ics-online-secret.json', scope)    
    client = gspread.authorize(creds)
    sheet = client.open(config['source']).sheet1
    cal_list = sheet.get_all_records()
    return cal_list

def read_config(filename):
    """Read YAML config file"""
    with open(filename, 'r') as f:
        return yaml.load(f)


def download_calendar(url):
    """Download and parse ics file"""
    req = requests.get(url)
    cal = Calendar.from_ical(req.text)
    return cal


def read_calendar(filename):
    """Parse local ics file"""
    with open(filename, 'r') as f:
        cal = Calendar.from_ical(f)
    return cal

def write_calendar(options, filename):
    #Create and write ics file"
    print('Writing ics...')
    cal = Calendar()
    timezones_cache = []
    global eventcounter
    for key, value in options.items():
        cal.add(key, value)
    for source_id, thiscal in cals.items():
        for timezone in thiscal.walk('VTIMEZONE'):
            if timezone['tzid'] not in timezones_cache:
                timezones_cache.append(timezone['tzid'])
                cal.add_component(timezone)
        for event in thiscal.walk('VEVENT'):
            event_copy = Event(event)
            # Erase categoryies with the one defined in the source file
            # To add a new cateogyr, should be: event_copy.add('category', categories[source_id])
            event_copy['categories'] = categories[source_id]
            
            # Check if address exists, if not add baseaddress, then try to check if Postal Code present
            if 'LOCATION' not in event_copy:
                event_copy['LOCATION'] = baseaddress[source_id]
            else:
                if countNumbersInString(event_copy['LOCATION']) < 3:                
                    event_copy['LOCATION'] = event_copy['LOCATION'] + ', ' +  baseaddress[source_id]
            cal.add_component(event_copy)
            eventcounter = eventcounter + 1 
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())

def set_log(logpath):
    class Logger(object):
        def __init__(self):
            script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
            abs_file_path = os.path.join(script_dir, logpath)
            fullfilename = abs_file_path + "/log_merge_ics.log"
            self.terminal = sys.stdout
            self.log = open(fullfilename, "a")

        def write(self, message):
            self.terminal.write(message)            
            if message != '\n':
                self.log.write(str(datetime.datetime.now()))
                self.log.write(" - ")  
            self.log.write(message)  

        def flush(self):
            #this flush method is needed for python 3 compatibility.
            #this handles the flush command by doing nothing.
            #you might want to specify some extra behavior here.
            pass    

    sys.stdout = Logger()

def main():

    # Get the name of the config file
    if len(sys.argv) != 2:
        print('Usage:')
        print('   merge-ics <config_file>')
        return 1
    config_file = sys.argv[1]

    # Read config
    print('Reading config..')
    try:
        config = read_config(config_file)
        
    except IOError:
        print('Unable to open ' + config_file)
        return 1
    except yaml.YAMLError:
        print('Unable to parse ' + config_file)
        return 1

    # Read calendar list
    print('Reading calendar list..')
    try:
        cal_list = read_calendar_list(config)
        
    except IOError:
        print('Unable to open calendar list. Check gspread-secret-json-filename and source specified in ' + config_file)
        return 1
    except yaml.YAMLError:
        print('Unable to parse ' + config_file)
        return 1                

    # Open Log file
    if not os.path.isdir(config['destination']['folder']):
            os.mkdir(config['destination']['folder'])
    set_log(config['destination']['folder'])
    print('Début')

    # Read/download and parse input calendars  
    print("Number of calendars to read: "+ str(len(cal_list)))    
    for cal_id, cal_source in enumerate(cal_list):
        if 'URL' in cal_source:
            try:
                cals[cal_id] = download_calendar(cal_source['URL'])                
                initiatives[cal_id] = cal_source['INITIATIVE']                
                print('Read ics from ' + initiatives[cal_id] + " (" + str(cal_id+1)+ "/" + str(len(cal_list)) + ")")
                categories[cal_id] = cal_source['CATEGORIE']
                baseaddress[cal_id] = cal_source['BASEADDRESS']
            except requests.exceptions.RequestException:
                print('Unable to download ' + cal_source['URL'])
            except ValueError:
                print('Unable to parse ' + cal_source['URL'])

    # Create and write output calendars    
    try:        
        completefilename = config['destination']['folder'] + '/' + config['destination']['filename']
        write_calendar(config['destination']['options'], completefilename)
    except IOError:
        print('Unable to write ' + sink['filename'])
    except ValueError:
        print('Unable to create calendar ' + sink['filename'])

    # End program
    print("Output size: "+ str(os.path.getsize(completefilename)/1000) + " kbytes")
    print(str(eventcounter) + " events written to file")
    print("Good end")
    print("--------------------------------------------------------")


main()