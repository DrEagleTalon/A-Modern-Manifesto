# Sources: The Condition of the Working Class in England (CWC)

## German column

**Text:** MEW 2, pp. 225-506 (Dietz, Berlin 1972), via the mlwerke.de transcription mirrored at `github.com/wertform/mlwerke.de` (`me02/me02_225.htm` to `me02_486.htm`; `me02_225.htm` is the contents page and holds no text). MEW prints the text of the first edition (Leipzig 1845). In angle brackets on the page it gives the readings of the second edition (Stuttgart 1892), its own corrections of Engels's slips, and the wording of the English editions where that matters. These become the `variants` of the verse they sit in (62 in all), with the edition in `editions`: `1892`, `1845`, `1845 and 1892` (a slip in both editions that MEW corrects), `English 1887` or `English 1887 and 1892`, and `MEW` for an editorial remark. Angle brackets that only translate an English phrase ("Home Office <Ministerium des Innern>") are kept in the text as square brackets, the way the shared reader treats MEW's `|...|`.

**Sections.** MEW does not number the chapters; the numbers here follow the order of the book.

| Section | Contents | MEW |
|---|---|---|
| `P1892` | Engels's preface to the English edition of 1892, written in English | not in MEW 2 |
| `D` | "An die arbeitenden Klassen Großbritanniens", the dedication | pp. 229-231 |
| `P1845` | Vorwort, Barmen, 15 March 1845 | pp. 232-234 |
| `E` | Einleitung | pp. 237-252 |
| `I` | Das industrielle Proletariat | pp. 253-255 |
| `II` | Die großen Städte | pp. 256-305 |
| `III` | Die Konkurrenz | pp. 306-319 |
| `IV` | Die irische Einwanderung | pp. 320-323 |
| `V` | Resultate | pp. 324-359 |
| `VI` | Die einzelnen Arbeitszweige. Die Fabrikarbeiter im engeren Sinne | pp. 360-407 |
| `VII` | Die übrigen Arbeitszweige | pp. 408-429 |
| `VIII` | Arbeiterbewegungen | pp. 430-455 |
| `IX` | Das Bergwerksproletariat | pp. 456-472 |
| `X` | Das Ackerbauproletariat | pp. 473-485 |
| `XI` | Die Stellung der Bourgeoisie zum Proletariat | pp. 486-506 |

Paragraph 0 of each section is its heading. In VI, MEW's subheading "Die Fabrikarbeiter im engeren Sinne" is paragraph 1 and Wischnewetzky's "FACTORY HANDS." sits on it.

**The dedication** was written by Engels in English ("To the Working-Classes of Great-Britain") and printed in English in the German edition of 1845. MEW gives only its German translation, so `D` has MEW's German in the original column (marked as a translation in `source_original`) and an empty English column. Engels's English text should fill the English column when it is found on a reachable mirror; the verse numbers do not change.

**Not yet in the library:** the English texts Engels wrote for the American edition (a preface of 1887 and an appendix of 1886), and his preface to the second German edition (1892, MEW 22). These are separate texts that a later run can add as sections of their own.

**Footnotes.** Engels's notes ("Anmerkungen F. E.") are `<section>.N<n>` as in MEW, 87 in all. Seven that he added for the second edition or the English edition of 1887 carry `note_edition` (`II.N1`, `III.N4`, `V.N17`, `VIII.N6`, `VIII.N7`, `IX.N2`, `X.N5`).

**Reader.** The mlwerke.de pages of MEW 2 use a different markup from the volumes the shared reader (`scripts/lib/mew.py`) was written for. Page numbers appear as `<306>` and notes are linked as `#O<n>`, with editorial matter in angle brackets. The ingest has its own small reader for them (`read_de`, `markup`); `scripts/lib` is not changed. Tables become one paragraph, cells joined by spaces and rows by " / "; the lines of Mead's poem (VI.78.1 to VI.86.1) and of the list of fines from the Manchester Guardian (II.78) are joined by " / " too, and a line that ends a sentence ends the verse.

**Pictures.** Six images on the II page are left out: the plan of Manchester (MEW pp. 277-278), two plans of courts (after "etwa so:" in II.59.5 and II.61.7), one more plan of back-to-back houses, and two small drawings of brick bonds inside II.64.9. The text around them is kept.

**Markup repairs** (`HTML_FIXES`, applied in memory; the raw files are not touched):

- IV: the anchor of note 1 is missing, so the note would be lost;
- VIII: the link to note 5 is broken by a stray SMALL tag;
- III: the anchor for p. 314 lacks a closing quote mark and swallowed the page number;
- VIII: the page between 442 and 444 is numbered 277; read as 443;
- XI: a stray comma after the quotation from the Times (`XI.26.2`) would have joined it to the next paragraph.

The page number 334 is missing from the V page altogether, so verses on that page show `mew_page` 333 (up to V.11.4). One word is broken across a page number without a hyphen ("Überflüs <319> sigen", III.18.3); it is re-joined with the page marker in front (`SPLIT_WORDS`). Words broken with a hyphen are re-joined the same way.

**Repairs to the text** (`CORRECTIONS_DE` in `ingest/build_verses.py`). Letters misread in the transcription:

- `III.11.12`: "steiger die Preise noch m hr" corrected to "steigert die Preise noch mehr", and "ein pur Tausend Millionen" to "ein paar Tausend Millionen".
- `VII.31.7`: "1 2/2 Pence" corrected to "1 1/2 Pence".
- `II.55.8`: "Fußhoden" to "Fußboden". `E.23.1`: "dingender" to "dringender". `VI.65.2`: "agiterte" to "agitierte". `XI.9.6`: "ausgeprochen" to "ausgesprochen".
- `II.51.4`: "faßt eher über als unter vier" to "fast eher über als unter vier".
- `II.3.2`: "sehen die Laute einander" to "sehen die Leute einander".
- `VIII.27.8`: "Zutand" to "Zustand". `VI.64.3`: "des Unterleibe," to "des Unterleibs,".
- `V.16.3`: "Agrikultursistrikt" to "Agrikulturdistrikt".
- `X.8.14`: "N[orthern] S[tarl" to "N[orthern] S[tar]"; the open bracket stopped the sentence splitter for the whole list of fires.
- `III.9.1`: "(a. a. 0. [p. 133])" to "(a. a. O. [p. 133])". `VI.81.1`: "0 Schand'" to "O Schand'".
- In the notes: "Wealth of Nationa" (`V.N14.1.2`), "Londen 1833" (`XI.N2.1.3`), "Working Clssses" (`II.N9.1.1`), "Infant Labeur" (`II.N14.1.1`), "Britsh Association" (`V.N3.1.1`), "Armengesetz-Kommision" (`X.N2.1.1`), "Vgl," for "Vgl." (`V.N8.1.1`), "Rev," for "Rev." (`V.N18.1.2`).
- `XI.23.4`: "Armengesetz- Novelle" to "Armengesetz-Novelle".

Stray or wrong punctuation: `VI.22.2` ("Rachitis. aber"), `VI.73.1` ("beitragen. den"), `II.62.1` ("schmutzigen. und"), `V.42.3` ("ist. derselbe"), `X.16.9` ("nimmt. und"), `XI.19.15` ("festgebunden. wurden"), `XI.19.19` ("aufgenommen. zu werden"), `X.5.1` ("die,kühne Bauerschaft", a comma for an opening quote mark), `VI.36.1` ("l. daß" for "1. daß").

The letter l for the digit 1 in numbers is read as 1 in 13 places (`DIGIT_L`): `E.14.12` (1805), `E.20.3` (1844), `II.14.1` (19jährigen), `II.75.16` and `II.78.19` (10. August), `V.5.25` and `V.5.26` (1817/18, three letters), `VI.54.22` and `VI.N6.1.2` (1844), `VII.12.10` (10 sh.), `VII.19.16` (18 000), `VIII.17.7` (1838).

MEW's own notes: two variants in `VI.7.26` give the editions as "(1845 und 1882)"; there was no edition of 1882, so they are read as 1845 and 1892. "irrtumlich" in the variant at `VIII.17.7` is read as "irrtümlich".

These were found by reading and by a spelling check of rare words against a German word list; none has been checked against a printed MEW 2. Spellings of Engels's time ("Hülfe", "gebornen", "frugen", "hieher") are left alone, and so is the misspelled German of the two workers' letters that Engels prints as he received them (`VI.11.1` to `VI.11.4`, `VI.74`). In `VII.12.7` the transcription has "~" where MEW prints a dash for "nothing" in sums of money ("Pfd. St. 1~-~-"); it is left as transcribed.

**Paragraphs.** Where MEW sets a quotation or a table as a block in the middle of a sentence, the paragraph that ends mid-sentence (or the one after it that starts in lower case) is joined to its neighbour, as in the OF ingest. After a table only a lower-case start continues the sentence. That joins 3 places in E, 4 in II, 1 in III, 3 in V, 1 in VI, 1 in VII and 3 in XI. The result, not counting the heading, is 6 paragraphs in D, 7 in P1845, 24 in E, 6 in I, 81 in II, 18 in III, 5 in IV, 51 in V, 86 in VI, 33 in VII, 30 in VIII, 20 in IX, 21 in X and 30 in XI.

**Copyright.** Engels died in 1895; his words are in the public domain everywhere.

## English column

**Text:** Florence Kelley Wischnewetzky's translation, first published in New York in 1887 and reissued with Engels's consent in London in March 1892 (Swan Sonnenschein), as transcribed by Project Gutenberg (ebook 17306, ASCII, accents stripped) from the 1943 Allen & Unwin reprint of the 1892 edition. Both printings appeared before 1929, so the translation is in the public domain in the United States. Engels's preface of 1892 (`P1892`) was written by him in English and has no German column.

**What the English leaves out:** the dedication and the preface of 1845 (in `P1892.2.1` Engels says why the American preface of 1887 was dropped and that his appendix of 1886 is largely used in the new preface), Mead's poem at the end of VI with its two introductory sentences (`VI.77.1` to `VI.86.1`), and Engels's link sentence `V.37.1`. Wischnewetzky's "Translator's note" (on quotations she re-translated from the German because the English originals were not to hand) and the index are not part of Engels's work and are left out of the verses; her note is summed up here instead. Her footnote {145} says the same of the weaver's letter in `VI.11`, and it sits in `en_note` there.

**Wischnewetzky's footnotes.** The Gutenberg text keeps her footnotes at the end, keyed by page ({7}, {35a}, {113b} ...), 142 in all. The ingest pairs them with Engels's notes by position and content (`pair_notes`): 65 of Engels's 87 notes get her version in the English column of the note verses, and `en_note` on the first note verse names her key. Seven notes the scoring got wrong were set by hand after reading both texts (`NOTE_PAIRS`: `II.N5`, `V.N3`, `V.N4`, `V.N13`, `V.N15`, `VI.N19`, `X.N1`). The other 77 are references that the German gives in the text, or notes of the English editions; they are kept as `en_note` on the verse where her marker stands ("English note {32}: Times, Oct. 12th, 1843."). Notes of Engels's with no English pair say so in `en_note`.

**Repairs:** none to the words. Lines that end in a hyphen are joined without a space, keeping the printed hyphen of compounds broken at a line end ("labouring-classes"). Italics marked with underscores are dropped.

Wischnewetzky's English is careful but not literal. She renders "Bourgeoisie" now as "bourgeoisie", now as "middle-class", and "arbeitende Klasse" sometimes as "proletariat" (`E.1.1`); see `glossary.yaml`. Her English quotations from British sources are often the originals Engels translated (Alison in `V.36`, Ure in `VIII.13`), so they differ from his German in wording and length; these are flagged.

## Alignment

All sections with both languages are aligned sentence by sentence across paragraph breaks (`flat=True`). The cost function adds anchors on shared Latin-derived words and on a short German-English word list for the book's recurring words (Arbeiter/worker, Fabrik/mill, Lohn/wage, Keller/cellar), each weighted by how rare it is in the section, as in the OF ingest. A 1:4 bead is allowed. All of this is local to the ingest; nothing in `scripts/lib` was changed.

The sentence splitter is the shared one with local abbreviations (Ch. Empl. Comm., Fact. Inq., evid., sh., Rev., Rd.) and local repairs in `_split`: page markers after ordinals, no cut inside an open bracket, English sums of money kept whole ("1 pounds 6s. 6d.", `NO_BREAK`), and lines of tables and lists cut where a sentence ends.

`REALIGN` redistributes Wischnewetzky's sentences over a run of verses where the length method slipped, after reading both texts: `III.11.9` to `III.11.12`, `III.12.6` to `III.12.9`, `II.80.10` to `II.81.3`, `VII.18.3` to `VII.18.6`, `V.36.6` to `V.37.1`, `VI.11.1` to `VI.12.2` (the weaver's letter, four run-on German sentences against seventeen English ones), `VI.36.1` to `VI.37.1` and `VI.76.3` to `VI.86.1` (the serf and the free worker, where the match had run on into the poem). The English text is only moved, never changed. Verses with no English at all are not flagged; `en_note` says so.

**Review flags: 528.** 315 are places where Wischnewetzky splits one of Engels's sentences in two, 65 where she splits it in three or more, 124 where she joins two or three German sentences, 18 groups of equal size (2:2), 2 German sentences with no English (in `V.N18`, whose German is longer), 3 matches where the lengths differ a lot (`VI.25.2`, `VII.31.5`, `VIII.13.1`, all checked and right) and one note with an extra English sentence (`III.N2`). 20 of the flagged verses were regrouped by `REALIGN` and say so in `review_reason`. The flagged verses were read in the runs where flags cluster and wherever the English is much longer or shorter than the German; the rest are ordinary splits and joins.

## Verse counts

| Section | Verses | Of which notes |
|---|---|---|
| `P1892` | 187 | 0 |
| `D` | 23 | 0 |
| `P1845` | 24 | 0 |
| `E` | 166 | 3 |
| `I` | 32 | 2 |
| `II` | 567 | 46 |
| `III` | 139 | 9 |
| `IV` | 58 | 6 |
| `V` | 458 | 42 |
| `VI` | 613 | 59 |
| `VII` | 266 | 4 |
| `VIII` | 305 | 8 |
| `IX` | 219 | 5 |
| `X` | 187 | 13 |
| `XI` | 275 | 15 |
| total | 3519 | 212 |

## Raw file checksums (SHA-256)

From `sources/MANIFEST.yaml` (fetched 8 November 2026 by `scripts/fetch_sources.py`; unchanged in this run).

```
bc9936e1707db9f661b7b170ff01f96ea9606c1fdd3da34bf16f7e0dbaaca87f  sources/raw/de/me02_225.htm
2305aa538ad5dec462b00f07e17022adf38e12810d0d4d9829a2a648fc64440b  sources/raw/de/me02_229.htm
3613643da2922e45fe92d28a1589e99970e6ca6c13b2e559e8c54bdc2714e515  sources/raw/de/me02_232.htm
7cd35fcc944c9673f1c004291b0ea182c862cc68ca3a3e7f1423ad9330d88bc8  sources/raw/de/me02_237.htm
239f9fae75e21ccba1b373e581b23fc4ae4e5844c97b52884e0eb3db2b0c14a3  sources/raw/de/me02_253.htm
124839b2be1d7223e4078d60e073a9b3d6c2320c466f5cd359b24792300e9d3b  sources/raw/de/me02_256.htm
b6f68d08cc464aab5671e8f5393d671875b4cd04600e02cbc0729cc46b1945ef  sources/raw/de/me02_306.htm
6db44233b53be93b306774d51160601a8ccdb1f9e08f793c512808f0a8b81a74  sources/raw/de/me02_320.htm
09b2afe914417629bcfd208f9c9167f5c98bac1bca576e62a4f4292d61262b3f  sources/raw/de/me02_324.htm
08b91670e5518f7426b5033de39e1e9ec4e11973ff65d1139c34c9017c813829  sources/raw/de/me02_360.htm
368d97f557d9fa809e90154029ec7c20eb42837b7f8001161ec5f1177fa7f377  sources/raw/de/me02_408.htm
59ef44fa788c226afa67eba54d33ff7d181bbd3f18e3f5570dddc614e4be9999  sources/raw/de/me02_430.htm
d9473ac9711f203be41e0e78e6c4cd8a2514cb0333d3f42a4e18ef1cf54ca594  sources/raw/de/me02_456.htm
7588efb4164c7c894c9adae2baff1de6e7358f0e1bd563b7c9f442e545dea6c5  sources/raw/de/me02_473.htm
5844a9f6db7572ec94a387cb87c9bcc0ff8a9d94d9f3f57e1790146f5cb9e78d  sources/raw/de/me02_486.htm
4f3a7a3f034700c8ba2f5e303dd1b567d1beaa33bccbf66a0010f927ee6af6b2  sources/raw/en/gutenberg_17306.txt
```
