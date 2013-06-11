# Allison Schubauer and Daisy Hernandez
# Created: 6/06/2013
# Last Updated: 6/11/2013
# For JCAP

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D # TODO: delete after pull
import matplotlib.colors as colors
import matplotlib.cm as cm
from process_deposition_data import DEP_DATA

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
        self.z1 = None
        self.z2 = None
        self.z2index = None
        self.zvar = None
        self.maxRate = 0
        self.changeScale = False
        # formatted string that represents the units of the data
        self.units = r'$10^{-8}$'+'g/s cm'+r'$^2$'

    def initPlotArea(self):
        self.xdata = []
        self.ydata = []
        self.ratedata = []
        
        self.plot = self.figure.add_subplot(1, 1, 1, adjustable='box', aspect=1,
                                            projection = '3d')
        self.plot.set_xlim(-50, 50)
        self.plot.set_ylim(-50, 50)
        #self.plot.set_zlim(2.8, 3.8)
        #self.plot.autoscale(enable=False, tight=False)
        self.plot.autoscale_view(tight=False, scalex=False, scaley=False,
                                 scalez=True)

    def firstPlot(self):
        self.z1 = DEP_DATA[0][0]
        self.zvar = self.z1
        for i, (z, x, y, rate) in enumerate(DEP_DATA):
            if  not self.z2 and z != self.z1:
                self.z2 = z
                self.zvar = self.z2
                self.z2index = i
            self.xdata.append(x)
            self.ydata.append(y)
            modified_rate = rate*self.convFactor
            self.ratedata.append(modified_rate)
            if modified_rate > self.maxRate:
                self.maxRate = modified_rate
        self.scalarMap = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=self.maxRate))
        self.scalarMap.set_array(np.array(self.ratedata))
        zarr = np.ones(len(self.xdata))*self.z1
        if self.z2:
            for i in range(self.z2index, len(zarr)):
                zarr[i] = self.z2
        self.datavis = self.plot.scatter(self.xdata, self.ydata, zs=zarr,
                                         c = self.ratedata, cmap=self.scalarMap.get_cmap(),
                                         marker='o', edgecolor='none', s=60,
                                         alpha=1)
        self.colorbar = self.figure.colorbar(self.scalarMap, ax = self.plot)
        self.colorbar.set_array(np.array(self.ratedata))
        self.colorbar.autoscale()
        self.scalarMap.set_colorbar(self.colorbar, self.plot)
        self.colorbar.set_label(self.units)

    def updatePlot(self, newData):
        for z, x, y, rate in newData:
            if not self.z1:
                self.firstPlot()
            elif z != self.zvar:
                self.z2 = z
                self.z2index = len(self.xdata)
                self.zvar = self.z2
                # get center point from dictionary
                center = DEP_DATA[-3]
                print 'center:', center
                self.xdata.append(center[1])
                self.ydata.append(center[2])
                modified_rate = center[3]*self.convFactor
                self.ratedata.append(modified_rate)
            self.xdata.append(x)
            self.ydata.append(y)
            modified_rate = rate*self.convFactor
            self.ratedata.append(modified_rate)
            if modified_rate > self.maxRate:
                self.maxRate = modified_rate
                self.changeScale = True
        print "deposition graph updating"
        self.datavis.remove()
        if not self.changeScale:
            self.datavis = self.plot.scatter(self.xdata[-2:], self.ydata[-2:], zs=self.zvar,
                                             c = self.ratedata[-2:],
                                             cmap=self.scalarMap.get_cmap(),
                                             marker='o', edgecolor='none', s=60)
        else:
            self.scalarMap.set_clim(0, self.maxRate)
            zarr = np.ones(len(self.xdata))*self.z1
            if self.z2:
                for i in range(self.z2index, len(zarr)):
                    zarr[i] = self.z2
            self.datavis = self.plot.scatter(self.xdata, self.ydata, zs=zarr,
                                             c = self.ratedata,
                                             cmap=self.scalarMap.get_cmap(),
                                             marker='o', edgecolor='none', s=60)
            self.colorbar.draw_all()
        self.draw()

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
