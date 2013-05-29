# Allison Schubauer and Daisy Hernandez
# Created: 5/29/2013
# Last Updated: 5/29/2013
# For JCAP

"""
Has helpful date functions to converting to datetime objects
"""

import time 
from time import strftime
import datetime

# give a time.time() object and it returns a datetime object
def dateObj(atime):
    localCurrTime = strftime("%H:%M:%S", time.localtime(atime))
    return datetime.datetime.strptime(localCurrTime, "%H:%M:%S")
