#!/usr/bin/python3
#-*- coding: utf-8 -*-
import logging
import random
import re
import yattag
import uuid
import markdown
from pygiftparser import i18n
from utils import *
from answer import *
import sys

_ = i18n.language.gettext

# TODOS:
# - unittest
MARKDOWN_EXT = ['markdown.extensions.extra', 'markdown.extensions.nl2br', 'superscript']

# Url and blank lines (moodle format)
reURL=re.compile(r"(http://[^ ]+)",re.M)
reNewLine=re.compile(r'\n\n',re.M)

#WARNING MESSAGES
INVALID_FORMAT_QUESTION = "Vous avez saisi un quizz invalide"

# Sub regular expressions
ANYCHAR=r'([^\\=~#]|(\\.))'
OPTIONALFEEDBACK='(#(?P<feedback>'+ANYCHAR+'*))?'
OPTIONALFEEDBACK2='(#(?P<feedback2>'+ANYCHAR+'*))?'
GENERALFEEDBACK='(####(\[(?P<gf_markup>.*?)\])*(?P<generalfeedback>.*))?'
NUMERIC='[\d]+(\.[\d]+)?'


# Regular Expressions
reSepQuestions=re.compile(r'^\s*$')
reComment=re.compile(r'^//.*$')
reCategory=re.compile(r'^\$CATEGORY: (?P<cat>[/\w$]*)')

# Special chars
reSpecialChar=re.compile(r'\\(?P<char>[#=~:{}])')


# Heading
# Title is supposed to be at the begining of a line
reTitle=re.compile(r'^::(?P<title>.*?)::(?P<text>.*)$',re.M+re.S)
reMarkup=re.compile(r'^\s*\[(?P<markup>.*?)\](?P<text>.*)',re.M+re.S)
reAnswer=re.compile(r'^(?P<head>.*[^\\]){\s*(?P<answer>.*?[^\\]?)'+GENERALFEEDBACK+'}(?P<tail>.*)',re.M+re.S)

# numeric answers
reAnswerNumeric=re.compile(r'^#[^#]')
reAnswerNumericValue = re.compile(r'\s*(?P<value>'+NUMERIC+')(:(?P<tolerance>'+NUMERIC+'))?'+OPTIONALFEEDBACK)
reAnswerNumericInterval=re.compile(r'\s*(?P<min>'+NUMERIC+')(\.\.(?P<max>'+NUMERIC+'))'+OPTIONALFEEDBACK)
reAnswerNumericExpression = re.compile(r'\s*(?P<val1>'+NUMERIC+')((?P<op>:|\.\.)(?P<val2>'+NUMERIC+'))?'+OPTIONALFEEDBACK)

# Multiple choices only ~ symbols
reAnswerMultipleChoices = re.compile(r'\s*(?P<sign>=|~)(%(?P<fraction>-?'+NUMERIC+')%)?(?P<answer>('+ANYCHAR+')*)'+OPTIONALFEEDBACK)

# True False
reAnswerTrueFalse = re.compile(r'^\s*(?P<answer>(T(RUE)?)|(F(ALSE)?))\s*'+OPTIONALFEEDBACK+OPTIONALFEEDBACK2)

# Match (applies on 'answer' part of the reAnswerMultipleChoices pattern
reMatch = re.compile(r'(?P<question>.*)->(?P<answer>.*)')

############ Questions ################

class Question:
    """ Question class.

    About rendering: It is up to you! But it mostly depends on the type of the answer set. Additionnally if it has a tail and the answerset is a ChoicesSet, it can be rendered as a "Missing word".
    """
    def __init__(self,source,full,cat):
        """ source of the question without comments and with comments"""
        self.id = uuid.uuid4()
        self.source = source
        self.full = full
        self.cat = cat
        self.valid = True
        self.tail = ''
        self.generalFeedback = ""
        self.parse(source)

    def getId(self):
        """ get Identifier for the question"""
        return 'Q'+str(id(self)) # TODO process title

    def parse(self,source):
        """ parses a question source. Comments should be removed first"""
        # split according to the answer
        match = reAnswer.match(source)
        if not match:
            # it is a description
            self.answers = Description(None)
            self.__parseHead(source)
        else:
            self.tail=stripMatch(match,'tail')
            self.__parseHead(match.group('head'))
            self.generalFeedback = stripMatch(match,'generalfeedback')
            # replace \n
            self.generalFeedback = re.sub(r'\\n','\n',self.generalFeedback)
            self.generalFeedbackHTML = mdToHtml(self.generalFeedback)
            self.__parseAnswer(match.group('answer'))

    def __parseHead(self,head):
        # finds the title and the type of the text
        match = reTitle.match(head)
        if match:
            self.title = match.group('title').strip()
            textMarkup = match.group('text')
        else:
            self.title = head[:20] # take 20 first chars as a title
            textMarkup = head

        match = reMarkup.match(textMarkup)
        if match:
            self.markup = match.group('markup').lower()
            self.text = match.group('text').strip()
        else:
            self.markup = 'moodle'
            self.text = textMarkup.strip()
        # replace \n
        self.text = re.sub(r'\\n','\n',self.text)
        self.textHTML = markdown.markdown(self.text, MARKDOWN_EXT, output_format='xhtml')

    def __parseNumericText(self,text):
        m = reAnswerNumericInterval.match(text)
        if m :
             a = NumericAnswerMinMax(m)
        else :
            m = reAnswerNumericValue.match(text)
            if m:
                a = NumericAnswer(m)
            else :
                self.valid = False
                return None
        a.feedback = stripMatch(m,"feedback")
        return a

    def __parseNumericAnswers(self,answer):
        self.numeric = True;
        answers=[]
        for match in reAnswerMultipleChoices.finditer(answer):
            a = self.__parseNumericText(match.group('answer'))
            if not a:
                return
            # fractions
            if match.group('fraction') :
                a.fraction=float(match.group('fraction'))
            else:
                if match.group('sign') == "=":
                    a.fraction = 100
                else:
                    a.fraction = 0
            a.feedback = stripMatch(match,"feedback")
            answers.append(a)
        if len(answers) == 0:
            a = self.__parseNumericText(answer)
            if a:
                a.fraction=100
                answers.append(a)
        self.answers = NumericAnswerSet(self,answers)


    def __parseAnswer(self,answer):
        # Essay
        if answer=='':
            self.answers = Essay(self)
            return

        # True False
        match = reAnswerTrueFalse.match(answer)
        if match:
            self.answers = TrueFalseSet(self,match)
            return

        # Numeric answer
        if reAnswerNumeric.match(answer) != None:
            self.__parseNumericAnswers(answer[1:])
            return


        #  answers with choices and short answers
        answers=[]
        select = False
        short = True
        matching = True
        for match in reAnswerMultipleChoices.finditer(answer):
            a = AnswerInList(match)
            # one = sign is a select question
            if a.select: select = True
            # short answers are only = signs without fractions
            short = short and a.select and a.fraction == 100
            matching = matching and short and a.isMatching
            answers.append(a)

        if len(answers) > 0 :
            if matching:
                self.answers = MatchingSet(self,answers)
                self.valid = self.answers.checkValidity()
            elif short:
                self.answers = ShortSet(self,answers)
            elif select:
                self.answers = SelectSet(self,answers)
            else:
                self.answers = MultipleChoicesSet(self,answers)
                self.valid = self.answers.checkValidity()
        else:
            # not a valid question  ?
            logging.warning("Incorrect question "+self.full)
            self.valid = False

    def toHTML(self, doc=None,feedbacks=False):
        """ produces an HTML fragment, feedbacks controls the output of feedbacks"""
        if not self.valid: return ''
        if doc == None : doc=yattag.Doc()
        doc.asis('\n')
        doc.asis('<!-- New question -->')
        with doc.tag('form', klass='question'):
            with doc.tag('h3', klass='questiontitle'):
                doc.text(self.title)
            if (not feedbacks):
                if self.tail !='' :
                    with doc.tag('span', klass='questionTextInline'):
                        mdToHtml(self.text,doc)
                    with doc.tag('span', klass='questionAnswersInline'):
                        self.answers.toHTML(doc)
                    doc.text(' ')
                    doc.asis(markupRendering(self.tail,self.markup))
                else:
                    with doc.tag('div', klass='questiontext'):
                        mdToHtml(self.text,doc)
                    self.answers.toHTML(doc)
            if feedbacks:
                with doc.tag('div', klass='questiontext'):
                    mdToHtml(self.text,doc)
                self.answers.toHTMLFB(doc)
                if self.generalFeedback != '':
                    with doc.tag('div', klass='global_feedback'):
                        # gf = markdown.markdown(self.generalFeedback, MARKDOWN_EXT, output_format='xhtml')
                        doc.asis('<b><em>Feedback:</em></b><br/>')
                        doc.asis(self.generalFeedbackHTML)
                        # mdToHtml(self.generalFeedback, doc)
        return doc

    def toEDX(self):
        """
        produces an XML fragment for EDX
        """
        if not self.valid :
            logging.warning (INVALID_FORMAT_QUESTION ) #
            return ''
        return self.answers.toEDX()

    def myprint(self):
        print ("=========Question=========")
        if not self.valid:
            return
        print (self.answers.__class__)
        for key, val in self.__dict__.items():
            if key in ['full','source',"answer","valid"]:
                continue
            if key == 'answers':
                self.answers.myprint()
            else:
                print (key,':',val)
