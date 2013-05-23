# Allison Schubauer and Daisy Hernandez
# Created: 5/23/2013
# Last Updated: 5/23/2013
# For JCAP

import csv
from PyQt4 import QtCore

DATA_DICT = {}
DATA_HEADINGS = {}

""" thread that reads data from file """
class DataReader(QtCore.QThread):
    def __init__(self, parent=None, filename='default.csv'):
        super(DataReader, self).__init__()

        self.initData(filename)

    def initData(self, filename):
        self.datafile = open(filename, 'rb')
        # read first line and create data arrays
        headings = self.datafile.readline().split(',')
        self.numColumns = len(headings)
        # strip off '/r/n' at end of line - only works on Windows
        headings[self.numColumns-1] = headings[self.numColumns-1][:-2]
        print headings
        print self.numColumns
        global DATA_DICT
        global DATA_HEADINGS
        for col in range(len(headings)):
            DATA_HEADINGS[col] = headings[col]
            DATA_DICT[headings[col]] = []
        print DATA_HEADINGS
        self.lastEOFpos = self.datafile.tell()

    def run(self):
        partial_rows = False
        partial_row_container = []
        global DATA_DICT
        numColumns = len(DATA_DICT)
        while True:
            # move to position where EOF was previously
            self.datafile.seek(self.lastEOFpos)
            data = csv.reader(self.datafile)
            for row in data:
                """ process colums:
                    check if row is complete
                    if so, add data to each appropriate column array
                    if not, save partial row to local variable container
                    if partial container is full, parse container
                """
                if len(row) == numColumns:
                    for col in range(len(row)):
                       heading = DATA_HEADINGS.get(col)
                       DATA_DICT[heading] += [row[col]]
                    print row
                else:
                    partial_rows = True
                    partial_row_container += row
                    if len(partial_row_container) == numColumns:
                        for col in range(len(partial_row_container)):
                           heading = DATA_HEADINGS.get(col)
                           DATA_DICT[heading] += partial_row_container[col]
                        partial_rows = False
                        print partial_row_container
                        partial_row_container = []
            # save current EOF position
            self.lastEOFpos = self.datafile.tell()

