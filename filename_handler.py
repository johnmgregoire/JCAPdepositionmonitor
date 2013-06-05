# Allison Schubauer and Daisy Hernandez
# Created: 6/05/2013
# Last Updated: 6/05/2013
# For JCAP

FILE_INFO = {}

def parseFilename(filename):
    global FILE_INFO
    if filename.endswith('.csv'):
        filename = filename[:-4]
    rawFileInfo = filename.split('_')
    tagsDict = {'Source': 'Source', 'Src': 'Source', 'SRC': 'Source',
            'src': 'Source', 't': 'TiltDeg', 'tilt': 'TiltDeg', 'z': 'Z_mm',
            'Z': 'Z_mm', 'Supply': 'Supply', 'Sup': 'Supply', 'sup': 'Supply'}
    for tag in rawFileInfo:
        strippedTag = filter(str.isalpha, tag)
        tagVal = filter(lambda x: not x.isalpha(), tag)
        if strippedTag in tagsDict:
            stdName = tagsDict.get(strippedTag)
            if (stdName == 'Z_mm' and stdName in FILE_INFO):
                FILE_INFO[stdName] += [tagVal]
            elif (stdName == 'Z_mm' or stdName == 'TiltDeg'):
                FILE_INFO[stdName] = [tagVal]
            else:
                FILE_INFO[stdName] = tagVal
        elif (tag.istitle() and tag.isalpha()):
            FILE_INFO['Element'] = tag
    if len(FILE_INFO) != 5:
        print 'Filename in incorrect format'
        # throw error
    print FILE_INFO