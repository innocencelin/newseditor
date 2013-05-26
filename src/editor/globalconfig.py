
from configmanager import cmapi

def getEditorFormat():
    return cmapi.getItemValue('editor.format', {})

