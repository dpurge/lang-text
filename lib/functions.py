import os
import shutil
import glob
import json
import markdown
import jinja2
import datetime
import subprocess

from weasyprint import HTML
#from weasyprint import CSS
#from weasyprint.fonts import FontConfiguration

from .data_transfer import *
from .lang_markdown import *

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
            title = doc['data']['title'],
            subtitle = doc.get('data').get('subtitle'),
            gitversion = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8"),
            format = doc['meta']['format'],
            version = doc['meta']['version'],
            language = doc['meta']['language'],
            tags = doc['meta']['tags'],
            directory = dir,
            files = files)
            
def export_document(document, directory, translation):
    
    templateLoader = jinja2.FileSystemLoader(
        searchpath=os.path.join(
            os.path.dirname(__file__), 'template'))
    templateEnv = jinja2.Environment(loader=templateLoader)
    md = markdown.Markdown(extensions=[LangText()])
    
    data = []
    for md_file in document.files:
        with open(md_file, encoding='utf-8') as f:
            text = md.convert(f.read())
        
        meta = None
        vocabulary = []
        json_file = '{name}.json'.format(name = os.path.splitext(md_file)[0])
        if os.path.exists(json_file):
            with open(json_file, encoding='utf-8') as f:
                text_json = json.loads(f.read())
            meta = text_json.get('meta')
            for item in text_json.get('vocabulary'):
                vocabulary.append(VocabularyItem(
                    phrase = item.get('phrase'),
                    transcription = item.get('transcription'),
                    lexcat = item.get('category').get('lexical'),
                    translation = item.get('translation').get(translation)))
        
        data.append(Article(
            meta =  meta,
            text = text,
            vocabulary = vocabulary))
    
    document_template = templateEnv.get_template(
        "{language}-document.html".format(
            language = document.language))
    html = HTML(
        string = document_template.render(
            document = document,
            data = data))
    
    if not os.path.exists(directory): os.makedirs(directory)
    outfile = os.path.join(directory,
        '{filename}.pdf'.format(
            filename = os.path.basename(document.directory)))
    html.write_pdf(outfile)
    
    return outfile

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
