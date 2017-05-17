#!/usr/bin/python3
#-*- coding: utf-8 -*-
import logging
import random
import re
import yattag
import uuid
import markdown
from pygiftparser import i18n
import sys

_ = i18n.language.gettext

# TODOS:
# - unittest
MARKDOWN_EXT = ['markdown.extensions.extra', 'markdown.extensions.nl2br', 'superscript']

def stripMatch(match,s):
    if match.group(s):
        return match.group(s).strip()
    else:
        return ""

def mdToHtml(text,doc=None):
    """
    Transform txt in markdown to html
    """
    if not (text.isspace()):
        text = re.sub(r'\\n','\n',text)
        html_text = markdown.markdown(text, MARKDOWN_EXT, output_format='xhtml')
        # html_text = utils.add_target_blank(html_text)
        if doc :
            doc.asis(html_text)
            doc.text(' ')
            return
        else :
            return html_text

def moodleRendering(src):
    """ See https://docs.moodle.org/23/en/Formatting_text#Moodle_auto-format"""
    # blank lines are new paragraphs, url are links, html is allowed
    # quick and dirty conversion (don't closed p tags...)
    src = transformSpecials(src)
    src = reURL.sub(r'<a href="\1">\1</a>', src)
    src = reNewLine.sub(r'<p>',src)
    return src

def htmlRendering(src):
    return transformSpecials(src)

def markdownRendering(src):
    return markdown.markdown(transformSpecials(src), MARKDOWN_EXT)

def markupRendering(src,markup='html'):
    m = sys.modules[__name__]
    rendering=markup+'Rendering'
    if rendering in m.__dict__ :
        return getattr(m,rendering)(src)
    else:
        logging.warning('Rendering error: unknown markup language '+markup)
        return src

def transformSpecials(src):
    return reSpecialChar.sub(r'\g<char>',src)
