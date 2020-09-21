#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 10:32:20 2020

@author: lea
"""
from collections import Counter
import re
import csv
from nltk import ngrams
import logging
import os 

logging.basicConfig(filename='errors.log', level=logging.DEBUG)

class RuleBasedParser():
    def __init__(self, filename):
        self.filename = filename
        self.clean_instructions = []
        self.raw_instructions = []
        self.token_counter = Counter()
        self.bigram_counter = Counter()
        self.sorted_bigrams = []
        self.blocks = dict()
        self.area_contexts = ['of', 'above', 'below', 'as', ]
        self.goal_contexts = ['Take', 'Move', 'Place', 'Find', 'move']
        
    
    def parse(self):    
        self._read_from_txt()
        self._count_bigrams(self._count_words_gen_bigrams())
        self._write_stats_to_csv("bigrams.csv", True)
        self._write_stats_to_csv("tokens.csv", False) 
        self._tag_instruct_blocks()
    
    def _tag_instruct_blocks(self):
        for raw_instr in self.raw_instructions:
            self.blocks[raw_instr] = {'goal' : '', 'area' : ''}
            raw_instr_clean = re.sub(r'block|box', '', raw_instr)
            split_instr = raw_instr_clean.split()
            block_nums = re.findall(r'\d+', raw_instr_clean)
            for i in range(len(split_instr)):
                if split_instr[i] in block_nums:
                    if split_instr[i-1] in self.goal_contexts:
                        self.blocks[raw_instr]['goal'] = split_instr[i]
                    if split_instr[i-1] in self.area_contexts:
                        self.blocks[raw_instr]['area'] = split_instr[i]
            if block_nums != []:
                for key, value in self.blocks.items():
                    if self.blocks[key]['goal'] == '':
                        self.blocks[key]['goal'] = block_nums[0]
                    if self.blocks[key]['area'] == '':
                        self.blocks[key]['area'] = block_nums[-1]          
                
    def _read_from_txt(self):
        """Method that reads a txt containing instructions, extracts and cleans
           them for later usage.

          Args:
              None
          Returns:
              None

        """

        if not os.path.isfile(self.filename):
            print("txt-file containing instructions was not found.")
            logging.error("txt-file containing instructions was not found.")
        with open(self.filename, "r", encoding = "utf-8") as txt_file:
            for line in txt_file:
                raw_line = line.rstrip("\n")
                self.raw_instructions.append(raw_line)
                # raw instructions used as the key of the self.blocks dict
                strip_line = line.rstrip(".\n")
                # strip newline and dots
                # raw instructions used as the key of the self.blocks dict
                # later
                strip_line = re.sub(r'[^\w\s]', '', strip_line)
                # remove punctuation
                strip_line = re.sub(r'\d+', 'NUM', strip_line)
                # replace number with num for better bigram stats
                self.clean_instructions.append(strip_line.lower())
                # treat them as "cleaned" instructions
           
    def _count_words_gen_bigrams(self):
        bigrams = []
        for instruct in self.clean_instructions:
            # use clean instrutions aka instructions without punctuation
            for bigram in ngrams(instruct.split(), 2):
                bigrams.append(bigram)
                # use nltk to get bigrams
            for token in instruct.split():
                if token != "block":
                # "block" and punctuation ignored
                    if token in self.token_counter.keys():
                        self.token_counter[token] += 1
                    else:
                        self.token_counter[token] = 1
        return bigrams
                        
    def _count_bigrams(self, bigrams):
        for bigram in bigrams:
            if bigram in self.bigram_counter.keys():
                self.bigram_counter[bigram] += 1
            else:
                self.bigram_counter[bigram] = 1
        self.sorted_bigrams = sorted(self.bigram_counter.items(), 
                                     key = lambda x : x[1], reverse = True)
        # by using sorted and lambda, the dict entries are turned into a list
        # that is sorted by the occurence of the bigrams (highest to lowest)
    
                
    def _write_stats_to_csv(self, filename, is_bigram):
        with open(filename, mode="w", encoding="utf-8",
                  newline="\n") as stats_file:
            stats_writer = csv.writer(stats_file, delimiter=",",
                                        quotechar='"',
                                        quoting=csv.QUOTE_MINIMAL)
            if is_bigram == True:
            # for bigram csv
                for bigram in self.sorted_bigrams:
                    stats_writer.writerow([bigram[0], bigram[1]])

            else:
            # for token csv
                for token in sorted(self.token_counter.items(), 
                                    key = lambda x : x[1], reverse = True):
                    stats_writer.writerow([token[0], token[1]])
                    
    def _write_results_to_csv(self):
        with open(filename, mode="w", encoding="utf-8",
                  newline="\n") as results_file:
            pass
    
    def _calculate_f1(self, gold_name):
        with open(gold_name, mode = "r", encoding = "utf-8", 
                  newline = "\n") as gold_file:
            correct_blocks = 0
            total_answers = 0
            total_blocks = 0
            for line in gold_file:
                split_line = line.split(";")
                if split_line[0] in self.blocks.keys():
                    if self.blocks[split_line[0]]['goal'] != '':
                        total_answers += 1
                    if self.blocks[split_line[0]]['area'] != '':
                        total_answers += 1
                    if self.blocks[split_line[0]]['goal'] == split_line[1]:
                        correct_blocks += 1
                    if self.blocks[split_line[0]]['area'] == split_line[2].rstrip("\r\n"):
                        correct_blocks += 1
                    total_blocks += len(split_line[1]) + len(split_line[2].rstrip("\r\n").split(","))
        recall = correct_blocks/total_blocks
        precision = correct_blocks/total_answers
        return precision
            
if __name__ == "__main__":
    rbp = RuleBasedParser("instructions.txt")
    rbp.parse()
    print(rbp._calculate_f1("gold_standard.csv"))