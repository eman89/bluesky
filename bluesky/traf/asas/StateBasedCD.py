"""
State-based conflict detection


"""
import numpy as np
import gc
from ...tools import geo
from ...tools.aero import nm


def detect(asas, traf, simt):
    if not asas.swasas:
        return

     # Reset asas lists before new CD
    asas.iconf        = [[] for ac in range(traf.ntraf)]
    asas.nconf        = 0
    
    asas.rngowncpa    = []
    asas.latowncpa    = []
    asas.lonowncpa    = []
    asas.altowncpa    = []

    asas.LOSlist_now  = []
    asas.conflist_now = []
    asas.confpairs    = []
    
    # Reset (some) asas logging lists before new CD
    asas.clogi         = []
    asas.clogj         = []
    asas.clogid1       = []
    asas.clogid2       = []
    asas.cloglatcpaid1 = []
    asas.clogloncpaid1 = []
    asas.clogaltcpaid1 = []
    asas.cloglatcpaid2 = []
    asas.clogloncpaid2 = []
    asas.clogaltcpaid2 = []
    
    asas.instlogi         = []
    asas.instlogj         = []
    asas.instlogid1       = []
    asas.instlogid2       = []
    asas.instloglatcpaid1 = []
    asas.instlogloncpaid1 = []
    asas.instlogaltcpaid1 = []
    asas.instloglatcpaid2 = []
    asas.instlogloncpaid2 = []
    asas.instlogaltcpaid2 = []
    
    # Reset variable for keeping track of number of current conflicts for display on GUI.
    asas.nconf_now = 0.0
    

    # Horizontal conflict ---------------------------------------------------------

    # qdlst is for [i,j] qdr from i to j, from perception of ADSB and own coordinates
    qdlst = geo.qdrdist_matrix(np.mat(traf.lat), np.mat(traf.lon),
                               np.mat(traf.adsb.lat), np.mat(traf.adsb.lon))

    # Convert results from mat-> array
    asas.qdr  = np.array(qdlst[0])  # degrees
    I           = np.eye(traf.ntraf)  # Identity matric of order ntraf
    asas.dist = np.array(qdlst[1]) * nm + 1e9 * I  # meters i to j

    # Transmission noise
    if traf.adsb.transnoise:
        # error in the determined bearing between two a/c
        bearingerror = np.random.normal(0, traf.adsb.transerror[0], asas.qdr.shape)  # degrees
        asas.qdr += bearingerror
        # error in the perceived distance between two a/c
        disterror = np.random.normal(0, traf.adsb.transerror[1], asas.dist.shape)  # meters
        asas.dist += disterror

    # Calculate horizontal closest point of approach (CPA)
    qdrrad    = np.radians(asas.qdr)
    asas.dx = asas.dist * np.sin(qdrrad)  # is pos j rel to i
    asas.dy = asas.dist * np.cos(qdrrad)  # is pos j rel to i

    trkrad   = np.radians(traf.trk)
    asas.u = traf.gs * np.sin(trkrad).reshape((1, len(trkrad)))  # m/s
    asas.v = traf.gs * np.cos(trkrad).reshape((1, len(trkrad)))  # m/s

    # parameters received through ADSB
    adsbtrkrad = np.radians(traf.adsb.trk)
    adsbu = traf.adsb.gs * np.sin(adsbtrkrad).reshape((1, len(adsbtrkrad)))  # m/s
    adsbv = traf.adsb.gs * np.cos(adsbtrkrad).reshape((1, len(adsbtrkrad)))  # m/s

    # Compute relative velocity
    du = asas.u - adsbu.T  # Speed du[i,j] is perceived eastern speed of i to j
    dv = asas.v - adsbv.T  # Speed dv[i,j] is perceived northern speed of i to j
    dv2 = du * du + dv * dv
    dv2 = np.where(np.abs(dv2) < 1e-6, 1e-6, dv2)  # limit lower absolute value
    vrel = np.sqrt(dv2)
    asas.tcpa = -(du * asas.dx + dv * asas.dy) / dv2 + 1e9 * I

    # Calculate CPA positions
    # xcpa = asas.tcpa * du
    # ycpa = asas.tcpa * dv

    # Calculate distance^2 at CPA (minimum distance^2)
    dcpa2 = asas.dist * asas.dist - asas.tcpa * asas.tcpa * dv2

    # Check for horizontal conflict
    R2 = asas.R * asas.R
    swhorconf = dcpa2 < R2  # conflict or not

    # Calculate times of entering and leaving horizontal conflict
    dxinhor = np.sqrt(np.maximum(0., R2 - dcpa2))  # half the distance travelled inzide zone
    dtinhor = dxinhor / vrel
    tinhor = np.where(swhorconf, asas.tcpa - dtinhor, 1e8)  # Set very large if no conf
    touthor = np.where(swhorconf, asas.tcpa + dtinhor, -1e8)  # set very large if no conf
    # swhorconf = swhorconf*(touthor>0)*(tinhor<asas.dtlook)

    # Vertical conflict -----------------------------------------------------------

    # Vertical crossing of disk (-dh,+dh)
    alt = traf.alt.reshape((1, traf.ntraf))
    adsbalt = traf.adsb.alt.reshape((1, traf.ntraf))
    
    if traf.adsb.transnoise:
        # error in the determined altitude of other a/c
        alterror = np.random.normal(0, traf.adsb.transerror[2], traf.alt.shape)  # degrees
        adsbalt += alterror

    asas.dalt = alt - adsbalt.T


    vs = traf.vs.reshape(1, len(traf.vs))
    avs = traf.adsb.vs.reshape(1, len(traf.adsb.vs))
    dvs = vs - avs.T

    # Check for passing through each others zone
    dvs = np.where(np.abs(dvs) < 1e-6, 1e-6, dvs)  # prevent division by zero
    tcrosshi = (asas.dalt + asas.dh) / -dvs
    tcrosslo = (asas.dalt - asas.dh) / -dvs

    tinver  = np.minimum(tcrosshi, tcrosslo)
    toutver = np.maximum(tcrosshi, tcrosslo)

    # Combine vertical and horizontal conflict-------------------------------------
    asas.tinconf = np.maximum(tinver, tinhor)
    asas.toutconf = np.minimum(toutver, touthor)
    
    # Boolean matrix of conflict or no conflict for each ac
    swconfl = swhorconf * (asas.tinconf <= asas.toutconf) * \
        (asas.toutconf > 0.) * (asas.tinconf < asas.dtlookahead) \
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
    if asas.swconfareafilt:
        ownidx, intidx, asas.rngowncpa, asas.latowncpa, asas.lonowncpa, asas.altowncpa \
                            = asas.ConfAreaFilter(traf, ownidx, intidx)
    else:
        # Determine CPA for ownship 
        asas.rngowncpa = asas.tcpa [ownidx,intidx] * traf.gs [ownidx] / nm
        asas.latowncpa, \
        asas.lonowncpa = geo.qdrpos(traf.lat[ownidx], traf.lon[ownidx], traf.trk [ownidx], asas.rngowncpa)
        asas.altowncpa = traf.alt [ownidx] + asas.tcpa [ownidx,intidx] * traf.vs[ownidx]
        
    # Number of CURRENTLY detected conflicts. All these conflicts satisfy the conflict-area-filter settings.
    asas.nconf = len(ownidx) 
    
    # Add to Conflict and LOS lists--------------------------------------------
    for idx in range(asas.nconf):
        gc.disable()
        
        # Determine idx of conflciting aircaft
        i = ownidx[idx]
        j = intidx[idx]
        if i == j:
            continue
        
        asas.iconf[i].append(idx)
        
        # Append all conflicts to confpairs list. This is used if ADSB is active
        # to solve conflicts.
        asas.confpairs.append((traf.id[i], traf.id[j]))
        
        # Combinations of conflicting aircraft
        # NB: if only one A/C detects a conflict, it is also added to these lists
        combi  = (traf.id[i],traf.id[j])
        combi2 = (traf.id[j],traf.id[i])

        # cpa lat, lon and alt aircraft i (ownship in combi)
        rngi      = asas.tcpa[i,j]*traf.gs[i]/nm
        lati,loni = geo.qdrpos(traf.lat[i],traf.lon[i], traf.trk[i],rngi)
        alti      = traf.alt[i]+asas.tcpa[i,j]*traf.vs[i]

        # cpa lat, lon and alt aircraft j (intruder in combi)
        rngj      = asas.tcpa[j,i]*traf.gs[j]/nm
        latj,lonj = geo.qdrpos(traf.lat[j],traf.lon[j], traf.trk[j],rngj)
        altj      = traf.alt[j]+asas.tcpa[j,i]*traf.vs[j]

        # Update conflist_active (currently active conflicts), nconf_total (GUI)
        # and some variables related to CFLLOG (others updated in asasLogUpdate())
        # and also do RESOSPAWNCHECK
        if combi not in asas.conflist_active and combi2 not in asas.conflist_active:
            asas.nconf_total = asas.nconf_total + 1    
            # Check if conflict tcpa and tinconf is greater than 0. only log 
            # if condition met
            if asas.tcpa[i,j] >= 0 and  asas.tcpa[j,i] >= 0 and \
                asas.tinconf[i,j] >= 0 and  asas.tinconf[j,i] >= 0: 
                    asas.conflist_active.append(combi)
                    # Now get the stuff you need for the CFLLOG variables!
                    asas.clogi.append(i)
                    asas.clogj.append(j)
                    asas.clogid1.append(combi[0])
                    asas.clogid2.append(combi[1])
                    asas.cloglatcpaid1.append(lati)
                    asas.clogloncpaid1.append(loni)
                    asas.clogaltcpaid1.append(alti)
                    asas.cloglatcpaid2.append(latj)
                    asas.clogloncpaid2.append(lonj)
                    asas.clogaltcpaid2.append(altj)
           
            # If RESOSPAWNCHECK is active, then check if this conflict cotains
            # an aircraft that is just spawned, and if that conflict is a very short term conflict.
            # If so, then add it to the 'conflist_resospawncheck' list
            if asas.swspawncheck:
                if abs(simt-traf.spawnTime[i]) <= asas.dtasas or abs(simt-traf.spawnTime[j]) <= asas.dtasas:
                    if asas.tcpa[i,j] <= asas.dtlookahead*asas.spawncheckfactor or asas.tcpa[j,i] <= asas.dtlookahead*asas.spawncheckfactor:
                        asas.conflist_resospawncheck.append(combi)
                        
        # Update conflist_now (newly detected conflicts during this detection cycle)
        # and some variables related INSTLOG (others updated in asasLogUpdate())
        if combi not in asas.conflist_now and combi2 not in asas.conflist_now:
            # Check if conflict tcpa and tinconf is greater than 0. only log 
            # and resolve if condition met
            asas.nconf_now = asas.nconf_now + 1.0 # not a LOS, update it now
            if asas.tcpa[i,j] >= 0 and  asas.tcpa[j,i] >= 0 and \
                asas.tinconf[i,j] >= 0 and  asas.tinconf[j,i] >= 0:
                    asas.conflist_now.append(combi)
                    # Now get the stuff you need for the INSTLOG variables!
                    asas.instlogi.append(i)
                    asas.instlogj.append(j)
                    asas.instlogid1.append(combi[0])
                    asas.instlogid2.append(combi[1])
                    asas.instloglatcpaid1.append(lati)
                    asas.instlogloncpaid1.append(loni)
                    asas.instlogaltcpaid1.append(alti)
                    asas.instloglatcpaid2.append(latj)
                    asas.instlogloncpaid2.append(lonj)
                    asas.instlogaltcpaid2.append(altj)
                                                
        # Check if a LOS occured
        dx     = (traf.lat[i] - traf.lat[j]) * 111319.
        dy     = (traf.lon[i] - traf.lon[j]) * 111319.
        hdist2 = dx**2 + dy**2
        hLOS   = hdist2 < asas.R**2
        vdist  = abs(traf.alt[i] - traf.alt[j])
        vLOS   = vdist < asas.dh
        isLOS  = (hLOS & vLOS)
        
        if isLOS:
            asas.nconf_now  = asas.nconf_now-0.5 # to prevent unnecessary double counting for GUI counter
            # Update LOS lists: LOSlist_active (all LOS that are active) and nLOS_total (GUI)
            if combi not in asas.LOSlist_active and combi2 not in asas.LOSlist_active:                
                asas.nLOS_total = asas.nLOS_total + 1  
                asas.LOSlist_active.append(combi)
                asas.LOSmaxsev.append(0.)
                asas.LOShmaxsev.append(0.)
                asas.LOSvmaxsev.append(0.)
            
            # LOSlist_now (newly detected conflicts during this detection cycle)
            if combi not in asas.LOSlist_now and combi2 not in asas.LOSlist_now:
                asas.LOSlist_now.append(combi)
                
            
            # NOTE: Logging for LOS done in logLOS() in asasLogUpdate.py
            #       This is because a LOS is only logged when its severity is 
            #       highest.
            #       Some variables for conflicts are also logged in asasLogUpdate
            #       but some are logged here are  as they are based on lists (easier here in loop)
        
        gc.enable()
#    asas.nconf_now = int(asas.nconf_now)
