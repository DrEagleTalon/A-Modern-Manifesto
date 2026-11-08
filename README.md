# A Modern Scholarly Translation of the Communist Manifesto

An open, verse-numbered parallel edition of the *Manifest der Kommunistischen Partei* (Marx and Engels, 1848) with every preface Marx and Engels wrote for it. Each sentence of the German original is a numbered verse. Beside it sit the 1888 English translation that Engels edited, a modern English draft, and notes. Anyone can propose a better rendering, argue about what a passage means, or fix a source error, and every one of those conversations points back to a verse number.

The goal is a translation that a reader today can pick up and understand, without losing what the authors actually wrote. Where the world has changed since 1848, or where readers disagree about what a line means, that goes in the notes and in recorded readings. The text itself stays faithful.

## What a verse looks like

`CM I.23.2` (Section I, paragraph 23, sentence 2):

| | |
|---|---|
| **German** | Sie hat enorme Städte geschaffen, sie hat die Zahl der städtischen Bevölkerung gegenüber der ländlichen in hohem Grade vermehrt und so einen bedeutenden Teil der Bevölkerung dem Idiotismus des Landlebens entrissen. |
| **English 1888** | It has created enormous cities, has greatly increased the urban population as compared with the rural, and has thus rescued a considerable part of the population from the idiocy of rural life. |
| **Modern draft** | It has built enormous urban centers, hugely increased the urban population relative to the rural one, and pulled a large part of the population out of the isolation of rural life. |
| **Notes** | *Idiotismus* is not "idiocy". See the glossary entry and Hal Draper's argument for "isolation". |

## What is in the repository

```
text/                      master files, one YAML file per section (this is what you edit)
  00-prefaces/             1872, 1882, 1883, 1888, 1890, 1892, 1893
  01-manifesto/            0 preamble, I-IV, and Engels's footnotes
  verse-ids.lock           every verse id ever issued; ids are frozen
glossary/terms.yaml        key terms, how Moore rendered them, open decisions
docs/cruxes.md             contested passages, with verse numbers, to start discussions from
dist/                      generated: CSV, Excel workbook, Markdown tables, HTML reader
scripts/                   validate.py, build.py, and the one-time ingest pipeline
sources/raw, sources/clean the exact files the parallel text was built from (see SOURCES.md)
sources/                   reference library kept from the start of the project
manifesto/                 the original modern rewrite (A-Modern-Manifesto.md, formerly this README) and the MIA source text
```

Open `dist/site/index.html` in a browser for the parallel reader, or `dist/manifesto-parallel.xlsx` if you prefer a spreadsheet. Both are rebuilt from `text/` by `python scripts/build.py`.

## Current state (v0.1)

| | |
|---|---|
| Verses | 730 (7 prefaces, preamble, Sections I-IV, Engels's notes) |
| German | complete, MEW text of the 1890 edition, with 1848/1872/1883/1888 variants attached to verses |
| English 1888 | complete for the Manifesto and the 1888 preface; other prefaces carry a later reference translation (see SOURCES.md) |
| Modern draft | 446 verses seeded from the original rewrite in `manifesto/A-Modern-Manifesto.md`, a paraphrase of the 1888 English. None of it has been checked against the German yet, so all of it is marked `seed` |
| Alignment checks | 40 verses flagged `review: true` where the German and English sentence boundaries do not line up one to one |

The prefaces have no modern draft yet. That is the easiest place for a new contributor to start, since the passages are short and self-contained.

## How to help

Read [CONTRIBUTING.md](CONTRIBUTING.md). In short:

- **Translate**: pick verses, write or improve the `modern` field working from the German, open a pull request with the verse numbers in the title.
- **Debate**: open a Discussion titled with the verse number, for example `[II.66.1] "in the hands of the State"`. When a debate produces distinct readings, they get recorded on the verse.
- **Check**: work through the verses flagged `review: true`, or proofread the German and English against facsimiles of the 1848 and 1888 editions.

The house rules for translation choices are in [docs/translation-principles.md](docs/translation-principles.md). The numbering rules are in [VERSIFICATION.md](VERSIFICATION.md).

## Citing

Cite verses as `CM I.12.3` for the Manifesto, `CM P1872.2.6` for a preface, `CM N2.1.3` for one of Engels's notes. A verse number always points at the same German sentence, in every release.

## Prior work

Hal Draper's *The Adventures of the Communist Manifesto* (1994, reissued by Haymarket 2020) set the 1848 German, Helen Macfarlane's 1850 English, the 1888 English and his own new translation side by side, paragraph by paragraph. This project does the same kind of work in the open, at sentence level, with the arguments kept alongside the text.

## License

Translations, notes, glossary and documentation: [CC BY-SA 4.0](LICENSE). Scripts: MIT ([LICENSE-CODE](LICENSE-CODE)). The German and the 1888 English are in the public domain; see [SOURCES.md](SOURCES.md) for the status of each transcription and of the later preface translations.
