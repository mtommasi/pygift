import unittest
from pygiftparser import parser


class TestQuestionClass(unittest.TestCase):

    def setUp(self):
        self.known_values = [
            ("::short:: [markdown] long {= apple # of course ~ peach # no no no}",
             dict(title="short", text="long", markup="markdown"),
             [dict(answer="apple", feedback="of course", fraction=100), dict(answer="peach", feedback="no no no", fraction=0)]
             ),
            ]

    def test_get_proper_attributes(self):
        for gift, attributes, answers in self.known_values:
            question = parser.Question(gift, "fullllll", "cattegory")
            for attr in attributes:
                self.assertEqual(getattr(question, attr), attributes[attr])
            for actual_answer, expected_answer_attributes in zip(question.answers.answers, answers):
                for attr in expected_answer_attributes:
                    self.assertEqual(getattr(actual_answer, attr), expected_answer_attributes[attr])

unittest.main()
