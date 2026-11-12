# Sources: Critique of the Gotha Programme (CGP)

## German column

**Text.** Marx's covering letter to Wilhelm Bracke (5 May 1875) and his marginal notes on the draft programme of the German Workers' Party, MEW 19, pp. 13-32 (Dietz, Berlin 1962). MEW prints Marx's manuscript. Where the first printing (Die Neue Zeit, 1891) reads differently, MEW gives the 1891 reading as a variant; where Engels left words out in 1891 and put dots in their place, MEW sets Marx's words in angle brackets `< >`.

The base text is the zeno.org transcription of MEW 19, mirrored by MARX-EBOOKS at `github.com/MARX-EBOOKS/marx-ebooks.github.io` (`docs/MEW-ZENO/19/ME19-013.html` for the letter, `ME19-015.html` for the notes).

**Why not mlwerke.de.** The catalog first listed the mlwerke.de page (`me19/me19_013.htm` in `github.com/wertform/mlwerke.de`). Whoever converted that page read MEW's angle brackets as HTML tags. Nine of the twelve bracketed passages became tags, with their words sorted alphabetically into tag attributes, and text that followed some of them was swallowed too: all or part of I.4, I.14, I.64, IV.6, IV.13, IV.20 and IV.26 here, besides several quotations from the draft. A few passages were later typed back in by hand, with slips ("anbehaltenem", "fr" for "für"). The page cannot be repaired from itself, so it is kept as a collation copy only.

**Engels's foreword** (`P1891`), MEW 22, pp. 90-91, from the mlwerke.de page `me22/me22_090.htm`, which has no angle brackets and is sound. Engels wrote it for the first printing in Die Neue Zeit (9. Jg., 1. Bd., Nr. 18, 1890-1891), dated London, 6 January 1891.

**Collation.** The zeno.org text was compared word by word with the mlwerke.de copy, and where that copy is damaged, with a third transcription in the same mirror (`MEW/19/ME19-013.html` and `ME19-015.html`), which follows a different edition and modern spelling and so only helps with plain slips. Repairs (see `CORRECTIONS` in `ingest/build_verses.py`), each backed by the mlwerke.de copy:

- `B.5.1`: "von hier auslenken" corrected to "von hier aus lenken".
- `I.13.1`: "von den Verfechtern" corrected to "von den Vorfechtern". The 1891 variant on the same word reads "Verfechtern", so the manuscript reading cannot be the same.
- `I.54.10`: "diese Mißstände zu vermelden" corrected to "zu vermeiden".
- `I.56.1`: "jeder nach seinen Fähigkeiten" corrected to "Jeder" (the third transcription agrees).
- `I.57.1`: "Ich bin weltläufiger" corrected to "weitläufiger".
- `I.64.1`: "gegen über Feudalen" corrected to "gegenüber" (the mlwerke.de copy lacks this paragraph; the third transcription has "gegenüber").
- `III.2.1`: "das Heilsmittel des Propheten" corrected to "Heilmittel".
- `IV.17.1`: a missing space restored in "die Worte: "Die".

**Readings left as in the base text.** Where the two MEW transcriptions differ and neither is a plain slip, the zeno.org reading stands. The mlwerke.de copy reads: "Doch es war" (`B.3.4`), "sorgsam" for "sorgsamst" (`B.5.1`), "Aktionen" for "Aktion" (`B.7.2`), "Schlußlieferung ... des Kapitals" (`B.10.1`), "der Mensch ist ein Wilder" (`I.10.3`), "In dem Maße" (`I.18.1`), "In der Tat ist aber" (`I.20.1`), "übernommen" for "überkommen" (`I.59.5`) and "bei der Abfassung" (`II.8.1`). A check against a printed MEW 19 would settle them; `cruxes.md` lists the two that change the sense.

**Variants.** The seventeen 1891 readings are `variants` entries `T1` to `T17`, numbered as the zeno.org page numbers them (A1 to A17). The mlwerke.de copy has fifteen, numbered 1 to 15: it lacks A1 (`I.3.5`) and A4 (`I.13.2`).

**Page numbers.** zeno.org's page anchors mark where a page ends; an anchor at the head of a section names the page the section starts on. The ingest turns both into page starts. The start of page 25 (`II.3.1`, "ehernes |25| Lohngesetz") comes from the mlwerke.de copy. The starts of pages 16, 27 and 28 are marked in neither copy, so verses on page 16 carry 15, the end of III carries 26 and the first part of IV carries 27. MEW's editorial note references ("(3)", "(5)") are not in the zeno.org text and are not added.

**Normalised in the ingest:** »« and „“ become straight double quotes, as in the library's other MEW texts; MEW's angle brackets (‹ › on zeno.org) become `< >`, as on mlwerke.de and in EB; dashes become " - ". Emphasis is dropped, as elsewhere. MEW's own bracketed insertions "[auf]" (`III.7.1`) and "[und]" (`IV.21.3`) and the editorial titles "[Brief an Wilhelm Bracke]", "[IV]" and "[Vorwort zu ...]" are kept as printed.

**Copyright.** Marx's and Engels's words are in the public domain.

## No English column

No public-domain English translation is on a reachable mirror yet. English printings made before 1931 would be public domain in the United States and could fill the `en` column later without renumbering; the later standard translations are not used. Until then the modern draft is translated straight from the German.

## Sections

| Section | Contents | File |
|---|---|---|
| `P1891` | Engels's foreword to the first printing | `text/00-foreword/1891.yaml` |
| `B` | Marx's letter to Bracke, 5 May 1875 | `text/01-letter/bracke.yaml` |
| `I` to `IV` | the marginal notes, by Marx's numerals (MEW prints the fourth as "[IV]") | `text/02-marginal-notes/` |

Paragraph 0 of each section is its heading. In I it holds two headings: the title of the notes (`I.0.1`) and the numeral (`I.0.2`). The paragraphs of the Gotha draft that Marx quotes before each comment are ordinary verses (`I.1.1`, `I.21.1`, `II.1.1`, `IV.19.1` and so on). Datelines and closings are `signature` verses.

## Sentences

The shared splitter, with rules kept local to this ingest (`_split`): "sog." is an abbreviation; a sentence may end just before or inside an angle-bracket passage (`B.8.4` to `B.8.6`); "etc." ends a sentence when a capital follows, except in "die materiellen etc. Bedingungen" (`I.19.2`); a quoted lower-case answer stays with its question (`I.61.2`); a page marker between two sentences moves to the second. Nothing in `scripts/lib` was changed.

**Review flags:** 0. Every section has one column, so nothing is aligned.

## Verse counts

| Section | Paragraphs | Verses |
|---|---|---|
| P1891 | 8 | 17 |
| B | 14 | 30 |
| I | 77 | 152 |
| II | 10 | 23 |
| III | 8 | 17 |
| IV | 44 | 87 |
| **Total** | 161 | **326** |

The zeno.org pages have 14 and 140 text blocks; with the two headings of I sharing paragraph 0 that gives the 14 and 139 paragraphs above.

## Raw file checksums (SHA-256)

From `sources/MANIFEST.yaml`, fetched 2026-11-12:

```
f4051353292b2d66e483810644def357d10316932b308975ff723cf117556414  sources/raw/de/ME19-013.html   (base text, letter)
c8daeb073286da4e853ac3e127db92bc41795652585e39f1b0e9c8d0caeaeb11  sources/raw/de/ME19-015.html   (base text, notes)
9d4ace1581c476b4d458b1d904571aa8a711105beaaf23d78d433d0501ae82f9  sources/raw/de/me19_013.htm    (collation copy)
2cb745202937c99cdbcaa73ed41915c683860ff4a86f62744862dae59af31bbf  sources/raw/de/me22_090.htm    (foreword)
```

The third transcription used for collation (`MEW/19/ME19-013.html`, `MEW/19/ME19-015.html` in the MARX-EBOOKS mirror) is not stored here.
