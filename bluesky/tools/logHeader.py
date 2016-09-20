'''
logHeader.py

Contains functions to write the header for the different log files

'''

def skyHeader():
    
    lines  = []
    parameters = " nTraf [-], Number of current Conflicts [-], Number of Current Intrusions [-]\n"
    
    lines = " ################################################### #\n"+ \
            " SKY LOG\n" + \
            " ################################################### #\n\n" + \
            parameters
    
    return lines


def snapHeader():
    
    lines  = []
    parameters = " nTraf [-], Number of current Conflicts [-], Number of Current Intrusions [-]\n"
    
    lines = " ################################################### #\n"+ \
            " SNAP LOG\n" + \
            " ################################################### #\n\n" + \
            parameters
    
    return lines

    
    
    
    

