# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/30/2013
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

    def __init__(self, datafile = "None"):
        super(GraphWindow, self).__init__()
        # save spreadsheet filename
        self.source = datafile
        self.updating = False

        self.initUI()

    """ draws the user interface of the window """
    def initUI(self):
        # set window size and position on screen
        self.setGeometry(300, 200, 800, 600)
        
        # set up the menu bar and profile creator
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        optionsMenu = menubar.addMenu('&Options')
        profileAction = QtGui.QAction('&Add Profile', self)
        profileAction.triggered.connect(self.createProfile)
        optionsMenu.addAction(profileAction)

        # main_widget holds all other widgets in window
        self.main_widget = QtGui.QWidget(self)

        # get variables from spreadsheet
        global DATA_HEADINGS
        self.vars = []
        for index in range(2, len(DATA_HEADINGS)):
            self.vars += [DATA_HEADINGS.get(index)]

        # initialize default graph
        self.graph = Graph(self.main_widget, xvarname="Time",
                           yvarname=self.vars[0])
        self.updating = True
        self.setWindowTitle(self.vars[0])

        # make drop-down menu for selecting graphs      
        self.selectVar = QtGui.QComboBox()
        for var in self.vars:
            self.selectVar.addItem(var)
        self.selectVar.activated[str].connect(self.selectGraph)

        # setup all the layouts - verify that they take in the correct
        # widget  - TODO figure out what QT as parent means
        self.layout = QtGui.QVBoxLayout(self.main_widget)
        self.gridlayout = QtGui.QGridLayout(self.main_widget)
        self.axeslayout = QtGui.QGridLayout(self.main_widget)
        self.timelayout = QtGui.QGridLayout(self.main_widget)
        # this exists so auto axis buttons can move if necessary
        self.autowidget = QtGui.QWidget(self.main_widget)
        self.autolayout = QtGui.QGridLayout(self.autowidget)

        # first column holds graph, second column holds graph options
        # set the column stretches - 0 is the default
        # set minimum column widths
        self.gridlayout.setColumnStretch(0,7)
        self.gridlayout.setColumnStretch(1,1)
        self.gridlayout.setColumnMinimumWidth(0,300)
        self.gridlayout.setRowMinimumHeight(0,375)

        # add drop-down menu to top of window
        self.layout.addWidget(self.selectVar)

        # grid_widget holds the graph and options
        self.grid_widget = QtGui.QWidget()
        self.grid_widget.setLayout(self.gridlayout)

        # initialize checkbox that acts as pause button
        self.hold_cb = QtGui.QCheckBox('Hold', self)
        self.hold_cb.stateChanged.connect(self.hold)
    
        # initialize input boxes for axis limits
        self.minutes = QtGui.QLineEdit(self)
        self.minutes.setFixedWidth(40)
        self.hours = QtGui.QLineEdit(self)
        self.hours.setFixedWidth(40)
        self.days = QtGui.QLineEdit(self)
        self.days.setFixedWidth(40)
        self.Ymin = QtGui.QLineEdit(self)
        self.Ymax = QtGui.QLineEdit(self)
        self.YminR = QtGui.QLineEdit(self)
        self.YmaxR = QtGui.QLineEdit(self)

        # create labels for the input boxes
        self.label_time = QtGui.QLabel('Show data from the last:')
        self.label_minutes = QtGui.QLabel('minutes')
        self.label_hours = QtGui.QLabel('hours')
        self.label_days = QtGui.QLabel('days')
        self.label_Ymin = QtGui.QLabel('Y Min (left):')
        self.label_Ymax = QtGui.QLabel('Y Max (left):')
        self.label_YminR = QtGui.QLabel('Y Min (right):')
        self.label_YmaxR = QtGui.QLabel('Y Max (right):')

        # initialize buttons and their connections
        self.set_axes = QtGui.QPushButton('Enter')
        self.auto_xaxes = QtGui.QPushButton('Auto X')
        self.auto_yaxes = QtGui.QPushButton('Auto Y (left)')
        self.auto_yraxes = QtGui.QPushButton('Auto Y (right)')
        self.screen_shot = QtGui.QPushButton('Screen Shot')
        self.set_axes.clicked.connect(self.setAxes)
        self.auto_xaxes.clicked.connect(self.autoXAxes)
        self.auto_yaxes.clicked.connect(self.autoYAxes)
        self.auto_yraxes.clicked.connect(self.autoYRAxes)
        self.screen_shot.clicked.connect(self.takeScreenShot)

        # set the possible streches of input boxes
        self.Ymin.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        self.Ymax.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        self.YminR.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        self.YmaxR.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        #self.set_axes.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)

        # initialize menu to choose variable for right-hand axis
        self.label_raxis = QtGui.QLabel('Choose a variable to plot on the right-hand axis:')
        self.choose_var = QtGui.QComboBox()
        for var in self.vars:
            self.choose_var.addItem(var)
        self.set_raxis = QtGui.QPushButton('Plot')
        self.set_raxis.clicked.connect(self.addRAxis)

        # place the main grid layout inside layout for window
        self.layout.addWidget(self.grid_widget)

        # add graph and options to main grid layout
        self.gridlayout.addWidget(self.graph, 0, 0)
        self.gridlayout.addLayout(self.axeslayout, 0, 1)

        # set alignments for the widgets
        self.axeslayout.setAlignment(QtCore.Qt.AlignTop)

        # add items to the graph options layout
        self.axeslayout.addWidget(self.hold_cb, 0, 0)
        self.axeslayout.addWidget(self.label_raxis)
        self.axeslayout.addWidget(self.choose_var)
        self.axeslayout.addWidget(self.set_raxis)
        self.axeslayout.addWidget(self.screen_shot)
        self.axeslayout.addWidget(self.label_time)
        self.axeslayout.addLayout(self.timelayout, 6, 0)

        # add options for time axis to a sub-grid
        self.timelayout.addWidget(self.minutes, 0, 0)
        self.timelayout.addWidget(self.label_minutes, 0, 1)
        self.timelayout.addWidget(self.hours, 1, 0)
        self.timelayout.addWidget(self.label_hours, 1, 1)
        self.timelayout.addWidget(self.days, 2, 0)
        self.timelayout.addWidget(self.label_days, 2, 1)

        # add more items to graph options layout
        self.axeslayout.addWidget(self.label_Ymin)
        self.axeslayout.addWidget(self.Ymin)
        self.axeslayout.addWidget(self.label_Ymax)
        self.axeslayout.addWidget(self.Ymax)
        self.axeslayout.addWidget(self.label_YminR)
        self.axeslayout.addWidget(self.YminR)
        self.axeslayout.addWidget(self.label_YmaxR)
        self.axeslayout.addWidget(self.YmaxR)
        self.axeslayout.addWidget(self.set_axes)

        # hide options for second axis initially
        self.label_YminR.hide()
        self.YminR.hide()
        self.label_YmaxR.hide()
        self.YmaxR.hide()
        
        self.axeslayout.addWidget(self.set_axes)
        # add widget that holds auto axis buttons
        self.axeslayout.addWidget(self.autowidget)
        # add auto axis buttons
        self.autolayout.addWidget(self.auto_xaxes, 0 , 0)
        self.autolayout.addWidget(self.auto_yaxes, 0 , 1)
        self.autolayout.addWidget(self.auto_yraxes, 0 , 2)
        # hide option for auto right axis initially
        self.auto_yraxes.hide()

        # set main_widget as center of window
        self.setCentralWidget(self.main_widget)
        
        self.show()

    """ called when variable to plot is selected """
    def selectGraph(self, varName):
        # clear previous plot and set parent to None so it can be deleted
        self.graph.clearPlot()
        self.graph.setParent(None)
        self.gridlayout.removeWidget(self.graph)
        self.graph =None
        # convert QString to string
        varString = str(varName)
        self.graph = Graph(self.main_widget, xvarname = "Time",
                           yvarname = varString)
        self.gridlayout.addWidget(self.graph, 0, 0)
        self.setWindowTitle(varString)
        # remove all options for right-hand axis because plot is initialized
        #   without it
        self.label_YminR.hide()
        self.YminR.hide()
        self.label_YmaxR.hide()
        self.YmaxR.hide()
        self.auto_yraxes.hide()
        # clear axis label fields
        self.minutes.clear()
        self.hours.clear()
        self.days.clear()
        self.Ymin.clear()
        self.Ymax.clear()
        self.YminR.clear()
        self.YmaxR.clear()

    """ called when request to add plot to right-hand axis is made """
    def addRAxis(self):
        # get name of variable from selection menu
        varName = self.choose_var.currentText()
        # convert QString to string
        varString = str(varName)
        self.graph.addRightAxis(varString)
        # reset right y-axis limit fields
        self.YminR.clear()
        self.YmaxR.clear()
        # show all options for right-hand axis
        self.label_YminR.show()
        self.YminR.show()
        self.label_YmaxR.show()
        self.YmaxR.show()
        self.auto_yraxes.show()

    """ called by MainMenu at every 1-second interval """        
    def updateWindow(self):
        if self.updating:
            self.graph.updatePlot()

    """ toggles auto-updating property of graphs in window """
    def hold(self):
        if self.updating == True:
            self.updating = False
        else:
            self.updating = True

    """ called when user gives input for axis limits """
    def setAxes(self):
        # [Are axes changing?, new min, new max]
        setXAxes = [False, None, None]
        setYAxes = [False, None, None]

        # dealing with the current time and the time that we have to
        #   go back for x-axis limits
        currTime = time.time()
        # measured in seconds
        timeBack = 0
        # x-axis maximum is current time
        setXAxes[2] = dateObj(currTime)

        # get and save input from all fields
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
            # if no input was given to field, ignore it
            except ValueError:
                pass

        # set x-axis minimum to current time minus specified time window
        setXAxes[1] = dateObj(currTime - timeBack)

        # if y-axis limits have been changed
        if setYAxes[0]:
            self.graph.setYlim(amin=setYAxes[1], amax=setYAxes[2])
        # if x-axis limits have been changed
        if setXAxes[0]:
            self.graph.auto = False
            self.graph.timeWindow = timeBack
            self.graph.setXlim(amin=setXAxes[1], amax=setXAxes[2])

        if self.graph.hasRightAxis:
            self.setRAxis()

    """ called when user gives input for right-hand axis limits """
    def setRAxis(self):
        # [Are axes changing?, new min, new max]
        setAxes = [False, None, None]
        YminR_input = self.YminR.text()
        YmaxR_input = self.YmaxR.text()
        try:
            setAxes[0] = True
            setAxes[1] = float(YminR_input)
        except ValueError:
            pass
        try:
            setAxes[0] = True
            setAxes[2] = float(YmaxR_input)
        except ValueError:
            pass
        if setAxes:
            self.graph.setRYlim(amin=setAxes[1], amax=setAxes[2])

    """ called when 'Auto X' button is clicked
        sets x axis limits automatically to fit all data """
    def autoXAxes(self):
        self.graph.auto = True
        self.graph.axes.set_xlim(auto=True)
        self.minutes.clear()
        self.hours.clear()
        self.days.clear()

    """ called when 'Auto Y (left)' button is clicked
        sets y axis limits automatically to fit all data """        
    def autoYAxes(self):
        self.graph.axes.set_ylim(auto=True)
        self.Ymin.clear()
        self.Ymax.clear()

    """ called when 'Auto Y (right)' button is clicked
        sets right-hand y axis limits automatically to fit all data """   
    def autoYRAxes(self):
        self.graph.rightAxes.set_ylim(auto=True)
        self.YminR.clear()
        self.YmaxR.clear()


    """ called when 'Create Profile' is chosen from options menu """
    def createProfile(self):
        self.profileCreator = ProfileCreator(datafile=self.source)
        # launches profile creator window
        self.profileCreator.show()

    """ called when 'Screen Shot' button is clicked """
    def takeScreenShot(self):
        print "Taking screen shot"
        self.graph.figure.savefig("test.png")
        print "Screen shot saved"
