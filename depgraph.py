# Allison Schubauer and Daisy Hernandez
# Created: 6/06/2013
# Last Updated: 6/14/2013
# For JCAP

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as colors
import matplotlib.cm as cm
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
        # set up the axes and their properties
        self.initPlotArea()
    
        # conversion factor is scalar used for changing units
        # maxRate is used for resetting the color scale
        self.convFactor, self.maxRate = 1, 0
        # currentZ is the z-position for which the graph
        #   is displaying deposition rate data
        # zvars holds all z-values for this experiment
        self.currentZ, self.zvars = None, []
        # formatted string that represents the units of the data
        #   (defaults to 10^-8 g/(s cm^2))
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
            # keep maxRate updated if we need to reset the scale
            if modified_rate > self.maxRate:
                self.maxRate = modified_rate
        # holds information about the scale of the colorbar
        self.scalarMap = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=self.maxRate))
        self.scalarMap.set_array(np.array(self.ratedata))
        # plot all available data and save scatter object for later deletion
        self.datavis = self.plot.scatter(self.xdata, self.ydata,
                                         c = self.ratedata, cmap=self.scalarMap.get_cmap(),
                                         marker='o', edgecolor='none', s=60)
        # initialize colorbar and set its properties
        self.colorbar = self.figure.colorbar(self.scalarMap, ax = self.plot)
        self.colorbar.set_array(np.array(self.ratedata))
        self.colorbar.autoscale()
        self.colorbar.set_label(self.units)
        self.scalarMap.set_clim(0, self.maxRate)
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
            if modified_rate > self.maxRate:
                self.maxRate = modified_rate
            # redraw plot with new point
            self.rescale()
            self.draw()

    """ NOTE: We redraw the entire plot every time a new point comes in
        rather than simply adding the point to the preexisting plot because
        matplotlib was often unable to associate the new point with the
        existing colormap, resulting in a lot of dark blue dots (representing
        0 on the scale, as far as we could tell) on the graph, which the user
        would have to correct manually by clicking 'Reset Colors.'  We decided
        that it was worth a negligible amount of extra memory to provide the
        user with a less frustrating experience. """

    """ redraws the graph with new data and new color scale
        (if maxRate has changed) """
    def rescale(self):
        # clear old color values from plot
        self.datavis.remove()
        # reset limits of color scale
        self.scalarMap.set_clim(0, self.maxRate)
        # plot entire set of data according to new scale
        self.datavis = self.plot.scatter(self.xdata, self.ydata,
                                         c = self.ratedata,
                                         cmap=self.scalarMap.get_cmap(),
                                         marker='o', edgecolor='none', s=60)
        # rescale the colorbar
        self.colorbar.draw_all()

    """ reset figure prior to switching z-values """
    def clearPlot(self):
        self.figure.clear()
        self.initPlotArea()
        self.convFactor, self.maxRate = 1, 0
        self.currentZ, self.zvars = None, []
        self.units = r'$10^{-8}$'+'g/s cm'+r'$^2$'

    """ convert rate data and change label on colorbar when converting units """
    def convertPlot(self):
        # used to make sure we got all the data values for the given z
        lenOfRateData = len(self.ratedata)
        currLocation = 0
        for z, x, y, rate in pdd.DEP_DATA:
            # convert only those rate with the desired z
            if currLocation < lenOfRateData and z == self.currentZ:
                self.ratedata[currLocation] = rate*self.convFactor
                currLocation +=1 
            elif currLocation >= lenOfRateData:
                break
        # get new maxRate with max function to prevent errors due to precision
        self.maxRate = max(self.ratedata)
        self.scalarMap.set_clim(0, self.maxRate)
        self.scalarMap.changed()
        self.colorbar.draw_all()
        self.draw()

    """ called when user clicks on graph to display (x, y) data """
    def onclick(self,event):
            try:
                xcorr = event.xdata
                ycorr = event.ydata
            except TypeError:
                pass
