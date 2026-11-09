# Editing YAML: a first-timer's guide

Every verse, glossary entry and commentary note in this library lives in a YAML file. If you have never seen one, this page is enough to start. You do not need to install anything to make your first edit.

## What YAML is

YAML is plain text with a few layout rules, so that people can read it and scripts can read it too. A verse looks like this:

```yaml
- id: II.52.2
  kind: p
  original: Die Arbeiter haben kein Vaterland.
  en: The working men have no country.
  modern: Workers have no country.
  modern_status: draft
  notes: ''
```

Read it as a list of records. The `-` starts a new record (one verse). Every line under it is a `field: value` pair. You change the words after the colon and leave the rest alone.

## The rules that actually bite

**Indent with spaces, never tabs.** Fields of the same verse line up exactly under each other. In this repository that is two spaces in from the `-`. One space too many or too few and the file breaks.

**A colon needs a space after it.** `modern: Workers have no country.` works. `modern:Workers` does not.

**Put text in quotes when it could confuse the parser.** That means text containing `: ` (colon then space), text starting with a quote mark, `[`, `{`, `&`, `*`, `#`, `!`, `%`, `@` or a backtick, and text that is only `yes`, `no`, `true`, `false` or a number. Single quotes are the safe choice. Inside single quotes, write an apostrophe as two apostrophes:

```yaml
modern: 'The workers'' movement: a movement of the immense majority.'
```

**Long text can go on its own lines.** Put `>-` after the colon and indent the text on the following lines. The lines are joined with spaces when the file is read:

```yaml
notes: >-
  Moore renders "Bourgeois" here and "bourgeoisie" two lines later;
  the German has the same word both times.
```

**`''` means empty.** Leave `notes: ''` as it is if you have nothing to add.

**Never change `id`.** Verse numbers are permanent, and the checks will refuse a pull request that renumbers anything.

You do not have to get this perfect. Every pull request runs `scripts/validate.py` automatically, and if the YAML is broken the check turns red and tells you the file and line.

## The easiest way: edit in your browser

This works on any computer or phone, with nothing installed.

1. Open the file on GitHub, for example `works/communist-manifesto/text/01-manifesto/2-proletarians-and-communists.yaml`.
2. Press the pencil icon ("Edit this file").
3. Change the `modern` line, or whatever you came to fix.
4. Press **Commit changes**, choose **Create a new branch and start a pull request**, and describe the change with the verse id (`CM II.52.2`).

On a computer you can also press the `.` key on any page of the repository to open **github.dev**, a full editor in the browser with search across all files.

## Apps, if you want to work offline or edit many verses

What you want is a *plain text* or *code* editor. It should show line numbers and keep the file in UTF-8, so the German, French and Russian letters survive.

| Platform | Recommended | Also good |
|---|---|---|
| Windows | [Visual Studio Code](https://code.visualstudio.com/) (free) with the **YAML** extension by Red Hat | [Notepad++](https://notepad-plus-plus.org/) (free) |
| Mac | Visual Studio Code with the Red Hat **YAML** extension | [BBEdit](https://www.barebones.com/products/bbedit/) (its free mode is plenty) |
| Linux | Visual Studio Code, or the open-source build VSCodium | Kate (KDE) or GNOME Text Editor, both usually preinstalled |
| iPhone and iPad | The GitHub website in Safari (see above) | [Runestone](https://apps.apple.com/us/app/id1548193893) (free, highlights YAML); Working Copy if you want a full Git client on the phone (pushing needs its paid tier) |
| Android | The GitHub website in Chrome (see above) | [Acode](https://acode.app/) (free, open source); pair it with MGit if you want to clone and push from the phone |

With the Red Hat YAML extension, VS Code underlines a mistake as you type, before you ever open a pull request. Ask in **Start here** if you want help setting up Git on your machine.

## Things that quietly break YAML

- **Word processors.** Word, Google Docs, Pages and TextEdit in rich-text mode add hidden formatting. Use a plain text editor or the browser.
- **Smart quotes on phones.** iPhone and many Android keyboards turn `'` into `’`. Inside the verse text that is fine, but the quote marks that open and close a value must be straight. On iPhone you can switch this off in Settings > General > Keyboard > Smart Punctuation.
- **Tabs.** Some editors insert a tab when you press Tab. Set the editor to "indent with spaces, size 2". VS Code does this for YAML by default.
- **Copying from a web page.** Pasted text can bring non-breaking spaces or line breaks in odd places. If the check fails on a line that looks fine, retype the spaces at the start of that line.
