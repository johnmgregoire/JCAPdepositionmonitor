# Allison Schubauer and Daisy Hernandez
# Created: 6/5/2013
# Last Updated: 6/5/2013
# For JCAP

from PyQt4 import QtGui
import sys

class DepositionWindow(QtGui.QMainWindow):

    def __init__(self):
        super(DepositionWindow, self).__init__()

        self.initUI()

    """ draws the user interface of the window """
    def initUI(self):
        # set window size and position on screen
        self.setGeometry(300, 200, 1000, 600)

        # main_widget holds all other widgets in window
        self.main_widget = QtGui.QWidget(self)

        self.setWindowTitle("Deposition Window - Work In Progress")

        # set main_widget as center of window
        self.setCentralWidget(self.main_widget)

        # dealing with layouts and design
        self.mainlayout = QtGui.QGridLayout(self.main_widget)
        self.sidelayout = QtGui.QGridLayout(self.main_widget)

        # adding layouts to one another
        self.mainlayout.addLayout(self.sidelayout,0,1)

        #drop down widget, text widgets, ect
        self.selectUnits = QtGui.QComboBox()
        self.chemEq = QtGui.QLineEdit(self)

        # labels
        self.label_chemEq = QtGui.QLabel('Chemical equation')
        self.unitOptions = ["A/s"]

        for unit in self.unitOptions:
            self.selectUnits.addItem(unit)

        self.selectUnits.activated[str].connect(self.selectConversion)

        #adding to sidelayout
        self.sidelayout.addWidget(self.label_chemEq)
        self.sidelayout.addWidget(self.chemEq)
        self.sidelayout.addWidget(self.selectUnits)

        self.show()


    def selectConversion(self, unitName):
        print unitName

def main():
    app = QtGui.QApplication(sys.argv)
    window = DepositionWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
