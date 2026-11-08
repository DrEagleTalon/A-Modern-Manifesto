# Left Classics

**The socialist, communist and anarchist classics, verse by verse, in plain English.**

Marx, Engels, Lenin, Luxemburg, Kropotkin, Malatesta and the rest, made readable for working people today without changing what they said, and open to every tradition on the left to explain, translate and argue about them in the open.

The library has four layers, kept apart so the original is never weighed down:

1. **Translations** (`works/`). Every sentence of the original is a numbered verse. Beside it sit a historical English translation and one shared modern English draft. The shared draft is faithful: plain words, same argument, no side taken.
2. **Renderings** (`renderings/`). A tradition's own translation of the passages where it would translate differently: a Maoist rendering, an anarchist rendering, and so on.
3. **Commentary** (`commentary/`). Each tradition's footnotes, explanations, background, application today, critique, and later theory that extends or supersedes a passage, each tied to a verse, a section or a whole work.
4. **Adaptations** (`adaptations/`). Short pamphlets for today ("Who Profits From Your Work?") with modern examples and modern money, citing the verses they draw on so any reader can check the original.

In the reader, renderings and commentary are off until you switch them on, and you can filter commentary by tradition and by kind.

## Works

Every work planned for the library, in queue order, and how far along it is. **Ready for rewrite** means the text is sourced, numbered, documented and open for the modern draft. This table is generated from [`catalog.yaml`](catalog.yaml) by `scripts/build.py`; a scheduled job takes the next planned work off the list twice a day.

<!-- catalog:start -->
| # | Work | Author | Cite as | Original | Rights | Stage | Progress |
|---|---|---|---|---|---|---|---|
| 1 | [Manifesto of the Communist Party (1848)](works/communist-manifesto) | Karl Marx, Friedrich Engels | `CM` | German | A | 📝 translating | 730 verses · 446 seeded · 0 drafted · 40 alignment checks |
| 2 | [Wage Labour and Capital (1849)](works/wage-labour-and-capital) | Karl Marx | `WLC` | German | A | ✅ ready for rewrite | 565 verses · 0 seeded · 0 drafted · 42 alignment checks |
| 3 | [Value, Price and Profit (1865)](works/value-price-and-profit) | Karl Marx | `VPP` | English | A | ✅ ready for rewrite | 765 verses · 0 seeded · 0 drafted · 0 alignment checks |
| 4 | [Principles of Communism (1847)](works/principles-of-communism) | Friedrich Engels | `PC` | German | B | ✅ ready for rewrite | 233 verses · 0 seeded · 0 drafted · 0 alignment checks |
| 5 | Preamble of the Industrial Workers of the World (1908) | Industrial Workers of the World | `IWW` | English | A | ⏳ planned |  |
| 6 | Socialism: Utopian and Scientific (1880) | Friedrich Engels | `SUS` | German | A | 📦 sourced |  |
| 7 | The Conquest of Bread (1892) | Peter Kropotkin | `CB` | French | A | ⏳ planned |  |
| 8 | Anarchy (1891) | Errico Malatesta | `AN` | Italian | A | ⏳ planned |  |
| 9 | God and the State (1882) | Mikhail Bakunin | `GAS` | French | A | ⏳ planned |  |
| 10 | The Civil War in France (1871) | Karl Marx | `CWF` | English | A | 📦 sourced |  |
| 11 | Anarchism and Other Essays (1910) | Emma Goldman | `AOE` | English | A | 📦 sourced |  |
| 12 | Mutual Aid: A Factor of Evolution (1902) | Peter Kropotkin | `MA` | English | A | 📦 sourced |  |
| 13 | The State and Revolution (1917) | Vladimir Lenin | `SR` | Russian | B | ⏳ planned |  |
| 14 | The Eighteenth Brumaire of Louis Bonaparte (1852) | Karl Marx | `EB` | German | A | 📦 sourced |  |
| 15 | Critique of the Gotha Programme (1875) | Karl Marx | `CGP` | German | B | 📦 sourced |  |
| 16 | The Origin of the Family, Private Property and the State (1884) | Friedrich Engels | `OF` | German | A | 📦 sourced |  |
| 17 | Woman and Socialism (1879) | August Bebel | `WAS` | German | A | ⏳ planned |  |
| 18 | The Poverty of Philosophy (1847) | Karl Marx | `POP` | French | A | ⏳ planned |  |
| 19 | The Condition of the Working Class in England (1845) | Friedrich Engels | `CWC` | German | A | 📦 sourced |  |
| 20 | The German Ideology (1846) | Karl Marx, Friedrich Engels | `GI` | German | B | ⏳ planned |  |
| 21 | The Mass Strike, the Political Party and the Trade Unions (1906) | Rosa Luxemburg | `MS` | German | B | ⏳ planned |  |
| 22 | Reform or Revolution (1899) | Rosa Luxemburg | `ROR` | German | B | ⏳ planned |  |
| 23 | Imperialism, the Highest Stage of Capitalism (1917) | Vladimir Lenin | `IMP` | Russian | B | ⏳ planned |  |
| 24 | Now and After: The ABC of Communist Anarchism (1929) | Alexander Berkman | `ABC` | English | A | ⏳ planned |  |
<!-- catalog:end -->

Copyright tiers (A, B, C) are explained in [docs/roadmap.md](docs/roadmap.md).

## What a verse looks like

`WLC I.13.1` (instalment I, paragraph 13, sentence 1):

| | |
|---|---|
| **German (1891)** | Die Arbeitskraft ist also eine Ware, die ihr Besitzer, der Lohnarbeiter, an das Kapital verkauft. |
| **1849 reading** | *Arbeit* instead of *Arbeitskraft* (Engels changed it in 1891) |
| **English 1902** | Consequently, labour-power is a commodity which its possessor, the wage-worker, sells to the capitalist. |
| **Modern draft** | *(yours to write)* |

## How contributing works

You only ever edit YAML: a work's `text/` and `glossary.yaml`, or your tradition's files in `commentary/` and `renderings/`. The scripts do the rest:

- `scripts/validate.py` checks every change: verse numbers frozen, statuses valid, and every verse cited by a glossary, commentary entry, rendering or adaptation actually exists.
- `scripts/build.py` regenerates everything in `dist/`: per-work CSV, Excel workbook and Markdown tables, and the HTML reader for the whole library.
- When a change is merged to `main`, GitHub Actions rebuilds `dist/`, commits it, and publishes the reader to GitHub Pages. Nobody edits `dist/` by hand.

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Then, depending on what you want to do: numbering rules in [VERSIFICATION.md](VERSIFICATION.md), house style in [docs/translation-principles.md](docs/translation-principles.md), commentary and renderings in [docs/commentary-guide.md](docs/commentary-guide.md), Discussions and labels in [docs/discussions.md](docs/discussions.md), adding a new work in [docs/adding-a-work.md](docs/adding-a-work.md). Everyone follows the [code of conduct](CODE_OF_CONDUCT.md).

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
renderings/<tradition>/    a tradition's alternative translations of chosen verses
commentary/<tradition>/    a tradition's footnotes, explanations, critique and later theory
traditions.yaml            the traditions recognised, named as their adherents name them
adaptations/               modern pamphlets, each citing the verses it uses
scripts/                   validate.py, build.py, reader template, shared lib/
dist/                      generated reading copies (do not edit)
docs/                      principles, roadmap, how to add a work
manifesto/                 the original A Modern Manifesto rewrite and its source text
sources/                   the project's reference library from before the restructure
```

## Prior work

Hal Draper's *The Adventures of the Communist Manifesto* (1994) set the 1848 German, the 1850 and 1888 English and his own translation side by side. This library does that kind of work in the open, at sentence level, across many works, with the arguments kept beside the text.

## Find this project

GitHub topics: marxism, socialism, communism, anarchism, leftism, political-education, communist-manifesto, karl-marx, translation, open-source-translation.

## License

Translations, notes, glossaries, adaptations and documentation: [CC BY-SA 4.0](LICENSE). Scripts: MIT ([LICENSE-CODE](LICENSE-CODE)). The status of every source text is in the work's SOURCES.md.
