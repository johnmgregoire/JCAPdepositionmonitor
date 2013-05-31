# Allison Schubauer and Daisy Hernandez
# Created: 5/23/2013
# Last Updated: 5/31/2013
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

""" widget to represent an auto-updating graph """
class Graph(FigureCanvas):

    """ sets up Figure object, plot, and auto-updating timer """
    def __init__(self, parent="None", width=3, height=2, dpi=80,
                 xvarname="None", yvarname="None"):
        self.auto = True
        self.timeWindow = 0
        self.hasRightAxis = False
        self.xvar = xvarname
        self.yvarL = yvarname
        self.yvarR = None
        self.colNum = [self.getCol("Date"),self.getCol(self.xvar),self.getCol(self.yvarL), None]
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
        self.axes.set_ylabel(self.yvarL)
        self.axes.xaxis_date()
        self.figure.autofmt_xdate()
        self.time_format = matplotlib.dates.DateFormatter('%m/%d/%y %H:%M:%S')
        self.axes.xaxis.set_major_formatter(self.time_format)
        self.axes.set_ylabel(self.yvarL)

        self.firstPlot("left", "bo")
        #self.updatePlot()

    """function that does the first plotting of the graph"""
    def firstPlot(self,nameOfAxis, lineDes):

        list_of_times = []
        theAxes = None
        theYvar = None

        if nameOfAxis == "left":
            (theAxes,theYvar) = (self.axes,self.yvarL)
            
        elif nameOfAxis == "right":
            (theAxes,theYvar) = (self.rightAxes,self.yvarR)
            

        ydata = copy.deepcopy(DATA_DICT.get(theYvar))
        time_array = copy.deepcopy(DATA_DICT.get(self.xvar))
        date_array = copy.deepcopy(DATA_DICT.get("Date"))
        
        for index in range(len(time_array)):
            full_time = date_array[index] + " " + time_array[index]
            formatted_time = dateObjFloat(full_time)
            list_of_times += [formatted_time]
            
        timeToPlot = matplotlib.dates.date2num(list_of_times)

        self.timeFrame()

        try:
            theAxes.plot_date(timeToPlot, ydata, lineDes, label = theYvar)
            
        except ValueError:
            print "size of time_array - dictionary " + str(len(time_array))
            print "size of date_array - dictionary " + str(len(date_array))
            print "length of list_of_times: " + str(len(list_of_times))
            print "size of x array: " + str(len(timeToPlot))
            print "size of y array: " + str(len(ydata))
            print "column not updated: " + theYvar
            pass

    def updatePlot(self,row):
        time_value = dateObjFloat(row[self.colNum[0]] + " " + row[self.colNum[1]])
        self.axes.plot_date(time_value, row[self.colNum[2]], "bo")

        if self.hasRightAxis:
            self.rightAxes.plot_date(time_value, row[self.colNum[3]], "ro")
            
        self.timeFrame()
        
        pass
        
##    """ function that updates plot every second """
##    def updatePlot(self,row):
##        ydata = copy.deepcopy(DATA_DICT.get(self.yvarL))
##        if self.hasRightAxis:
##            yrightdata = copy.deepcopy(DATA_DICT.get(self.yvarR))
##        list_of_times = []
##        time_array = copy.deepcopy(DATA_DICT.get(self.xvar))
##        date_array = copy.deepcopy(DATA_DICT.get("Date"))
##        for index in range(len(time_array)):
##            full_time = date_array[index] + " " + time_array[index]
##            formatted_time = dateObjFloat(full_time)
##            list_of_times += [formatted_time]
##        timeToPlot = matplotlib.dates.date2num(list_of_times)
##        try:
##            del self.axes.lines[0]
##        except IndexError:
##            pass
##        
##        try:
##            self.axes.plot_date(timeToPlot, ydata, label = self.yvarL)
##            if not self.auto:
##                currTime = time.time()
##                rightLim = dateObj(currTime)
##                leftLim = dateObj(currTime - self.timeWindow)
##                self.setXlim(amin=leftLim, amax=rightLim)
##        except ValueError:
##            print "size of time_array - DICT " + str(len(time_array))
##            print "size of date_array - DICT " + str(len(date_array))
##            print "length of list_of_times: " + str(len(list_of_times))
##            print "size of x array: " + str(len(timeToPlot))
##            print "size of y array: " + str(len(ydata))
##            print "column not updated: " + self.yvarL
##            pass
##
##        if self.hasRightAxis:
##            try:
##                del self.rightAxes.lines[0]
##            except IndexError:
##                pass
##            try:
##                self.rightAxes.plot_date(timeToPlot, yrightdata, "ro", label = self.yvarR) 
##            except ValueError:
##                print "size of x array: " + str(len(timeToPlot))
##                print "size of y array: " + str(len(yrightdata))
##                print "column not updated: " + self.yvarR
##                pass
##            #add legend to graph
##            linesL, labelsL = self.axes.get_legend_handles_labels()
##            linesR, labelsR = self.rightAxes.get_legend_handles_labels()
##            self.rightAxes.legend(linesL + linesR, labelsL + labelsR, loc=2, prop={"size":"small"})
##
##        self.draw()

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
        self.yvarR = rightvar
        self.colNum[3] = self.getCol(self.yvarR)
        self.hasRightAxis = True
        #self.rightAxes = self.figure.add_subplot(111, sharex=self.axes, frameon=False)
        self.rightAxes = self.axes.twinx()
        self.rightAxes.yaxis.tick_right()
        self.rightAxes.yaxis.set_label_position("right")
        self.rightAxes.set_ylabel(self.yvarR)
        self.rightAxes.xaxis.set_major_formatter(self.time_format)
        self.rightAxes.get_xaxis().set_visible(False)
        self.firstPlot("right", "ro")
        #add legend to graph
        linesL, labelsL = self.axes.get_legend_handles_labels()
        linesR, labelsR = self.rightAxes.get_legend_handles_labels()
        self.rightAxes.legend(linesL + linesR, labelsL + labelsR, loc=2, prop={"size":"small"})

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
