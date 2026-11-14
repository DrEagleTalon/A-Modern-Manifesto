# Sources: The Mass Strike, the Political Party and the Trade Unions (MS)

## German column

**Text.** Rosa Luxemburg, *Massenstreik, Partei und Gewerkschaften*, the first edition: "Im Auftrage des Vorstandes der sozialdemokratischen Landesorganisation Hamburgs und der Vorstände der sozialdemokratischen Vereine von Altona, Ottensen und Wandsbek", Hamburg: Erdmann Dubber, 1906, set in Fraktur. Luxemburg wrote it in Kuokkala, Finland, in the late summer of 1906, after her release from prison in Warsaw and before the party congress at Mannheim that September.

The base text is Project Gutenberg ebook 31614 (released 12 March 2010), produced by Odessa Paige Turner and the Online Distributed Proofreading Team from Google Print scans of the 1906 printing. The ISO-8859-1 file `31614.txt` is mirrored at `github.com/GITenberg/Massenstreik-Partei-und-Gewerkschaften_31614`. The mirror also has `31614-8.txt`, which is byte for byte the same file.

**Transcriber's note.** The transcription says obvious misprints were corrected, and that inconsistent capitals and spelling variants were left as printed. It marks spaced type with `_` and Antiqua type with `#`.

**Second copy.** No second transcription was reachable from the scheduled run (marxists.org and zeno.org are not mirrored for Luxemburg). The Gutenberg text was read on its own. A check against the 1906 scan, or against *Gesammelte Werke* vol. 2 (Dietz, Berlin 1972), would confirm the repairs below.

**Rights.** Luxemburg died in 1919. The pamphlet was published in 1906, and works published before 1931 are in the public domain in the United States. It is also out of copyright in every country with a term of life plus 70 years or less. Project Gutenberg's licence covers its trademark and header, which are not used here.

## No English column

Patrick Lavin's translation (*The Mass Strike, the Political Party and the Trade Unions*, Marxist Educational Society of Detroit, 1925) was published in the United States before 1931 and is in the public domain there, but no copy is on a reachable mirror. When one is found it can fill the `en` column without renumbering. Until then the modern draft is translated straight from the German, as in PC, CGP and GI.

## Sections and numbering

| Section | Contents |
|---|---|
| `0` | the title page: `0.0.1` the title, `0.1.1` the line saying for whom the pamphlet was written |
| `I` to `VIII` | Luxemburg's eight numbered parts. Paragraph 0 is the numeral as printed ("I.") |

The parts have no titles in the pamphlet. The files give them as "Part I" and so on in `title_en`.

**Footnotes.** Luxemburg numbers her four notes through the pamphlet. The transcription marks them "[1]" in the text and prints each after its paragraph as "[Fußnote 1: ...]". Each sits inside its part as `<part>.N<number>`, as in CB: `I.N1` (Engels, "Die Bakunisten an der Arbeit"), `III.N2` (strikes in the first two weeks of June 1906), `V.N3` (against Roland-Holst, with the report of the Petersburg trade union council) and `VIII.N4` (the Mainz resolution, in six paragraphs). The verse with the marker lists the note under `footnotes`: `I.2.8`, `III.25.21`, `V.3.5`, `VIII.6.1`.

**Left out.** The Gutenberg header and licence; "Von Rosa Luxemburg" and the imprint "Verlag von Erdmann Dubber in Hamburg 1906" on the title page; the printer's line at the end ("Druck: Hamburger Buchdruckerei und Verlagsanstalt Auer & Co. in Hamburg.").

**Normalised in the ingest.** The guillemets »x« become straight double quotes, as in the library's other German texts; nested quotations, which the transcription also sets in guillemets, become double quotes too (`V.N3.1.4`, `VIII.N4.2.1`). The marks for spaced type and Antiqua are dropped, as emphasis is dropped elsewhere. No-break spaces (in abbreviations such as "d. h." and in figures such as "200 000") become plain spaces. Gutenberg's double hyphen for a dash ("--") is kept, as in MA and GAS. There are no hyphens at line ends and no page numbers in this transcription, so verses carry no page field.

## Repairs

Listed in `CORRECTIONS` in `ingest/build_verses.py`. None could be checked against a scan.

- `II.1.2`: "z. b. durch Bömelburg" corrected to "z. B.", as everywhere else in the pamphlet.
- `III.4.11`: "1000 Arbeitet wurden verhaftet" corrected to "Arbeiter".
- `VII.10.4`: "der kapitialistischen Entwicklung" corrected to "kapitalistischen".

**Kept as printed.** "dass" seven times beside "daß" a hundred and eleven times (`I.2.4`, `I.2.5`, `II.1.7`, `II.1.8`, `III.4.4`, `III.N2.1.8`, `VIII.8.6`); the transcriber kept spelling variants, and only the scan can say whether these are the printer's. Also "Farçe" (`III.30.2`), "zu stande", "Gährung", "Apothekergehülfen", "Massacre", "Raisonnement" and "Renkontre", which are forms of the time. A modern draft spells in today's way; the original column keeps them.

## Sentence splitting

The shared splitter in `scripts/lib/segment.py` is used with local additions in the ingest. `scripts/lib` is unchanged.

- Abbreviations added for this work: "Fr. Engels" (`I.N1.1.1`), "Sächs. Arbeiterzeitung" (`II.4.3`), "za." for "zirka" (`III.4.6`, `III.4.11`, `III.6.4`), "Peter v. Struve" (`III.8.47`) and "&c." (`III.7.3`, `VIII.10.4`).
- Two places where the shared rules split inside a sentence are rejoined: the title "Die Bakunisten an der Arbeit. Internationales aus dem Volksstaat" (`I.N1.1.1`) and the points of suspension in "lebensfrohe ..... Gewerkschaften" (`III.22.18`). The shared clean-up closes the space before the points.
- Two sentence ends after "usw." that the splitter cannot see are split by hand: `III.17.7` / `III.17.8` and `VIII.8.8` / `VIII.8.9`.
- Luxemburg runs reports from several towns together in one paragraph, each opening with a dash ("... finden. -- In Jelissawetgrad beginnt ..."). The shared rules do not split before a double hyphen; this ingest does when a full stop, question mark, exclamation mark or closing quote comes before it and a capital after it. The dash stays at the head of the new verse (`I.2.5`, `III.8.8`, `III.8.11`, `III.8.24`, `III.8.37`, `III.8.41`, `III.8.42`, `III.24.3`, `VI.4.5`). Dashes inside a sentence are untouched.

The shared rule never splits inside an open parenthesis, so the citation "(S. "Neue Zeit" Nr. 33, 1906.)" is a verse of its own (`V.N3.1.2`) and "(im Jahre 1904. R. L.)" stays inside `V.N3.1.4`. Numbered demands ("1. Auszahlung der Löhne ...; 2. ...", `III.4.6`) stay in one verse; Luxemburg's numbered points in IV ("1. Es ist gänzlich verkehrt", `IV.4.1`) open their paragraphs.

## Alignment

There is only one text column, so nothing is aligned and there are **0 review flags**. Checks made before the lock: every part has as many paragraphs as the transcription; the verses of each paragraph joined together give back the paragraph; every footnote marker has its note and every note its marker; no verse is empty or punctuation only; no underscores, Antiqua marks, guillemets, brackets or page numbers are left in the text. A check for words one letter away from a commoner word in the same text found the repairs above. Twenty verses across the title page, all eight parts and the notes were read against the source.

## Verse counts

| Section | Paragraphs (without heading) | Notes | Verses |
|---|---|---|---|
| `0` | 2 | 0 | 2 |
| `I` | 5 | 1 | 39 |
| `II` | 8 | 0 | 42 |
| `III` | 30 | 1 | 276 |
| `IV` | 16 | 0 | 110 |
| `V` | 11 | 1 | 75 |
| `VI` | 9 | 0 | 62 |
| `VII` | 11 | 0 | 67 |
| `VIII` | 20 | 1 | 138 |
| total | 112 | 4 | 811 |

## Raw file checksum (SHA-256)

From `sources/MANIFEST.yaml`:

```
83121854be5b6082f8db1a67fc79d1ecbc84b91e978d2b419f1b3cef7fe5484a  sources/raw/de/gutenberg_31614.txt
```
