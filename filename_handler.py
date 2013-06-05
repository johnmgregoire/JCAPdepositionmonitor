# Allison Schubauer and Daisy Hernandez
# Created: 6/05/2013
# Last Updated: 6/05/2013
# For JCAP

FILE_INFO = {}

def parseFilename(filename):
    global FILE_INFO
    print filename
    if filename.endswith('.csv'):
        filename = filename[:-4]
    rawFileInfo = filename.split('_')
    print rawFileInfo
    tagsDict = {'Source': 'Source', 'Src': 'Source', 'SRC': 'Source',
            'src': 'Source', 't': 'TiltDeg', 'tilt': 'TiltDeg', 'z': 'Z_mm',
            'Z': 'Z_mm', 'Supply': 'Supply', 'Sup': 'Supply', 'sup': 'Supply'}
    for tag in rawFileInfo:
        strippedTag = filter(str.isalpha, tag)
        tagVal = filter(lambda x: not x.isalpha(), tag)
        if strippedTag in tagsDict:
            FILE_INFO[tagsDict.get(strippedTag)] = tagVal
        elif (tag.istitle() and tag.isalpha()):
            FILE_INFO['Element'] = tag
    print FILE_INFO
