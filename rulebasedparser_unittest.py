#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Lea Wetzke
# Unit Test
# Einführung in die Programmiersprache SoSe 2020
# 797451

from rulebasedparser import RuleBasedParser
from collections import Counter
import unittest
import os

class RuleBasedParserTestMethods(unittest.TestCase):
    def setUp(self):
        self.rbp = RuleBasedParser("instructions.txt")

    def test_if_FileNotFound_raised_with_wrong_instructions_filename(self):
        self.rbp.parse()
        self.rbp_error = RuleBasedParser("wrongfilename.txt")
        with self.assertRaises(FileNotFoundError):
            self.rbp_error.parse()
    
    def test_if_read_from_txt_fills_raw_instructions_attribute(self):
        self.rbp.parse()
        self.assertTrue(self.rbp.raw_instructions != [])
    
    def test_if_raw_instructions_and_clean_instructions_are_unequal(self):
        self.rbp.parse()
        self.assertTrue(
                      self.rbp.raw_instructions != self.rbp.clean_instructions)
    
    def test_if_get_tokens_bigrams_gets_tokens(self):
        self.rbp.raw_instructions = ["Move block 18 above and to the right " 
                                     + "of block 15."]
        self.rbp.clean_instructions = ["move block num above and to the right " 
                                     + "of block num"]
        self.rbp.get_tokens_bigrams()
        self.assertTrue(Counter({'block': 2, 'num': 2, 'move': 1, 
                                 'above': 1, 'and': 1, 'to': 1, 
                                 'the': 1, 'right': 1, 'of': 1}) 
                        == self.rbp.token_counter)
    
    def test_if_get_tokens_bigrams_gets_bigrams(self):
        self.rbp.raw_instructions = ["Move block 18 above and to the right " 
                                     + "of block 15."]
        self.rbp.clean_instructions = ["move block num above and to the right " 
                                     + "of block num"]
        self.rbp.get_tokens_bigrams()
        self.assertTrue(Counter({('block', 'num'): 2, ('move', 'block'): 1, 
                                 ('num', 'above'): 1, ('above', 'and'): 1, 
                                 ('and', 'to'): 1, ('to', 'the'): 1, 
                                 ('the', 'right'): 1, ('right', 'of'): 1, 
                                 ('of', 'block'): 1})
                        == self.rbp.bigram_counter)
    
    def test_if_get_tokens_bigrams_writes_csvs(self):
        self.rbp.parse()
        self.rbp.get_tokens_bigrams()
        self.assertTrue(os.path.isfile("tokens.csv") 
                        and os.path.isfile("bigrams.csv"))
    
    def test_if_tag_instruct_blocks_tags_blocks_correctly(self):
        self.rbp.raw_instructions = ["Move block 18 above and to the right " 
                                     + "of block 15.", 
                                     "Move block eight above block two.",
                                     "Move box 10 two steps to the right.",
                                     "",
                                     "Take 10 and place it between 12 and 13."]
        self.rbp._tag_instruct_blocks()
        self.assertEqual(self.rbp.blocks, 
                         {'Move block 18 above and to the right of block 15.'
                          : {'goal': '18', 'area': '15'}, 
                          'Move block eight above block two.'
                          : {'goal': '-', 'area': '-'}, 
                          'Move box 10 two steps to the right.'
                          : {'goal': '10', 'area': '-'}, 
                          '': {'goal': '-', 'area': '-'}, 
                          'Take 10 and place it between 12 and 13.'
                          : {'goal': '10', 'area': '12'}})
        
    def test_if_tag_instruct_IndexError_triggered(self):
        self.rbp.raw_instructions = []
        with self.assertRaises(IndexError):
            self.rbp._tag_instruct_blocks()
    
    def test_if_calculate_f1_returns_tuple(self):
        self.rbp.parse()
        self.assertTrue(type(self.rbp.calculate_f1("gold_standard.csv")) 
                        == tuple)
    
    def test_if_calculate_f1_tuple_contains_float(self):
        self.rbp.parse()
        self.assertTrue(type(self.rbp.calculate_f1("gold_standard.csv")[0]) 
                        == float)

        
        
if __name__ == "__main__":
    unittest.main()