import collections

Language = collections.namedtuple('Language',[
    'name',
    'code',
    'directory',
    'documents'])

Document = collections.namedtuple('Document',[
    'directory',
    'files'])