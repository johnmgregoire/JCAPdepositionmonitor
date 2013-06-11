# Allison Schubauer and Daisy Hernandez
# Created: 5/29/2013
# Last Updated: 6/05/2013
# For JCAP

"""
Has a function that helps us deal with time conversion
"""

import time 
import datetime

# give a float of seconds - such as time.time() and it returns a datetime obj
def dateObj(atime):
    localCurrTime = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(atime))
    return datetime.datetime.strptime(localCurrTime, "%d/%m/%Y %H:%M:%S")

# give it a string of the form d/m/Y H:M:S:f and it returns a date time object
def dateObjFloat(fullTime):
    return datetime.datetime.strptime(fullTime,"%d/%m/%Y %H:%M:%S:%f")

# gives the current local time in the form of a string
def dateString():
    localCurrTime = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time.time()))
    return localCurrTime

# gives the current local time in the form of a string
def dateStringFile():
    localCurrTime = time.strftime("%d_%m_%Y-%H_%M_%S", time.localtime(time.time()))
    return localCurrTime
