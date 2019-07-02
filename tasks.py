import os

from invoke import task
from lib import *

src_dir = os.path.abspath('./src')
tmp_dir = os.path.abspath('./tmp')
out_dir = os.path.abspath('./out')

@task
def clean(c, output = False):
    directories = [tmp_dir]
    if output:
        directories.append(out_dir)
    delete_directories(*directories)

@task
def build(c, language = '*', translation = 'pol'):
    create_directories(out_dir)
    
    for lang in get_language(directory=src_dir, language = language):
        print("[{lang.code}] {lang.name}: {lang.directory}".format(lang = lang))
        for doc in lang.documents:
            print("  - {filename}".format(
                filename = export_document(
                    document = doc,
                    tmpdir = tmp_dir,
                    outdir = out_dir)))
