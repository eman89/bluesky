'''
logHeader.py

Contains functions to write the header for the different log files

'''


def skyHeader():    
    parameters =  "SimTime [s], "  + \
                  "N Cruising Aircraft [-], " + \
                  "N Climbing/Descending (C/D) Aicraft [-], " + \
                  "N Total Inst Aircraft [-], " + \
                  "N Cruise-Cruise Conflicts [-], " + \
                  "N Cruise-C/D Conflicts [-], " + \
                  "N C/D-C/D Conflicts [-], " + \
                  "N Total Conflicts [-], " + \
                  "Average Absolute Climb Angle for C/D Aircraft [deg], " + \
                  "Average Absolute Climb Angle for All Aircraft [deg]"
    
    lines      = "#######################################################\n" + \
                 "SKY LOG\n" + \
                 "Instantaneous Summary Data For Entire Simulation Area\n" + \
                 "#######################################################\n\n" + \
                 "Parameters [Units]:\n" + \
                 parameters + "\n" 
                 
    return lines


def smodelHeader():    
    parameters =  "SimTime [s], "  + \
                  "N Cruising Aircraft [-], " + \
                  "N Climbing/Descending (C/D) Aicraft [-], " + \
                  "N Total Inst Aircraft [-], " + \
                  "N Cruise-Cruise Conflicts [-], " + \
                  "N Cruise-C/D Conflicts [-], " + \
                  "N C/D-C/D Conflicts [-], " + \
                  "N Total Conflicts [-], " + \
                  "Average Absolute Climb Angle for C/D Aircraft [deg], " + \
                  "Average Absolute Climb Angle for All Aircraft [deg]"
    
    lines      = "#######################################################\n" + \
                 "SMODEL LOG\n" + \
                 "Instantaneous Summary Data For Square Analysis Area\n" + \
                 "#######################################################\n\n" + \
                 "Parameters [Units]:\n" + \
                 parameters + "\n"    
                 
    return lines


def cmodelHeader():    
    parameters =  "SimTime [s], "  + \
                  "N Cruising Aircraft [-], " + \
                  "N Climbing/Descending (C/D) Aicraft [-], " + \
                  "N Total Inst Aircraft [-], " + \
                  "N Cruise-Cruise Conflicts [-], " + \
                  "N Cruise-C/D Conflicts [-], " + \
                  "N C/D-C/D Conflicts [-], " + \
                  "N Total Conflicts [-], " + \
                  "Average Absolute Climb Angle for C/D Aircraft [deg], " + \
                  "Average Absolute Climb Angle for All Aircraft [deg]"
    
    lines      = "#######################################################\n" + \
                 "CMODEL LOG\n" + \
                 "Instantaneous Summary Data For Circular Analysis Area\n" + \
                 "#######################################################\n\n" + \
                 "Parameters [Units]:\n" + \
                 parameters + "\n"  
                 
    return lines


def snapHeader():
  parameters = "SimTime [s], "  + \
               "Call Sign [-], " + \
               "Spawn Time [s], " + \
               "Latitude [deg], " + \
               "Longitude [deg], " + \
               "Altitude [m], " + \
               "TAS [m/s], " + \
               "Vertical Speed [m/s], " + \
               "Heading [deg], " + \
               "Origin Lat [deg], " + \
               "Origin Lon [deg]" + \
               "Destination Lat [deg], " + \
               "Destination Lon [deg], " + \
               "ASAS Active [bool], " + \
               "Pilot ALT [m], " + \
               "Pilot SPD (TAS) [m/s], " + \
               "Pilot VS [m/s], " + \
               "Pilot HDG [deg]"

  lines      = "#######################################################\n" + \
               "SNAP LOG\n" + \
               "Airspace Snapshot Data\n" + \
               "DT: %s [s]\n" + \
               "#######################################################\n\n" + \
               "Parameters [Units]:\n" + \
               parameters + "\n"

  return lines
  

def flstHeader(): 
  parameters = "Deletion Time [s], " + \
               "Call sign [-], " + \
               "Spawn Time [s], " + \
               "Flight time [s], " + \
               "Actual Distance 2D [m], " + \
               "Actual Distance 3D [m], " + \
               "Work Done [J], " + \
               "Latitude [deg], " + \
               "Longitude [deg], " + \
               "Altitude [m], " + \
               "TAS [m/s], " + \
               "Vertical Speed [m/s], " + \
               "Heading [deg], " + \
               "Origin Lat [deg], " + \
               "Origin Lon [deg]" + \
               "Destination Lat [deg], " + \
               "Destination Lon [deg], " + \
               "ASAS Active [bool], " + \
               "Pilot ALT [m], " + \
               "Pilot SPD (TAS) [m/s], " + \
               "Pilot HDG [deg], " + \
               "Pilot VS [m/s]" 

  lines      = "#######################################################\n" + \
               "FLST LOG\n" + \
               "Flight Statistics\n" + \
               "#######################################################\n\n" + \
               "Parameters [Units]:\n" + \
               parameters + "\n"

  return lines


def cflHeader():
  parameters = "Simulation Time  [s], " + \
               "Call sign id1 [-], " + \
               "tinconf id1   [s], " + \
               "toutconf id1  [s], " + \
               "tcpa id1  [s], " + \
               "Latitude id1 [deg], " + \
               "Longitude id1 [deg], " + \
               "Altitude id1  [m], " + \
               "Latitude cpa id1  [deg], " + \
               "Longitude cpa id1 [deg], " + \
               "Altitude cpa id1  [m], " + \
               "TAS id1 [m/s], " + \
               "Vertical speed id1  [m/s], " + \
               "Heading id1 [deg], " + \
               "Call sign id2 [-], " + \
               "tinconf id2 [s], " + \
               "toutconf id2  [s], " + \
               "tcpa id2  [s, " + \
               "Latitude id2  [deg], " + \
               "Longitude id2 [deg], " + \
               "Altitude id2  [m], " + \
               "Latitude cpa id2  [deg], " + \
               "Longitude cpa id2 [deg], " + \
               "Altitude cpa id2  [m], " + \
               "TAS id2 [m/s], " + \
               "Vertical speed id2  [m/s], " + \
               "Heading id2 [deg]"

  lines      = "#######################################################\n" + \
               "CFL LOG\n" + \
               "Conflict Log\n" + \
               "#######################################################\n\n" + \
               "Parameters [Units]:\n" + \
               parameters + "\n"

  return lines


def instHeader():
  parameters = "Simulation Time  [s], " + \
               "Call sign id1 [-], " + \
               "tinconf id1   [s], " + \
               "toutconf id1  [s], " + \
               "tcpa id1  [s], " + \
               "Latitude id1 [deg], " + \
               "Longitude id1 [deg], " + \
               "Altitude id1  [m], " + \
               "Latitude cpa id1  [deg], " + \
               "Longitude cpa id1 [deg], " + \
               "Altitude cpa id1  [m], " + \
               "TAS id1 [m/s], " + \
               "Vertical speed id1  [m/s], " + \
               "Heading id1 [deg], " + \
               "Call sign id2 [-], " + \
               "tinconf id2 [s], " + \
               "toutconf id2  [s], " + \
               "tcpa id2  [s, " + \
               "Latitude id2  [deg], " + \
               "Longitude id2 [deg], " + \
               "Altitude id2  [m], " + \
               "Latitude cpa id2  [deg], " + \
               "Longitude cpa id2 [deg], " + \
               "Altitude cpa id2  [m], " + \
               "TAS id2 [m/s], " + \
               "Vertical speed id2  [m/s], " + \
               "Heading id2 [deg]"

  lines      = "#######################################################\n" + \
               "INST LOG\n" + \
               "Instantaneous Conflict Log\n" + \
               "#######################################################\n\n" + \
               "Parameters [Units]:\n" + \
               parameters + "\n"

  return lines


def intHeader():
  parameters = "Simulation Time  [s], " + \
               "Call sign id1 [-], " + \
               "tinconf id1   [s], " + \
               "toutconf id1  [s], " + \
               "tcpa id1  [s], " + \
               "Latitude id1 [deg], " + \
               "Longitude id1 [deg], " + \
               "Altitude id1  [m], " + \
               "Latitude cpa id1  [deg], " + \
               "Longitude cpa id1 [deg], " + \
               "Altitude cpa id1  [m], " + \
               "TAS id1 [m/s], " + \
               "Vertical speed id1  [m/s], " + \
               "Heading id1 [deg], " + \
               "Call sign id2 [-], " + \
               "tinconf id2 [s], " + \
               "toutconf id2  [s], " + \
               "tcpa id2  [s, " + \
               "Latitude id2  [deg], " + \
               "Longitude id2 [deg], " + \
               "Altitude id2  [m], " + \
               "Latitude cpa id2  [deg], " + \
               "Longitude cpa id2 [deg], " + \
               "Altitude cpa id2  [m], " + \
               "TAS id2 [m/s], " + \
               "Vertical speed id2  [m/s], " + \
               "Heading id2 [deg], " + \
               "Max Intrusion Severity [-], " + \
               "Horiz Intrusion at Max IS [-], " + \
               "Vert Intrusion at Max IS [-]"

  lines      = "#######################################################\n" + \
               "INT LOG\n" + \
               "Intrusion Log\n" + \
               "#######################################################\n\n" + \
               "Parameters [Units]:\n" + \
               parameters + "\n"

  return lines
