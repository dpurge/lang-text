import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from .html_snippets import DialogAnonPhraseSnippet, DialogNamedPhraseSnippet

class LangText(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.register(TextBlockPreprocessor(md), 'lang_text_block', 25)
        md.preprocessors.register(DialogBlockPreprocessor(md), 'lang_dialog_block', 25)
        md.preprocessors.register(VocabularyBlockPreprocessor(md), 'lang_vocabulary_block', 25)
        
class TextBlockPreprocessor(Preprocessor):

    _pattern = re.compile(r"""
    ^~~~start-text~~~[ ]*\n
    (?P<text>.*?)(?<=\n)
    ~~~end-text~~~
    [ ]*$""", re.MULTILINE | re.DOTALL | re.VERBOSE)
    
    _snippet = r"""{before_text}<section class="text">{rendered_text}</section>{after_text}"""

    def __init__(self, md):
        super(TextBlockPreprocessor, self).__init__(md)
        self._md = md
    
    def run(self, lines):
        text = "\n".join(lines)
        while True:
            m = self._pattern.search(text)
            if m:
                rendered_text = self.render_text(m.group('text'))
                text = self._snippet.format(
                    before_text = text[:m.start()],
                    rendered_text = rendered_text,
                    after_text = text[m.end():])
            else:
                break
        return text.split("\n")
        
    def render_text(self, text):
        return self.md.convert(text)


class VocabularyBlockPreprocessor(Preprocessor):

    _pattern = re.compile(r"""
    ^~~~start-vocabulary~~~[ ]*\n
    (?P<text>.*?)(?<=\n)
    ~~~end-vocabulary~~~
    [ ]*$""", re.MULTILINE | re.DOTALL | re.VERBOSE)
    
    _snippet = r"""{before_text}<section class="vocabulary">{rendered_text}</section>{after_text}"""

    def __init__(self, md):
        super(VocabularyBlockPreprocessor, self).__init__(md)
        self._md = md
    
    def run(self, lines):
        text = "\n".join(lines)
        while True:
            m = self._pattern.search(text)
            if m:
                rendered_text = self.render_text(m.group('text'))
                text = self._snippet.format(
                    before_text = text[:m.start()],
                    rendered_text = rendered_text,
                    after_text = text[m.end():])
            else:
                break
        return text.split("\n")
        
    def render_text(self, text):
        rendered_text = ''
        if text:
            rendered_text += self.md.convert(text)
        if 'vocabulary' in self._md.Meta:
            items = []
            for item in self._md.Meta['vocabulary']:
                if not item.phrase:
                    continue
                buffer = []
                buffer.append('<dt class="vocabulary-item-term">')
                buffer.append(
                    '<span class="vocabulary-item-phrase">{}</span>'.format(
                        item.phrase))
                if item.lexcat:
                    buffer.append(
                        ' <span class="vocabulary-item-lexcat">{}</span>'.format(
                            item.lexcat))
                if item.transcription:
                    buffer.append(
                        ' <span class="vocabulary-item-transcription">[{}]</span>'.format(
                            item.transcription))
                buffer.append('</dt>')
                buffer.append('<dd class="vocabulary-item-definition">')
                buffer.append(item.translation)
                buffer.append('</dd>')
                
                items.append(''.join(buffer))
                
            rendered_text += '<dl class="vocabulary-data">{}</dl>'.format(
                '\n'.join(items))
        return rendered_text

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
                yield DialogAnonPhraseSnippet.format(
                        content = self.render_buffer(buffer))
                buffer = []
            
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
                yield DialogNamedPhraseSnippet.format(
                        person = person,
                        separator = separator,
                        content = self.render_buffer(buffer))
                buffer = []
            
            else:
                buffer.append(line)
                i += 1
            if i < maxlines: line = lines[i].rstrip()
        
        if buffer: yield self.render_buffer(buffer)
    
    def render_buffer(self, lines):
        return self.md.convert('\n'.join(lines).strip())
