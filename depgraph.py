# Allison Schubauer and Daisy Hernandez
# Created: 6/06/2013
# Last Updated: 6/13/2013
# For JCAP

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as colors
import matplotlib.cm as cm
#from process_deposition_data import DEP_DATA
import process_deposition_data as pdd
import numpy as np


""" the deposition graph, its axes, and its data """
class DepositionGraph(FigureCanvas):

    def __init__(self, parent="None", width=2, height=2, dpi=120):
        # initialize matplotlib figure
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.figure)
        # let graph expand when window expands
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.initPlotArea()

        # conversion factor is scalar used for changing units
        # maxRate is used for resetting the color scale
        self.convFactor, self.maxRate = 1, 0
        # currentZ is z-position for which this graph is
        #   currently displaying deposition rate data
        # zvars holds all z-values for this experiment
        self.currentZ, self.zvars = None, []
        # used for resetting the color scale
        self.changeScale = False
        # formatted string that represents the units of the data
        self.units = r'$10^{-8}$'+'g/s cm'+r'$^2$'

    """ initializes the graph's data and axes """
    def initPlotArea(self):
        self.xdata, self.ydata, self.ratedata = [], [], []
        self.plot = self.figure.add_subplot(1, 1, 1, adjustable='box', aspect=1)
        self.plot.set_xlim(-50, 50)
        self.plot.set_ylim(-50, 50)
        # keep x and y limits fixed because radius values are fixed
        self.plot.autoscale(enable=False, tight=False)

    """ plots all available data when window is opened """
    def firstPlot(self, zval = None):
        self.currentZ = zval
        # default to first z-value in data file
        if not zval:
            self.currentZ = pdd.DEP_DATA[0][0]
        # keep track of all valid z-values for experiment
        if self.currentZ not in self.zvars:
            self.zvars.append(self.currentZ)
        for z, x, y, rate in pdd.DEP_DATA:
            # save other z-values for user to access later
            if z != self.currentZ:
                if z not in self.zvars:
                    self.zvars.append(z)
                continue
            # otherwise, plot rate on this graph
            self.xdata.append(x)
            self.ydata.append(y)
            modified_rate = rate*self.convFactor
            self.ratedata.append(modified_rate)
            if modified_rate > self.maxRate*self.convFactor:
                self.maxRate = modified_rate
        # holds information about the scale of the colorbar
        self.scalarMap = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=self.maxRate*self.convFactor))
        self.scalarMap.set_array(np.array(self.ratedata))
        # plot all available data and save scatter object for
        #   later deletion
        self.datavis = [self.plot.scatter(self.xdata, self.ydata,
                                         c = self.ratedata, cmap=self.scalarMap.get_cmap(),
                                         marker='o', edgecolor='none', s=60)]
        # initialize colorbar
        self.colorbar = self.figure.colorbar(self.scalarMap, ax = self.plot)
        self.colorbar.set_array(np.array(self.ratedata))
        self.colorbar.autoscale()
        self.colorbar.set_label(self.units)
        self.scalarMap.set_clim(0, self.maxRate*self.convFactor)
        self.scalarMap.changed()
        self.draw()

    """ plots newly-processed data on preexisting graph """
    def updatePlot(self, newData):
        # only plot data corresponding to current z-position
        for z, x, y, rate in [newData]:
            if z!= self.currentZ:
                break
            self.xdata.append(x)
            self.ydata.append(y)
            modified_rate = rate*self.convFactor
            self.ratedata.append(modified_rate)
            # reset colorbar scale if necessary
            if modified_rate > self.maxRate*self.convFactor:
                self.maxRate = modified_rate
                self.changeScale = True
            # add single point to plot
            if not self.changeScale:
                self.datavis += [self.plot.scatter(x, y, c = rate,
                                                 cmap=self.scalarMap.get_cmap(),
                                                 marker='o', edgecolor='none', s=60)]
            else:
                self.rescale()
        
        self.draw()

    """ redraws the graph according to the new color scale
        determined by the new maximum rate value """
    def rescale(self):
        # clear old color values from plot
        for plot in self.datavis:
            plot.remove()
        # reset limits of color scale
        self.scalarMap.set_clim(0, self.maxRate*self.convFactor)
        # plot entire set of data according to new scale
        self.datavis = [self.plot.scatter(self.xdata, self.ydata,
                                         c = self.ratedata,
                                         cmap=self.scalarMap.get_cmap(),
                                         marker='o', edgecolor='none', s=60)]
        # rescale the colorbar
        self.colorbar.draw_all()

    """ reset figure prior to switching z-values """
    def clearPlot(self):
        self.figure.clear()
        self.initPlotArea()
        self.convFactor, self.maxRate = 1, 0
        self.currentZ, self.zvars = None, []
        self.changeScale = False
        self.units = r'$10^{-8}$'+'g/s cm'+r'$^2$'

    """ convert all rate data and change labels on colorbar
        when converting units """
    def convertPlot(self):
        lenOfRateData = len(self.ratedata)
        for rateLoc, (z, x, y, rate) in enumerate(pdd.DEP_DATA[:lenOfRateData]):
            self.ratedata[rateLoc] = rate*self.convFactor
        self.scalarMap.set_clim(0, max(self.ratedata))
        self.colorbar.draw_all()
        self.draw()
