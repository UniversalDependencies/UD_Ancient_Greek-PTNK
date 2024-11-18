#!/usr/bin/env python3

import re

dests = [
    ('genesis', [(1, 18, 'dev'), (19, 30, 'test'), (31, 50, 'train')]),
    ('ruth', [(1, 4, 'train')]),
]

output = {
    'train': [],
    'dev': [],
    'test': [],
}

book_names = {
    'genesis': 'Genesis',
    'ruth': 'Ruth',
}

fixes = [
    ('obl:tmod', 'obl'),
    ('PronType=Art', 'PronType=Dem'),
    ('obl:npmod', 'obl'),
    ('nmod:poss', 'nmod'),
    ('NumType=Card', ''),
    ('NumType=Ord', ''),
    ('PronType=Ind', ''),
    ('\t\t', '\t_\t'),
    ('|\t', '\t'),
    ('cc:preconj', 'cc'),
    ('advcl:relcl', 'advcl'),
    ('dislocated:relcl', 'dislocated'),
    ('cop:outer', 'cop'),
    ('nmod:relcl', 'nmod'),
    ('obj:relcl', 'obj'),
]

def parse_verse(sid, verse_re, book):
    m = verse_re.match(sid)
    if not m:
        raise ValueError(f'Unable to parse sent_id {v} in {book}.')
    ch = int(m.group(1))
    vs = int(m.group(2))
    return ch, vs

def process_sentence(sid, block, ranges, book, verse_re):
    global output
    ls = [parse_verse(v, verse_re, book) for v in sid.split('+')]
    verse = ''
    chs, vs = ls[0]
    che, ve = ls[-1]
    if chs != che:
        verse = f'{chs}:{vs}-{che}:{ve}'
    elif vs != ve:
        verse = f'{chs}:{vs}-{ve}'
    else:
        verse = f'{chs}:{vs}'
    nsid = f'# sent_id = Septuagint-{book_names[book]}-{verse}-grc'
    text = ''
    skip_to = None
    for line in block:
        ls = line.split('\t')
        if len(ls) != 10:
            continue
        if '.' in ls[0]:
            continue
        if skip_to:
            if skip_to == ls[0]:
                skip_to = None
            continue
        text += ls[1]
        if 'SpaceAfter=No' not in ls[9]:
            text += ' '
        if '-' in ls[0]:
            skip_to = ls[0].split('-')[1]
    out = '\n'.join([nsid, f'# text = {text.strip()}'] + block)
    for a, b in fixes:
        out = out.replace(a, b)
    for a, b, d in ranges:
        if a <= chs <= b:
            output[d].append(out)
            break
    else:
        raise ValueError(f'Chapter {chs} of {book} has no destination')

def process_book(book, ranges):
    verse_re = re.compile(f'^lxx/{book}(\\d+)_v(\\d+)$')
    with open(f'ready/{book}.conllu') as fin:
        cur = []
        sid = None
        for line in fin:
            if not line.strip():
                if sid:
                    process_sentence(sid, cur, ranges, book, verse_re)
                    cur = []
                    sid = None
            elif 'sent_id =' in line:
                sid = line.split()[-1]
            else:
                cur.append(line.strip())
        if sid:
            process_sentence(sid, cur, ranges, book, verse_re)

for book, ranges in dests:
    try:
        process_book(book, ranges)
    except FileNotFoundError:
        print(f'{book} not found, skipping')

for k, v in output.items():
    with open(f'temp/grc_ptnk-ud-{k}.conllu', 'w') as fout:
        fout.write('\n\n'.join(v) + '\n\n')
