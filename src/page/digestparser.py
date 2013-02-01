import re

from pagecommon import isTextParagraph

def parse(contentFormat, paragraphs):
    sentenceFormat = contentFormat.get('sentence')
    paragraphs = [paragraph for paragraph in paragraphs
                    if isTextParagraph(sentenceFormat, paragraph)]
    MIN_PARAGRAPH_SIZE = 20
    paragraphs = [paragraph for paragraph in paragraphs
                    if len(paragraph) >=  MIN_PARAGRAPH_SIZE]
    if paragraphs and isCopyrightParagraph(contentFormat, paragraphs[-1]):
        paragraphs = paragraphs[:-1]
    result = {}
    result['paragraphs'] = {}
    result['sentences'] = {}
    result['paragraphs']['first'] = paragraphs[0]
    sentences = getSentences(contentFormat, paragraphs[0])
    if sentences:
        result['sentences']['first'] = sentences[0]
    if len(paragraphs) > 1:
        result['paragraphs']['last'] = paragraphs[-1]
        sentences = getSentences(contentFormat, paragraphs[-1])
        if sentences:
            result['sentences']['last'] = sentences[-1]
    return result

def isCopyrightParagraph(contentFormat, text):
    copyrightPatterns = contentFormat.get('copyright')
    if not copyrightPatterns:
        return False
    for copyrightPattern in copyrightPatterns:
        if re.search(copyrightPattern, text, re.IGNORECASE|re.DOTALL):
            return True
    return False

def getSentences(contentFormat, text):
    sentenceEnds = contentFormat['sentence'].get('end')
    suffixStrip = None
    stripFormat = contentFormat.get('filter')
    if stripFormat:
        suffixStrips = stripFormat.get('suffix')
    MIN_SENTENCE = stripFormat.get('length', 10)
    start = 0
    sentences = []
    while True:
        minPos = -1
        for sentenceEnd in sentenceEnds:
            found = text.find(sentenceEnd, start)
            if found > 0 and (minPos < 0 or found < minPos):
                minPos = found
        if minPos < 0:
            break
        sentence = text[start:minPos + 1]
        if len(sentence) >= MIN_SENTENCE:
            sentences.append(sentence)
        start = minPos + 1
    return sentences

