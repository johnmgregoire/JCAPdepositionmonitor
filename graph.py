# Allison Schubauer and Daisy Hernandez
# Created: 5/23/2013
# Last Updated: 6/3/2013
# For JCAP

import datetime
import time
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pylab import *
from datareader import *
from date_helpers import *
import copy
from yvariable import *


""" widget to represent an auto-updating graph """
class Graph(FigureCanvas):

    """ sets up Figure object, plot, and auto-updating timer """
    def __init__(self, parent="None", width=3, height=2, dpi=80,
                 xvarname="None", yvarname="None"):
        self.auto = True
        self.timeWindow = 0
        self.hasRightAxis = False
        self.legend = None
        self.xvar = xvarname
        self.yvarsL = [YVariable(varName = yvarname,
                                   columnNumber = self.getCol(yvarname), color = "bo")]
        self.colNums = [self.getCol("Date"),self.getCol(self.xvar)]
        self.figure = Figure(figsize=(width, height), dpi=dpi)

        FigureCanvas.__init__(self, self.figure)
        # Graph will have a parent widget if contained in a layout
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.initPlot()
        
        # clicking on graph gives x and y coordinates
        #   (not enabled when right y axis is present)
        self.figure.canvas.mpl_connect('button_press_event', self.onclick)
        
        #self.draw()
        
    """ draws and labels axes """
    def initPlot(self):
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel(self.xvar)
        self.axes.set_ylabel(self.yvarsL[0].varName)
        self.axes.xaxis_date()
        self.figure.autofmt_xdate()
        self.time_format = matplotlib.dates.DateFormatter('%m/%d/%y %H:%M:%S')
        self.axes.xaxis.set_major_formatter(self.time_format)
        self.axes.set_ylabel(self.yvarsL[0].varName)

        # Set them as their axis
        self.yvarsL[0].axis = self.axes
        
        self.firstPlot(self.yvarsL[0])
        #self.updatePlot()

    """function that does the first plotting of the graph"""
    def firstPlot(self, yvarIns):

        list_of_times = []
        theAxes = yvarIns.axis
        theYvar = yvarIns.varName            
            

        ydata = copy.deepcopy(DATA_DICT.get(theYvar))
        time_array = copy.deepcopy(DATA_DICT.get(self.xvar))
        date_array = copy.deepcopy(DATA_DICT.get("Date"))
        
        for index in range(len(time_array)):
            full_time = date_array[index] + " " + time_array[index]
            formatted_time = dateObjFloat(full_time)
            list_of_times += [formatted_time]
            
        timeToPlot = matplotlib.dates.date2num(list_of_times)

        try:
            theAxes.plot_date(timeToPlot, ydata, yvarIns.color, label = theYvar)
            
            self.timeFrame()
            
        except ValueError:
            print "size of time_array - dictionary " + str(len(time_array))
            print "size of date_array - dictionary " + str(len(date_array))
            print "length of list_of_times: " + str(len(list_of_times))
            print "size of x array: " + str(len(timeToPlot))
            print "size of y array: " + str(len(ydata))
            print "column not updated: " + theYvar
            pass

    def updatePlot(self,row):
        time_value = dateObjFloat(row[self.colNums[0]] + " " + row[self.colNums[1]])
        self.axes.plot_date(time_value, row[self.yvarsL[0].columnNumber], self.yvarsL[0].color)

        if self.hasRightAxis:
            self.rightAxes.plot_date(time_value, row[self.yvarsR[0].columnNumber], self.yvarsR[0].color)
            
        
        pass


    def timeFrame(self):
            if not self.auto:
                currTime = time.time()
                rightLim = dateObj(currTime)
                leftLim = dateObj(currTime - self.timeWindow)
                self.setXlim(amin=leftLim, amax=rightLim)


    def getCol(self,colName):
        theCol = [k for k, v in DATA_HEADINGS.iteritems() if v == colName]
        return theCol[0]

    def addRightAxis(self, rightvar):
        if self.hasRightAxis:
            self.figure.delaxes(self.rightAxes)
        self.hasRightAxis = True
        #self.rightAxes = self.figure.add_subplot(111, sharex=self.axes, frameon=False)
        self.rightAxes = self.axes.twinx()
        self.rightAxes.yaxis.tick_right()
        self.rightAxes.yaxis.set_label_position("right")
        self.rightAxes.set_ylabel(rightvar)
        self.rightAxes.xaxis.set_major_formatter(self.time_format)
        self.rightAxes.get_xaxis().set_visible(False)

        # Saving the rights information 
        self.yvarsR = [YVariable(varName = rightvar, axis = self.rightAxes,
                                 columnNumber = self.getCol(rightvar), color = "ro")]
        self.firstPlot(self.yvarsR[0])
        
        self.addLegend()

    def addVarToAxis(self, varString, axis="left"):
        newVar = YVariable(varName = varString, axis = self.axes,
                                      columnNumber = self.getCol(varString), color = "go")
        if axis == "left":
            self.axes.get_yaxis().get_label().set_visible(False)
            self.yvarsL += [newVar]
        if axis == "right":
            newVar.axis = self.rightAxes
            newVar.color = "yo"
            self.rightAxes.get_yaxis().get_label().set_visible(False)
            self.yvarsR += [newVar]
        self.firstPlot(newVar)

        self.addLegend()

    def addLegend(self):
        if self.legend:
            self.legend.set_visible(False)
        linesL, labelsL = self.axes.get_legend_handles_labels()
        if self.hasRightAxis:
            linesR, labelsR = self.rightAxes.get_legend_handles_labels()
            self.legend = self.rightAxes.legend(linesL + linesR, labelsL + labelsR, loc=2, prop={"size":"small"})
        else:
            self.legend = self.axes.legend(loc=2, prop={"size":"small"})
        self.legend.draggable(state = True)
        
    def setXlim(self, amin=None, amax=None):
        self.axes.set_xlim(left=amin, right=amax)

    def setYlim(self, amin=None, amax=None):
        self.axes.set_ylim(bottom=amin, top=amax)

    def setRYlim(self, amin=None, amax=None):
        self.rightAxes.set_ylim(bottom=amin, top=amax)

    def clearPlot(self):
        self.figure.clf()

    def onclick(self,event):
        print "clicked graph"
        if not self.hasRightAxis:
            try:
                datetime_date = matplotlib.dates.num2date(event.xdata)
                formatted_xdate = datetime_date.strftime("%m/%d/%Y %H:%M:%S")
                print 'xdata=%s, ydata=%f'%(formatted_xdate, event.ydata)
            except TypeError:
                pass
