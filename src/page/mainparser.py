
def parse(pagePositions):
    contentelement = pagePositions.get('contentelement')
    publishedelement = pagePositions.get('publishedelement')
    if contentelement is None or publishedelement is None:
        return
    parents = []
    parent = contentelement
    while parent is not None:
        parents.append(parent)
        parent = parent.getparent()
    parent = publishedelement
    while parent is not None:
        if parent in parents:
            pagePositions['mainelement'] = parent
            break
        parent = parent.getparent()

