import os
import shutil
import configparser
from threading import Lock

# Setup
lockC = Lock() # Lock for Config
CONFIG = {}

# Functions
def save_ini(fpath = 'test.ini', dict_in = {}):
    '''Save a dictionary to an INI file'''
    if not dict_in:
        return 0 # Not saved
    file = open(fpath,"w")
    config_object = configparser.ConfigParser()        
    for section, options in dict_in.items():
        config_object.add_section(section)
        for key, value in options.items():
            config_object.set(section, key, str(value))
    config_object.write(file)
    file.close()
    return fpath

def read_ini(fpath):
    '''Read a dictionary from an INI file'''
    config_object = configparser.ConfigParser()
    with open(fpath,"r", encoding='utf-8') as file:
        config_object.read_file(file)
    output_dict={s:dict(config_object.items(s)) for s in config_object.sections()}
    return output_dict     
# NOTE: output_dict is a dictionary. Where values are also dicts, their keys are in lowercase

def loadConfig(lockC, forcereload = False):
    '''Return config file (read when necessary)'''
    with lockC:
        global CONFIG 
        if CONFIG and not forcereload:
            return CONFIG
        else:
            fpath = 'config.ini'
            if not os.path.isfile(fpath):
                shutil.copy('default_config.ini', 'config.ini')
            # READ config.ini and parse contents
            CONFIG = read_ini(fpath)
            print('Config Loaded from File')
            return CONFIG
        
def editConfigFile():
    '''Open config file for editing'''
    fpath = 'config.ini'
    if not os.path.isfile(fpath):
        shutil.copy('default_config.ini', 'config.ini')
    os.startfile(fpath)

# Keep for testing
if __name__ == '__main__':
    #import json

    # data = {'employee': {'name': 'John Doe', 'age': '35'},
    #             'job': {'title': 'Software Engineer', 'department': 'IT', 'years_of_experience': '10'},
    #             'address': {'street': '123 Main St.', 'city': 'San Francisco', 'state': 'CA', 'zip': '94102'}}

    #f = save_ini()
    #read_ini(f)

    # read config.txt and parse contents as json
    # with open('config.txt', 'r') as f:
    #     data = json.load(f)

    #f = save_ini('test.ini', data)
    di = read_ini('config.ini')

    print(di)

