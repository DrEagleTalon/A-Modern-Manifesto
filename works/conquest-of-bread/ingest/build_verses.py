"""One-time ingest for The Conquest of Bread (CB). English-only build.

Kropotkin wrote La Conquête du pain in French (Paris 1892). The French is not in this repository yet,
so this build has the English column only and the original column is left empty. Until the French is
added, the English sets the verse boundaries (anchor_language: en), as VERSIFICATION.md allows for
CM P1893. When a public-domain French text is added it becomes the original column; the verse ids
do not change, and places where the French divides differently are handled with joined_to and align.

English  The anonymous English translation first published in London in 1906, with Kropotkin's
         preface of January 1913, in the Vanguard Press printing (New York 1926), as transcribed by
         Project Gutenberg (ebook 23428, ISO-8859-1 file 23428-8.txt, which keeps the accents and the
         pound sign that the ASCII file 23428.txt drops). Public domain in the United States.

Sections:
  P1913      Kropotkin's preface, dated Brighton, January 1913.
  I to XVII  the seventeen chapters. Paragraph 0 is the chapter heading. Kropotkin's numbered
             subsections (I, II ...) are headings with a paragraph number of their own, as in CM III.
Footnotes are numbered 1 to 13 across the book; each sits in the chapter it belongs to as
<chapter>.N<number>, for example II.N1, XVII.N13.

Left out: the Vanguard Press title page and its two blurbs ("The Man", "The Book"), which are not by
Kropotkin.

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

RAW = WORK / "sources" / "raw" / "en" / "gutenberg_23428-8.txt"
CLEAN = WORK / "sources" / "clean"

SRC_ORIG = ("Not yet in this repository. Kropotkin's French, La Conquête du pain (Paris 1892), "
            "is still to be located on a reachable mirror.")
SRC_EN = ("Anonymous English translation (London: Chapman and Hall, 1906) with Kropotkin's preface of 1913, "
          "Vanguard Press printing (New York 1926), Project Gutenberg ebook 23428 (public domain)")

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII"]
TITLES = ["Our Riches", "Well-Being for All", "Anarchist Communism", "Expropriation", "Food", "Dwellings",
          "Clothing", "Ways and Means", "The Need for Luxury", "Agreeable Work", "Free Agreement", "Objections",
          "The Collectivist Wages System", "Consumption and Production", "The Division of Labour",
          "The Decentralization of Industry", "Agriculture"]

# Printing and transcription errors, checked against the page scans in the Gutenberg repository.
# Listed in SOURCES.md.
CORRECTIONS = [
    ("_coup d'êtat_", "_coup d'état_"),          # P1913: misprint in the 1926 printing (scan p. xi)
    ("the shrewed heads", "the shrewd heads"),     # IV.4.1: misprint in the 1926 printing (scan p. 34)
]

# Local to this ingest; the shared rules in scripts/lib are not changed.
segment.ABBR["en"] = segment.ABBR["en"] | {"Wm", "vols", "Mlle", "MM", "Prof"}
# Sentence ends the shared splitter cannot see because the word before the stop is also an abbreviation.
EN_BREAKS = ["Technical skill of the worker?--No."]


def _split(text, lang):
    out = []
    for s in segment.split_sentences(text, lang):
        # shillings and pence: "1s. 8d." is one sum, not a sentence end
        if out and re.search(r"\b\d+s\.$", out[-1]) and re.match(r"\d+d\.", s):
            out[-1] = out[-1] + " " + s
        else:
            out.append(s)
    for b in EN_BREAKS:
        out = [x for s in out for x in ([s[:s.index(b) + len(b)].strip(), s[s.index(b) + len(b):].strip()]
                                         if b in s and not s.endswith(b) else [s])]
    return out


def _para_sentences(text, lang, kind):
    if kind in ("heading", "signature"):
        return [text]
    return _split(text, lang)


versify.para_sentences = _para_sentences
USED = set()


# ---------------------------------------------------------------- reading the Gutenberg text

def load():
    t = RAW.read_bytes().decode("latin-1").replace("\r", "")
    for a, b in CORRECTIONS:
        assert t.count(a) == 1, a
        t = t.replace(a, b)
        USED.add(a)
    for b in EN_BREAKS:
        assert t.replace("\n", " ").count(b) == 1, b
    lines = t.split("\n")
    start = lines.index("PREFACE", lines.index("CONTENTS"))
    end = next(i for i, ln in enumerate(lines) if ln.startswith("End of Project Gutenberg"))
    return lines[start:end]


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
    s = " ".join(x.strip() for x in block)
    s = s.replace("_", "")                                   # Gutenberg's italics
    s = re.sub(r"\[(\d+)\]", r" [[F\1]]", s)                 # footnote markers
    s = re.sub(r"\s+", " ", s).strip()
    return s


def table_rows(block):
    """Footnote 13 sets its figures as a table. One row per paragraph, label and figure joined by a colon."""
    rows = [x.strip() for x in block if not re.fullmatch(r"\s*-+\s*", x)]
    merged = []
    for r in rows:
        if merged and not re.search(r"\s{2,}\S", merged[-1]) and not merged[-1].endswith(":--") and merged[-1].upper() != merged[-1]:
            merged[-1] = merged[-1] + " " + r          # label wrapped onto a second line
        else:
            merged.append(r)
    out = []
    for r in merged:
        parts = re.split(r"\s{2,}", r)
        out.append(parts[0] if len(parts) == 1 else f"{parts[0]}: {parts[1]}")
    return out


def parse():
    lines = load()
    half = lines.index("THE CONQUEST OF BREAD")
    pre = blocks(lines[1:half])
    assert text_of(pre[-2]) == "BRIGHTON." and text_of(pre[-1]) == "January, 1913.", pre[-2:]
    preface = [P("heading", "Preface")] + [P("p", text_of(b)) for b in pre[:-2]] + [P("signature", "BRIGHTON. January, 1913.")]

    heads = [i for i, ln in enumerate(lines) if re.fullmatch(r"CHAPTER [IVX]+", ln)]
    assert [lines[i].split()[1] for i in heads] == ROMAN
    chapters = []
    for k, i in enumerate(heads):
        j = heads[k + 1] if k + 1 < len(heads) else len(lines)
        bl = blocks(lines[i:j])
        sid = ROMAN[k]
        title = text_of(bl[1])
        assert re.sub(r" \[\[F\d+\]\]", "", title) == TITLES[k].upper(), (title, TITLES[k])
        heading = f"Chapter {sid}. {TITLES[k]}" + re.sub(r"^[^\[]*", "", title).replace("[[", " [[")
        body, notes, cur, in_notes = [P("heading", re.sub(r"\s+", " ", heading))], {}, None, False
        for b in bl[2:]:
            t = text_of(b)
            if t in ("FOOTNOTE:", "FOOTNOTES:"):
                in_notes = True
                continue
            if not in_notes:
                body.append(P("heading" if re.fullmatch(r"[IVX]+", t) else "p", t))
                continue
            m = re.match(r"^\[\[F(\d+)\]\] (.*)$", t)
            if m:
                cur = int(m.group(1))
                notes[cur] = [P("note", m.group(2))]
            elif b[0].startswith("   "):
                notes[cur] += [P("note", r) for r in table_rows(b)]
            else:
                notes[cur].append(P("note", t))
        refs = [int(n) for p in body for n in re.findall(r"\[\[F(\d+)\]\]", p["text"])]
        assert refs == sorted(notes), (sid, refs, sorted(notes))
        chapters.append({"sid": sid, "title": f"Chapter {sid}. {TITLES[k]}", "body": body, "notes": notes})
    assert sorted(n for c in chapters for n in c["notes"]) == list(range(1, 14))
    return preface, chapters


# ---------------------------------------------------------------- writing

def meta(section, title):
    return {"section": section, "title_original": title, "title_en": title, "author": "Peter Kropotkin",
            "date": "1913" if section == "P1913" else "1892 (French); English 1906",
            "original_language": "fr", "anchor_language": "en", "source_original": SRC_ORIG, "source_en": SRC_EN}


def number(sid, paras, para0_heading=True):
    vs, _ = build_section(sid, sid, "en", paras, [], lang_a="en", single=True, para0_heading=para0_heading)
    attach_apparatus(vs, {}, f"{sid}.", {})
    return vs


def main():
    preface, chapters = parse()
    total, out = 0, {}
    vs = finalise(number("P1913", preface))
    dump(WORK / "text" / "00-preface" / "1913.yaml", meta("P1913", "Preface (1913)"), vs)
    out["P1913"] = (len(vs), 0)
    total += len(vs)
    for i, c in enumerate(chapters, start=1):
        vs = number(c["sid"], c["body"])
        nv = []
        for n, paras in c["notes"].items():
            nv += number(f"{c['sid']}.N{n}", paras, para0_heading=False)
        vs = finalise(vs + nv)
        dump(WORK / "text" / "01-conquest-of-bread" / f"{i:02d}-{c['sid'].lower()}.yaml", meta(c["sid"], c["title"]), vs)
        out[c["sid"]] = (len(vs), len(finalise(nv)))
        total += len(vs)
    assert USED == {a for a, _ in CORRECTIONS}
    CLEAN.mkdir(parents=True, exist_ok=True)
    (CLEAN / "en.json").write_text(json.dumps({"P1913": [p["text"] for p in preface],
                                               **{c["sid"]: {"body": [p["text"] for p in c["body"]],
                                                             "notes": {str(n): [p["text"] for p in ps] for n, ps in c["notes"].items()}}
                                                  for c in chapters}}, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, (n, nn) in out.items():
        print(f"{k:6} {n:5} verses ({nn} in notes)")
    print("total", total)


if __name__ == "__main__":
    main()
