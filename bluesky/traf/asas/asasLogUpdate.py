import numpy as np
import gc
#from ...tools import areafilter

def asasLogUpdate(asas, traf):
    
    # SKYLOG START ------------------------------------------------------------
    
    # Total number of instantaneous conflicts
    asas.ncfl = len(asas.conflist_now)
    
    # vertical speeds of aircraft in the instantaneous conflict lists 
    vsskyid1 = traf.vs[asas.instlogi]
    vsskyid2 = traf.vs[asas.instlogj]
        
    # Number of instantaneous conflicts between cruising aircraft
    asas.ncflCruising = sum((np.abs(vsskyid1)<=traf.cruiseLimVS)*(np.abs(vsskyid2)<=traf.cruiseLimVS))
    
    # Number of instantaneous conflicts between cruising and C/D aircraft 
    asas.ncflCruisingVS = sum((np.abs(vsskyid1)<=traf.cruiseLimVS)*(np.abs(vsskyid2)>traf.cruiseLimVS)) + \
                                sum((np.abs(vsskyid1)>traf.cruiseLimVS)*(np.abs(vsskyid2)<=traf.cruiseLimVS))
    
    # Number of instantaneous conflicts between C/D aircraft
    asas.ncflVS = sum((np.abs(vsskyid1)>traf.cruiseLimVS)*(np.abs(vsskyid2)>traf.cruiseLimVS)) 
    
    # SKYLOG END --------------------------------------------------------------
    
    # SMODELLOG START ---------------------------------------------------------
    
#    # Only do anything is SQUAREMODELAREA exists!
#    if 'SQUAREMODELAREA' in areafilter.areas:
#        
#        # Determine the idx of the aircraft that have a conflict and are in the square area (POSITION BASED 'OR' FILTERING)
#        insmodelareaid1 = areafilter.checkInside('SQUAREMODELAREA', traf.lat[asas.instlogi], traf.lon[asas.instlogi], traf.alt[asas.instlogi])
#        insmodelareaid2 = areafilter.checkInside('SQUAREMODELAREA', traf.lat[asas.instlogj], traf.lon[asas.instlogj], traf.alt[asas.instlogj])
#        insmodelarea  = list(np.where(np.logical_or(insmodelareaid1,insmodelareaid2))[0])
#        id1smodelarea = list(np.asarray(asas.instlogi)[insmodelarea])
#        id2smodelarea = list(np.asarray(asas.instlogj)[insmodelarea])
#        
#        
#        # Total number of instantaneous conflicts inside square area
#        asas.smodncfl = len(id1smodelarea)
#        
#        # vertical speeds of aircraft in the instantaneous conflict lists that are also in the square area
#        vssmodelid1 = traf.vs[id1smodelarea]
#        vssmodelid2 = traf.vs[id2smodelarea]
#        
#        # Number of instantaneous conflicts between cruising aircraft inside square area
#        asas.smodncflCruising = sum((np.abs(vssmodelid1)<=traf.cruiseLimVS)*(np.abs(vssmodelid2)<=traf.cruiseLimVS))
#        
#        # Number of instantaneous conflicts between cruising and C/D aircraft inside square area 
#        asas.smodncflCruisingVS = sum((np.abs(vssmodelid1)<=traf.cruiseLimVS)*(np.abs(vssmodelid2)>traf.cruiseLimVS)) + \
#                                        sum((np.abs(vssmodelid1)>traf.cruiseLimVS)*(np.abs(vssmodelid2)<=traf.cruiseLimVS))
#                                        
#        # Number of instantaneous conflicts between C/D aircraft inside square area                                       
#        asas.smodncflVS = sum((np.abs(vssmodelid1)>traf.cruiseLimVS)*(np.abs(vssmodelid2)>traf.cruiseLimVS))
#    
    
    # SMODELLOG END -----------------------------------------------------------
    
    
    # CMODELLOG START ---------------------------------------------------------
    
#    # Only do anything is CIRCLEMODELAREA exists!
#    if 'CIRCLEMODELAREA' in areafilter.areas:
#        
#        # Determine the idx of the aircraft that have a conflict and are in the circle area (POSITION BASED 'OR' FILTERING)
#        incmodelareaid1 = areafilter.checkInside('CIRCLEMODELAREA', traf.lat[asas.instlogi], traf.lon[asas.instlogi], traf.alt[asas.instlogi])
#        incmodelareaid2 = areafilter.checkInside('CIRCLEMODELAREA', traf.lat[asas.instlogj], traf.lon[asas.instlogj], traf.alt[asas.instlogj])
#        incmodelarea  = list(np.where(np.logical_or(incmodelareaid1,incmodelareaid2))[0])
#        id1cmodelarea = list(np.asarray(asas.instlogi)[incmodelarea])
#        id2cmodelarea = list(np.asarray(asas.instlogj)[incmodelarea])
#        
#        
#        # Total number of instantaneous conflicts inside circle area
#        asas.cmodncfl = len(id1cmodelarea)
#        
#        # vertical speeds of aircraft in the instantaneous conflict lists that are also in the circle area
#        vscmodelid1 = traf.vs[id1cmodelarea]
#        vscmodelid2 = traf.vs[id2cmodelarea]
#        
#        # Number of instantaneous conflicts between cruising aircraft inside circle area
#        asas.cmodncflCruising = sum((np.abs(vscmodelid1)<=traf.cruiseLimVS)*(np.abs(vscmodelid2)<=traf.cruiseLimVS))
#        
#        # Number of instantaneous conflicts between cruising and C/D aircraft inside circle area
#        asas.cmodncflCruisingVS = sum((np.abs(vscmodelid1)<=traf.cruiseLimVS)*(np.abs(vscmodelid2)>traf.cruiseLimVS)) + \
#                                        sum((np.abs(vscmodelid1)>traf.cruiseLimVS)*(np.abs(vscmodelid2)<=traf.cruiseLimVS))
#                                        
#        # Number of instantaneous conflicts between C/D aircraft inside circle area                                      
#        asas.cmodncflVS = sum((np.abs(vscmodelid1)>traf.cruiseLimVS)*(np.abs(vscmodelid2)>traf.cruiseLimVS))
    
    # CMODELLOG END -----------------------------------------------------------
        
    # CFLLOG  START -----------------------------------------------------------
    # NOTE: some of the varaibles (which are based on lists ) are updated 
    #       in StateBasedCD        
    
    # Reset the CFL log variables that have not been reset in StateBasedCD
    asas.clogspawntimeid1 = []
    asas.clogtinconfid1 = []
    asas.clogtoutconfid1 = []
    asas.clogtcpaid1 = []
    asas.cloglatid1 = []
    asas.cloglonid1 = []
    asas.clogaltid1 = []
    asas.clogtasid1 = []
    asas.clogvsid1 = []
    asas.cloghdgid1 = []
    asas.clogasasactiveid1 = []
    asas.clogasasaltid1 = []
    asas.clogasastasid1 = []
    asas.clogasasvsid1 = []
    asas.clogasashdgid1 = []
    asas.clogspawntimeid2 = []
    asas.clogtinconfid2 = []
    asas.clogtoutconfid2 = []
    asas.clogtcpaid2 = []
    asas.cloglatid2 = []
    asas.cloglonid2 = []
    asas.clogaltid2 = []
    asas.clogtasid2 = []
    asas.clogvsid2 = []
    asas.cloghdgid2 = []
    asas.clogasasactiveid2 = []
    asas.clogasasaltid2 = []
    asas.clogasastasid2 = []
    asas.clogasasvsid2 = []
    asas.clogasashdgid2 = []
        
    # Update the lists if there is something to log
    if len(asas.clogi) > 0:

        # Update the variables belonging to id1
        asas.clogspawntimeid1 = traf.spawnTime[asas.clogi]
        asas.clogtinconfid1 = asas.tinconf[asas.clogi,asas.clogj]
        asas.clogtoutconfid1 = asas.toutconf[asas.clogi,asas.clogj]
        asas.clogtcpaid1 = asas.tcpa[asas.clogi,asas.clogj]
        asas.cloglatid1 = traf.lat[asas.clogi]
        asas.cloglonid1 = traf.lon[asas.clogi]
        asas.clogaltid1 = traf.alt[asas.clogi]
        asas.clogtasid1 = traf.tas[asas.clogi]
        asas.clogvsid1 = traf.vs[asas.clogi]
        asas.cloghdgid1 = traf.hdg[asas.clogi]
        asas.clogasasactiveid1 = asas.active[asas.clogi]
        asas.clogasasaltid1 = asas.alt[asas.clogi]
        asas.clogasastasid1 = asas.spd[asas.clogi]
        asas.clogasasvsid1 = asas.vs[asas.clogi]
        asas.clogasashdgid1 = asas.hdg[asas.clogi]

        # Update the variables belonging to id2
        asas.clogspawntimeid2 = traf.spawnTime[asas.clogj]
        asas.clogtinconfid2 = asas.tinconf[asas.clogj,asas.clogi]
        asas.clogtoutconfid2 = asas.toutconf[asas.clogj,asas.clogi]
        asas.clogtcpaid2 = asas.tcpa[asas.clogj,asas.clogi]
        asas.cloglatid2 = traf.lat[asas.clogj]
        asas.cloglonid2 = traf.lon[asas.clogj]
        asas.clogaltid2 = traf.alt[asas.clogj]
        asas.clogtasid2 = traf.tas[asas.clogj]
        asas.clogvsid2 = traf.vs[asas.clogj]
        asas.cloghdgid2 = traf.hdg[asas.clogj]
        asas.clogasasactiveid2 = asas.active[asas.clogj]
        asas.clogasasaltid2 = asas.alt[asas.clogj]
        asas.clogasastasid2 = asas.spd[asas.clogj]
        asas.clogasasvsid2 = asas.vs[asas.clogj]
        asas.clogasashdgid2 = asas.hdg[asas.clogj]
        
        # Finally, call the logger
        asas.cfllog.log()
    
    # CFLLOG END --------------------------------------------------------------
        
    # INSTLOG START -----------------------------------------------------------
    # NOTE: some of the varaibles (which are based on lists ) are updated 
    #       in StateBasedCD
    
    # Reset the INST log variables that have not been reset in StateBasedCD
    asas.instlogspawntimeid1 = []
    asas.instlogtinconfid1 = []
    asas.instlogtoutconfid1 = []
    asas.instlogtcpaid1 = []
    asas.instloglatid1 = []
    asas.instloglonid1 = []
    asas.instlogaltid1 = []
    asas.instlogtasid1 = []
    asas.instlogvsid1 = []
    asas.instloghdgid1 = []
    asas.instlogasasactiveid1 = []
    asas.instlogasasaltid1 = []
    asas.instlogasastasid1 = []
    asas.instlogasasvsid1 = []
    asas.instlogasashdgid1 = []
    asas.instlogspawntimeid2 = []
    asas.instlogtinconfid2 = []
    asas.instlogtoutconfid2 = []
    asas.instlogtcpaid2 = []
    asas.instloglatid2 = []
    asas.instloglonid2 = []
    asas.instlogaltid2 = []
    asas.instlogtasid2 = []
    asas.instlogvsid2 = []
    asas.instloghdgid2 = []
    asas.instlogasasactiveid2 = []
    asas.instlogasasaltid2 = []
    asas.instlogasastasid2 = []
    asas.instlogasasvsid2 = []
    asas.instlogasashdgid2 = []

    # Update the lists if there is something to log
    if len(asas.instlogi) > 0:
    
        # Update the variables belonging to id1
        asas.instlogspawntimeid1 = traf.spawnTime[asas.instlogi]
        asas.instlogtinconfid1 = asas.tinconf[asas.instlogi,asas.instlogj]
        asas.instlogtoutconfid1 = asas.toutconf[asas.instlogi,asas.instlogj]
        asas.instlogtcpaid1 = asas.tcpa[asas.instlogi,asas.instlogj]
        asas.instloglatid1 = traf.lat[asas.instlogi]
        asas.instloglonid1 = traf.lon[asas.instlogi]
        asas.instlogaltid1 = traf.alt[asas.instlogi]
        asas.instlogtasid1 = traf.tas[asas.instlogi]
        asas.instlogvsid1 = traf.vs[asas.instlogi]
        asas.instloghdgid1 = traf.hdg[asas.instlogi]
        asas.instlogasasactiveid1 = asas.active[asas.instlogi]
        asas.instlogasasaltid1 = asas.alt[asas.instlogi]
        asas.instlogasastasid1 = asas.spd[asas.instlogi]
        asas.instlogasasvsid1 = asas.vs[asas.instlogi]
        asas.instlogasashdgid1 = asas.hdg[asas.instlogi]

        # Update the variables belonging to id2
        asas.instlogspawntimeid2 = traf.spawnTime[asas.instlogj]
        asas.instlogtinconfid2 = asas.tinconf[asas.instlogj,asas.instlogi]
        asas.instlogtoutconfid2 = asas.toutconf[asas.instlogj,asas.instlogi]
        asas.instlogtcpaid2 = asas.tcpa[asas.instlogj,asas.instlogi]
        asas.instloglatid2 = traf.lat[asas.instlogj]
        asas.instloglonid2 = traf.lon[asas.instlogj]
        asas.instlogaltid2 = traf.alt[asas.instlogj]
        asas.instlogtasid2 = traf.tas[asas.instlogj]
        asas.instlogvsid2 = traf.vs[asas.instlogj]
        asas.instloghdgid2 = traf.hdg[asas.instlogj]
        asas.instlogasasactiveid2 = asas.active[asas.instlogj]
        asas.instlogasasaltid2 = asas.alt[asas.instlogj]
        asas.instlogasastasid2 = asas.spd[asas.instlogj]
        asas.instlogasasvsid2 = asas.vs[asas.instlogj]
        asas.instlogasashdgid2 = asas.hdg[asas.instlogj]    
    
    # INSTLOG END -------------------------------------------------------------

    # INTLOG START ------------------------------------------------------------
    
    # first check all the current active LOS and compute the severity
    logLOS(asas, traf)
        
    id1exists = np.asarray(asas.ilogid1exists)
    id2exists = np.asarray(asas.ilogid2exists)
    
    Fail = -999.999
#    Fail = 'Fail'
    
    # Reset intlog varaibles that have not been reset in logLOS
    asas.ilogspawntimeid1 = []
    asas.ilogtinconfid1 = []
    asas.ilogtoutconfid1 = []
    asas.ilogtcpaid1 = []
    asas.iloglatid1 = []
    asas.iloglonid1 = []
    asas.ilogaltid1 = []
    asas.ilogtasid1 = []
    asas.ilogvsid1 = []
    asas.iloghdgid1 = []
    asas.ilogasasactiveid1 = []
    asas.ilogasasaltid1 = []
    asas.ilogasastasid1 = []
    asas.ilogasasvsid1 = []
    asas.ilogasashdgid1 = []
    asas.ilogspawntimeid2 = []
    asas.ilogtinconfid2 = []
    asas.ilogtoutconfid2 = []
    asas.ilogtcpaid2 = []
    asas.iloglatid2 = []
    asas.iloglonid2 = []
    asas.ilogaltid2 = []
    asas.ilogtasid2 = []
    asas.ilogvsid2 = []
    asas.iloghdgid2 = []
    asas.ilogasasactiveid2 = []
    asas.ilogasasaltid2 = []
    asas.ilogasastasid2 = []
    asas.ilogasasvsid2 = []
    asas.ilogasashdgid2 = []

    # Update the lists if there is something to log        
    if len(asas.ilogi) > 0:   
        
        # Update the variables belonging to id1
        asas.ilogspawntimeid1 = np.where(id1exists, traf.spawnTime[asas.ilogi], Fail)
        asas.ilogtinconfid1 = np.where(id1exists & id2exists, asas.tinconf[asas.ilogi,asas.ilogj], Fail)
        asas.ilogtoutconfid1 = np.where(id1exists & id2exists, asas.toutconf[asas.ilogi,asas.ilogj], Fail)
        asas.ilogtcpaid1 = np.where(id1exists & id2exists, asas.tcpa[asas.ilogi,asas.ilogj], Fail)
        asas.iloglatid1 = np.where(id1exists, traf.lat[asas.ilogi], Fail)
        asas.iloglonid1 = np.where(id1exists, traf.lon[asas.ilogi], Fail)
        asas.ilogaltid1 = np.where(id1exists, traf.alt[asas.ilogi], Fail)
        asas.ilogtasid1 = np.where(id1exists, traf.tas[asas.ilogi], Fail)
        asas.ilogvsid1 = np.where(id1exists, traf.vs[asas.ilogi], Fail)
        asas.iloghdgid1 = np.where(id1exists, traf.hdg[asas.ilogi], Fail)
        asas.ilogasasactiveid1 = np.where(id1exists, asas.active[asas.ilogi], Fail)
        asas.ilogasasaltid1 = np.where(id1exists,asas.alt[asas.ilogi], Fail)
        asas.ilogasastasid1 = np.where(id1exists,asas.spd[asas.ilogi], Fail)
        asas.ilogasasvsid1 = np.where(id1exists,asas.vs[asas.ilogi], Fail)
        asas.ilogasashdgid1 = np.where(id1exists,asas.hdg[asas.ilogi], Fail)
        
        # Update the variables belonging to id2
        asas.ilogspawntimeid2 = np.where(id2exists, traf.spawnTime[asas.ilogj], Fail)
        asas.ilogtinconfid2 = np.where(id1exists & id2exists, asas.tinconf[asas.ilogj,asas.ilogi], Fail)
        asas.ilogtoutconfid2 = np.where(id1exists & id2exists, asas.toutconf[asas.ilogj,asas.ilogi], Fail)
        asas.ilogtcpaid2 = np.where(id1exists & id2exists, asas.tcpa[asas.ilogj,asas.ilogi], Fail)
        asas.iloglatid2 = np.where(id2exists, traf.lat[asas.ilogj], Fail)
        asas.iloglonid2 = np.where(id2exists, traf.lon[asas.ilogj], Fail)
        asas.ilogaltid2 = np.where(id2exists, traf.alt[asas.ilogj], Fail)
        asas.ilogtasid2 = np.where(id2exists, traf.tas[asas.ilogj], Fail)
        asas.ilogvsid2 = np.where(id2exists, traf.vs[asas.ilogj], Fail)
        asas.iloghdgid2 = np.where(id2exists, traf.hdg[asas.ilogj], Fail)
        asas.ilogasasactiveid2 = np.where(id2exists, asas.active[asas.ilogj], Fail)
        asas.ilogasasaltid2 = np.where(id2exists,asas.alt[asas.ilogj], Fail)
        asas.ilogasastasid2 = np.where(id2exists,asas.spd[asas.ilogj], Fail)
        asas.ilogasasvsid2 = np.where(id2exists,asas.vs[asas.ilogj], Fail)
        asas.ilogasashdgid2 = np.where(id2exists,asas.hdg[asas.ilogj], Fail)
        
        # Finally, call the logger
        asas.intlog.log()

    
def logLOS(asas, traf):
    # Check the current LOS and compute severity

    # Reset some INTLOG variables
    asas.ilogid1exists = []
    asas.ilogid2exists = []
    asas.ilogi         = []
    asas.ilogj         = []
    asas.ilogid1       = []
    asas.ilogid2       = []
    asas.ilogintsev    = []
    asas.iloginthsev   = []
    asas.ilogintvsev   = []
    
    for intrusion in asas.LOSlist_active[:]:
        gc.disable()
        
        # Determine the aircraft involved in this LOS
        ac1      = intrusion[0]
        ac2      = intrusion[1]
        id1, id2 = traf.id2idx(ac1), traf.id2idx(ac2)
        intid    = asas.LOSlist_active.index(intrusion)
        
        # Check is the aircraft still exist 
        id1exists = False if id1<0 else True
        id2exists = False if id2<0 else True        
        
        # If both ac exist then check if it is still a LOS
        if id1exists and id2exists:
            # LOS check
            dx     = (traf.lat[id1] - traf.lat[id2]) * 111319.
            dy     = (traf.lon[id1] - traf.lon[id2]) * 111319.
            hdist2 = dx**2 + dy**2
            hLOS   = hdist2 < asas.R**2
            vdist  = abs(traf.alt[id1] - traf.alt[id2])
            vLOS   = vdist < asas.dh
            isLOS  = (hLOS & vLOS)
            # if it is still a LOS, then compute the severity
            if isLOS:
                # Calculate the current intrusion severity for the current LOS
                Ih       = 1.0 - np.sqrt(hdist2) / asas.R
                Iv       = 1.0 - vdist / asas.dh
                severity = min(Ih, Iv)
                # Check if the severity is larger than the one logged for this LOS.
                # If so update the severity
                if severity >= asas.LOSmaxsev[intid]:
                    asas.LOSmaxsev[intid]  = severity
                    asas.LOShmaxsev[intid] = Ih
                    asas.LOSvmaxsev[intid] = Iv
                # If the severity is decreasing then log it the first time it starts decreasing    
                else: 
                    if intrusion not in asas.LOSlist_logged:
                        asas.ilogid1exists.append(id1exists)
                        asas.ilogid2exists.append(id2exists)
                        asas.ilogi.append(id1)
                        asas.ilogj.append(id2)
                        asas.ilogid1.append(ac1)
                        asas.ilogid2.append(ac2)
                        asas.ilogintsev.append(asas.LOSmaxsev[intid])
                        asas.iloginthsev.append(asas.LOShmaxsev[intid])
                        asas.ilogintvsev.append(asas.LOSvmaxsev[intid])
                        asas.LOSlist_logged.append(intrusion)
            # If it is no longer a LOS, check if it has been logged, and then delete it   
            else:
                if intrusion not in asas.LOSlist_logged:
                    asas.ilogid1exists.append(id1exists)
                    asas.ilogid2exists.append(id2exists)
                    asas.ilogi.append(id1)
                    asas.ilogj.append(id2)
                    asas.ilogid1.append(ac1)
                    asas.ilogid2.append(ac2)
                    asas.ilogintsev.append(asas.LOSmaxsev[intid])
                    asas.iloginthsev.append(asas.LOShmaxsev[intid])
                    asas.ilogintvsev.append(asas.LOSvmaxsev[intid])
                # Delete it completely 
                if intrusion in asas.LOSlist_logged:
                    asas.LOSlist_logged.remove(intrusion)
                asas.LOSlist_active.remove(intrusion)
                del asas.LOSmaxsev[intid]
                del asas.LOShmaxsev[intid]
                del asas.LOSvmaxsev[intid]           
        # If one or both of the both aircraft no longer exists, check if it has 
        # been logged and then delete it
        else:
            if intrusion not in asas.LOSlist_logged:
                asas.ilogid1exists.append(id1exists)
                asas.ilogid2exists.append(id2exists)
                asas.ilogi.append(id1)
                asas.ilogj.append(id2)
                asas.ilogid1.append(ac1)
                asas.ilogid2.append(ac2)
                asas.ilogintsev.append(asas.LOSmaxsev[intid])
                asas.iloginthsev.append(asas.LOShmaxsev[intid])
                asas.ilogintvsev.append(asas.LOSvmaxsev[intid])
            # Delete it completely
            if intrusion in asas.LOSlist_logged:
                asas.LOSlist_logged.remove(intrusion)
            asas.LOSlist_active.remove(intrusion)
            del asas.LOSmaxsev[intid]
            del asas.LOShmaxsev[intid]
            del asas.LOSvmaxsev[intid]
        
        gc.enable() 