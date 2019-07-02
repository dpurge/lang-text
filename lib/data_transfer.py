import collections

Language = collections.namedtuple('Language',[
    'name',
    'code',
    'directory',
    'documents'])

Document = collections.namedtuple('Document',[
    'format',
    'version',
    'language',
    'tags',
    'directory',
    'files'])