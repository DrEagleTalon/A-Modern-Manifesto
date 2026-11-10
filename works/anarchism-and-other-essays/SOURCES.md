# Sources: Anarchism and Other Essays (AOE)

## Original column (English)

Emma Goldman wrote these essays in English and collected them in one volume, *Anarchism and Other Essays*, published by the Mother Earth Publishing Association, New York, in 1910, with a "Biographic Sketch" of Goldman by Hippolyte Havel. The `original` column holds that English text. There is no historical-translation column (`columns.en` is empty), as in VPP and CWF.

**Text:** Project Gutenberg ebook 2162 (released 2000, posted 2009), "Produced by Eva", the plain ASCII file `2162.txt`, mirrored at `github.com/GITenberg/Anarchism-and-Other-Essays_2162`. Gutenberg does not say which printing it transcribed. It has the twelve essays with Goldman's preface, and Havel's sketch signed "New York, December, 1910". Comparing against a scan of the 1910 printing on archive.org would settle the edition and the repairs below.

**Which file.** The mirror has only the ASCII text and an HTML file made from it (`2162-h/2162-h.htm`, "HTML version by Al Haines"). The HTML was checked: it has the same capitals for italics and no accents, so it adds nothing and was not fetched into `sources/raw/`.

**Capitals stand for italics.** The transcription sets every italic word in capitals. Most are titles and foreign words (`THE HOUSE OF BONDAGE`, `MOTHER EARTH`, `ATTENTATER`, `UEBERMENSCH`); the rest are words Goldman stresses (`the LIVING John Browns`, `B.3.7`; `HIS country`, `V.6.2`). They are kept as transcribed. Turning them back into lower case would mean guessing, word by word, which capitals were in the book and which mark italics. The draft writes them in normal case; see cruxes.md. Accents are missing for the same reason ("Elisee Reclus", "Coppee", "L'HUMANITE"); they are kept as transcribed too.

**Rights.** Goldman died in 1940 and Havel in 1950. The book was published in the United States in 1910, and works published there before 1931 are in the public domain in 2026. The poems and passages Goldman quotes were all published before 1931 as well. Project Gutenberg's licence covers its trademark and header, which are not used here.

**Left out.** The Gutenberg header and licence, the title page and the table of contents are not versified.

## Sections and numbering

| Section | Contents |
|---|---|
| `B` | Hippolyte Havel's biographic sketch, headed "Emma Goldman" in the book and "Biographic Sketch" in the contents |
| `P1910` | Goldman's Preface |
| `I` | Anarchism: What It Really Stands For |
| `II` | Minorities Versus Majorities |
| `III` | The Psychology of Political Violence |
| `IV` | Prisons: A Social Crime and Failure |
| `V` | Patriotism: A Menace to Liberty |
| `VI` | Francisco Ferrer and The Modern School |
| `VII` | The Hypocrisy of Puritanism |
| `VIII` | The Traffic in Women |
| `IX` | Woman Suffrage |
| `X` | The Tragedy of Woman's Emancipation |
| `XI` | Marriage and Love |
| `XII` | The Modern Drama: A Powerful Disseminator of Radical Thought |

Goldman did not number the essays. The Roman numerals follow the order of the book's contents and are the library's, as in CWF. Havel's sketch is `B` rather than a `P` section because it is a biography, not a preface to the essays, and both pieces date from 1910.

Paragraph 0 of each section is its heading, written in title case (the book sets headings in capitals). The heading of XII is the one over the essay ("The Modern Drama"); the contents call it "The Drama".

**Footnotes.** Goldman numbers her notes afresh in each essay and prints them at its end. Each sits inside its essay as `<essay>.N<number>`, for example `III.N1` (Goldman's gloss on "Attentater"), and the verse carrying the marker lists it under `footnotes`. Essays II, III, IV, VI, VII, VIII, IX and XII have notes, 34 in all. `XII.21.1` and `XII.35.1` each carry two.

**Quotations set as blocks.** The book sets epigraphs, verse and one letter apart from the text.

- Verse quotations keep their line breaks as " / ": Mackay's "Anarchy" (`I.2.1` to `I.2.5`), the American anthem (`III.27.1`), Wilde's *Ballad of Reading Gaol* (`IV.16.1`, `IV.56.1`) and the couplet at `VI.73.1`. Their verses follow the sentences, so a verse can start or end mid-line.
- The title of Mackay's poem is a heading of its own (`I.1.1`), as CB does with its subsections.
- Attributions, datelines and signatures are verses of kind `signature`, never split: `B.2.1` (Holyoake), `B.81.1` and `B.82.1` (Havel's signature and date), `P1910.14.1` (Goldman), `I.3.1` (Mackay), and Ferrer's letter, dated at `VI.45.1` and signed at `VI.49.1`.
- Where the block finishes Goldman's sentence ("lulled him to sleep with," `III.26.2`; "was engraved, significantly," `III.49.2`) the verse break falls inside the sentence. See cruxes.md.

**Typography.** Gutenberg's double hyphen for a dash ("--") is kept, as in GAS. There are no hyphens at line ends in this transcription and no page numbers.

## Repairs

Listed in `CORRECTIONS` in `ingest/build_verses.py`. None could be checked against a scan.

- `B.3.9`: "Wendel Phillips" corrected to "Wendell Phillips", the spelling in II (`II.13.1`, `II.13.5`).
- `B.79.4`: "Josiah Warrn" corrected to "Josiah Warren".
- `IV.15.1`: "THE BALLAD OF READING GOAL" corrected to "GAOL".
- `XII.78.5`: "Galworthy's JUSTICE" corrected to "Galsworthy's"; the name is spelled correctly elsewhere in the essay.

**Kept as printed.** These may be the book's own forms and are kept: "Banger" for the criminologist Willem Bonger, spelled the same way twice (`VIII.30.1`, `VIII.N5.1.1`); "Mr. Gutzen Burglum" for the sculptor Gutzon Borglum (`VII.1.1`, `VII.2.1`); "Madar Sol Dhingra" for Madan Lal Dhingra (`III.83.3`); "Miss Van Etton" (`B.40.7`); "Police Inspector Momento" (`III.17.4`); "Guttenberg" (`III.64.5`); "Pittsburg" (`B.32.3`); "bigotted" (`IX.21.1`); "fetich" (`IX.1.2`); British spellings such as "defence" and "mould". The Dr. Johnson line is misquoted in the book (`V.3.2`, see cruxes.md). A modern draft spells and words them in today's way; the historical column keeps them.

## Sentence splitting

The shared splitter in `scripts/lib/segment.py` is used with local additions in the ingest. `scripts/lib` is unchanged.

- Abbreviations added for this work: "Wm." (`B.40.7`), "Rev." (`B.41.4`), "Gen." (`V.33.4`, `V.35.1`), "Mlle." (`VI.30.1`, `VI.31.3`, `VI.33.1`), "Prof." (`VII.11.10`) and "Mfg." ("the Reliance-Sterling Mfg. Co.", `IV.49.2`, `IV.50.1`, `IV.50.2`, `IV.50.5`).
- Sentence ends the splitter cannot see, split by hand in `EN_BREAKS`: seven places where an abbreviation or a number ends a sentence (`III.13.8` and `III.13.9` end with "No." as an answer; `V.6.1`, `VIII.2.1`, `IX.35.1`, `V.11.1`, `V.12.4`).
- In the footnotes a book title stays in one verse with the author's name after it ("CRIME AND CRIMINALS. W. C. Owen.", `IV.N1.1.1`; also `VII.N1.1.1`, `IX.N1.1.1`, `IX.N5.1.1`).

Titles and initials stay inside their sentences ("Dr. Sanger", "Mrs. Alving", "St. Petersburg", "W. C. Owen", "U. S. mails"). "Co." ends a sentence where it ends one ("the Garson Co.", `B.18.1`) and is otherwise left alone because "Mfg." comes before it.

## Alignment

There is only one text column, so nothing is aligned and there are **0 review flags**. Checks made before the lock: every section has as many paragraphs as the transcription, the verses of each paragraph joined together give back the paragraph exactly, every footnote marker has its note and every note its marker, no verse is punctuation only, and no footnote markers, page numbers, asterisks or underscores are left in the text. A spelling check over the whole text found the repairs above. Thirty verses across the sketch, the preface, the essays and the notes were read against the source.

## Verse counts

| Section | Paragraphs (without the heading) | Notes | Verses |
|---|---|---|---|
| `B` | 82 | 0 | 490 |
| `P1910` | 14 | 0 | 62 |
| `I` | 57 | 0 | 234 |
| `II` | 23 | 1 | 127 |
| `III` | 92 | 4 | 347 |
| `IV` | 56 | 5 | 204 |
| `V` | 47 | 0 | 212 |
| `VI` | 73 | 5 | 273 |
| `VII` | 16 | 1 | 107 |
| `VIII` | 55 | 6 | 194 |
| `IX` | 37 | 5 | 211 |
| `X` | 24 | 0 | 122 |
| `XI` | 32 | 0 | 165 |
| `XII` | 98 | 7 | 402 |
| total | 706 | 34 | 3150 |

## Raw file checksums (SHA-256)

From `sources/MANIFEST.yaml`:

```
afc77c738938fcbfcd646c95ce78e0d528378cabe0decaad4f65cf1bc4a6f96f  sources/raw/en/gutenberg_2162.txt
```
