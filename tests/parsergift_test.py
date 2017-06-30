#! /usr/bin/python3
# encoding=utf8

# problem with utf8 loading
import sys
import os
import yattag
from bs4 import BeautifulSoup
import unittest

import logging

if sys.version_info[0] == 3:
    pass
else:
    reload(sys)
    sys.setdefaultencoding('utf8')

sys.path.append('..')
from pygiftparser import parser as pygift

if sys.version_info[0] == 3:
    from io import StringIO
else:
    from StringIO import StringIO

# Ignore Warning
logger = logging.getLogger()
logger.setLevel(40)


_ = pygift.i18n.language.gettext


"""
    Test File for pygiftparser module
    =================================

    Here is a test file to test pygiftparser module
    This file test :
        - The parsing of a Gift activity into a python object (questiontext, answers, feedback,etc...)
        - Transformation of a Gift activity into HTML

    How to use this file ?
    ---------------------
    In your terminal, use the command :
        >> $ python parsergift_test.py
        or
        >> $ pytest parsergift_test.py


"""


class GiftParsingHTMLTestCase(unittest.TestCase):

    def testUnChoix(self):
        io_gift = StringIO(u"""
::Pourquoi représenter avec des nombres ?::
Pourquoi faut-il <strong>représenter</strong> les textes, images, sons, etc, *par* des nombres dans un ordinateur ?
{
~C'est un choix <strong>industriel</strong>.#Non, les industriels n'avaient pas le choix.
~Les ordinateurs ont été inventés par des mathématiciens.#Non, les mathématiciens savent manipuler autre chose que des nombres, et les ordinateurs sont le fruit de l'interaction entre de nombreuses sciences.
=Tout ordinateur est fondamentalement une machine qui calcule avec des
nombres.#Oui, comme un ordinateur ne manipule que des nombres,
tout doit être représenté sous forme de nombres être manipulé par un ordinateur.
####Un ordinateur ne manipule que des nombres, tout doit donc être représenté sous forme de nombres pour qu'il puisse le manipuler. }
""")
        questions = pygift.parseFile(io_gift)
        io_gift.close()

        d = yattag.Doc()
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d, True)

        for q in questions:
            q.toHTML(d, False)

        #Vérifie qu'une seule question a bien été créée
        self.assertEqual(len(questions),1,"More than one Question for 'Test un choix'")

        # TEST HTML
        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            self.assertEqual(str(form.h3.contents[0]), "Pourquoi représenter avec des nombres ?")
            for j,div in enumerate(form.find_all('div')):
                if j == 0 :
                    self.assertEqual(div['class'][0], u'questiontext',"Not div or not good class for 1rst div")
                    self.assertEqual(str(div.contents[0]), u"<p>Pourquoi faut-il <strong>représenter</strong> les textes, images, sons, etc, <em>par</em> des nombres dans un ordinateur ?</p>")
                if (j == 1):
                    if (i == 0):
                        self.assertEqual(div['class'][0], u'groupedAnswerFeedback')
                        # print(div.contents[0])
                        self.assertEqual(str(div.contents[0]), u"""<ul class="multichoice"><li class="wrong_answer"><p>C'est un choix <strong>industriel</strong>.</p> ⇝ <p>Non, les industriels n'avaient pas le choix.</p></li><li class="wrong_answer"><p>Les ordinateurs ont été inventés par des mathématiciens.</p> ⇝ <p>Non, les mathématiciens savent manipuler autre chose que des nombres, et les ordinateurs sont le fruit de l'interaction entre de nombreuses sciences.</p></li><li class="right_answer"><p>Tout ordinateur est fondamentalement une machine qui calcule avec des<br/>
nombres.</p> ⇝ <p>Oui, comme un ordinateur ne manipule que des nombres,<br/>
tout doit être représenté sous forme de nombres être manipulé par un ordinateur.</p></li></ul>""")
                    elif (i == 1):
                        self.assertEqual(div['class'][0], u'groupedAnswer')
                if (j == 2):
                        self.assertEqual(div['class'][0], u'global_feedback')
                        self.assertEqual(str(div.contents[0]), "<b><em>Feedback:</em></b>")
                        self.assertEqual(str(div.contents[2]), "<p>Un ordinateur ne manipule que des nombres, tout doit donc être représenté sous forme de nombres pour qu'il puisse le manipuler.</p>")
            self.assertEqual(form.ul['class'][0], u'multichoice')
            nb_li = len(form.find_all('li'))
            self.assertEqual(nb_li,3)
            for j, li in enumerate(soup.find_all('li')):
                if j == 0:
                    self.assertEqual(str(li.contents[0]), "<p>C'est un choix <strong>industriel</strong>.</p>")
                if j == 1:
                    self.assertEqual(str(li.contents[0]), "<p>Les ordinateurs ont été inventés par des mathématiciens.</p>")
                if j == 2:
                    self.assertEqual(str(li.contents[0]), "<p>Tout ordinateur est fondamentalement une machine qui calcule avec des<br/>\nnombres.</p>")


        print("[GiftParsingHTMLTestCase]-- check_single_answer OK --")


    def testMultiple(self):
        io_gift = StringIO("""
::Parmi ces personnes, nommez-en deux qui sont enterrées dans la Grant's tomb. ::{
   ~%-100%Personne # NOMMEZ EN DEUX
   ~%50%Grant # Et de un
   ~%50%L'épouse de Grant # Et de deux
   ~%-100%Le père de Grant # Perdu !
####C'était Grant ainsi que sa femme
}""")
        questions = pygift.parseFile(io_gift)
        io_gift.close()

        d = yattag.Doc()
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d, True)

        for q in questions:
            q.toHTML(d, False)

        self.assertEqual(len(questions),1,"More than one Question for 'TestMultiple'")

        # TEST HTML
        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            for j,div in enumerate(form.find_all('div')):
                if j == 0 :
                    self.assertEqual(div['class'][0], u'questiontext',"Not div or not good class for 1rst div")
                if (j == 1):
                    if (i == 0):
                        self.assertEqual(div['class'][0], u'groupedAnswerFeedback')
                    elif (i == 1):
                        self.assertEqual(div['class'][0], u'groupedAnswer')
                if (j == 2):
                        self.assertEqual(div['class'][0], u'global_feedback')
                        self.assertEqual(str(div.contents[0]), "<b><em>Feedback:</em></b>")
                        self.assertEqual(str(div.contents[2]), "<p>C'était Grant ainsi que sa femme</p>")
            self.assertEqual(form.ul['class'][0], u'multianswer')
            nb_li = len(form.find_all('li'))
            self.assertEqual(nb_li,4)


        print("[GiftParsingHTMLTestCase]-- check_multiple_answer OK --")


    def testSimpleText(self):
        io_gift = StringIO("""
::Le numérique concerne tout le monde::
**Quels étudiants sont concernés par le numérique ?**
Le numérique concerne évidemment les étudiants en informatique et plus généralement les étudiants des filières scientifiques.  Mais vous qui êtes inscrits dans une université de sciences humaines et sociales, êtes-vous concernés ?
Choisissez au moins 3 des domaines suivants et faites des recherches pour voir en quoi ils sont impactés par le numérique : les médias, la santé, l'histoire, la sociologie, la linguistique, les arts, la culture, l'enseignement, l'archéologie.
Faites une synthèse en quelques lignes de vos recherches en précisant les domaines auxquels vous vous êtes intéressés. Indiquez les liens des sites sur lesquels vous avez trouvé ces informations. La liste est non exhaustive et vous pouvez vous intéresser à d'autres domaines.
{####
# Le numérique concerne tout le monde
Ces recherches ont dû vous convaincre, si c'était nécessaire, que le numérique **n'est pas réservé** aux informaticiens, il concerne tout le monde, toutes les disciplines.
S'agissant plus particulièrement des **sciences humaines**, la prise en compte du numérique a fait évoluer les champs disciplinaires pour faire apparaître ce qu'on appelle les **humanités numériques** ( *digital humanities* en anglais).
Voici quelques exemples que nous vous proposons, n'hésitez pas à proposer d'autres exemples dans le forum de discussion :
* Dans les **médias** : nouveau sous-métier de journalisme : les **data-journalistes**
	* [data-visualisation](http://www.lemonde.fr/data-visualisation/)
	* [journalisme de données](http://fr.wikipedia.org/wiki/Journalisme_de_données)
* Dans la **santé** : (imagerie, dossier numérique du patient, ...)
	* [simulation](https://interstices.info/jcms/c_21525/simulation-de-loperation-de-la-cataracte)
* En **histoire, sociologie, linguistique** : *fouille de données*
	* [fouille de données](http://www.youtube.com/watch?feature=player_embedded&v=tp4y-_VoXdA)
* En **art et culture** :
	* [Le Fresnoy](http://www.lefresnoy.net/fr/Le-Fresnoy/presentation)
* Dans l'**enseignement** : (outils numérique d'accompagnement scolaire, MOOC,...):
	* [FUN](https://www.france-universite-numerique-mooc.fr/cours/)
* En fouille archéologique :  une réalisation prestigieuse réalisée à Lille3 :
	* [vase qui parle](http://bsa.biblio.univ-lille3.fr/blog/2013/09/exposition-le-vase-qui-parle-au-palais-des-beaux-arts-de-lille/)
}
""")
        questions = pygift.parseFile(io_gift)
        io_gift.close()

        d = yattag.Doc()
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d,True)

        for q in questions:
            q.toHTML(d,False)

        self.assertEqual(len(questions),1,"More than one Question for 'TestSimpleText'")

        # TEST HTML
        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            self.assertEqual(str(form.h3.contents[0]), u'Le numérique concerne tout le monde')
            if i == 1:
                self.assertIsNotNone(form.textarea)
                self.assertTrue(form.textarea['placeholder'], _(u'Your answer here'))
            for j,div in enumerate(form.find_all('div')):
                if j == 0 :
                    self.assertEqual(div['class'][0], u'questiontext',"Not div or not good class for 1rst div")
                if (j == 1):
                        self.assertEqual(div['class'][0], u'global_feedback')
                        self.assertEqual(str(div.contents[0]), "<b><em>Feedback:</em></b>")
                        self.assertEqual(str(div.contents[2]), "<h1>Le numérique concerne tout le monde</h1>")
                        self.assertEqual(str(div.contents[4]), """<p>Ces recherches ont dû vous convaincre, si c'était nécessaire, que le numérique <strong>n'est pas réservé</strong> aux informaticiens, il concerne tout le monde, toutes les disciplines.<br/>
S'agissant plus particulièrement des <strong>sciences humaines</strong>, la prise en compte du numérique a fait évoluer les champs disciplinaires pour faire apparaître ce qu'on appelle les <strong>humanités numériques</strong> ( <em>digital humanities</em> en anglais).<br/>
Voici quelques exemples que nous vous proposons, n'hésitez pas à proposer d'autres exemples dans le forum de discussion :<br/>
<em> Dans les <strong>médias</strong> : nouveau sous-métier de journalisme : les <strong>data-journalistes</strong><br/>
    * <a href="http://www.lemonde.fr/data-visualisation/">data-visualisation</a><br/>
    * <a href="http://fr.wikipedia.org/wiki/Journalisme_de_données">journalisme de données</a><br/>
</em> Dans la <strong>santé</strong> : (imagerie, dossier numérique du patient, ...)<br/>
    * <a href="https://interstices.info/jcms/c_21525/simulation-de-loperation-de-la-cataracte">simulation</a><br/>
<em> En <strong>histoire, sociologie, linguistique</strong> : </em>fouille de données<em><br/>
    * <a href="http://www.youtube.com/watch?feature=player_embedded&amp;v=tp4y-_VoXdA">fouille de données</a><br/>
</em> En <strong>art et culture</strong> :<br/>
    * <a href="http://www.lefresnoy.net/fr/Le-Fresnoy/presentation">Le Fresnoy</a><br/>
<em> Dans l'<strong>enseignement</strong> : (outils numérique d'accompagnement scolaire, MOOC,...):<br/>
    * <a href="https://www.france-universite-numerique-mooc.fr/cours/">FUN</a><br/>
</em> En fouille archéologique :  une réalisation prestigieuse réalisée à Lille3 :<br/>
    * <a href="http://bsa.biblio.univ-lille3.fr/blog/2013/09/exposition-le-vase-qui-parle-au-palais-des-beaux-arts-de-lille/">vase qui parle</a></p>""")




        print("[GiftParsingHTMLTestCase]-- check_text1 OK --")


    def testTrueFalse(self):
        """
        """
        # INITIALISATION
        d = yattag.Doc()
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")

# AVEC UNE RÉPONSE SIMPLE
        io_tf = StringIO("""
Le soleil se lève à l'Ouest.{F#Non!#Oui le soleil se lève à l'Est}
        """)

        questions = pygift.parseFile(io_tf)
        io_tf.close()

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d, True)

        for q in questions:
            q.toHTML(d, False)

        self.assertEqual(len(questions),1,"More than one Question for 'TestTrueFalse'")

        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            for j,div in enumerate(form.find_all('div')):
                if j == 0:
                    self.assertEqual(div['class'][0], u'questiontext',"Not div or not good class for 1rst div")
                if i == 0:
                    if j == 1:
                        self.assertEqual(div['class'][0], u'answerFeedback',"Not div or not good class for 2sd div")
                        self.assertEqual(div.contents[0], u'False')
                    if j == 2:
                        self.assertEqual(div['class'][0], u'correct_answer',"Not div or not good class for 3rd div")
                        self.assertEqual(str(div.contents[0]), "<p>Oui le soleil se lève à l'Est</p>")
                    if j == 3:
                        self.assertEqual(div['class'][0], u'wrong_answer')
                        self.assertEqual(str(div.contents[0]), "<p>Non!</p>")
            if i == 1:
                self.assertIsNotNone(form.ul)
                for j,li in enumerate(form.find_all('li')):
                    if j == 0:
                        self.assertEqual(li.contents[0]['type'], u'radio')
                        self.assertEqual(li.contents[0]['value'], u'True')
                        self.assertEqual(li.contents[1], _(u'True'))
                    if j == 1:
                        self.assertEqual(li.contents[0]['type'], u'radio')
                        self.assertEqual(li.contents[0]['value'], u'False')
                        self.assertEqual(li.contents[1], _(u'False'))

        print("[GiftParsingHTMLTestCase]-- check_truefalse OK --")


    def testAnswerArea(self):
        #INITIALISATION
        d = yattag.Doc()
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")

# AVEC UNE RÉPONSE SIMPLE
        io_simple = StringIO("""
::first paret of text of Q2::
//comment in Q2
second part of text of Q2
My Question{
=2 =Q2 =Question2
} other part
        """)

        questions = pygift.parseFile(io_simple)
        io_simple.close()

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d, True)

        for q in questions:
            q.toHTML(d, False)

        self.assertEqual(len(questions),1,"More than one Question for 'TestAnswerArea 1'")

        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            if i == 0:
                for j,div in enumerate(form.find_all('div')):
                    if j == 0:
                        self.assertEqual(div['class'][0], u'questiontext')
                        self.assertEqual(str(div.contents[0]),'<p>second part of text of Q2<br/>\nMy Question</p>')
                    if j == 2:
                        self.assertEqual(div['class'][0], 'groupedAnswerFeedback')
                        self.assertEqual(str(div.contents[0]),'<ul><li class="right_answer">2</li><li class="right_answer">Q2</li><li class="right_answer">Question2</li></ul>')
            if i == 1:
                for j,span in enumerate(form.find_all('span')):
                    if j == 0:
                        self.assertEqual(span['class'][0], u'questionTextInline')
                        self.assertEqual(str(span.contents[0]),'<p>second part of text of Q2<br/>\nMy Question</p>')
                    if j == 1:
                        self.assertEqual(span['class'][0], u'questionAnswersInline')
                        self.assertEqual(span.input['type'], u'text')

        print("[GiftParsingHTMLTestCase]-- check_answer_area OK --")


    def testNumerical(self):

        d = yattag.Doc()
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")

        #NUMERICAL ANSWER
        io_num = StringIO("""
::Num1::
When was Ulysses S. Grant born?{#1822:5}

::Num2::
What is the value of pi (to 3 decimal places)? {#3.141..3.142}.

::Num3::
When was Ulysses S. Grant born? {#
=1822:0
=%50%1822:2
}

::Num4::
1 2 ou 3 ? {#2}
}
        """)

        questions = pygift.parseFile(io_num)
        io_num.close()


        for q in questions:
            with d.tag('h2'):
                d.text(str(questions[0].answers.__class__))
            q.toHTML(d, True)

        for q in questions:
            q.toHTML(d, False)


        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            if i < 4 :
                for j,div in enumerate(form.find_all('div')):
                    if j == 0:
                        self.assertEqual(div['class'][0], u'questiontext')
                        if i == 0:
                            self.assertEqual(str(div.contents[0]), '<p>When was Ulysses S. Grant born?</p>')
                        if i == 1 :
                            self.assertEqual(str(div.contents[0]), '<p>What is the value of pi (to 3 decimal places)?</p>')
                        if i == 2 :
                            self.assertEqual(str(div.contents[0]), '<p>When was Ulysses S. Grant born?</p>')
                    if j == 1:
                        self.assertEqual(div['class'][0], u'answerFeedback')
            else :
                for j,span in enumerate(form.find_all('span')):
                    if j == 0 :
                        self.assertEqual(span['class'][0], u'questionTextInline')
                    if j == 1 :
                        self.assertEqual(span['class'][0], u'questionAnswersInline')
                        self.assertEqual(span.input['type'], u'number')


        print("[GiftParsingHTMLTestCase]-- check_numerical OK --")



    def testMatch(self):

        d = yattag.Doc()
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")

        io_match = StringIO("""
::Match::
Match the following countries with their corresponding capitals. {
=Canada -> Ottawa
=Italy -> Rome
=Japan -> Tokyo
=India -> New Delhi
}
        """)
        questions = pygift.parseFile(io_match)
        io_match.close()

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d, True)

        for q in questions:
            q.toHTML(d, False)

        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            if i == 0 :
                for j, div in enumerate(form.find_all('div')):
                    if j == 0:
                        self.assertEqual(div['class'][0], u'questiontext')
                    if j == 2:
                        self.assertEqual(div['class'][0], u'groupedAnswerFeedback')
                        self.assertEqual(str(div.contents),u'<ul><li class="right_answer">Canada  ⇝  Ottawa</li><li class="right_answer">Italy  ⇝  Rome</li><li class="right_answer">Japan  ⇝  Tokyo</li><li class="right_answer">India  ⇝  New Delhi</li></ul>')
            if i == 1 :
                self.assertIsNotNone(form.table)
                for j,tr in enumerate(soup.find_all('tr')):
                    # WARNING : check options
                    for p,td in enumerate(tr.find_all('td')):
                        if p == 0:
                            if j == 0:
                                self.assertEqual(tr.td.contents[0], u'Canada  ')
                            if j == 1:
                                self.assertEqual(tr.td.contents[0], u'Italy  ')
                            if j == 2:
                                self.assertEqual(tr.td.contents[0], u'Japan  ')
                            if j == 3:
                                self.assertEqual(tr.td.contents[0], u'India  ')
                        if p == 1 :
                            self.assertIsNotNone(td.select)
                            self.assertIsNotNone(td.find('select')['name'])
                            self.assertEqual(len(td.find('select').find_all('option')),4)


        print("[GiftParsingHTMLTestCase]-- check_match OK --")


class GiftParserTestCase(unittest.TestCase):

    def testParseHead(self) :
        """
        """
        io_head1 = ("""::Macumba::
[markdown]
blabla
\n
bleble
{}""")
        io_head2 = ("""[html]
Macumba
blabla
\n
bleble
{}""")
        # HEAD 1
        question = pygift.Question('', '', '')
        question._parseHead(io_head1)
        self.assertEqual(question.title,"Macumba")
        self.assertEqual(question.text,"blabla\n\n\nbleble\n{}")
        self.assertEqual(question.markup,"markdown")

        # HEAD 2
        question2 = pygift.Question('', '', '')
        question2._parseHead(io_head2)
        self.assertEqual(question2.title,"")
        self.assertEqual(question2.text,"Macumba\nblabla\n\n\nbleble\n{}")
        self.assertEqual(question2.markup,"html")

        del question,question2

    def testParseSelectSet(self):
        """
        """
        io_mult1 = ("""
Qui repose dans la Grant's tomb ? {=Grant ~Personne ~Napoléon ~Churchill ~Mère Teresa}
""")
        io_mult2 = ("""
// Question : 1 Nom : Grant's tomb
::Grant's tomb::Qui repose dans la Grant's tomb à New-York ? {
=Grant
~Personne
#C'était vrai pendant 12 ans, mais la dépouille de Grant a été enterrée dans cette tombe en 1897.
~Napoléon
#Il a été enterré en France.
~Churchill
#Il a été enterré en Angleterre.
~Mère Teresa
#Elle a été enterrée en Inde.
}
""")
        # mult1
        question1 = pygift.Question('','','')
        question1.parse(io_mult1)
        self.assertIsInstance(question1.answers, pygift.SelectSet)
        for (i,a) in enumerate(question1.answers.answers) :
            self.assertIsInstance(a,pygift.AnswerInList)
            if i == 0:
                self.assertTrue('Grant' in a.answer)
                self.assertEqual(a.fraction, 100)
            else :
                self.assertEqual(a.fraction, 0)
            if i == 1: self.assertTrue('Personne' in a.answer)
            if i == 2: self.assertTrue('Napoléon' in a.answer)
            if i == 3: self.assertTrue('Churchill' in a.answer)
            if i == 4: self.assertTrue('Mère Teresa' in a.answer)

        # #TEST MY PRINT !! ##
        question1.myprint()
        print('\n')

        del question1

        # mult2
        question2 = pygift.Question('','','')
        question2.parse(io_mult2)
        self.assertIsInstance(question2.answers, pygift.SelectSet)
        for (i, a) in enumerate(question2.answers.answers):
            self.assertIsInstance(a, pygift.AnswerInList)
            if i == 0:
                self.assertTrue('Grant' in a.answer)
                self.assertEqual(a.fraction, 100)
            else:
                self.assertEqual(a.fraction, 0)
            if i == 1:
                self.assertTrue('Personne' in a.answer)
                self.assertTrue("C'était vrai pendant 12 ans, mais la dépouille de Grant a été enterrée dans cette tombe en 1897." in a.feedback)
            if i == 2:
                self.assertTrue('Napoléon' in a.answer)
                self.assertTrue("Il a été enterré en France." in a.feedback)
            if i == 3:
                self.assertTrue('Churchill' in a.answer)
                self.assertTrue("Il a été enterré en Angleterre." in a.feedback)
            if i == 4:
                self.assertTrue('Mère Teresa' in a.answer)
                self.assertTrue('Elle a été enterrée en Inde.' in a.feedback)
        ##TEST MY PRINT !! ##
        question2.myprint()
        print('\n')

        del question2

    def testParseMatchingSet(self):
        """
        """
        io_match1 = ("""
Appariez les pays suivants avec les capitales correspondantes. {
   =Canada -> Ottawa
   =Italie -> Rome
   =Japon -> Tokyo
   =Inde -> New Delhi
}""")
        question1 = pygift.Question('','','')
        question1.parse(io_match1)
        self.assertIsInstance(question1.answers, pygift.MatchingSet)
        self.assertEqual([' Ottawa', ' Rome', ' Tokyo', ' New Delhi'], question1.answers.possibleAnswers)
        for (i,a) in enumerate(question1.answers.answers) :
            if i == 0 :
                self.assertTrue('Canada' in a.question)
                self.assertTrue('Ottawa' in a.answer)
            if i == 1 :
                self.assertTrue('Italie' in a.question)
                self.assertTrue('Rome' in a.answer)
            if i == 2:
                self.assertTrue('Japon' in a.question)
                self.assertTrue('Tokyo' in a.answer)
            if i == 3:
                self.assertTrue('Inde' in a.question)
                self.assertTrue('New Delhi' in a.answer)

        ##TEST MY PRINT !! ##
        question1.myprint()
        print('\n')

        del question1

    def testParseShortSet(self):
        """
        """
        io_short1 = ("""
second part of text of Q2
My Question{
=2 =Q2 =Question2
} other part
        """)
        question1 = pygift.Question('','','')
        question1.parse(io_short1)
        self.assertIsInstance(question1.answers, pygift.ShortSet)
        for (i,a) in enumerate(question1.answers.answers):
            if i == 0:
                self.assertTrue('2' in a.answer)
            if i == 1:
                self.assertTrue('Q2' in a.answer)
            if i == 2:
                self.assertTrue('Question2' in a.answer)

        ##TEST MY PRINT !! ##
        question1.myprint()
        print('\n')

        del question1

    def testParseMultiChoiceSet(self):
        """
        """
        io_choice1 = ("""
Parmi ces personnes, nommez-en deux qui sont enterrées dans la Grant's tomb. {
   ~%-100%Personne
   ~%50%Grant
   ~%50%L'épouse de Grant
   ~%-100%Le père de Grant
}        """)

        io_choice2 = ("""
question {
~%33.33333%Bonne réponse
~%33.33333%Bonne réponse
~%33.33333%Bonne réponse
~%0%Mauvaise réponse
~%0%Mauvaise réponse
}
        """)

        #CHOICE1
        question1 = pygift.Question('','','')
        question1.parse(io_choice1)
        self.assertIsInstance(question1.answers, pygift.MultipleChoicesSet)
        for (i,a) in enumerate(question1.answers.answers):
            if i == 0:
                self.assertTrue('Personne' in a.answer)
                self.assertEqual(-100,float(a.fraction))
            if i == 1:
                self.assertTrue('Grant' in a.answer)
                self.assertEqual(50,float(a.fraction))
            if i == 2:
                self.assertTrue("L'épouse de Grant" in a.answer)
                self.assertEqual(50,float(a.fraction))
            if i == 3:
                self.assertTrue('Le père de Grant' in a.answer)
                self.assertEqual(-100,float(a.fraction))

        ##TEST MY PRINT !! ##
        question1.myprint()
        print('\n')
        del question1

        #CHOICE2
        question2 = pygift.Question('','','')
        question2.parse(io_choice2)
        self.assertIsInstance(question2.answers, pygift.MultipleChoicesSet)
        for (i,a) in enumerate(question2.answers.answers):
            if i == 0:
                self.assertTrue('Bonne réponse' in a.answer)
                self.assertEqual(33.33333,float(a.fraction))
            if i == 1:
                self.assertTrue('Bonne réponse' in a.answer)
                self.assertEqual(33.33333,float(a.fraction))
            if i == 2:
                self.assertTrue('Bonne réponse' in a.answer)
                self.assertEqual(33.33333,float(a.fraction))
            if i == 3:
                self.assertTrue('Mauvaise réponse' in a.answer)
                self.assertEqual(0,float(a.fraction))
            if i == 4:
                self.assertTrue('Mauvaise réponse' in a.answer)
                self.assertEqual(0,float(a.fraction))

        ##TEST MY PRINT !! ##
        question2.myprint()
        print('\n')

        del question2

    def testParseTrueFalse(self):
        """
        """
        io_tf1 = ("""
Grant a été enterré dans une tombe à New-York.{T #Faux #Vrai}
        """)

        io_tf2 = ("""
Le soleil se lève à l'Ouest.{FALSE}
        """)

        #TF1
        question1 = pygift.Question('','','')
        question1.parse(io_tf1)
        self.assertIsInstance(question1.answers, pygift.TrueFalseSet)
        self.assertTrue(question1.answers.answer)
        self.assertTrue('Faux' in question1.answers.feedbackWrong)
        self.assertTrue('Vrai' in question1.answers.feedbackCorrect)

        ##TEST MY PRINT !! ##
        question1.myprint()
        print('\n')
        del question1

        #TF2
        question2 = pygift.Question('','','')
        question2.parse(io_tf2)
        self.assertIsInstance(question2.answers, pygift.TrueFalseSet)
        self.assertFalse(question2.answers.answer)

        ##TEST MY PRINT !! ##
        question2.myprint()
        print('\n')
        del question2

    def testParseDescription(self):
        """
        """
        io_descrip = ("""
Blablablablabla
        """)

        #DESCRIP
        question1 = pygift.Question('','','')
        question1.parse(io_descrip)
        self.assertIsInstance(question1.answers, pygift.Description)

        ##TEST MY PRINT !! ##
        question1.myprint()
        print('\n')

        del question1

    def testParseEssay(self):
        """
        """
        io_essay =("""
Blablablablabla
{}
        """)

        #ESSAY
        question1 = pygift.Question('','','')
        question1.parse(io_essay)
        self.assertIsInstance(question1.answers, pygift.Essay)

        ##TEST MY PRINT !! ##
        question1.myprint()
        print('\n')
        del question1



    def testParseNumeric(self):
        """
        test numeric answer return of :func:`pygift._parseNumericAnswers`
        """
        io_num1 = ("""
1 OU 2 OU 3?{
#2
}""")
        io_num2 = ("""
1 OU 2 OU 3?{
#2:1
#### MEGA COMMENT
}""")
        io_num3 = ("""
1 OU 2 OU 3?{
#1..3
}""")

        io_num4 = ("""
1 OU 2 OU 3?{
#
}""")
        # FIXME : Ne pas passer par la méthode parse mais par _parseNumericAnswers / _parseNumericText
        #NUM1
        question1 = pygift.Question('', '', '')
        question1.parse(io_num1)
        self.assertTrue(question1.numeric)
        self.assertIsInstance(question1.answers, pygift.NumericAnswerSet)
        self.assertIsInstance(question1.answers.answers[0], pygift.NumericAnswer)
        self.assertEqual(question1.answers.answers[0].value, 2)
        self.assertEqual(question1.answers.answers[0].tolerance, 0)
        del question1
        # NUM2
        question2 = pygift.Question('', '', '')
        question2.parse(io_num2)
        self.assertTrue(question2.numeric)
        self.assertIsInstance(question2.answers, pygift.NumericAnswerSet)
        self.assertIsInstance(question2.answers.answers[0], pygift.NumericAnswer)
        self.assertEqual(question2.answers.answers[0]. value, 2)
        self.assertEqual(question2.answers.answers[0].tolerance, 1)
        del question2
        # #NUM3
        question3 = pygift.Question('', '', '')
        question3.parse(io_num3)
        self.assertTrue(question3.numeric)
        self.assertIsInstance(question3.answers, pygift. NumericAnswerSet)
        self.assertIsInstance(question3.answers.answers[0], pygift.NumericAnswerMinMax)
        self.assertEqual(question3.answers.answers[0].mini, str(1))
        self.assertEqual(question3.answers.answers[0].maxi, str(3))
        del question3

        question4 = pygift.Question('', '', '')
        question4.parse(io_num4)
        self.assertTrue(question4.numeric)
        self.assertFalse(question4.valid)

    def testParseError(self):
        """
        test the fail value of :func:`pygift._parseAnswer`
        """
        q = pygift.Question('', '', '')
        q._parseAnswer('blazqopk')
        self.assertFalse(q.valid)
        q.myprint()
        self.assertEqual('', q.toHTML())

    def testParseQuestionWithSpaces(self):
        io = StringIO("""
  // some comment
  ::question_title::question_text{
    =Grant
    ~Personne
}
        """)
        questions = pygift.parseFile(io)
        io.close()
        self.assertEqual(questions[0].text, 'question_text')


# Main
if __name__ == '__main__':
    unittest.main(verbosity=1)
