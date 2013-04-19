import datetime
import urlparse

from commonutil import dateutil
import configmanager.models
from configmanager import cmapi


class PageConstantTitle(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(PageConstantTitle)

def isConstantTitle(titleConfig, url, title, sideEffect):
    if not url:
        return False
    netloc = urlparse.urlparse(url).netloc
    key = netloc
    value = cmapi.getItemValue(key, {}, modelname=PageConstantTitle)
    record = value.get(title)
    if not record:
        record = {}
    count = record.get('c', 0)
    isconstant = count >= titleConfig.get('occurrence', 1)
    if sideEffect:
        nnow = datetime.datetime.utcnow()
        record['c'] = count + 1
        record['u'] = dateutil.getDateAs14(nnow)
        if len(value) > 20:
            for ik, iv in value.items():
                if (nnow - dateutil.parseDate14(iv['u'])).days >= titleConfig.get('cache.day', 7):
                    del value[ik]
        value[title] = record
        success = cmapi.saveItem(key, value, modelname=PageConstantTitle)
    return isconstant

