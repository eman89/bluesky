import numpy as np
from ... import settings
from ...tools.aero import ft, nm
from ...tools import areafilter, geo

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


class ASAS():
    """ Central class for ASAS conflict detection and resolution.
        Maintains a confict database, and links to external CD and CR methods."""

    # Dictionary of CD methods
    CDmethods = {"STATEBASED": StateBasedCD}

    # Dictionary of CR methods
    CRmethods = {"OFF": DoNothing, "MVP": MVP, "EBY": Eby, "SWARM": Swarm}

    @classmethod
    def addCDMethod(asas, name, module):
        asas.CDmethods[name] = module

    @classmethod
    def addCRMethod(asas, name, module):
        asas.CRmethods[name] = module

    def __init__(self):
        # All ASAS variables are initialized in the reset function
        self.reset()

    def reset(self):
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

        self.vmin         = 51.4                       # [m/s] Minimum ASAS velocity (100 kts)
        self.vmax         = 308.6                      # [m/s] Maximum ASAS velocity (600 kts)
        self.vsmin        = -3000./60.*ft              # [m/s] Minimum ASAS vertical speed        
        self.vsmax        = 3000./60.*ft               # [m/s] Maximum ASAS vertical speed   
        
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
        self.areafiltercode  = None                    # [-] Code for the conflict area filter that should be used (OPTION1, OPTION2, OPTION3) 
        self.areafiltershape = None                    # [-] Name of shape where area conflict filter is active 

        self.confpairs    = []                         # Start with emtpy database: no conflicts
        self.nconf        = 0                          # Number of detected conflicts
        self.latowncpa    = np.array([])
        self.lonowncpa    = np.array([])
        self.altowncpa    = np.array([])

        self.conflist_all  = []  # List of all Conflicts that are still active (not past CPA). Conflict deleted from list once past CPA
        self.LOSlist_all   = []  # List of all Losses Of Separation till now.
        self.conflist_now  = []  # List of Conflicts detected in the current ASAS cycle. Used to resolve conflicts. 
        self.LOSlist_now   = []  # List of Losses Of Separations in the current ASAS cycle. 
        
        # For keeping track of locations with most severe intrusions
        self.LOSmaxsev    = []
        self.LOShmaxsev   = []
        self.LOSvmaxsev   = []

        # ASAS info per aircraft:
        self.iconf        = []            # index in 'conflicting' aircraft database
        self.asasactive   = np.array([], dtype=bool)  # whether the autopilot follows ASAS or not
        self.asastrk      = np.array([])  # heading provided by the ASAS [deg]
        self.asasspd      = np.array([])  # speed provided by the ASAS (eas) [m/s]
        self.asasalt      = np.array([])  # speed alt by the ASAS [m]
        self.asasvsp      = np.array([])  # speed vspeed by the ASAS [m/s]

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
            return True, ("RSZONEDH [height (ft)]\nCurrent PZ height margin: %.2f ft" %( self.dhm / ft))

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
        options = ["BOTH","SPD","HDG","NONE","ON","OFF","OF"]        
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
        options = ["NONE","ON","OFF","OF","V/S"]        
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
        self.R = self.R*self.resoFacH
        self.Rm = self.R*self.mar
        
        return True, "IMPORTANT NOTE: " + \
                     "\nCurrent horizontal resolution factor is: "+ str(self.resoFacH) + \
                     "\nCurrent PZ radius:" + str(self.R/nm) + " NM" + \
                     "\nCurrent resolution PZ radius: " + str(self.Rm/nm) + " NM\n"
        
    def SetResoFacV(self, value=None):
        ''' Set the vertical resolution factor'''
        if value is None:
            return True, ("RFACV [FACTOR]\nCurrent vertical resolution factor is: %.1f" % self.resoFacV)
        
        self.resoFacV = np.abs(value)
        self.dh = self.dh*self.resoFacV
        self.dhm = self.dh*self.mar
        
        return True, "IMPORTANT NOTE: " + \
                     "\nCurrent vertical resolution factor is: "+ str(self.resoFacV) + \
                     "\nCurrent PZ height:" + str(self.dh/ft) + " ft" + \
                     "\nCurrent resolution PZ height: " + str(self.dhm/ft) + " ft\n"
                     
    def SetPrio(self, flag=None, priocode="FF1"):
        '''Set the prio switch and the type of prio '''
        options = ["FF1","FF2","FF3","LAY1","LAY2"]        
        if flag is None:
            return True, "PRIORULES [ON/OFF] [PRIOCODE]"  + \
                         "\nAvailable priority codes: " + \
                         "\n     FF1:  Free Flight Primary (No Prio) " + \
                         "\n     FF2:  Free Flight Secondary (Cruising has priority)" + \
                         "\n     FF3:  Free Flight Tertiary (Climbing/descending has priority)" + \
                         "\n     LAY1: Layers Primary (Cruising has priority + horizontal resolutions)" + \
                         "\n     LAY2: Layers Secondary (Climbing/descending has priority + horizontal resolutions)" + \
                         "\nPriority is currently " + ("ON" if self.swprio else "OFF") + \
                         "\nPriority code is currently: " + str(self.priocode)                        
        self.swprio = flag         
        if priocode not in options:
            return False, "Priority code Not Understood. Available Options: " + str(options)
        else:
            self.priocode = priocode
            
    def SetNoreso(self,noresoac=''):
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
        self.swnoreso = len(self.noresolst)>0   
        
    def SetResooff(self,resooffac=''):
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
        self.swresooff = len(self.resoofflst)>0  
    
    def SetConfAreaFilter(self, flag=None, filtercode=None, shapename=None):
        '''Set the conflict-area-filter switch, the type of filter, and the shape where it should act'''
        options = ["OPTION1","OPTION2","OPTION3"]       
        if flag is None and filtercode is None and shapename is None:
            return True , "CONFAREAFILTER ON/OFF, FILTERCODE, SHAPENAME" + \
                          "\nAvialable filter codes:" + \
                          "\n     OPTION1: CPA in shapename" + \
                          "\n     OPTION2: CPA and 1 aircraft in conflict pair in shapename" + \
                          "\n     OPTION3: CPA and both aircraft in conflict pair in shapename" + \
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
    
    def ConfAreaFilter(self, traf, i, j):
        '''Checks if the conflict between ownship and intruder matches the 
        Conflict-Area-Filter settings'''
        
        # Determine CPA of Ownship (What to do when ADSB is ON?)
        rng              = self.tcpa[i, j] * traf.gs[i] / nm
        cpalato, cpalono = geo.qdrpos(traf.lat[i], traf.lon[i], traf.trk[i], rng)
        cpaalto          = traf.alt[i] + self.tcpa[i, j] * traf.vs[i]

        # Determine CPA of Intruder (What to do when ADSB is ON?)
        rng              = self.tcpa[i, j] * traf.gs[j] / nm
        cpalati, cpaloni = geo.qdrpos(traf.lat[j], traf.lon[j], traf.trk[j], rng)
        cpaalti          = traf.alt[j] + self.tcpa[i, j] * traf.vs[j]       
        
        # Check if CPAs are inside selected shape
        cpaoInside = areafilter.checkInside(self.areafiltershape, cpalato, cpalono, cpaalto)
        cpaiInside = areafilter.checkInside(self.areafiltershape, cpalati, cpaloni, cpaalti)
        
        # OPTION1: CPA inside selected shape 
        if self.areafiltercode == "OPTION1":            
            confInArea = cpaiInside and cpaoInside               
            
        # OPTION2: CPA and 1 aircraft inside selected shape
        elif self.areafiltercode == "OPTION2":
            acoInside = areafilter.checkInside(self.areafiltershape, traf.lat[i], traf.lon[i], traf.alt[i])
            aciInside = areafilter.checkInside(self.areafiltershape, traf.lat[j], traf.lon[j], traf.alt[j])
            confInArea = (cpaiInside and cpaoInside) and (acoInside or aciInside)
            
        # OPTION3: CPA and both aircraft inside selected shape
        elif self.areafiltercode == "OPTION3":
            acoInside = areafilter.checkInside(self.areafiltershape, traf.lat[i], traf.lon[i], traf.alt[i])
            aciInside = areafilter.checkInside(self.areafiltershape, traf.lat[j], traf.lon[j], traf.alt[j])
            confInArea = (cpaiInside and cpaoInside) and (acoInside and aciInside)          
        
        return cpalato, cpalono, cpaalto, confInArea
    
    def APorASAS(self, traf):
        """ Decide for each aircraft in the conflict list whether the ASAS
        should be followed or not, based on if the aircraft pairs passed
        their CPA. """
        
        self.asasactive.fill(False)
    
        # Look at all conflicts, also the ones that are solved but CPA is yet to come
        for conflict in self.conflist_all:
            ac1, ac2 = conflict.split(" ")
            id1, id2 = traf.id2idx(ac1), traf.id2idx(ac2)
            if id1 >= 0 and id2 >= 0:
                # Check if conflict is past CPA
                d = np.array([traf.lon[id2] - traf.lon[id1], traf.lat[id2] - traf.lat[id1]])
    
                # write velocities as vectors
                v1 = np.array([traf.gseast[id1], traf.gsnorth[id1]])
                v2 = np.array([traf.gseast[id2], traf.gsnorth[id2]])
                
                # Compute pastCPA
                pastCPA = np.dot(d,v2-v1)>0.
                
                # hLOS:
                # Aircraft should continue to resolve until there is no horizontal 
                # LOS. This is particularly relevant when vertical resolutions
                # are used. 
                dx = (traf.lat[id1] - traf.lat[id2]) * 111319.
                dy = (traf.lon[id1] - traf.lon[id2]) * 111319.    
                hdist2 = dx**2 + dy**2
                hLOS   = hdist2 < self.R**2          
                
                # Bouncing conflicts:
                # If two aircraft are getting in and out of conflict continously, 
                # then they it is a bouncing conflict. ASAS should stay active until 
                # the bouncing stops.
                bouncingConflict = (abs(traf.trk[id1] - traf.trk[id2]) < 30.) & (hdist2<self.Rm**2)         
                
                # Decide if conflict is over or not. 
                # If not over, turn asasactive to true. 
                # If over, then initiate recovery
                if not pastCPA or hLOS or bouncingConflict:
                    # Aircraft haven't passed their CPA: must follow their ASAS
                    self.asasactive[id1] = True
                    self.asasactive[id2] = True
                
                else:
                    # Waypoint recovery after conflict
                    # Find the next active waypoint and send the aircraft to that 
                    # waypoint.             
                    iwpid1 = traf.route[id1].findact(traf,id1)
                    if iwpid1 != -1: # To avoid problems if there are no waypoints
                        traf.route[id1].direct(traf, id1, traf.route[id1].wpname[iwpid1])
                    iwpid2 = traf.route[id2].findact(traf,id2)
                    if iwpid2 != -1: # To avoid problems if there are no waypoints
                        traf.route[id2].direct(traf, id2, traf.route[id2].wpname[iwpid2])
                    
                    # If conflict is solved, remove it from conflist_all list
                    # This is so that if a conflict between this pair of aircraft 
                    # occurs again, then that new conflict should be detected, logged
                    # and solved (if reso is on)
                    self.conflist_all.remove(conflict)
            
            # If aircraft id1 cannot be found in traffic because it has finished its
            # flight (and has been deleted), start trajectory recovery for aircraft id2
            # And remove the conflict from the conflict_all list
            elif id1 < 0 and id2 >= 0:
                 iwpid2 = traf.route[id2].findact(traf,id2)
                 if iwpid2 != -1: # To avoid problems if there are no waypoints
                     traf.route[id2].direct(traf, id2, traf.route[id2].wpname[iwpid2])
                 self.conflist_all.remove(conflict)
    
            # If aircraft id2 cannot be found in traffic because it has finished its
            # flight (and has been deleted) start trajectory recovery for aircraft id1
            # And remove the conflict from the conflict_all list
            elif id2 < 0 and id1 >= 0:
                iwpid1 = traf.route[id1].findact(traf,id1)
                if iwpid1 != -1: # To avoid problems if there are no waypoints
                    traf.route[id1].direct(traf, id1, traf.route[id1].wpname[iwpid1])
                self.conflist_all.remove(conflict)
            
            # if both ids are unknown, then delete this conflict, because both aircraft
            # have completed their flights (and have been deleted)
            else:
                self.conflist_all.remove(conflict)      

    def create(self, trk, spd, alt):
        # ASAS info: no conflict => empty list
        self.iconf.append([])  # List of indices in 'conflicting' aircraft database

        # ASAS output commanded values
        self.asasactive = np.append(self.asasactive, False)
        self.asastrk    = np.append(self.asastrk, trk)
        self.asasspd    = np.append(self.asasspd, spd)
        self.asasalt    = np.append(self.asasalt, alt)
        self.asasvsp    = np.append(self.asasvsp, 0.)

    def delete(self, idx):
        del self.iconf[idx]
        self.asasactive = np.delete(self.asasactive, idx)
        self.asastrk    = np.delete(self.asastrk, idx)
        self.asasspd    = np.delete(self.asasspd, idx)
        self.asasalt    = np.delete(self.asasalt, idx)
        self.asasvsp    = np.delete(self.asasvsp, idx)

    def update(self, traf, simt):
        # Scheduling: update when dt has passed
        if self.swasas and simt >= self.tasas:
            self.tasas += self.dtasas

            # Conflict detection
            self.cd.detect(self, traf, simt)
            # Is conflict active? Then follow ASAS, else follow AP.
            self.APorASAS(traf)
            # Conflict resolution
            self.cr.resolve(self, traf)
