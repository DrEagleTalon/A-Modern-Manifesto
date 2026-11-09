# Sources: God and the State (GAS)

## Original column (French): still to come

Bakunin wrote this text in French in 1871. By the usual account it is a piece of the unfinished manuscript of *L'Empire knouto-germanique et la Révolution sociale*. He left it without an ending. After his death Carlo Cafiero and Elisée Reclus published it in Geneva in 1882 as *Dieu et l'État*, with their own preface, and gave it its title. No public-domain French text is in this repository yet, and the library has no French sentence rules, so this is an **English-only build**: the `original` column is empty in every verse and the reader says so.

Until the French is added, the English sets the verse boundaries (`anchor_language: en` in every section file), the same exception VERSIFICATION.md makes for CM P1893 and that CB and AN use. When a public-domain French text is found on a reachable mirror, it goes into the `original` column and the verse ids stay as they are. Where the French divides a sentence differently, use `joined_to` and `align` as described in VERSIFICATION.md.

Do not confuse this text with the longer manuscript that Max Nettlau later published under the same French title in Bakunin's *Œuvres* (volume 1, 1895). The French to add here is the 1882 Cafiero and Reclus edition, the one Tucker translated.

## English column

**Text:** the English translation by Benjamin Tucker, first published in Boston in 1883, in the printing of the Mother Earth Publishing Association, New York. The printing is undated; its advertisements cite the April 1916 issue of *Mother Earth*, so it is from about 1916. It names no translator. The title page calls it the "First American Edition", which does not fit Tucker's Boston edition of 1883; the catalog and the usual bibliographies give the translation as Tucker's, and that should be checked against a scan of either printing. Transcribed by Fritz Ohrenschall, René Anderson Benitz and the Online Distributed Proofreading Team as Project Gutenberg ebook 36568 (2011), mirrored at `github.com/GITenberg/God-and-the-State_36568`.

**Which file.** The catalog fetch brought the ASCII file `36568.txt`, which drops every accent ("Elisee", "elite", "Caesars", "proletaires"). The same mirror has the ISO-8859-1 file `36568-8.txt`, which keeps them ("Elisée", "élite", "Cæsars", "prolétaires"). Apart from the Gutenberg header and the publisher's advertisements, the two files differ only in those characters. The ingest builds from `36568-8.txt`; the ASCII file stays in `sources/raw/` because the catalog fetch produces it. Gutenberg's HTML file (`36568-h/36568-h.htm`) was also compared word by word; it agrees with `36568-8.txt`. It comes from the same transcribers, so it is not an independent check.

**No page scans.** The mirror has the frontispiece portrait but no scans of the pages, so the repair below could not be checked against the printing. An archive.org copy of the Mother Earth printing or of Tucker's 1883 edition would settle it and the cruxes that depend on the printed wording.

**Rights.** Bakunin died in 1876; Cafiero and Reclus died before 1906. The French was published in 1882 and Tucker's translation in the United States in 1883; this printing followed there in about 1916. All are in the public domain in the United States (works published before 1931 are public domain there in 2026). Project Gutenberg's licence covers its trademark and header, which are not used here.

**Left out.** The Gutenberg header and transcriber's note, both title pages and the portrait are not versified. Nor are the publisher's advertisements after the footnotes (for *Mother Earth*, Emma Goldman's books and others). The row of asterisks that closes the footnotes is left out too.

## Sections and numbering

| Section | Contents |
|---|---|
| `P1882` | the editors' "Preface to the First French Edition", signed by Carlo Cafiero and Elisée Reclus |
| `0` | Bakunin's text, which has no numbered divisions |
| `0.N1` to `0.N11` | the footnotes, numbered as printed |

Paragraph 0 of `P1882` is its heading. The signature, "Carlo Cafiero. Elisée Reclus.", is one verse of kind `signature` (`P1882.7.1`). Paragraph 0 of `0` is the title, written "God and the State" (the book prints it in capitals).

**The footnotes.** They sit inside section `0`, as CB keeps its notes in the chapter they belong to. Each verse carrying a footnote marker lists the note under `footnotes`. Notes 5 and 6 are the editors', not Bakunin's: N5 says three pages of the manuscript are missing, and N6 guesses at the lost words. Both are attached to `0.121.4`, where the gap is. Note 4 is far longer than the rest (eight paragraphs, 60 verses): it starts from Mazzini's schools and turns into Bakunin's case on education, authority and public opinion. Note 1 mentions "the Appendix alluded to", which is not in this book (see cruxes.md).

**The asterisks.** The book divides Bakunin's text with rows of asterisks. They are not part of the verse address. They fall just before these verses:

`0.11.1`, `0.12.1`, `0.38.1`, `0.122.1` (after the gap at `0.121.4`), `0.162.1`, `0.166.1`

The first two frame a single paragraph, `0.11`, Bakunin's statement of the elements of human development. `sources/clean/en.json` records the asterisks too, by paragraph.

**Typography.** Gutenberg's underscores for italics are removed, as in SUS, CB and AN. Its double hyphen for a dash ("--") is kept. Where a line of the transcription begins with "--", the dash is joined to the word before it. The centred Latin line "Credo quod absurdum." is its own paragraph (`0.171.1`), as the book sets it. The gap marker "laws[5] ..." reads "laws..." once the footnote marker is lifted out (`0.121.4`).

## Repairs

Listed in `CORRECTIONS` in `ingest/build_verses.py`:

- `0.193.5`: "a meretorious and sincere conversion" corrected to "meritorious". Not checked against a scan (there is none on the mirror); it may be the printer's error rather than the transcribers'.

**Kept as printed.** These are the translation's own forms or may be, and are kept: "the walls of their cheese" (`P1882.5.2`, see cruxes.md), "that do the laws" (`0.121.4`), "Beyond those limits being the doctrinaire and governmental pretentions" (`0.133.7`, a sentence without a main verb), "breveted savants" (`0.137.1`), "curser" (`0.19.1`), "bourgeoise" as an English adjective (`0.94.8`, `0.97.4`), "doctrinairisme" left in French (`0.125.6`), "warmer-over" (`0.N11.1.1`), and "milliards" for thousands of millions (`0.6.4`, `0.114.7`, `0.132.5`). A modern draft spells and words them in today's way; the historical column keeps them.

## Sentence splitting

The shared splitter in `scripts/lib/segment.py` is used with local additions in the ingest. `scripts/lib` is unchanged.

- Two sentence ends the splitter misses: "the dictatorship of Bonaparte I." ends `0.179.6` (a regnal numeral), and "the revolution of 1789 and '93." ends `0.182.3` (a two-digit year).

Initials and titles stay inside their sentences: "J. J. Rousseau" (`0.50.2`, `0.178.4`, `0.179.5`), "P. L. Courier" (`0.184.5`), "M. Cousin" (`0.199.1`), "Mr. Stuart Mill" (`0.N2.1.1`), "Napoleon III." and "Gregory VII." where the sentence goes on. A colon does not end a verse, so the quotation that follows "His first commandment was this:" is its own paragraph (`0.152.1`) only because the book sets it that way.

## Alignment

There is only one text column, so nothing is aligned and there are **0 review flags**. Checks made before the lock: every section has as many paragraphs as the source (199 in `0` after the six rows of asterisks are taken out), the verses of each paragraph joined together give back the paragraph exactly, every footnote marker has its note, no verse is punctuation only, and no asterisks, page numbers, footnote markers or underscores are left in the text. Twenty verses across the preface, the body and the notes were read against the source.

## Verse counts

| Section | Paragraphs (without the heading) | Verses |
|---|---|---|
| `P1882` | 7 (with the signature) | 44 |
| `0` | 199 | 838 |
| `0.N1` to `0.N11` | 18 | 88 |
| total | 224 | 970 |

## Raw file checksums (SHA-256)

From `sources/MANIFEST.yaml`:

```
9f8aca8864ac783f89ebf19d99740779ea52433dee7e20532dcbdc739f0ea85d  sources/raw/en/gutenberg_36568.txt
9cd32118c44c291bb88c3645934976d5e0889f903175d528bfbd59a37185d1a1  sources/raw/en/gutenberg_36568-8.txt
```
