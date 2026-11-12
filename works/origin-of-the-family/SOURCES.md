# Sources: The Origin of the Family, Private Property and the State (OF)

## German column

**Text:** MEW 21, pp. 25-173 (Dietz, Berlin 1962), via the mlwerke.de transcription mirrored at `github.com/wertform/mlwerke.de` (`me21/me21_025.htm` to `me21_152.htm`; `me21_025.htm` is the contents page and holds no text). MEW prints the fourth edition (Stuttgart 1892), which Engels revised and enlarged in 1891, and records every substantial reading of the first edition (Hottingen-Zürich 1884) as a text variant. The variants are kept in each verse's `variants` field with edition `1884`.

**Prefaces.**

- `P1884`: Engels's preface to the first edition, MEW 21, pp. 27-29 (`me21_027.htm`). Its footnote on Morgan's *Ancient Society* is `P1884.N1`.
- `P1891`: Engels's preface to the fourth edition, MEW 22, pp. 211-222 (`me22_211.htm`), first printed in *Die Neue Zeit* in 1891. Its one variant gives the *Neue Zeit* reading. Its footnote on Morgan's life in Rochester is `P1891.N1`. MEW's separator line between the opening paragraphs and the history of the subject is left out.

`me22_211.htm` was added to the catalog sources in this run; the twelve other files are unchanged from the fetch of 8 November (same checksums).

**Sections.** `I` to `IX` are Engels's chapters. Paragraph 0 of each is the chapter title from MEW's contents page. In II the four family forms ("1. Die Blutsverwandtschaftsfamilie" and so on) open their paragraphs, as in MEW, and are not separate headings. The dash lines that divide II and IX into parts are left out.

**Footnotes.** Engels's notes are `<section>.N<n>` as in MEW: `P1884.N1`, `P1891.N1`, `II.N1` to `II.N3`, `IV.N1`, `VI.N1`, `VII.N1` and `VII.N2`, `VIII.N1` and `VIII.N2`, `IX.N1` to `IX.N5`. One variant (`T30` in II) sits inside `II.N2` and is attached there.

**Markup repairs** (in `_prepare` and `HTML_FIXES`, before parsing; the raw files are not touched):

- three pages (`me21_036.htm`, `me21_152.htm`, `me22_211.htm`) are 8-bit; their only bytes in the 0x80 to 0x9F range are the dash lines;
- `P1891.N1` is printed but not linked on the page; the link is added so the note is kept;
- `P1891.3.5` and `P1891.3.6`: the Romanian title and translator's name are garbled into control characters ("propnet\x01\x03\x01cii", "N\x01\x03dejde"); restored as "proprietăţii private şi a statului" and "Nădejde", and a FONT tag inside the page anchor for p. 212 removed;
- `II.67.3`, `II.67.5`: control characters in the Serbian words "domaćin" and "domaćica" restored; `VII.9.3`: "žena" restored;
- `IV.16.1`, `IV.23.4`: two page anchors (pp. 100, 102) with their bar outside the link, which left "[ 100]" in the text;
- `IV.35` to `IV.37`: the shared reader takes a paragraph that opens with 'In der "' for the start of MEW's apparatus and stopped there, which lost the last three paragraphs of chapter IV ("In der 'Ilias' ..."); a marker in front of the paragraph prevents that;
- words broken across a page anchor where the first half ends in an HTML entity ("m&ouml;g- |149| lich", `VIII.13.5`; "H&uuml;lsenfr&uuml;ch- ...", `IX.11.8`) are re-joined.

**Repairs to the text** (see `CORRECTIONS_DE` in `ingest/build_verses.py`):

- `P1891.17.1`: "daß. soviel" corrected to "daß, soviel".
- `P1891.18.1`: "verwickeitere" corrected to "verwickeltere".
- `II.5.6`: stray full stop removed in "Diese Veränderungen. sind".
- `II.16.2`: comma at the end of the paragraph corrected to a full stop ("auf diesen Punkt zurück.").
- `II.19.2`: "Volker" corrected to "Völker".
- `II.43.1`, `II.43.4`: "südamenkanischen", "nordamerinkanischen" corrected.
- `II.43.6`, `III.28.7`, `IX.15.9`: "ändern" corrected to "andern" (the other).
- `II.79.3`: "sondem" corrected to "sondern".
- `II.91.1`, `III.20.1`, `IV.1.2`, `IX.35.3`, `IX.N2.1.2`: "Fallen" corrected to "Fällen".
- `II.116.1`: "Einnuß" corrected to "Einfluß".
- `VII.6.3`: "hochschottischcn" corrected.
- `VII.13.1`: closing quotation mark restored after "Völuspâ".
- `IX.5.7`: "Rollstoffs" corrected to "Rohstoffs".
- `IX.19.5`: "fortgeschnttnere" corrected to "fortgeschrittnere".

These were found by reading and by a spelling check of words that occur once; none has been checked against a printed MEW 21, and a second mirror (`MARX-EBOOKS/MLRAW`) was not compared in this run. Spellings of Engels's time ("Hülfe", "gebornen", "nirgendswo") are left alone.

**Variant 1 in VII** has no link in the body of the page. Its reading (the 1884 edition lacks the text up to "Hier nur einige kurze Notizen") places it at the start of the chapter, so it is attached to `VII.1.1` (`UNLINKED_VARIANTS`). The edition label "l884" of `T30` in II is read as 1884.

**Paragraphs.** Where MEW sets a quotation as a block in the middle of a sentence, the paragraph that ends mid-sentence (or the one after it that starts in lower case) is joined to its neighbour, as in the SUS ingest. That joins 2 places in P1891 (`P1891.9.4`, `P1891.15.2`), 5 in II (`II.15.14`, `II.20.4`, `II.24.2`, `II.61.2`, `II.120.5`), 3 in IV (`IV.23.2` twice, `IV.29.6`), 1 in V (`V.3.5`), 1 in VI (`VI.23.1`) and 5 in VII (`VII.3.13`, `VII.6.4`, `VII.9.8`, `VII.14.1`, `VII.25.2`). Numbered list items are never joined. The result is 4 paragraphs in P1884, 33 in P1891, 21 in I, 120 in II, 46 in III, 37 in IV, 24 in V, 35 in VI, 29 in VII, 20 in VIII and 40 in IX, not counting the title.

**Copyright.** Engels died in 1895; his words are in the public domain.

## English column

**Text:** Ernest Untermann's translation, *The Origin of the Family, Private Property and the State* (Charles H. Kerr, Chicago; copyright 1902, 1908 printing), as transcribed by Project Gutenberg (ebook 33111, ASCII, accents stripped). Published in the United States in 1902, it is in the public domain there. Untermann translated the fourth edition, with both of Engels's prefaces. His own translator's preface (Chicago, August 1902) is not part of Engels's work and is left out. The Gutenberg text signs the 1884 preface "FREDERICK ENGELS."; MEW prints it unsigned, so that line is left out too.

**Untermann's notes.** The Gutenberg text numbers the footnotes 1 to 46 through the book. Fifteen are Untermann's versions of Engels's notes (his label "Author's note." is dropped) and fill the English column of the note verses; he does not translate `P1891.N1`. "Author's note to the fourth edition." in `VII.N1.1.1` is kept, since it renders Engels's "Zur vierten Auflage.". The other 31 are his own translator's notes or references that Engels gives in the text; they are kept as `en_note` on the verse where the marker stands ("Untermann's note [6]: ..." or "Untermann's footnote [2]: ..."). Every English note marker falls in the same verse as Engels's German one.

**Repairs** (see `CORRECTIONS_EN`): `VII.14.1`: "Broedbr" corrected to "Broedhr". The running title "THE ORIGIN OF THE FAMILY" that the Gutenberg text prints after the prefaces is dropped from the body and from note [5].

Untermann's English is free and not always accurate. The serious slip is "sexual ties" and "sex organization" for "Geschlechtsbande" and "Geschlechtsverband" (kinship, kin group), in `P1884.2.5` to `P1884.3.1`, `III.1.2` and `III.2.1`; see `glossary.yaml` and `cruxes.md`. He also gives a different publisher for Morgan's *Ancient Society* (`P1884.N1.1.3`) and prints the Old Norse lines in `VII.14.1` in another order. These are left as he wrote them.

## Alignment

All sections are aligned sentence by sentence across paragraph breaks (`flat=True`): Untermann has 5, 44, 21, 109, 50, 33, 26, 31, 29, 22 and 39 paragraphs against Engels's 4, 33, 21, 120, 46, 37, 24, 35, 29, 20 and 40 (P1884, P1891, I to IX). The cost function adds anchors on shared Latin-derived words (Gens/gens, Phratrie/phratry), as in the SUS and EB ingests, and on a short German-English word list for the book's recurring words (Frau/woman, Stamm/tribe, Ehe/marriage), each weighted by how rare it is in the section. A 1:4 bead is allowed, since Untermann often turns one German sentence into four. All of this is local to the ingest; nothing in `scripts/lib` was changed.

The sentence splitter is the shared one, with local repairs in `_split`: page markers after ordinals, no cut inside an open bracket, short bracketed references hung on the sentence they cite, Untermann's list "1. Wolf. 2. Bear. ..." kept as one sentence (`III.4.2`), and two titles kept whole (`NO_BREAK`: "etc. etc." in `P1891.4.6`, "Code Napoleon Art. 312" in `II.84.8`).

`REALIGN` redistributes Untermann's sentences over a run of verses where the length method slipped: `I.6.5` to `I.7.2`, `P1891.9.4` to `P1891.9.6`, `II.46.1` to `II.47.2`, `II.77.4` to `II.77.5`, `VI.18.4` to `VI.19.1` and `IX.9.10` to `IX.9.12`. The English text is only moved, never changed.

**Review flags:** 556. 513 are places where Untermann splits one of Engels's sentences into two or more (most of them 1:2), 29 where he joins German sentences, 13 groups of equal size (2:2) and one note on `P1891.9.5`, whose English also covers half of `P1891.9.6`. 12 of the flagged verses were regrouped by `REALIGN` and say so in `review_reason`.

## Verse counts

| Section | Verses | Of which notes |
|---|---|---|
| `P1884` | 28 | 5 |
| `P1891` | 147 | 4 |
| `I` | 73 | 0 |
| `II` | 668 | 19 |
| `III` | 195 | 0 |
| `IV` | 112 | 2 |
| `V` | 146 | 0 |
| `VI` | 130 | 3 |
| `VII` | 172 | 14 |
| `VIII` | 139 | 4 |
| `IX` | 285 | 14 |
| total | 2095 | 65 |

## Raw file checksums (SHA-256)

```
b8cb89ef0eec2d2e8f20bf319484efc7cf0e50fa07aa93fcc68ae7a7251330b3  sources/raw/de/me21_025.htm
ba12885a8ca0a0ada1d09294fd10adc07ab6e0acee58e3c2d1fe7985cbec5732  sources/raw/de/me21_027.htm
33f17c46a530df0e9b9d048e10e7b97ad3b549231ece786a30625f395ce31580  sources/raw/de/me21_030.htm
9e19813475628e606684e9ecf749b3fce472f1368b75afbee2e1c21584b009d2  sources/raw/de/me21_036.htm
e252b9b7ebfdf43a745e78bae991657857ca80d22d3f92bbb5a62b31bc9b0de0  sources/raw/de/me21_085.htm
17186fcf8ccf11bea130f7fb6ab98c6c419cc686211b130a3ae092aa0846a376  sources/raw/de/me21_098.htm
cfa2668357bd46e6361767ce629a4cbf322da71782c1b3d34e22e035ea5e3ae8  sources/raw/de/me21_107.htm
cd771259656a40f897975eefd5b544594a75a24c0701fc20c8f9d14dbe19bdbb  sources/raw/de/me21_117.htm
8f74ad052967fac6abec66b4a30285a8633c39e0a664afdddc8ffb3066700d3f  sources/raw/de/me21_127.htm
17ffcf7b73eb1a3efde8b705102e575d92f0024bc85b39ce6b986ccb0f442080  sources/raw/de/me21_141.htm
b43fd6d0dcd5d0fd393a12f97aca28a131ebf4b568c38fe50fcb1605c4bc9aa5  sources/raw/de/me21_152.htm
4701bf5ec08986a37b784165ffa8536dc55c7198d3483ff3d50a3baba029d58a  sources/raw/de/me22_211.htm
c53dab97224b8acacb09d44fcbc5a738f12640fabd5f6580d878f949f4f4eb60  sources/raw/en/gutenberg_33111.txt
```
