# Allison Schubauer and Daisy Hernandez
# Created: 5/20/2013
# Last Updated: 5/21/2013
# For JCAP

import csv 
import time, os

def regularRead(filename):
    """ Function that does normal processing of CSV file - no following
        copied from StackOverflow """
    with open(filename, 'rb') as csvfile:     
        csvText = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in csvText:
            print ', '.join(row)


""" Algorithm for followingRead:
make csv reader object
use tell() to find position of end of file
update reader object
use seek() to go to previous EoF and read from there

Concerns:
how long does it take to make reader object/perform seek() -
will this take too long?

Notes:
When processing data, remember that csv.reader() returns entire row,
so we need to separate the columns ourselves. """

def followingRead(filename):
    """ reads csv file as it is continuously updated """
    # opens csv file as read-only with binary line endings
    with open(filename, 'rb') as csvfile:
        lastEOFpos = 0
        colNames = []
        while True:
            # move to position where EOF was previously
            csvfile.seek(lastEOFpos)
            data = csv.reader(csvfile, delimiter=' ', quotechar='|')

            # Gets the column names -- verify that no data is lost
            if(lastEOFpos == 0):
                for x in data:
                  colNames = x
                  break

            # prints entire row of data for debugging purposes
            for row in data:
                print row
            # save current EOF position
            lastEOFpos = csvfile.tell()

""" this uses cont_write_test.py, which continuously writes
    to a csv file (for testing purposes) """
followingRead('testcsv.csv')
            

                
