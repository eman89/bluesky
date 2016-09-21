'''
logHeader.py

Contains functions to write the header for the different log files

'''

def skyHeader():    
    parameters = "nTraf [-], Number of current Conflicts [-], Number of Current Intrusions [-]"
    
    lines      = "##################### #\n"   + \
                 "SKY LOG\n"                   + \
                 "##################### #\n\n" + \
                 "Units for parameters:\n"     + \
                 parameters + "\n"             + \
                 "NOTE: ORDER OF PARAMETERS VARIES FROM ABOVE LIST!\n" + \
                 "      See below for actual order\n"
                 
                 
    return lines


def snapHeader():
    parameters = "Call Sign [-], Spawn Time [s], Latitude [deg], Longitude [deg], "  + \
                 "Altitude [m], TAS [m/s], VS [m/s], HDG [deg], CMDALT [m], "        + \
                 "CMDTAS [m/s], CMDTRK [deg], CMDVS [m/s], ASAS Active [-], "        + \
                 "ASASTAS [m/s], ASASTRK [deg], LNAV Active [-], Origin [-], "       + \
                 "Destination [-]"
                 
    lines      = "##################### #\n"    + \
                 "SNAP LOG\n"                   + \
                 "##################### #\n\n"  + \
                 "Units for parameters:\n"      + \
                 parameters + "\n"              + \
                 "NOTE: ORDER OF PARAMETERS VARIES FROM ABOVE LIST!\n" + \
                 "      See below for actual order\n"
    
    return lines
    

def cflHeader():
    
    parameters =  "Call Sign id1 [-], Latitude id1 [deg], Longitude id1 [deg], "   + \
                  "Altitude id1 [m], TAS id1 [m/s], VS id1 [m/s], HDG id1 [deg], " + \
                  "ASAS Active id1 [-], ASASTAS id1 [m/s], ASASTRK id1 [deg], "    + \
                  "CPA LAT id1 [deg], CPA LON id1 [deg], CPA ALT id1 [m], "        + \
                  "Tinconf id1 [s], Toutconf id1 [s], Tcpa id1[s],"                + \
                  "n active Conflicts with id1, "                                  + \
                  "Call Sign id2 [-], Latitude id2 [deg], Longitude id2 [deg], "   + \
                  "Altitude id2 [m], TAS id2 [m/s], VS id2 [m/s], HDG id2 [deg], " + \
                  "ASAS Active id2 [-], ASASTAS id2 [m/s], ASASTRK id1 [deg], "    + \
                  "CPA LAT id2 [deg], CPA LON id2 [deg], CPA ALT id2 [m], "        + \
                  "Tinconf id2 [s], Toutconf id2 [s], Tcpa id2[s], "               + \
                  "n active Conflicts with id1"
    
    lines      = "##################### #\n"    + \
                 "CFL LOG\n"                   + \
                 "##################### #\n\n"  + \
                 "Units for parameters:\n"      + \
                 parameters + "\n"              + \
                 "NOTE: ORDER OF PARAMETERS VARIES FROM ABOVE LIST!\n" + \
                 "      See below for actual order\n"
    
    return lines
                  



    
    
    
    

