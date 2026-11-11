"""One-time ingest for Mutual Aid: A Factor of Evolution (MA).

Kropotkin wrote Mutual Aid in English. The chapters first appeared as articles in The Nineteenth
Century (1890 to 1896) and were collected, revised, as a book by William Heinemann, London, 1902.
So the original column IS the English and there is no historical-translation column, as in VPP,
CWF and AOE.

Source: Project Gutenberg ebook 4341 (plain ASCII text, "Produced by Charles Aldarondo"), mirrored at
github.com/GITenberg/Mutual-Aid--A-Factor-of-Evolution_4341. It has the 1902 title page and the
Introduction dated "Bromley, Kent, 1902". It has no accents and no italics, and leaves out the
book's Appendix (see SOURCES.md).

Sections:
  P1902    Kropotkin's Introduction, dated Bromley, Kent, 1902. Paragraph 0 is its heading.
  I to VIII the eight chapters. Paragraph 0 is the chapter heading. Paragraph 1 is Kropotkin's
           summary of the chapter, printed under the title as a run of short phrases; it is one
           verse of kind `heading`, never split.
  C        the Conclusion. Paragraph 0 is its heading.
Footnotes are numbered afresh in each chapter and printed at its end under "NOTES:". Each sits
inside its chapter as <chapter>.N<number>, for example I.N3.

Left out: the Gutenberg header and licence, and the title page.

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

RAW = WORK / "sources" / "raw" / "en" / "gutenberg_4341.txt"
CLEAN = WORK / "sources" / "clean"

SRC = ("P. Kropotkin, Mutual Aid: A Factor of Evolution (London: William Heinemann, 1902), public domain; "
       "Project Gutenberg ebook 4341")

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]

# Obvious errors in the transcription, listed in SOURCES.md. Applied to the joined paragraph text.
# Each must occur exactly once. None could be checked against a scan of the 1902 printing.
CORRECTIONS = [
    # I: Huxley's sentence as printed in The Nineteenth Century, Feb. 1888 ("set to fight--whereby");
    # the transcription has a stray comma and has lost the dash and a letter.
    ("set to, fight hereby the strongest", "set to fight--whereby the strongest"),
    # I.N3: the title of Houzeau's book is "Etudes sur les facultes mentales des animaux".
    ("Les facultes etales des animaux", "Les facultes mentales des animaux"),
    # IV.15: dash lost between two clauses.
    ("the territory was dottedall these", "the territory was dotted--all these"),
    # IV.N4: the Russian review Severnyi Vestnik.
    ("Severnyi Vestnil", "Severnyi Vestnik"),
    # V.N40: comma for full stop.
    ("Les Communes francaises, pp, 45-46", "Les Communes francaises, pp. 45-46"),
    # C.11: the first of a pair of dashes lost ("mutual support--not mutual struggle--has had").
    ("mutual support not mutual struggle--has", "mutual support--not mutual struggle--has"),
]

# Local to this ingest; the shared rules in scripts/lib are not changed.
# Abbreviations that never end a sentence here, almost all in the notes: initials of first names
# ("Ch. Dixon", "Max. Perty", "Joh. Falke"), titles ("Prof.", "Rev."), months, and the shortened
# words of German and French citations ("Bd.", "Abth.", "Botan. Mitth.", "Bull. Soc.").
segment.ABBR["en"] = segment.ABBR["en"] | {
    "Ch", "Max", "Alf", "Eb", "Joh", "Fr", "Wilh", "Dm", "Aug", "Col",
    "Prof", "Rev", "Feb", "Sept", "Nos", "Pp", "Cf", "Bd", "Abth",
    "vols", "Botan", "Geol", "Geogr", "Histor", "Bull", "Afrik",
}
# A lower-case Roman numeral is a volume number in the notes ("Brehm, iv. 567"), and "l.c." is "loc. cit.":
# never split after one when a page, part or number of the cited work follows.
ROMAN_VOL = re.compile(r"(\b[ivxl]+|\bl\.c)\.$")
VOL_NEXT = re.compile(r"(\d|Part |No\. \d|Bd\. )")
# Sentence ends the shared splitter cannot see (a number or "etc." before the full stop): split between
# the two halves of each pair. Each pair occurs once in the book.
EN_BREAKS = [
    ("instead of 80.", "But a revolution"),               # VI.36
    ("579, etc.", "Among the gulls"),                     # II.N4
    ("loc. cit. p. 24.", "Europeans, grown"),             # III.N28
    ("pp. 1-36.", "A remainder"),                         # III.N39
    ("iii. p. 7.", "Also Grey"),                          # III.N45
    ("Doniol, etc.", "For Italy"),                        # IV.N4
    ("Arnold, etc.", "For India"),                        # IV.N4
    ("pp. 11-13.", "E. Nys"),                             # IV.N29
    ("ii. 58.", "The same respect"),                      # IV.N35
    ("1890, p. 68.", "They also took"),                   # IV.N36
    ("1885, p. 67.", "It appears very probable"),         # V.N36
    ("pp. 12-16.", "In 1485"),                            # V.N52
    ("75, etc.", "As to Mr. Gross"),                      # VI.N14
    ("pp. 20-31.", "Also Sismondi"),                      # VI.N37
    ("viii. 85-99.", "The popular hatred"),               # VI.N37
    ("341, etc.", "M. Terssac"),                          # VII.N28
]
# Places where the shared rules split inside one sentence: rejoin after these.
EN_NOBREAKS = [
    "on 7s.",                              # VIII: "on 7s. 6d. a week"
    "Lettres sur l'histoire de France.",   # V.N10: "... de France. 7th Letter."
    "3e edition.",                         # VII.N5: "3e edition. Paris, 1892."
    "Life of an Artisan.",                 # VIII.N18: "... an Artisan. Coventry, 1893."
]
BREAKS_USED, NOBREAKS_USED, USED = set(), set(), set()
# Datelines: one verse each, never split.
SIGNATURES = ["Bromley, Kent, 1902."]
SIG_SEEN = []


def _split(text, lang):
    out = segment.split_sentences(text, lang)
    merged = []                # first rejoin splits made inside a sentence
    for s in out:
        hit = [nb for nb in EN_NOBREAKS if merged and merged[-1].endswith(nb)]
        vol = merged and ROMAN_VOL.search(merged[-1]) and VOL_NEXT.match(s)
        if hit or vol:
            NOBREAKS_USED.update(hit)
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)
    out = merged
    for a, b in EN_BREAKS:     # then split where a sentence ends unseen
        res = []
        for s in out:
            k = s.find(a + " " + b)
            if k >= 0:
                BREAKS_USED.add((a, b))
                res += [s[:k + len(a)].strip(), s[k + len(a):].strip()]
            else:
                res.append(s)
        out = res
    return out


def _para_sentences(text, lang, kind):
    if kind in ("heading", "signature"):
        return [text]
    return _split(text, lang)


versify.para_sentences = _para_sentences


# ---------------------------------------------------------------- reading the Gutenberg text

def load():
    t = RAW.read_bytes().decode("ascii").replace("\r", "")
    lines = t.split("\n")
    start = lines.index("INTRODUCTION")
    end = next(i for i, ln in enumerate(lines) if ln.startswith("End of Project Gutenberg's"))
    return lines[start:end]


def blocks(lines):
    out, cur = [], []
    for ln in lines + [""]:
        if ln.strip():
            cur.append(ln)
        elif cur:
            out.append(cur)
            cur = []
    return out


def fix(s):
    for a, b in CORRECTIONS:
        if a in s:
            assert s.count(a) == 1 and a not in USED, a
            s = s.replace(a, b)
            USED.add(a)
    return s


def join(lines):
    s = " ".join(x.strip() for x in lines)
    s = re.sub(r"\((\d+)\)", r" [[F\1]]", s)
    s = re.sub(r"\s+", " ", s).strip()
    return fix(s)


def title_case(t):
    small = {"a", "an", "the", "of", "in", "among", "amongst", "and"}
    words = t.lower().split()
    return " ".join(w if (i and w in small) else w.capitalize() for i, w in enumerate(words))


def parse():
    """-> {sid: (heading, summary or None, [blocks])}"""
    bl = blocks(load())
    heads = []
    i = 0
    while i < len(bl):
        t = " ".join(x.strip() for x in bl[i])
        if t == "INTRODUCTION":
            heads.append(("P1902", i, "Introduction", None, i + 1))
        elif t == "CONCLUSION":
            heads.append(("C", i, "Conclusion", None, i + 1))
        elif re.fullmatch(r"CHAPTER ([IVX]+)", t):
            rn = t.split()[1]
            name = " ".join(x.strip() for x in bl[i + 1])
            name = title_case(name.replace(" (continued)", "").replace(" (CONTINUED)", ""))
            if "(continued)" in " ".join(bl[i + 1]).lower():
                name += " (continued)"
            summary = " ".join(x.strip() for x in bl[i + 2])
            heads.append((rn, i, f"Chapter {rn}. {name}", summary, i + 3))
        i += 1
    assert [h[0] for h in heads] == ["P1902"] + ROMAN + ["C"], [h[0] for h in heads]
    secs = {}
    for k, (sid, _, heading, summary, body_start) in enumerate(heads):
        end = heads[k + 1][1] if k + 1 < len(heads) else len(bl)
        secs[sid] = (heading, summary, bl[body_start:end])
    return secs


def section(sid, bl):
    """Body paragraphs and footnotes of one section."""
    body, notes, in_notes = [], {}, False
    for b in bl:
        t = " ".join(x.strip() for x in b)
        if t == "NOTES:":
            in_notes = True
            continue
        if in_notes:
            m = re.match(r"^(\d+)\. ", t)
            assert m, (sid, t[:60])
            n = int(m.group(1))
            assert n == len(notes) + 1, (sid, n)
            notes[n] = [P("note", fix(re.sub(r"\s+", " ", t[m.end():]).strip()))]
            continue
        txt = join(b)
        kind = "signature" if txt in SIGNATURES else "p"
        if kind == "signature":
            SIG_SEEN.append(txt)
        body.append(P(kind, txt))
    refs = [int(n) for p in body for n in re.findall(r"\[\[F(\d+)\]\]", p["text"])]
    # III: the transcription has no marker for note 8, whose text it gives as "None" (see SOURCES.md).
    expect = [n for n in sorted(notes) if not (sid == "III" and n == 8)]
    assert refs == expect, (sid, refs, sorted(notes))
    return body, notes


# ---------------------------------------------------------------- writing

def meta(sid, title):
    return {"section": sid, "title_original": title, "title_en": title, "author": "Peter Kropotkin",
            "date": "1902", "original_language": "en", "anchor_language": "en", "source_original": SRC,
            "source_en": "None needed: the original is in English"}


def number(sid, paras, para0_heading=True):
    vs, _ = build_section(sid, sid, "de", paras, [], lang_a="en", single=True, para0_heading=para0_heading)
    attach_apparatus(vs, {}, f"{sid}.", {})
    return vs


SLUGS = {"I": "animals", "II": "animals-continued", "III": "savages", "IV": "barbarians",
         "V": "mediaeval-city", "VI": "mediaeval-city-continued", "VII": "amongst-ourselves",
         "VIII": "amongst-ourselves-continued"}


def main():
    secs = parse()
    files = {"P1902": "00-introduction.yaml", "C": "09-conclusion.yaml"}
    for i, sid in enumerate(ROMAN):
        files[sid] = f"{i + 1:02d}-{sid.lower()}-{SLUGS[sid]}.yaml"
    clean, total = {}, 0
    for sid, (heading, summary, bl) in secs.items():
        body, notes = section(sid, bl)
        head = [P("heading", heading)] + ([P("heading", summary)] if summary else [])
        vb = number(sid, head + body)
        vn = []
        for n, paras in notes.items():
            part = number(f"{sid}.N{n}", paras, para0_heading=False)
            if paras[0]["text"] == "None":
                where = ("and has no marker for it in the text; check the 1902 printing for the note and where "
                         "its marker falls") if sid == "III" else "; check the 1902 printing for the note"
                for v in part:
                    v["review"] = True
                    v["review_reason"] = f"The transcription gives this note as \"None\" {where}".replace(" ;", ";")
            vn += part
        vs = finalise(vb + vn)
        dump(WORK / "text" / files[sid], meta(sid, heading), vs)
        total += len(vs)
        clean[sid] = {"heading": heading, "summary": summary, "body": [p["text"] for p in body],
                      "notes": {str(n): [p["text"] for p in ps] for n, ps in notes.items()}}
        print(f"{sid:6} {len(body):4} paragraphs {len(vb):5} verses   notes {len(notes):2} {len(vn):4} verses")
    missing = [a for a, _ in CORRECTIONS if a not in USED]
    assert not missing, missing
    assert SIG_SEEN == SIGNATURES, SIG_SEEN
    assert BREAKS_USED == set(EN_BREAKS), set(EN_BREAKS) - BREAKS_USED
    assert NOBREAKS_USED == set(EN_NOBREAKS), set(EN_NOBREAKS) - NOBREAKS_USED
    print("total", total)
    CLEAN.mkdir(parents=True, exist_ok=True)
    (CLEAN / "en.json").write_text(json.dumps(clean, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
