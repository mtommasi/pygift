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
import sys

_ = i18n.language.gettext

############# Sets of answers ###############
# Can be a singleton, empty or not or just the emptyset!

class AnswerSet:
    def __init__(self,question):
        self.question = question
        self.valid = True
        self.cc_profile = 'ESSAY' # need in toIMS.py
        self.max_att = '1'


    def myprint(self):
        print (self.__class__)


    def toHTML(self,doc):
        pass

    def toHTMLFB(self,doc):
        pass

#IMS
    def listInteractionsIMS(self,doc,tag,text):
        pass

    def possiblesAnswersIMS(self,doc,tag,text):
        pass

    def toIMSFB(self,doc,tag,text):
        pass

    def cardinaliteIMS(self,doc,tag,text,rcardinality='Single'):
        pass

#EDX
    def toEDX(self):
        assert (self.question)
        doc = yattag.Doc()
        with doc.tag("problem", display_name=self.question.title, max_attempts=self.max_att):
            with doc.tag("legend"):
                mdToHtml(self.question.text,doc)
            self.scriptEDX(doc)
            self.ownEDX(doc)
            # FIXME : Ajouter un warning ici si rien n'est renvoyé
            if (len(self.question.generalFeedback) > 1):
                with doc.tag("solution"):
                    with doc.tag("div", klass="detailed-solution"):
                        mdToHtml(self.question.generalFeedback,doc)
        return doc.getvalue()

    def ownEDX(self,doc):
        pass

    def scriptEDX(self,doc):
        pass


class Essay(AnswerSet):
    """ Empty answer """
    def __init__(self,question):
        AnswerSet.__init__(self,question)
        self.max_att = ''

    def toHTML(self, doc):
        with doc.tag('textarea',name=self.question.getId(),placeholder=_('Your answer here')):
            doc.text('')

    def possiblesAnswersIMS(self,doc,tag,text):
        with doc.tag('response_str', rcardinality='Single', ident='response_'+str(self.question.id)):
            doc.stag('render_fib', rows=5, prompt='Box', fibtype="String")

    def scriptEDX(self,doc):
        with doc.tag("script", type="loncapa/python"):
            doc.text("""
import re
def checkAnswerEssay(expect, ans):
    response = re.search('', ans)
    if response:
        return 1
    else:
        return 0
            """)
        doc.asis('<span id="'+str(self.question.id)+'"></span>')
        with doc.tag("script", type="text/javascript"):
            doc.asis("""
    /* The object here is to replace the single line input with a textarea */
    (function() {
    var elem = $("#"""+str(self.question.id)+"""")
        .closest("div.problem")
        .find(":text");
    /* There's CSS in the LMS that controls the height, so we have to override here */
    var textarea = $('<textarea style="height:150px" rows="20" cols="70"/>');
    console.log(elem);
    console.log(textarea);
    //This is just a way to do an iterator in JS
    for (attrib in {'id':null, 'name':null}) {
        textarea.attr(attrib, elem.attr(attrib));
    }
    /* copy over the submitted value */
    textarea.val(elem.val())
    elem.replaceWith(textarea);

    })();
            """)

    # def ownEDX(self,doc):
        with doc.tag("customresponse", cfn="checkAnswerEssay"):
            doc.asis('<textline size="40" correct_answer="" label="Problem Text"/>')


class Description(AnswerSet):
    """ Emptyset, nothing!"""
    def __init__(self,question):
        AnswerSet.__init__(self,question)
        self.cc_profile = 'DESCRIPTION'

    def toHTML(self,doc):
        return

    def toHTMLFB(self,doc):
        return


class TrueFalseSet(AnswerSet):
    """ True or False"""
    # Q: should I introduce Answer variables?
    def __init__(self,question,match):
        AnswerSet.__init__(self,question)
        self.answer = match.group('answer').startswith('T')
        self.feedbackWrong = stripMatch(match,"feedback")
        self.feedbackCorrect = stripMatch(match,"feedback2")
        self.cc_profile = 'TRUEFALSE'

    def myprint(self):
        print (">TrueFalse:",self.answer,"--",self.feedbackWrong,"--",self.feedbackCorrect)

    def toHTML(self,doc):
        with doc.tag('ul'):
            with doc.tag('li'):
                doc.input(name = self.question.getId(), type = 'radio', value = True)
                doc.text(_('True'))
            with doc.tag('li'):
                doc.input(name = self.question.getId(), type = 'radio', value = False)
                doc.text(_('False'))

    def toHTMLFB(self,doc):
        with doc.tag('div', klass='answerFeedback'):
            doc.text(self.answer)
        if self.feedbackCorrect :
            with doc.tag('div', klass='correct_answer'):
                doc.asis(markupRendering(self.feedbackCorrect,self.question.markup))
        if self.feedbackWrong :
            with doc.tag('div', klass='wrong_answer'):
                doc.asis(markupRendering(self.feedbackWrong,self.question.markup))


    def ownEDX(self, doc):
        with doc.tag("multiplechoiceresponse"):
            with doc.tag("choicegroup", type="MultipleChoice"):
                if self.feedbackCorrect :
                    correct = 'true'
                    wrong = 'false'
                else :
                    correct = 'false'
                    wrong = 'true'
                with doc.tag("choice", correct=correct):
                    doc.text('Vrai')
                    if self.feedbackCorrect:
                        doc.asis("<choicehint>"+self.feedbackCorrect+"</choicehint>")
                with doc.tag("choice", correct=wrong):
                    doc.text('Faux')
                    if self.feedbackWrong:
                        doc.asis("<choicehint>"+self.feedbackWrong+"</choicehint>")

    def cardinaliteIMS(self,doc,tag,text,rcardinality='Single'):
        with tag('response_lid', rcardinality=rcardinality, ident='response_'+str(self.question.id)):
            with tag('render_choice', shuffle='No'):
                with tag('response_label', ident='answer_'+str(self.question.id) ):
                    with tag('material'):
                        with tag('mattext', texttype="text/html"):
                            if self.feedbackWrong:
                                text(self.feedbackWrong)
                            elif self.feedbackCorrect:
                                text(self.feedbackCorrect)


class NumericAnswerSet(AnswerSet):
    """ """
    def __init__(self,question,answers):
        AnswerSet.__init__(self,question)
        self.answers = answers

    def toHTML(self,doc):
        doc.input(name = self.question.getId(), type = 'number', step="any")

    def toHTMLFB(self,doc):
        with doc.tag('div', klass='answerFeedback'):
            with doc.tag('ul'):
                for a in self.answers:
                    if a.fraction>0:
                        aklass="right_answer"
                    else:
                        aklass="wrong_answer"
                    with doc.tag('li', klass=aklass):
                        doc.asis(a.toHTMLFB())
                        if a.feedback:
                            doc.asis(" &#8669; "+markupRendering(a.feedback,self.question.markup))

    def ownEDX(self,doc):
        #FIXME : Problème pour le multi answer NUMERIC, ne gère qu'une réponse
        correctAnswer = []
        for a in self.answers:
            if a.fraction > 0:
                correctAnswer.append(a)
        if len(correctAnswer) == 0:
            logging.warning('')
            return
        elif len(correctAnswer) == 1:
            correctAnswer[0].ownEDX(doc)

#IMS
    def toIMSFB(self,doc,tag,text):
        for id_a, answer in enumerate(self.answers):
            if answer.feedback:
                with tag('itemfeedback', ident='feedb_'+str(id_a)):
                    with tag('flow_mat'):
                        with tag('material'):
                            with tag('mattext', texttype='text/html'):
                                text(markupRendering(answer.feedback,self.question.markup))

    # def scriptEDX(self,doc):
    #     with doc.tag('script', type="loncapa/python"):
    #         doc.text("computed_response = math.sqrt(math.fsum([math.pow(math.pi,2), math.pow(math.e,2)]))")



class MatchingSet(AnswerSet):
    """  a mapping (list of pairs) """
    def __init__(self,question,answers):
        AnswerSet.__init__(self,question)
        self.answers = answers
        self.possibleAnswers = [a.answer for a in self.answers]
        self.cc_profile = 'MATCH'

    def checkValidity(self):
        valid = True
        for a in self.answers:
            valid = valid and a.isMatching
        return valid

    def myprint(self):
        print ("Answers :")
        for a in self.answers:
            a.myprint()
            print ('~~~~~')

    def toHTML(self,doc):
        with doc.tag('table'):
            for a in self.answers:
                with doc.tag('tr'):
                    with doc.tag('td'):
                        doc.text(a.question+" ")
                    with doc.tag('td'):
                        # should be distinct to _charset_ and isindex,...
                        n = self.question.getId() + a.question
                        with doc.tag('select', name= n):
                            random.shuffle(self.possibleAnswers)
                            for a in self.possibleAnswers:
                                with doc.tag('option'):
                                    doc.text(" "+a)

    def toHTMLFB(self,doc):
        with doc.tag('div', klass='groupedAnswerFeedback'):
            with doc.tag('ul'):
                for a in self.answers:
                    with doc.tag('li', klass="right_answer"):
                        doc.text(a.question)
                        doc.asis(" &#8669; ")
                        doc.text(a.answer)

    def ownEDX(self,doc):
        for a in self.answers:
            with doc.tag('h2'):
                doc.text(a.question+" ")
            with doc.tag('optionresponse'):
                options = '\"('
                random.shuffle(self.possibleAnswers)
                for a2 in self.possibleAnswers:
                    options += "'"+a2+"'"+','
                options += ')\"'
                doc.asis("<optioninput label=\""+a.question+"\" options="+options+"  correct=\""+a.answer+"\" ></optioninput>")



class ChoicesSet(AnswerSet):
    """ One or many choices in a list (Abstract)"""
    def __init__(self,question,answers):
        AnswerSet.__init__(self,question)
        self.answers = answers

    def myprint(self):
        print ("Answers :")
        for a in self.answers:
            a.myprint()
            print ('~~~~~')

#IMS
    def listInteractions(self,doc,tag,text):
        for id_a, answer in enumerate(self.answers):
            score = 0
            if answer.fraction == 100:
                title = 'Correct'
                score = 100
            else:
                title = ''
                score = answer.fraction
            with tag('respcondition', title=title):
                with tag('conditionvar'):
                    with tag('varequal', respident='response_'+str(self.question.id)): # respoident is id of response_lid element
                        text('answer_'+str(self.question.id)+'_'+str(id_a))
                with tag('setvar', varname='SCORE', action='Set'):
                    text(score)
                doc.stag('displayfeedback', feedbacktype='Response', linkrefid='feedb_'+str(id_a))

    def cardinaliteIMS(self,doc,tag,text,rcardinality='Single'):
        with tag('response_lid', rcardinality=rcardinality, ident='response_'+str(self.question.id)):
            with tag('render_choice', shuffle='No'):
                for id_a, answer in enumerate(self.answers):
                    with tag('response_label', ident='answer_'+str(self.question.id)+'_'+str(id_a)):
                        with tag('material'):
                            with tag('mattext', texttype="text/html"):
                                text(answer.answer)

    def toIMSFB(self,doc,tag,text):
        for id_a, answer in enumerate(self.answers):
            if answer.feedback:
                with tag('itemfeedback', ident='feedb_'+str(id_a)):
                    with tag('flow_mat'):
                        with tag('material'):
                            with tag('mattext', texttype='text/html'):
                                text(markupRendering(answer.feedback,self.question.markup))


class ShortSet(ChoicesSet):
    """ A single answer is expected but several solutions are possible """
    def __init__(self,question,answers):
        ChoicesSet.__init__(self,question,answers)
        self.cc_profile = 'MISSINGWORD'

    def toHTML(self,doc):
        doc.input(name=self.question.getId(), type = 'text')

    def toHTMLFB(self,doc):
        with doc.tag('div', klass='groupedAnswerFeedback'):
            with doc.tag('ul'):
                for a in self.answers:
                    with doc.tag('li', klass="right_answer"):
                        doc.text(a.answer)
                        if a.feedback:
                            doc.asis(" &#8669; "+markupRendering(a.feedback,self.question.markup))

    def ownEDX(self,doc):
        with doc.tag('stringresponse', answer = self.answers[0].answer, type = 'ci'):
            if len(self.answers) > 1:
                for i,a in enumerate(self.answers):
                    if i > 0 :
                        doc.asis('<additional_answer answer='+ a.answer +'></additional_answer>')
            doc.asis("<texline size='20' />")




class SelectSet(ChoicesSet):
    """ One  choice in a list"""
    def __init__(self,question,answers):
        ChoicesSet.__init__(self,question,answers)
        self.cc_profile = 'MULTICHOICE'

    def toHTML(self,doc):
        with doc.tag('div', klass='groupedAnswer'):
            with doc.tag("ul", klass='multichoice'):
                for a in self.answers:
                    with doc.tag("li"):
                        doc.input(name = "name", type = 'radio')
                        doc.asis(markupRendering(a.answer, self.question.markup))

    def toHTMLFB(self,doc):
        with doc.tag('div', klass='groupedAnswerFeedback'):
            with doc.tag("ul", klass='multichoice'):
                for a in self.answers:
                    if a.fraction>0:
                        aklass="right_answer"
                    else:
                        aklass="wrong_answer"
                    with doc.tag('li', klass=aklass):
                        doc.asis(markupRendering(a.answer,self.question.markup))
                        if a.feedback:
                            doc.asis(" &#8669; "+markupRendering(a.feedback,self.question.markup))

    def ownEDX(self,doc):
        with doc.tag("multiplechoiceresponse"):
            with doc.tag("choicegroup", type="MultipleChoice"):
                for a in self.answers:
                    if a.fraction>0:
                        korrect = 'true'
                    else :
                        korrect = 'false'
                    with doc.tag("choice", correct=korrect):
                        doc.text(a.answer)
                        if (a.feedback) and (len(a.feedback)> 1):
                            doc.asis("<choicehint>"+a.feedback+"</choicehint>")



class MultipleChoicesSet(ChoicesSet):
    """ One or more choices in a list"""
    def __init__(self,question,answers):
        ChoicesSet.__init__(self,question,answers)
        self.cc_profile = 'MULTIANSWER'

    def checkValidity(self):
        """ Check validity the sum f fractions should be 100 """
        total = sum([ a.fraction for a in self.answers if a.fraction>0])
        return total >= 99 and total <= 100

    def toHTML(self,doc):
        with doc.tag('div', klass='groupedAnswer'):
            with doc.tag('ul', klass='multianswer'):
                for a in self.answers:
                    with doc.tag('li'):
                        doc.input(name = self.question.getId(), type = 'checkbox')
                        doc.asis(markupRendering(a.answer,self.question.markup))

    def toHTMLFB(self,doc):
        with doc.tag('div', klass='groupedAnswerFeedback'):
            with doc.tag('ul', klass='multianswer'):
                for a in self.answers:
                    if a.fraction>0:
                        aklass="right_answer"
                    else:
                        aklass="wrong_answer"
                    with doc.tag('li', klass=aklass):
                        doc.asis(markupRendering(a.answer,self.question.markup))
                        if  a.feedback:
                            doc.asis(" &#8669; "+markupRendering(a.feedback,self.question.markup))

    def ownEDX(self,doc):
        with doc.tag("choiceresponse", partial_credit="EDC"):
            with doc.tag("checkboxgroup"):
                for a in self.answers:
                    if a.fraction>0:
                        korrect = 'true'
                    else :
                        korrect = 'false'
                    with doc.tag("choice", correct=korrect):
                        doc.text(a.answer)
                        if (a.feedback) and (len(a.feedback)> 1):
                            with doc.tag("choicehint", selected="true"):
                                doc.text(a.answer+" : "+a.feedback)

    def cardinaliteIMS(self,doc,tag,text):
        ChoicesSet.cardinaliteIMS(self,doc,tag,text,'Multiple')

    def listInteractions(self,doc,tag,text):
        with tag('respcondition', title="Correct", kontinue='No'):
            with tag('conditionvar'):
                with tag('and'):
                    for id_a, answer in enumerate(self.answers):
                        score = 0
                        try:
                            score = answer.fraction
                        except:
                            pass
                        if score <= 0:
                            with tag('not'):
                                with tag('varequal', case='Yes', respident='response_'+str(self.question.id)): # respoident is id of response_lid element
                                    text('answer_'+str(self.question.id)+'_'+str(id_a))
                        else:
                            with tag('varequal', case='Yes', respident='response_'+str(self.question.id)): # respoident is id of response_lid element
                                text('answer_'+str(self.question.id)+'_'+str(id_a))
            with tag('setvar', varname='SCORE', action='Set'):
                text('100')
            doc.stag('displayfeedback', feedbacktype='Response', linkrefid='general_fb')
        for id_a, answer in enumerate(self.answers):
            with tag('respcondition', kontinue='No'):
                with tag('conditionvar'):
                    with tag('varequal', respident='response_'+str(self.question.id), case="Yes"):
                        text('answer_'+str(self.question.id)+'_'+str(id_a))
                doc.stag('displayfeedback', feedbacktype='Response', linkrefid='feedb_'+str(id_a))



################# Single answer ######################
class Answer:
    """ one answer in a list"""
    pass


class NumericAnswer(Answer):
    def __init__(self,match):
        self.value = float(match.group('value'))
        if match.group('tolerance'):
            self.tolerance = float( match.group('tolerance') )
        else:
            self.tolerance = 0

    def toHTMLFB(self):
        return str(self.value)+"&#177;"+str(self.tolerance)

    def ownEDX(self, doc):
        with doc.tag('numericalresponse', answer = str(self.value)):
            if self.tolerance != 0.0:
                doc.asis("<responseparam type='tolerance' default='"+str(self.tolerance)+"' />")
            doc.asis("<formulaequationinput />")

class NumericAnswerMinMax(Answer):
    def __init__(self,match):
        self.mini = match.group('min')
        self.maxi = match.group('max')

    def toHTMLFB(self):
        return _('Between')+" "+str(self.mini)+" "+_('and')+" "+str(self.maxi)

    def ownEDX(self, doc):
        with doc.tag('numericalresponse', answer = "["+str(self.mini)+","+str(self.maxi)+"]"):
            doc.asis("<formulaequationinput />")


class AnswerInList(Answer):
    """ one answer in a list"""
    def __init__(self,match):
        if not match : return
        self.answer = match.group('answer').strip()
        self.feedback = stripMatch(match,"feedback")
        # At least one = sign => selects (radio buttons)
        self.select = match.group('sign') == "="

        # fractions
        if match.group('fraction') :
            self.fraction=float(match.group('fraction'))
        else:
            if match.group('sign') == "=":
                self.fraction = 100
            else:
                self.fraction = 0

        # matching
        match = reMatch.match(self.answer)
        self.isMatching = match != None
        if self.isMatching:
            self.answer = match.group('answer')
            self.question = match.group('question')

    def myprint(self):
        for key, val in self.__dict__.items():
            print ('>',key,':',val)
