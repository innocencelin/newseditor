
_MAX_LENGTH = 150

def parse(paragraphFormat, paragraphs):
    content = paragraphs[0]
    sentenceContains = paragraphFormat.get('contain')
    if not sentenceContains:
        return content[:_MAX_LENGTH]
    flag = sentenceContains[0]
    start = 0
    found = -1
    while start < _MAX_LENGTH:
        index = content.find(flag, start)
        if index < 0 or index > _MAX_LENGTH:
            break
        found = index + len(flag)
        start = found + 1
    if found > 0:
        return  content[:found].strip()
    return content[:_MAX_LENGTH].strip()

