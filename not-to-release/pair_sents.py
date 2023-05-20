#!/usr/bin/env python3

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('hbo', action='store')
parser.add_argument('grc', action='store')
parser.add_argument('words', action='store')
parser.add_argument('ids', action='store')
args = parser.parse_args()

def parse_id(sid):
    if sid.endswith('-hbo'):
        ls = sid.replace(':', '-').split('-')
        if len(ls) == 5:
            return (int(ls[2]), int(ls[3]), int(ls[3]))
        else:
            return (int(ls[2]), int(ls[3]), int(ls[4]))
    else:
        ls = sid.split('_')
        i = len(ls[0])-1
        while ls[0][i].isdigit(): i -= 1
        return (int(ls[0][i+1:]), int(ls[1][1:]))

skip_words = ['(', ')', ',', '.', ';', '[', ']', '·', '־', '׀', '׃', '—', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'ס', 'פ', ',']

def load(fname):
    with open(fname) as fin:
        ret = {}
        for block in fin.read().split('\n\n'):
            if not block.strip(): continue
            sid = None
            words = []
            for l in block.splitlines():
                if 'sent_id' in l:
                    sid = l.split('=')[1].strip()
                ls = l.split('\t')
                if len(ls) == 10 and ls[0].isdigit() and ls[2] not in skip_words:
                    words.append((ls[0], ls[2]))
            if not sid:
                print(len(ret), fname)
            ret[parse_id(sid)] = (sid, words)
        return ret

hbo = load(args.hbo)
grc = load(args.grc)
with open(args.words, 'w') as wout:
    with open(args.ids, 'w') as iout:
        for sid in hbo:
            gw = []
            gi = []
            for v in range(sid[1], sid[2]+1):
                k = (sid[0], v)
                if k in grc:
                    ls = [grc[k][0]]
                    for wid, lem in grc[k][1]:
                        ls.append(wid)
                        gw.append(lem)
                    gi.append('+'.join(ls))
            if gw:
                wout.write(' '.join(x[1] for x in hbo[sid][1]) + ' ||| ' + ' '.join(gw) + '\n')
                iout.write(hbo[sid][0] + '+' + '+'.join(x[0] for x in hbo[sid][1]) + ' ' + ' '.join(gi) + '\n')
