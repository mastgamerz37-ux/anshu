import glob
for f in glob.glob('actions/*.py'):
    content = open(f, encoding='utf8').read()
    content = content.replace('"gemini-2.5-flash"', '"gemini-2.0-flash"')
    content = content.replace('"gemini-2.5-flash-lite"', '"gemini-2.0-flash-lite-preview-02-05"')
    open(f, 'w', encoding='utf8').write(content)
