#!/bin/bash

for f in temp/*.conllu
do
  echo "$f -> ${f/temp/..}"
  env/bin/udapy -s ud.FixPunct < "$f" > "${f/temp/..}"
done
