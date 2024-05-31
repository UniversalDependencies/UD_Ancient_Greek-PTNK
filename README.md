# Summary

UD Ancient Greek PTNK contains portions of the Septuagint according to the Codex Alexandrinus.

# Introduction

This treebank was produced using text extracted from https://greekdoc.github.io with initial syntactic relations produced by word-aligning and projecting the relations from the parallel Ancient Hebrew treebank.

# Data Split

The following texts are included in this treebank:

| Book    | Chapters | Split | Added |
|---------|----------|-------|-------|
| Genesis | 1-18     | Dev   | 2.13  |
|         | 19-30    | Test  | 2.13  |
|         | 31-50    | Train | 2.13  |
| Ruth    | 1-4      | Train | 2.13  |

# Acknowledgments

Thank you to John Barach for granting permission to use his morphological annotations in this treebank.

## References

```
@inproceedings{swanson-etal-2024-producing-parallel,
    title = "Producing a Parallel {U}niversal {D}ependencies Treebank of {A}ncient {H}ebrew and {A}ncient {G}reek via Cross-Lingual Projection",
    author = "Swanson, Daniel G.  and
      Bussert, Bryce D.  and
      Tyers, Francis",
    editor = "Calzolari, Nicoletta  and
      Kan, Min-Yen  and
      Hoste, Veronique  and
      Lenci, Alessandro  and
      Sakti, Sakriani  and
      Xue, Nianwen",
    booktitle = "Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)",
    month = may,
    year = "2024",
    address = "Torino, Italia",
    publisher = "ELRA and ICCL",
    url = "https://aclanthology.org/2024.lrec-main.1145",
    pages = "13074--13078",
    abstract = "In this paper we present the initial construction of a treebank of Ancient Greek containing portions of the Septuagint, a translation of the Hebrew Scriptures (1576 sentences, 39K tokens, roughly 7{\%} of the total corpus). We construct the treebank by word-aligning and projecting from the parallel text in Ancient Hebrew before automatically correcting systematic syntactic mismatches and manually correcting other errors.",
}
```


# Changelog

* 2023-11-15 v2.13
  * Initial release in Universal Dependencies.


<pre>
=== Machine-readable metadata (DO NOT REMOVE!) ================================
Data available since: UD v2.13
License: CC BY-SA 4.0
Includes text: yes
Genre: bible
Lemmas: manual native
UPOS: manual native
XPOS: not available
Features: manual native
Relations: manual native
Parallel: Bible (Ref)
Contributors: Swanson, Daniel
Contributing: here
Contact: awesomeevildudes@gmail.com
===============================================================================
</pre>
