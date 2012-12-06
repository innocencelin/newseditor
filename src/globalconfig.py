from configmanager import cmapi

def getTitleSeparators():
    return cmapi.getItemValue('titleseparator', '_|-')

