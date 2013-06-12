# Allison Schubauer and Daisy Hernandez
# Created: 5/23/2013
# Last Updated: 6/12/2013
# For JCAP

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pylab import matplotlib
import sys
import date_helpers
import yvariable
import copy
import itertools
import time
from dictionary_helpers import *


""" widget to represent an auto-updating graph """
class Graph(FigureCanvas):

    """ sets up Figure object and plot """
    def __init__(self, parent="None", width=3, height=2, dpi=80,
                 xvarname="None", yvarname="None"):
        self.auto = True
        self.timeWindow = 0
        self.hasRightAxis = False
        self.legendL = None
        self.xvar = xvarname
        # holds matplotlib keywords for color of plots
        self.colors = itertools.cycle(["g","c","m","y","k","b","r"])
        # put first y-var into list of y-vars on left axis
        self.yvarsL = [yvariable.YVariable(varName = yvarname,
                                   columnNumber = getCol(yvarname), color = "b")]
        # used to access date/time data for formatting
        #   and displaying on the x-axis
        self.colNums = [getCol("Date"),getCol(self.xvar)]
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

        # Assign first y variable to left-hand axis
        self.yvarsL[0].axis = self.axes
        
        self.firstPlot(self.yvarsL[0])

    """ plots initial data for a given y-var on the graph """
    def firstPlot(self, yvarIns):
        list_of_times = []
        theAxes = yvarIns.axis
        theYvar = yvarIns.varName            
            
        ydata = copy.deepcopy(DATA_DICT.get(theYvar))
        time_array = copy.deepcopy(DATA_DICT.get(self.xvar))
        date_array = copy.deepcopy(DATA_DICT.get("Date"))
        
        for index in range(len(time_array)):
            full_time = date_array[index] + " " + time_array[index]
            formatted_time = date_helpers.dateObjFloat(full_time)
            list_of_times += [formatted_time]
            
        timeToPlot = matplotlib.dates.date2num(list_of_times)

        # If reader is still reading, DATA_DICT is changing,
        #   and it is possible for timeToPlot to be a different
        #   length than ydata.  In that case, we can wait for
        #   DATA_DICT to update and try again.
        try:
            theAxes.plot_date(timeToPlot, ydata, markerfacecolor=yvarIns.color, label = theYvar,
                              markeredgecolor=yvarIns.color)   
            self.timeFrame()    
        except ValueError:
            time.sleep(0.5)
            firstPlot(self, yvarIns)

    """ adds new data to graph whenever reader sends new row """
    def updatePlot(self, row):
        # turn date/time strings into time objects
        time_value = date_helpers.dateObjFloat(row[self.colNums[0]] + " " + row[self.colNums[1]])
        # plot new point for all left-hand y-vars
        for i in range(len(self.yvarsL)):
            self.axes.plot_date(time_value, row[self.yvarsL[i].columnNumber],
                                markerfacecolor=self.yvarsL[i].color,
                                markeredgecolor=self.yvarsL[i].color)
        # plot new point for all right-hand y-vars
        if self.hasRightAxis:
            for i in range(len(self.yvarsR)):
                self.rightAxes.plot_date(time_value, row[self.yvarsR[i].columnNumber],
                                         markerfacecolor=self.yvarsR[i].color,
                                         markeredgecolor=self.yvarsR[i].color)

    """ resets the x-axis limits when specific time window is selected """
    def timeFrame(self):
            if not self.auto:
                currTime = time.time()
                rightLim = date_helpers.dateObj(currTime)
                leftLim = date_helpers.dateObj(currTime - self.timeWindow)
                self.setXlim(amin=leftLim, amax=rightLim)

    """ initializes the right-hand y-axis and adds the first variable """
    def addRightAxis(self, rightvar):
        # replace old right-hand axis
        if self.hasRightAxis:
            self.figure.delaxes(self.rightAxes)
        self.hasRightAxis = True
        # share x-axis with left-hand y-axis
        self.rightAxes = self.axes.twinx()
        self.rightAxes.yaxis.tick_right()
        self.rightAxes.yaxis.set_label_position("right")
        self.rightAxes.set_ylabel(rightvar)
        self.rightAxes.xaxis.set_major_formatter(self.time_format)
        self.rightAxes.get_xaxis().set_visible(False)

        # save the right-hand axis information 
        self.yvarsR = [yvariable.YVariable(varName = rightvar, axis = self.rightAxes,
                                 columnNumber = getCol(rightvar), color = "r")]
        self.firstPlot(self.yvarsR[0])

        # add legend if 3 or more variables on same plot
        if len(self.yvarsL) > 1:
            self.addLegends()

    """ adds another variable to the specified y-axis """
    def addVarToAxis(self, varString, axis="left"):
        newVar = yvariable.YVariable(varName = varString, axis = self.axes,
                                      columnNumber = getCol(varString), color = self.colors.next())
        if axis == "left":
            self.axes.get_yaxis().get_label().set_visible(False)
            self.yvarsL += [newVar]
        elif axis == "right":
            newVar.axis = self.rightAxes
            self.rightAxes.get_yaxis().get_label().set_visible(False)
            self.yvarsR += [newVar]
        self.firstPlot(newVar)
        self.addLegends()

    """ adds left-hand and right-hand axis legends """
    def addLegends(self):
        # remove old legend if there is already one in place
        if self.legendL:
            self.legendL.set_visible(False)
        linesL, labelsL = self.axes.get_legend_handles_labels()
        if self.hasRightAxis:
            linesR, labelsR = self.rightAxes.get_legend_handles_labels()
            # place left-hand legend in upper left corner
            self.legendL = self.rightAxes.legend(linesL, labelsL, loc=2,
                                                 title="Left", prop={"size":"small"})
            # place right-hand legend in upper right corner
            self.legendR = self.rightAxes.legend(linesR, labelsR, loc=1,
                                                 title = "Right", prop={"size":"small"})
            # add left-hand legend to upper Axes object so
            #   it can be manipulated
            self.rightAxes.add_artist(self.legendL)
            self.legendL.draggable(state = True)
            self.legendR.draggable(state = True)
        else:
            self.legendL = self.axes.legend(linesL, labelsL, loc=2,
                                title="Left", prop={"size":"small"})
            self.legendL.draggable(state = True)

    """ called when user specifies a time window to display """     
    def setXlim(self, amin=None, amax=None):
        self.axes.set_xlim(left=amin, right=amax)

    """ called when user specifies left-hand y-axis limits """
    def setYlim(self, amin=None, amax=None):
        self.axes.set_ylim(bottom=amin, top=amax)

    """ called when user specifies right-hand y-axis limits """
    def setRYlim(self, amin=None, amax=None):
        self.rightAxes.set_ylim(bottom=amin, top=amax)

    """ called when new graph is selected for window """
    def clearPlot(self):
        self.figure.clf()

    """ called when user clicks on graph to display (x, y) data """
    def onclick(self,event):
        print "clicked graph"
        if not self.hasRightAxis:
            try:
                datetime_date = matplotlib.dates.num2date(event.xdata)
                formatted_xdate = datetime_date.strftime("%m/%d/%Y %H:%M:%S")
                print 'xdata=%s, ydata=%f'%(formatted_xdate, event.ydata)
            except TypeError:
                pass
