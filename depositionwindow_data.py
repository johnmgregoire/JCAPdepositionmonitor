# Allison Schubauer and Daisy Hernandez
# Created: 6/5/2013
# Last Updated: 6/6/2013
# For JCAP

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

        #drop down widget, text widgets, ect
        self.selectUnits = QtGui.QComboBox()
        self.chemEQ = QtGui.QLineEdit(self)
        self.densityLine = QtGui.QLineEdit(self)
        self.procChem = QtGui.QPushButton('Enter')

        # set connections up
        self.procChem.clicked.connect(self.handleEQS)

        # labels
        self.label_chemEQ = QtGui.QLabel('Chemical equation:')
        self.unitOptions = ["g/(scm^3)", "nm/s", "mol/(s*cm^2)"]

        for unit in self.unitOptions:
            self.selectUnits.addItem(unit)

        self.selectUnits.activated[str].connect(self.selectConversion)

        self.sidelayout.setAlignment(QtCore.Qt.AlignTop)

        #adding to sidelayout
        self.sidelayout.addWidget(self.selectUnits)
        self.sidelayout.addWidget(self.label_chemEQ)
        self.sidelayout.addWidget(self.chemEQ)
        self.sidelayout.addWidget(self.densityLine)
        self.sidelayout.addWidget(self.procChem)


        self.show()


    def selectConversion(self, unitName):

        print unitName

        if self.Lmnts:
            if "g/(scm^3)":
                pass
            if "nm/s":
                density = self.density
                print self.density
                pass
            if "mol/(s*cm^2)":
                scaledMass = self.Lmnts["Metal Name"].mass + self.Lmnts["Second Element"].mass \
                            *self.Lmnts["Second Element Stoich"]
                factor = Fraction(self.Lmnts["Second Element Stoich"]).limit_denominator()
                molarMass = scaledMass * factor._denominator
                print molarMass
        

    def handleEQS(self):
        formula = self.chemEQ.text()

        if not formula:
            return

        if not self.densityLine.text():
            self.density = self.densityLine.text()
            
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

    def updateWindow(self,newDepRates):
        # newDepRates = [(x, y, rate1), (x, y, rate2)]
        self.depgraph.updatePlot(newDepRates)
        pass

    def redrawWindow(self):
        pass
