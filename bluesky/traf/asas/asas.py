import numpy as np
from ... import settings
from ...tools.aero import ft, nm, fpm, kts, vcas2tas, vtas2cas
from ...tools.dynamicarrays import DynamicArrays, RegisterElementParameters
from ...tools import areafilter, geo, datalog, logHeader
from asasLogUpdate import asasLogUpdate


# Import default CD methods
try:
    import casas as StateBasedCD
except ImportError:
    StateBasedCD = False

if not settings.prefer_compiled or not StateBasedCD:
    import StateBasedCD

# Import default CR methods
import DoNothing
import Eby
import MVP
import Swarm
import MVP2


class ASAS(DynamicArrays):
    """ Central class for ASAS conflict detection and resolution.
        Maintains a confict database, and links to external CD and CR methods."""

    # Dictionary of CD methods
    CDmethods = {"STATEBASED": StateBasedCD}

    # Dictionary of CR methods
    CRmethods = {"OFF": DoNothing, "MVP": MVP, "EBY": Eby, "SWARM": Swarm, "MVP2": MVP2}

    @classmethod
    def addCDMethod(asas, name, module):
        asas.CDmethods[name] = module

    @classmethod
    def addCRMethod(asas, name, module):
        asas.CRmethods[name] = module

    def __init__(self, traf):

        self.traf = traf
        self.simt = 0.0

        with RegisterElementParameters(self):
            # ASAS info per aircraft:
            self.iconf    = []            # index in 'conflicting' aircraft database

            self.trk      = np.array([])  # heading provided by the ASAS [deg]
            self.spd      = np.array([])  # speed provided by the ASAS (tas) [m/s]
            self.alt      = np.array([])  # speed alt by the ASAS [m]
            self.vs       = np.array([])  # speed vspeed by the ASAS [m/s]

            # Register the following parameters for SNAP logging
            with datalog.registerLogParameters('SNAPLOG', self):
                self.active   = np.array([], dtype=bool)  # whether the autopilot follows ASAS or not

        # Create event based ASAS loggers
        self.cfllog = datalog.defineLogger("CFLLOG", logHeader.cflHeader())
        self.intlog = datalog.defineLogger("INTLOG", logHeader.intHeader())
        self.trlog  = datalog.defineLogger("TRLOG", logHeader.trHeader())

        # Create periodic ASAS loggers
        datalog.definePeriodicLogger('INSTLOG', logHeader.instHeader(), settings.instdt)

        # Register the following parameters for SKY logging
        with datalog.registerLogParameters('SKYLOG', self):
            self.ncfl = 0
            self.ncflCruising = 0
            self.ncflCruisingVS = 0
            self.ncflVS = 0

#        # Register the following parameters for SModel logging
#        with datalog.registerLogParameters('SMODELLOG', self):
#            self.smodncfl = 0
#            self.smodncflCruising = 0
#            self.smodncflCruisingVS = 0
#            self.smodncflVS = 0
#
#        # Register the following parameters for CModel logging
#        with datalog.registerLogParameters('CMODELLOG', self):
#            self.cmodncfl = 0
#            self.cmodncflCruising = 0
#            self.cmodncflCruisingVS = 0
#            self.cmodncflVS = 0

        # Register the following parameters for CFL logging
        with datalog.registerLogParameters('CFLLOG', self):
            self.clogid1 = []
            self.clogspawntimeid1 = []
            self.clogtinconfid1 = []
            self.clogtoutconfid1 = []
            self.clogtcpaid1 = []
            self.cloglatid1 = []
            self.cloglonid1 = []
            self.clogaltid1 = []
            self.clogtasid1 = []
            self.clogvsid1 = []
            self.cloghdgid1 = []
            self.cloglatcpaid1 = []
            self.clogloncpaid1 = []
            self.clogaltcpaid1 = []
            self.clogasasactiveid1 = []
            self.clogasasaltid1 = []
            self.clogasastasid1 = []
            self.clogasasvsid1 = []
            self.clogasashdgid1 = []
            self.clogid2 = []
            self.clogspawntimeid2 = []
            self.clogtinconfid2 = []
            self.clogtoutconfid2 = []
            self.clogtcpaid2 = []
            self.cloglatid2 = []
            self.cloglonid2 = []
            self.clogaltid2 = []
            self.clogtasid2 = []
            self.clogvsid2 = []
            self.cloghdgid2 = []
            self.cloglatcpaid2 = []
            self.clogloncpaid2 = []
            self.clogaltcpaid2 = []
            self.clogasasactiveid2 = []
            self.clogasasaltid2 = []
            self.clogasastasid2 = []
            self.clogasasvsid2 = []
            self.clogasashdgid2 = []

        # Register the following parameters for INT logging
        with datalog.registerLogParameters('INTLOG', self):
            self.ilogid1 = []
            self.ilogspawntimeid1 = []
            self.ilogtinconfid1 = []
            self.ilogtoutconfid1 = []
            self.ilogtcpaid1 = []
            self.iloglatid1 = []
            self.iloglonid1 = []
            self.ilogaltid1 = []
            self.ilogtasid1 = []
            self.ilogvsid1 = []
            self.iloghdgid1 = []
            self.ilogasasactiveid1 = []
            self.ilogasasaltid1 = []
            self.ilogasastasid1 = []
            self.ilogasasvsid1 = []
            self.ilogasashdgid1 = []
            self.ilogid2 = []
            self.ilogspawntimeid2 = []
            self.ilogtinconfid2 = []
            self.ilogtoutconfid2 = []
            self.ilogtcpaid2 = []
            self.iloglatid2 = []
            self.iloglonid2 = []
            self.ilogaltid2 = []
            self.ilogtasid2 = []
            self.ilogvsid2 = []
            self.iloghdgid2 = []
            self.ilogasasactiveid2 = []
            self.ilogasasaltid2 = []
            self.ilogasastasid2 = []
            self.ilogasasvsid2 = []
            self.ilogasashdgid2 = []
            self.ilogintsev    = []
            self.iloginthsev   = []
            self.ilogintvsev   = []


        # Register the following parameters for CFL logging
        with datalog.registerLogParameters('INSTLOG', self):
            self.instlogid1 = []
            self.instlogspawntimeid1 = []
            self.instlogtinconfid1 = []
            self.instlogtoutconfid1 = []
            self.instlogtcpaid1 = []
            self.instloglatid1 = []
            self.instloglonid1 = []
            self.instlogaltid1 = []
            self.instlogtasid1 = []
            self.instlogvsid1 = []
            self.instloghdgid1 = []
            self.instloglatcpaid1 = []
            self.instlogloncpaid1 = []
            self.instlogaltcpaid1 = []
            self.instlogasasactiveid1 = []
            self.instlogasasaltid1 = []
            self.instlogasastasid1 = []
            self.instlogasasvsid1 = []
            self.instlogasashdgid1 = []
            self.instlogid2 = []
            self.instlogspawntimeid2 = []
            self.instlogtinconfid2 = []
            self.instlogtoutconfid2 = []
            self.instlogtcpaid2 = []
            self.instloglatid2 = []
            self.instloglonid2 = []
            self.instlogaltid2 = []
            self.instlogtasid2 = []
            self.instlogvsid2 = []
            self.instloghdgid2 = []
            self.instloglatcpaid2 = []
            self.instlogloncpaid2 = []
            self.instlogaltcpaid2 = []
            self.instlogasasactiveid2 = []
            self.instlogasasaltid2 = []
            self.instlogasastasid2 = []
            self.instlogasasvsid2 = []
            self.instlogasashdgid2 = []
            
        # Register the following parameters for TR logging
        with datalog.registerLogParameters('TRLOG', self):
            self.trlogid = []
            self.trlogiscruising = []
            self.trlogprealt = []
            self.trlogpreapalt = []
            self.trlogprehdg = []
            self.trlogpreaphdg = []
            self.trlogprelaylowerhdg = []
            self.trlogprelayupperhdg = []
            self.trlogrecoverylowerhdg = []
            self.trlogrecoveryupperhdg = []
            self.trloginrecoveryrange = []
            self.trlogpostalt = []
            self.trlogposthdg = []
            self.trlogpostlaylowerhdg = []
            self.trlogpostlayupperhdg = []
            
        # All ASAS variables are initialized in the reset function
        self.reset()

    def reset(self):
        super(ASAS, self).reset()

        """ ASAS constructor """
        self.cd_name      = "STATEBASED"
        self.cr_name      = "OFF"
        self.cd           = ASAS.CDmethods[self.cd_name]
        self.cr           = ASAS.CRmethods[self.cr_name]

        self.dtasas       = settings.asas_dt           # interval for ASAS
        self.dtlookahead  = settings.asas_dtlookahead  # [s] lookahead time
        self.mar          = settings.asas_mar          # [-] Safety margin for evasion
        self.R            = settings.asas_pzr * nm     # [m] Horizontal separation minimum for detection
        self.dh           = settings.asas_pzh * ft     # [m] Vertical separation minimum for detection
        self.Rm           = self.R * self.mar          # [m] Horizontal separation minimum for resolution
        self.dhm          = self.dh * self.mar         # [m] Vertical separation minimum for resolution
        self.swasas       = True                       # [-] whether to perform CD&R
        self.tasas        = 0.0                        # Next time ASAS should be called

        self.vmin         = 100.0*kts                  # [m/s] Minimum ASAS velocity (100 kts)
        self.vmax         = 600.0*kts                  # [m/s] Maximum ASAS velocity (600 kts)
        self.vsmin        = -4000.0*fpm                # [m/s] Minimum ASAS vertical speed
        self.vsmax        = 4000.0*fpm                 # [m/s] Maximum ASAS vertical speed

        self.swresohoriz  = False                      # [-] switch to limit resolution to the horizontal direction
        self.swresospd    = False                      # [-] switch to use only speed resolutions (works with swresohoriz = True)
        self.swresohdg    = False                      # [-] switch to use only heading resolutions (works with swresohoriz = True)
        self.swresovert   = False                      # [-] switch to limit resolution to the vertical direction
        self.swresocoop   = False                      # [-] switch to limit resolution magnitude to half (cooperative resolutions)

        self.swprio       = False                      # [-] switch to activate priority rules for conflict resolution
        self.priocode     = "FF1"                      # [-] Code of the priority rule that is to be used (FF1, FF2, FF3, LAY1, LAY2)

        self.swnoreso     = False                      # [-] switch to activate the NORESO command. Nobody will avoid conflicts with  NORESO aircraft
        self.noresolst    = []                         # [-] list for NORESO command. Nobody will avoid conflicts with aircraft in this list

        self.swresooff    = False                      # [-] switch to active the RESOOFF command. RESOOFF aircraft will NOT avoid other aircraft. Opposite of NORESO command.
        self.resoofflst   = []                         # [-] list for the RESOOFF command. These aircraft will not do conflict resolutions.

        self.resoFacH     = 1.0                        # [-] set horizontal resolution factor (1.0 = 100%)
        self.resoFacV     = 1.0                        # [-] set horizontal resolution factor (1.0 = 100%)

        self.swconfareafilt  = False                   # [-] swtich to activate the CONFAREAFILT command. This conflict filter is area based.
        self.areafiltercode  = None                    # [-] Code for the conflict area filter that should be used (OPTION1, OPTION2, OPTION3, OPTION4, OPTION5)
        self.areafiltershape = None                    # [-] Name of shape where area conflict filter is active

        self.swspawncheck     = False                  # [-] switch to activate the RESOSPAWNCHECK command. This command prevents aircraft spawned in very short term conflicts and in intrusions from perfroming conflict resolutions.
        self.spawncheckfactor = 1.0                    # [-] factor that is multiplied with the look-ahead-time to determine what constitutes a 'very short term conflcit'

        self.swconfdef = False                         # [-] switch to activate the CONFDEF command. This command activates the alterante conflict definition (intrusion is not a conflict)

        self.swafterconfalt = False                    # [-] if True, altitude not recovered after conflict resolution for cruising aircraft with waypoints

        self.nconf        = 0                          # Number of detected conflicts
        self.latowncpa    = np.array([])
        self.lonowncpa    = np.array([])
        self.altowncpa    = np.array([])

        self.confpairs               = []  # Start with emtpy database: no conflicts
        self.conflist_active         = []  # List of all Conflicts that are still active (not past CPA). Conflict deleted from this list once past CPA
        self.LOSlist_active          = []  # List of all Losses Of Separation that are still active (LOS still on-going). LOS deleted from this list when it is over.
        self.conflist_now            = []  # List of Conflicts detected in the current ASAS cycle. Used to resolve conflicts.
        self.LOSlist_now             = []  # List of Losses Of Separations in the current ASAS cycle.
        self.LOSlist_logged          = []  # List of all LOS that have been logged. LOS logged only at max severity. Needed to ensure that a LOS is logged only once.
        self.conflist_resospawncheck = []  # List of conflicts that have met the Reso Spawn Check command conditions. These conflicts will not be solved even if CR is on.

        self.nconf_total             = 0   # Number of all conflicts since the simulation has started. Used for display on the GUI.
        self.nLOS_total              = 0   # Number of all LOS since the simulation has started. Used for display on the GUI.
        
        self.conceptcode    = "UA"                     # Concept code. Anything can be typed here. Corresponding logic will only for UA and layered airspaces. UA = Unstructured airspace. L45 =  layers 45.   
        self.isLayers       = False                    # Is the requested concept a layered concept?
        self.minCruiseAlt   = 4000.0                   # Minimum cruising altitude [ft]
        self.layerHeight    = self.dhm + 50.0          # Vertical spacing between layers [ft] 
        self.numLayers      = 8.0                      # Number of layers / flight levels for cruising aircraft
        self.minDist        = 200.0                    # Minimum flight distance of aircraft in sector of interest [NM]
        self.maxDist        = 250.0                    # Maximum flight distance of aircraft in sector of interest [NM]
        self.recoveryMargin = False                    # Should minor heading differences be excused for layers concept?
        self.alpha          = 360.0                    # heading range allowed per layer. Only makes sense for layered airspaces [deg] 
        self.numLayerSets   = 8.0                      # Number of layer sets. Default value is 8 (this assumes alpha=360.0, numLayers=8.0) [-]
        self.numFLin1Set    = 1.0                      # Number of flight levels/layers in 1 layer set. Default value is 1.0 (this assumes alpha=360.0) [-]
        self.maxCruiseAlt   = 11700.0                  # Maximum cruising altitude [ft]
        
        self.swfinder      = False  # switch to activate the CFL finder.         
        self.cflFinderCase = None   # case name to detect and activate debugger when encountering conflicts between aircraft in desired flight phases (CL-CL, CL-CR, CR-CR, CR-DE, DE-DE)

        # For keeping track of locations with most severe intrusions
        self.LOSmaxsev    = []
        self.LOShmaxsev   = []
        self.LOSvmaxsev   = []

        # Reset Sky log asas parameters
        self.ncfl = 0
        self.ncflCruising = 0
        self.ncflCruisingVS = 0
        self.ncflVS = 0

    def toggle(self, flag=None):
        if flag is None:
            return True, "ASAS is currently " + ("ON" if self.swasas else "OFF")
        self.swasas = flag
        return True

    def SetCDmethod(self, method=""):
        if method is "":
            return True, ("Current CD method: " + self.cd_name +
                        "\nAvailable CD methods: " + str.join(", ", ASAS.CDmethods.keys()))
        if method not in ASAS.CDmethods:
            return False, (method + " doesn't exist.\nAvailable CD methods: " + str.join(", ", ASAS.CDmethods.keys()))

        self.cd_name = method
        self.cd = ASAS.CDmethods[method]

    def SetCRmethod(self, method=""):
        if method is "":
            return True, ("Current CR method: " + self.cr_name +
                        "\nAvailable CR methods: " + str.join(", ", ASAS.CRmethods.keys()))
        if method not in ASAS.CRmethods:
            return False, (method + " doesn't exist.\nAvailable CR methods: " + str.join(", ", ASAS.CRmethods.keys()))

        self.cr_name = method
        self.cr = ASAS.CRmethods[method]
        self.cr.start(self)

    def SetPZR(self, value=None):
        if value is None:
            return True, ("ZONER [radius (nm)]\nCurrent PZ radius: %.2f NM" % (self.R / nm))

        self.R  = value * nm
        self.Rm = np.maximum(self.mar * self.R, self.Rm)

    def SetPZH(self, value=None):
        if value is None:
            return True, ("ZONEDH [height (ft)]\nCurrent PZ height: %.2f ft" % (self.dh / ft))

        self.dh  = value * ft
        self.dhm = np.maximum(self.mar * self.dh, self.dhm)

    def SetPZRm(self, value=None):
        if value is None:
            return True, ("RSZONER [radius (nm)]\nCurrent PZ radius margin: %.2f NM" % (self.Rm / nm))

        if value < self.R / nm:
            return False, "PZ radius margin may not be smaller than PZ radius"

        self.Rm  = value * nm

    def SetPZHm(self, value=None):
        if value is None:
            return True, ("RSZONEDH [height (ft)]\nCurrent PZ height margin: %.2f ft" % (self.dhm / ft))

        if value < self.dh / ft:
            return False, "PZ height margin may not be smaller than PZ height"

        self.dhm  = value * ft

    def SetDtLook(self, value=None):
        if value is None:
            return True, ("DTLOOK [time]\nCurrent value: %.1f sec" % self.dtlookahead)

        self.dtlookahead = value

    def SetDtNoLook(self, value=None):
        if value is None:
            return True, ("DTNOLOOK [time]\nCurrent value: %.1f sec" % self.dtasas)

        self.dtasas = value

    def SetResoHoriz(self, value=None):
        """ Processes the RMETHH command. Sets swresovert = False"""
        # Acceptable arguments for this command
        options = ["BOTH", "SPD", "HDG", "NONE", "ON", "OFF", "OF"]
        if value is None:
            return True, "RMETHH [ON / BOTH / OFF / NONE / SPD / HDG]" + \
                         "\nHorizontal resolution limitation is currently " + ("ON" if self.swresohoriz else "OFF") + \
                         "\nSpeed resolution limitation is currently " + ("ON" if self.swresospd else "OFF") + \
                         "\nHeading resolution limitation is currently " + ("ON" if self.swresohdg else "OFF")
        if str(value) not in options:
            return False, "RMETH Not Understood" + "\nRMETHH [ON / BOTH / OFF / NONE / SPD / HDG]"
        else:
            if value == "ON" or value == "BOTH":
                self.swresohoriz = True
                self.swresospd   = True
                self.swresohdg   = True
                self.swresovert  = False
            elif value == "OFF" or value == "OF" or value == "NONE":
                # Do NOT swtich off self.swresovert if value == OFF
                self.swresohoriz = False
                self.swresospd   = False
                self.swresohdg   = False
            elif value == "SPD":
                self.swresohoriz = True
                self.swresospd   = True
                self.swresohdg   = False
                self.swresovert  = False
            elif value == "HDG":
                self.swresohoriz = True
                self.swresospd   = False
                self.swresohdg   = True
                self.swresovert  = False

    def SetResoVert(self, value=None):
        """ Processes the RMETHV command. Sets swresohoriz = False."""
        # Acceptable arguments for this command
        options = ["NONE", "ON", "OFF", "OF", "V/S"]
        if value is None:
            return True, "RMETHV [ON / V/S / OFF / NONE]" + \
                         "\nVertical resolution limitation is currently " + ("ON" if self.swresovert else "OFF")
        if str(value) not in options:
            return False, "RMETV Not Understood" + "\nRMETHV [ON / V/S / OFF / NONE]"
        else:
            if value == "ON" or value == "V/S":
                self.swresovert  = True
                self.swresohoriz = False
                self.swresospd   = False
                self.swresohdg   = False
            elif value == "OFF" or value == "OF" or value == "NONE":
                # Do NOT swtich off self.swresohoriz if value == OFF
                self.swresovert  = False

    def SetResoFacH(self, value=None):
        ''' Set the horizontal resolution factor'''
        if value is None:
            return True, ("RFACH [FACTOR]\nCurrent horizontal resolution factor is: %.1f" % self.resoFacH)

        self.resoFacH = np.abs(value)
        self.R  = self.R * self.resoFacH
        self.Rm = self.R * self.mar

        return True, "IMPORTANT NOTE: " + \
                     "\nCurrent horizontal resolution factor is: " + str(self.resoFacH) + \
                     "\nCurrent PZ radius:" + str(self.R / nm) + " NM" + \
                     "\nCurrent resolution PZ radius: " + str(self.Rm / nm) + " NM\n"

    def SetResoFacV(self, value=None):
        ''' Set the vertical resolution factor'''
        if value is None:
            return True, ("RFACV [FACTOR]\nCurrent vertical resolution factor is: %.1f" % self.resoFacV)

        self.resoFacV = np.abs(value)
        self.dh  = self.dh * self.resoFacV
        self.dhm = self.dh * self.mar

        return True, "IMPORTANT NOTE: " + \
                     "\nCurrent vertical resolution factor is: " + str(self.resoFacV) + \
                     "\nCurrent PZ height:" + str(self.dh / ft) + " ft" + \
                     "\nCurrent resolution PZ height: " + str(self.dhm / ft) + " ft\n"

    def SetPrio(self, flag=None, priocode="FF1"):
        '''Set the prio switch and the type of prio '''
        options = ["FF1", "FF2", "FF3", "LAY1", "LAY2", "PROJECT3", "1000FT", "CRUISE", "CLIMB"]
        if flag is None:
            return True, "PRIORULES [ON/OFF] [PRIOCODE]"  + \
                         "\nAvailable priority codes: " + \
                         "\n     FF1:       Free Flight Primary (No Prio) " + \
                         "\n     FF2:       Free Flight Secondary (Cruising has priority)" + \
                         "\n     FF3:       Free Flight Tertiary (Climbing/descending has priority)" + \
                         "\n     LAY1:      Layers Primary (Cruising has priority + horizontal resolutions)" + \
                         "\n     LAY2:      Layers Secondary (Climbing/descending has priority + horizontal resolutions)" + \
                         "\n     PROJECT3:  For conflicts with C/D aircraft, where at least 1 C/D aircraft is below 4000ft" + \
                         "\n                both aircraft solve horizontally, even if only vertical resolutions are allowed" + \
                         "\n     1000FT:    Dont resolve if both aircraft are below 1000FT" + \
                         "\n     CRUISE:    Same as LAY1" + \
                         "\n     CLIMB:     Same as LAY2" + \
                         "\nPriority is currently " + ("ON" if self.swprio else "OFF") + \
                         "\nPriority code is currently: " + str(self.priocode)
        if priocode not in options:
            return False, "Priority code Not Understood. Available Options: " + str(options)
        else:
            self.priocode = priocode
        self.swprio = flag
        return True, "Priority is " + ("ON" if self.swprio else "OFF") + \
                     "\nPriority code is : " + str(self.priocode)
                     
    def SetConflictFinder(self, flag=None, case=None):
        '''Set the conflict finder swtich and the case'''
        options = ["CL-CL", "CL-CR", "CR-CR", "CR-DE", "DE-DE", None]
        if flag is None:
            return True, "CFLFINDER [CASE]"  + \
                         "\nAvailable CASES: " + \
                         "\n     CL-CL:  Climb   - Climb   conflict " + \
                         "\n     CL-CR:  Climb   - Cruise  conflict" + \
                         "\n     CR-CR:  Cruise  - Cruise  conflict" + \
                         "\n     CR-DE:  Cruise  - Descend conflict" + \
                         "\n     DE-DE:  Descend - Descend conflict" + \
                         "\nCFLFINDER is currently " + ("ON" if self.swfinder else "OFF") + \
                         "\nCFLFINDER case is currently: " + str(self.cflFinderCase) + \
                         "\nNOTE: CFLFINDER ONLY WORKS WITH MVP ACTIVATED!!!! "
        if case not in options:
            return False, "CFLFINDER CASE Not Understood. Available Options: " + str(options)
        else:
            self.cflFinderCase = case
        self.swfinder = flag
        if self.cr_name != "MVP":
            self.cflFinderCase = None
            self.swfinder = False
            return False, "CFLFINDER REQUIRES MVP TO BE ACTIVATED FIRST!!!" + \
                          "\nACTIVATE MVP BY TYPING IN 'RESO MVP'"
        return True, "CFLFINDER is " + ("ON" if self.swfinder else "OFF") + \
                     "\nCFLFINDER case is : " + str(self.cflFinderCase)

    def SetNoreso(self, noresoac=''):
        '''ADD or Remove aircraft that nobody will avoid.
        Multiple aircraft can be sent to this function at once '''
        if noresoac is '':
            return True, "NORESO [ACID]" + \
                         "\nCurrent list of aircraft nobody will avoid:" + \
                         str(self.noresolst)
        # Split the input into separate aircraft ids if multiple acids are given
        acids = noresoac.split(',') if len(noresoac.split(',')) > 1 else noresoac.split(' ')

        # Remove acids if they are already in self.noresolst. This is used to
        # delete aircraft from this list.
        # Else, add them to self.noresolst. Nobody will avoid these aircraft
        if set(acids) <= set(self.noresolst):
            self.noresolst = filter(lambda x: x not in set(acids), self.noresolst)
        else:
            self.noresolst.extend(acids)

        # active the switch, if there are acids in the list
        self.swnoreso = len(self.noresolst) > 0

    def SetResooff(self, resooffac=''):
        "ADD or Remove aircraft that will not avoid anybody else"
        if resooffac is '':
            return True, "NORESO [ACID]" + \
                         "\nCurrent list of aircraft will not avoid anybody:" + \
                         str(self.resoofflst)
        # Split the input into separate aircraft ids if multiple acids are given
        acids = resooffac.split(',') if len(resooffac.split(',')) > 1 else resooffac.split(' ')

        # Remove acids if they are already in self.resoofflst. This is used to
        # delete aircraft from this list.
        # Else, add them to self.resoofflst. These aircraft will not avoid anybody
        if set(acids) <= set(self.resoofflst):
            self.resoofflst = filter(lambda x: x not in set(acids), self.resoofflst)
        else:
            self.resoofflst.extend(acids)

        # active the switch, if there are acids in the list
        self.swresooff = len(self.resoofflst) > 0

    def SetConfAreaFilter(self, flag=None, filtercode=None, shapename=None):
        '''Set the conflict-area-filter switch, the type of filter, and the shape where it should act'''
        options = ["OPTION1","OPTION2","OPTION3", "OPTION4", "OPTION5"]
        if flag is None and filtercode is None and shapename is None:
            return True , "CONFAREAFILTER ON/OFF, FILTERCODE, SHAPENAME" + \
                          "\nAvialable filter codes:" + \
                          "\n     OPTION1: CPA in shapename" + \
                          "\n     OPTION2: CPA and 1 aircraft in conflict pair in shapename" + \
                          "\n     OPTION3: CPA and both aircraft in conflict pair in shapename" + \
                          "\n     OPTION4: Both aircraft in conflict pair in shapename" + \
                          "\n     OPTION5: CPA or 1 aircraft in conflict pair in shapename" + \
                          "\nConflictAreaFilter is currently " + ("ON" if self.swconfareafilt else "OFF") + \
                          "\nFiltercode is currently " + str(self.areafiltercode) + \
                          "\nShapename  is currently " + str(self.areafiltershape)
        if not flag:
            self.swconfareafilt  = flag
            self.areafiltercode  = None
            self.areafiltershape = None
            return True
        else:
            if filtercode not in options:
                return False, "Filter code not understood. Available Options: " + str(options)
            elif shapename not in areafilter.areas:
                return False, "Shape does not exist (please create shape first) or incorrectly spelt."
            self.swconfareafilt  = flag
            self.areafiltercode  = filtercode
            self.areafiltershape = shapename
            return True

    def SetResoSpawnCheck(self, flag=None, factor=None):
        '''Set the reso-spawn-check flag and factor.
        Reso-spawn-check prevents aircraft that are just spawned
        in a very short term conflict (determined by the factor argument), or
        spawned in an intrusion, from performing a resolution. This is good from
        a resolution stabilty point of view. These conflicts/intrusions will
        continue to be logged, but not resolved.
        '''
        if flag is None and factor is None:
            return True, "RESOSPAWNCHECK ON/OFF, [LOOK_AHEAD_TIME_FACTOR (>0)]" + \
                         "\nRESOSPAWNCHECK is currently " + ("ON" if self.swspawncheck else "OFF") + \
                         "\nLOOK_AHEAD_TIME_FACTOR is currently " + str(self.spawncheckfactor)
        if not flag:
            self.swspawncheck     = flag
            self.spawncheckfactor = 1.0 # restore the reso-spawn-check factor
        else:
            if factor is None:
                self.swspawncheck = flag
                return True, "RESOSPAWNCHECK activated. LOOK_AHEAD_TIME_FACTOR equals " + str(self.spawncheckfactor)
            elif factor<0.0:
                return False,"LOOK_AHEAD_TIME_FACTOR must be a POSITIVE float"
            elif factor>0.0:
                self.swspawncheck = flag
                self.spawncheckfactor = factor
                return True, "RESOSPAWNCHECK activated. LOOK_AHEAD_TIME_FACTOR equals " + str(self.spawncheckfactor)
            else:
                return False, "LOOK_AHEAD_TIME_FACTOR not understood. Check syntax!"

    def ConfAreaFilter(self, traf, ownidx, intidx):
        '''Checks if the conflict between ownship and intruder matches the
        Conflict-Area-Filter settings'''

        # Determine CPA for ownship
        rngo       = self.tcpa[ownidx,intidx] * traf.gs[ownidx] / nm
        lato, lono = geo.qdrpos(traf.lat[ownidx], traf.lon[ownidx], traf.trk[ownidx], rngo)
        alto       = traf.alt[ownidx] + self.tcpa[ownidx,intidx] * traf.vs[ownidx]

        # Determine CPA for intruder
        rngi       = self.tcpa[intidx,ownidx] * traf.gs[intidx] / nm
        lati, loni = geo.qdrpos(traf.lat[intidx], traf.lon[intidx], traf.trk[intidx], rngi)
        alti       = traf.alt[intidx] + self.tcpa[intidx,ownidx] * traf.vs[intidx]

        # Check if CPAs are inside selected shape
        cpainsideo = areafilter.checkInside(self.areafiltershape, lato, lono, alto)
        cpainsidei = areafilter.checkInside(self.areafiltershape, lati, loni, alti)

        # OPTION1: CPA inside selected shape
        if self.areafiltercode == "OPTION1":
            inarea = np.where(np.logical_and(cpainsidei,cpainsideo))

        # OPTION2: CPA and 1 aircraft inside selected shape
        elif self.areafiltercode == "OPTION2":
            acinsideo = areafilter.checkInside(self.areafiltershape, traf.lat[ownidx], traf.lon[ownidx], traf.alt[ownidx])
            acinsidei = areafilter.checkInside(self.areafiltershape, traf.lat[intidx], traf.lon[intidx], traf.alt[intidx])
            inarea    = np.where(np.logical_and(np.logical_and(cpainsidei,cpainsideo), np.logical_or(acinsideo,acinsidei)))

        # OPTION3: CPA and both aircraft inside selected shape
        elif self.areafiltercode == "OPTION3":
            acinsideo = areafilter.checkInside(self.areafiltershape, traf.lat[ownidx], traf.lon[ownidx], traf.alt[ownidx])
            acinsidei = areafilter.checkInside(self.areafiltershape, traf.lat[intidx], traf.lon[intidx], traf.alt[intidx])
            inarea    = np.where(np.logical_and(np.logical_and(cpainsidei,cpainsideo), np.logical_and(acinsideo,acinsidei)))

        # OPTION4: Both aircraft inside selected shape
        elif self.areafiltercode == "OPTION4":
            acinsideo = areafilter.checkInside(self.areafiltershape, traf.lat[ownidx], traf.lon[ownidx], traf.alt[ownidx])
            acinsidei = areafilter.checkInside(self.areafiltershape, traf.lat[intidx], traf.lon[intidx], traf.alt[intidx])
            inarea    = np.where(np.logical_and(acinsideo,acinsidei))

        # OPTION5: CPA OR 1 aircraft inside selected shape
        elif self.areafiltercode == "OPTION5":
            acinsideo = areafilter.checkInside(self.areafiltershape, traf.lat[ownidx], traf.lon[ownidx], traf.alt[ownidx])
            acinsidei = areafilter.checkInside(self.areafiltershape, traf.lat[intidx], traf.lon[intidx], traf.alt[intidx])
            inarea    = np.where(np.logical_or(np.logical_or(cpainsidei,cpainsideo), np.logical_or(acinsideo,acinsidei)))

        # OPTION6: One aircraft inside selected shape
        elif self.areafiltercode == "OPTION6":
            acinsideo = areafilter.checkInside(self.areafiltershape, traf.lat[ownidx], traf.lon[ownidx], traf.alt[ownidx])
            acinsidei = areafilter.checkInside(self.areafiltershape, traf.lat[intidx], traf.lon[intidx], traf.alt[intidx])
            inarea    = np.where(np.logical_or(acinsideo,acinsidei))

        # Filter out the conflcits that do not match the selected "option"
        ownidx = ownidx[inarea]
        intidx = intidx[inarea]
        rngo   = rngo[inarea]
        lato   = lato[inarea]
        lono   = lono[inarea]
        alto   = alto[inarea]

        return ownidx, intidx, rngo, lato, lono, alto

    def APorASAS(self):
        """ Decide for each aircraft in the active conflict list whether the
        ASAS commands should be followed or not, based on if the conflcit pairs
        passed their CPA. """

        # first assume that asas should be turned off. Do the below computations
        # and turn it back on if conflict is not past CPA
        self.active.fill(False)

        # Look at all conflicts, also the ones that are solved but CPA is yet to come
        for conflict in self.conflist_active[:]:
            ac1      = conflict[0]
            ac2      = conflict[1]
            id1, id2 = self.traf.id2idx(ac1), self.traf.id2idx(ac2)
            if id1 >= 0 and id2 >= 0:
                # Check if conflict is past CPA
                d = np.array([self.traf.lon[id2] - self.traf.lon[id1], self.traf.lat[id2] - self.traf.lat[id1]])

                # write velocities as vectors
                v1 = np.array([self.traf.gseast[id1], self.traf.gsnorth[id1]])
                v2 = np.array([self.traf.gseast[id2], self.traf.gsnorth[id2]])

                # Compute pastCPA
                pastCPA = np.dot(d,v2-v1)>0.

                # hLOS:
                # Aircraft should continue to resolve until there is no horizontal
                # LOS. This is particularly relevant when vertical resolutions
                # are used.
                dx     = (self.traf.lat[id1] - self.traf.lat[id2]) * 111319.
                dy     = (self.traf.lon[id1] - self.traf.lon[id2]) * 111319.
                hdist2 = dx**2 + dy**2
                hLOS   = hdist2 < self.R**2

                # Bouncing conflicts:
                # If two aircraft are getting in and out of conflict continously,
                # then it is a bouncing conflict. ASAS should stay active until
                # the bouncing stops.
                bouncingConflict = (abs(self.traf.trk[id1] - self.traf.trk[id2]) < 15.) & (hdist2<self.Rm**2)

                # Decide if conflict is over or not.
                # If not over, turn active to true.
                # If over, then initiate recovery
                if not pastCPA or hLOS or bouncingConflict:
                    # Aircraft haven't passed their CPA: must follow their ASAS
                    self.active[id1] = True
                    self.active[id2] = True

                else:
                    # Waypoint recovery after conflict
                    # Find the next active waypoint and send the aircraft to that
                    # waypoint.
                    iwpid1 = self.traf.ap.route[id1].findact(self.traf,id1)
                    if iwpid1 != -1: # To avoid problems if there are no waypoints
                        # send aircraft direct to the next active waypoint
                        self.traf.ap.route[id1].direct(self.traf, id1, self.traf.ap.route[id1].wpname[iwpid1])
                        # afterconfalt for id1 (only if activated and not if only horizontal resolutions)
                        if self.swafterconfalt and not self.swresohoriz and self.cr_name != "OFF": 
                            self.afterConfAlt(id1,iwpid1)
                        # if layered airspace, send id1 to new altitude if required after resolution
                        if self.isLayers and self.swresohoriz and self.cr_name != "OFF":
                            self.layersTrajectoryRecovery(id1,iwpid1)
                    
                    iwpid2 = self.traf.ap.route[id2].findact(self.traf,id2)
                    if iwpid2 != -1: # To avoid problems if there are no waypoints
                        # send aircraft direct to the next active waypoint
                        self.traf.ap.route[id2].direct(self.traf, id2, self.traf.ap.route[id2].wpname[iwpid2])
                        # afterconfalt for id2 (only if activated and not if only horizontal resolutions)
                        if self.swafterconfalt and not self.swresohoriz and self.cr_name != "OFF": 
                            self.afterConfAlt(id2,iwpid2)
                        # if layered airspace, send id2 to new altitude if required after resolution
                        if self.isLayers and self.swresohoriz and self.cr_name != "OFF":
                            self.layersTrajectoryRecovery(id2,iwpid2)
                    
                    # If conflict is solved, remove it from conflist_active list
                    # This is so that if a conflict between this pair of aircraft
                    # occurs again, then that new conflict should be detected, logged
                    # and solved (if reso is on). The conflict should also be removed
                    # from conflist_resospwancheck list.
                    self.conflist_active.remove(conflict)
                    if conflict in self.conflist_resospawncheck:
                        self.conflist_resospawncheck.remove(conflict)

            # If aircraft id1 cannot be found in traffic because it has finished its
            # flight (and has been deleted), start trajectory recovery for aircraft id2
            # And remove the conflict from the conflist_active list
            elif id1 < 0 and id2 >= 0:
                 iwpid2 = self.traf.ap.route[id2].findact(self.traf,id2)
                 if iwpid2 != -1: # To avoid problems if there are no waypoints
                     self.traf.ap.route[id2].direct(self.traf, id2, self.traf.ap.route[id2].wpname[iwpid2])
                     # afterconfalt for id2 (only if activated and not if only horizontal resolutions)
                     if self.swafterconfalt and not self.swresohoriz and self.cr_name != "OFF": 
                         self.afterConfAlt(id2,iwpid2)
                     # if layered airspace, send id2 to new altitude if required after resolution
                     if self.isLayers and self.swresohoriz and self.cr_name != "OFF":
                         self.layersTrajectoryRecovery(id2,iwpid2)
                 
                 # also remove from active list and resospawn check
                 self.conflist_active.remove(conflict)
                 if conflict in self.conflist_resospawncheck:
                        self.conflist_resospawncheck.remove(conflict)

            # If aircraft id2 cannot be found in traffic because it has finished its
            # flight (and has been deleted) start trajectory recovery for aircraft id1
            # And remove the conflict from the conflist_active list
            elif id2 < 0 and id1 >= 0:
                iwpid1 = self.traf.ap.route[id1].findact(self.traf,id1)
                if iwpid1 != -1: # To avoid problems if there are no waypoints
                    self.traf.ap.route[id1].direct(self.traf, id1, self.traf.ap.route[id1].wpname[iwpid1])
                    # afterconfalt for id1 (only if activated and not if only horizontal resolutions)
                    if self.swafterconfalt and not self.swresohoriz and self.cr_name != "OFF": 
                        self.afterConfAlt(id1,iwpid1)
                    # if layered airspace, send id1 to new altitude if required after resolution
                    if self.isLayers and self.swresohoriz and self.cr_name != "OFF":
                        self.layersTrajectoryRecovery(id1,iwpid1)
                
                # also remove from active list and resospawn check
                self.conflist_active.remove(conflict)
                if conflict in self.conflist_resospawncheck:
                        self.conflist_resospawncheck.remove(conflict)

            # if both ids are unknown, then delete this conflict, because both aircraft
            # have completed their flights (and have been deleted)
            else:
                self.conflist_active.remove(conflict)
                if conflict in self.conflist_resospawncheck:
                        self.conflist_resospawncheck.remove(conflict)

    def setConflictDefinition(self, flag=None):
        ''' Activates the alternate conflict definition (intrusion is not a conflict)
            This means that when tinconf < 0, and the conflict turns into a intrusion,
            it is no longer regarded to be a conflict, but it is regarded to be an intrusion '''
        if flag is None:
            return True, "CONFDEF is currently " + ("ON" if self.swconfdef else "OFF")
        self.swconfdef = flag
        return True, "CONFDEF is " + ("ON" if self.swconfdef else "OFF")

    def setAfterConfAlt(self, flag=None):
        ''' If switched on, altitude not recovered for cruising aircraft with waypoints  '''
        if flag is None:
            return True, "AFTERCONFALT is currently " + ("ON" if self.swafterconfalt else "OFF")
        self.swafterconfalt = flag
        return True, "AFTERCONFALT is " + ("ON" if self.swafterconfalt else "OFF")
        
    def setAirspaceConcept(self, conceptcode=None, minCruiseAlt=None, layerHeight=None, numLayers=None, minDist=None, maxDist=None, margin=False):
        ''' Sets the parameters of the airspace concept'''
        
        options = ["UA","L360","L180","L90","L45"]        
        
        if conceptcode is None:
            return True, "CONCEPT is currently " + self.conceptcode + "\nAvailable Options: " + str(options)
            
        if conceptcode not in options:
            return False, "Conceptcode not understood.\nAvailable Options: " + str(options)
            
        # redefine default concept variables with new values
        self.conceptcode    = conceptcode
        self.minCruiseAlt   = minCruiseAlt if minCruiseAlt is not None else self.minCruiseAlt # [ft]
        self.layerHeight    = layerHeight if layerHeight is not None else self.layerHeight    # [ft]
        self.numLayers      = numLayers if numLayers is not None else self.numLayers
        self.minDist        = minDist if minDist is not None else self.minDist                # [NM]
        self.maxDist        = maxDist if maxDist is not None else self.maxDist                # [NM]
        self.recoveryMargin = margin
        self.maxCruiseAlt   = self.minCruiseAlt + (self.numLayers-1)*self.layerHeight         # [ft]
        
        # Computed layered airspace parameters if layered concept 
        if self.conceptcode[0] == 'L':
            self.alpha        = float(conceptcode[1:])  # [deg]
            self.numFLin1Set  = 360.0/self.alpha
            self.numLayerSets = self.numLayers/self.numFLin1Set
            self.isLayers     = True
        
        return True, "Airsapce Concept is set to " + self.conceptcode
        
        
    def layersCruisingAltitude(self, idx, iwp):
        '''Compute the cruising altitude [m] for an aircraft in layered airspaces
           This depends on the direct bearing from the aircrafts current position to the destination
           It is also checked if the aircraft is in the recovery heading range of its assigned flight level
           NOTE: This function should only be called for climbing and cruising aircraft.
                 This check should be done outside this function. '''
                 
        # TRLOG reset
        self.trlogid = []
        self.trlogiscruising = []
        self.trlogprealt = []
        self.trlogpreapalt = []
        self.trlogprehdg = []
        self.trlogpreaphdg = []
        self.trlogprelaylowerhdg = []
        self.trlogprelayupperhdg = []
        self.trlogrecoverylowerhdg = []
        self.trlogrecoveryupperhdg = []
        self.trloginrecoveryrange = []
        self.trlogpostalt = []
        self.trlogposthdg = []
        self.trlogpostlaylowerhdg = []
        self.trlogpostlayupperhdg = []
        
        # lat and lon of aircraft's origin and destination
        # needed for layers altitude equation
        origlat = self.traf.ap.origlat[idx]
        origlon = self.traf.ap.origlon[idx]
        destlat = self.traf.ap.destlat[idx]
        destlon = self.traf.ap.destlon[idx]
        
        # Compute distance between origin and destination of aircraft [NM]
        # needed for layers altitude equation
        distanceAC = geo.latlondist(origlat,origlon,destlat,destlon)/nm
        
        # compute the bearing and the distance from origin to destination
        qdrorig2dest, distorig2dest = geo.qdrdist(origlat, origlon, destlat, destlon)  # [deg][nm])
        qdrorig2dest = qdrorig2dest%360.0
        
        # compute the bearing and the distance to the destination from the aircraft's current location
        # needed for layers altitude equation - > i.e, at time of trajectory recovery
        qdr2Dest, dist2Dest = geo.qdrdist(self.traf.lat[idx], self.traf.lon[idx], destlat, destlon)  # [deg][nm])
        qdr2Dest = qdr2Dest%360.0
        
        # Determine the lower heading value of the flight level layer the ac is currently in, or is climbing to. 
        layerHdg = int(qdrorig2dest/self.alpha)*self.alpha # [deg] # ap.trk contains the pre conflict direction of the aircraft. 
        # Determine the lower and upper heading range taking into consideration an additional 5 deg of recovery margin
        upperRecoveryHdg  = (layerHdg + self.alpha + 5.0)%360.0  # upper with a margin of 5 deg
        lowerRecoveryHdg  = (layerHdg - 5.0)%360.0 # lower with margin of 5 deg
        
        # Determine if the aircraft is inside the recovery heading range of the current flight level
        # Note: for alpha = 360.0 all headings are allowed in each cruising flight level, so there is no
        #       need to change altitude after CR no matter what qdr2Dest is
        if self.alpha == 360.0:
            inRecoveryHdgRange = True
        else:
            # Determine if aicraft bearing to destination is inside recovery heading range for this flight level
            if lowerRecoveryHdg < upperRecoveryHdg:
                inRecoveryHdgRange = lowerRecoveryHdg <= qdr2Dest <= upperRecoveryHdg
            else:
                inRecoveryHdgRange = lowerRecoveryHdg <= qdr2Dest or qdr2Dest <= upperRecoveryHdg

        # Set the values needed for TR logging
        self.trlogid.append(self.traf.id[idx])
        self.trlogiscruising.append(abs(self.traf.vs[idx])<0.1)
        self.trlogprealt.append(self.traf.alt[idx])
        self.trlogpreapalt.append(self.traf.ap.alt[idx])
        self.trlogprehdg.append(self.traf.trk[idx]%360.0)
        self.trlogpreaphdg.append(qdrorig2dest)
        self.trlogprelaylowerhdg.append(layerHdg%360.0)
        self.trlogprelayupperhdg.append((layerHdg + self.alpha)%360.0)
        self.trlogrecoverylowerhdg.append(lowerRecoveryHdg)
        self.trlogrecoveryupperhdg.append(upperRecoveryHdg)
        self.trloginrecoveryrange.append(inRecoveryHdgRange)
        self.trlogposthdg.append(qdr2Dest)
       
        # if recovery margin is on, and if ac is cruising/climbing and if the ac is inside  
        # the current/target flight level's recovery heading range, then keep 
        # flying in the current (or previous target) altitude even if this is slightly wrong.
        if self.recoveryMargin and inRecoveryHdgRange:
            # self.traf.ap.alt[idx] is the previously commanded altitude. So just keep flying this if in recovery margin. 
            newAlt = self.traf.ap.alt[idx] # already in [m]

            # Set the values needed for TR logging
            self.trlogpostalt.append(newAlt)
            self.trlogpostlaylowerhdg.append(layerHdg%360.0)
            self.trlogpostlayupperhdg.append((layerHdg + self.alpha)%360.0)
            
            # print outs for debugging
            print
            print "%s is staying is within the recovery heading range" %(self.traf.id[idx])
            print "     LowerHeading: %i, UpperHeading: %i" %(int(layerHdg%360.0),int((layerHdg + self.alpha)%360.0))
            print "     LowerRHdg: %i, UpperRHdg:  %i"   %(lowerRecoveryHdg, upperRecoveryHdg) 
            print "     Old AP altitude:  %f ft" %(self.traf.ap.alt[idx]/ft)
            print "     New AP altitude:  %f ft" %(newAlt/ft)
            print "     Old AP Hdg: %f" %(qdrorig2dest)            
            print "     New AP Hdg: %f" %(qdr2Dest)
            print
        
        # otherwise, it must be climbing, or cruising but with a bearing to destination that is outside 
        # the receovery heading range of the flight level it is in. Then use the layers 
        # altitude equation to send it to a new cruising altitude. 
        else:
            
            # compute distance ratio
            distanceRatio = (distanceAC-self.minDist)/(self.maxDist-self.minDist)
            
            # heading ratio
            headingRatio = qdr2Dest/self.alpha
            
            # compute newAlt using layers altitude equation
            newAlt = self.minCruiseAlt + self.layerHeight*\
                    (np.floor(distanceRatio*self.numLayerSets)*self.numFLin1Set + np.floor(headingRatio))
            newAlt = newAlt*ft # convert to [m]

            # Set the values needed for TR logging
            self.trlogpostalt.append(newAlt)
            self.trlogpostlaylowerhdg.append(int(qdr2Dest/self.alpha)*self.alpha)
            self.trlogpostlayupperhdg.append(int(qdr2Dest/self.alpha)*self.alpha + self.alpha)
            
            # print outs for debugging
            print
            print "%s is CLIMBING/DESCENDING TO NEW CRUISING ALTITUDE" %(self.traf.id[idx])
            print "     LowerHeading: %i, UpperHeading: %i" %(int(layerHdg%360.0),int((layerHdg + self.alpha)%360.0))
            print "     LowerRHdg: %i, UpperRHdg:  %i"   %(lowerRecoveryHdg, upperRecoveryHdg) 
            print "     Old AP altitude:  %f ft" %(self.traf.ap.alt[idx]/ft)
            print "     New AP altitude:  %f ft" %(newAlt/ft)
            print "     Old AP Hdg: %f" %(qdrorig2dest)            
            print "     New AP Hdg: %f" %(qdr2Dest)
            print "     New altitude hdg range: %i-%i" %(int(int(qdr2Dest/self.alpha)*self.alpha),int(int(qdr2Dest/self.alpha)*self.alpha+self.alpha))
            print
            
            import pdb
            pdb.set_trace()
            
        # call the TR logger
        self.trlog.log()
            
        # return the cruising altitude[m]
        return newAlt
        
    
    def layersTrajectoryRecovery(self, idx, iwp): 
        '''Commands the autopilot to climb/descend to a new cruising altitude 
        if that is required for a particular cruising/climbing aircraft during 
        trajectory recovery to the destination after a conflict resolution'''
        
        # determine if ac is desending to destination
        isDestination = self.traf.ap.route[idx].wptype[iwp] == self.traf.ap.route[idx].dest
        isDescending1 = np.logical_and(self.traf.vs[idx] <= -0.1, isDestination)
        isDescending2 = np.logical_and(self.traf.ap.alt[idx] <= 10.0*ft, isDestination) # to handle aircraft cruising at zero altitude for a few seconds while waiting to be deleted because area function is periodic
        isDescending  = np.logical_or(isDescending1, isDescending2)
        
        # Only ask the auto-pilot to do anything if the aircraft is climbing or cruising
        # i.e., only if it is NOT descending to destination
        if not isDescending:
        
            # compute new altitude based on the recovery heading of the aircraft
            newAlt = self.layersCruisingAltitude(idx, iwp)
            
            # set the autopilot to the new cruising altitude
            self.traf.apalt[idx]  = newAlt
            self.traf.ap.alt[idx] = newAlt
            
            # Update the TOC waypoint in route with the new altitude and speed
            # Needed before recalculaing the flight-plan in the next step
            # NOTE. TOC waypoint has index [1] for the type of scenarios used
            #       the here. Also, wpsd is in CAS since this is taken directly from scn file
            taswp = vcas2tas(self.traf.ap.route[idx].wpspd[1], self.traf.ap.route[idx].wpalt[1])
            caswp = vtas2cas(taswp,newAlt)
            self.traf.ap.route[idx].wpspd[1] = caswp
            self.traf.ap.route[idx].wpalt[1] = newAlt
            
            # recompute flight plan and compute VNAV so that dist2vs is updated
            # this will ensure that the aircraft starts its descent to the destination at the right time
            # even though the aircraft has changed its altitude. 
            self.traf.ap.route[idx].calcfp()
            self.traf.ap.ComputeVNAV(idx, self.traf.ap.route[idx].wptoalt[iwp], self.traf.ap.route[idx].wpxtoalt[iwp])
            
            
    def afterConfAlt(self, idx, iwp):
        ''' Commands the autopilot to not recover pre-conflict altitude during
            trajectory recovery after conflict '''
        # a/c has to be in the cruising alt range -> 1219m (=4000ft) and 3567m (=11700ft)    
        if (self.minCruiseAlt-1)*ft <= self.traf.alt[idx] <= (self.maxCruiseAlt+1)*ft: 
            
            # a/c has be in the cruise phase of a flight
            if iwp > 1 and self.traf.ap.swvnavvs[idx] == False: 
            
                # Then set the selected autopilot altitude to be the current alt
                self.traf.apalt[idx] = self.traf.alt[idx]
                self.traf.ap.alt[idx] = self.traf.alt[idx]
                
                # Update the TOC waypoint in route with the new altitude and speed
                # Needed before recalculaing the flight-plan in the next step
                # NOTE. TOC waypoint has index [1] for the type of scenarios used
                #       the here. Also, wpsd is in CAS since this is taken directly from scn file
                taswp = vcas2tas(self.traf.ap.route[idx].wpspd[1], self.traf.ap.route[idx].wpalt[1])
                caswp = vtas2cas(taswp,self.traf.alt[idx])
                self.traf.ap.route[idx].wpspd[1] = caswp
                self.traf.ap.route[idx].wpalt[1] = self.traf.alt[idx]
                    
                # recompute flight plan and compute VNAV so that dist2vs is updated
                # this will ensure that the aircraft starts its descent to the destination at the right time
                # even though the aircraft has changed its altitude. 
                self.traf.ap.route[idx].calcfp()
                self.traf.ap.ComputeVNAV(idx, self.traf.ap.route[idx].wptoalt[iwp], self.traf.ap.route[idx].wpxtoalt[iwp])
            

    def create(self):
        super(ASAS, self).create()

        # ASAS output commanded values
        self.trk[-1] = self.traf.trk[-1]
        self.spd[-1] = self.traf.tas[-1]
        self.alt[-1] = self.traf.alt[-1]

    def update(self, simt):
        self.simt = simt
        iconf0 = np.array(self.iconf)

        # Scheduling: update when dt has passed
        if self.swasas and simt >= self.tasas:
            self.tasas += self.dtasas

            # Conflict detection
            self.cd.detect(self, self.traf, simt)

            # Is conflict active?
            self.APorASAS()

            # Conflict resolution
            self.cr.resolve(self, self.traf)

            # Update ASAS log variables
            asasLogUpdate(self, self.traf)
            

        # Change labels in interface
        if settings.gui == "pygame":
            for i in range(self.traf.ntraf):
                if np.any(iconf0[i] != self.iconf[i]):
                    self.traf.label[i] = [" ", " ", " ", " "]
