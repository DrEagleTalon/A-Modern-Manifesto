# Sources: Wage Labour and Capital (WLC)

## German column

**Text:** MEW 6, pp. 397-423 (Dietz, Berlin 1959), via the mlwerke.de transcription mirrored at `github.com/wertform/mlwerke.de` (`me06_397.htm`). MEW prints the text of Engels's 1891 pamphlet edition and records every reading of the original newspaper version (*Neue Rheinische Zeitung* nos. 264-267 and 269, 5-11 April 1849) in its apparatus. Those 109 readings are attached to the verses as `variants` with `editions: 1849 (NRZ)`. The `base_text` field shows the words around MEW's marker, with `‸` at the spot.

How to read a variant: `fehlt: X` means the 1849 text lacks X (Engels added it in 1891). `eingefügt: X` means the 1849 text had X, which Engels removed. A bare word means the 1849 text had that word in place of the 1891 word just before `‸` (for example *Arbeit* where 1891 has *Arbeitskraft*). `vorangestellt` / `nachgestellt` mark the newspaper's dateline and "to be continued" lines.

**Engels's 1891 introduction:** MEW 22, pp. 202-209 (`me22_202.htm`), Engels's original German.

**Sections.** Marx's text is divided into the five newspaper instalments, which is the only division the authors made. The section headings (`I.0.1` to `V.0.1`) are editorial. The single heading inside the text, "Was ist der Arbeitslohn? Wie wird er bestimmt?" (`I.7.1`), is Marx's.

**Second mirror check.** The `MARX-EBOOKS/MLRAW` copy of the same file matches word for word except variant {20}, which it gives as "fehlt: den man" against "fehlt: den" here. Check against the printed MEW.

**Copyright.** Marx's and Engels's words are in the public domain.

## English column

**Text:** Harriet E. Lothrop's translation, *Wage-Labor and Capital*, New York Labor News Company, 1902 (reprinted 1921), which includes Engels's introduction. Public domain in the United States. Used here in the Marxists Internet Archive edition (proofed by Alek Blain, 2006; MIA transcriptions are CC BY-SA), which is Lothrop's text with modernised spelling and with the money changed from dollars to shillings and pounds. A scan of the 1921 printing is at archive.org (`wagelaborcapital00marx_2`) and was used to check the repairs below.

**Lothrop's chapters.** Lothrop divided the text into nine chapters with headings of her own ("Preliminary", "By what is the price of a commodity determined?" and so on). They are not in the German. Each is kept as an `en_note` on the verse where the chapter begins, except chapter 2's heading, which translates Marx's heading at `I.7.1`.

**Removed MIA insertions.** MIA's square-bracket notes were removed from the English column: four in the introduction (on the Russian invasion of Hungary, the 1849 uprisings, a *Capital* reference, May Day 1891) and two glosses in chapter 1 ("[petty-bourgeois]", "[peasants]"). MIA's footnote to the introduction was also dropped. The full list is in `sources/clean/en.json`.

**Repairs from the 1902 text** (see `CORRECTIONS` in `ingest/build_verses.py`):

- `V.31.1` to `V.32.1`: MIA had lost a passage ("cannot at the same time be a big manufacturer. That the interest on capital decreases ... joining the ranks of the small manufacturers"). Restored from Lothrop.
- `V.30.2`: "grow every leaner" corrected to "grow ever leaner".
- `P1891.18.5`: "but not for a stipulated payment" corrected to "but for a stipulated payment".
- `P1891.13.4`: duplicated "were values were values" corrected.

**Known differences that are not errors.** Lothrop sometimes reorders or merges sentences, and her money amounts differ from Engels's (for example 2 Mark in the German, two shillings in MIA, dollars in 1902). The modern column follows the German. Converting to today's money belongs in the adaptation layer.

## Raw file checksums (SHA-256)

```
cf46e35436df3ed9fdc1ffd6062e2902829f05c739ad7808cfb702a08db364f0  sources/raw/de/me06_397.htm
73dbba3a63b18f9fa2a5fd01b8132b4f9253884b22de5ee422843174702ccb96  sources/raw/de/me22_202.htm
f577af4819ea179ff5c6df88f40bd682fd6978d58ce6111ced1702aca97017bb  sources/raw/en/mia_intro.html
e311f9f1910e51f5305ae512bb6e528563acfc11dc8ca4ff4f2ad6c715117979  sources/raw/en/mia_ch01.html
8e9b52cc43ea8890122a811770e8288466f1a62814ba003999f6082563471f78  sources/raw/en/mia_ch02.html
7db306c462ad760f80446b5b9ee146cbb548e94c6242e1c83d8c866b4cd32369  sources/raw/en/mia_ch03.html
d06bdfcc4f28ed8315d0fe3a12335cb9ae90a3fd0cb1407ca95f4bbd14e8df5c  sources/raw/en/mia_ch04.html
ac5dff47c79653564cb110f513b28d2c5979c1f9d0c769d4d64f8ae1fddf9b9a  sources/raw/en/mia_ch05.html
e3612d44b6a75253224214d8b786d0d3508f9fa7b4e1e244fec6308052108682  sources/raw/en/mia_ch06.html
5d580a5b43297e1df0516afc584706e3c1b7e6d99cad374f362bda58f8687a3e  sources/raw/en/mia_ch07.html
fd544082729aaf4ed83b1f2738f3ea9ce76d13049dab48585e014457e3431f15  sources/raw/en/mia_ch08.html
184a7b906e670e12fa4cd6c9849b07d50ed6c611676de18fb43bd0db7d4da649  sources/raw/en/mia_ch09.html
```
