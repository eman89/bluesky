'''
logHeader.py

Contains functions to write the header for the different log files

'''

def skyHeader():    
    parameters = "nTraf [-], nConflicts Now [-], nIntrusions Now [-]"
    
    lines      = "#####################\n"   + \
                 "SKY LOG\n"                   + \
                 "#####################\n\n" + \
                 "Parameters [Units]:\n"      + \
                 parameters + "\n"
                 
                 
    return lines


def snapHeader():
    parameters = "Call Sign [-], Spawn Time [s], Latitude [deg], Longitude [deg], "  + \
                 "Altitude [m], TAS [m/s], VS [m/s], HDG [deg], CMDALT [m], "        + \
                 "CMDTAS [m/s], CMDTRK [deg], CMDVS [m/s], LNAV Active [-], "        + \
                 "Origin [-], Destination [-], ASAS Active [-], ASASTAS [m/s], "     + \
                 "ASASTRK [deg]"
                 
    lines      = "#####################\n"    + \
                 "SNAP LOG\n"                   + \
                 "#####################\n\n"  + \
                 "Parameters [Units]:\n"        + \
                 parameters + "\n"
    
    return lines
    

def cflHeader():
    parameters =  "Call Sign id1 [-], Call Sign id2 [-], tinconf [s], toutconf [s], "     + \
                  "tcpa [s], Latitude id1 [deg], Longitude id1 [deg], Altitude id1 [m], " + \
                  "TAS id1 [m/s], VS id1 [m/s], HDG id1 [deg], Latitude CPA id1 [deg], "  + \
                  "Longitude CPA id1 [deg], Altitude CPA id1 [m], ASAS Active id1 [-], "  + \
                  "ASASTAS id1 [m/s], ASASTRK id1 [deg], nConflicts With id1 [-], "       + \
                  "Latitude id2 [deg], Longitude id2 [deg], Altitude id2 [m], "           + \
                  "TAS id2 [m/s], VS id2 [m/s], HDG id2 [deg], Latitude CPA id2 [deg], "  + \
                  "Longitude CPA id2 [deg], Altitude CPA id2 [m], ASAS Active id2 [-], "  + \
                  "ASASTAS id2 [m/s], ASASTRK id2 [deg], nConflicts With id2 [-]"
    
    lines      = "#####################\n"    + \
                 "CFL LOG\n"                    + \
                 "#####################\n\n"  + \
                 "Parameters [Units]:\n"        + \
                 parameters + "\n"
    
    return lines
                  



    
    
    
    

