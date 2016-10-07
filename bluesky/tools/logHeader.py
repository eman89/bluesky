'''
logHeader.py

Contains functions to write the header for the different log files

'''

def skyHeader():    
    parameters = "SimTime [s], nTraf [-], nTraf Expt Area [-], nConflicts Now [-], nIntrusions Now [-]"
    
    lines      = "##############################\n"   + \
                 "SKY LOG\n"                          + \
                 "Summary Data\n"                     + \
                 "##############################\n\n" + \
                 "Parameters [Units]:\n"              + \
                 parameters + "\n"       
                 
    return lines


def snapHeader():
    parameters = "SimTime [s], Call Sign [-], Spawn Time [s], Latitude [deg], Longitude [deg], "  + \
                 "Altitude [m], TAS [m/s], VS [m/s], HDG [deg], CMDALT [m], "                     + \
                 "CMDTAS [m/s], CMDTRK [deg], CMDVS [m/s], LNAV Active [-], "                     + \
                 "Origin [-], Destination [-], ASAS Active [-], ASASTAS [m/s], "                  + \
                 "ASASTRK [deg]"
                 
    lines      = "##############################\n"    + \
                 "SNAP LOG\n"                          + \
                 "Airspace Snapshot Data\n"            + \
                 "##############################\n\n"  + \
                 "Parameters [Units]:\n"               + \
                 parameters + "\n"
    
    return lines
    

def cflHeader():
    parameters =  "SimTime [s], Call Sign id1 [-], Call Sign id2 [-], tinconf [s], toutconf [s], " + \
                  "tcpa [s], Latitude id1 [deg], Longitude id1 [deg], Altitude id1 [m], "          + \
                  "TAS id1 [m/s], VS id1 [m/s], HDG id1 [deg], Latitude CPA id1 [deg], "           + \
                  "Longitude CPA id1 [deg], Altitude CPA id1 [m], ASAS Active id1 [-], "           + \
                  "ASASTAS id1 [m/s], ASASTRK id1 [deg], nSecondary Conflicts id1 [-], "           + \
                  "Latitude id2 [deg], Longitude id2 [deg], Altitude id2 [m], "                    + \
                  "TAS id2 [m/s], VS id2 [m/s], HDG id2 [deg], Latitude CPA id2 [deg], "           + \
                  "Longitude CPA id2 [deg], Altitude CPA id2 [m], ASAS Active id2 [-], "           + \
                  "ASASTAS id2 [m/s], ASASTRK id2 [deg], nSecondary Conflicts id2 [-]"
    
    lines      = "##############################\n"    + \
                 "CFL LOG\n"                           + \
                 "Conflict Data\n"                     + \
                 "##############################\n\n"  + \
                 "Parameters [Units]:\n"               + \
                 parameters + "\n"
    
    return lines
    

def instHeader():
    parameters =  "SimTime [s], Call Sign id1 [-], Call Sign id2 [-], tinconf [s], toutconf [s], " + \
                  "tcpa [s], Latitude id1 [deg], Longitude id1 [deg], Altitude id1 [m], "          + \
                  "TAS id1 [m/s], VS id1 [m/s], HDG id1 [deg], Latitude CPA id1 [deg], "           + \
                  "Longitude CPA id1 [deg], Altitude CPA id1 [m], ASAS Active id1 [-], "           + \
                  "ASASTAS id1 [m/s], ASASTRK id1 [deg], "                                         + \
                  "Latitude id2 [deg], Longitude id2 [deg], Altitude id2 [m], "                    + \
                  "TAS id2 [m/s], VS id2 [m/s], HDG id2 [deg], Latitude CPA id2 [deg], "           + \
                  "Longitude CPA id2 [deg], Altitude CPA id2 [m], ASAS Active id2 [-], "           + \
                  "ASASTAS id2 [m/s], ASASTRK id2 [deg], "                                         + \
                  "nTraf, nTraf Expt Area [-]"
    
    lines      = "##############################\n"    + \
                 "INST LOG\n"                          + \
                 "Instantaneous Conflict Data\n"       + \
                 "##############################\n\n"  + \
                 "Parameters [Units]:\n"               + \
                 parameters + "\n"
    
    return lines
    

def intHeader():
    parameters =  "SimTime [s], Call Sign id1 [-], Call Sign id2 [-], Max Intrusion Severity, " + \
                  "Horizontal Intrusion at Max IS [-], Vertical Intrusion at MAX IS [-], "      + \
                  "tinconf [s], toutconf [s], "                                                 + \
                  "Latitude id1 [deg], Longitude id1 [deg], Altitude id1 [m], "                 + \
                  "TAS id1 [m/s], VS id1 [m/s], HDG id1 [deg], "                                + \
                  "ASAS Active id1 [-], ASASTAS id1 [m/s], ASASTRK id1 [deg], "                 + \
                  "Latitude id2 [deg], Longitude id2 [deg], Altitude id2 [m], "                 + \
                  "TAS id2 [m/s], VS id2 [m/s], HDG id2 [deg], "                                + \
                  "ASAS Active id2 [-], ASASTAS id2 [m/s], ASASTRK id2 [deg]" 
                  
    warning    = "NOTE!!! 9999.9999 INDICATES THAT AN INTRUSION WAS LOGGED AFTER AN AIRCRAFT WAS DELETED!!!"
    
    lines      = "##############################\n"    + \
                 "INT LOG\n"                          + \
                 "Intrusion (LOS) Data\n"       + \
                 "##############################\n\n"  + \
                 "Parameters [Units]:\n"               + \
                 parameters + "\n\n" + warning + "\n\n"
    
    return lines
    
    
def flstHeader():
    parameters = "SimTime [s], Call Sign [-], flightDuration [s], Distance2D [m], "               + \
                 "Distance3D [m], Work Done [J], Route Efficiency [-],"                           + \
                 "Spawn Time [s], Latitude [deg], Longitude [deg], "                              + \
                 "Altitude [m], TAS [m/s], VS [m/s], HDG [deg], CMDALT [m], "                     + \
                 "CMDTAS [m/s], CMDTRK [deg], CMDVS [m/s], LNAV Active [-], "                     + \
                 "Origin [-], Destination [-], ASAS Active [-], ASASTAS [m/s], "                  + \
                 "ASASTRK [deg], 2D Dist2Dest [m]"
                 
    lines      = "##############################\n"    + \
                 "FLST LOG\n"                          + \
                 "Flight Efficiency Data\n"            + \
                 "##############################\n\n"  + \
                 "Parameters [Units]:\n"               + \
                 parameters + "\n"
    
    return lines