# Allison Schubauer and Daisy Hernandez
# Created: 6/05/2013
# Last Updated: 6/05/2013
# For JCAP

from datareader import DATA_DICT, DATA_HEADINGS

""" helper function to get the column number associated with a heading
    in the data spreadsheet """
def getCol(colName):
    theCol = [k for k, v in DATA_HEADINGS.iteritems() if v == colName]
    return theCol[0]
