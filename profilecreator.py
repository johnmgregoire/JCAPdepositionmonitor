# Allison Schubauer and Daisy Hernandez
# Created: 5/23/2013
# Last Updated: 5/24/2013
# For JCAP

from PyQt4 import QtGui
from datareader import *
import cPickle as pickle

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
        instructions.setText("Choose up to 8 variables to graph.")
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
        buttons = QtGui.QDialogButtonBox()
        buttons.setStandardButtons(QtGui.QDialogButtonBox.Ok
                                         | QtGui.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.saveProfile)
        buttons.rejected.connect(self.close)
        vBox.addWidget(buttons)

    def getVars(self):
        global DATA_HEADINGS
        self.checkboxes = []
        for index in range(len(DATA_HEADINGS)-2):
            self.checkboxes += [QtGui.QCheckBox(DATA_HEADINGS.get(index+2),
                                                self)]
            if index <= (len(DATA_HEADINGS)-2)/2:
                self.col1.addWidget(self.checkboxes[index])
            else:
                self.col2.addWidget(self.checkboxes[index])

    def saveProfile(self):
        #get varsList from checked boxes
        varsList = []
        for box in self.checkboxes:
            if box.isChecked():
                varsList += [str(box.text())]
        if len(varsList) > 8:
            self.tooManyVars()
            return
        elif len(varsList) < 1:
            self.tooFewVars()
            return
        name, ok = QtGui.QInputDialog.getText(self, 'Create a New Profile',
                                              'Please enter a name for this profile.')
        if ok:
            # 'ab+' indicates append to file
            savefile = open('saved_profiles.txt', 'ab+')
            pickle.dump((str(name), varsList), savefile)
            print 'Saved!'
        self.close()

    def tooManyVars(self):
        error = QtGui.QMessageBox.question(None, 'Error',
                                           'You can only put 8 graphs in a profile.',
                                           QtGui.QMessageBox.Ok)

    def tooFewVars(self):
        error = QtGui.QMessageBox.question(None, 'Error',
                                           'Please select at least one graph for this profile.',
                                           QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        if (error == QtGui.QMessageBox.Cancel):
            self.close()

    def updateWindow(self):
        pass
            
