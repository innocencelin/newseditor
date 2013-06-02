
from configmanager import cmapi

def getEditorFormat():
    return cmapi.getItemValue('editor.format', {})

def getSiteConfig():
    return cmapi.getItemValue('site',
        {'name': 'Site Name'})

def getI18N():
    return cmapi.getItemValue('i18n',
        {'home': 'Home'})

