import numpy as np
import gc
#from ...tools import areafilter

def asasLogUpdate(dbconf, traf):
    
    # SKYLOG START ------------------------------------------------------------
    
    # Total number of instantaneous conflicts
    dbconf.ncfl = len(dbconf.conflist_now)
    
    # vertical speeds of aircraft in the instantaneous conflict lists 
    vsskyid1 = traf.vs[dbconf.instlogi]
    vsskyid2 = traf.vs[dbconf.instlogj]
        
    # Number of instantaneous conflicts between cruising aircraft
    dbconf.ncflCruising = sum((np.abs(vsskyid1)<=traf.cruiseLimVS)*(np.abs(vsskyid2)<=traf.cruiseLimVS))
    
    # Number of instantaneous conflicts between cruising and C/D aircraft 
    dbconf.ncflCruisingVS = sum((np.abs(vsskyid1)<=traf.cruiseLimVS)*(np.abs(vsskyid2)>traf.cruiseLimVS)) + \
                                sum((np.abs(vsskyid1)>traf.cruiseLimVS)*(np.abs(vsskyid2)<=traf.cruiseLimVS))
    
    # Number of instantaneous conflicts between C/D aircraft
    dbconf.ncflVS = sum((np.abs(vsskyid1)>traf.cruiseLimVS)*(np.abs(vsskyid2)>traf.cruiseLimVS)) 
    
    # SKYLOG END --------------------------------------------------------------
    
    # SMODELLOG START ---------------------------------------------------------
    
#    # Only do anything is SQUAREMODELAREA exists!
#    if 'SQUAREMODELAREA' in areafilter.areas:
#        
#        # Determine the idx of the aircraft that have a conflict and are in the square area (POSITION BASED 'OR' FILTERING)
#        insmodelareaid1 = areafilter.checkInside('SQUAREMODELAREA', traf.lat[dbconf.instlogi], traf.lon[dbconf.instlogi], traf.alt[dbconf.instlogi])
#        insmodelareaid2 = areafilter.checkInside('SQUAREMODELAREA', traf.lat[dbconf.instlogj], traf.lon[dbconf.instlogj], traf.alt[dbconf.instlogj])
#        insmodelarea  = list(np.where(np.logical_or(insmodelareaid1,insmodelareaid2))[0])
#        id1smodelarea = list(np.asarray(dbconf.instlogi)[insmodelarea])
#        id2smodelarea = list(np.asarray(dbconf.instlogj)[insmodelarea])
#        
#        
#        # Total number of instantaneous conflicts inside square area
#        dbconf.smodncfl = len(id1smodelarea)
#        
#        # vertical speeds of aircraft in the instantaneous conflict lists that are also in the square area
#        vssmodelid1 = traf.vs[id1smodelarea]
#        vssmodelid2 = traf.vs[id2smodelarea]
#        
#        # Number of instantaneous conflicts between cruising aircraft inside square area
#        dbconf.smodncflCruising = sum((np.abs(vssmodelid1)<=traf.cruiseLimVS)*(np.abs(vssmodelid2)<=traf.cruiseLimVS))
#        
#        # Number of instantaneous conflicts between cruising and C/D aircraft inside square area 
#        dbconf.smodncflCruisingVS = sum((np.abs(vssmodelid1)<=traf.cruiseLimVS)*(np.abs(vssmodelid2)>traf.cruiseLimVS)) + \
#                                        sum((np.abs(vssmodelid1)>traf.cruiseLimVS)*(np.abs(vssmodelid2)<=traf.cruiseLimVS))
#                                        
#        # Number of instantaneous conflicts between C/D aircraft inside square area                                       
#        dbconf.smodncflVS = sum((np.abs(vssmodelid1)>traf.cruiseLimVS)*(np.abs(vssmodelid2)>traf.cruiseLimVS))
#    
    
    # SMODELLOG END -----------------------------------------------------------
    
    
    # CMODELLOG START ---------------------------------------------------------
    
#    # Only do anything is CIRCLEMODELAREA exists!
#    if 'CIRCLEMODELAREA' in areafilter.areas:
#        
#        # Determine the idx of the aircraft that have a conflict and are in the circle area (POSITION BASED 'OR' FILTERING)
#        incmodelareaid1 = areafilter.checkInside('CIRCLEMODELAREA', traf.lat[dbconf.instlogi], traf.lon[dbconf.instlogi], traf.alt[dbconf.instlogi])
#        incmodelareaid2 = areafilter.checkInside('CIRCLEMODELAREA', traf.lat[dbconf.instlogj], traf.lon[dbconf.instlogj], traf.alt[dbconf.instlogj])
#        incmodelarea  = list(np.where(np.logical_or(incmodelareaid1,incmodelareaid2))[0])
#        id1cmodelarea = list(np.asarray(dbconf.instlogi)[incmodelarea])
#        id2cmodelarea = list(np.asarray(dbconf.instlogj)[incmodelarea])
#        
#        
#        # Total number of instantaneous conflicts inside circle area
#        dbconf.cmodncfl = len(id1cmodelarea)
#        
#        # vertical speeds of aircraft in the instantaneous conflict lists that are also in the circle area
#        vscmodelid1 = traf.vs[id1cmodelarea]
#        vscmodelid2 = traf.vs[id2cmodelarea]
#        
#        # Number of instantaneous conflicts between cruising aircraft inside circle area
#        dbconf.cmodncflCruising = sum((np.abs(vscmodelid1)<=traf.cruiseLimVS)*(np.abs(vscmodelid2)<=traf.cruiseLimVS))
#        
#        # Number of instantaneous conflicts between cruising and C/D aircraft inside circle area
#        dbconf.cmodncflCruisingVS = sum((np.abs(vscmodelid1)<=traf.cruiseLimVS)*(np.abs(vscmodelid2)>traf.cruiseLimVS)) + \
#                                        sum((np.abs(vscmodelid1)>traf.cruiseLimVS)*(np.abs(vscmodelid2)<=traf.cruiseLimVS))
#                                        
#        # Number of instantaneous conflicts between C/D aircraft inside circle area                                      
#        dbconf.cmodncflVS = sum((np.abs(vscmodelid1)>traf.cruiseLimVS)*(np.abs(vscmodelid2)>traf.cruiseLimVS))
    
    # CMODELLOG END -----------------------------------------------------------
        
    # CFLLOG  START -----------------------------------------------------------
    # NOTE: some of the varaibles (which are based on lists ) are updated 
    #       in StateBasedCD        
    
    # Reset the CFL log variables that have not been reset in StateBasedCD
    dbconf.clogtinconfid1 = []
    dbconf.clogtoutconfid1 = []
    dbconf.clogtcpaid1 = []
    dbconf.cloglatid1 = []
    dbconf.cloglonid1 = []
    dbconf.clogaltid1 = []
    dbconf.clogtasid1 = []
    dbconf.clogvsid1 = []
    dbconf.cloghdgid1 = []
    dbconf.clogasasactiveid1 = []
    dbconf.clogtinconfid2 = []
    dbconf.clogtoutconfid2 = []
    dbconf.clogtcpaid2 = []
    dbconf.cloglatid2 = []
    dbconf.cloglonid2 = []
    dbconf.clogaltid2 = []
    dbconf.clogtasid2 = []
    dbconf.clogvsid2 = []
    dbconf.cloghdgid2 = []
    dbconf.clogasasactiveid2 = []
        
    # Update the lists if there is something to log
    if len(dbconf.clogi) > 0:

        # Update the variables belonging to id1
        dbconf.clogtinconfid1 = dbconf.tinconf[dbconf.clogi,dbconf.clogj]
        dbconf.clogtoutconfid1 = dbconf.toutconf[dbconf.clogi,dbconf.clogj]
        dbconf.clogtcpaid1 = dbconf.tcpa[dbconf.clogi,dbconf.clogj]
        dbconf.cloglatid1 = traf.lat[dbconf.clogi]
        dbconf.cloglonid1 = traf.lon[dbconf.clogi]
        dbconf.clogaltid1 = traf.alt[dbconf.clogi]
        dbconf.clogtasid1 = traf.tas[dbconf.clogi]
        dbconf.clogvsid1 = traf.vs[dbconf.clogi]
        dbconf.cloghdgid1 = traf.hdg[dbconf.clogi]
        dbconf.clogasasactiveid1 = dbconf.active[dbconf.clogi]

        # Update the variables belonging to id2
        dbconf.clogtinconfid2 = dbconf.tinconf[dbconf.clogj,dbconf.clogi]
        dbconf.clogtoutconfid2 = dbconf.toutconf[dbconf.clogj,dbconf.clogi]
        dbconf.clogtcpaid2 = dbconf.tcpa[dbconf.clogj,dbconf.clogi]
        dbconf.cloglatid2 = traf.lat[dbconf.clogj]
        dbconf.cloglonid2 = traf.lon[dbconf.clogj]
        dbconf.clogaltid2 = traf.alt[dbconf.clogj]
        dbconf.clogtasid2 = traf.tas[dbconf.clogj]
        dbconf.clogvsid2 = traf.vs[dbconf.clogj]
        dbconf.cloghdgid2 = traf.hdg[dbconf.clogj]
        dbconf.clogasasactiveid2 = dbconf.active[dbconf.clogj]
        
        # Finally, call the logger
        dbconf.cfllog.log()
    
    # CFLLOG END --------------------------------------------------------------
        
    # INSTLOG START -----------------------------------------------------------
    # NOTE: some of the varaibles (which are based on lists ) are updated 
    #       in StateBasedCD
    
    # Reset the INST log variables that have not been reset in StateBasedCD
    dbconf.instlogtinconfid1 = []
    dbconf.instlogtoutconfid1 = []
    dbconf.instlogtcpaid1 = []
    dbconf.instloglatid1 = []
    dbconf.instloglonid1 = []
    dbconf.instlogaltid1 = []
    dbconf.instlogtasid1 = []
    dbconf.instlogvsid1 = []
    dbconf.instloghdgid1 = []
    dbconf.instlogasasactiveid1 = []
    dbconf.instlogtinconfid2 = []
    dbconf.instlogtoutconfid2 = []
    dbconf.instlogtcpaid2 = []
    dbconf.instloglatid2 = []
    dbconf.instloglonid2 = []
    dbconf.instlogaltid2 = []
    dbconf.instlogtasid2 = []
    dbconf.instlogvsid2 = []
    dbconf.instloghdgid2 = []
    dbconf.instlogasasactiveid2 = []

    # Update the lists if there is something to log
    if len(dbconf.instlogi) > 0:
    
        # Update the variables belonging to id1
        dbconf.instlogtinconfid1 = dbconf.tinconf[dbconf.instlogi,dbconf.instlogj]
        dbconf.instlogtoutconfid1 = dbconf.toutconf[dbconf.instlogi,dbconf.instlogj]
        dbconf.instlogtcpaid1 = dbconf.tcpa[dbconf.instlogi,dbconf.instlogj]
        dbconf.instloglatid1 = traf.lat[dbconf.instlogi]
        dbconf.instloglonid1 = traf.lon[dbconf.instlogi]
        dbconf.instlogaltid1 = traf.alt[dbconf.instlogi]
        dbconf.instlogtasid1 = traf.tas[dbconf.instlogi]
        dbconf.instlogvsid1 = traf.vs[dbconf.instlogi]
        dbconf.instloghdgid1 = traf.hdg[dbconf.instlogi]
        dbconf.instlogasasactiveid1 = dbconf.active[dbconf.instlogi]

        # Update the variables belonging to id2
        dbconf.instlogtinconfid2 = dbconf.tinconf[dbconf.instlogj,dbconf.instlogi]
        dbconf.instlogtoutconfid2 = dbconf.toutconf[dbconf.instlogj,dbconf.instlogi]
        dbconf.instlogtcpaid2 = dbconf.tcpa[dbconf.instlogj,dbconf.instlogi]
        dbconf.instloglatid2 = traf.lat[dbconf.instlogj]
        dbconf.instloglonid2 = traf.lon[dbconf.instlogj]
        dbconf.instlogaltid2 = traf.alt[dbconf.instlogj]
        dbconf.instlogtasid2 = traf.tas[dbconf.instlogj]
        dbconf.instlogvsid2 = traf.vs[dbconf.instlogj]
        dbconf.instloghdgid2 = traf.hdg[dbconf.instlogj]
        dbconf.instlogasasactiveid2 = dbconf.active[dbconf.instlogj]    
    
    # INSTLOG END -------------------------------------------------------------

    # INTLOG START ------------------------------------------------------------
    
    # first check all the current active LOS and compute the severity
    logLOS(dbconf, traf)
        
    id1exists = np.asarray(dbconf.ilogid1exists)
    id2exists = np.asarray(dbconf.ilogid2exists)
    
    Fail = -999.999
#    Fail = 'Fail'
    
    # Reset intlog varaibles that have not been reset in logLOS
    dbconf.ilogtinconfid1 = []
    dbconf.ilogtoutconfid1 = []
    dbconf.ilogtcpaid1 = []
    dbconf.iloglatid1 = []
    dbconf.iloglonid1 = []
    dbconf.ilogaltid1 = []
    dbconf.ilogtasid1 = []
    dbconf.ilogvsid1 = []
    dbconf.iloghdgid1 = []
    dbconf.ilogasasactiveid1 = []
    dbconf.ilogtinconfid2 = []
    dbconf.ilogtoutconfid2 = []
    dbconf.ilogtcpaid2 = []
    dbconf.iloglatid2 = []
    dbconf.iloglonid2 = []
    dbconf.ilogaltid2 = []
    dbconf.ilogtasid2 = []
    dbconf.ilogvsid2 = []
    dbconf.iloghdgid2 = []
    dbconf.ilogasasactiveid2 = []

    # Update the lists if there is something to log        
    if len(dbconf.ilogi) > 0:   
        
        # Update the variables belonging to id1
        dbconf.ilogtinconfid1 = np.where(id1exists & id2exists, dbconf.tinconf[dbconf.ilogi,dbconf.ilogj], Fail)
        dbconf.ilogtoutconfid1 = np.where(id1exists & id2exists, dbconf.toutconf[dbconf.ilogi,dbconf.ilogj], Fail)
        dbconf.ilogtcpaid1 = np.where(id1exists & id2exists, dbconf.tcpa[dbconf.ilogi,dbconf.ilogj], Fail)
        dbconf.iloglatid1 = np.where(id1exists, traf.lat[dbconf.ilogi], Fail)
        dbconf.iloglonid1 = np.where(id1exists, traf.lon[dbconf.ilogi], Fail)
        dbconf.ilogaltid1 = np.where(id1exists, traf.alt[dbconf.ilogi], Fail)
        dbconf.ilogtasid1 = np.where(id1exists, traf.tas[dbconf.ilogi], Fail)
        dbconf.ilogvsid1 = np.where(id1exists, traf.vs[dbconf.ilogi], Fail)
        dbconf.iloghdgid1 = np.where(id1exists, traf.hdg[dbconf.ilogi], Fail)
        dbconf.ilogasasactiveid1 = np.where(id1exists, dbconf.active[dbconf.ilogi], Fail)
        
        # Update the variables belonging to id2
        dbconf.ilogtinconfid2 = np.where(id1exists & id2exists, dbconf.tinconf[dbconf.ilogj,dbconf.ilogi], Fail)
        dbconf.ilogtoutconfid2 = np.where(id1exists & id2exists, dbconf.toutconf[dbconf.ilogj,dbconf.ilogi], Fail)
        dbconf.ilogtcpaid2 = np.where(id1exists & id2exists, dbconf.tcpa[dbconf.ilogj,dbconf.ilogi], Fail)
        dbconf.iloglatid2 = np.where(id1exists, traf.lat[dbconf.ilogj], Fail)
        dbconf.iloglonid2 = np.where(id1exists, traf.lon[dbconf.ilogj], Fail)
        dbconf.ilogaltid2 = np.where(id1exists, traf.alt[dbconf.ilogj], Fail)
        dbconf.ilogtasid2 = np.where(id1exists, traf.tas[dbconf.ilogj], Fail)
        dbconf.ilogvsid2 = np.where(id1exists, traf.vs[dbconf.ilogj], Fail)
        dbconf.iloghdgid2 = np.where(id1exists, traf.hdg[dbconf.ilogj], Fail)
        dbconf.ilogasasactiveid2 = np.where(id1exists, dbconf.active[dbconf.ilogj], Fail)
        
        # Finally, call the logger
        dbconf.intlog.log()

    
def logLOS(dbconf, traf):
    # Check the current LOS and compute severity

    # Reset some INTLOG variables
    dbconf.ilogid1exists = []
    dbconf.ilogid2exists = []
    dbconf.ilogi         = []
    dbconf.ilogj         = []
    dbconf.ilogid1       = []
    dbconf.ilogid2       = []
    dbconf.ilogintsev    = []
    dbconf.iloginthsev   = []
    dbconf.ilogintvsev   = []
    
    for intrusion in dbconf.LOSlist_active[:]:
        gc.disable()
        
        # Determine the aircraft involved in this LOS
        ac1      = intrusion[0]
        ac2      = intrusion[1]
        id1, id2 = traf.id2idx(ac1), traf.id2idx(ac2)
        intid    = dbconf.LOSlist_active.index(intrusion)
        
        # Check is the aircraft still exist 
        id1exists = False if id1<0 else True
        id2exists = False if id2<0 else True        
        
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
                if severity >= dbconf.LOSmaxsev[intid]:
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
                # Delete it completely 
                if intrusion in dbconf.LOSlist_logged:
                    dbconf.LOSlist_logged.remove(intrusion)
                dbconf.LOSlist_active.remove(intrusion)
                del dbconf.LOSmaxsev[intid]
                del dbconf.LOShmaxsev[intid]
                del dbconf.LOSvmaxsev[intid]           
        # If one or both of the both aircraft no longer exists, check if it has 
        # been logged and then delete it
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
            # Delete it completely
            if intrusion in dbconf.LOSlist_logged:
                dbconf.LOSlist_logged.remove(intrusion)
            dbconf.LOSlist_active.remove(intrusion)
            del dbconf.LOSmaxsev[intid]
            del dbconf.LOShmaxsev[intid]
            del dbconf.LOSvmaxsev[intid]
        
        gc.enable() 