import datetime
import urlparse

import configmanager.models

from configmanager import cmapi

class PageConstantTitle(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(PageConstantTitle)

def getTitleSeparators():
    return cmapi.getItemValue('titleseparator', '_|-')

def isConstantTitle(url, title):
    if not url:
        return False
    netloc = urlparse.urlparse(url).netloc
    key = netloc
    value = cmapi.getItemValue(key, {}, modelname=PageConstantTitle)
    record = value.get(title)
    if not record:
        record = {}
    count = record.get('c', 0)
    isconstant = count >= 3

    nnow = datetime.datetime.utcnow()
    record['c'] = count + 1
    record['u'] = nnow
    if len(value) > 20:
        for ik, iv in value.items():
            if (nnow - iv['u']).days >= 7:
                del value[ik]
    value[title] = record
    success = cmapi.saveItem(key, value, modelname=PageConstantTitle)
    return isconstant

