"""
State-based conflict detection


"""
import numpy as np
from ...tools import geo
from ...tools.aero import nm


def detect(dbconf, traf, simt):
    if not dbconf.swasas:
        return

    # Reset lists before new CD
    dbconf.iconf        = [[] for ac in range(traf.ntraf)]
    dbconf.nconf        = 0
    dbconf.confpairs    = []
    dbconf.rngowncpa    = []
    dbconf.latowncpa    = []
    dbconf.lonowncpa    = []
    dbconf.altowncpa    = []
    dbconf.rngintcpa    = []
    dbconf.latintcpa    = []
    dbconf.lonintcpa    = []
    dbconf.altintcpa    = []

    dbconf.LOSlist_now  = []
    dbconf.conflist_now = []

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
        ownidx, intidx, dbconf.rngowncpa, dbconf.latowncpa, dbconf.lonowncpa, dbconf.altowncpa, \
                    dbconf.rngintcpa, dbconf.latintcpa, dbconf.lonintcpa, dbconf.altintcpa \
                            = dbconf.ConfAreaFilter(traf, ownidx, intidx)
    else:
        # Determine CPA for ownship 
        dbconf.rngowncpa = dbconf.tcpa [ownidx,intidx] * traf.gs [ownidx] / nm
        dbconf.latowncpa, \
        dbconf.lonowncpa = geo.qdrpos(traf.lat[ownidx], traf.lon[ownidx], traf.trk [ownidx], dbconf.rngowncpa)
        dbconf.altowncpa = traf.alt [ownidx] + dbconf.tcpa [ownidx,intidx] * traf.vs[ownidx]
        
        # Determine CPA for intruder (for logging)
        dbconf.rngintcpa = dbconf.tcpa[intidx,ownidx] * traf.gs[intidx] / nm
        dbconf.latintcpa, \
        dbconf.lonintcpa = geo.qdrpos(traf.lat[intidx], traf.lon[intidx], traf.trk[intidx], dbconf.rngintcpa)
        dbconf.altintcpa = traf.alt[intidx] + dbconf.tcpa[intidx,ownidx] * traf.vs[intidx]
    
    # Number of CURRENTLY Detected conflicts. All these conflicts satisfy the conflict-area-filter settings.
    dbconf.nconf = len(ownidx)
    
    # Add to Conflict and LOS lists------------------------------------------
    if dbconf.nconf > 0:

        # Combinations of conflicting aircraft
        # NB: if only one A/C detects a conflict, it is also added to these lists
        totalconfcombi  = [(str(traf.id[i]),str(traf.id[j])) for i,j in zip(ownidx,intidx)]
        uniqueconfcombi = list(set(tuple(sorted(l)) for l in totalconfcombi)) # we want only unique        
        
        # Update conflist_all (currently active conflicts) used for logging conflicts that occured and APorASAS  
        # NOTE: EXTEND WITH UNIQUE ONES THAT ARE DIFFERENT FROM WHAT ALREADY IN ALL!
        confcombidiff = list(set(uniqueconfcombi)-set(dbconf.conflist_all))
        dbconf.conflist_all.extend(confcombidiff) 
        
        # Update conflict_now used for resolving without ADSB/noise and logging instantaneous conflicts
        dbconf.conflist_now.extend(uniqueconfcombi)
        
        # Update confpairs used for resolving with ADSB/noise
        dbconf.confpairs.extend(totalconfcombi) 
        
        # Check if a LOS occured
        dx     = (traf.lat[ownidx] - traf.lat[intidx]) * 111319.
        dy     = (traf.lon[ownidx] - traf.lon[intidx]) * 111319.
        hdist2 = dx**2 + dy**2
        hLOS   = hdist2 < dbconf.R**2
        vdist  = abs(traf.alt[ownidx] - traf.alt[intidx])
        vLOS   = vdist < dbconf.dh
        LOS    = (hLOS & vLOS)    
        lostotalidx = np.where(LOS)[0] # index of los in total conflicts (including repetitions)
        
        if len(lostotalidx)>0:            
        
            # Combinations of intruding/LOS aircraft
            # NB: if only one A/C detects an intrusion, it is also added to these lists        
            LOScombi       = np.asarray(totalconfcombi)             
            LOScombi       = map(tuple, LOScombi[lostotalidx].tolist()) # get the conflicts that are also intrusions
            uniqueLOScombi = list(set(tuple(sorted(l)) for l in LOScombi)) # we want only unique
            
            # Indexes of unique intrusions from the original set of conflicts
            losuniqueidx = [index for (index, pair) in enumerate(totalconfcombi) if pair in uniqueLOScombi]            
            
            # Update LOSlist_all (all LOS since ASAS is ON) used for logging intrusions that occured
            # NOTE: EXTEND WITH UNIQUE ONES THAT ARE DIFFERENT!
            LOScombidiff  = list(set(uniqueLOScombi)-set(dbconf.LOSlist_all))
            dummyseverity = [0.0]*len(LOScombidiff)
            dbconf.LOSlist_all.extend(LOScombidiff)           
            dbconf.LOSmaxsev.extend(dummyseverity)
            dbconf.LOShmaxsev.extend(dummyseverity)
            dbconf.LOSvmaxsev.extend(dummyseverity)
            
            # Update loslist_now (could be used for logging instantaneous intrusions)
            dbconf.LOSlist_now.extend(uniqueLOScombi)
            
            # Find the indexes in LOSlist_all that contain LOScombi1(i.e., current LOSs) for severity 
            losnowidx = [index for (index, pair) in enumerate(dbconf.LOSlist_all) if pair in uniqueLOScombi]
            
            # Calculate the current intrusion severity for the current conflicts/LOS
            Ih       = 1.0 - np.sqrt(hdist2) / dbconf.R
            Iv       = 1.0 - vdist / dbconf.dh
            severity = np.minimum(Ih, Iv)
            Ih       = Ih[losuniqueidx]            
            Iv       = Iv[losuniqueidx]
            severity = severity[losuniqueidx]            
        
            # For the current LOSs, update severity if new severity is bigger than the old value             
            LOSmaxsev               = np.asarray(dbconf.LOSmaxsev)
            LOShmaxsev              = np.asarray(dbconf.LOShmaxsev)
            LOSvmaxsev              = np.asarray(dbconf.LOSvmaxsev)
            LOSmaxsev[losnowidx]    = np.where(severity > LOSmaxsev[losnowidx], severity, LOSmaxsev[losnowidx])
            LOShmaxsev[losnowidx]   = np.where(Ih > LOSmaxsev[losnowidx], Ih, LOShmaxsev[losnowidx])
            LOSvmaxsev[losnowidx]   = np.where(Iv > LOSmaxsev[losnowidx], Iv, LOSvmaxsev[losnowidx])            
            dbconf.LOSmaxsev        = LOSmaxsev.tolist()
            dbconf.LOShmaxsev       = LOShmaxsev.tolist()
            dbconf.LOSvmaxsev       = LOSvmaxsev.tolist()     
    
    # Loop to update iconf which is a list of lists
    for idx in range(dbconf.nconf):        
        
        # Determine idx of conflciting aircaft
        i = ownidx[idx]
        j = intidx[idx]
        if i == j:
            continue
        dbconf.iconf[i].append(idx)
