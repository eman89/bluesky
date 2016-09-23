import numpy as np
from collections import Counter
import gc


def asasLogUpdate(dbconf, traf):
        
    # SKYLOG-------------------------------------------------------------------
    dbconf.nconflictsnow  = len(dbconf.conflist_now)
    dbconf.nintrusionsnow = len(dbconf.LOSlist_now)
    # SKYLOG-------------------------------------------------------------------
    
    
    # CFLLOG-------------------------------------------------------------------
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
        
        # Update the number of secondary conflicts for id1 and id2
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
    # CFLLOG-------------------------------------------------------------------
        
        
    # INSTLOG------------------------------------------------------------------
    # NOTE: some of the varaibles (which are based on lists ) are updated 
    #       in StateBasedCD   
    # Reset variables
    dbconf.inslogtinconf       = []
    dbconf.inslogtoutconf      = []
    dbconf.inslogtcpa          = []
    dbconf.insloglatid1        = []
    dbconf.insloglonid1        = []
    dbconf.inslogaltid1        = []
    dbconf.inslogtasid1        = []
    dbconf.inslogvsid1         = []
    dbconf.insloghdgid1        = []
    dbconf.inslogasasactiveid1 = []
    dbconf.inslogasastasid1    = []
    dbconf.inslogasastrkid1    = []
    dbconf.insloglatid2        = []
    dbconf.insloglonid2        = []
    dbconf.inslogaltid2        = []
    dbconf.inslogtasid2        = []
    dbconf.inslogvsid2         = []
    dbconf.insloghdgid2        = []
    dbconf.inslogasasactiveid2 = []
    dbconf.inslogasastasid2    = []
    dbconf.inslogasastrkid2    = []
    dbconf.inslogntraf         = []
    
    # Update the cpa time variables
    dbconf.inslogtinconf  = dbconf.tinconf[dbconf.inslogi,dbconf.inslogj]
    dbconf.inslogtoutconf = dbconf.toutconf[dbconf.inslogi,dbconf.inslogj]
    dbconf.inslogtcpa     = dbconf.tcpa[dbconf.inslogi,dbconf.inslogj]
                
    # Update the variables belonging to id1
    dbconf.insloglatid1        = traf.lat[dbconf.inslogi]
    dbconf.insloglonid1        = traf.lon[dbconf.inslogi]
    dbconf.inslogaltid1        = traf.alt[dbconf.inslogi]
    dbconf.inslogtasid1        = traf.tas[dbconf.inslogi]
    dbconf.inslogvsid1         = traf.vs[dbconf.inslogi]
    dbconf.insloghdgid1        = traf.hdg[dbconf.inslogi]
    dbconf.inslogasasactiveid1 = dbconf.asasactive[dbconf.inslogi]
    dbconf.inslogasastasid1    = dbconf.asasspd[dbconf.inslogi]
    dbconf.inslogasastrkid1    = dbconf.asastrk[dbconf.inslogi]
            
    # Update the variables belonging to id2
    dbconf.insloglatid2        = traf.lat[dbconf.inslogj]
    dbconf.insloglonid2        = traf.lon[dbconf.inslogj]
    dbconf.inslogaltid2        = traf.alt[dbconf.inslogj]
    dbconf.inslogtasid2        = traf.tas[dbconf.inslogj]
    dbconf.inslogvsid2         = traf.vs[dbconf.inslogj]
    dbconf.insloghdgid2        = traf.hdg[dbconf.inslogj]
    dbconf.inslogasasactiveid2 = dbconf.asasactive[dbconf.inslogj]
    dbconf.inslogasastasid2    = dbconf.asasspd[dbconf.inslogj]
    dbconf.inslogasastrkid2    = dbconf.asastrk[dbconf.inslogj]
        
    # Update number of aircraft
    dbconf.inslogntraf = [traf.ntraf]*len(dbconf.inslogi)
    
    # There is no need to manually call the logger as INSTLOG is periodic!
    # INSTLOG------------------------------------------------------------------
    
    
    # INTLOG-------------------------------------------------------------------
    
    # first check all the current active LOS and compute the severity
    
    id1exists = np.asarray(dbconf.ilogid1exists)
    id2exists = np.asarray(dbconf.ilogid2exists)
    
    Fail = -999.999
#    Fail = 'Fail'
    
    if len(dbconf.ilogid1) > 0:        
        # Reset Varaibles
        dbconf.ilogtinconf       = []
        dbconf.ilogtoutconf      = []
        dbconf.iloglatid1        = []
        dbconf.iloglonid1        = []
        dbconf.ilogaltid1        = []
        dbconf.ilogtasid1        = []
        dbconf.ilogvsid1         = []
        dbconf.iloghdgid1        = []
        dbconf.ilogasasactiveid1 = []
        dbconf.ilogasastasid1    = []
        dbconf.ilogasastrkid1    = []
        dbconf.iloglatid2        = []
        dbconf.iloglonid2        = []
        dbconf.ilogaltid2        = []
        dbconf.ilogtasid2        = []
        dbconf.ilogvsid2         = []
        dbconf.iloghdgid2        = []
        dbconf.ilogasasactiveid2 = []
        dbconf.ilogasastasid2    = []
        dbconf.ilogasastrkid2    = []
        
        # Update the conflict time variables
        dbconf.ilogtinconf  = np.where(id1exists & id2exists, dbconf.tinconf[dbconf.ilogi,dbconf.ilogj], Fail)
        dbconf.ilogtoutconf = np.where(id1exists & id2exists, dbconf.toutconf[dbconf.ilogi,dbconf.ilogj], Fail)       
        
        # Update the varaibles beloning to id1
        dbconf.iloglatid1        = np.where(id1exists, traf.lat[dbconf.ilogi], Fail)
        dbconf.iloglonid1        = np.where(id1exists, traf.lon[dbconf.ilogi], Fail)
        dbconf.ilogaltid1        = np.where(id1exists, traf.alt[dbconf.ilogi], Fail)
        dbconf.ilogtasid1        = np.where(id1exists, traf.tas[dbconf.ilogi], Fail)
        dbconf.ilogvsid1         = np.where(id1exists, traf.vs[dbconf.ilogi] , Fail)
        dbconf.iloghdgid1        = np.where(id1exists, traf.hdg[dbconf.ilogi], Fail)
        dbconf.ilogasasactiveid1 = np.where(id1exists, dbconf.asasactive[dbconf.ilogi], Fail)
        dbconf.ilogasastasid1    = np.where(id1exists, dbconf.asasspd[dbconf.ilogi], Fail)
        dbconf.ilogasastrkid1    = np.where(id1exists, dbconf.asastrk[dbconf.ilogi], Fail)
        
        # Update the variables belonging to id2
        dbconf.iloglatid2        = np.where(id2exists, traf.lat[dbconf.ilogj], Fail)
        dbconf.iloglonid2        = np.where(id2exists, traf.lon[dbconf.ilogj], Fail)
        dbconf.ilogaltid2        = np.where(id2exists, traf.alt[dbconf.ilogj], Fail)
        dbconf.ilogtasid2        = np.where(id2exists, traf.tas[dbconf.ilogj], Fail)
        dbconf.ilogvsid2         = np.where(id2exists, traf.vs[dbconf.ilogj] , Fail)
        dbconf.iloghdgid2        = np.where(id2exists, traf.hdg[dbconf.ilogj], Fail)
        dbconf.ilogasasactiveid2 = np.where(id2exists, dbconf.asasactive[dbconf.ilogj], Fail)
        dbconf.ilogasastasid2    = np.where(id2exists, dbconf.asasspd[dbconf.ilogj], Fail)
        dbconf.ilogasastrkid2    = np.where(id2exists, dbconf.asastrk[dbconf.ilogj], Fail) 
        
        # Finally, call the logger
        dbconf.intlog.log()   
    # INTLOG-------------------------------------------------------------------

    
def logLOS(dbconf, traf):
    
    # Reset variables
    dbconf.ilogid1exists = []
    dbconf.ilogid2exists = []
    dbconf.ilogi         = []
    dbconf.ilogj         = []
    dbconf.ilogid1       = []
    dbconf.ilogid2       = []
    dbconf.ilogintsev    = []
    dbconf.iloginthsev   = []
    dbconf.ilogintvsev   = []
    
    for intrusion in dbconf.LOSlist_all:
        gc.disable()
        
        # Determine the aircraft involved in this LOS
        ac1      = intrusion[0]
        ac2      = intrusion[1]
        id1, id2 = traf.id2idx(ac1), traf.id2idx(ac2)
        intid    = dbconf.LOSlist_all.index(intrusion)
        
        # Check is the aircraft still exist 
        id1exists = False if id1<0 else True
        id2exists = False if id2<0 else True        
        
        import pdb
        pdb.set_trace()
        
        # If both ac exist then check if it is still a LOS
        if id1exists and id2exists:
            # LOS check
            dx     = (traf.lat[id1] - traf.lat[id2]) * 111319.
            dy     = (traf.lon[id1] - traf.lon[id2]) * 111319.
            hdist2 = dx**2 + dy**2
            hLOS   = hdist2 < dbconf.R**2
            vdist  = abs(traf.alt[id1] - traf.alt[id2])
            vLOS   = vdist < dbconf.dh
            isLOS  = (hLOS & vLOS)
            # if it is still a LOS, then compute the severity
            if isLOS:
                # Calculate the current intrusion severity for the current LOS
                Ih       = 1.0 - np.sqrt(hdist2) / dbconf.R
                Iv       = 1.0 - vdist / dbconf.dh
                severity = min(Ih, Iv)
                # Check if the severity is larger than the one logged for this LOS.
                # If so update the severity
                if severity > dbconf.LOSmaxsev[intid]:
                    dbconf.LOSmaxsev[intid]  = severity
                    dbconf.LOShmaxsev[intid] = Ih
                    dbconf.LOSvmaxsev[intid] = Iv
                # If the severity is decreasing then log it the first time it starts decreasing    
                else: 
                    if intrusion not in dbconf.LOSlist_logged:
                        dbconf.ilogid1exists.append(id1exists)
                        dbconf.ilogid2exists.append(id2exists)
                        dbconf.ilogi.append(id1)
                        dbconf.ilogj.append(id2)
                        dbconf.ilogid1.append(ac1)
                        dbconf.ilogid2.append(ac2)
                        dbconf.ilogintsev.append(dbconf.LOSmaxsev[intid])
                        dbconf.iloginthsev.append(dbconf.LOShmaxsev[intid])
                        dbconf.ilogintvsev.append(dbconf.LOSvmaxsev[intid])
                        dbconf.LOSlist_logged.append(intrusion)
            # If it is no longer a LOS, check if it has been logged, and then delete it   
            else:
#                import pdb
#                pdb.set_trace()
                if intrusion not in dbconf.LOSlist_logged:
                    dbconf.ilogid1exists.append(id1exists)
                    dbconf.ilogid2exists.append(id2exists)
                    dbconf.ilogi.append(id1)
                    dbconf.ilogj.append(id2)
                    dbconf.ilogid1.append(ac1)
                    dbconf.ilogid2.append(ac2)
                    dbconf.ilogintsev.append(dbconf.LOSmaxsev[intid])
                    dbconf.iloginthsev.append(dbconf.LOShmaxsev[intid])
                    dbconf.ilogintvsev.append(dbconf.LOSvmaxsev[intid])
                # delete it completely (not from LOSlist_now)
                dbconf.LOSlist_all.remove(intrusion)
                dbconf.LOSlist_logged.remove(intrusion)
                del dbconf.LOSmaxsev[intid]
                del dbconf.LOShmaxsev[intid]
                del dbconf.LOSvmaxsev[intid]           
        #if one or both of the both aircraft no longer exists, check if it has 
        # been logged and then delete it
        else:
#            import pdb
#            pdb.set_trace()
            if intrusion not in dbconf.LOSlist_logged:
                dbconf.ilogid1exists.append(id1exists)
                dbconf.ilogid2exists.append(id2exists)
                dbconf.ilogi.append(id1)
                dbconf.ilogj.append(id2)
                dbconf.ilogid1.append(ac1)
                dbconf.ilogid2.append(ac2)
                dbconf.ilogintsev.append(dbconf.LOSmaxsev[intid])
                dbconf.iloginthsev.append(dbconf.LOShmaxsev[intid])
                dbconf.ilogintvsev.append(dbconf.LOSvmaxsev[intid])
            # delete it completely (not from LOSlist_now)
            dbconf.LOSlist_all.remove(intrusion)
            dbconf.LOSlist_logged.remove(intrusion)
            del dbconf.LOSmaxsev[intid]
            del dbconf.LOShmaxsev[intid]
            del dbconf.LOSvmaxsev[intid]
        
        gc.enable() 