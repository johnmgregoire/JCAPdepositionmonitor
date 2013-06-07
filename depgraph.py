# Allison Schubauer and Daisy Hernandez
# Created: 6/06/2013
# Last Updated: 6/06/2013
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
        self.zdata = []

    def initPlotArea(self):
        self.xdata = []
        self.ydata = []
        self.ratedata = []
        
        self.plot = self.figure.add_subplot(1, 1, 1, adjustable='box', aspect=1,
                                            projection = '3d')
        self.plot.set_xlim(-50, 50)
        self.plot.set_ylim(-50, 50)
        self.plot.set_zlim(2.8, 3.8)
        self.plot.autoscale(enable=False, tight=False)
        #self.plot.autoscale_view(tight=False, scalex=False, scaley=False,
                                 #scalez=True)

    def firstPlot(self):
        for z, x, y, rate in DEP_DATA:
            self.zdata.append(z)
            self.xdata.append(x)
            self.ydata.append(y)
            modified_rate = rate*self.convFactor
            self.ratedata.append(modified_rate)
        self.scalarMap = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=max(self.ratedata)))
        self.scalarMap.set_array(np.array(self.ratedata))
        self.datavis = self.plot.scatter(self.xdata, self.ydata, zs=self.zdata, zdir='z',
                                         c = self.ratedata, cmap=self.scalarMap.get_cmap(),
                                         marker='o', edgecolor='none', s=60)
        self.colorbar = self.figure.colorbar(self.scalarMap, ax = self.plot)
        self.colorbar.set_array(np.array(self.ratedata))
        self.colorbar.autoscale()
        self.scalarMap.set_colorbar(self.colorbar, self.plot)
        self.colorbar.set_label(r'$10^{-8}$'+'g/s cm'+r'$^2$')

    def updatePlot(self, newData):
        for z, x, y, rate in newData:
            self.zdata.append(z)
            self.xdata.append(x)
            self.ydata.append(y)
            modified_rate = rate*self.convFactor
            self.ratedata.append(modified_rate)
        print "deposition graph updating"
        self.datavis.remove()
        self.datavis = self.plot.scatter(self.xdata, self.ydata, zs=self.zdata,
                                         c = self.ratedata,
                                         cmap=self.scalarMap.get_cmap(),
                                         marker='o', edgecolor='none', s=60)
        self.scalarMap.set_clim(0, max(self.ratedata))
        self.colorbar.draw_all()
        self.draw()

    def convertPlot(self):
        print "converting plot", self.convFactor
        lenOfRateData = len(self.ratedata)
        print "Before conversion", self.ratedata
        for rateLoc, (x, y, rate) in enumerate(DEP_DATA[:lenOfRateData]):
            modified_rate = rate*self.convFactor
            self.ratedata[rateLoc] = modified_rate
        print "After conversion", self.ratedata
        self.scalarMap.set_clim(0, max(self.ratedata))
        self.colorbar.draw_all()
        self.draw()
