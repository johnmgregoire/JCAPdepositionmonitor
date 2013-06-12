# Allison Schubauer and Daisy Hernandez
# Created: 6/5/2013
# Last Updated: 6/12/2013
# For JCAP

import numpy as np
from PyQt4 import QtCore, QtGui
import depgraph
from process_deposition_data import DEP_DATA
from elements import ELEMENTS
from fractions import Fraction
import re
import sys

class DepositionWindow(QtGui.QMainWindow):

    def __init__(self):
        super(DepositionWindow, self).__init__()

        # Lmnts is a dictionary to hold the information of the
        # composition it was given.
        self.Lmnts, self.density = {}, None
        self.initUI()

    """ draws the user interface of the window """
    def initUI(self):
        # set window size and position on screen
        self.setGeometry(300, 200, 1000, 600)

        # main_widget holds all other widgets in window
        self.main_widget = QtGui.QWidget(self)

        # initialize the graph
        self.depgraph = depgraph.DepositionGraph(self.main_widget)
        if DEP_DATA:
            self.depgraph.firstPlot()

        self.setWindowTitle("Deposition Window - Work In Progress")

        # set main_widget as center of window
        self.setCentralWidget(self.main_widget)

        # dealing with layouts and design
        self.mainlayout = QtGui.QGridLayout(self.main_widget)
        self.sidelayout = QtGui.QGridLayout(self.main_widget)

        # adding layouts to one another
        self.mainlayout.addWidget(self.depgraph,0,0)
        self.mainlayout.addLayout(self.sidelayout,0,1)

        #set the streches
        self.mainlayout.setColumnStretch(0,5)
        self.mainlayout.setColumnStretch(1,0)

        #drop down widget, text widgets, etc.
        self.selectUnits = QtGui.QComboBox()
        self.chemEQ = QtGui.QLineEdit(self)
        self.densityLine = QtGui.QLineEdit(self)
        self.procChem = QtGui.QPushButton('Enter')
        self.setZ = QtGui.QComboBox()
        self.rescaleButton = QtGui.QPushButton('Reset Colors')

        # set connections up
        self.procChem.clicked.connect(self.handleEQS)
        self.rescaleButton.clicked.connect(self.resetColors)

        # labels
        self.label_conversions = QtGui.QLabel('Conversions Available:')
        self.label_chemEQ = QtGui.QLabel('Chemical equation:')
        self.label_density = QtGui.QLabel('Density:')
        self.label_zvars = QtGui.QLabel('Z values:')
        self.unitOptions = []

        #for unit in self.unitOptions:
            #self.selectUnits.addItem(unit)

        self.selectUnits.activated[str].connect(self.selectConversion)

        for zval in self.depgraph.zvars:
            self.setZ.addItem(str(zval))

        self.setZ.activated[str].connect(self.switchZ)

        self.sidelayout.setAlignment(QtCore.Qt.AlignTop)

        #adding to sidelayout
        self.sidelayout.addWidget(self.label_conversions)
        self.sidelayout.addWidget(self.selectUnits)
        self.sidelayout.addWidget(self.label_chemEQ)
        self.sidelayout.addWidget(self.chemEQ)
        self.sidelayout.addWidget(self.label_density)
        self.sidelayout.addWidget(self.densityLine)
        self.sidelayout.addWidget(self.procChem)
        self.sidelayout.addWidget(self.label_zvars)
        self.sidelayout.addWidget(self.setZ)
        self.sidelayout.addWidget(self.rescaleButton)

        self.show()


    def selectConversion(self, unitName):

        unitNameStr = str(unitName)
        
        if self.Lmnts:
            if "ng/(scm^2)" == unitNameStr:
                self.depgraph.convFactor = 10
                self.depgraph.units = 'ng/s cm'+r'$^2$'
            elif "nm/s" == unitNameStr:
                #divide using the density - consider A/s
                self.depgraph.convFactor = 0.1/self.density
                self.depgraph.units = 'nm/s'
            elif "nmol/(s*cm^2)" == unitNameStr:
                # divide using the molar mass to get this
                scaledMass = self.Lmnts["Metal Name"].mass + self.Lmnts["Second Element"].mass \
                            *self.Lmnts["Second Element Stoich"]
                factor = Fraction(self.Lmnts["Second Element Stoich"]).limit_denominator(100)
                molarMass = scaledMass * factor._denominator
                self.depgraph.convFactor = 10./molarMass
                self.depgraph.units = 'nmoles/s cm'+r'$^2$'

            self.depgraph.colorbar.set_label(self.depgraph.units)
            self.depgraph.convertPlot()
            
            print self.depgraph.convFactor    

    """Deals with the """
    def handleEQS(self):
        formula = self.chemEQ.text()

        if self.densityLine.text():
            try:
                self.density = float(self.densityLine.text())
                if "nm/s" not in self.unitOptions:
                    self.unitOptions.append("nm/s")
                    self.selectUnits.addItem("nm/s")
            except ValueError:
                valError = QtGui.QMessageBox.information(None,
                                                        "Invalid Density","Unxpected density value")
        if not self.densityLine.text():
            if "nm/s" in self.unitOptions:
                self.selectUnits.removeItem(self.unitOptions.index("nm/s"))
                self.unitOptions.remove("nm/s")

        if formula and self.checkRegEx(formula):
            if "nmol/(s*cm^2)" not in self.unitOptions:
                self.unitOptions.append("nmol/(s*cm^2)")
                self.selectUnits.addItem("nmol/(s*cm^2)")
        if not formula:
            if "nmol/(s*cm^2)" in self.unitOptions:
                self.selectUnits.removeItem(self.unitOptions.index("nmol/(s*cm^2)"))
                self.unitOptions.remove("nmol/(s*cm^2)")
        if formula and not self.checkRegEx(formula):
            message = "The equation you entered is of the wrong format or is missing an element."
            message += "Some examples are: FeO and FeO1.5"
            inputError = QtGui.QMessageBox.information(None,"Wrong Format", message)

        
    """Checks that the users chemical equation is the in the correct format"""
    def checkRegEx(self,text):
        reg0 = '^'
        reg1 = '[A-Z]'
        reg2 = '[a-z]?'
        reg3 = '([ONBC])'
        reg4 = '[\d]*'
        reg5 = '(\.\d+)?'
        reg6 = '$'
        
        totalReg = reg0 + '(' + reg1+reg2 + ')' + reg3 + '(' + reg4 + reg5 + ')' + reg6

        regEX = re.compile(totalReg)
        matchedReg = re.match(regEX,str(text))

        if matchedReg:
            metalName, otherElmntName = matchedReg.group(1), matchedReg.group(2)
            otherElmntStoich  = matchedReg.group(3)
            
            if otherElmntStoich == "":
                otherElmntStoich = 1.

            try:
                metalElmntObject = ELEMENTS[metalName]
                secondElmntObject = ELEMENTS[otherElmntName]
                self.Lmnts["Metal Name"] = metalElmntObject
                self.Lmnts["Second Element"] = secondElmntObject
                self.Lmnts["Second Element Stoich"] = float(otherElmntStoich)
                return True

            except KeyError:
                pass
    
        return False

    def updateWindow(self,newDepRates):
        self.depgraph.updatePlot(newDepRates)

    """ redraws the scatter plot when the z-position of the data changes """
    def switchZ(self, newZ):
        zval = float(newZ)
        self.depgraph.clearPlot()
        self.depgraph.firstPlot(zval)

    """ manually redraws the colors in the scatter plot """
    def resetColors(self):
        self.depgraph.rescale()
        self.depgraph.draw()

    """ redraws the scatter plot when new data point is processed """
    def updateWindow(self,newDepRate):
        # newDepRates = (z, x, y, rate)
        z = newDepRate[0]
        # this will occur if the instrument moved to a new z or the graph
        # window was opened before the first data points had been processed
        if z not in self.depgraph.zvars:
            self.setZ.addItem(str(z))
            self.setZ.setCurrentIndex(self.setZ.count()-1)
            self.switchZ(z)
        self.depgraph.updatePlot(newDepRate)

    """ the deposition graph is redrawn whenever new data comes in
        rather than on every one-second interval """
    def redrawWindow(self):
        pass
