"""
The main purpose is to identify the content element.
It is the core feature, and other modules depend on its result.
"""
import logging
import math
import re

import pyquery

from commonutil import lxmlutil

def _getMainElement(titleElement):
    parent = titleElement
    p_parent = titleElement.getparent()
    if p_parent is None:
        return None

    result = []
    while p_parent is not None:
        len1 = len(lxmlutil.getCleanText(parent))
        len2 = len(lxmlutil.getCleanText(p_parent))
        # title and parent element should as close as possible.
        weight = (len2 - len1) - math.pow(titleElement.sourceline - p_parent.sourceline, 2)
        result.append((weight, p_parent))
        parent = p_parent
        p_parent = p_parent.getparent()

    return max(result, key=lambda item: item[0])

def parse(titleElements):
    result = []
    for titleElement in titleElements:
        mainelementResult = _getMainElement(titleElement)
        result.append((titleElement, mainelementResult))
    maxitem = max(result, key=lambda item: item[1][0])
    return maxitem[0], maxitem[1][1] # title, main

