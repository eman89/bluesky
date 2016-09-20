'''
logHeader.py

Contains functions to write the header for the different log files

'''

# import packages
from datetime import datetime

def skyHeader():
    
    lines  = []
    parameters = " nTraf [-], Number of current Conflicts [-], Number of Current Intrusions [-]\n"
    
    lines = " ################################################### #\n"+ \
            " SKY LOG\n" + \
            " New run at: %s\n" %datetime.now().strftime('%Y-%m-%d / %H-%M-%S') + \
            " ################################################### #\n\n" + \
            parameters
    
    return lines
    
    
    
    

