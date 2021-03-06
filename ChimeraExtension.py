# -*- coding: utf-8 -*-
"""
Created on Tue May 31 10:40:14 2016

@author: jeremy
"""

import chimera.extension

class TetrEMO(chimera.extension.EMO):
    def name(self):
        return 'Tetr'

    def description(self):
        return 'Run the Tetr utility'

    def categories(self):
        return ['Utilities']

    def icon(self):
        return self.path('TetrLogo.tiff')

    def activate(self):
        # Comment out if no GUI is needed
        from chimera.dialogs import display
        display(self.module("gui").TetrDialog.name)
        return None

# Register
chimera.extension.manager.registerExtension(TetrEMO(__file__))

from Midas.midas_text import addCommand

def cmdTetr(cmdName, args):
    from Tetr import runTetr
    from Midas.midas_text import doExtensionFunc
    doExtensionFunc(runTetr, args)

addCommand("tetr", cmdTetr, changesDisplay=True)




class Lev00EMO(chimera.extension.EMO):
    def name(self):
        return 'Lev00'

    def description(self):
        return 'Run the Lev00 utility'

    def categories(self):
        return ['Utilities']

    def icon(self):
        return self.path('Lev00Logo.tiff')

    def activate(self):
        # Comment out if no GUI is needed
        from chimera.dialogs import display
        display(self.module("gui").Lev00Dialog.name)
        return None

# Register
chimera.extension.manager.registerExtension(Lev00EMO(__file__))

from Midas.midas_text import addCommand

def cmdTetr(cmdName, args):
    from Tetr import runTetr
    from Midas.midas_text import doExtensionFunc
    doExtensionFunc(runTetr, args)

addCommand("lev00", cmdTetr, changesDisplay=True)
