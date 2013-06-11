# Allison Schubauer and Daisy Hernandez
# Created: 6/5/2013
# Last Updated: 6/7/2013
# For JCAP

import numpy as np
from graph import *
from depgraph import *
from elements import ELEMENTS
from fractions import Fraction
import re
import sys

class DepositionWindow(QtGui.QMainWindow):

    def __init__(self):
        super(DepositionWindow, self).__init__()

        self.Lmnts = {}
        self.density = None
        self.initUI()

    """ draws the user interface of the window """
    def initUI(self):
        # set window size and position on screen
        self.setGeometry(300, 200, 1000, 600)

        # main_widget holds all other widgets in window
        self.main_widget = QtGui.QWidget(self)

        # initialize the graph
        self.depgraph = DepositionGraph(self.main_widget)
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
        self.label_chemEQ = QtGui.QLabel('Chemical equation:')
        self.label_density = QtGui.QLabel('Density:')
        self.unitOptions = ["ng/(scm^2)", "nm/s", "nmol/(s*cm^2)"]

        for unit in self.unitOptions:
            self.selectUnits.addItem(unit)

        self.selectUnits.activated[str].connect(self.selectConversion)

        for zval in self.depgraph.zvars:
            self.setZ.addItem(str(zval))

        self.setZ.activated[str].connect(self.switchZ)

        self.sidelayout.setAlignment(QtCore.Qt.AlignTop)

        #adding to sidelayout
        self.sidelayout.addWidget(self.selectUnits)
        self.sidelayout.addWidget(self.label_chemEQ)
        self.sidelayout.addWidget(self.chemEQ)
        self.sidelayout.addWidget(self.label_density)
        self.sidelayout.addWidget(self.densityLine)
        self.sidelayout.addWidget(self.procChem)
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

            print self.depgraph.convFactor
            
            self.depgraph.convertPlot()
        

    def handleEQS(self):
        formula = self.chemEQ.text()

        if not formula:
            return

        if self.densityLine.text():
            try:
                self.density = float(self.densityLine.text())
            except ValueError:
                valEror = QtGui.QMessageBox.information(None,
                                                        "Invalid Density","Unxpected density value")
            
        if not self.checkRegEx(formula):
            message = "The equation you entered is of the wrong format or is missing an element."
            message += "Some examples are: FeO and FeO1.5"
            inputError = QtGui.QMessageBox.information(None,"Wrong Format", message)
        

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
        x = re.match(regEX,str(text))

        if x:
            metalName = x.group(1)
            otherElmntName = x.group(2)
            otherElmntStoich  = x.group(3)
            
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

<<<<<<< HEAD
    def updateWindow(self,newDepRates):
        # newDepRates = [(x, y, rate1), (x, y, rate2)]
        self.depgraph.updatePlot(newDepRates)
=======
    def switchZ(self, newZ):
        zval = float(newZ)
        self.depgraph.clearPlot()
        self.depgraph.firstPlot(zval)

    def resetColors(self):
        self.depgraph.rescale()
        self.depgraph.draw()

    def updateWindow(self,newDepRate):
        # newDepRates = (z, x, y, rate)
        z = newDepRate[0]
        # this will occur if the instrument has moved to
        #   the next z-value, or if the graph window was opened
        #   before the first data points had been processed
        if z not in self.depgraph.zvars:
            self.setZ.addItem(str(z))
            self.setZ.setCurrentIndex(self.setZ.count()-1)
            self.switchZ(z)
        self.depgraph.updatePlot(newDepRate)
>>>>>>> a5214829283867f6cb65566c52f98332055a2550
        pass

    def redrawWindow(self):
        pass
