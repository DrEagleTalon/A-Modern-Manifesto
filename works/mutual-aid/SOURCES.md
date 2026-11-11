# Sources: Mutual Aid: A Factor of Evolution (MA)

## Original column (English)

Kropotkin wrote Mutual Aid in English. The chapters first appeared as articles in *The Nineteenth Century* between 1890 and 1896, in reply to Huxley's essay "The Struggle for Existence" (1888). He revised and enlarged them for the book, published by William Heinemann, London, in 1902 (New York: McClure, Phillips, the same year). The `original` column holds that English text. There is no historical-translation column (`columns.en` is empty), as in VPP, CWF and AOE.

**Text:** Project Gutenberg ebook 4341 (first posted 2002, revised 2011), "Produced by Charles Aldarondo", the plain ASCII file `4341.txt`, mirrored at `github.com/GITenberg/Mutual-Aid--A-Factor-of-Evolution_4341`. It reproduces the 1902 title page and Kropotkin's Introduction signed "Bromley, Kent, 1902". It does not say which printing it follows. A scan of the 1902 Heinemann printing on archive.org would settle the edition and the open questions below.

**What the transcription lacks.** It has no accents ("Koln", "Societes animales", "Besancon") and no italics, so titles of books and foreign words are set in plain type. Both are kept as transcribed. It also leaves out the book's **Appendix** (seventeen short notes, numbered I to XVII, with further material on ants, birds, the village community and the guilds). The notes still point to it ("See Appendix II.", `I.N7.1.4`; also `III.N31.1.1`, `IV.N5.1.6`, `VI.N2.1.3`) and the Introduction describes it (`P1902.17`). When a transcription of the Appendix is found it can be added as a new section `A` with its own ids; the ids here do not change.

**Rights.** Kropotkin died in 1921. The book was published in 1902, and works published before 1931 are in the public domain in the United States in 2026. It is also out of copyright in every country with a term of life plus 70 years or less. Project Gutenberg's licence covers its trademark and header, which are not used here.

**Left out.** The Gutenberg header and licence, and the title page, are not versified.

## Sections and numbering

| Section | Contents |
|---|---|
| `P1902` | Kropotkin's Introduction, dated Bromley, Kent, 1902 |
| `I` | Mutual Aid among Animals |
| `II` | Mutual Aid among Animals (continued) |
| `III` | Mutual Aid among Savages |
| `IV` | Mutual Aid among the Barbarians |
| `V` | Mutual Aid in the Mediaeval City |
| `VI` | Mutual Aid in the Mediaeval City (continued) |
| `VII` | Mutual Aid amongst Ourselves |
| `VIII` | Mutual Aid amongst Ourselves (continued) |
| `C` | Conclusion |

The chapter numbers are Kropotkin's. The Introduction is `P1902` by the library's rule for prefaces and introductions. The Conclusion is unnumbered in the book and is `C` here.

Paragraph 0 of each section is its heading, written in title case (the transcription sets headings in capitals).

**Chapter summaries.** Under each chapter title the book prints a summary of the chapter as a run of short phrases ("Struggle for existence. Mutual Aid a law of Nature and chief factor of progressive evolution. Invertebrates. Ants and Bees."). Each summary is paragraph 1 of its chapter, one verse of kind `heading` (`I.1.1` to `VIII.1.1`), and is not split into sentences. The chapter text starts at paragraph 2.

**Footnotes.** Kropotkin numbers his notes afresh in each chapter. The transcription marks them as "(1)" in the text and prints them at the end of the chapter under "NOTES:". Each sits inside its chapter as `<chapter>.N<number>`, for example `I.N3` (Kropotkin's survey of the literature before Kessler), and the verse carrying the marker lists it under `footnotes`. The Introduction and the Conclusion have no notes. There are 310 notes and 309 markers; see the next paragraph.

**Two notes the transcription does not give.** Note 8 of chapter III and note 38 of chapter V are printed in the transcription as "None". `V.N38.1.1` has its marker in the text (`V.19.11`, the end of the paragraph on the guild tribunal). `III.N8.1.1` has no marker anywhere in chapter III. Both verses keep "None" as transcribed and carry `review: true`, so the ids exist when someone checks the 1902 printing and fills them in.

**Quotations set as blocks.** The book sets longer quotations apart from the text (Huxley at `I.6` and `I.8`, a traveller on the Dayaks at `III.38`, the Norse ideal of a man at `IV.20`). Each is a paragraph of its own here, as in the transcription.

**Typography.** Gutenberg's double hyphen for a dash ("--") is kept, as in GAS and AOE. There are no hyphens at line ends and no page numbers in this transcription.

## Repairs

Listed in `CORRECTIONS` in `ingest/build_verses.py`. None could be checked against a scan.

- `I.6.2`: Huxley's sentence "set to, fight hereby the strongest" corrected to "set to fight--whereby the strongest", as Huxley printed it in *The Nineteenth Century*, February 1888.
- `I.N3.1.2`: "Les facultes etales des animaux" corrected to "Les facultes mentales des animaux", the title of Houzeau's book.
- `IV.15.5`: "the territory was dottedall these" corrected to "was dotted--all these".
- `IV.N4.1.7`: "Severnyi Vestnil" corrected to "Severnyi Vestnik", the Russian review; `IV.N23.1.1` spells it correctly.
- `V.N40.1.1`: "pp, 45-46" corrected to "pp. 45-46".
- `C.11.7`: "mutual support not mutual struggle--has had the leading part" corrected to "mutual support--not mutual struggle--has had", restoring the first dash of the pair.

**Kept as printed.** These may be the book's own forms and are kept: compounds written as one word ("domeshaped", `II.17.5`; "whitetailed", `I.26.10`; "shellheaps", `III.9.4`; "craftguilds", `VI.1.1`; "motherbranch", `V.5.9`; "everworking", `VIII.18.1`); "F. oesulon" for the merlin, *Falco aesalon* (`I.27.13`); "the Lives and Coures" for the Livonians and Curonians (`IV.9.5`, `IV.N4.1.7`); "another.. One" with two points (`III.17`); British spellings such as "defence", "labour" and "mould". A modern draft spells them in today's way; the historical column keeps them.

## Sentence splitting

The shared splitter in `scripts/lib/segment.py` is used with local additions in the ingest. `scripts/lib` is unchanged.

- Abbreviations added for this work, almost all in the notes: first-name initials ("Ch. Dixon", `I.28.2`, `II.46.2`; "Max. Perty", "Alf. Moeller", "Eb. Bain", "Joh. Falke", "Fr. Seebohm", "Wilh. Arnold", "Dm. Bakradze"), titles ("Prof.", `P1902.16.3`; "Rev.", `V.N25.1.1`), months ("Feb.", "Aug.", "Sept."), "Col." (Colonel), "Nos.", "Pp.", "Cf.", "vols." and the shortened words of German and French citations ("Bd.", "Abth.", "Botan.", "Geol.", "Geogr.", "Histor.", "Bull.", "Afrik.").
- A lower-case Roman numeral is a volume number in the notes ("Brehm, iv. 567", `I.N19.1.1`), and so is "l.c." followed by a volume ("Buchenberger, l.c. Bd. ii. p. 510", `VII.N33.1.1`). The ingest never splits after one when a page, a part or a number of the cited work follows.
- Four places where the shared rules split inside a sentence are rejoined: "on 7s. 6d. a week" (`VIII.34.1`), "de France. 7th Letter." (`V.N10.1.1`), "3e edition. Paris, 1892." (`VII.N5.1.1`), "an Artisan. Coventry, 1893." (`VIII.N18.1.1`).
- Sentence ends the splitter cannot see, split by hand in `EN_BREAKS`: sixteen places where a number or "etc." ends a sentence, one in the text ("instead of 80.", `VI.36.4`) and fifteen in the notes.

The shared rule never splits inside an open parenthesis, so `III.30.9` (an anecdote of Veniaminoff's in four sentences, all inside brackets) and the closing bracket of `VII.N3.1.1` are single verses. A contributor who wants them split can do so with letter suffixes (see VERSIFICATION.md).

## Alignment

There is only one text column, so nothing is aligned. There are **2 review flags**, both for the missing notes (`III.N8.1.1`, `V.N38.1.1`). Checks made before the lock: every section has as many paragraphs as the transcription, the verses of each paragraph joined together give back the paragraph exactly, every footnote marker has its note and every note but `III.N8` its marker, no verse is punctuation only, and no footnote markers, page numbers or underscores are left in the text. A spelling check over the text found the repairs above. Twenty-six verses across the Introduction, the chapters, the summaries, the notes and the Conclusion were read against the source.

## Verse counts

| Section | Paragraphs (without heading and summary) | Notes | Verses |
|---|---|---|---|
| `P1902` | 19 | 0 | 82 |
| `I` | 36 | 22 | 280 |
| `II` | 49 | 40 | 438 |
| `III` | 44 | 46 | 486 |
| `IV` | 34 | 42 | 372 |
| `V` | 31 | 54 | 320 |
| `VI` | 36 | 41 | 375 |
| `VII` | 46 | 43 | 384 |
| `VIII` | 37 | 22 | 324 |
| `C` | 11 | 0 | 48 |
| total | 343 | 310 | 3109 |

## Raw file checksums (SHA-256)

From `sources/MANIFEST.yaml`:

```
c2640f9c77ac28808e593b9cd3b31c2370592977ecd74eb8e1a446e661896130  sources/raw/en/gutenberg_4341.txt
```
