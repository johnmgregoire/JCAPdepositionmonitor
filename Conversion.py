# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 10:30:59 2013

@author: Solrisa
"""

from  PyQt4 import QtCore, QtGui
from PyQt4 import Qt
from elements import ELEMENTS
#from fractions import Fraction
from math import *
import re
#import sys

#LmtngElmnt=Elmnt3 #Set Rate-limiting Element
#Prompt the user or record the crystal montitor reading for
#the deposition rate of the slowest-depositing element.
#This value is usually valuex10^-8 g/sec-cm2
LmtngDepRateXM=1.94
Elmnt1Conc=0.5
Elmnt2Conc=0.25
Elmnt3Conc=0.25

def getElement(chemFormula):
    reg0 = '^'
    reg1 = '[A-Z]'
    reg2 = '[a-z]?'
    reg3 = '([ONBC])'
    reg4 = '[\d]*'
    reg5 = '(\.\d+)?'
    reg6 = '(' + reg3 + '(' + reg4 + reg5 + ')' +')?'
    reg7 = '$'
    totalReg = reg0 +'(' + reg1+reg2 + ')' + reg6 + reg7
    regEX = re.compile(totalReg)
    matchedReg = re.match(regEX,str(chemFormula))
    
    if matchedReg:
        metalName, otherElmntName = matchedReg.group(1), matchedReg.group(3)
        otherElmntStoich = matchedReg.group(4)
        try:
            metalElmntObject = ELEMENTS[metalName]
            secondElmntObject = ELEMENTS[otherElmntName] if otherElmntName else ""
            if not otherElmntStoich:
                otherElmntStoich = 1.
            secondElmntStoich = float(otherElmntStoich)
            elementMass = metalElmntObject.mass
            totalmass = elementMass + (secondElmntObject.mass * secondElmntStoich)
            return totalmass #in gram/mol
        except KeyError:
            pass
    return False
        
#                self.Lmnts["Metal Name"] = metalElmntObject
#                self.Lmnts["Second Element"] = secondElmntObject
#                self.Lmnts["Second Element Stoich"] = float(otherElmntStoich)

               # divide using the molar mass to get this
#def conversion(elementMass, secondElmntMass, secondElmntStoich):
#    print type(elementMass)
#    scaledMass = elementMass + (secondElmntMass * secondElmntStoich)
#    convertedMass = 10./scaledMass
#    return convertedMass
##    units = 'nmol/s cm'+r'$^2$'
#
#def unconvert(elementMass):
#    unScaledMass = elementMass + (secondElmntObject.mass * secondElmntStoich)
#    unconvertedMass = unScaledMass/10.
#    return unconvertedMass


#Set deposition-estimates rates (factors for # of cations per molecule)
def Rates(element1, element2, element3):
    Elmnt1Mass = getElement(element1)
    Elmnt2Mass = getElement(element2)
    Elmnt3Mass = getElement(element3)

    LmtngElmnt=Elmnt1Mass

#    if LmtngElmnt==Elmnt1Mass:
    Elmnt1RateNMol=LmtngDepRateXM*10/Elmnt1Mass
    Elmnt1RateGrams=LmtngDepRateXM
    print 'Element1 = Limiting Rate Element (in nmol/sec*cm^2):%0.9f' % (Elmnt1RateNMol)
    Elmnt2RateNMol=Elmnt1RateNMol*(Elmnt2Conc/Elmnt1Conc)
    Elmnt2RateGrams=Elmnt2RateNMol*(Elmnt2Mass/10)
    print 'Element2 Calculated Deposition Rate (in 10^-8 g/sec*cm^2):%0.9f' % (Elmnt2RateGrams)
    Elmnt3RateNMol=Elmnt1RateNMol*(Elmnt3Conc/Elmnt1Conc)
    Elmnt3RateGrams=Elmnt3RateNMol*(Elmnt3Mass/10)
    print 'Element3 Calculated Deposition Rate (in 10^-8 g/sec*cm^2):%0.9f' % (Elmnt3RateGrams)
#    elif LmtngElmnt==Elmnt2Mass:
##        LEcatrate=E2catrate
#        Elmnt2RateNMol=LmtngDepRateXM*Elmnt2Mass*(10**8)
#        Elmnt2RateGrams=LmtngDepRateXM*10**8
#        print 'Element2 = Limiting Rate Element (in nmol/sec*cm^2):%0.9f' % (Elmnt2RateNMol)
#        Elmnt3RateNMol=Elmnt2RateNMol*(Elmnt3Conc/Elmnt2Conc)
#        Elmnt3RateGrams=Elmnt3RateNMol/(Elmnt3Mass/10)
#        print 'Element3 Calculated Deposition Rate (in 10^-8 g/sec*cm^2):%0.9f' % (Elmnt3RateGrams)
#        Elmnt1RateNMol=Elmnt2RateNMol*(Elmnt1Conc/Elmnt2Conc)
#        Elmnt1RateGrams=Elmnt1RateNMol/(Elmnt1Mass/10)
#        print 'Element1 Calculated Deposition Rate (in 10^-8 g/sec*cm^2):%0.9f' % (Elmnt1RateGrams)
#    elif LmtngElmnt==Elmnt3Mass:
##        LEcatrate=E3catrate
#        Elmnt3RateNMol=LmtngDepRateXM*Elmnt3Mass*(10**8)
#        Elmnt3RateGrams=LmtngDepRateXM*10**8
#        print 'Element3 = Limiting Rate Element (in nmol/sec*cm^2):%0.9f' % (Elmnt3RateNMol)
#        Elmnt1RateNMol=Elmnt3RateNMol*(Elmnt1Conc/Elmnt3Conc)
#        Elmnt1RateGrams=Elmnt1RateNMol/(Elmnt1Mass/10)
#        print 'Element1 Calculated Deposition Rate (in 10^-8 g/sec*cm^2):%0.9f' % (Elmnt1RateGrams)
#        Elmnt2RateNMol=Elmnt3RateNMol*(Elmnt2Conc/Elmnt3Conc)
#        Elmnt2RateGrams=Elmnt2RateNMol/(Elmnt2Mass/10)
#        print 'Element2 Calculated Deposition Rate (in 10^-8 g/sec*cm^2):%0.9f' % (Elmnt2RateGrams)

    Elmnt1DepRateReal=Elmnt1RateNMol
    Elmnt2DepRateReal=Elmnt2RateNMol
    Elmnt3DepRateReal=Elmnt3RateNMol
    
    ##Set(create look-up table?) for density values of apprpriate oxides
    ElmntOxide1dnsty=7.215 #g/cm^3
    ElmntOxide2dnsty=6.67 #g/cm3 (monoclinic, occurs at <70 degreesC)
    ElmntOxide3dnsty=6.11 #g/cm3 (α-form/cubic form, ocurs at <570 degreesC)
    
    #Set *real* deposition rates (apply limiting-rate)
    Rate=100*((Elmnt1Conc*ElmntOxide1dnsty/Elmnt1Mass)+\
        (Elmnt2Conc*ElmntOxide2dnsty/Elmnt2Mass)+\
        (Elmnt3Conc*ElmntOxide3dnsty/Elmnt3Mass))/\
        (Elmnt1DepRateReal+Elmnt2DepRateReal+Elmnt3DepRateReal)
    print 'Time/Thickness Rate (in sec/nm):%0.9F' % (Rate)
##Set *real* deposition rates (apply limiting-rate)
#def RateCalculator():
#    Rate=(Elmnt1conc*(E1catrate*ElmntOxide1dnsty/Elmnt1mw)+Elmnt2conc*(E2catrate*ElmntOxide2dnsty/Elmnt2mw)+Elmnt3conc*(E3catrate*ElmntOxide3dnsty/Elmnt3mw))/(Elmnt1DepRateReal+Elmnt2DepRateReal+Elmnt3DepRateReal)
#    print Rate