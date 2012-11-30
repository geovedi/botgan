#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
__version__ =   "0.2"
__author__  =   "@geovedi"
__date__    =   "2010/02/01"
"""

import itertools
import random
import re
import readline
import sys
import urllib

from BeautifulSoup import BeautifulSoup, SoupStrainer

IGNORED_TAGS = ['img', 'a', 'br']

DEFAULT_SWAPWORDS = {
        'saya':'ane', 'sy':'ane', 'gue':'ane', 'kamu':'agan', 'elo':'agan', 
        'lo':'gan', 'ts':'agan', 'agan ts':'agan', 'tsnya':'agan', 
        'kaskuser':'yg laen', 'atas ane':'yg laen', 'bawah ane':'yg laen',
    }

DEFAULT_EXCUSES = [
        'ane gak tau gan.',
        'terserah deh, yg penting ane bisa makan hari ini. ;p',
        'ampun, gan. ane gak tau. ngomong yang lain aja ya.',
        'wah, ane off bentar ya. kebelet pipis.',
        'maho!',
        'wahahahaha',
        'waduh? cepet amat, gan???',
        'gak ngerti. tolong pencerahannya',
        'mantap gan',
        'ampun, gan',
        'agan orangnya ribet. ane jadi males',
        'ijin nyimak, gan',
        'maap double post gan',
        'nyimax dulu gan',
        'wah, selamat yah gan...',
        'boleh dong, ane ditimpuk pake cendol nya...',
        'wah enak gan ane juga pengen',
        'wkwkw bisa nahan gan',
        'sepertinya ane mesti setuju ama ente gan',
        'ga ada sumbernya nih jangan jangan HOAX',
    ]


def kaskus_search(keywords):
    archive_url = 'http://archive.kaskus.co.id/search'
    page = urllib.urlopen(archive_url, urllib.urlencode({'q':keywords}))
    links = []
    for link in BeautifulSoup(page, parseOnlyThese=SoupStrainer('a')):
        if link.has_key('href'):
            match = re.search('/thread/', link['href'])
            if match:
                links.append(link['href'])
    return random.choice(links)


def get_comments(url):
    page = urllib.urlopen(url).read()
    comments = []
    for comment in BeautifulSoup(page, 
                                 parseOnlyThese=SoupStrainer(
                                    'div', {'class':'pagetext'}
                                 )):
        for quote in comment.findAll('div'):
            quote.extract()
        comments.append(comment)
    return comments


def clean_tags(html):
    soup = BeautifulSoup(html)
    for tag in soup.findAll(True):
        if tag.name in IGNORED_TAGS:
            tag.hidden = True
    text = soup.renderContents()
    text = re.sub('http://.*\s', '', text, re.IGNORECASE)
    text = re.sub('\[.*\]\s', '', text)
    text = re.sub('\n', ' ', text)
    text = re.sub('\s+\s', ' ', text)
    text = re.sub('(^ +| +$)', '', text)
    return text
    

def windows(iterable, length=2, overlap=0):
    it = iter(iterable)
    results = list(itertools.islice(it, length))
    while len(results) == length:
        yield results
        results = results[length-overlap:]
        results.extend(itertools.islice(it, length-overlap))


def build_structure(string):
    return [' '.join(window) for n in range(len(string)) for
            window in windows(string.split(), n + 1, n)]


def clean_word(string):
    pattern = re.compile('[\W_]+')
    words = []
    for word in string.split():
        word = re.sub(pattern, ' ', word)
        words.append(word)
    return ' '.join(words)


def make_keywords(string):
    string = clean_word(string.lower())
    keywords = []
    for phrase in build_structure(string):
        if len(list(phrase.split())) >= 1 and len(list(phrase.split())) <= 2:
            if phrase is not None and phrase.strip() != '':
                keywords.append(phrase)
    return random.choice(keywords)


def swap(text, dictionary):
    x = re.compile(r'\b(%s)\b' % '|'.join(map(re.escape, dictionary.keys())))
    return x.sub(lambda m: dictionary[m.string[m.start():m.end()]], text)


def ask_kaskus(question):
    try:
        comments = []
        for comment in get_comments(kaskus_search(make_keywords(question))):
            comment = clean_tags(comment.renderContents())
            if len(comment) < 120 and comment.strip() != '':
                comments.append(comment)
        return swap(random.choice(comments), DEFAULT_SWAPWORDS).strip()
    except:
        return random.choice(DEFAULT_EXCUSES)
  
if __name__ == '__main__':
    question = raw_input('> ')
    while (question != 'quit'):
        try:
            print ask_kaskus(question).lower()
            question = raw_input('> ')
        except:
            sys.exit(1)
