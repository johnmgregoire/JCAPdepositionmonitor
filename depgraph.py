# Allison Schubauer and Daisy Hernandez
# Created: 6/06/2013
# Last Updated: 6/06/2013
# For JCAP

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pylab

class DepositionGraph(FigureCanvas):

    def __init__(self, parent="None", width=2, height=2,
                 dpi=100):
        # initialize matplotlib figure
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.figure)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.initPlot()

    def initPlot(self):
        self.plot = self.figure.add_subplot(111)
        # comment this back in when data processor is connected
        #self.plot.scatter(x, y, c=cs, marker='o', edgecolor='none', s=60)
        self.plot.set_aspect(1.)
        self.figure.colorbar()
