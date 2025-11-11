#!/bin/bash

for f in temp/grc_ptnk*.conllu
do
  echo "$f -> ${f/temp/..}"
  env/bin/udapy -s ud.FixPunct < "$f" > "${f/temp/..}"
done
