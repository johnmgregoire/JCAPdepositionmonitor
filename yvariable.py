# Allison Schubauer and Daisy Hernandez
# Created: 6/3/2013
# Last Updated: 6/3/2013
# For JCAP



""" used for multi-plots - holds information for the given variable"""
class YVariable():

    def __init__(self, varName = None, axis = "None", columnNumber = None, color = "bo"):

        self.varName = varName
        self.axis = axis
        self.columnNumber = columnNumber
        self.color = color

    def __repr__(self):
        w = "Variable Name: " + self.varName + "\n"
        x = "The axis: " + str(self.axis) + "\n"
        y = "The column number is: " + str(self.columnNumber) + "\n"
        z = "The color is: " + self.color
        return w + y + z
