# Allison Schubauer and Daisy Hernandez
# Created: 6/06/2013
# Last Updated: 6/07/2013
# For JCAP

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
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
        self.convFactor = 1
        self.currentZ = None
        self.zvars = []
        self.maxRate = 0
        self.changeScale = False
        # formatted string that represents the units of the data
        self.units = r'$10^{-8}$'+'g/s cm'+r'$^2$'

    def initPlotArea(self):
        self.xdata = []
        self.ydata = []
        self.ratedata = []      
        self.plot = self.figure.add_subplot(1, 1, 1, adjustable='box', aspect=1)
        self.plot.set_xlim(-50, 50)
        self.plot.set_ylim(-50, 50)
        self.plot.autoscale(enable=False, tight=False)

    def firstPlot(self, zval = None):
        self.currentZ = zval
        if not zval:
            self.currentZ = DEP_DATA[0][0]
        if self.currentZ not in self.zvars:
            self.zvars.append(self.currentZ)
        #print 'currentZ:', self.currentZ
        for i, (z, x, y, rate) in enumerate(DEP_DATA):
            if z != self.currentZ:
                if z not in self.zvars:
                    self.zvars.append(z)
                continue
            self.xdata.append(x)
            self.ydata.append(y)
            modified_rate = rate*self.convFactor
            self.ratedata.append(modified_rate)
            if modified_rate > self.maxRate:
                self.maxRate = modified_rate
        self.scalarMap = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=self.maxRate))
        self.scalarMap.set_array(np.array(self.ratedata))
        self.datavis = [self.plot.scatter(self.xdata, self.ydata,
                                         c = self.ratedata, cmap=self.scalarMap.get_cmap(),
                                         marker='o', edgecolor='none', s=60)]
        self.colorbar = self.figure.colorbar(self.scalarMap, ax = self.plot)
        self.colorbar.set_array(np.array(self.ratedata))
        self.colorbar.autoscale()
        self.colorbar.set_label(self.units)
        self.draw()

    def updatePlot(self, newData):
        for z, x, y, rate in [newData]:
            if z!= self.currentZ:
                break
            self.xdata.append(x)
            self.ydata.append(y)
            modified_rate = rate*self.convFactor
            self.ratedata.append(modified_rate)
            if modified_rate > self.maxRate:
                self.maxRate = modified_rate
                self.changeScale = True
            if not self.changeScale:
                self.datavis += [self.plot.scatter(x, y, c = rate,
                                                 cmap=self.scalarMap.get_cmap(),
                                                 marker='o', edgecolor='none', s=60)]
            else:
                self.rescale()
        
        self.draw()

    def rescale(self):
        for plot in self.datavis:
            plot.remove()
        self.scalarMap.set_clim(0, self.maxRate)
        self.datavis = [self.plot.scatter(self.xdata, self.ydata,
                                         c = self.ratedata,
                                         cmap=self.scalarMap.get_cmap(),
                                         marker='o', edgecolor='none', s=60)]
        self.colorbar.draw_all()

    def clearPlot(self):
        self.figure.clear()
        self.initPlotArea()
        self.convFactor = 1
        self.currentZ = None
        self.zvars = []
        self.maxRate = 0
        self.changeScale = False
        self.units = r'$10^{-8}$'+'g/s cm'+r'$^2$'

    def convertPlot(self):
        print "converting plot", self.convFactor
        lenOfRateData = len(self.ratedata)
        print "Before conversion", self.ratedata
        for rateLoc, (z, x, y, rate) in enumerate(DEP_DATA[:lenOfRateData]):
            modified_rate = rate*self.convFactor
            self.ratedata[rateLoc] = modified_rate
        print "After conversion", self.ratedata
        self.scalarMap.set_clim(0, max(self.ratedata))
        self.colorbar.draw_all()
        self.draw()
