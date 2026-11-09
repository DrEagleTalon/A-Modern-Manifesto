"""One-time ingest for God and the State (GAS). English-only build.

Bakunin wrote this fragment in French in 1871. Carlo Cafiero and Elisée Reclus published it in
Geneva in 1882 as Dieu et l'Etat, with their preface. The French is not in this repository yet,
so this build has the English column only and the original column is left empty. Until the French
is added, the English sets the verse boundaries (anchor_language: en), as VERSIFICATION.md allows
for CM P1893 and as CB and AN do. When a public-domain French text is added it becomes the original
column; the verse ids do not change, and places where the French divides differently are handled
with joined_to and align.

English  Benjamin Tucker's translation (Boston 1883) as reprinted by the Mother Earth Publishing
         Association, New York (about 1916; the printing names no translator), transcribed by
         Project Gutenberg (ebook 36568). Built from the ISO-8859-1 file 36568-8.txt, which keeps
         the accents that the fetched ASCII file 36568.txt drops; otherwise the two agree. Public domain in the United States.

Sections:
  P1882  the editors' "Preface to the First French Edition" (Cafiero and Reclus). Paragraph 0 is
         its heading; the closing signature is the last paragraph.
  0      Bakunin's text, which has no numbered divisions. Paragraph 0 is the title.
  0.N1 to 0.N11
         the footnotes, numbered as printed, inside section 0 as CB does (II.N1). N5 and N6 are
         the editors' notes on the gap in the manuscript; the rest are Bakunin's.
The book divides the text with rows of asterisks. They are not part of the verse addresses; the
script prints where each falls and SOURCES.md lists them.

Left out: the Gutenberg header and transcriber's note, the title pages and illustration, and the
publisher's advertisements after the footnotes.

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

RAW = WORK / "sources" / "raw" / "en" / "gutenberg_36568-8.txt"
CLEAN = WORK / "sources" / "clean"

SRC_ORIG = ("Not yet in this repository. Bakunin's French, Dieu et l'Etat (Geneva 1882, ed. Carlo Cafiero "
            "and Elisée Reclus), is still to be located on a reachable mirror.")
SRC_EN = ("Benjamin Tucker's English translation (Boston 1883), Mother Earth Publishing Association printing "
          "(New York, about 1916), Project Gutenberg ebook 36568 (public domain)")

# Obvious errors in the transcription, listed in SOURCES.md. Spellings that only look odd are kept.
CORRECTIONS = [
    ("a meretorious and sincere", "a meritorious and sincere"),   # 0.193.5: misspelling
]

# Local to this ingest; the shared rules in scripts/lib are not changed.
# Sentence ends the shared splitter cannot see: a regnal numeral and a two-digit year.
EN_BREAKS = ["the dictatorship of Bonaparte I.", "the revolution of 1789 and '93."]


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

STARS = re.compile(r"\*(\s+\*){4}")
USED = set()


# ---------------------------------------------------------------- reading the Gutenberg text

def load():
    raw = RAW.read_bytes()
    t = raw.decode("latin-1")
    for a, b in CORRECTIONS:
        assert t.count(a) == 1, a
        t = t.replace(a, b)
        USED.add(a)
    t = t.replace("\r", "")
    for b in EN_BREAKS:
        assert t.replace("\n", " ").count(b) == 1, b
    lines = t.split("\n")
    start = lines.index("Preface to the First French Edition")
    end = lines.index("                   THE ONLY ANARCHIST MONTHLY")
    body = lines[start:end]
    assert all(ord(c) < 128 or c in "éêëôûæ" for ln in body for c in ln), "unexpected character in the text"
    return body


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
    s = re.sub(r"\[(\d+)\]", r" [[F\1]]", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse():
    bl = blocks(load())
    texts = [text_of(b) for b in bl]
    assert texts[0] == "Preface to the First French Edition"
    i_title = texts.index("GOD AND THE STATE")
    i_notes = texts.index("FOOTNOTES:")
    # the preface, ending with the two-line signature
    pre = texts[1:i_title]
    assert pre[-1] == "Carlo Cafiero. Elisée Reclus.", pre[-1]
    preface = [P("heading", "Preface to the First French Edition")] + [P("p", t) for t in pre[:-1]] + [P("signature", pre[-1])]
    # Bakunin's text
    body, rules = [P("heading", "God and the State")], []
    for t in texts[i_title + 1:i_notes]:
        if STARS.fullmatch(t):
            rules.append(len(body))      # the rule falls before paragraph len(body)
            continue
        assert not t.startswith("-") and "*" not in t, t
        body.append(P("p", t))
    # the footnotes; a note runs on until the next "[n]"
    notes, cur = {}, None
    for t in texts[i_notes + 1:]:
        if STARS.fullmatch(t):
            break
        m = re.match(r"\[\[F(\d+)\]\] (.*)$", t)
        if m:
            cur = int(m.group(1))
            assert cur == len(notes) + 1, cur
            notes[cur] = [P("note", m.group(2))]
        else:
            notes[cur].append(P("note", t))
    refs = [int(n) for p in body for n in re.findall(r"\[\[F(\d+)\]\]", p["text"])]
    assert refs == list(range(1, 12)) == sorted(notes), (refs, sorted(notes))
    return preface, body, notes, rules


# ---------------------------------------------------------------- writing

def meta(section, title):
    return {"section": section, "title_original": title, "title_en": title,
            "author": "Carlo Cafiero and Elisée Reclus" if section == "P1882" else "Mikhail Bakunin",
            "date": "1882 (French); English 1883" if section == "P1882" else "1871 (French, published 1882); English 1883",
            "original_language": "fr", "anchor_language": "en", "source_original": SRC_ORIG, "source_en": SRC_EN}


def number(sid, paras, para0_heading=True):
    vs, _ = build_section(sid, sid, "en", paras, [], lang_a="en", single=True, para0_heading=para0_heading)
    attach_apparatus(vs, {}, f"{sid}.", {})
    return vs


def main():
    preface, body, notes, rules = parse()
    vp = finalise(number("P1882", preface))
    dump(WORK / "text" / "00-preface" / "1882.yaml", meta("P1882", "Preface to the First French Edition"), vp)
    vb = number("0", body)
    vn = []
    for n, paras in notes.items():
        vn += number(f"0.N{n}", paras, para0_heading=False)
    vs = finalise(vb + vn)
    dump(WORK / "text" / "01-god-and-the-state" / "god-and-the-state.yaml", meta("0", "God and the State"), vs)
    assert USED == {a for a, _ in CORRECTIONS}
    print(f"P1882 {len(preface) - 1:4} paragraphs {len(vp):5} verses")
    print(f"0     {len(body) - 1:4} paragraphs {len(vb):5} verses")
    print(f"notes {sum(len(p) for p in notes.values()):4} paragraphs {len(vn):5} verses in {len(notes)} notes")
    for r in rules:
        print(f"rule before 0.{r}.1")
    print("total", len(vp) + len(vs))
    CLEAN.mkdir(parents=True, exist_ok=True)
    (CLEAN / "en.json").write_text(json.dumps({"P1882": [p["text"] for p in preface],
                                               "0": [p["text"] for p in body],
                                               "notes": {str(n): [p["text"] for p in ps] for n, ps in notes.items()},
                                               "rules_before_paragraph": rules}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
