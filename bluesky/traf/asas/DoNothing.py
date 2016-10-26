# -*- coding: utf-8 -*-
"""
Created on Wed Mar 04 14:27:44 2015

@author: Jerom Maas
"""

import numpy as np
from ...tools.aero import ft, nm

def start(dbconf):
    pass

def resolve(dbconf, traf):
    # If resolution is off, and detection is on, and a conflict is detected
    # then asas will be active for that airplane. Since resolution is off, it
    # should then follow the auto pilot instructions.     
    dbconf.asastrk = traf.atrk
    dbconf.asasspd = traf.aptas
    dbconf.asasalt = traf.apalt
    
    # for vs, first check if it needs to change altitude
    # if it does, then use the default climb rate    
    swaltsel = np.abs(traf.apalt-traf.alt) > 0.0
    dbconf.asasvsp = swaltsel*np.sign(traf.apalt-traf.alt)*(3000.*ft/(10.*nm)*traf.gs)
    
    return
