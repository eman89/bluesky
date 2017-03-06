import numpy as np
from math import *
from random import random, randint
from ..tools import datalog, logHeader, areafilter
from ..tools.misc import latlon2txt
from ..tools.aero import fpm, kts, ft, g0, Rearth, \
                         vatmos,  vtas2cas, vtas2mach, casormach

from ..tools.dynamicarrays import DynamicArrays, RegisterElementParameters

from windsim import WindSim

from trails import Trails
from adsbmodel import ADSB
from asas import ASAS
from pilot import Pilot
from autopilot import Autopilot
from activewpdata import ActiveWaypoint
from turbulence import Turbulence
from area import Area

from .. import settings

try:
    if settings.performance_model == 'bluesky':
        print 'Using BlueSky performance model'
        from perf import Perf

    elif settings.performance_model == 'bada':
        from perfbada import PerfBADA as Perf

except ImportError as err:
    print err.args[0]
    print 'Falling back to BlueSky performance model'
    from perf import Perf


class Traffic(DynamicArrays):
    """
    Traffic class definition    : Traffic data
    Methods:
        Traffic()            :  constructor
        reset()              :  Reset traffic database w.r.t a/c data
        create(acid,actype,aclat,aclon,achdg,acalt,acspd) : create aircraft
        delete(acid)         : delete an aircraft from traffic data
        deletall()           : delete all traffic
        update(sim)          : do a numerical integration step
        id2idx(name)         : return index in traffic database of given call sign
        engchange(i,engtype) : change engine type of an aircraft
        setNoise(A)          : Add turbulence
    Members: see create
    Created by  : Jacco M. Hoekstra
    """

    def __init__(self, navdb):
        self.wind = WindSim()

        # Define the periodic loggers
        datalog.definePeriodicLogger('SNAPLOG', logHeader.snapHeader(), settings.snapdt)
        datalog.definePeriodicLogger('SKYLOG', logHeader.skyHeader(), settings.skydt)
        datalog.definePeriodicLogger('SMODELLOG', logHeader.smodelHeader(), settings.skydt)
        datalog.definePeriodicLogger('CMODELLOG', logHeader.cmodelHeader(), settings.skydt)
        
        # Define event based loggers
        self.flstlog = datalog.defineLogger("FLSTLOG", logHeader.flstHeader())    
        
        # Register the following parameters for SKY logging
        with datalog.registerLogParameters('SKYLOG', self):
            self.ntraf = 0
            self.ntrafCruising = 0
            self.ntrafVS = 0
            self.gammaAll = 0.0 # [deg]            
            self.gammaVS = 0.0 # [deg]
        
        # Register the following parameters for SMODELLOG logging
        with datalog.registerLogParameters('SMODELLOG', self):
            self.smodntraf = 0
            self.smodntrafCruising = 0
            self.smodntrafVS = 0
            self.smodgammaAll = 0.0 # [deg]            
            self.smodgammaVS = 0.0 # [deg]
        
        # Register the following parameters for CMODELLOG logging
        with datalog.registerLogParameters('CMODELLOG', self):
            self.cmodntraf = 0
            self.cmodntrafCruising = 0
            self.cmodntrafVS = 0
            self.cmodgammaAll = 0.0 # [deg]            
            self.cmodgammaVS = 0.0 # [deg]
        
        # Register the following parameters for FLST logging
        with datalog.registerLogParameters('FLSTLOG', self):
            self.flogid = []
            self.flogspawntime = []
            self.flogflightime = []
            self.flogdistance2D = []
            self.flogdistance3D = []
            self.flogwork = []
            self.floglat = []
            self.floglon = []
            self.flogalt = []
            self.flogtas = []
            self.flogvs = []
            self.floghdg = []
            self.flogoriglat = []
            self.flogoriglon = []
            self.flogdestlat = []
            self.flogdestlon = []
            self.flogasasactive = []
            self.flogpilotalt = []
            self.flogpilottas = []
            self.flogpilotvs = []
            self.flogpilothdg = []            
        
        # Register the following parameters as Dynamic Arrays 
        with RegisterElementParameters(self):

            # Register the following parameters for SNAP logging
            with datalog.registerLogParameters('SNAPLOG', self):
                # Aircraft Info
                self.id        = []           # identifier (string)
                self.spawnTime = np.array([]) # aircraft creation times [s]

                # Positions
                self.lat     = np.array([])  # latitude [deg]
                self.lon     = np.array([])  # longitude [deg]
                self.alt     = np.array([])  # altitude [m]
                
                # Velocities
                self.tas     = np.array([])  # true airspeed [m/s]
                self.vs      = np.array([])  # vertical speed [m/s]
                
                # Heading
                self.hdg     = np.array([])  # traffic heading [deg]
            
            # Efficiency related variables
            self.distance2D = np.array([])   # Horizontal flight distance [m]
            self.distance3D = np.array([])   # 3D flight distance [m]
            self.work       = np.array([])   # Work Done [J]
            
            # Flight path angle [deg]
            self.gamma = np.array([])

            # Aircraft Info
            self.type    = []            # aircaft type (string)
            
            # Positions
            self.trk     = np.array([])  # track angle [deg]
            
            # Velocities
            self.gs      = np.array([])  # ground speed [m/s]
            self.gsnorth = np.array([])  # ground speed [m/s]
            self.gseast  = np.array([])  # ground speed [m/s]
            self.cas     = np.array([])  # calibrated airspeed [m/s]
            self.M       = np.array([])  # mach number

            # Whether to perform LNAV and VNAV
            self.swlnav   = np.array([], dtype=np.bool)
            self.swvnav   = np.array([], dtype=np.bool)
            
            # Traffic autopilot settings
            self.aspd   = np.array([])  # selected spd(CAS) [m/s]
            self.aptas  = np.array([])  # just for initializing
            self.ama    = np.array([])  # selected spd above crossover altitude (Mach) [-]
            self.apalt  = np.array([])  # selected alt[m]
            self.avs    = np.array([])  # selected vertical speed [m/s]
            
            # Atmosphere
            self.p       = np.array([])  # air pressure [N/m2]
            self.rho     = np.array([])  # air density [kg/m3]
            self.Temp    = np.array([])  # air temperature [K]
            self.dtemp   = np.array([])  # delta t for non-ISA conditions

            # Flight Models
            self.ap     = Autopilot(self)
            self.asas   = ASAS(self)
            self.pilot  = Pilot(self)
            self.adsb   = ADSB(self)
            self.trails = Trails(self)
            self.actwp  = ActiveWaypoint(self)

            # Traffic performance data
            self.avsdef = np.array([])  # [m/s]default vertical speed of autopilot
            self.aphi   = np.array([])  # [rad] bank angle setting of autopilot
            self.ax     = np.array([])  # [m/s2] absolute value of longitudinal accelleration
            self.bank   = np.array([])  # nominal bank angle, [radian]
            self.hdgsel = np.array([], dtype=np.bool)  # determines whether aircraft is turning

            # Crossover altitude
            self.abco   = np.array([])
            self.belco  = np.array([])

            # limit settings
            self.limspd      = np.array([])  # limit speed
            self.limspd_flag = np.array([], dtype=np.bool)  # flag for limit spd - we have to test for max and min
            self.limalt      = np.array([])  # limit altitude
            self.limvs       = np.array([])  # limit vertical speed due to thrust limitation
            self.limvs_flag  = np.array([])

            # Display information on label
            self.label       = []  # Text and bitmap of traffic label

            # Miscallaneous
            self.coslat = np.array([])  # Cosine of latitude for computations
            self.eps    = np.array([])  # Small nonzero numbers
            
        # Default bank angles per flight phase
        self.bphase = np.deg2rad(np.array([15, 35, 35, 35, 15, 45]))
        
        self.reset(navdb)

    def reset(self, navdb):
        # This ensures that the traffic arrays (which size is dynamic)
        # are all reset as well, so all lat,lon,sdp etc but also objects adsb
        super(Traffic, self).reset()

        # SKY Log count variables reset 
        self.ntraf = 0
        self.ntrafCruising = 0
        self.ntrafVS = 0
        self.gammaAll = 0.0 # [deg]            
        self.gammaVS = 0.0 # [deg]
        
        # SMODEL Log count variables reset
        self.smodntraf = 0
        self.smodntrafCruising = 0
        self.smodntrafVS = 0
        self.smodgammaAll = 0.0 # [deg]            
        self.smodgammaVS = 0.0 # [deg]
        
        # CMODEL Log count variables reset
        self.cmodntraf = 0
        self.cmodntrafCruising = 0
        self.cmodntrafVS = 0
        self.cmodgammaAll = 0.0 # [deg]            
        self.cmodgammaVS = 0.0 # [deg]

        # Reset models
        self.wind.clear()

        # Build new modules for area and turbulence
        self.area       = Area(self)
        self.Turbulence = Turbulence(self)

        # Noise (turbulence, ADBS-transmission noise, ADSB-truncated effect)
        self.setNoise(False)

        # Import navigation data base
        self.navdb   = navdb

        # Default: BlueSky internal performance model.
        # Insert your BADA files to the folder "BlueSky/data/coefficients/BADA"
        # for working with EUROCONTROL`s Base of Aircraft Data revision 3.12
        self.perf    = Perf(self)
        
        # VS threshold to determine which aircraft are cruising aircraft [m/s]
        self.cruiseLimVS = 25.0*fpm

    def mcreate(self, count, actype=None, alt=None, spd=None, dest=None, area=None):
        """ Create multiple random aircraft in a specified area """
        idbase = chr(randint(65, 90)) + chr(randint(65, 90))
        if actype is None:
            actype = 'B744'

        for i in xrange(count):
            acid  = idbase + '%05d' % i
            aclat = random() * (area[1] - area[0]) + area[0]
            aclon = random() * (area[3] - area[2]) + area[2]
            achdg = float(randint(1, 360))
            acalt = (randint(2000, 39000) * ft) if alt is None else alt
            acspd = (randint(250, 450) * kts) if spd is None else spd

            self.create(acid, actype, aclat, aclon, achdg, acalt, acspd)

    def create(self, sim, acid=None, actype="B744", aclat=None, aclon=None, achdg=None, acalt=None, casmach=None):
        """Create an aircraft"""

        # Check if not already exist
        if self.id.count(acid.upper()) > 0:
            return False, acid + " already exists."  # already exists do nothing

        # Catch missing acid, replace by a default
        if acid is None or acid == "*":
            acid = "KL204"
            flno = 204
            while self.id.count(acid) > 0:
                flno = flno + 1
                acid = "KL" + str(flno)

        # Check for (other) missing arguments
        if actype is None or aclat is None or aclon is None or achdg is None \
                or acalt is None or casmach is None:

            return False, "CRE: Missing one or more arguments:"\
                          "acid,actype,aclat,aclon,achdg,acalt,acspd"

        super(Traffic, self).create()

        # Increase number of aircraft
        self.ntraf = self.ntraf + 1

        # Aircraft Info
        self.id[-1]   = acid.upper()
        self.type[-1] = actype

        # Positions
        self.lat[-1]  = aclat
        self.lon[-1]  = aclon
        self.alt[-1]  = acalt

        self.hdg[-1]  = achdg
        self.trk[-1]  = achdg

        # Velocities
        self.tas[-1], self.cas[-1], self.M[-1] = casormach(casmach, acalt)
        self.gs[-1]      = self.tas[-1]
        self.gsnorth[-1] = self.tas[-1] * cos(radians(self.hdg[-1]))
        self.gseast[-1]  = self.tas[-1] * sin(radians(self.hdg[-1]))

        # Atmosphere
        self.p[-1], self.rho[-1], self.Temp[-1] = vatmos(acalt)

        # Wind
        if self.wind.winddim > 0:
            vnwnd, vewnd     = self.wind.getdata(self.lat[-1], self.lon[-1], self.alt[-1])
            self.gsnorth[-1] = self.gsnorth[-1] + vnwnd
            self.gseast[-1]  = self.gseast[-1]  + vewnd
            self.trk[-1]     = np.degrees(np.arctan2(self.gseast[-1], self.gsnorth[-1]))
            self.gs[-1]      = np.sqrt(self.gsnorth[-1]**2 + self.gseast[-1]**2)

        # Traffic performance data
        #(temporarily default values)
#        self.avsdef[-1] = 1500. * fpm   # default vertical speed of autopilot
        # set the default vertical speed based on the steepness defined in autopilot
        # protect against zero/invalid ground speed value
        self.avsdef[-1] = self.ap.steepness * (self.gs[-1] +
                                  (self.gs[-1] < 0.2 * self.tas[-1]) * self.tas[-1])
        self.aphi[-1]   = radians(25.)  # bank angle setting of autopilot
        self.ax[-1]     = kts           # absolute value of longitudinal accelleration
        self.bank[-1]   = radians(25.)

        # Crossover altitude
        self.abco[-1]   = 0  # not necessary to overwrite 0 to 0, but leave for clarity
        self.belco[-1]  = 1

        # Traffic autopilot settings
        self.aspd[-1]  = self.cas[-1]
        self.aptas[-1] = self.tas[-1]
        self.apalt[-1] = self.alt[-1]

        # Display information on label
        self.label[-1] = ['', '', '', 0]

        # Miscallaneous
        self.coslat[-1] = cos(radians(aclat))  # Cosine of latitude for flat-earth aproximations
        self.eps[-1] = 0.01
        
        # Flight Statistics
        self.spawnTime[-1] = sim.simt
        
        # Efficiency related variables
        self.distance2D[-1] = 0.0   # Horizontal flight distance [m]
        self.distance3D[-1] = 0.0   # 3D flight distance [m]
        self.work[-1]       = 0.0   # Work Done [J]
        
        # Flight path angle [deg]
        self.gamma[-1] = np.degrees(np.arctan2(self.vs[-1],self.tas[-1]))

        # ----- Submodules of Traffic -----
        self.ap.create()
        self.actwp.create()
        self.pilot.create()
        self.adsb.create()
        self.area.create()
        self.asas.create()
        self.perf.create()
        self.trails.create()

        return True

    def delete(self, acid):
        """Delete an aircraft"""

        # Look up index of aircraft
        idx = self.id2idx(acid)
        # Do nothing if not found
        if idx < 0:
            return False
        # Decrease number of aircraft
        self.ntraf = self.ntraf - 1

        # Delete all aircraft parameters
        super(Traffic, self).delete(idx)

        # ----- Submodules of Traffic -----
        self.perf.delete(idx)
        self.area.delete(idx)
        return True

    def update(self, simt, simdt):
        # Update only if there is traffic ---------------------
        if self.ntraf == 0:
            return
        
        #---------- Atmosphere --------------------------------
        self.p, self.rho, self.Temp = vatmos(self.alt)

        #---------- ADSB Update -------------------------------
        self.adsb.update(simt)

        #---------- Fly the Aircraft --------------------------
        self.ap.update(simt)
        self.asas.update(simt)
        self.pilot.FMSOrAsas()

        #---------- Limit Speeds ------------------------------
        self.pilot.FlightEnvelope()

        #---------- Kinematics --------------------------------
        self.UpdateAirSpeed(simdt, simt)
        self.UpdateGroundSpeed(simdt)
        self.UpdatePosition(simdt)

        #---------- Performance Update ------------------------
        self.perf.perf(simt)
        
        #---------- Simulate Turbulence -----------------------
        self.Turbulence.Woosh(simdt)

        #---------- Aftermath ---------------------------------
        self.trails.update(simt)
        self.area.check(simt)
        
        #---------- Flight Efficiency Update ------------------
        self.UpdateEfficiency(simdt)
        
        #---------- SKY/MODEL Logs Traf Count Update ----------
        self.UpdateTrafCountSkyLog()
        self.UpdateTrafCountSModelLog()
        self.UpdateTrafCountCModelLog()
        
        return

    def UpdateAirSpeed(self, simdt, simt):
        # Acceleration
        self.delspd = self.pilot.spd - self.tas
        swspdsel = np.abs(self.delspd) > 0.001  # <1 kts = 0.514444 m/s
        ax = self.perf.acceleration(simdt)

        # Update velocities
        self.tas = self.tas + swspdsel * ax * np.sign(self.delspd) * simdt
        self.cas = vtas2cas(self.tas, self.alt)
        self.M   = vtas2mach(self.tas, self.alt)

        # Turning
        turnrate = np.degrees(g0 * np.tan(self.bank) / np.maximum(self.tas, self.eps))
        delhdg   = (self.pilot.hdg - self.hdg + 180.) % 360 - 180.  # [deg]
        self.hdgsel = np.abs(delhdg) > np.abs(1. * simdt * turnrate)

        # Update heading
        self.hdg = (self.hdg + simdt * turnrate * self.hdgsel * np.sign(delhdg)) % 360.

        # Update vertical speed
        delalt   = self.pilot.alt - self.alt
        self.swaltsel = np.abs(delalt) > np.maximum(10 * ft, np.abs(2 * simdt * np.abs(self.vs)))
        self.vs  = self.swaltsel * np.sign(delalt) * self.pilot.vs

    def UpdateGroundSpeed(self, simdt):
        # Compute ground speed and track from heading, airspeed and wind
        if self.wind.winddim == 0:  # no wind
            self.gsnorth  = self.tas * np.cos(np.radians(self.hdg))
            self.gseast   = self.tas * np.sin(np.radians(self.hdg))

            self.gs  = self.tas
            self.trk = self.hdg

        else:
            windnorth, windeast = self.wind.getdata(self.lat, self.lon, self.alt)
            self.gsnorth  = self.tas * np.cos(np.radians(self.hdg)) + windnorth
            self.gseast   = self.tas * np.sin(np.radians(self.hdg)) + windeast

            self.gs  = np.sqrt(self.gsnorth**2 + self.gseast**2)
            self.trk = np.degrees(np.arctan2(self.gseast, self.gsnorth)) % 360.

    def UpdatePosition(self, simdt):
        # Update position 
        self.alt = np.where(self.swaltsel, self.alt + self.vs * simdt, self.pilot.alt)
        self.lat = self.lat + np.degrees(simdt * self.gsnorth / Rearth)
        self.coslat = np.cos(np.deg2rad(self.lat))
        self.lon = self.lon + np.degrees(simdt * self.gseast / self.coslat / Rearth)
        
        # Update flight path angle [deg]
        self.gamma = np.degrees(np.arctan2(self.vs,self.tas))
        
        # print out the flight path angle
#        print "Gamma: %s" %(np.degrees(np.arctan2(self.vs,self.tas)))
#        print "TAS  : %s" %(self.tas/kts)
#        print "VS   : %s" %(self.vs/fpm)
#        print
    
    def UpdateEfficiency(self, simdt):
        # Update flight efficiency metrics
        
        # Horizontal distance [m]
        self.distance2D = self.distance2D + (simdt*self.gs)
        
        # 3D distance [m]
        resultantspd = np.sqrt(self.gs*self.gs + self.vs*self.vs)
        self.distance3D = self.distance3D + (simdt*resultantspd)
        
        # Work Done [MJ] = Force * distance; distance = spd*time
        self.work = self.work + (self.perf.Thr*simdt*resultantspd)
        
    def id2idx(self, acid):
        """Find index of aircraft id"""
        try:
            return self.id.index(acid.upper())
        except:
            return -1

    def setNoise(self, noise=None):
        """Noise (turbulence, ADBS-transmission noise, ADSB-truncated effect)"""
        if noise is None:
            return True, "Noise is currently " + ("on" if self.Turbulence.active else "off")

        self.Turbulence.SetNoise(noise)
        self.adsb.SetNoise(noise)
        return True

    def engchange(self, acid, engid):
        """Change of engines"""
        self.perf.engchange(acid, engid)
        return

    def move(self, idx, lat, lon, alt=None, hdg=None, casmach=None, vspd=None):
        self.lat[idx]      = lat
        self.lon[idx]      = lon

        if alt:
            self.alt[idx]   = alt
            self.apalt[idx] = alt

        if hdg:
            self.hdg[idx]  = hdg
            self.ap.trk[idx] = hdg

        if casmach:
            self.tas[idx], self.aspd[-1], dummy = casormach(casmach, alt)

        if vspd:
            self.vs[idx]       = vspd
            self.swvnav[idx] = False

    def nom(self, idx):
        """ Reset acceleration back to nominal (1 kt/s^2): NOM acid """
        self.ax[idx] = kts

    def poscommand(self, scr, idxorwp):# Show info on aircraft(int) or waypoint or airport (str)
        """POS command: Show info or an aircraft, airport, waypoint or navaid"""
        # Aircraft index
        if type(idxorwp)==int and idxorwp >= 0:

            idx           = idxorwp
            acid          = self.id[idx]
            actype        = self.type[idx]
            latlon        = latlon2txt(self.lat[idx], self.lon[idx])
            alt           = round(self.alt[idx] / ft)
            hdg           = round(self.hdg[idx])
            trk           = round(self.trk[idx])
            cas           = round(self.cas[idx] / kts)
            tas           = round(self.tas[idx] / kts)
            gs            = round(self.gs[idx]/kts)
            M             = self.M[idx]
            VS            = round(self.vs[idx]/ft*60.)              
            route         = self.ap.route[idx]
            
            # Position report
            
            lines = "Info on %s %s index = %d\n" %(acid, actype, idx)     \
                  + "Pos: "+latlon+ "\n"                                  \
                  + "Hdg: %03d   Trk: %03d\n"        %(hdg, trk)              \
                  + "Alt: %d ft  V/S: %d fpm\n"  %(alt,VS)                \
                  + "CAS/TAS/GS: %d/%d/%d kts   M: %.3f\n"%(cas,tas,gs,M)

            # FMS AP modes
            if self.swlnav[idx] and route.nwp > 0 and route.iactwp >= 0:

                if self.swvnav[idx]:
                    lines = lines + "VNAV, "

                lines += "LNAV to " + route.wpname[route.iactwp] + "\n"

            # Flight info: Destination and origin
            if self.ap.orig[idx] != "" or self.ap.dest[idx] != "":
                lines = lines +  "Flying"

                if self.ap.orig[idx] != "":
                    lines = lines +  " from " + self.ap.orig[idx]

                if self.ap.dest[idx] != "":
                    lines = lines +  " to " + self.ap.dest[idx]

            # Show a/c info and highlight route of aircraft in radar window
            # and pan to a/c (to show route)
            return scr.showacinfo(acid,lines)        

        # Waypoint: airport, navaid or fix
        else:
            wp = idxorwp.upper()

            # Reference position for finding nearest            
            reflat = scr.ctrlat
            reflon = scr.ctrlon            
            
            lines = "Info on "+wp+":\n"
                       
            # First try airports (most used and shorter, hence faster list)
            iap = self.navdb.getaptidx(wp)
            if iap>=0:                
                aptypes = ["large","medium","small"]
                lines = lines + self.navdb.aptname[iap]+"\n"                 \
                        + "is a "+ aptypes[max(-1,self.navdb.aptype[iap]-1)] \
                        +" airport at:\n"                                    \
                        + latlon2txt(self.navdb.aptlat[iap],                 \
                                     self.navdb.aptlon[iap]) + "\n"          \
                        + "Elevation: "                                      \
                        + str(int(round(self.navdb.aptelev[iap]/ft)))        \
                        + " ft \n"

               # Show country name
                try:
                     ico = self.navdb.cocode2.index(self.navdb.aptco[iap].upper())
                     lines = lines + "in "+self.navdb.coname[ico]+" ("+      \
                             self.navdb.aptco[iap]+")"
                except:
                     ico = -1
                     lines = lines + "Country code: "+self.navdb.aptco[iap]
                try:
                    rwytxt = str(self.navdb.rwythresholds[self.navdb.aptid[iap]].keys())
                    lines = lines + "\nRunways: " +rwytxt.strip("[]").replace("'","")
                except:
                    pass

            # Not found as airport, try waypoints & navaids
            else:
                iwps = self.navdb.getwpindices(wp,reflat,reflon)
                if iwps[0]>=0:
                    typetxt = ""
                    desctxt = ""
                    lastdesc = "XXXXXXXX"
                    for i in iwps:
                        
                        # One line type text                        
                        if typetxt == "":
                            typetxt = typetxt+self.navdb.wptype[i]
                        else:
                            typetxt = typetxt+" and "+self.navdb.wptype[i]

                        # Description: multi-line
                        samedesc = self.navdb.wpdesc[i]==lastdesc
                        if desctxt == "":
                            desctxt = desctxt +self.navdb.wpdesc[i]
                            lastdesc = self.navdb.wpdesc[i]
                        elif not samedesc:
                            desctxt = desctxt +"\n"+self.navdb.wpdesc[i]
                            lastdesc = self.navdb.wpdesc[i]
                            
                        # Navaid: frequency
                        if self.navdb.wptype[i] in ["VOR","DME","TACAN"] and not samedesc:
                            desctxt = desctxt + " "+ str(self.navdb.wpfreq[i])+" MHz"
                        elif self.navdb.wptype[i]=="NDB" and not samedesc:
                            desctxt = desctxt+ " " + str(self.navdb.wpfreq[i])+" kHz"  

                    iwp = iwps[0]

                    # Basic info
                    lines = lines + wp +" is a "+ typetxt       \
                           + " at\n"\
                           + latlon2txt(self.navdb.wplat[iwp],  \
                                        self.navdb.wplon[iwp])
                    # Navaids have description                    
                    if len(desctxt)>0:
                        lines = lines+ "\n" + desctxt           

                    # VOR give variation
                    if self.navdb.wptype[iwp]=="VOR":
                        lines = lines + "\nVariation: "+ \
                                     str(self.navdb.wpvar[iwp])+" deg"

  
                    # How many others?
                    nother = self.navdb.wpid.count(wp)-len(iwps)
                    if nother>0:
                        verb = ["is ","are "][min(1,max(0,nother-1))]
                        lines = lines +"\nThere "+verb + str(nother) +\
                                   " other waypoint(s) also named " + wp
                    
                    # In which airways?
                    connect = self.navdb.listconnections(wp, \
                                                self.navdb.wplat[iwp],
                                                self.navdb.wplon[iwp])
                    if len(connect)>0:                    
                        awset = set([])                   
                        for c in connect:
                            awset.add(c[0])
        
                        lines = lines+"\nAirways: "+"-".join(awset)

               
               # Try airway id
                else:  # airway
                    awid = wp
                    airway = self.navdb.listairway(awid)
                    if len(airway)>0:
                        lines = ""  
                        for segment in airway:
                            lines = lines+"Airway "+ awid + ": " + \
                                    " - ".join(segment)+"\n"
                        lines = lines[:-1] # cut off final newline
                    else:
                        return False,idxorwp+" not found as a/c, airport, navaid or waypoint"

            # Show what we found on airport and navaid/waypoint
            scr.echo(lines)
            
        return True
        
    def airwaycmd(self,scr,key=""):
        # Show conections of a waypoint
 
        reflat = scr.ctrlat
        reflon = scr.ctrlon

        if key=="":
            return False,'AIRWAY needs waypoint or airway'
        
        if self.navdb.awid.count(key)>0:
            return self.poscommand(scr, key.upper())
        else:    
            # Find connecting airway legs
            wpid = key.upper()
            iwp = self.navdb.getwpidx(wpid,reflat,reflon)
            if iwp<0:
                return False,key," not found."
                
            wplat = self.navdb.wplat[iwp]
            wplon = self.navdb.wplon[iwp]
            connect = self.navdb.listconnections(key.upper(),wplat,wplon)
            if len(connect)>0:
                lines = ""
                for c in connect:
                    if len(c)>=2:
                        # Add airway, direction, waypoint
                        lines = lines+ c[0]+": to "+c[1]+"\n"
                scr.echo(lines[:-1])  # exclude final newline
            else:
                return False,"No airway legs found for ",key
    
    def logFLST(self, simt, delAircraftidx):
        # Updates the arrays that are used for FLST logging
        # FLST statistics logged when aircraft are deleted
        # delAircraftidx = index of aircraft to be deleted
    
        if len(delAircraftidx)>0:
            
            # Reset variables
            self.flogid = []
            self.flogspawntime = []
            self.flogflightime = []
            self.flogdistance2D = []
            self.flogdistance3D = []
            self.flogwork = []
            self.floglat = []
            self.floglon = []
            self.flogalt = []
            self.flogtas = []
            self.flogvs = []
            self.floghdg = []
            self.flogoriglat = []
            self.flogoriglon = []
            self.flogdestlat = []
            self.flogdestlon = []
            self.flogasasactive = []
            self.flogpilotalt = []
            self.flogpilottas = []
            self.flogpilotvs = []
            self.flogpilothdg = []
            
            # Update FLST arrays
            self.flogid = np.array(self.id)[delAircraftidx]
            self.flogspawntime = self.spawnTime[delAircraftidx]
            self.flogflightime = simt - self.spawnTime[delAircraftidx]
            self.flogdistance2D = self.distance2D[delAircraftidx]
            self.flogdistance3D = self.distance3D[delAircraftidx]
            self.flogwork = self.work[delAircraftidx]
            self.floglat = self.lat[delAircraftidx]
            self.floglon = self.lon[delAircraftidx]
            self.flogalt = self.alt[delAircraftidx]
            self.flogtas = self.tas[delAircraftidx]
            self.flogvs  = self.vs[delAircraftidx]
            self.floghdg = self.hdg[delAircraftidx]
            self.flogoriglat = self.ap.origlat[delAircraftidx]
            self.flogoriglon = self.ap.origlon[delAircraftidx]
            self.flogdestlat = self.ap.destlat[delAircraftidx]
            self.flogdestlon = self.ap.destlon[delAircraftidx]
            self.flogasasactive = self.asas.active[delAircraftidx]
            self.flogpilotalt = self.pilot.alt[delAircraftidx]
            self.flogpilottas = self.pilot.spd[delAircraftidx]
            self.flogpilotvs = self.pilot.vs[delAircraftidx]
            self.flogpilothdg = self.pilot.hdg[delAircraftidx]
            
            # Call the logger
            self.flstlog.log()
            
    def UpdateTrafCountSkyLog(self):
        # Update intantaneous traffic counts and average flight path angles for Sky Log
        # note ntraf is already updated in traf.create() and traf.delete()
        
        # Number of intantaneous cruising aircraft
        self.ntrafCruising = len(self.vs[np.abs(self.vs) <= self.cruiseLimVS])
        
        # Number of instantaneous climbing and descending aircraft
        self.ntrafVS = self.ntraf - self.ntrafCruising
        
         # Average of absolute flight path angle for all aircraft [deg]
        self.gammaAll = np.average(np.abs(self.gamma)) if self.ntraf > 0 else 0
        
        # Average of absolute flight path angle for climbing/descending aircraft [deg]
        self.gammaVS = np.average(np.abs(self.gamma[np.abs(self.vs) > self.cruiseLimVS])) if self.ntrafVS > 0 else 0
        
    def UpdateTrafCountSModelLog(self):
        # Update instantaneous traffic counts and average flight path angles for 
        # aircraft inside the predefined square analysis area
        
        if 'SQUAREMODELAREA' in areafilter.areas:
            inside = areafilter.checkInside('SQUAREMODELAREA', self.lat, self.lon, self.alt)
            
            # Total number of instantaneous aircraft inside area
            self.smodntraf = sum(inside)
            
            # Number of intantaneous cruising aircraft inside area
            vsinside = self.vs[inside==True] 
            self.smodntrafCruising = len(vsinside[np.abs(vsinside) <= self.cruiseLimVS])
            
            # Number of instantaneous climbing and descending aircraft inside area
            self.smodntrafVS = self.smodntraf - self.smodntrafCruising
            
            # Average of absolute flight path angle for all aircraft inside area [deg]
            gammainside = self.gamma[inside==True]
            self.smodgammaAll = np.average(np.abs(gammainside)) if self.smodntraf > 0 else 0       
            
            # Average of absolute flight path angle for climbing/descending aircraft inside area [deg]
            self.smodgammaVS = np.average(np.abs(gammainside[np.abs(vsinside) > self.cruiseLimVS])) if self.smodntrafVS > 0 else 0
            
    def UpdateTrafCountCModelLog(self):
        # Update instantaneous traffic counts and average flight path angles for 
        # aircraft inside the predefined circular analysis area
        
        if 'CIRCLEMODELAREA' in areafilter.areas:
            inside = areafilter.checkInside('CIRCLEMODELAREA', self.lat, self.lon, self.alt)
            
            # Total number of instantaneous aircraft inside area
            self.cmodntraf = sum(inside)
            
            # Number of intantaneous cruising aircraft inside area
            vsinside = self.vs[inside==True] 
            self.cmodntrafCruising = len(vsinside[np.abs(vsinside) <= self.cruiseLimVS])
            
            # Number of instantaneous climbing and descending aircraft inside area
            self.cmodntrafVS = self.cmodntraf - self.cmodntrafCruising
            
            # Average of absolute flight path angle for all aircraft inside area [deg]
            gammainside = self.gamma[inside==True]
            self.cmodgammaAll = np.average(np.abs(gammainside)) if self.cmodntraf > 0 else 0         
            
            # Average of absolute flight path angle for climbing/descending aircraft inside area [deg]
            self.cmodgammaVS = np.average(np.abs(gammainside[np.abs(vsinside) > self.cruiseLimVS])) if self.cmodntrafVS > 0 else 0
        