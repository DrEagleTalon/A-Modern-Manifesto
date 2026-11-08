# Sources: Socialism: Utopian and Scientific (SUS)

## German column

**Text:** MEW 19, pp. 177-228 (Dietz, Berlin 1962), via the mlwerke.de transcription mirrored at `github.com/wertform/mlwerke.de` (`me19/me19_181.htm` to `me19_210.htm`; `me19_177.htm` is the title page and holds no text). MEW prints the fourth German edition (Stuttgart 1891), the last Engels revised. The pamphlet is three chapters of *Anti-Dühring* (1878), which Engels reworked for Paul Lafargue's French version (*Revue socialiste*, 1880) and again for the German editions of 1882 (dated 1883) and 1891.

**Prefaces.**

- `P1880`: Marx's preface to the French edition. Marx wrote it in French and it appeared over Lafargue's name. The German here is MEW's translation, not an original. The French is not in this repository yet; when a public-domain French text is added it becomes a reference column and the verse numbers do not change (the rule in VERSIFICATION.md for CM P1893). MEW's two readings from the Lafargue-signed printing are attached as `variants`.
- `P1882`: Engels's preface to the first German edition, original German. Aveling did not translate it, so its English column is empty. Its footnote `P1882.N1` was added by Engels in the third edition of 1883.
- `P1892`: Engels's special introduction to the English edition, written by Engels in English. Here the English sets the verses (as in CM P1888) and the German column is empty. MEW 22 has a German translation that can be added later as a reference column without changing the verse numbers.

**Variants.** MEW 19 records two more readings, both single words: `II` from the French edition, `III` from *Anti-Dühring*. MEW gives them no edition label; the ingest labels them from the wording of the reading.

**Second mirror check.** The `MARX-EBOOKS/MLRAW` copy of the five text pages (`mewerke/me19/`) matches word for word, including the errors repaired below, so these repairs still need checking against a printed MEW 19.

**Repairs** (see `CORRECTIONS_DE` in `ingest/build_verses.py`):

- `I.11.1`: "ranzösischen" corrected to "französischen".
- `I.11.3`: stray comma removed in "die, besitzende Bourgeoisie".
- `I.16.10`: space removed before the closing quotation mark.
- `I.N1.1.7`: "gekommen.." corrected to `gekommen."`, closing Hegel's quotation.
- `III.1.2`: stray comma removed in "sondern in, Veränderungen".
- `III.17.1`: "Gesellschaft- diese" spaced as a dash, "Gesellschaft - diese".
- `III.17.5`: "Oberfluß" corrected to "Überfluß".

**Paragraphs.** MEW sets some quotations as separate paragraphs in the middle of a sentence (Saint-Simon's "alle Menschen arbeiten sollen", Fourier on civilisation, Owen's "die Leute waren meine Sklaven"). The ingest joins a paragraph that ends without closing punctuation, or one that starts in lower case, to the one before, so each sentence keeps one address. That gives 26 paragraphs in I, 12 in II and 33 in III.

**MEW's editorial brackets** ("[Siehe: Karl Marx, "Das Kapital" ...]", "["Die Mark"]") are kept, attached to the sentence they follow.

**The appendix.** Footnote `III.N2` points to Engels's appendix "Die Mark". It is in MEW 19 but outside the page range fetched, and the Kerr reprint used for the English leaves it out. It can be added later as section `A`.

**Copyright.** Marx's and Engels's words are in the public domain.

## English column

**Text:** Edward Aveling's translation, authorised by Engels (*Socialism, Utopian and Scientific*, Swan Sonnenschein, London 1892), with Engels's special introduction, in the Charles H. Kerr reprint (Chicago 1908) as transcribed by Project Gutenberg (ebook 39257, from an Internet Archive scan). Public domain in the United States. Kerr's 1908 publisher's note is left out.

Aveling translated from the German. He often splits one long German sentence into two or three, so most review flags in I to III are `1:2` or `1:3` matches, which is how VERSIFICATION.md handles them.

**Footnotes.** Aveling numbers Engels's notes [1] to [8] across the book. They are matched to MEW's notes: `I.N1`, `I.N2`, `III.N1` to `III.N5`. Aveling places his note on "The Revolution in Mind and Practice" one quotation earlier than MEW (`I.20.2`, recorded in `en_note`), and adds a note of his own, "Note, l. c., p. 70.", which MEW does not have; it is `I.E1`, following CM E1. The introduction's notes [A] to [C] are Engels's English notes `P1892.N1` to `P1892.N3`.

**Repairs:** Gutenberg writes the pound sign as "L" (`L300,000`); the ingest restores "£" in `I.21.2` and `III.N5`.

**Not used.** The Marxists Internet Archive pages fetched with the sources (`raw/en/ch01.html` to `ch03.html`, `int-hist.html`, `int-mat.html`, `guide.html`, `index.html`) are an MIA transcription of the same translation (CC BY-SA) plus a study guide. They are kept for checking the Gutenberg text, not built from.

## Alignment

The chapters are aligned sentence by sentence across paragraph breaks (`flat=True`), since Aveling re-paragraphs (30, 18 and 41 English paragraphs against 26, 12 and 33 German). Three repairs the length method could not make on its own are scripted in the ingest:

- an anchor on shared Latin-derived words (Dialektik/dialectic), which fixed a drift in `II.3.1` to `II.3.6`;
- `REGROUP`: `I.16.10` is joined to `I.16.9`, because Aveling folds "So daß z.B." into the previous sentence;
- `MOVE_EN`: one English sentence moved across a verse boundary at `I.6.1` and one at `III.10.8`.

The sentence splitter is the shared one, with local repairs listed in `_split` (page markers after ordinals, square brackets, "Pfd. St.", "a. M.", "usw." at a sentence end). Nothing in `scripts/lib` was changed.

**Review flags:** 83, all in I to III and their notes. 77 are places where Aveling uses two or more sentences for one German sentence or the reverse; 3 are the figures in `III.N5` (the German gives pounds and marks, the English pounds only); 3 are the regrouped verses `I.6.1`, `I.16.9` and `III.10.8`. Each has a `review_reason`. The prefaces have none: `P1880` and `P1882` have one column, `P1892` sets its own verses.

## Verse counts

| Section | Verses | Of which notes |
|---|---|---|
| `P1880` | 21 | 0 |
| `P1882` | 35 | 6 |
| `P1892` | 302 | 10 |
| `I` | 167 | 11 |
| `II` | 77 | 0 |
| `III` | 265 | 17 |
| total | 867 | 44 |

## Raw file checksums (SHA-256)

```
740d8d9c1b2d1a983f817fec8aedb09c0cedc627f4279e03e711ce43cbe52b8f  sources/raw/de/me19_177.htm
723839ec48e4f3c971d2b55d0f4327deef18e112a4ab32b3fbff89e45c391811  sources/raw/de/me19_181.htm
75e8a02aff550f28549619de334438bf2740104b854a6b84ddef2714244a5ef6  sources/raw/de/me19_186.htm
a14d5683c263ce12660e44c128ee3e701db805eeafba1f970c4094098a063cba  sources/raw/de/me19_189.htm
c868b556fd614c40abd3d688089b172995cb607d2fd7a131b61559cfe5d84a9e  sources/raw/de/me19_202.htm
103d07d294471e229d29ef4befd0fafb623f6eeaec5c85ed44da905bc5edfe99  sources/raw/de/me19_210.htm
5245774ef9ead57dc56a6e8337d2503bf962ad8ea367671e081096ea82cce122  sources/raw/en/gutenberg_39257.txt
```
