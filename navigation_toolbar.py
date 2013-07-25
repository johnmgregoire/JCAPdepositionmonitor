# Allison Schubauer and Daisy Hernandez
# Created: 7/25/2013
# Last Updated: 7/25/2013
# For JCAP

import matplotlib.backends.backend_qt4
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar

class NavigationToolbar(NavigationToolbar):
    # only display the buttons we need
    matplotlib.backends.backend_qt4.figureoptions = None
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Pan', 'Zoom', 'Save')]
