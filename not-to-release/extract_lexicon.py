#!/usr/bin/env python3

from html.parser import HTMLParser
import glob
import sys

known_pos = {
    'Adj:': 'ADJ',
    'Adverb': 'ADV',
    'Adv:': 'ADV',
    'article:': 'DET',
    'Article:': 'DET',
    'Conjunction': 'CCONJ', # TODO
    'Noun:': 'NOUN',
    'noun': 'NOUN',
    'Number': 'NUM',
    'number': 'NUM',
    'Numeral': 'NUM',
    'Part:': 'PART', # TODO: maybe actually VERB participle?
    'particle': 'PART',
    'PREP': 'ADP',
    'Preposition': 'ADP',
    'Prep': 'ADP',
    'Pronoun:': 'PRON',
    'pronoun:': 'PRON',
    'Verb:': 'VERB',
}

known_tags = {
    '1st': 'Person=1',
    '2nd': 'Person=2',
    '3rd': 'Person=3',
    '1Aor': 'Aspect=Aor',
    '2Aor': 'Aspect=Aor',
    '1Fut': 'Tense=Fut',
    '2Fut': 'Tense=Fut',
    '1Perf': 'Aspect=Perf',
    '2Perf': 'Aspect=Perf',
    'Acc': 'Case=Acc',
    'Act': 'Voice=Act',
    'Aor': 'Tense=Aor',
    'Cardinal': 'NumType=Card',
    'cardinal': 'NumType=Card',
    'Comparative': 'Degree=Cmp',
    'Dat': 'Case=Dat',
    'Definite': 'Definite=Def',
    'Fem': 'Gender=Fem',
    'Fem;': 'Gendef=Fem',
    'Fut': 'Tense=Fut',
    'Gen': 'Case=Gen',
    'Imperative': 'Mood=Imp',
    'Imperativ': 'Mood=Imp',
    'Imperat': 'Mood=Imp',
    'Imperfect': 'Aspect=Impf',
    'Imperf': 'Aspect=Impf',
    'Ind': 'Mood=Ind',
    'Indefinite': 'Definite=Ind',
    'Ind/Subj': 'Mood=Ind,Sub',
    'Infin': 'VerbForm=Inf',
    'Masc': 'Gender=Masc',
    'Masc/Fem': 'Gender=Masc,Fem',
    'Masc/Neut': 'Gender=Masc,Neut',
    'MFN': 'Gender=Masc,Fem,Neut',
    'Mid': 'Voice=Mid',
    'Mid/Pass': 'Voice=Mid,Pass',
    'Neut': 'Gender=Neut',
    'Nom': 'Case=Nom',
    'Nom/Acc': 'Case=Nom,Acc',
    'Nom/Voc': 'Case=Nom,Voc',
    'Opt': 'Mood=Opt',
    'Pass': 'Voice=Pass',
    'Perf': 'Aspect=Perf',
    'Personal': 'PronType=Prs',
    'Plur': 'Number=Plur',
    'plur': 'Number=Plur',
    'Pres': 'Tense=Pres',
    'Reflexive': 'PronType=Prs|Reflex=Yes',
    'Relative': 'PronType=Rel',
    'Sing': 'Number=Sing',
    'Subj': 'Mood=Sub',
    'Superlative': 'Degree=Sup',
    'Voc': 'Case=Voc',
}

def process_parse(p):
    upos = ''
    feats = []
    unk = []
    for w in p.split():
        if w in known_pos:
            upos += known_pos[w]
        elif w in known_tags:
            feats.append(known_tags[w])
        else:
            unk.append(w)
    if unk:
        feats.append('Unknown=' + ','.join(unk))
    return upos or '_', '|'.join(sorted(feats)) or '_'

class LexiconParser(HTMLParser):
    in_dl = False
    in_dt = False
    in_parse = False
    cur_head = None
    cur_root = None
    next_data_is_parse = False
    cur_parse = []
    next_data_is_root = False
    cur_page = None
    cur_ref = []
    in_fieldset = False
    last_data_was_forms = False
    nested_ul = False
    def handle_starttag(self, tag, attrs):
        if tag == 'dl':
            self.in_dl = True
        elif tag == 'dt':
            self.cur_ref = []
            self.in_dt = True
        elif self.in_dt and tag == 'a':
            self.cur_ref.append(attrs[0][1])
        elif tag in ['span', 'li'] and ('class', 'parse') in attrs and not self.in_fieldset:
            self.next_data_is_parse = True
        elif self.in_dl and tag == 'script':
            src = dict(attrs).get('src')
            if src == 'js/verb/vpai1s.js':
                self.cur_parse.append('Verb: Pres Act Ind/Subj 1st Sing')
            elif src == 'js/verb/vpmpi1s.js':
                self.cur_parse.append('Verb: Pres Mid/Pass Ind 1st Sing')
            elif src == 'js/verb/vaainfin.js':
                self.cur_parse += [
                    'Verb: Aor Act Infin',
                    'Verb: Aor Act Opt 3rd Sing',
                    'Verb: Aor Mid Imperative 2nd Sing',
                ]
        elif tag == 'fieldset' or (self.last_data_was_forms and tag == 'ul'):
            self.in_fieldset = tag
        elif self.in_fieldset == 'ul' and tag == 'ul':
            self.nested_ul = True
    def handle_data(self, data_):
        data = data_.strip().strip(',').strip()
        if not self.in_dl or not data:
            return
        self.last_data_was_forms = False
        if self.in_dt:
            self.cur_head = data
            self.next_data_is_head = False
        elif self.next_data_is_parse:
            self.cur_parse.append(data)
            self.next_data_is_parse = False
        elif data == 'Root:':
            self.next_data_is_root = True
        elif self.next_data_is_root:
            self.cur_root = data
            self.next_data_is_root = False
        elif self.in_dl and data.startswith('Parse:'):
            st = data[6:].lstrip()
            if st: self.cur_parse.append(st)
        elif data == 'Forms:':
            self.last_data_was_forms = True
    def handle_endtag(self, tag):
        if tag == 'dl':
            self.in_dl = False
            if self.cur_root and ',' in self.cur_root:
                for w in self.cur_root.split(','):
                    if w.strip():
                        self.cur_root = w
                        break
            heads = []
            for h in (self.cur_head or '').split(','):
                if h.strip():
                    heads.append(h.strip())
                    if self.cur_root is None:
                        self.cur_root = h.strip()
            for head in heads:
                for ref in self.cur_ref or ['(no_id)']:
                    for p in self.cur_parse or ['###NO PARSE###']:
                        upos, feats = process_parse(p)
                        if self.cur_root == 'εἰμί':
                            upos = 'AUX'
                        print(f'{self.cur_page}#{ref}\t{head}\t{self.cur_root}\t{upos}\t{feats}')
                        weird = False
                        for c in ' ,':
                            for s in [head, self.cur_root]:
                                if isinstance(s, str) and c in s:
                                    weird = True
                        if weird:
                            print([self.cur_page, ref, self.cur_head, self.cur_root], file=sys.stderr)
            self.cur_parse = []
            self.cur_head = None
            self.cur_ref = []
            self.cur_root = None
        elif tag == 'dt':
            self.in_dt = False
        elif tag == 'ul' and self.nested_ul:
            self.nested_ul = False
        elif tag == self.in_fieldset:
            self.in_fieldset = False

p = LexiconParser()
for fname in sorted(glob.glob('KOINE/lexicon/*.html')):
    p.cur_page = fname
    with open(fname) as fin:
        p.feed(fin.read())
