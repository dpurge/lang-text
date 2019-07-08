import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class LangText(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.register(DialogBlockPreprocessor(md), 'dialog_block', 25)

class DialogBlockPreprocessor(Preprocessor):

    PATTERN = re.compile(r'''
^~{3,}start-dialog~{3,}[ ]*
(?P<dialog>.*?)
^~{3,}end-dialog~{3,}[ ]*$
''', re.MULTILINE | re.DOTALL | re.VERBOSE)

    def __init__(self, md):
        super(DialogBlockPreprocessor, self).__init__(md)
    
    def run(self, lines):
        text = "\n".join(lines)
        while True:
            m = self.PATTERN.search(text)
            if m:
                dialog = self._render(m.group('dialog'))
                placeholder = self.md.htmlStash.store(dialog)
                text = '{start}\n{content}\n{end}'.format(
                    start = text[:m.start()],
                    content = placeholder,
                    end = text[m.end():])
            else:
                break
        return text.split("\n")
    
    def _render(self, text):
        pattern = re.compile(r'''
(?P<name>^[^:]+)
:[ ]*
(?P<phrase>(\n[ ]{2,}.*)+)
''', re.MULTILINE | re.VERBOSE)
        content = []
        for m in re.finditer(pattern, text):
            name = m.group('name').strip()
            phrase = m.group('phrase').strip()
            content.append('<div>{name}: {phrase}<div>'.format(name=name, phrase=phrase))
        return '<div class="dialog">\n{content}\n</div>'.format(content = '\n'.join(content))