# Allison Schubauer and Daisy Hernandez
# Created: 6/06/2013
# Last Updated: 6/06/2013
# For JCAP

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as colors
import matplotlib.cm as cm
from process_deposition_data import *

class DepositionGraph(FigureCanvas):

    def __init__(self, parent="None", width=2, height=2,
                 dpi=120):
        # initialize matplotlib figure
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.figure)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.initPlot()

    def initPlot(self):
        self.xdata = []
        self.ydata = []
        self.ratedata = []
        for x, y, rate in DEP_DATA:
            self.xdata.append(x)
            self.ydata.append(y)
            self.ratedata.append(rate)
        self.plot = self.figure.add_subplot(111)
        self.scalarMap = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=150))
        self.scalarMap._A = self.ratedata
        # comment this back in when data processor is connected
        self.plot.scatter(self.xdata, self.ydata, c=self.ratedata, marker='o', edgecolor='none', s=60)
        self.plot.set_aspect(1.)
        self.figure.colorbar(self.scalarMap)

    def updatePlot(self):
        print "deposition graph updating"
        
        pass
