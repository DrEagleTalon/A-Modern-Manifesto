# Contributing

You do not need to know Git to help, and you do not need to know YAML either: [docs/editing-yaml.md](docs/editing-yaml.md) explains the file format in five minutes and lists free editors for Windows, Mac, Linux, iPhone and Android. Most edits can be made straight in the browser on GitHub.

What you do need is to say which verse you are talking about, every time, with the work's prefix: `CM I.12.3`, `WLC II.4.2`. Verse numbers are how this project keeps hundreds of separate conversations attached to the right sentence.

## Ways in

| You want to | Do this |
|---|---|
| Suggest a better modern rendering of a verse or two | Open an issue with the **Translation proposal** form, or edit the YAML on GitHub and open a pull request |
| Argue about what a passage means | Start a Discussion in **Interpretation**, titled `[CM I.12.3] short subject` |
| Settle how a recurring term is translated | Start a Discussion in **Glossary**, then update the work's `glossary.yaml` |
| Add your tradition's footnotes, explanations or critique | Write an entry in `commentary/<tradition>/` (see `docs/commentary-guide.md`) |
| Translate passages the way your tradition would | Add verses to `renderings/<tradition>/` |
| Write a modern pamphlet based on a work | See `adaptations/README.md` |
| Add a new work to the library | See `docs/adding-a-work.md` |
| Report a wrong word, a typo, or a bad alignment | Open an issue with the **Source or alignment error** form |
| Check the alignment flags | Search `review: true` in a work's `text/`, fix or confirm, remove the flag |

## The verse record

Each verse in `works/<work>/text/**/*.yaml` looks like this:

```yaml
- id: II.52.2
  kind: p                 # heading | p | signature | note
  original: Die Arbeiter haben kein Vaterland.
  en: The working men have no country.
  modern: Workers have no country.
  modern_status: draft    # see the status ladder below
  notes: ''               # short translator notes; long arguments go to Discussions
  discussion: https://github.com/<owner>/<repo>/discussions/12   # optional
```

Fields you normally edit: `modern`, `modern_status`, `notes`, `discussion`.

Fields you should not edit without a source: `original` and `en`. They are transcriptions of printed editions. `original` is the text in the work's original language (German for Marx and Engels, Russian for Lenin), and the work's `work.yaml` says which edition each column comes from. A change needs a facsimile page or an edition reference in the pull request.

Fields written by the pipeline, which you may correct but should not invent: `joined_to`, `align`, `footnotes`, `variants`, `mew_page`, `note_edition`, `en_note`, `review`, `review_reason`.

## The status ladder

| `modern_status` | Meaning | Who can set it |
|---|---|---|
| `empty` | no modern text yet | anyone |
| `seed` | imported from an earlier modern rewrite (for CM, *A Modern Manifesto*), not yet checked against the original | pipeline only |
| `draft` | someone has worked this verse against the original | the author of the change |
| `reviewed` | a second person who reads the original language has checked it against the original and the historical English and approves | a reviewer, not the author |
| `settled` | wording fixed for a release; changing it needs a Discussion first | maintainers |
| `joined` | this original sentence is covered by the previous verse's English and modern text | pipeline or splitter |

A pull request may move a verse up one step at a time. Turning a `seed` into a `draft` means rereading the original, not just polishing the English.

## Writing a modern rendering

Read [docs/translation-principles.md](docs/translation-principles.md) first. The short version:

1. Translate from the original language. Use Moore and Engels as a witness, not as the source.
2. Keep the claim the authors made, even when you think history has moved on. Put the update in `notes`.
3. Use the glossary term. If you disagree with the glossary, argue it in the glossary discussion instead of quietly using a different word.
4. Plain modern English, readable aloud. No slang that will date in five years.

## Interpretations, alternative translations and commentary

People read these texts differently, and some lines carry real weight in arguments between tendencies: in the Manifesto, the state in CM II.66.1, democracy in CM II.65.1, the family in CM II.39.1, the nation in CM II.52.2. This project does not pretend those arguments are settled, and it does not let any of them win inside the shared text.

- The `modern` field in `works/` holds the single rendering that is most faithful to the original. Short, neutral translator notes go in `notes`.
- A tradition's own way of translating a passage goes in `renderings/<tradition>/<work>.yaml`.
- Footnotes, explanations, background, application today, critique, and later theory that extends or supersedes a passage go in `commentary/<tradition>/<work>.yaml`.

Read [docs/commentary-guide.md](docs/commentary-guide.md) for the kinds of entry and the rules, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

If the original genuinely supports two translations, say so in `notes` and pick the more literal one for `modern`.

## Pull requests

- Title starts with the work and verse range: `[CM I.12.1-I.12.4] tighten modern draft`.
- One section of one work per pull request where possible, so reviews stay readable.
- Run `python scripts/validate.py` before pushing. CI runs it too, then rebuilds `dist/`.
- Do not edit anything in `dist/`. It is generated, and rebuilt automatically when your change is merged.

## Discussions

Categories: **Start here**, **Interpretation**, **Translation choices**, **Glossary**, **Traditions**, **Commentary review**, **Library proposals**, **Adaptations**, plus Announcements, General and Polls. Title every thread with the verse number or glossary term in square brackets so search works: `[CM I.18.5] "All that is solid melts into air"`, `[WLC glossary] Arbeitskraft`.

When a thread reaches a conclusion, someone opens a pull request that writes it up (in the verse's `modern` or `notes`, or as a commentary entry or rendering) and links the thread. Categories, labels and search tips are in [docs/discussions.md](docs/discussions.md).

## Conduct

Argue with positions, not people. Comrades from different tendencies are expected to disagree here and to keep working on the same text afterward. The full rules are in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Setup for the scripts

```
pip install -r requirements.txt
python scripts/validate.py
python scripts/build.py
```
