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
        in_dialog = False
        block_dedent = None
        block_indent = None
        for line in lines:
            line = line.rstrip()
            
            if line == '~~~start-dialog~~~':
                if in_dialog:
                    throw('Cannot open dialog block twice!')
                yield '<div class="dialog">'
                in_dialog = True
                block_dedent = []
                block_indent = []
            elif line == '~~~end-dialog~~~':
                if not in_dialog:
                    throw('Cannot close dialog block because it has not been opened!')
                for i in self._render(block_dedent, block_indent):
                    if i:
                        yield i
                yield '</div>'
                block_indent = None
                block_dedent = None
                in_dialog = False
            else:
                if in_dialog:
                    # Start processing in dialog
                    stripped_line = line.lstrip()
                    is_indented = len(line) - len(stripped_line) > 0
                    
                    if is_indented or not stripped_line:
                        if block_indent or stripped_line:
                            block_indent.append(stripped_line)
                    else:
                        if block_indent or not stripped_line:
                            for i in self._render(
                                block_dedent, block_indent):
                                if i:
                                    yield i
                            block_dedent = []
                            block_indent = []
                        if block_dedent or stripped_line:
                            block_dedent.append(stripped_line)
                    # End processing in dialog
                else:
                    yield line

    def _render(self, block_dedent, block_indent):
        #if block_dedent:
        #    while not block_dedent[0]: del block_dedent[0]
        #    while not block_dedent[-1]: del block_dedent[-1]
    
        if block_indent \
            and len(block_dedent) == 1 \
            and block_dedent[0].endswith(':'):
            # person: phrase
            person = block_dedent[0][:-1]
            separator = block_dedent[0][-1]
            phrase = self._md.convert('\n'.join(block_indent))
            
            yield '<div class="person">{person}{separator} {phrase}</div>'.format(
                person = person,
                separator = separator,
                phrase = phrase)
        elif block_indent \
            and len(block_dedent) == 1 \
            and block_dedent[0] == '--':
            # -- phrase
            yield self._md.convert(
                '<div class="anonymous"">-- {phrase}</div>'.format(
                phrase = '\n'.join(block_indent)))
        elif not block_indent:
            # paragraph
            yield self._md.convert('\n'.join(block_dedent))
        else:
            raise Exception(
                "Unrecognized format in dialog:\nDedented:\n{dedented}\nIndented:\n{indented}".format(
                    dedented = '\n'.join(block_dedent),
                    indented = '\n'.join(block_indent)))
