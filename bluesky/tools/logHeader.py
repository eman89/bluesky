'''
logHeader.py

Contains functions to write the header for the different log files

'''

def skyHeader():
    
    parameters = " nTraf [-], Number of current Conflicts [-], Number of Current Intrusions [-]\n"
    
    lines = " ################################################### #\n"+ \
            " SKY LOG\n" + \
            " ################################################### #\n\n" + \
            " Units for parameters:\n" + \
            parameters
    
    return lines


def snapHeader():

    parameters = " Call Sign [-], Spawn Time [s], AC Type [-], Latitude [deg],"   + \
                 " Longitude [deg], Altitude [m], TAS [m/s], GS [m/s], VS [m/s]," + \
                 " HDG [deg], TRK [deg], CMDALT [m], CMDTAS [m/s], CMDTRK [deg]," + \
                 " CMDVS [m/s], ASAS Active [-], ASASALT [m], ASASTAS [m/s],"     + \
                 " ASASTRK [deg], ASASVS [m/s], LNAV Active [-], VNAV Active [-],"+ \
                 " Origin [-], Destination [-]"
    
    lines = " ################################################### #\n"+ \
            " SNAP LOG\n" + \
            " ################################################### #\n\n" + \
            " Units for parameters:\n" + \
            parameters
    
    return lines

    
    
    
    

