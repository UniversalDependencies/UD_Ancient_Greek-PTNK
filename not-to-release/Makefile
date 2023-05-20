all: ready/genesis.conllu

ready/%.conllu: temp/%.hbo.conllu temp/%.grc.conllu temp/%.align.txt project.py
	mkdir -p ready
	./project.py $* > $@

#temp/genesis.hbo.conllu:

lexicon.tsv: extract_lexicon.py

temp/%.grc.conllu: lexicon.tsv
	./parse_chapter.py $* > $@

temp/%.words.txt: temp/%.hbo.conllu temp/%.grc.conllu
	./pair_sents.py $^ $@ temp/$*.ids.txt

temp/%.align.txt: temp/%.words.txt
	eflomal-align -i $< -m 2 -f $@ --overwrite
