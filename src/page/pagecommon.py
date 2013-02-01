
def isTextParagraph(sentenceFormat, text):
    if not sentenceFormat:
        return False
    sentenceEnds = sentenceFormat.get('end')
    sentenceContains = sentenceFormat.get('contain')
    lastCharacter = text[-1]
    if lastCharacter in sentenceEnds:
        return True
    for contain in sentenceContains:
        if contain in text:
            return True
    return False

