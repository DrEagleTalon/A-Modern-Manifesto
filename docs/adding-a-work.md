# Adding a work to the library

Adding a work is a one-time job for someone comfortable with Python. After it is merged, everyone else only edits YAML.

## 1. Pick the work and check the rights

Find it in [roadmap.md](roadmap.md). Decide which edition is the base text (for Marx and Engels, usually the last edition they revised) and confirm that the original, and any historical English translation you plan to include, are in the public domain in the United States. Write down why. That reasoning goes into the work's `SOURCES.md`.

## 2. Make the folder

```
works/<work-id>/
  work.yaml
  SOURCES.md
  glossary.yaml
  cruxes.md
  sources/raw/      the exact files you build from, never edited
  ingest/build_verses.py
```

`work.yaml`:

```yaml
id: value-price-and-profit
prefix: VPP                 # unique, 2-6 capital letters; checked by validate.py
title: Value, Price and Profit
title_original: Value, Price and Profit
authors: [Karl Marx]
year: 1865
original_language: en
base_text: "Eleanor Marx's 1898 edition"
order: 30                   # position in the reader
columns:
  original: English original (1898 edition)
  en: ""                    # no historical translation when the original is English
  modern: Modern draft
status: setting-up
rights: Public domain.
```

## 3. Get the sources

- **Marx and Engels in German:** MEW via the mlwerke.de mirror (`github.com/wertform/mlwerke.de`, path `me/meNN/meNN_PPP.htm`). Compare against a second copy if you can. One mirror of the Manifesto had a word dropped from its most famous sentence.
- **English:** Marxists Internet Archive pages (mirrored at `github.com/MARX-EBOOKS/marx-ebooks.github.io`), Project Gutenberg (`github.com/GITenberg`), and archive.org scans of the original printings for checking.
- Save the raw files in `sources/raw/` and record their SHA-256 in `SOURCES.md`.

## 4. Write the ingest script

Copy `works/wage-labour-and-capital/ingest/build_verses.py` and adapt it. The shared library does the heavy lifting:

| Module | What it does |
|---|---|
| `scripts/lib/mew.py` | `parse_mew()` reads MEW pages (footnotes, variants, page numbers); `parse_mia()` reads Marxists Internet Archive pages and strips MIA's bracketed insertions |
| `scripts/lib/segment.py` | splits sentences (German and English rules; add rules for other languages here) |
| `scripts/lib/align.py` | aligns two languages sentence by sentence |
| `scripts/lib/versify.py` | `build_section()` numbers the verses and aligns, `attach_apparatus()` turns markers into footnotes, variants and pages, `finalise()` and `dump()` write the YAML |

Choices you make in the script:

- **Sections**: follow the author's own divisions (chapters, instalments, numbered theses). Prefaces and introductions are `P<year>`.
- **Alignment mode**: `build_section(..., flat=True)` aligns sentences across paragraph breaks, best when the historical translation re-paragraphs the text (as Lothrop did). The default aligns paragraphs first, best when paragraphs match (as in the Manifesto).
- **Repairs**: fix obvious transcription errors in a `CORRECTIONS` list, checked against a scan, and list them in `SOURCES.md`.

Run it, then read the flagged verses (`review: true`). Fix what the script can fix; leave the rest flagged for contributors.

## 5. Freeze the numbering

```
python scripts/validate.py --init-lock <work-id>
python scripts/validate.py
python scripts/build.py
```

The lock file makes the verse ids permanent. From now on nobody runs the ingest script again; the YAML is the source of truth.

## 6. Write the docs and open the pull request

Fill in `SOURCES.md` (editions, licences, repairs, checksums), start `glossary.yaml` with the terms that will recur, list the hard passages in `cruxes.md`, add the work to the table in the top-level README and mark it done in `roadmap.md`.
