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
