# Sources: Anarchy (AN)

## Original column (Italian): still to come

Malatesta wrote *L'Anarchia* in Italian; the catalog dates it to 1891. No public-domain Italian text is in this repository yet, and the library has no Italian sentence rules, so this is an **English-only build**: the `original` column is empty in every verse and the reader says so.

Until the Italian is added, the English sets the verse boundaries (`anchor_language: en` in every section file), the same exception VERSIFICATION.md makes for CM P1893 and that CB uses for its French. When a public-domain Italian text is found on a reachable mirror, it goes into the `original` column and the verse ids stay as they are. Where the Italian divides a sentence differently, use `joined_to` and `align` as described in VERSIFICATION.md. Which Italian edition to use (the first pamphlet or a later one Malatesta revised) is still to be decided, and the choice should be written here.

## English column

**Text:** the anonymous English translation as printed by the Free Society Library in 1900 (the title page reads "Published by the Free Society Library in 1900"). The translator is not named. Transcribed by Vineshen Pillay as Project Gutenberg ebook 40365 (2012), mirrored at `github.com/GITenberg/Anarchy_40365`. The ingest builds from the ASCII file `40365.txt`.

**Second copy.** The same mirror has Gutenberg's HTML file (`40365-h/40365-h.htm`). Its words agree with the text file throughout. It comes from the same transcriber, so it is not an independent check.

**No page scans.** Unlike CB, the mirror has no scans of the printing, so the repairs below could not be checked against the page. An archive.org copy of the 1900 printing, or of the earlier English printings, would settle them and the cruxes that depend on the printed wording.

**Rights.** Malatesta died in 1932. The Italian dates from 1891, and this English printing was published in the United States in 1900. Both are in the public domain in the United States (works published before 1931 are public domain there in 2026). Project Gutenberg's licence covers its trademark and header, which are not used here.

**Left out.** The title page (title, author and the publisher's line) and Gutenberg's transcriber's note are not versified. The book has no footnotes.

## Sections and numbering

The book prints the title "ANARCHY." and then runs as one essay, divided by rules. It numbers only two parts, "I." and "II.", and both come late. The sections follow that:

- `0` is the title and everything before "I.": what the word Anarchy means, and what government is and how it arose. Paragraph 0 is the title, written "Anarchy".
- `I` is the part the book numbers I: the instinct of solidarity, and the society of free men that would replace government.
- `II` is the part the book numbers II: the usual objections answered, and the way to Anarchy. Paragraph 0 of `I` and `II` is the number the book prints, without its full stop.

**The rules.** A long rule ends each of the four parts of the book. Three of them fall at a section break or at the end; the other falls inside section `0`, between the discussion of the word and the discussion of government. Short rules mark smaller turns inside `I` and `II`. Neither kind is part of the verse address. They fall just before these verses:

| Rule | Before |
|---|---|
| long | `0.20.1` ("We have said that Anarchy is society without government.") |
| short | `I.28.1` |
| short | `II.11.1`, `II.19.1`, `II.28.1`, `II.33.1`, `II.35.1`, `II.43.1`, `II.54.1`, `II.56.1`, `II.72.1` |

`sources/clean/en.json` records them too, by paragraph.

**Typography.** Gutenberg's underscores for italics are removed, as in SUS and CB. Its double hyphen for a dash ("--") is kept. Where a line of the transcription begins with "--", the dash is joined to the word before it, so `0.7.1` reads "differently--and might try to propagate their opinions--to keep silence".

## Repairs

Listed in `CORRECTIONS` in `ingest/build_verses.py`:

- `II.2.2`: "over man, there, would be no reason" corrected to "over man, there would be no reason". A stray comma, either in the transcription or in the printing. Not checked against a scan (there is none on the mirror).
- `II.70.8`: "which among them is the must superior" corrected to "the most superior". Not checked against a scan either.

**Kept as printed.** "proprietory" (`0.38.2`, `0.39.3`, `0.44.1`, `0.46.1`, against "proprietary" in `II.49.10`), "Appenines" (`I.25.2`), "partizans" (`II.34.2`), and "if it do not succeed" (`II.13.4`) are the translation's own forms and are kept. So is the comma in "It would be to destroy, every social bond" (`II.10.2`), which may be the printer's but changes nothing in the sense. A modern draft spells them in today's way; the historical column keeps them. `II.70.3` ends with a full stop where a question mark is meant ("And how shall we recognize their superiority."); it is kept, since the sentence reads correctly either way.

## Sentence splitting

The shared splitter in `scripts/lib/segment.py` is used with one local addition in the ingest. `scripts/lib` is unchanged.

- One sentence end the splitter misses because "etc." is also an abbreviation: "technical direction, administration, etc." ends `II.31.1`, and `II.31.2` begins "But the authoritarians".

"i. e." (`0.38.2`) and "M.P." (`0.37.2`) stay inside their sentences. Quotations from Bakunin, Kropotkin and Sismondi are split into sentences like the rest of the text; a quotation that runs over several paragraphs keeps its opening and closing marks where the book puts them (`I.14.1` to `I.15.4`, `II.63.1` to `II.64.3`).

## Alignment

There is only one text column, so nothing is aligned and there are **0 review flags**. Checks made before the lock: every section has as many paragraphs as the source, the verses of each paragraph joined together give back the paragraph exactly, no verse is punctuation only, and no rules, page numbers or underscores are left in the text.

## Verse counts

| Section | Paragraphs (without the heading) | Verses |
|---|---|---|
| `0` | 50 | 153 |
| `I` | 34 | 82 |
| `II` | 77 | 298 |
| total | 161 | 533 |

## Raw file checksums (SHA-256)

From `sources/MANIFEST.yaml`:

```
c1e699edccb681918cf0c2d260c07a0f4b7860f9a2d71caa16b6cb9c84b38595  sources/raw/en/gutenberg_40365.txt
```
