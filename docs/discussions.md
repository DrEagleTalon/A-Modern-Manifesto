# Discussions, labels and how to find things

## How threads are organised

Every thread has three handles, so it can be found three ways:

1. **Category**: what kind of conversation it is (below).
2. **Title prefix**: what it is about, in square brackets: `[CM II.66.1]`, `[WLC glossary] Arbeitskraft`, `[general:idiotismus-is-isolation]`, `[new work] Value, Price and Profit`.
3. **Labels**: which work (`work: CM`), which tradition (`tradition: maoist`), which kind of commentary (`kind: critique`) and what state it is in (`disputed`, `needs German reader`).

### Categories

| Section | Category | Format | For |
|---|---|---|---|
| Community | 📣 Announcements | Announcement | Releases, new works, rule changes (maintainers post) |
| Community | 👋 Start here | Question and answer | New to theory or to GitHub? Ask anything |
| Community | 💬 General | Open-ended | Anything else |
| Community | 🗳️ Polls | Poll | Quick votes, for example which work comes next |
| The texts | 🔎 Interpretation | Open-ended | What a passage means, from a tradition or from the text |
| The texts | 🔤 Translation choices | Open-ended | Wording of the shared modern draft |
| The texts | 📚 Glossary | Open-ended | How a recurring term is translated |
| Traditions | 🧭 Traditions | Open-ended | Introduce a tradition, volunteer as its maintainer, propose a new one |
| Traditions | ✍️ Commentary review | Open-ended | Facts, sources and fairness of a specific commentary entry |
| Building the library | 📖 Library proposals | Open-ended | Which work next, and its copyright status |
| Building the library | 🛠️ Adaptations | Open-ended | Planning and reviewing modern pamphlets |

Each of the categories in "The texts", "Traditions" and "Building the library", plus "Start here", has a form in `.github/DISCUSSION_TEMPLATE/` that asks for the verse, tradition and sources up front.

Source errors and concrete translation proposals go to **Issues** instead, through the issue forms, because they end in a specific change to a file.

### Labels

| Group | Labels | Where they come from |
|---|---|---|
| Work | `work: CM`, `work: WLC` ... | generated from `works/*/work.yaml` |
| Tradition | `tradition: anarchist-communist`, `tradition: marxist-leninist` ... | generated from `traditions.yaml` |
| Kind of commentary | `kind: footnote`, `kind: translation note`, `kind: explanation`, `kind: background`, `kind: today`, `kind: critique`, `kind: later theory` | `.github/labels.yml` |
| Topic | `translation`, `rendering`, `commentary`, `glossary`, `adaptation`, `source`, `alignment`, `new work`, `tooling` | `.github/labels.yml` |
| State | `needs German reader`, `needs tradition review`, `disputed`, `good first issue`, `help wanted` | `.github/labels.yml` |

`scripts/sync_labels.py` creates and updates them, and the `labels` workflow runs it automatically whenever a work or tradition is added.

### Finding things

In the Discussions or Issues search box:

- Everything on one verse: `"CM II.66.1"`
- One tradition's threads: `label:"tradition: anarchist-communist"`
- All critiques of the Manifesto: `label:"work: CM" label:"kind: critique"`
- Open questions that need a German reader: `label:"needs German reader" is:open`
- Good first tasks: `label:"good first issue" is:open`

In the reader, switch on **Commentary** and use the tradition and kind filters.

## One-time setup (maintainers)

The labels already exist on the repository, and the forms and workflows are in the code. GitHub only lets the owner change repository settings and create Discussion categories, so these are clicks, in this order:

1. **Settings > General**: rename the repository to `left-classics` (old links redirect). Under Features, tick **Discussions**.
2. On the repository's main page, the gear icon next to **About**: description "The socialist, communist and anarchist classics, verse by verse, in plain English", website `https://dreagletalon.github.io/left-classics/`, and the topics listed in the README.
3. **Settings > Pages**: Source **GitHub Actions**.
4. **Settings > Actions > General**: Workflow permissions **Read and write**.
5. **Discussions**, pencil next to **Categories**: create the categories in the table above with exactly these names, typed without the emoji (pick the emoji with the separate emoji button; the forms match on the name): **Start here**, **Interpretation**, **Translation choices**, **Glossary**, **Traditions**, **Commentary review**, **Library proposals**, **Adaptations**. Use the format shown in the table.
6. Delete the default **Q&A**, **Ideas** and **Show and tell** categories (Start here and Library proposals replace them).
7. Optional: create the sections Community, The texts, Traditions, Building the library, and drag the categories into them.
8. Post the welcome message below in **Announcements** and pin it.

### Welcome post

> **Welcome to Left Classics**
>
> This is an open library of socialist, communist and anarchist classics, verse by verse: the original, a historical English translation, a plain modern English draft, and commentary from every tradition that wants to take part.
>
> New here? Ask anything in **Start here**. If you want to help, pick a `good first issue`, or try drafting a few verses of the modern translation. You can also bring your own tradition's reading of a passage to **Interpretation**.
>
> A couple of ground rules. Cite the verse you're talking about (`CM II.66.1`) and back up your facts with a source. And before you criticise another tradition, describe it the way its own people would. The full code of conduct is in the repository.
