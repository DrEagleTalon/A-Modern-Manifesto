# Contributing

You do not need to know Git to help. You do need to say which verse you are talking about, every time. Verse numbers are how this project keeps hundreds of separate conversations attached to the right sentence.

## Ways in

| You want to | Do this |
|---|---|
| Suggest a better modern rendering of a verse or two | Open an issue with the **Translation proposal** form, or edit the YAML on GitHub and open a pull request |
| Argue about what a passage means | Start a Discussion in **Interpretation**, titled `[I.12.3] short subject` |
| Settle how a recurring term is translated | Start a Discussion in **Glossary**, then update `glossary/terms.yaml` |
| Report a wrong word, a typo, or a bad alignment | Open an issue with the **Source or alignment error** form |
| Check the alignment flags | Search `review: true` in `text/`, fix or confirm, remove the flag |

## The verse record

Each verse in `text/**/*.yaml` looks like this:

```yaml
- id: II.52.2
  kind: p                 # heading | p | signature | note
  de: Die Arbeiter haben kein Vaterland.
  en: The working men have no country.
  modern: Workers have no country.
  modern_status: draft    # see the status ladder below
  notes: ''               # short translator notes; long arguments go to Discussions
  discussion: https://github.com/<org>/<repo>/discussions/12   # optional
  readings:               # optional, see "Recording interpretations"
  - tradition: ...
    rendering: ...
    argument: ...
    proposed_by: '@handle'
```

Fields you normally edit: `modern`, `modern_status`, `notes`, `discussion`, `readings`.

Fields you should not edit without a source: `de` and `en`. They are transcriptions of printed editions. A change needs a facsimile page or an edition reference in the pull request.

Fields written by the pipeline, which you may correct but should not invent: `joined_to`, `align`, `footnotes`, `de_variants`, `mew_page`, `note_edition`, `en_note`, `review`, `review_reason`.

## The status ladder

| `modern_status` | Meaning | Who can set it |
|---|---|---|
| `empty` | no modern text yet | anyone |
| `seed` | imported from *A Modern Manifesto*, a paraphrase of the 1888 English, not yet checked against the German | pipeline only |
| `draft` | someone has worked this verse against the German | the author of the change |
| `reviewed` | a second person who reads German has checked it against the German and the 1888 English and approves | a reviewer, not the author |
| `settled` | wording fixed for a release; changing it needs a Discussion first | maintainers |
| `joined` | this German sentence is covered by the previous verse's English and modern text | pipeline or splitter |

A pull request may move a verse up one step at a time. Turning a `seed` into a `draft` means rereading the German, not just polishing the English.

## Writing a modern rendering

Read [docs/translation-principles.md](docs/translation-principles.md) first. The short version:

1. Translate from the German. Use Moore and Engels as a witness, not as the source.
2. Keep the claim the authors made, even when you think history has moved on. Put the update in `notes`.
3. Use the glossary term. If you disagree with the glossary, argue it in the glossary discussion instead of quietly using a different word.
4. Plain modern English, readable aloud. No slang that will date in five years.

## Recording interpretations

People read the Manifesto differently, and some lines carry real weight in arguments between tendencies: the state in II.66.1, democracy in II.65.1, the family in II.39.1, the nation in II.52.2. This project does not pretend those arguments are settled.

The rule is:

- The `modern` field holds the single rendering that is most faithful to the German. It is not where an interpretation wins.
- When a Discussion surfaces readings that differ in substance, each one is added to the verse's `readings` list with the tradition or school it comes from, how it would render or gloss the line, and the argument in a sentence or two. Name the tradition as its own adherents would name it.
- A reading needs a source or a clear argument, and the Discussion link. Readings are not ranked.

If a reading shows that the German genuinely supports two translations, say so in `notes` and pick the more literal one for `modern`.

## Pull requests

- Title starts with the verse range: `[I.12.1-I.12.4] tighten modern draft`.
- One section per pull request where possible, so reviews stay readable.
- Run `python scripts/validate.py` before pushing. CI runs it too, then rebuilds `dist/`.
- Do not edit anything in `dist/`. It is generated.

## Discussions

Recommended categories: **Interpretation**, **Glossary**, **Translation choices**, **Sources**, **General**. Title every thread with the verse number or glossary term in square brackets so search works: `[I.18.5] "All that is solid melts into air"`, `[glossary] Aufhebung`.

When a thread reaches a conclusion, someone opens a pull request that writes it into the verse (`modern`, `notes`, or `readings`) and links the thread in `discussion`.

## Conduct

Argue with positions, not people. Comrades from different tendencies are expected to disagree here and to keep working on the same text afterward. Personal attacks, sectarian baiting and harassment get a warning and then a ban.

## Setup for the scripts

```
pip install -r requirements.txt
python scripts/validate.py
python scripts/build.py
```
