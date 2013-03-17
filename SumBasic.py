# -*- coding: utf-8 -*-
"""
Kathryn Nichols
LING 571
Project 2

Uses SumBasic algorithm to summarize a text.

"""

from __future__ import division
from collections import defaultdict
import nltk
import re

def get_sentences(filename):
    """
    Removes stopwords from, stems and tokenizes sentences.
    Computes probability distribution over words.

    @param filename -- name of file containing sentences

    @return distribution -- probability distribution of words
    @return clean_sentences -- list of clean sentences
    @return processed_sentences -- list of processed sentences

    """

    stopwords = nltk.corpus.stopwords.words('english') + ['n']
    stemmer = nltk.stem.PorterStemmer()
    tokenize = nltk.word_tokenize

    clean_sentences, processed_sentences = [], []
    distribution = defaultdict(int)
    total = 0

    for line in open(filename):
        line = line.strip()
        if not line: continue

        # remove non-alphanumeric symbols, stem, tokenize, stopwordize
        sentence = re.sub(r'\W', ' ', line).lower()
        sentence = [stemmer.stem(word) for word in tokenize(sentence) \
                    if not word in stopwords]

        # store sentences if not empty
        if sentence:
            processed_sentences.append(sentence)
            clean_sentences.append(clean(line))

        # update frequency
        for word in sentence:
            distribution[word] += 1
            total += 1

    # convert frequency distribution to probability distribution
    for word in distribution: distribution[word] = distribution[word]/total

    return distribution, clean_sentences, processed_sentences

def summarize(distribution, clean_sentences, processed_sentences, N):
    """
    Recursively runs SumBasic algorithm on sentences.

    @param distribution -- probability distribution over words
    @param clean_sentences -- list of clean sentences
    @param processed_sentences -- list of processed sentences
    @param N -- maximum length of summary in words

    @return -- summary pieces as strings

    """

    if N == 0 or N == 1: return ''

    # sort words by probability
    words = sorted(distribution, key=distribution.get, reverse=True)

    for word in words:

        # get candidate sentences containing word
        candidates = [sentence for sentence in processed_sentences if word in sentence]
        
        # sort candidates by average probability
        candidates = sentence_averages(distribution, candidates)

        for candidate in candidates:
            original = clean_sentences[processed_sentences.index(candidate)]
            processed_sentences.remove(candidate)
            clean_sentences.remove(original)

            # if sentence fits, add sentence to summary
            if len(original.split()) <= N:    
        
                # update distribution
                for word in candidate: distribution[word] = distribution[word]**2

                return original + ' ' + summarize(distribution, \
                        clean_sentences, processed_sentences, (N - len(original.split())))
       
    return ''


def sentence_averages(distribution, sentences):
    """
    Finds average word probability per sentence and returns highest.

    @param distribution -- probability distribution over words
    @param sentences -- list of sentences

    @return averages -- sentences sorted by average probability

    """
    
    scores = defaultdict(float)
    index = 0

    for sentence in sentences:
        scores[index] = sum([distribution[word] for word in sentence])/len(sentence)
        index += 1

    averages = [sentences[index] for index in sorted(scores, key=scores.get, reverse=True)]

    return averages

def clean(sentence):
    """
    Cleans given sentence for use in a summary.

    @param sentence -- sentence to clean

    @return sentence -- cleaned sentence

    """

    punc = re.compile(r' +(;|:|\?|!|\.|,|%|\'\')')
    clitics = re.compile(r' +(\'s|\'re|n\'t|\'ve|\'m|\'ll|\'d)')

    sentence = sentence.strip()
    sentence = re.sub(punc, r'\1', sentence)     # attach punc to previous word
    sentence = re.sub(r'\\/', '/', sentence)     # slash attaches to left and right words
    sentence = re.sub(r'\$ +', '$', sentence)    # attach $ to next word
    sentence = re.sub(r'`+|\'\'', '', sentence)  # remove quotes
    sentence = re.sub(clitics, r'\1', sentence)  # attach clitics to previous word
    sentence = re.sub(r' +', r' ', sentence)     # delete extra spaces

    return sentence

def main():
    """
    Reads in sentences, uses SumBasic to find sentences for summary, prints
    summary to console.

    """
    
    import argparse, sys
    
    args = argparse.ArgumentParser()
    args.add_argument('sentences', help='file of line-separated sentences to summarize')
    args.add_argument('N', help='number of words in summary', type=int)
    args.parse_args()
    
    N = int(sys.argv[2])
    
    if N < 1:
        sys.stderr.write('N must be greater than 0. No output produced.')
        sys.exit()
    
    distribution, clean_sentences, processed_sentences = get_sentences(sys.argv[1])
    print summarize(distribution, clean_sentences, processed_sentences, N)

if __name__=='__main__':
    main()
