# Allison Schubauer and Daisy Hernandez
# Created: 5/23/2013
# Last Updated: 5/23/2013
# For JCAP

import csv, time
from PyQt4 import QtCore

DATA_DICT = {}
DATA_HEADINGS = {}

""" thread that reads data from file """
class DataReader(QtCore.QThread):
    def __init__(self, parent=None, filename='default.csv'):
        super(DataReader, self).__init__()
        self.running = True

        self.initData(filename)

    def initData(self, filename):
        self.datafile = open(filename, 'rb')
        # read first line and create data arrays
        headings = self.datafile.readline().split(',')
        self.numColumns = len(headings)
        # strip off '/r/n' at end of line - only works on Windows
        headings[self.numColumns-1] = headings[self.numColumns-1][:-2]
        #print headings
        #print self.numColumns
        global DATA_DICT
        global DATA_HEADINGS
        for col in range(len(headings)):
            DATA_HEADINGS[col] = headings[col]
            DATA_DICT[headings[col]] = []
        #print DATA_HEADINGS
        self.lastEOFpos = self.datafile.tell()

    def run(self):
        partial_rows = False
        partial_row_container = []
        global DATA_DICT
        global DATA_HEADINGS
        numColumns = len(DATA_DICT)

        while self.running:
            print self.running
            time.sleep(0.05)
            self.datafile.seek(self.lastEOFpos)
            data = self.datafile.readline()
            row = data.split(',')
            if len(row) == numColumns:
                partial_rows = False
                for col in range(len(row)):
                    heading = DATA_HEADINGS.get(col)
                    DATA_DICT[heading] += [row[col]]
                self.lastEOFpos = self.datafile.tell()
            else:
                partial_rows = True

    def end(self):
        print "message received"
        self.datafile.close()
        self.running = False
        

