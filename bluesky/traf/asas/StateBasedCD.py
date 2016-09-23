"""
State-based conflict detection


"""
import numpy as np
import gc
from ...tools import geo
from ...tools.aero import nm


def detect(dbconf, traf, simt):
    if not dbconf.swasas:
        return

    # Reset lists before new CD
    dbconf.iconf        = [[] for ac in range(traf.ntraf)]
    dbconf.nconf        = 0
    
    dbconf.rngowncpa    = []
    dbconf.latowncpa    = []
    dbconf.lonowncpa    = []
    dbconf.altowncpa    = []

    dbconf.LOSlist_now  = []
    dbconf.conflist_now = []
    dbconf.confpairs    = []
    
    dbconf.clogi         = []
    dbconf.clogj         = []
    dbconf.clogid1       = []
    dbconf.clogid2       = []
    dbconf.cloglatcpaid1 = []
    dbconf.clogloncpaid1 = []
    dbconf.clogaltcpaid1 = []
    dbconf.cloglatcpaid2 = []
    dbconf.clogloncpaid2 = []
    dbconf.clogaltcpaid2 = []
    
    dbconf.inslogi         = []
    dbconf.inslogj         = []
    dbconf.inslogid1       = []
    dbconf.inslogid2       = []
    dbconf.insloglatcpaid1 = []
    dbconf.inslogloncpaid1 = []
    dbconf.inslogaltcpaid1 = []
    dbconf.insloglatcpaid2 = []
    dbconf.inslogloncpaid2 = []
    dbconf.inslogaltcpaid2 = []
    
    dbconf.ilogi       = []
    dbconf.ilogj       = []
    dbconf.ilogid1     = []
    dbconf.ilogid2     = []
    dbconf.ilogintsev  = []
    dbconf.iloginthsev = []
    dbconf.ilogintvsev = []
    
    
    # Horizontal conflict ---------------------------------------------------------

    # qdlst is for [i,j] qdr from i to j, from perception of ADSB and own coordinates
    qdlst = geo.qdrdist_matrix(np.mat(traf.lat), np.mat(traf.lon),
                               np.mat(traf.adsblat), np.mat(traf.adsblon))

    # Convert results from mat-> array
    dbconf.qdr  = np.array(qdlst[0])  # degrees
    I           = np.eye(traf.ntraf)  # Identity matric of order ntraf
    dbconf.dist = np.array(qdlst[1]) * nm + 1e9 * I  # meters i to j

    # Transmission noise
    if traf.ADSBtransnoise:
        # error in the determined bearing between two a/c
        bearingerror = np.random.normal(0, traf.transerror[0], dbconf.qdr.shape)  # degrees
        dbconf.qdr += bearingerror
        # error in the perceived distance between two a/c
        disterror = np.random.normal(0, traf.transerror[1], dbconf.dist.shape)  # meters
        dbconf.dist += disterror

    # Calculate horizontal closest point of approach (CPA)
    qdrrad    = np.radians(dbconf.qdr)
    dbconf.dx = dbconf.dist * np.sin(qdrrad)  # is pos j rel to i
    dbconf.dy = dbconf.dist * np.cos(qdrrad)  # is pos j rel to i
    trkrad    = np.radians(traf.trk)
    dbconf.u  = traf.gs * np.sin(trkrad).reshape((1, len(trkrad)))  # m/s
    dbconf.v  = traf.gs * np.cos(trkrad).reshape((1, len(trkrad)))  # m/s

    # parameters received through ADSB
    adsbtrkrad = np.radians(traf.adsbtrk)
    adsbu      = traf.adsbgs * np.sin(adsbtrkrad).reshape((1, len(adsbtrkrad)))  # m/s
    adsbv      = traf.adsbgs * np.cos(adsbtrkrad).reshape((1, len(adsbtrkrad)))  # m/s

    # Compute relative velocity
    du   = dbconf.u - adsbu.T  # Speed du[i,j] is perceived eastern speed of i to j
    dv   = dbconf.v - adsbv.T  # Speed dv[i,j] is perceived northern speed of i to j
    dv2  = du * du + dv * dv
    dv2  = np.where(np.abs(dv2) < 1e-6, 1e-6, dv2)  # limit lower absolute value
    vrel = np.sqrt(dv2)

    dbconf.tcpa = -(du * dbconf.dx + dv * dbconf.dy) / dv2 + 1e9 * I

    # Calculate CPA positions
    # xcpa = dbconf.tcpa * du
    # ycpa = dbconf.tcpa * dv

    # Calculate distance^2 at CPA (minimum distance^2)
    dcpa2 = dbconf.dist * dbconf.dist - dbconf.tcpa * dbconf.tcpa * dv2

    # Check for horizontal conflict
    R2 = dbconf.R * dbconf.R
    swhorconf = dcpa2 < R2  # conflict or not

    # Calculate times of entering and leaving horizontal conflict
    dxinhor = np.sqrt(np.maximum(0., R2 - dcpa2))  # half the distance travelled inzide zone
    dtinhor = dxinhor / vrel
    tinhor  = np.where(swhorconf, dbconf.tcpa - dtinhor, 1e8)  # Set very large if no conf
    touthor = np.where(swhorconf, dbconf.tcpa + dtinhor, -1e8)  # set very large if no conf
    # swhorconf = swhorconf*(touthor>0)*(tinhor<dbconf.dtlook)

    # Vertical conflict -----------------------------------------------------------

    # Vertical crossing of disk (-dh,+dh)
    alt     = traf.alt.reshape((1, traf.ntraf))
    adsbalt = traf.adsbalt.reshape((1, traf.ntraf))

    if traf.ADSBtransnoise:
        # error in the determined altitude of other a/c
        alterror = np.random.normal(0, traf.transerror[2], adsbalt.shape)  # degrees
        adsbalt  = adsbalt + alterror

    dbconf.dalt = alt - adsbalt.T

    vs  = traf.vs.reshape(1, len(traf.vs))
    avs = traf.adsbvs.reshape(1, len(traf.adsbvs))
    dvs = vs - avs.T

    # Check for passing through each others zone
    dvs      = np.where(np.abs(dvs) < 1e-6, 1e-6, dvs)  # prevent division by zero
    tcrosshi = (dbconf.dalt + dbconf.dh) / -dvs
    tcrosslo = (dbconf.dalt - dbconf.dh) / -dvs

    tinver  = np.minimum(tcrosshi, tcrosslo)
    toutver = np.maximum(tcrosshi, tcrosslo)

    # Combine vertical and horizontal conflict-------------------------------------
    dbconf.tinconf  = np.maximum(tinver, tinhor)
    dbconf.toutconf = np.minimum(toutver, touthor)

    swconfl = swhorconf * (dbconf.tinconf <= dbconf.toutconf) * \
                (dbconf.toutconf > 0.) * (dbconf.tinconf < dbconf.dtlookahead) \
                * (1. - I)

    # ----------------------------------------------------------------------
    # Update conflict lists
    # ----------------------------------------------------------------------
    if len(swconfl) == 0:
        return    
    # Select conflicting pairs: each a/c gets their own record
    confidxs = np.where(swconfl)
    ownidx   = confidxs[0]
    intidx   = confidxs[1]
    
    # Do conflict area filtering
    if dbconf.swconfareafilt:
        ownidx, intidx, dbconf.rngowncpa, dbconf.latowncpa, dbconf.lonowncpa, dbconf.altowncpa \
                            = dbconf.ConfAreaFilter(traf, ownidx, intidx)
    else:
        # Determine CPA for ownship 
        dbconf.rngowncpa = dbconf.tcpa [ownidx,intidx] * traf.gs [ownidx] / nm
        dbconf.latowncpa, \
        dbconf.lonowncpa = geo.qdrpos(traf.lat[ownidx], traf.lon[ownidx], traf.trk [ownidx], dbconf.rngowncpa)
        dbconf.altowncpa = traf.alt [ownidx] + dbconf.tcpa [ownidx,intidx] * traf.vs[ownidx]
        
    # Number of CURRENTLY detected conflicts. All these conflicts satisfy the conflict-area-filter settings.
    dbconf.nconf = len(ownidx) 
    
    # Add to Conflict and LOS lists--------------------------------------------
    for idx in range(dbconf.nconf):
        gc.disable()        
        
        # Determine idx of conflciting aircaft
        i = ownidx[idx]
        j = intidx[idx]
        if i == j:
            continue
        
        dbconf.iconf[i].append(idx)
        dbconf.confpairs.append((traf.id[i], traf.id[j]))
        
        # Combinations of conflicting aircraft
        # NB: if only one A/C detects a conflict, it is also added to these lists
        combi  = (traf.id[i],traf.id[j])
        combi2 = (traf.id[j],traf.id[i])

        # cpa lat, lon and alt aircraft i (ownship in combi)
        rngi      = dbconf.tcpa[i,j]*traf.gs[i]/nm
        lati,loni = geo.qdrpos(traf.lat[i],traf.lon[i], traf.trk[i],rngi)
        alti      = traf.alt[i]+dbconf.tcpa[i,j]*traf.vs[i]

        # cpa lat, lon and alt aircraft j (intruder in combi)
        rngj      = dbconf.tcpa[i,j]*traf.gs[j]/nm
        latj,lonj = geo.qdrpos(traf.lat[j],traf.lon[j], traf.trk[j],rngj)
        altj      = traf.alt[j]+dbconf.tcpa[i,j]*traf.vs[j]

        # Update conflict lists: conflist_all (currently active conflicts) and 
        # all variables related to CFLLOG
        if combi not in dbconf.conflist_all and combi2 not in dbconf.conflist_all:
            dbconf.conflist_all.append(combi)
            # Now get the stuff you need for the CFLLOG variables!
            dbconf.clogi.append(i)
            dbconf.clogj.append(j)
            dbconf.clogid1.append(combi[0])
            dbconf.clogid2.append(combi[1])
            dbconf.cloglatcpaid1.append(lati)
            dbconf.clogloncpaid1.append(loni)
            dbconf.clogaltcpaid1.append(alti)
            dbconf.cloglatcpaid2.append(latj)
            dbconf.clogloncpaid2.append(lonj)
            dbconf.clogaltcpaid2.append(altj)
            
        # Update conflist_now (newly detected conflicts during this detection cycle)
        # and all variables related INSTLOG 
        if combi not in dbconf.conflist_now and combi2 not in dbconf.conflist_now:
            dbconf.conflist_now.append(combi)
            # Now get the stuff you need for the INSTLOG variables!
            dbconf.inslogi.append(i)
            dbconf.inslogj.append(j)
            dbconf.inslogid1.append(combi[0])
            dbconf.inslogid2.append(combi[1])
            dbconf.insloglatcpaid1.append(lati)
            dbconf.inslogloncpaid1.append(loni)
            dbconf.inslogaltcpaid1.append(alti)
            dbconf.insloglatcpaid2.append(latj)
            dbconf.inslogloncpaid2.append(lonj)
            dbconf.inslogaltcpaid2.append(altj)
                                    
        # Check if a LOS occured
        dx     = (traf.lat[i] - traf.lat[j]) * 111319.
        dy     = (traf.lon[i] - traf.lon[j]) * 111319.
        hdist2 = dx**2 + dy**2
        hLOS   = hdist2 < dbconf.R**2
        vdist  = abs(traf.alt[i] - traf.alt[j])
        vLOS   = vdist < dbconf.dh
        LOS    = (hLOS & vLOS)
        
        if LOS:
            # Update LOS lists: LOSlist_all (all LOS since ASAS is ON) and 
            # all variables related to INTLOG
            if combi not in dbconf.LOSlist_all and combi2 not in dbconf.LOSlist_all:
                dbconf.LOSlist_all.append(combi)
                dbconf.LOSmaxsev.append(0.)
                dbconf.LOShmaxsev.append(0.)
                dbconf.LOSvmaxsev.append(0.)
            
            # LOSlist_now (newly detected conflicts during this detection cycle)
            if combi not in dbconf.LOSlist_now and combi2 not in dbconf.LOSlist_now:
                dbconf.LOSlist_now.append(combi)

#            # Calculate the current intrusion severity for the current LOS
#            Ih       = 1.0 - np.sqrt(hdist2) / dbconf.R
#            Iv       = 1.0 - vdist / dbconf.dh
#            severity = min(Ih, Iv)
#            
#            # Only continue if combi is found in LOSlist (and not combi2)
#            try:  
#                idx = dbconf.LOSlist_all.index(combi)
#            except:
#                idx = -1
#            
#            # Update severity if new severity is bigger than the old value
#            if idx >= 0:
#                if severity > dbconf.LOSmaxsev[idx]:
#                    dbconf.LOSmaxsev[idx]  = severity
#                    dbconf.LOShmaxsev[idx] = Ih
#                    dbconf.LOSvmaxsev[idx] = Iv
#                    
#                else: # If the severity is decreasing then log it the first time it starts decreasing
#                    if combi not in dbconf.LOSlist_logged:
#                        dbconf.ilogi.append(i)
#                        dbconf.ilogj.append(j)
#                        dbconf.ilogid1.append(traf.id[i])
#                        dbconf.ilogid2.append(traf.id[j])
#                        dbconf.ilogintsev.append(dbconf.LOSmaxsev[idx])
#                        dbconf.iloginthsev.append(dbconf.LOShmaxsev[idx])
#                        dbconf.ilogintvsev.append(dbconf.LOSvmaxsev[idx])
#                        dbconf.LOSlist_logged.append(combi)                
        
        gc.enable()
        
    # ----------------------------------------------------------------------
    # Check if LOS has passed
    # ----------------------------------------------------------------------
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
                
        # If both ac exist then check if it is still a LOS
        if id1exists and id2exists:
            
            # LOS check
            dx     = (traf.lat[id1] - traf.lat[id2]) * 111319.
            dy     = (traf.lon[id1] - traf.lon[id2]) * 111319.
            hdist2 = dx**2 + dy**2
            hLOS   = hdist2 < dbconf.R**2
            vdist  = abs(traf.alt[id1] - traf.alt[id2])
            vLOS   = vdist < dbconf.dh
            LOS    = (hLOS & vLOS)
            
            # if it is a LOS, then compute the severity
            if LOS:
                
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
                dbconf.LOSllist_all.remove(intrusion)
                dbconf.LOSlist_logged.remove(intrusion)
                del dbconf.LOSmaxsev[intid]
                del dbconf.LOShmaxsev[intid]
                del dbconf.LOSvmaxsev[intid]           
        
        #if one or both of the both aircraft no longer exists, check if it has 
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
                
            # delete it completely (not from LOSlist_now)
            dbconf.LOSllist_all.remove(intrusion)
            dbconf.LOSlist_logged.remove(intrusion)
            del dbconf.LOSmaxsev[intid]
            del dbconf.LOShmaxsev[intid]
            del dbconf.LOSvmaxsev[intid]
        
        gc.enable()
                
        
        
        
        
        
    