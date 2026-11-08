# Modern Classics Library

An open, crowdsourced effort to make the classic texts of the socialist, communist and anarchist movements readable by working people today, without changing what the authors actually said.

The library has two layers:

1. **Translations** (`works/`). Every sentence of the original is a numbered verse. Beside it sit a historical English translation and a modern English draft, plus notes. The modern draft is faithful: plain words, same argument.
2. **Adaptations** (`adaptations/`). Short pamphlets for today ("Who Profits From Your Work?") that use modern examples, modern money and modern workplaces. They say openly that they adapt, and they cite the verses they draw on, so any reader can check the original.

## Works in the library

| Work | Cite as | Original | Historical English | State |
|---|---|---|---|---|
| [Manifesto of the Communist Party](works/communist-manifesto) (1848), with all seven prefaces | `CM I.12.3` | German, MEW (1890 text) | Moore and Engels, 1888 | 730 verses; modern draft seeded from *A Modern Manifesto* |
| [Wage Labour and Capital](works/wage-labour-and-capital) (1849), with Engels's 1891 introduction | `WLC II.4.2` | German, MEW (1891 text, 1849 readings as variants) | Lothrop, 1902 | 565 verses; modern draft not started |

The queue of works and the copyright status of each is in [docs/roadmap.md](docs/roadmap.md). Live progress per work is in `dist/README.md`.

## What a verse looks like

`WLC I.13.1` (instalment I, paragraph 13, sentence 1):

| | |
|---|---|
| **German (1891)** | Die Arbeitskraft ist also eine Ware, die ihr Besitzer, der Lohnarbeiter, an das Kapital verkauft. |
| **1849 reading** | *Arbeit* instead of *Arbeitskraft* (Engels changed it in 1891) |
| **English 1902** | Consequently, labour-power is a commodity which its possessor, the wage-worker, sells to the capitalist. |
| **Modern draft** | *(yours to write)* |

## How contributing works

You only ever edit YAML files in a work's `text/` folder (plus its `glossary.yaml`). The scripts do the rest:

- `scripts/validate.py` checks every change: verse numbers frozen, statuses valid, glossary and adaptation citations pointing at real verses.
- `scripts/build.py` regenerates everything in `dist/`: per-work CSV, Excel workbook and Markdown tables, and the HTML reader for the whole library.
- When a change is merged to `main`, GitHub Actions rebuilds `dist/`, commits it, and publishes the reader to GitHub Pages. Nobody edits `dist/` by hand.

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Numbering rules: [VERSIFICATION.md](VERSIFICATION.md). House style: [docs/translation-principles.md](docs/translation-principles.md). Adding a new work: [docs/adding-a-work.md](docs/adding-a-work.md).

## Repository layout

```
works/<work>/              one folder per work
  work.yaml                title, citation prefix, column labels, status
  text/                    master verse files (this is what contributors edit)
  glossary.yaml            how recurring terms are rendered in this work
  cruxes.md                hard passages, good first Discussions
  SOURCES.md               where every column came from, licences, repairs
  verse-ids.lock           every verse id ever issued; ids never change
  sources/                 the exact raw files the text was built from
  ingest/                  the one-time script that created the numbering
adaptations/               modern pamphlets, each citing the verses it uses
scripts/                   validate.py, build.py, reader template, shared lib/
dist/                      generated reading copies (do not edit)
docs/                      principles, roadmap, how to add a work
manifesto/                 the original A Modern Manifesto rewrite and its source text
sources/                   the project's reference library from before the restructure
```

## Prior work

Hal Draper's *The Adventures of the Communist Manifesto* (1994) set the 1848 German, the 1850 and 1888 English and his own translation side by side. This library does that kind of work in the open, at sentence level, across many works, with the arguments kept beside the text.

## License

Translations, notes, glossaries, adaptations and documentation: [CC BY-SA 4.0](LICENSE). Scripts: MIT ([LICENSE-CODE](LICENSE-CODE)). The status of every source text is in the work's SOURCES.md.
