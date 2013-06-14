# Allison Schubauer and Daisy Hernandez
# Created: 6/05/2013
# Last Updated: 6/14/2013
# For JCAP

# holds important information associated with data file
FILE_INFO = {'Element':'', 'Source':'', 'Supply':'', 'TiltDeg':[],
             'Z_mm':[]}

""" gets information for FILE_INFO from name of data file """
def parseFilename(filename):
    global FILE_INFO
    # ignore '.csv' at end of filename
    if filename.endswith('.csv'):
        filename = filename[:-4]
    # experiment parameters should be separated with underscores
    rawFileInfo = filename.split('_')
    # keys: keywords in filename; values: corresponding keys in FILE_INFO
    tagsDict = {'Source': 'Source', 'Src': 'Source', 'SRC': 'Source',
            'src': 'Source', 't': 'TiltDeg', 'tilt': 'TiltDeg', 'z': 'Z_mm',
            'Z': 'Z_mm', 'Supply': 'Supply', 'Sup': 'Supply', 'sup': 'Supply'}
    for tag in rawFileInfo:
        # strippedTag is the keyword
        strippedTag = filter(str.isalpha, tag)
        # tagVal is the numerical value attached to the keyword
        tagVal = filter(lambda x: not x.isalpha(), tag)
        if strippedTag in tagsDict:
            stdName = tagsDict.get(strippedTag)
            # multiple z-values can be listed in filename
            if (stdName == 'Z_mm' and stdName in FILE_INFO):
                FILE_INFO[stdName] += [float(tagVal)]
            # z and t values should be stored in a list (used in
            #   data processing)
            elif (stdName == 'Z_mm' or stdName == 'TiltDeg'):
                FILE_INFO[stdName] = [float(tagVal)]
            # all other values can be saved as string
            else:
                FILE_INFO[stdName] = tagVal
        # element starts with capital letter and is not grouped with
        #   any numbers
        elif (tag.istitle() and tag.isalpha()):
            FILE_INFO['Element'] = tag

    # keep track of any parameters that were not found in filename
    invalidTags = []
    for tag in FILE_INFO:
        if not FILE_INFO.get(tag):
            print 'No info entered for', tag
            invalidTags.append(tag)
    
    print FILE_INFO
    # existence of invalidTags will be checked by MainMenu
    return invalidTags
