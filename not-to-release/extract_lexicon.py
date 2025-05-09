#!/usr/bin/env python3

from html.parser import HTMLParser
import glob
import sys

known_pos = {
    'adj': 'ADJ',
    'adjective': 'ADJ',
    'adverb': 'ADV',
    'adv': 'ADV',
    'article': 'DET',
    'conjunction': 'CCONJ', # TODO
    'interjection': 'INTJ',
    'noun': 'NOUN',
    'number': 'NUM',
    'numeral': 'NUM',
    'part': 'PART', # TODO: maybe actually VERB participle?
    'particle': 'PART',
    'prep': 'ADP',
    'preposition': 'ADP',
    'pronoun': 'PRON',
    'verb': 'VERB',
}

known_tags = {
    '1st': 'Person=1',
    '2nd': 'Person=2',
    '3rd': 'Person=3',
    '1aor': 'Aspect=Perf|Tense=Past',
    '2aor': 'Aspect=Perf|Tense=Past',
    '1fut': 'Aspect=Imp|Tense=Fut',
    '2fut': 'Aspect=Imp|Tense=Fut',
    '1perf': 'Aspect=Perf|Tense=Past',
    '2perf': 'Aspect=Perf|Tense=Past',
    'acc': 'Case=Acc',
    'act': 'Voice=Act',
    'aor': 'Aspect=Perf|Tense=Past',
    'cardinal': 'NumType=Card',
    'comparative': 'Degree=Cmp',
    'dat': 'Case=Dat',
    'definite': 'Definite=Def',
    'demonstrative': 'PronType=Dem',
    'fem': 'Gender=Fem',
    'fem;': 'Gendef=Fem',
    'fut': 'Aspect=Imp|Tense=Fut',
    'futperf': 'Aspect=Perf|Tense=Fut',
    'gen': 'Case=Gen',
    'imperative': 'Mood=Imp',
    'imperativ': 'Mood=Imp',
    'imperat': 'Mood=Imp',
    'imperfect': 'Aspect=Imp|Tense=Past',
    'imperf': 'Aspect=Impf',
    'ind': 'Mood=Ind',
    'ind/imperative': 'Mood=Imp,Ind',
    'indefinite': 'Definite=Ind',
    'ind/subj': 'Mood=Ind,Sub',
    'infin': 'VerbForm=Inf',
    'interrogative': 'PronType=Int',
    'masc': 'Gender=Masc',
    'masc/fem': 'Gender=Fem,Masc',
    'masc/neut': 'Gender=Masc,Neut',
    'mfn': 'Gender=Fem,Masc,Neut',
    'mid': 'Voice=Mid',
    'mid/pass': 'Voice=Mid,Pass',
    'neg.': 'Polarity=Neg',
    'neut': 'Gender=Neut',
    'nom': 'Case=Nom',
    'nom/acc': 'Case=Acc,Nom',
    'nom/acc/voc': 'Case=Acc,Nom,Voc',
    'nom/voc': 'Case=Nom,Voc',
    'opt': 'Mood=Opt',
    'pass': 'Voice=Pass',
    'perf': 'Aspect=Perf|Tense=Pres',
    'personal': 'PronType=Prs',
    'pluperf': 'Aspect=Perf|Tense=Pqp',
    'plur': 'Number=Plur',
    'plural': 'Number=Plur',
    'possessive': 'PronType=Prs|Possessive=Yes',
    'pres': 'Tense=Pres',
    'pres/imperfect': 'Aspect=Imp|Tense=Past,Pres',
    'pres/fut': 'Aspect=Imp|Tense=Fut,Pres',
    'reciprocal': 'PronType=Rcp',
    'reflexive': 'PronType=Prs|Reflex=Yes',
    'relative': 'PronType=Rel',
    'sing': 'Number=Sing',
    'singular': 'Number=Sing',
    'subj': 'Mood=Sub',
    'superlative': 'Degree=Sup',
    'voc': 'Case=Voc',
}

skip_tags = {
    'transliterated',
    'hebrew',
    'word',
    'meaning',
    'form',
    '',
    'aramaic',
    'enclitic',
    'transliteration',
    'or',
    '+',
    'and',
    'and/or',
    'contracted',
    'indeclined',
    'verbal',
    'of',
    'person',
}

def process_parse(p):
    upos = ''
    feats = []
    unk = []
    for w_ in p.replace('Fut Perf', 'FutPerf').split():
        w = w_.strip(':').lower()
        if w in known_pos:
            upos += known_pos[w]
        elif w in known_tags:
            feats += known_tags[w].split('|')
        elif w in skip_tags:
            continue
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
                        if self.cur_page.endswith('/aut.html#auths'):
                            p = p.replace('Acc', 'Gen')
                        upos, feats = process_parse(p)
                        if self.cur_root == 'εἰμί':
                            upos = 'AUX'
                        if '/names/' in self.cur_page:
                            upos = 'PROPN'
                        print(f'{self.cur_page.replace("KOINE", "..")}#{ref}\t{head}\t{self.cur_root}\t{upos}\t{feats}')
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
for dirname in ['lexicon', 'names']:
    for fname in sorted(glob.glob(f'KOINE/{dirname}/*.html')):
        p.cur_page = fname
        with open(fname) as fin:
            p.feed(fin.read())
