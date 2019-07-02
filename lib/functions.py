import os
import shutil
import glob
import json
import markdown
import jinja2

from .data_transfer import *

def create_directories(*directories):
    
    for directory in directories:
        if (not os.path.exists(directory)):
            print(
                "Creating directory: {directory}".format(
                    directory = directory))
            try:  
                os.makedirs(directory)
            except OSError:  
                print(
                    "Cannot create directory: {directory}".format(
                        directory = directory))

def delete_directories(*directories):
        
    for directory in directories:
        if (os.path.exists(directory)):
            print(
                "Deleting directory: {directory}".format(
                    directory = directory))
            shutil.rmtree(directory)

def get_document(directory):
    for docfile in glob.glob(
        os.path.join(directory, '*', 'document.json'), recursive=False):
        dir = os.path.dirname(docfile)
        with open(docfile, encoding='utf-8') as f:
            doc = json.loads(f.read())
        if doc['meta']['status'] != 'ready':
            continue
        files = glob.glob(
            os.path.join(dir, '*.md'), recursive=False)
        yield Document(
            format = doc['meta']['format'],
            version = doc['meta']['version'],
            language = doc['meta']['language'],
            tags = doc['meta']['tags'],
            directory = dir,
            files = files)
            
def export_document(document, tmpdir, outdir):
    
    templateLoader = jinja2.FileSystemLoader(
        searchpath=os.path.join(
            os.path.dirname(__file__), 'template'))
    templateEnv = jinja2.Environment(loader=templateLoader)
    md = markdown.Markdown()
        
    template = templateEnv.get_template(
        "{language}-{format}.html".format(
            language = document.language,
            format = document.format))
            
    html_file = os.path.join(tmpdir,
        '{filename}.html'.format(
            filename = os.path.basename(document.directory)))
    
    data = []
    for md_file in document.files:
        with open(md_file, encoding='utf-8') as f:
            md_text = f.read()
        data.append(md.convert(md_text))
    
    if not os.path.exists(tmpdir): os.makedirs(tmpdir)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(template.render(data = data))
    
    return html_file

def get_language(directory, language):
    
    for filename in glob.glob(
        os.path.join(directory, language, 'language.json'), recursive = True):
        
        with open(filename, encoding='utf-8') as f:
                lang = json.loads(f.read())
        if lang['meta']['status'] != 'ready':
            continue
        
        name = lang['data']['name']
        code = lang['data']['code']
        dir  = os.path.dirname(filename)
        documents = get_document(directory = dir)
        
        yield Language(
            name = name,
            code = code,
            directory = dir,
            documents = documents)
