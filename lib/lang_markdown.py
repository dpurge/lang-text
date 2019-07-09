import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class LangText(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.register(DialogBlockPreprocessor(md), 'dialog_block', 25)

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
                yield '<section class="dialog">'
                start = i+1
                in_dialog = True
            elif line == '~~~end-dialog~~~':
                if not in_dialog:
                    throw('Cannot close dialog block because it has not been opened!')
                for l in self.render_dialog(lines[start:i]):
                    yield l
                yield '</section>'
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
        len_indent = len(indent)
        maxlines = len(lines)
        
        buffer = []
        i = 0; line = lines[i].rstrip()
        while i < maxlines:
            
            if line == '--' \
                and i < maxlines \
                and (lines[i+1].startswith(indent) or lines[i+1].strip()):
                
                if buffer:
                    yield self.render_buffer(buffer)
                    buffer = []
                separator = line
                
                i += 1
                while i < maxlines:
                    line = lines[i].rstrip()
                    if line.startswith(indent) or line == '':
                        buffer.append(line[len_indent:])
                    else:
                        break
                    i += 1
                yield '''
<div class="phrase-anonymous">
<div class="phrase-separator">--</div>
<div class="phrase-content">{content}</div>
</div>'''.format(
                        content = self.render_buffer(buffer))
                buffer = []
                #if i < maxlines:
                #    buffer.append(line)
            
            elif line.startswith('[') \
                and line.endswith(']:') \
                and i < maxlines \
                and (lines[i+1].startswith(indent) or lines[i+1].strip()):
                
                if buffer: yield self.render_buffer(buffer); buffer = []
                person = line[1:-2]
                separator = line[-1]
                
                i += 1
                while i < maxlines:
                    line = lines[i].rstrip()
                    if line.startswith(indent) or line == '':
                        buffer.append(line[len_indent:])
                    else:
                        break
                    i += 1
                yield '''\
<div class="phrase-named">
<div class="phrase-separator">\
<span class="person-name">{person}</span>\
<span class="separator">{separator}</span>\
</div>
<div class="phrase-content">{content}</div>
</div>'''.format(
                        person = person,
                        separator = separator,
                        content = self.render_buffer(buffer))
                buffer = []
                #if i < maxlines:
                #    buffer.append(line)
            
            else:
                buffer.append(line)
                i += 1
            if i < maxlines: line = lines[i].rstrip()
        
        if buffer: yield self.render_buffer(buffer)
    
    def render_buffer(self, lines):
        return self.md.convert('\n'.join(lines).strip())
