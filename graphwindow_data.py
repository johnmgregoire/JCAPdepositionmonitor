# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/29/2013
# For JCAP

"""
Displays single auto-updating data graph
"""

from graph import *
from profilecreator import *
from date_helpers import *

""" Functionality to add:
    - reset axis labels while maintaining same range (i.e., last 10 minutes)

    Concerns for multiple graphs:
    - loading previous data when switching graphs
    - should all graphs be initialized at the beginning, or initialized
        only when clicked on?
    - incomplete set of data in DATA_DICT when graphs are updated
    - Different graphs are affected by terminal/shell activity due to them
        technically being on the same look/update information. This is likely
        not fixable by simply separating them, probably threading is necessary.
        (This is probably not an issue anymore.)

    TO DO:
    - take data on certain conditions?
    - try/catch with partial rows (and other places)
    - fix reader so it doesn't put partial last columns into dictionary

    More things to consider:
    - Is importing a library file more than once dangerous?
    - Should we use a QListWidget for the profile creator?
    - Can we detect when the writer has closed the data file?
    - Does it take up too much processing power to keep reading when
        no new data is being sent?
    - How regularly does information get sent to the data file?
    - Is the data file saved (so we can detect that it's been modified)
        after each write?
    - Format of data files
"""

""" main window of the application """
class GraphWindow(QtGui.QMainWindow):

    def __init__(self):
        super(GraphWindow, self).__init__()
        

        self.initUI()

    def initUI(self):
        # set window size and position on screen
        self.setGeometry(300, 200, 800, 600)
        
        # set up the menu bar and pop up windows
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        optionsMenu = menubar.addMenu('&Options')
        optionsAction = QtGui.QAction('&Add Profile', self)
        optionsAction.triggered.connect(self.createProfile)
        optionsMenu.addAction(optionsAction)
        
        self.main_widget = QtGui.QWidget(self)

        # get variables from spreadsheet
        global DATA_HEADINGS
        self.vars = []
        for index in range(2, len(DATA_HEADINGS)):
            self.vars += [DATA_HEADINGS.get(index)]

        # initialize default graph
        self.graph = Graph(self.main_widget, xvarname="Time",
                           yvarname=self.vars[0])
        self.setWindowTitle(self.vars[0])

        # make drop-down menu for selecting graphs      
        self.selectVar = QtGui.QComboBox()
        for var in self.vars:
            self.selectVar.addItem(var)

        self.selectVar.activated[str].connect(self.selectGraph)

        # setup all the layouts - verify that they take in the correct
        # widget  - TODO
        self.layout = QtGui.QVBoxLayout(self.main_widget)
        self.gridlayout = QtGui.QGridLayout(self.main_widget)
        self.axeslayout = QtGui.QGridLayout(self.main_widget)
        self.timelayout = QtGui.QGridLayout(self.main_widget)
        self.autolayout = QtGui.QGridLayout(self.main_widget)

        # setup the column stretches - 0 is the default
        # setup minimum column widths
        self.gridlayout.setColumnStretch(0,4)
        self.gridlayout.setColumnStretch(1,0)
        self.gridlayout.setColumnMinimumWidth(0,300)
        self.gridlayout.setRowMinimumHeight(0,375)

        # drop down menu
        self.layout.addWidget(self.selectVar)

        # made widgets for layouts
        self.grid_widget = QtGui.QWidget()
        self.grid_widget.setLayout(self.gridlayout)

        # input boxes for axes and checkboxes for gui
        self.hold_cb = QtGui.QCheckBox('Hold', self)
        self.hold_cb.stateChanged.connect(self.graph.hold)
    
        self.minutes = QtGui.QLineEdit(self)
        self.minutes.setFixedWidth(40)
        self.hours = QtGui.QLineEdit(self)
        self.hours.setFixedWidth(40)
        self.days = QtGui.QLineEdit(self)
        self.days.setFixedWidth(40)
        self.Ymin = QtGui.QLineEdit(self)
        self.Ymax = QtGui.QLineEdit(self)

        # lables for the input boxes
        self.label_time = QtGui.QLabel('Show data from the last:')
        self.label_minutes = QtGui.QLabel('minutes')
        self.label_hours = QtGui.QLabel('hours')
        self.label_days = QtGui.QLabel('days')
        self.label_Ymin = QtGui.QLabel('Y Min:')
        self.label_Ymax = QtGui.QLabel('Y Max:')

        # buttons and their connections
        self.set_axes = QtGui.QPushButton('Enter')
        self.auto_xaxes = QtGui.QPushButton('Auto X')
        self.auto_yaxes = QtGui.QPushButton('Auto Y')
        self.screen_shot = QtGui.QPushButton('Screen Shot')
        self.set_axes.clicked.connect(self.setAxes)
        self.auto_xaxes.clicked.connect(self.autoXAxes)
        self.auto_yaxes.clicked.connect(self.autoYAxes)
        self.auto_yaxes.clicked.connect(self.takeScreenShot)
        

        # place the layouts inside the other layouts
        self.layout.addWidget(self.grid_widget)

        # add items to the grid widget
        self.gridlayout.addWidget(self.graph,0, 0)
        self.gridlayout.addLayout(self.axeslayout, 0, 1)

        # set alignments for the widgets
        self.axeslayout.setAlignment(QtCore.Qt.AlignTop)

        # add items to the axis widget
        self.axeslayout.addWidget(self.hold_cb, 0, 0)
        self.axeslayout.addWidget(self.label_time, 1, 0)
        self.axeslayout.addLayout(self.timelayout, 2, 0)

        self.timelayout.addWidget(self.minutes, 0, 0)
        self.timelayout.addWidget(self.label_minutes, 0, 1)
        self.timelayout.addWidget(self.hours, 1, 0)
        self.timelayout.addWidget(self.label_hours, 1, 1)
        self.timelayout.addWidget(self.days, 2, 0)
        self.timelayout.addWidget(self.label_days, 2, 1)
        
        self.axeslayout.addWidget(self.label_Ymin, 3, 0)
        self.axeslayout.addWidget(self.Ymin, 4, 0)
        self.axeslayout.addWidget(self.label_Ymax,5, 0)
        self.axeslayout.addWidget(self.Ymax, 6, 0)
        self.axeslayout.addWidget(self.set_axes, 7, 0)
        self.axeslayout.addLayout(self.autolayout, 8, 0)

        self.autolayout.addWidget(self.auto_xaxes, 0 , 0)
        self.autolayout.addWidget(self.auto_yaxes, 0 , 1)

        self.axeslayout.addWidget(self.screen_shot,9,0)
        
        
        self.setCentralWidget(self.main_widget)
        
        
        self.show()

    def selectGraph(self, varName):
        # clear plot and set parent to None so it can be deleted
        self.graph.clearPlot()
        self.graph.setParent(None)
        self.gridlayout.removeWidget(self.graph)
        self.graph =  None
        varString = str(varName)
        self.graph = Graph(self.main_widget, xvarname = "Time",
                           yvarname = varString)
        self.gridlayout.addWidget(self.graph,0,0)
        self.setWindowTitle(varString)
        
    def updateWindow(self):
        self.graph.updatePlot()

    def setAxes(self):
        setXAxes = [False, None, None]
        setYAxes = [False, None, None]

        # dealing with the current time and the time that we have to
        # go back
        currTime = time.time()
        timeBack = 0
        setXAxes[2] = dateObj(currTime)

        min_input = self.minutes.text()
        hour_input = self.hours.text()
        day_input = self.days.text()
        Ymin_input = self.Ymin.text()
        Ymax_input = self.Ymax.text()
        axes_input = [('min', min_input), ('hour', hour_input),
                      ('day', day_input), ('Ymin', Ymin_input),
                      ('Ymax', Ymax_input)]
        for axis_tuple in axes_input:
            try:
                value = float(axis_tuple[1])
                #self.axesToSet += [(axis_tuple[0], value)]
                if axis_tuple[0] == 'Ymin':
                    setYAxes[0] = True
                    setYAxes[1] = value
                elif axis_tuple[0] == 'Ymax':
                    setYAxes[0] = True
                    setYAxes[2] = value
                elif axis_tuple[0] == 'min':
                    setXAxes[0] = True
                    timeBack += value*60
                elif axis_tuple[0] == 'hour':
                    setXAxes[0] = True
                    timeBack += value*60*60
                elif axis_tuple[0] == 'day':
                    setXAxes[0] = True
                    timeBack += value*60*60*24
            except ValueError:
                pass
        print setXAxes
        print setYAxes
        
        setXAxes[1] = dateObj(currTime - timeBack)
        
        if setYAxes[0]:
            self.graph.setYlim(amin=setYAxes[1], amax=setYAxes[2])
        if setXAxes[0]:
            self.graph.auto = False
            self.graph.timeWindow = timeBack
            self.graph.setXlim(amin=setXAxes[1], amax=setXAxes[2])

    def autoXAxes(self):
        self.graph.auto = True
        self.graph.axes.set_xlim(auto=True)
        
    def autoYAxes(self):
        self.graph.axes.set_ylim(auto=True)

    def createProfile(self):
        self.profileCreator = ProfileCreator()
        self.profileCreator.show()

    def takeScreenShot(self):
        pass
        
    


"""def main():
    app = QtGui.QApplication(sys.argv)
    window = GraphWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()"""
        
