# Allison Schubauer and Daisy Hernandez
# Created: 5/23/2013
# Last Updated: 5/23/2013
# For JCAP

from PyQt4 import QtGui
from datareader import *

"""widget to make profiles"""
class ProfileCreator(QtGui.QWidget):

    """sets up the Widget"""
    def __init__(self):
        super(ProfileCreator, self).__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(400, 400, 400, 300)
        self.setWindowTitle('Create a New Profile')
        vBox = QtGui.QVBoxLayout(self)
        instructions = QtGui.QLabel()
        instructions.setText("Choose which variables to graph.")
        instructions.setMaximumHeight(20)
        vBox.addWidget(instructions)
        checkField = QtGui.QWidget()
        hBox = QtGui.QHBoxLayout(checkField)
        vBox.addWidget(checkField)
        self.col1 = QtGui.QVBoxLayout()
        self.col2 = QtGui.QVBoxLayout()
        hBox.addLayout(self.col1)
        hBox.addLayout(self.col2)
        self.col1.setAlignment(QtCore.Qt.AlignTop)
        self.col2.setAlignment(QtCore.Qt.AlignTop)
        # add all checkboxes to col1 and col2
        self.getVars()
        okButton = QtGui.QPushButton("OK")
        # this will need to be changed to actually add profiles
        okButton.clicked.connect(self.close)
        cancelButton = QtGui.QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)
        buttons = QtGui.QHBoxLayout()
        vBox.addLayout(buttons)
        buttons.addWidget(okButton)
        buttons.addWidget(cancelButton)

    def getVars(self):
        global DATA_HEADINGS
        print DATA_HEADINGS
        print len(DATA_HEADINGS)
        checkboxes = []
        for index in range(len(DATA_HEADINGS)):
            checkboxes += [QtGui.QCheckBox(DATA_HEADINGS.get(index), self)]
            if index <= len(DATA_HEADINGS)/2:
                self.col1.addWidget(checkboxes[index])
            else:
                self.col2.addWidget(checkboxes[index])

    def launch(self):
        self.show()
        
