#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Lea Wetzke
# Rule Based Parser
# Einführung in die Programmiersprache SoSe 2020
# 797451

from collections import Counter
from nltk import ngrams
import re
import csv
import logging
import os 

logging.basicConfig(filename='errors.log', level=logging.DEBUG)

class RuleBasedParser():
    """Class that reads instructions from a .txt file, extracts the absolute
    token and bigram frequencies, and tags the block numbers in an instruction 
    as either a goal block or an area block, exporting the results as a csv.

    Args:
        filename (str): .txt-file containing the instructions.

    Returns:
        None

    """
    def __init__(self, filename):
        self.filename = filename
        # name of the txt containing the instructions
        self.clean_instructions = []
        # cleaned instructions (no punctuation, no capital letters, numbers
        # replaced with num)
        self.raw_instructions = []
        # raw instructions right from the txt
        self.token_counter = Counter()
        # Counter for absolute frequency of tokens
        self.bigram_counter = Counter()
        # Counter for absolute frequency of bigrams
        self.sorted_bigrams = []
        # list of bigram tuples sorted by their absolute frequency
        self.blocks = dict()
        # Nested dict: keys are raw instructions, value dict contains "goal"
        # and "area" as keys and numbers as values.
        # Example: { "instruction" : "goal" : 10, "area" : 14}
        self.area_contexts = ['of', 'above', 'below', 'as']
        # Contexts implying the following block is an area block
        self.goal_contexts = ['Take', 'Move', 'Place', 'Find', 'move']
         # Contexts implying the following block is a goal block       
    
    def parse(self):    
        """Method that reads the instructions from the txt, tags the 
           block numbers, and writes the results to a csv.

          Args:
              None
              
          Returns:
              None
              
        """
        self._read_from_txt()
        # read information from the instructions.txt
        self._tag_instruct_blocks()
        # tag the block numbers for each instruction, saved in self.blocks
        self._write_results_to_csv("results.csv")
        # Write block inf to a csv
        
    def get_tokens_bigrams(self):
        """Method that gets the absolute frequencies of tokens and bigrams,
           exporting them as a csv.

          Args:
              None
              
          Returns:
              None
              
        """
        self._count_bigrams(self._count_words_make_bigrams())
        # get absolute bigram and absolute token frequency
        self._write_stats_to_csv("bigrams.csv", True)
        self._write_stats_to_csv("tokens.csv", False) 
        # write both to csvs

    def calculate_f1(self, gold_name):
        """Method that calculates precision, recall and the F1 score.

          Args:
              gold_name (str) : Name of the gold standard csv.
              
          Returns:
              precision, recall, 
              ((2*precision*recall)/(precision+recall)) (float) : 
                  Floats representing the statistical measures of precision,
                  recall and the F1 score.
              
        """  
        if not os.path.isfile(gold_name):
            print("csv containing gold standard was not found.")
            logging.error("csv file containing gold standard was not found.")
            raise FileNotFoundError
        with open(gold_name, mode = "r", encoding = "utf-8", 
                  newline = "\n") as gold_file:
            correct_blocks = 0
            # num of correct blocks
            total_answers = 0
            # num of actual answers (not "-")
            total_blocks = 0
            # num of total blocks
            for line in gold_file:
                if line != "\n" or line != "":
                    split_line = line.split(";")
                    if split_line[0] in self.blocks.keys():
                        if self.blocks[split_line[0]]['goal'] != '-':
                            total_answers += 1
                            # change from '-' implies given answer
                        if self.blocks[split_line[0]]['area'] != '-':
                            total_answers += 1
                        if self.blocks[split_line[0]]['goal'] == split_line[1]:
                            correct_blocks += 1
                            # If gold standard and tagging match up: 
                            # correct block
                        gold_area = split_line[2].rstrip("\r\n")
                        if self.blocks[split_line[0]]['area'] in \
                                                          gold_area.split(","):
                            correct_blocks += 1
                            # if area block in list of gold standard area 
                            # blocks: one more correct block
                        total_blocks += (len(split_line[1]) 
                                         + len(gold_area.split(",")))
        recall = correct_blocks/total_blocks
        precision = correct_blocks/total_answers
        return precision, recall, ((2*precision*recall)/(precision+recall))
    
    def _tag_instruct_blocks(self):
        """Method that tags the number blocks appearing in all instructions as
           either a goal block or an area block corresponding to an 
           instrunction.

          Args:
              None
          Returns:
              None

        """
        if self.raw_instructions == []:
            logging.error("WARNING: no instructions were collected.")
            raise IndexError
        for raw_instr in self.raw_instructions:
            self.blocks[raw_instr] = {'goal' : '-', 'area' : '-'}
            # make "standard" options for goal and area
            raw_instr_clean = re.sub(r'block|box', '', raw_instr)
            # remove mentions of block and box
            split_instr = raw_instr_clean.split()
            block_nums = re.findall(r'\d+', raw_instr_clean)
            # find all mentions of numbers
            for i in range(len(split_instr)):
                if split_instr[i] in block_nums:
                    if split_instr[i-1] in self.goal_contexts:
                        self.blocks[raw_instr]['goal'] = split_instr[i]
                        # if the word before the block number is a goal 
                        # context, the number is assumed to be a goal
                    if split_instr[i-1] in self.area_contexts:
                        self.blocks[raw_instr]['area'] = split_instr[i]
                        # same with area block (only one)
            if block_nums != []:
                if self.blocks[raw_instr]['goal'] == '-':
                    self.blocks[raw_instr]['goal'] = block_nums[0]
                    # if number did not have a goal context but was the first
                    # number found, it is assumed to be the goal block
                if len(block_nums) >= 2:
                    if self.blocks[raw_instr]['area'] == '-':
                        self.blocks[raw_instr]['area'] = block_nums[1]  
                        # the number after the assumed goal is assumed to be 
                        # an area block if it there are more than 2 blocks
            
    def _read_from_txt(self):
        """Method that reads a txt containing instructions, extracts and 
           cleans them for later usage.

          Args:
              None
          Returns:
              None

        """
        if not os.path.isfile(self.filename):
            print("txt-file containing instructions was not found.")
            logging.error("txt-file containing instructions was not found.")
            raise FileNotFoundError
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


           
    def _count_words_make_bigrams(self):
        """Method that extracts tokens and their absolute frequency, plus
           all bigrams.

          Args:
              None
          Returns:
              bigrams (list) : List containing tuples representing bigrams.

        """
        bigrams = []
        for instruct in self.clean_instructions:
            # use clean instrutions aka instructions without punctuation
            for bigram in ngrams(instruct.split(), 2):
                bigrams.append(bigram)
                # use nltk to get bigrams
            for token in instruct.split():
                if token != "block" or token != "box":
                # "block" and punctuation ignored
                    if token in self.token_counter.keys():
                        self.token_counter[token] += 1
                        # add if dict entry for token already exists                        
                    else:
                        self.token_counter[token] = 1
                        # make new dict entry
        return bigrams
                        
    def _count_bigrams(self, bigrams):
        """Method that calculates absolute frequency of all bigrams.

          Args:
              bigrams (list) : List containing tuples representing bigrams.
          Returns:
              None
              
        """
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
        """Method that writes tokens and bigrams plus their absolute frequency
           out as a csv.

          Args:
              filename (str) : String representing the desired filename.
              bigrams (list) : List containing tuples representing bigrams.
          Returns:
              None
              
        """  
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
                    
    def _write_results_to_csv(self, filename):
        """Method that writes tokens and bigrams plus their absolute frequency
           out as a csv.

          Args:
              filename (str) : String representing the desired filename.
              bigrams (list) : List containing tuples representing bigrams.
          Returns:
              None
              
        """  
        with open(filename, mode="w", encoding="utf-8",
                  newline="\n") as results_file:
            results_writer = csv.writer(results_file, delimiter=";",
                                      quotechar='"',
                                      quoting=csv.QUOTE_MINIMAL)
            for key, value in self.blocks.items():
                results_writer.writerow([key, value["goal"], value["area"]])
                
    

