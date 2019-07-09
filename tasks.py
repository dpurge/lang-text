import os

from invoke import task
from lib import *

src_dir = os.path.abspath('./src')
tmp_dir = os.path.abspath('./tmp')
out_dir = os.path.abspath('./out')

@task
def test(c):
    import markdown
    from lib.lang_markdown import LangText
    text = """
# Title

~~~start-dialog~~~
~~~end-dialog~~~

~~~start-dialog~~~   

Zenek:
  Ja to mówię, Zenek.
  Byłem tu.
  
  Następny paragraf.

Franek:
  Ja to mówię, Franek.
~~~end-dialog~~~  

Paragraph text.

~~~start-dialog~~~   
Zenek:
  Ja to mówię, Zenek.

(Krótki komentarz)

Franek:
  Ja to mówię, Franek.
~~~end-dialog~~~  

Paragraph text.

~~~start-dialog~~~
--
  Ja to mówię, Zenek.

(Krótki komentarz)

--
  Ja to mówię, Franek.
~~~end-dialog~~~
    """
    print(markdown.markdown(text, extensions=[LangText()]))

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
                    directory = os.path.join(out_dir, lang.code),
                    translation = translation)))
