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
    def __init__(self, datafile="None"):
        super(ProfileCreator, self).__init__()
        self.source = datafile

        self.initUI()

    """creates all graphics in the Widget"""
    def initUI(self):
        self.setGeometry(400, 400, 400, 300)
        self.setWindowTitle('Create a New Profile')
        # top-level vertical layout
        vBox = QtGui.QVBoxLayout(self)
        instructions = QtGui.QLabel()
        instructions.setText("Choose up to 8 variables to graph.")
        instructions.setMaximumHeight(20)
        vBox.addWidget(instructions)
        # make widget and layout to hold checkboxes
        checkField = QtGui.QWidget()
        hBox = QtGui.QHBoxLayout(checkField)
        vBox.addWidget(checkField)
        # checkboxes displayed in 2 columns
        self.col1 = QtGui.QVBoxLayout()
        self.col2 = QtGui.QVBoxLayout()
        hBox.addLayout(self.col1)
        hBox.addLayout(self.col2)
        self.col1.setAlignment(QtCore.Qt.AlignTop)
        self.col2.setAlignment(QtCore.Qt.AlignTop)
        # add all checkboxes to col1 and col2
        self.getVars()
        # create OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.setStandardButtons(QtGui.QDialogButtonBox.Ok
                                         | QtGui.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.saveProfile)
        buttons.rejected.connect(self.close)
        vBox.addWidget(buttons)

    """makes checkboxes for each variable in data set"""
    def getVars(self):
        global DATA_HEADINGS
        self.checkboxes = []
        # this ignores first 2 columns in spreadsheet (date and time)
        for index in range(len(DATA_HEADINGS)-2):
            self.checkboxes += [QtGui.QCheckBox(DATA_HEADINGS.get(index+2),
                                                self)]
            # first half of variables added to first column
            if index <= (len(DATA_HEADINGS)-2)/2:
                self.col1.addWidget(self.checkboxes[index])
            # second half of variables added to second column
            else:
                self.col2.addWidget(self.checkboxes[index])

    """uses cPickle to save profile for future use"""
    def saveProfile(self):
        varsList = []
        # get varsList from checked boxes
        for box in self.checkboxes:
            if box.isChecked():
                varsList += [str(box.text())]
        # error if more than 8 variables checked
        if len(varsList) > 8:
            self.tooManyVars()
            return
        # error if no variables selected
        elif len(varsList) < 1:
            self.tooFewVars()
            return
        # asks for name of profile
        name, ok = QtGui.QInputDialog.getText(self, 'Create a New Profile',
                                              'Please enter a name for this profile.')
        # saves profile if name is entered and OK is clicked
        if name and ok:
            # 'ab+' indicates append to file
            savefile = open('saved_profiles.txt', 'ab+')
            # save tuple of profile name and list of variables in profile
            pickle.dump((self.source, str(name), varsList), savefile)
            print 'Saved!'
        self.close()

    """sends error message if more than 8 variables selected"""
    def tooManyVars(self):
        error = QtGui.QMessageBox.question(None, 'Error',
                                           'You can only put 8 graphs in a profile.',
                                           QtGui.QMessageBox.Ok)

    """sends error message if no variables selected"""
    def tooFewVars(self):
        error = QtGui.QMessageBox.question(None, 'Error',
                                           'Please select at least one graph for this profile.',
                                           QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        # exits profile creator if Cancel is clicked
        if (error == QtGui.QMessageBox.Cancel):
            self.close()

    """function called on all windows by MainMenu"""
    def updateWindow(self):
        # no figures to update
        pass

    """function called on all windows by MainMenu"""
    def redrawWindow(self):
        # no figures to draw
        pass
            
