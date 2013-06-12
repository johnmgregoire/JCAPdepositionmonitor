# Allison Schubauer and Daisy Hernandez
# Created: 6/06/2013
# Last Updated: 6/11/2013
# For JCAP

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as colors
import matplotlib.cm as cm
from process_deposition_data import DEP_DATA
import numpy as np


"""creates the depotion graph"""
class DepositionGraph(FigureCanvas):

    def __init__(self, parent="None", width=2, height=2, dpi=120):
        # initialize matplotlib figure
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.figure)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.initPlotArea()

        # maxRate used for the reseting the color scale
        # currentZ for which z one is currently viewing
        # zvars ia all the possible z's
        self.convFactor, self.maxRate = 1, 0
        self.currentZ, self.zvars = None, []
        # for the reset color map
        self.changeScale = False
        # formatted string that represents the units of the data
        self.units = r'$10^{-8}$'+'g/s cm'+r'$^2$'

    def initPlotArea(self):
        self.xdata, self.ydata, self.ratedata = [], [], []   
        self.plot = self.figure.add_subplot(1, 1, 1, adjustable='box', aspect=1)
        self.plot.set_xlim(-50, 50)
        self.plot.set_ylim(-50, 50)
        self.plot.autoscale(enable=False, tight=False)

    def firstPlot(self, zval = None):
        self.currentZ = zval
        # if zval is None, we need to get one from DEP_Data
        if not zval:
            self.currentZ = DEP_DATA[0][0]
        if self.currentZ not in self.zvars:
            self.zvars.append(self.currentZ)
        # loop and get all the z's the we can find in DEP_DATA
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

    """Same spirit as first plost, however, it only plots one point"""
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
        # remove all the points in the scatterplot
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
        self.convFactor, self.maxRate = 1, 0
        self.currentZ, self.zvars = None, []
        self.changeScale = False
        self.units = r'$10^{-8}$'+'g/s cm'+r'$^2$'

    def convertPlot(self):
        lenOfRateData = len(self.ratedata)
        for rateLoc, (z, x, y, rate) in enumerate(DEP_DATA[:lenOfRateData]):
            self.ratedata[rateLoc] = rate*self.convFactor
        self.scalarMap.set_clim(0, max(self.ratedata))
        self.colorbar.draw_all()
        self.draw()
