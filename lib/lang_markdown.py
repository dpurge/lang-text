import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class LangText(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.register(DialogBlockPreprocessorRe(md), 'dialog_block', 25)

class DialogBlockPreprocessorRe(Preprocessor):

    BlockPattern = re.compile(r'''
        (?P<DialogStart>~~~start-dialog~~~)
        (?P<DialogBody>(.*)*)
        (?P<DialogEnd>~~~end-dialog~~~)
    ''', re.MULTILINE | re.VERBOSE)

    def __init__(self, md):
        super(DialogBlockPreprocessorRe, self).__init__(md)
        self._md = md
    
    def run(self, lines):
        text = "\n".join(lines)
        while True:
            m = self.BlockPattern.search(text)
            if m:
                body = m.group('DialogBody')
                placeholder = self.md.htmlStash.store(body)
                #placeholder = self.md.htmlStash.store('xxx')
                text = '%s\n%s\n%s' % (text[:m.start()],
                                       placeholder,
                                       text[m.end():])
            else:
                break
        return text.split("\n")

class DialogBlockPreprocessor(Preprocessor):

    def __init__(self, md):
        super(DialogBlockPreprocessor, self).__init__(md)
        self._md = md
    
    def run(self, lines):
        i = 0
        in_dialog = False
        start = i
        while i < len(lines):
            line = lines[i].rstrip()
            if line == '~~~start-dialog~~~':
                if in_dialog:
                    throw('Cannot open dialog block twice!')
                yield '<div class="dialog">'
                start = i+1
                in_dialog = True
            elif line == '~~~end-dialog~~~':
                if not in_dialog:
                    throw('Cannot close dialog block because it has not been opened!')
                for l in self.render_dialog(lines[start:i]):
                    yield l
                yield '</div>'
                in_dialog = False
            elif in_dialog:
                pass
            else:
                yield line
            i += 1
        
    def render_dialog(self, lines):
        if not lines:
            return []
        
        indent = '  '
        buffer = []
        name = None
        separator = None
        
        was_blank = False
        was_indented = False
        had_separator = False
        
        is_anonumous_phrase = False
        is_named_phrase = False
        has_separator = False
        
        for line in lines:
        
            line = line.rstrip()
            is_blank = line == ''
            is_indented = line.startswith(indent)
            
            if line == '--':
                is_anonumous_phrase = True
            else:
                yield line
            
            was_blank = is_blank
            was_indented = is_indented
            had_separator = has_separator
    
    def render_dialog_bak(self, lines):
        indent = '  '
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if line:
                if line == '--':
                    buffer = []
                    i += 1
                    line = lines[i]
                    while line.startswith(indent):
                        buffer.append(line)
                        i += 1
                        line = lines[i]
                elif line.endswith(':'):
                    buffer = []
                else:
                    buffer = []
                    while line != '--' and not line.endswith(':'):
                        buffer.append(line)
                        line = lines[i].rstrip()
                        i += 1
