# Sources

This file covers the parallel edition in `text/`. The reference material already in `sources/` (the PDF, DOCX and HTML files, and the background reading) was there before and is untouched.

What each column was built from, what was done to it, and what still needs checking. If you find an error, open an issue with the **Source or alignment error** form and cite the printed edition.

## German column

**Text:** *Karl Marx/Friedrich Engels, Werke* (MEW), Dietz Verlag, Berlin, via the mlwerke.de transcription as mirrored at `github.com/wertform/mlwerke.de`.

| Section | MEW | File | Notes |
|---|---|---|---|
| Manifesto, 0 and I-IV, notes N1-N8 | 4, pp. 459-493 | `me04_459.htm` | MEW prints the 1890 edition, the last Engels saw through the press |
| P1872 | 18, pp. 95-96 | `me18_095.htm` | Marx and Engels, original German |
| P1882 | 19, pp. 295-296 | `me19_295.htm` | from the German manuscript, which Engels believed lost in 1890 |
| P1883 | 21, pp. 3-4 | `me21_003.htm` | Engels, original German |
| P1888 | 21, pp. 352-359 | `me21_352.htm` | **translation** by the MEW editors from Engels's English |
| P1890 | 22, pp. 52-59 | `me22_052.htm` | Engels, original German; contains his back-translation of P1882 |
| P1892 | 22, pp. 282-283 | `me22_282.htm` | from Engels's German manuscript (published in Polish) |
| P1893 | 22, pp. 365-366 | `me22_365.htm` | **translation** by the MEW editors from Engels's French |

**Variants.** MEW's apparatus marks where the 1848, 1872 and 1883 German editions differ from the 1890 text, and where the 1888 English added or changed something. These are attached to verses as `de_variants`, with the edition, the other reading, and the first words of the base text where the variant starts. 73 variants in the Manifesto, one in P1888.

**Page numbers.** `mew_page` gives the MEW page on which the verse starts (or a range when it crosses a page).

**A corrupted copy, avoided.** A second GitHub mirror of the same MEW file (`MARX-EBOOKS/MLRAW`, `mewerke/me04/me04_459.htm`) differs from the corrected transcription in exactly one place: it drops *die Bedingung für* from II.81.1, turning "the free development of each is the condition for the free development of all" into "the free development of each is the free development of all". This repository uses the `wertform` copy, which matches the printed MEW. The two mirrors agree everywhere else, and all seven preface files are identical in both.

**Copyright.** The words of Marx and Engels are in the public domain. MEW's German translations of P1888, P1893 and of the notes Engels wrote in English for 1888 were made by the Institut für Marxismus-Leninismus around 1962-63 and may still be protected in Germany. They are included as reference text and marked in each file's `source_de`. They should be replaced by the project's own German renderings, or removed, if that becomes a problem.

## English column

**Text:** Samuel Moore's translation, edited and annotated by Engels, London (William Reeves) 1888, in the Marxists Internet Archive (MIA) transcription that Andy Blunden proofread against the 1888 edition in 2004. MIA releases its transcriptions under CC BY-SA. The source file is the MIA text already kept in this repository at `manifesto/the-communist-Manifesto-marx-engels-1848-convert.txt`, lines 52-363 for the text and 725-736 for the notes.

Two Project Gutenberg editions were compared and rejected as the base:

- Gutenberg #61 (1888 text) drops words, for example "population, centralised the means of production" from I.24.2.
- Gutenberg #31193 is the 1908 New York Labor News reprint, with American spelling and some wording differences. It is a useful second witness when proofreading.

**Prefaces other than 1888.** The English of P1872, P1882, P1883, P1890, P1892 and P1893 in MIA comes from the Progress Publishers translation (Moscow, 1969). Its copyright status is unverified. These are marked in each file's `source_en` and should eventually be replaced by the project's own translations from the German, which is the modern column's job anyway.

**MIA editorial insertions.** Square brackets in the English column are MIA or Progress insertions, not Engels: P1872.1.2 `[French]` `[in 1848]`, P1882.1.1 and P1890.3.1 `[a reference to the Free Russian Printing House]`, P1883.1.3 `[March 14, 1883]`, P1888.4.5 `[W. Bevan]`, P1890.1.1 `[the first German preface of 1883]`, P1890.18.10 `[from the General Rules of the International]`, I.49.1 `[lumpenproletariat]`, II.39.1 `[Aufhebung]`, III.59.7 `[or]`.

**Gaps and repairs.**

- MIA prints only a placeholder where Engels reprinted the 1882 preface inside P1890. Verses P1890.3.1 to P1890.9.1 carry the P1882 English, marked in `en_note`. Engels's 1890 back-translation differs slightly from the 1882 manuscript.
- MIA has no English for Engels's 1890 note on Lassalle (P1890.N1) or for the 1890 paragraph of note N8.
- P1893.2.6: MIA reads "national independence Therefore"; a full stop was restored.
- MIA end-note numbers glued to words ("sixties1", "Unite!5") were removed.

## Modern column

Seeded from *A Modern Manifesto* by Yusuf Talan Saunders (CC BY-SA 4.0), the modern-language rewrite of the 1888 English that this repository started with. It was the root `README.md` up to commit `3f59c73` and now lives, unchanged, at `manifesto/A-Modern-Manifesto.md`. It was aligned to the verses automatically and every seeded verse is marked `modern_status: seed`. It covers the preamble and Sections I-IV. The prefaces and notes have no modern text yet.

## Proofreading still to do

- German against a facsimile of the 1890 edition, and the variants against the 1848 first edition (23-page London pamphlet).
- English against a facsimile of the 1888 Reeves edition.
- The 40 verses flagged `review: true`.

## Columns worth adding later

- The 1848 first-edition German as its own column.
- Helen Macfarlane's 1850 English, the first translation (public domain).
- Engels's French text of P1893, or the 1893 Italian edition.

## Raw file checksums (SHA-256)

```
6df4115561276789e1210c423ae2d25fe8175ec8e4722ff6f87cce2dcdfaa4ad  sources/raw/de/me04_459.htm
4600435cfeb46557366560db673554867e8b6f1d7b6ca88ca126cbe2ec29e7df  sources/raw/de/me18_095.htm
2256348ef176736cdafdcb665a1296567907754a59b301a308b26df99b5a30d2  sources/raw/de/me19_295.htm
4f11a3b8fa5fa2dad59023c52afb2a9a8e0f9d7707d5c0e984d8aa3647bb8151  sources/raw/de/me21_003.htm
d30ab7aa348eae2ed366ca1ab931da0aa6c5fa1faa5804b5ec901d2996b0f7ed  sources/raw/de/me21_352.htm
bd8e98b25e2c051584035f0cafb1bd60f7cbfb139596cf1ec3ee41f318d0fd0c  sources/raw/de/me22_052.htm
4d85cdfd105df449cefc06840c470eb0d5d8d235f65b8a6eafa41d385b8c861c  sources/raw/de/me22_282.htm
b222e0b83d36dde883a65d3d6ca00365003dbc346c7de91a2a39ebe0cab4f999  sources/raw/de/me22_365.htm
d73b5a1660f0b8662ff1cc2da48cf4761294f5fe87ed045ab4ebcb46fd659ec1  sources/raw/en/mia_manifesto_1888.txt
60cd5e3383325c4b3a6d96c600e145a1c09a40b2db708eebb72783ed8e635134  manifesto/A-Modern-Manifesto.md
```
