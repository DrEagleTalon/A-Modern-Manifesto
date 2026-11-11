# Sources: The Eighteenth Brumaire of Louis Bonaparte (EB)

## German column

**Text:** MEW 8, pp. 115-207 (Dietz, Berlin 1960), via the mlwerke.de transcription mirrored at `github.com/wertform/mlwerke.de` (`me08/me08_115.htm` to `me08_194.htm`, one page per chapter; `me08_111.htm` is the contents page and holds no text). MEW prints the second edition (Hamburg 1869), which Marx revised lightly, with a few stylistic changes taken from the third edition (1885). Marx wrote the work between December 1851 and March 1852 for Joseph Weydemeyer's *Die Revolution* (New York, May 1852).

**Prefaces.**

- `P1869`: Marx's preface to the second edition, MEW 16, pp. 358-360 (`me16_358.htm`). Original German. De Leon did not translate it, so its English column is empty. Its footnote on Weydemeyer is `P1869.N1`.
- `P1885`: Engels's preface to the third edition, MEW 21, pp. 248-249 (`me21_248.htm`). Original German, no English.

Both pages were added to the catalog sources in this run; the eight MEW 8 pages are unchanged from the earlier fetch (same checksums).

**Footnotes.** Marx's four notes in VII are `VII.N1` to `VII.N4`. MEW 8 and 16 link footnotes as `#M<n>`, not the `#F<n>` the shared reader expects; the ingest rewrites the links in a copy of the page before parsing (the raw files are not touched).

**The 1852 ending of VII.27.** MEW prints, in angle brackets after VII.27, the lines with which the 1852 edition ended that paragraph and which Marx cut in 1869 ("Die Zertrümmerung der Staatsmaschinerie wird die Zentralisation nicht gefährden ... zum Sterbelied wird"). They are not part of the base text, so they are a `variants` entry (ref `1852`) on the paragraph's last verse, `VII.27.5`, not verses of their own. De Leon translated the 1869 text and does not have them.

**MEW's editorial insertions** in angle brackets (German renderings of French and Latin phrases such as `<Handstreich>`, `<Staatsstreichs>`, and one cross-reference `<Siehe MEW, Bd. 8, S. 336-341>`) are kept as printed, as in WLC. One bracketed reference, "(MEW Bd. 7, S. 44/45)" in II.15.1, hangs on the sentence it cites.

**Markup repairs** (in `_prepare` and `HTML_FIXES`, before parsing):

- pages 115 to 148 are Windows-1252, not Latin-1; byte 0x96 is a dash and becomes " - " as on the UTF-8 pages, 0x92 becomes an apostrophe;
- emphasis tags are dropped, which keeps "G<EM>eschichte" (II.2.1) and "Februar<EM>-Regierung" (I.14) whole and removes a stray tag inside "4. Mai 1</I>848" (I.13.1);
- page anchors with `<STRONG>` inside them are flattened so words broken across a page ("Ordnungs- <138> partei") are re-joined; "St-Jean-d'Angely" (V.19.6) keeps its hyphen;
- in VI one item of the closing schema ("Dritte Periode") has no `<P>` tag and is given one.

**Repairs to the text** (see `CORRECTIONS_DE` in `ingest/build_verses.py`):

- `I.2.3`: "die neuen Weltgeschichtsszene" corrected to "die neue Weltgeschichtsszene".
- `III.26.5`: "sei Körper" corrected to "sein Körper".
- `V.16.12`: "Gesellschaft vom 10! Dezember." corrected to "Gesellschaft vom 10. Dezember!".
- `VII.8.1`: "C est" corrected to "C'est".
- `VII.21.1`: "protestierte in Teil" corrected to "protestierte ein Teil".
- `VII.28.1`: stray comma removed in "auf den Berg Sinai, führten".
- `VII.30.2`: comma before "Er weiß" corrected to a full stop.
- `VII.33.14`: "Ludwig XV," corrected to "Ludwig XV.".
- `P1869.1.2`: MEW's gloss "Staatstreichs" corrected to "Staatsstreichs".
- `P1869.9.1`: the date line reads "London, 23. Juni 1859" in the mirror; MEW 16 dates the preface 23 June 1869.

These have not been checked against a printed MEW 8; a second mirror (`MARX-EBOOKS/MLRAW`) was not compared in this run.

**Paragraphs.** MEW sets "Hic Rhodus, hic salta! Hier ist die Rose, hier tanze!" as a separate block in the middle of a sentence; it is joined to I.8 (`JOIN_AFTER`). No other paragraphs are joined. That gives 19 paragraphs in I, 24 in II, 26 in III, 20 in IV, 26 in V, 57 in VI (the closing schema is one paragraph per item, as in MEW) and 34 in VII.

**Copyright.** Marx's and Engels's words are in the public domain.

## English column

**Text:** Daniel De Leon's translation (*The Eighteenth Brumaire of Louis Bonaparte*, International Publishing Co., New York 1898, later New York Labor News), as transcribed by Project Gutenberg (ebook 1346, ASCII, accents stripped). De Leon died in 1914; the translation is in the public domain in the United States. De Leon's own translator's preface (dated 12 September 1897) is not part of Marx's work and is left out.

De Leon translated the 1869 text. His English is free: he often joins two or three of Marx's sentences with semicolons and dashes, adds words, and in places slips on dates and figures (III.5.1 gives December 20, 1849 for 1848; V.2.19 gives a committee of 18 for 28). Those are left as he wrote them and listed in `cruxes.md`. He calls the Bauern "farmers" and the Lumpenproletariat "the slums"; see `glossary.yaml`.

**De Leon's notes.** The Gutenberg text carries De Leon's glosses inline as `[#n ...]`, numbered from 1 in each chapter (VII has no note 3). They are taken out of the verse text and kept as `en_note` on the verse where they stand ("De Leon's note [1]: Silk-stocking republican"). His notes 10, 11, 13 and 15 in VII are his versions of Marx's own footnotes and fill the English column of `VII.N1` to `VII.N4`. He attaches note 15 one verse earlier than MEW, which `VII.33.14` records.

**Repairs** (see `CORRECTIONS_EN`):

- `I.1.3`: "1793-05" corrected to "1793-95".
- `I.12.1`: stray apostrophe removed in "of' February".
- `II.16.10`, `V.4.3`, `V.18.4`, `VI.33.3`, `VI.38.6`: a full stop missing between two sentences restored.
- `VI.34.3`: "His own Prime Minister. Odillon Barrot," corrected to a comma.
- `VI.47.2`: "against the house of Mr. proletariat" corrected to "against the proletariat" (the words are carried over from a line further up the Gutenberg file).
- `VII.2.13`: "Oniesce" corrected to "Quiesce".
- `VII.6.7`: "Messieurs. Bourgeois" corrected to "Messieurs Bourgeois".
- `VII.8.1`: "Ic triomphe" corrected to "le triomphe", and a stray quotation mark removed.
- `VII.16.2`: "turns I up" corrected to "turns up".

**Known defects not repaired**, since the right reading cannot be recovered without the 1898 printing: "Hegel says somewhere that that great historic facts" (`I.1.1`), and a garbled clause in `VII.11.1` ("under the absolute monarchy, was only the means whereby the first revolution, and under Napoleon, to prepare"). Both are in `cruxes.md`.

## Alignment

The chapters are aligned sentence by sentence across paragraph breaks (`flat=True`): De Leon has 23, 31, 27, 20, 24, 54 and 33 paragraphs against Marx's 19, 24, 26, 20, 26, 57 and 34. The cost function adds an anchor on shared Latin-derived words (Konstitution/Constitution, Legitimisten/Legitimists), as in the SUS ingest.

The sentence splitter is the shared one, with local repairs in `_split`: page markers after ordinals, MEW's angle-bracket translations, a few pairs kept together (`NO_BREAK`, such as "Henri V! Henri V!" and "Vive Napoléon! Vivent les saucissons!"), short bracketed references hung on the sentence they cite, and De Leon's list letters (a. to d.) kept with their items. Nothing in `scripts/lib` was changed.

`REALIGN` redistributes De Leon's sentences over a run of verses where the length method slipped by one sentence: `I.12.1` to `I.13.1`, `III.14.9` to `III.16.5`, `V.4.10` to `V.4.14`, `VII.8.6` to `VII.9.4` and `VII.23.17` to `VII.24.9`. The English text is only moved, never changed.

**Review flags:** 118, all in I to VII. 97 are places where De Leon joins two or more of Marx's sentences into one (80 of them 2:1); 21 are places where he splits one German sentence in two. 7 of the flags are verses regrouped by `REALIGN`, which say so in `review_reason`. The prefaces and notes have none: `P1869` and `P1885` have one column.

## Verse counts

| Section | Verses | Of which notes |
|---|---|---|
| `P1869` | 32 | 1 |
| `P1885` | 16 | 0 |
| `I` | 107 | 0 |
| `II` | 148 | 0 |
| `III` | 199 | 0 |
| `IV` | 139 | 0 |
| `V` | 250 | 0 |
| `VI` | 281 | 0 |
| `VII` | 230 | 4 |
| total | 1402 | 5 |

## Raw file checksums (SHA-256)

```
b48d32d7c80b21dc3afc7c8ad11d81ef829a91f30274c607c9d968b8a1d3bb9f  sources/raw/de/me08_111.htm
b2f8252ebfab08c3b54ed7028d040133a56375ddb3bbaf6a18ae98a4f0179cef  sources/raw/de/me08_115.htm
9f12e151a621d75f7272a8673109fa111daab337b6e518b1d45e6d91a205a957  sources/raw/de/me08_124.htm
c1c103ecddb26bad665fa3fe5e72c14ae586ee5af8f65e6fa5abd965ba3cf320  sources/raw/de/me08_135.htm
b4b839fbbb0f0e13adfdf6be5d078e342360419fd178dd288b00e22edfda08ec  sources/raw/de/me08_149.htm
6200a5fe484efc8cbdee40b806d5f8ece7dd6d9946eec3896d3baa7d1c10e714  sources/raw/de/me08_159.htm
dd7ff76b21d97cfbd736a5559593da114985a7d361536f87414852061d3adb4d  sources/raw/de/me08_176.htm
5a37abf1b70e6292b8424516c1e9309d738f7b1f6098021bf05818139a8dcdc6  sources/raw/de/me08_194.htm
9b2456bcd04bfb5cd38003264bf81d71299b9e1213c15539a946f6102326f248  sources/raw/de/me16_358.htm
97c73fb49d6acc5407ef60826c6d60e0b1a74e7eecf2245651027738d7e6bf8a  sources/raw/de/me21_248.htm
c45c7e95f7db0fab7ce7ff151ef19860ee170d26fd6b48da467b4aa044e09dfc  sources/raw/en/gutenberg_1346.txt
```
