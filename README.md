This project was written on Linux Manjaro KDE Plasma 20.0.3 with Python 3.7.6.

## parse-anweisungen
The following project is a rule-based parser that extracts number blocks from instructions, tagging them as either a goal block or an area block.

## DESCRIPTION
Out of a set of instructions to be used for moving a block to a certain area, this class extracts linguistic information from said instructions (both absolute frequencies of tokens and bigrams) and tags the number blocks appearing in the instructions corresponding to their role. A block can either be a goal block (the goal to be moved) or an area block (a block that is used to describe the position that the goal block should be moved to).
The class RuleBasedParser is used to first read the data from the instructions.txt, which is then stored in a raw and in a "clean" form (tokenized & punctuation removed) for linguistic analysis. Then, the absolute frequencies of both tokens and bigrams across all instructions are calculated and exported to a csv. Afterwards, the numbers in each construction are collected and tagged as a goal block or an area block, depending on either the linguistic context or the position in the instruction. Multiple area blocks are ignored. The performance of the parser is then analyzed by calculating the precision, recall and F-score.

## REQUIREMENTS
The requirements can be found in the requirements.txt.

## HOW TO USE
1.  Install nltk with the following command: 
`pip install nltk`
2.  Run the following command in your terminal: 
`python3 parse_anweisungen.py <instruction file name> <gold standard file name>`
with standard file names, the command is the following:
`python3 parse_anweisungen.py instructions.txt gold_standard.csv`
3. Optional: get unit test results:
`python3 rulebasedparser_unittest.py`

The token and bigram frequencies are both saved in tokens.csv and bigrams.csv respectively. For errors, errors.log offers more information. The results are exported as results.csv.

## Author: 
Lea Wetzke / 797451 / Einführung in die Programmiersprache SoSe 2020 / [lwetzke@uni-potsdam.de](mailto:lwetzke@uni-potsdam.de)
