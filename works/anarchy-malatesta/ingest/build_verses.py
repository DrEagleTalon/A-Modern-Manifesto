"""One-time ingest for Anarchy (AN). English-only build.

Malatesta wrote L'Anarchia in Italian (1891 in the catalog). The Italian is not in this repository
yet, so this build has the English column only and the original column is left empty. Until the
Italian is added, the English sets the verse boundaries (anchor_language: en), as VERSIFICATION.md
allows for CM P1893 and as CB does for its French. When a public-domain Italian text is added it
becomes the original column; the verse ids do not change, and places where the Italian divides
differently are handled with joined_to and align.

English  The anonymous English translation in the Free Society Library printing of 1900, as
         transcribed by Project Gutenberg (ebook 40365, ASCII file 40365.txt). Public domain in the
         United States.

Sections follow the book's own divisions:
  0    the title and the unnumbered opening (what the word means; what government is). Paragraph 0
       is the title heading.
  I    the part the book numbers I (solidarity; the society of free men).
  II   the part the book numbers II (objections answered; the way to Anarchy).
       Paragraph 0 of I and II is the number the book prints.
The book also divides the text with rules: a long rule inside section 0 and short rules inside I
and II. They are not part of the verse addresses; the script prints where each falls and
SOURCES.md lists them.

Left out: the title page (title, author, "Published by the Free Society Library in 1900") and
the transcriber's note. There are no footnotes.

Run once. After the lock file exists the YAML in text/ is the source of truth.
"""
import json
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
REPO = WORK.parents[1]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
import segment  # noqa: E402
import versify  # noqa: E402
from versify import P, attach_apparatus, build_section, dump, finalise  # noqa: E402

RAW = WORK / "sources" / "raw" / "en" / "gutenberg_40365.txt"
CLEAN = WORK / "sources" / "clean"

SRC_ORIG = ("Not yet in this repository. Malatesta's Italian, L'Anarchia (1891), "
            "is still to be located on a reachable mirror.")
SRC_EN = ("Anonymous English translation, Free Society Library printing (1900), "
          "Project Gutenberg ebook 40365 (public domain)")

# Obvious errors in the transcription. The Gutenberg mirror has no page scans, so these could not be
# checked against the printing. Listed in SOURCES.md; spellings that only look odd are kept.
CORRECTIONS = [
    ("over man, there,\r\nwould be", "over man, there\r\nwould be"),     # II.2.2: stray comma
    ("is the must superior.", "is the most superior."),                    # II.70.8: "must" for "most"
]

# Local to this ingest; the shared rules in scripts/lib are not changed.
# A sentence end the shared splitter cannot see because "etc." is also an abbreviation.
EN_BREAKS = ["technical direction, administration, etc."]


def _split(text, lang):
    out = segment.split_sentences(text, lang)
    for b in EN_BREAKS:
        out = [x for s in out for x in ([s[:s.index(b) + len(b)].strip(), s[s.index(b) + len(b):].strip()]
                                         if b in s and not s.endswith(b) else [s])]
    return out


def _para_sentences(text, lang, kind):
    if kind in ("heading", "signature"):
        return [text]
    return _split(text, lang)


versify.para_sentences = _para_sentences

LONG_RULE = re.compile(r"-{20}")
SHORT_RULE = re.compile(r"-{10}")
USED = set()


# ---------------------------------------------------------------- reading the Gutenberg text

def load():
    t = RAW.read_bytes().decode("ascii")
    for a, b in CORRECTIONS:
        assert t.count(a) == 1, a
        t = t.replace(a, b)
        USED.add(a)
    t = t.replace("\r", "")
    for b in EN_BREAKS:
        assert t.replace("\n", " ").count(b) == 1, b
    lines = t.split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.strip() == "Published by the Free Society Library in 1900")
    end = next(i for i, ln in enumerate(lines) if ln.startswith("End of the Project Gutenberg"))
    return lines[start + 1:end]


def blocks(lines):
    """Runs of non-blank lines, each as its list of raw lines."""
    out, cur = [], []
    for ln in lines + [""]:
        if ln.strip():
            cur.append(ln)
        elif cur:
            out.append(cur)
            cur = []
    return out


def text_of(block):
    s = "\n".join(x.strip() for x in block)
    s = re.sub(r"\n--", "--", s)          # a dash carried over to the next line belongs to the word before
    s = s.replace("\n", " ")
    s = s.replace("_", "")                # Gutenberg's italics
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse():
    bl = blocks(load())
    assert text_of(bl[0]) == "ANARCHY." and SHORT_RULE.fullmatch(text_of(bl[1])), bl[:2]
    sections = [{"sid": "0", "title": "Anarchy", "paras": [P("heading", "Anarchy")]}]
    rules = []
    for b in bl[2:]:
        t = text_of(b)
        if re.fullmatch(r"(I|II)\.", t):
            sid = t[:-1]
            sections.append({"sid": sid, "title": sid, "paras": [P("heading", sid)]})
            continue
        if LONG_RULE.fullmatch(t) or SHORT_RULE.fullmatch(t):
            cur = sections[-1]
            rules.append({"section": cur["sid"], "after_para": len(cur["paras"]) - 1,
                          "rule": "long" if LONG_RULE.fullmatch(t) else "short"})
            continue
        assert not t.startswith("-"), t
        sections[-1]["paras"].append(P("p", t))
    assert [s["sid"] for s in sections] == ["0", "I", "II"]
    # the long rules that stand just before "I." and "II." and at the end are section breaks
    rules = [r for r in rules if not (r["rule"] == "long" and
                                      r["after_para"] == len(next(s for s in sections if s["sid"] == r["section"])["paras"]) - 1)]
    return sections, rules


# ---------------------------------------------------------------- writing

def meta(sid, title):
    return {"section": sid, "title_original": title, "title_en": title, "author": "Errico Malatesta",
            "date": "1891 (Italian); English printing 1900",
            "original_language": "it", "anchor_language": "en", "source_original": SRC_ORIG, "source_en": SRC_EN}


def main():
    sections, rules = parse()
    total = 0
    names = {"0": "00-opening", "I": "01-i", "II": "02-ii"}
    for s in sections:
        vs, _ = build_section(s["sid"], s["sid"], "en", s["paras"], [], lang_a="en", single=True)
        attach_apparatus(vs, {}, f"{s['sid']}.", {})
        vs = finalise(vs)
        dump(WORK / "text" / f"{names[s['sid']]}.yaml", meta(s["sid"], s["title"]), vs)
        print(f"{s['sid']:3} {len(s['paras']) - 1:4} paragraphs {len(vs):5} verses")
        total += len(vs)
    assert USED == {a for a, _ in CORRECTIONS}
    for r in rules:
        print(f"{r['rule']:5} rule after {r['section']}.{r['after_para']}, before {r['section']}.{r['after_para'] + 1}")
    CLEAN.mkdir(parents=True, exist_ok=True)
    (CLEAN / "en.json").write_text(json.dumps({"sections": {s["sid"]: [p["text"] for p in s["paras"]] for s in sections},
                                               "rules": rules}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("total", total)


if __name__ == "__main__":
    main()
