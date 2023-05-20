#!/usr/bin/env python3

import sys

class Tree:
    def __init__(self):
        self.sent_id = None
        self.comments = []
        self.words = []
        self.ided = False
    def renumber(self):
        old2new = {}
        for i, w in enumerate(self.words, 1):
            old2new[w[0]] = str(i)
            w[0] = str(i)
        for w in self.words:
            w[6] = old2new.get(w[6], w[6])
        self.ided = False
    def idify(self):
        if self.ided:
            return
        for w in self.words:
            w[0] = self.sent_id + ':' + w[0]
            if w[6] != '_':
                w[6] = self.sent_id + ':' + w[6]
        self.ided = True
    def append(self, other):
        other.idify()
        self.words += other.words
        self.sent_id += '+' + other.sent_id
    def to_conllu(self):
        ls = [f'# sent_id = {self.sent_id}'] + self.comments
        ls += ['\t'.join(w) for w in self.words]
        return '\n'.join(ls)

def load(fname):
    with open(fname) as fin:
        ret = {}
        for block in fin.read().split('\n\n'):
            if not block.strip(): continue
            t = Tree()
            for line in block.splitlines():
                if line.startswith('#'):
                    if 'sent_id' in line:
                        t.sent_id = line.split('=')[1].strip()
                    else:
                        t.comments.append(line.strip())
                elif line.count('\t') == 9:
                    t.words.append(line.strip().split('\t'))
            ret[t.sent_id] = t
        return ret

book = sys.argv[1]
hbo = load(f'temp/{book}.hbo.conllu')
grc = load(f'temp/{book}.grc.conllu')
with open(f'temp/{book}.ids.txt') as idin:
    with open(f'temp/{book}.align.txt') as alignin:
        for ids, aligns in zip(idin, alignin):
            if not ids.strip():
                continue
            idls = ids.split()
            hw = idls[0].split('+')[1:]
            hid = idls[0].split('+')[0]
            ht = hbo[hid]
            gt = None
            gw = []
            for gs in idls[1:]:
                ls = gs.split('+')
                grc[ls[0]].idify()
                if gt is None:
                    gt = grc[ls[0]]
                else:
                    gt.append(grc[ls[0]])
                gw += [ls[0] + ':' + x for x in ls[1:]]
            pairings = []
            for pair in aligns.split():
                hidx, gidx = pair.split('-')
                pairings.append((hw[int(hidx)], gw[int(gidx)]))
            h2g = dict(pairings)
            h2g['0'] = '0'
            g2h = dict([(y,x) for x,y in pairings])
            h2rel = {}
            for word in ht.words:
                h2rel[word[0]] = (word[6], word[7])
            for word in gt.words:
                if word[0] in g2h:
                    oid = g2h[word[0]]
                    rel = h2rel[oid]
                    if rel[0] in h2g:
                        word[6] = h2g[rel[0]]
                        word[7] = rel[1]
            gt.renumber()
            print(gt.to_conllu())
            print('')

