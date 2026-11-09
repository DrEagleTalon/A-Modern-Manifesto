# Commentary and renderings: a guide

The texts in `works/` are kept clean: the original, a historical English translation, and one shared modern draft. Everything a tradition wants to say *about* a text lives in two separate layers, so Marxist-Leninists, Maoists, anarchists, syndicalists, Islamic socialists and everyone else can each have their full say without weighing down the original or each other.

| Layer | Folder | What it holds |
|---|---|---|
| **Renderings** | `renderings/<tradition>/<work>.yaml` | A tradition's own modern translation of the verses where it would translate differently from the shared draft |
| **Commentary** | `commentary/<tradition>/<work>.yaml` | Footnotes, explanations, background, application, critique and later theory, each attached to a verse, a range, a section or a whole work |

Both are off by default in the reader. A reader switches on **Commentary** or **Rendering** and filters by tradition and kind.

## Which tradition?

Traditions are listed in [`traditions.yaml`](../traditions.yaml), each with a slug used for folders and labels (`anarchist-communist`, `marxist-leninist`, `maoist` ...). Use `general` for textual history and scholarship that does not argue for a tendency. If yours is missing, propose it in the **Traditions** Discussion category; it needs one maintainer who belongs to it.

## Commentary

### Where it goes

One file per tradition per work: `commentary/anarchist-communist/communist-manifesto.yaml`. An entry about several works at once (for example, on the state across Marx, Engels and Lenin) goes in `commentary/<tradition>/_library.yaml` with `work: "*"`. Start from [`commentary/_template.yaml`](../commentary/_template.yaml).

Why not one giant file for everything? A single file edited by hundreds of people from rival tendencies turns every pull request into a merge conflict and every review into a fight over someone else's paragraph. One file per tradition keeps each tradition's work under its own maintainers. Readers still get everything in one place: the reader shows it all together, and `dist/<work>/commentary.md` collects every entry for a work in verse order.

### Kinds of entry

| `kind` | Shown as | Use it for | Example |
|---|---|---|---|
| `gloss` | Footnote | A short note on a word, name or phrase | Who Guizot was (CM 0.1.2) |
| `translation` | Translation note | Arguing that a word or passage should be rendered differently | Idiotismus is isolation, not idiocy (CM I.23.2) |
| `exegesis` | Explanation | What a passage, section or whole work means and how it fits together | What "winning the battle of democracy" means (CM II.65.1) |
| `context` | Background | History a reader needs | Why the WLC series stopped in 1849 |
| `application` | Today | How the idea applies to present conditions and organizing | Relative wages and productivity since the 1970s (WLC IV.12.1) |
| `critique` | Critique | Where your tradition thinks the text is wrong | An anarchist objection to the state in CM II.66.1 |
| `development` | Later theory | The idea was extended, revised or superseded by later thought | The authors' own 1872 revision of CM II.66.1-II.79.1 |

Keep kinds apart. An explanation that turns into a critique halfway through should be two entries: readers filtering for "Explanation" should not be ambushed by a polemic, and readers looking for critiques should find all of them.

`development` entries need two extra fields:

- `relation`: `extends` (builds on it), `revises` (changes part of it) or `supersedes` (replaces it).
- `by`: what does the extending, revising or superseding: verses (`CM P1872.2.6`), another entry (`marxist-leninist:imperialism-stage`), or a work outside the library ("Lenin, Imperialism (1917), ch. 7").

### What an entry can point at

`targets` takes one or more of:

| Form | Means |
|---|---|
| `CM II.66.1` | one verse |
| `CM II.65.1-II.81.1` | a range of verses |
| `CM II` | a whole section |
| `CM` | the whole work |

The validator rejects targets that do not exist.

### Answering another tradition

Never edit another tradition's file. Write your own entry and set `responds_to: "<tradition>:<entry-id>"`. The reader shows the exchange side by side. If you think an entry misrepresents your tradition or gets a fact wrong, open a thread in **Commentary review** instead.

### Status

| `status` | Meaning |
|---|---|
| `proposed` | written, not yet reviewed by the tradition's maintainers |
| `accepted` | the tradition's maintainers stand behind it |
| `disputed` | contested inside the tradition or on facts; see the linked Discussion |
| `retired` | kept for the record but no longer endorsed |

Core maintainers check format, sources and conduct. They do not rule on doctrine. A tradition's maintainers decide what their tradition's file says.

## Renderings

A rendering is a tradition's own modern translation, verse by verse, of the passages where it would translate differently from the shared draft. File: `renderings/<tradition>/<work>.yaml`, from [`renderings/_template.yaml`](../renderings/_template.yaml).

- List only the verses that differ. Where a rendering is silent, the reader shows "same as the shared draft".
- Start with `principles`: two or three sentences on what the rendering does differently and why.
- Every verse gets a `note` saying why it differs, citing the original wording.
- A rendering is still a translation. If what you want to write is an argument about the passage, it is commentary.

## Rules that apply to everyone

1. **Cite verses.** Every claim about what a text says points to a verse.
2. **Source facts.** Historical and factual claims need a source a reader can check.
3. **Name others fairly.** Describe another tradition the way its adherents would recognise before you criticise it.
4. **Stay in your lane.** Your tradition's files are yours; everyone else's are theirs.
5. **No anonymous doctrine.** Every entry lists its `authors`.

See also [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) and [discussions.md](discussions.md).
