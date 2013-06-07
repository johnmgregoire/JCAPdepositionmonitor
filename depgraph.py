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
        self.initPlotArea()

    def initPlotArea(self):
        self.xdata = []
        self.ydata = []
        self.ratedata = []
        
        self.plot = self.figure.add_subplot(1, 1, 1, adjustable='box', aspect=1)
        self.plot.set_xlim(-60, 60)
        self.plot.set_ylim(-60, 60)
        self.plot.autoscale(enable=False, tight=False)

    def firstPlot(self):
        for x, y, rate in DEP_DATA:
            self.xdata.append(x)
            self.ydata.append(y)
            self.ratedata.append(rate)
        self.scalarMap = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=max(self.ratedata)))
        self.scalarMap.set_array(np.array(self.ratedata))
        self.datavis = self.plot.scatter(self.xdata, self.ydata, c = self.ratedata,
                          cmap=self.scalarMap.get_cmap(), marker='o', edgecolor='none', s=60)
        self.colorbar = self.figure.colorbar(self.scalarMap, ax = self.plot)
        self.colorbar.set_array(np.array(self.ratedata))
        self.colorbar.autoscale()
        self.scalarMap.set_colorbar(self.colorbar, self.plot)

    def updatePlot(self, newData):
        for x, y, rate in newData:
            self.xdata.append(x)
            self.ydata.append(y)
            self.ratedata.append(rate)
        print "deposition graph updating"
        self.datavis.remove()
        self.datavis = self.plot.scatter(self.xdata, self.ydata, c = self.ratedata,
                          cmap=self.scalarMap.get_cmap(), marker='o', edgecolor='none', s=60)
        self.scalarMap.set_clim(0, max(self.ratedata))
        self.colorbar.draw_all()
        self.draw()
