#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Lea Wetzke
# main
# Einführung in die Programmiersprache SoSe 2020
# 797451

from rulebasedparser import RuleBasedParser
import os

if __name__ == "__main__":
    rbp = RuleBasedParser("instructions.txt")
    print("Extracting absolute frequencies of tokens and bigrams...")
    if os.path.isfile("tokens.csv") and os.path.isfile("bigrams.csv"):
        print("tokens.csv and bigrams.csv already generated. ")
    else:
        rbp.get_tokens_bigrams()
    print("Tagging block numbers...")
    rbp.parse()
    print("Block numbers of instructions successfully tagged. Results " +
          "in results.csv.")
    stats = rbp.calculate_f1("gold_standard.csv")
    print("precision: ", stats[0])
    print("recall: ", stats[1]) 
    print("F1: ", stats[2]) 