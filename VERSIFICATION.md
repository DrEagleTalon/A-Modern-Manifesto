# Versification

Every sentence of the text has a permanent address. This file explains how the addresses were made and the rules that keep them stable, so that a citation written today still points at the same sentence in ten years.

## The address

```
CM  I . 23 . 2
│   │   │    └─ sentence within the paragraph (1, 2, 3 ...)
│   │   └────── paragraph within the section (0 = the section heading)
│   └────────── section
└────────────── work (Communist Manifesto)
```

Sections:

| Section | Contents | Example |
|---|---|---|
| `P1872` `P1882` `P1883` `P1888` `P1890` `P1892` `P1893` | the prefaces, by year of the edition | `P1872.2.6` |
| `0` | title and preamble ("Ein Gespenst geht um in Europa") | `0.1.1` |
| `I` `II` `III` `IV` | the four sections of the Manifesto | `II.81.1` |
| `N1` to `N8` | Engels's footnotes to the Manifesto, numbered as in MEW | `N2.1.3` |
| `E1` | Engels's note on "guild-master", which exists only in the English | `E1.1.1` |
| `P1888.N1` etc. | footnotes inside a preface | `P1888.N1.1.2` |

Inside a note the middle number is the note's paragraph. Several notes have one paragraph written for the 1888 English edition and a second written for the 1890 German edition; the `note_edition` field says which is which.

Subheadings in Section III (for example "a) Der feudale Sozialismus") take a paragraph number of their own, so `III.2.1` is a heading and `III.3.1` is the first sentence under it.

## Which language sets the boundaries

The German is the original, so German sentences define the verses. The 1888 English is lined up against them.

Two prefaces were not written in German, and for those the rule bends:

- **P1888** was written by Engels in English. The English sentences define the verses and the German column holds MEW's translation for reference.
- **P1893** was written in French (published in Italian). Neither original is in this repository yet, so the verses follow MEW's German translation and the English column holds a later translation. When a public-domain French or Italian text is added, it becomes a new column; the verse numbers do not change.

Each section file records this in `original_language` and `anchor_language`.

## When the languages do not match one to one

Moore and Engels often split one long German sentence into two English ones, or joined two short German sentences into one. The German numbering wins every time:

- **One German sentence, two English sentences**: both English sentences go in the one verse. The verse carries `align: "1:2"`.
- **Two German sentences, one English sentence**: the English (and the modern draft) sits on the first verse. The second verse carries `joined_to: <first verse id>` and leaves `en` and `modern` empty. Readers and the build tools show the joined verses as one group.

The modern draft does not have to follow Moore's sentence breaks. If a modern sentence needs to cover two German verses, use `joined_to` the same way.

## The freeze

`text/verse-ids.lock` lists every id that has ever been issued. `scripts/validate.py` fails a pull request if:

- an id in the lock file disappears or is renamed,
- a new id appears that is not a split of an existing one.

The only way to add a verse is to **split** an existing one with a letter suffix: `I.12.3` becomes `I.12.3a` and `I.12.3b`. Do this only when the original segmentation was wrong (for example the splitter broke a sentence at an abbreviation). Run `python scripts/validate.py --update-lock` to record the new ids. Merging verses is never done; use `joined_to` instead.

## How the first numbering was produced

`scripts/ingest/` holds the one-time pipeline. It extracted paragraphs from the sources, split sentences with simple published rules (`scripts/lib/segment.py`), and aligned English and the modern seed against the German with a length-and-anchor method in the style of Gale and Church (`scripts/lib/align.py`). Every alignment that was not a clean one-to-one match, or looked doubtful, was flagged `review: true` with a `review_reason`. The pipeline must not be run again over the published files; after v1.0 the YAML in `text/` is the source of truth.
