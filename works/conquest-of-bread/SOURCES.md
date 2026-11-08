# Sources: The Conquest of Bread (CB)

## Original column (French): still to come

Kropotkin wrote *La Conquête du pain* in French. It was published in Paris in 1892, mostly from articles he had written for *Le Révolté* and *La Révolte*. No public-domain French text is in this repository yet, and the library has no French sentence rules, so this is an **English-only build**: the `original` column is empty in every verse and the reader says so.

Until the French is added, the English sets the verse boundaries (`anchor_language: en` in every section file), the same exception VERSIFICATION.md makes for CM P1893. When a public-domain French text is found on a reachable mirror, it goes into the `original` column and the verse ids stay as they are. Where the French divides a sentence differently, use `joined_to` and `align` as described in VERSIFICATION.md. The French chapter titles replace the English ones in each file's `title_original` at the same time.

The 1913 preface (`P1913`) is dated Brighton, January 1913, and Kropotkin wrote it while living in England. Whether he wrote it in English or in French still needs checking. If it was written in English, its English is the original and its `original` column should take the same text.

## English column

**Text:** the anonymous English translation first published in London (Chapman and Hall) in 1906, with Kropotkin's preface of January 1913, in the Vanguard Press printing (New York 1926). The translator is not named in the book. Transcribed by Steven desJardins, Martin Pettit and the Online Distributed Proofreading Team as Project Gutenberg ebook 23428 (2007), mirrored at `github.com/GITenberg/The-Conquest-of-Bread_23428`.

**Which file.** The catalog fetch brought the ASCII file `23428.txt`, which writes the pound sign as "L" and drops every accent ("Considerant", "L50"). The same mirror has the ISO-8859-1 file `23428-8.txt`, which keeps them ("Considérant", "£50"). Apart from the encoding line in the Gutenberg header, the two files differ only in those characters. The ingest builds from `23428-8.txt`; the ASCII file stays in `sources/raw/` because the catalog fetch produces it.

**Page scans.** The mirror also has scans of every page of the Vanguard printing (`23428-page-images/`). The repair below was checked against them.

**Rights.** Kropotkin died in 1921. The French text dates from 1892 and the English translation from 1906, and the Vanguard printing was published in the United States in 1926. All are in the public domain in the United States (works published before 1931 are public domain there in 2026). Project Gutenberg's licence covers its trademark and header, which are not used here.

**Left out.** The Vanguard title page and its two publisher's blurbs ("The Man", "The Book") are not by Kropotkin and are not versified. Nor is the contents page. Its last entry, "Notes 213", refers to the footnotes, which are included.

## Sections and numbering

| Section | Contents |
|---|---|
| `P1913` | Kropotkin's preface, dated Brighton, January 1913 |
| `I` to `XVII` | the seventeen chapters, each followed by its footnotes (`<chapter>.N<n>`) |

Paragraph 0 of each chapter is the chapter heading, written as "Chapter I. Our Riches" (the book sets the number and title on two lines in capitals). Kropotkin's numbered subsections inside a chapter (I, II, III ...) are headings with a paragraph number of their own, as in CM III, so `I.1.1` is the subsection number "I" and `I.2.1` is the first sentence of the chapter.

The footnotes are numbered 1 to 13 across the book. Each one is kept with its number in the chapter it belongs to: `II.N1`, `IV.N2`, `V.N3`, `V.N4`, `VI.N5`, `IX.N6`, `IX.N7`, `X.N8`, `XII.N9`, `XVI.N10`, `XVII.N11`, `XVII.N12`, `XVII.N13`. The verse carrying each footnote marker lists it under `footnotes`. Note 10 is attached to the heading of chapter XVI (`XVI.0.1`), as in the book.

**The table in note 13.** The book sets the figures for Seine and Seine-et-Oise as a two-column table. Each row is one paragraph of the note, with the label and the figure joined by a colon ("Area in acres: 1,507,300"); the colon is the only thing added. The rule under "Extras" is left out. Rows run from `XVII.N13.2.1` to `XVII.N13.16.1`.

**Typography.** Gutenberg's underscores for italics are removed, as in SUS. Its double hyphen for a dash ("--") is kept as it is in the other works built from Gutenberg.

## Repairs

Listed in `CORRECTIONS` in `ingest/build_verses.py`:

- `P1913.13.3`: "coup d'êtat" corrected to "coup d'état" (scan of page xi).
- `IV.4.1`: "shrewed heads" corrected to "shrewd heads" (scan of page 34).

Both misprints are in the 1926 printing itself, not only in the transcription. On the same page 34 the printing has "middle classess", which Gutenberg already corrected to "classes".

**Kept as printed.** Some spellings look wrong but are what the book prints, checked against the scans: "conquerers" (`V.77.5`), "jewelery" (`XVII.37.1`), "pleasureable" (`XVII.47.7`), and "familystery" for Godin's Familistère (`X.20.4`). A modern draft spells them in today's way; the historical column keeps them.

## Sentence splitting

The shared splitter in `scripts/lib/segment.py` is used with local additions in the ingest. `scripts/lib` is unchanged.

- Abbreviations added for this work: "Wm.", "vols.", "Mlle.", "MM.", "Prof." (the bibliography in `XVII.N12` needs "Wm. Fream").
- Shillings and pence stay together: "1s. 8d." and "2s. 6d." are one sum, not a sentence end (for example `II.41.1` and `XVII.75.3`).
- One sentence end the splitter misses because "No." is also an abbreviation: "Technical skill of the worker?--No." (`XVI.22.6`).

Quoted questions inside a sentence are split the usual way, so `VI.19.1` is `"But how?` and `VI.19.2` is `How can it be done?" you ask us.`

## Alignment

There is only one text column, so nothing is aligned and there are **0 review flags**. Checks made before the lock: every section has as many paragraphs as the source, every footnote marker has its note in the same chapter, no verse is punctuation only, and no page numbers or footnote markers are left in the text.

## Verse counts

| Section | Verses | Of which notes |
|---|---|---|
| `P1913` | 77 | 0 |
| `I` | 138 | 0 |
| `II` | 134 | 1 |
| `III` | 117 | 0 |
| `IV` | 186 | 1 |
| `V` | 336 | 5 |
| `VI` | 138 | 1 |
| `VII` | 32 | 0 |
| `VIII` | 77 | 0 |
| `IX` | 186 | 2 |
| `X` | 132 | 6 |
| `XI` | 211 | 0 |
| `XII` | 213 | 2 |
| `XIII` | 209 | 0 |
| `XIV` | 95 | 0 |
| `XV` | 41 | 0 |
| `XVI` | 146 | 1 |
| `XVII` | 302 | 32 |
| total | 2770 | 51 |

## Raw file checksums (SHA-256)

From `sources/MANIFEST.yaml`:

```
e76d17c1cdbe37a8c3bdb9e924016c1964fb97767fb5e3445521ab0f7e34e214  sources/raw/en/gutenberg_23428.txt
0ec40b2bc77e16b36caf80c37c0e6c2591a9c096629f26f4a2bd21a39917f137  sources/raw/en/gutenberg_23428-8.txt
```
