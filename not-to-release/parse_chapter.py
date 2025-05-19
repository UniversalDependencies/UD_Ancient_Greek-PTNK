#!/usr/bin/env python3

from html.parser import HTMLParser
import sys
import glob

MORPH = {}
with open('lexicon.tsv') as fin:
    for line in fin:
        ls = line.strip().split('\t')
        if not ls or ls[0] in MORPH:
            continue
        MORPH[ls[0]] = ls[1:]

book_abbrev = {
    'genesis': 'GEN',
    'ruth': 'RUTH',
}

class ChapterParser(HTMLParser):
    in_article = False
    chapter = None
    verse = None
    sentence = [] # [(link, gloss, surface),...]
    cur_link = None
    cur_gloss = None
    in_skip_element = False
    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            self.in_article = True
        if not self.in_article:
            return
        if tag == 'a':
            dct = dict(attrs)
            if 'id' in dct:
                if self.sentence:
                    self.write_tree()
                self.verse = dct['id']
            else:
                self.cur_link = dct.get('href')
                self.cur_gloss = dct.get('title')
        if tag in ['sup', 'h4']:
            self.in_skip_element = True
    def handle_data(self, data_):
        if not self.in_article:
            return
        if self.in_skip_element:
            return
        data = data_.strip()
        if not data:
            return
        if self.cur_link or self.cur_gloss:
            self.sentence.append((self.cur_link, self.cur_gloss, data))
            self.cur_link = None
            self.cur_gloss = None
        elif self.sentence:
            for c in data.split():
                self.sentence.append((None, None, c))
    def handle_endtag(self, tag):
        if tag == 'article':
            self.in_article = False
        if tag in ['sup', 'h4']:
            self.in_skip_element = False
    def get_ref(self):
        bk = self.chapter.split('/')[-1]
        ch = ''
        while bk[-1].isdigit():
            ch = bk[-1] + ch
            bk = bk[:-1]
        v = self.verse.strip('v')
        return book_abbrev.get(bk, bk) + '_' + ch.lstrip('0') + '.' + v.lstrip('0')
    def write_tree(self):
        print(f'# sent_id = {self.chapter.replace("KOINE/","")}_{self.verse}')
        for i, (link, gloss, surf) in enumerate(self.sentence):
            data = MORPH.get(link)
            if not data and link and '/names/' not in link:
                data = MORPH.get(link.replace('/lexicon/', '/names/'))
            ln = ['_']*10
            ln[0] = str(i+1)
            ln[1] = surf
            if data:
                ln[2] = data[1]
                ln[3] = data[2]
                ln[5] = data[3]
            else:
                ln[2] = surf
                ln[3] = 'PUNCT'
            misc = []
            if gloss:
                misc.append('Gloss=' + gloss.replace(', ', ',').replace(' ', '-'))
            misc.append('Ref=' + self.get_ref())
            if i+1 < len(self.sentence) and not self.sentence[i+1][0]:
                misc.append('SpaceAfter=No')
            ln[9] = '|'.join(misc) or '_'
            print('\t'.join(ln))
        print('')
        self.sentence = []

p = ChapterParser()
book = sys.argv[1]
book2file = {
    'genesis': 'gen',
    'ruth': 'ruth',
}
for fname in sorted(glob.glob(f'KOINE/lxx/{book2file[book]}*.html')):
    p.chapter = fname.rstrip('.html')
    with open(fname) as fin:
        p.feed(fin.read())
    if p.sentence:
        p.write_tree()
