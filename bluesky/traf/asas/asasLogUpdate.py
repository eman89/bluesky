import numpy as np
from collections import Counter


def asasLogUpdate(dbconf, traf):
        
    # SKYLOG---------------------------------------------------------------
    dbconf.nconflictsnow  = len(dbconf.conflist_now)
    dbconf.nintrusionsnow = len(dbconf.LOSlist_now)
    # SKYLOG---------------------------------------------------------------
    
    
    # CFLLOG---------------------------------------------------------------
    # NOTE: some of the varaibles (which are based on lists ) are updated 
    #       in StateBasedCD        
    if len(dbconf.clogid1) > 0:       
        # Reset variables
        dbconf.clogtinconf       = []
        dbconf.clogtoutconf      = []
        dbconf.clogtcpa          = []
        dbconf.cloglatid1        = []
        dbconf.cloglonid1        = []
        dbconf.clogaltid1        = []
        dbconf.clogtasid1        = []
        dbconf.clogvsid1         = []
        dbconf.cloghdgid1        = []
        dbconf.clogasasactiveid1 = []
        dbconf.clogasastasid1    = []
        dbconf.clogasastrkid1    = []
        dbconf.clognsecondaryid1 = np.zeros(len(dbconf.clogid1))            
        dbconf.cloglatid2        = []
        dbconf.cloglonid2        = []
        dbconf.clogaltid2        = []
        dbconf.clogtasid2        = []
        dbconf.clogvsid2         = []
        dbconf.cloghdgid2        = []
        dbconf.clogasasactiveid2 = []
        dbconf.clogasastasid2    = []
        dbconf.clogasastrkid2    = []
        dbconf.clognsecondaryid2 = np.zeros(len(dbconf.clogid2))

		# Update the cpa time variables
        dbconf.clogtinconf  = dbconf.tinconf[dbconf.clogi,dbconf.clogj]
        dbconf.clogtoutconf = dbconf.toutconf[dbconf.clogi,dbconf.clogj]
        dbconf.clogtcpa     = dbconf.tcpa[dbconf.clogi,dbconf.clogj]
                
        # Update the variables belonging to id1
        dbconf.cloglatid1        = traf.lat[dbconf.clogi]
        dbconf.cloglonid1        = traf.lon[dbconf.clogi]
        dbconf.clogaltid1        = traf.alt[dbconf.clogi]
        dbconf.clogtasid1        = traf.tas[dbconf.clogi]
        dbconf.clogvsid1         = traf.vs[dbconf.clogi]
        dbconf.cloghdgid1        = traf.hdg[dbconf.clogi]
        dbconf.clogasasactiveid1 = dbconf.asasactive[dbconf.clogi]
        dbconf.clogasastasid1    = dbconf.asasspd[dbconf.clogi]
        dbconf.clogasastrkid1    = dbconf.asastrk[dbconf.clogi]
                
        # Update the variables belonging to id2
        dbconf.cloglatid2        = traf.lat[dbconf.clogj]
        dbconf.cloglonid2        = traf.lon[dbconf.clogj]
        dbconf.clogaltid2        = traf.alt[dbconf.clogj]
        dbconf.clogtasid2        = traf.tas[dbconf.clogj]
        dbconf.clogvsid2         = traf.vs[dbconf.clogj]
        dbconf.cloghdgid2        = traf.hdg[dbconf.clogj]
        dbconf.clogasasactiveid2 = dbconf.asasactive[dbconf.clogj]
        dbconf.clogasastasid2    = dbconf.asasspd[dbconf.clogj]
        dbconf.clogasastrkid2    = dbconf.asastrk[dbconf.clogj]
        
        # Update the number of conflicts variables for id1 and id2
        conflist_all_flatten = np.array(dbconf.conflist_all).flatten()
        countConflist_all    = Counter(conflist_all_flatten)
        for i in range(len(dbconf.clogid1)):
            if dbconf.clogid1[i] in conflist_all_flatten:
                dbconf.clognsecondaryid1[i] = dbconf.clognsecondaryid1[i] + countConflist_all[dbconf.clogid1[i]]
                dbconf.clognsecondaryid1[i] = dbconf.clognsecondaryid1[i] - dbconf.clogid1.count(dbconf.clogid1[i]) - dbconf.clogid2.count(dbconf.clogid1[i])
            if dbconf.clogid2[i] in conflist_all_flatten:
                dbconf.clognsecondaryid2[i] = dbconf.clognsecondaryid2[i] + countConflist_all[dbconf.clogid2[i]]
                dbconf.clognsecondaryid2[i] = dbconf.clognsecondaryid2[i] - dbconf.clogid1.count(dbconf.clogid2[i]) - dbconf.clogid2.count(dbconf.clogid2[i])

        # Finally, call the logger
        dbconf.cfllog.log()
    # CFLLOG---------------------------------------------------------------
