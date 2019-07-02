import os
import shutil
import glob
import json

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
        yield Document(
            directory = dir,
            files = None)

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
