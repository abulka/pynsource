# import unittest
# import sys
# import re
# from parsing.quick_parse import REGEX_FOR_METHODS
#
# # python -m unittest tests.test_ast_quickparse
#
# class TestQuickParse(unittest.TestCase):
#
#     def setUp(self):
#         self.regex = r'^\s*def (.*?)\(.*\):'  # the ? turns off greedy
#
#     def test_regex1(self):
#         source = "def fred(): pass"
#         defs = re.findall(REGEX_FOR_METHODS, source, re.MULTILINE)
#         self.assertEqual(defs, ['fred'])
#
#     def test_regex2(self):
#         source = "    def fred(): pass"
#         defs = re.findall(REGEX_FOR_METHODS, source, re.MULTILINE)
#         self.assertEqual(defs, ['fred'])
#
#     def test_regex3(self):
#         source = "    def fred(param1): pass"
#         defs = re.findall(REGEX_FOR_METHODS, source, re.MULTILINE)
#         self.assertEqual(defs, ['fred'])
#
#     def test_regex3(self):
#         source = "    def fred(timepos, modernyear=2001, waryear=int(DEFAULT_WARDATE_USFORMAT[2]), month=int(DEFAULT_WARDATE_USFORMAT[0]), day=int(DEFAULT_WARDATE_USFORMAT[1]), hour=6):"
#         defs = re.findall(REGEX_FOR_METHODS, source, re.MULTILINE)
#         self.assertEqual(defs, ['fred'])
#
