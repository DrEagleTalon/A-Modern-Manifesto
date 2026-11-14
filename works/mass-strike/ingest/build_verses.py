"""One-time ingest for The Mass Strike, the Political Party and the Trade Unions (MS).

German  Rosa Luxemburg, Massenstreik, Partei und Gewerkschaften (Hamburg: Erdmann Dubber, 1906), the first
        edition, printed in Fraktur for the Social Democratic organisations of Hamburg, Altona, Ottensen and
        Wandsbek. Project Gutenberg ebook 31614 (ISO-8859-1 file 31614.txt, produced by the Online
        Distributed Proofreading Team from Google Print scans), mirrored at
        github.com/GITenberg/Massenstreik-Partei-und-Gewerkschaften_31614.

There is no English column yet. Patrick Lavin's translation (Detroit 1925) is on no reachable mirror, so the
modern draft is translated straight from the German, as in PC, CGP and GI.

Sections:
  0        the title page: paragraph 0 is the title, paragraph 1 the line saying for whom it was written.
  I to VIII Luxemburg's eight numbered parts. Paragraph 0 is the numeral as printed.
Footnotes are numbered 1 to 4 across the pamphlet; each sits in the part it belongs to as
<part>.N<number>, for example I.N1.

Normalised: Gutenberg's marks for spaced type (_x_) and Antiqua (#x#) are dropped, and the guillemets
(»x«) become plain double quotes, as in the other German texts of the library. No-break spaces become
spaces. Left out: the Gutenberg front and back matter, and the imprint and printer's line of the 1906
printing.

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

RAW = WORK / "sources" / "raw" / "de" / "gutenberg_31614.txt"
CLEAN = WORK / "sources" / "clean"

SRC = ("Rosa Luxemburg, Massenstreik, Partei und Gewerkschaften (Hamburg: Erdmann Dubber, 1906), public domain; "
       "Project Gutenberg ebook 31614")
TITLE = "Massenstreik, Partei und Gewerkschaften"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]

# Obvious errors in the transcription, listed in SOURCES.md. Applied to the raw text; each must occur once.
CORRECTIONS = [
    # II.5: lower-case "b" in "z. B." (the abbreviation is "z. B." everywhere else in the pamphlet).
    ("z.\xa0b. durch Bömelburg", "z.\xa0B. durch Bömelburg"),
    # III.4: "Arbeitet" for "Arbeiter".
    ("1000 Arbeitet wurden", "1000 Arbeiter wurden"),
    # VII.10: a stray letter.
    ("kapitialistischen", "kapitalistischen"),
]

# Local to this ingest; the shared rules in scripts/lib are not changed.
# Abbreviations that never end a sentence here: "Fr. Engels" (I.N1), "Sächs. Arbeiterzeitung" (II.4),
# "za." for "zirka" (III.4, III.6), "Peter v. Struve" (III.8) and "&c." (VIII.10).
segment.ABBR["de"] = segment.ABBR["de"] | {"Fr", "Sächs", "za", "v", "&c"}
# Places where the shared rules split inside one sentence: rejoin after these.
DE_NOBREAKS = [
    "Die Bakunisten an der Arbeit.",      # I.N1: a title, followed by the series "Internationales aus dem Volksstaat"
    "lebensfrohe .....",                  # III.22: points of suspension before the last word
]
# Sentence ends the shared splitter cannot see ("usw." before a new sentence): split between the two halves.
DE_BREAKS = [
    ("usw. usw.", "Die Anstreicher"),     # III.17
    ("lesen usw.", "Um dies"),            # VIII.8
]
# Luxemburg runs reports from several towns together in one paragraph, divided by a dash ("... finden.
# -- In Jelissawetgrad beginnt ..."). The shared rules do not split before a double hyphen; this ingest
# does, and the dash stays at the head of the new sentence.
DASH = re.compile(r'(?<=[.!?"]) (?=-- [A-ZÄÖÜ"])')
NOBREAKS_USED, BREAKS_USED, USED = set(), set(), set()


def _split(text, lang):
    out = segment.split_sentences(text, lang)
    merged = []
    for s in out:
        hit = [nb for nb in DE_NOBREAKS if merged and merged[-1].endswith(nb)]
        if hit:
            NOBREAKS_USED.update(hit)
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)
    out = merged
    for a, b in DE_BREAKS:
        res = []
        for s in out:
            k = s.find(a + " " + b)
            if k >= 0:
                BREAKS_USED.add((a, b))
                res += [s[:k + len(a)].strip(), s[k + len(a):].strip()]
            else:
                res.append(s)
        out = res
    return [x for s in out for x in DASH.split(s)]


def _para_sentences(text, lang, kind):
    if kind in ("heading", "signature"):
        return [text]
    return _split(text, lang)


versify.para_sentences = _para_sentences


# ---------------------------------------------------------------- reading the Gutenberg text

def load():
    t = RAW.read_bytes().decode("latin-1").replace("\r", "")
    for a, b in CORRECTIONS:
        assert t.count(a) == 1, a
        t = t.replace(a, b)
        USED.add(a)
    lines = t.split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.strip() == "Massenstreik, Partei")
    end = next(i for i, ln in enumerate(lines) if ln.startswith("Druck: Hamburger Buchdruckerei"))
    body = lines[start:end]
    assert "„" not in t and "“" not in t   # so that the guillemets can become plain quotes without ambiguity
    return body


def blocks(lines):
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
    s = s.replace("_", "").replace("#", "")           # spaced type and Antiqua
    s = s.replace("»", '"').replace("«", '"')
    s = s.replace("\xa0", " ")
    s = re.sub(r"\[(\d)\]", r" [[F\1]]", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse():
    bl = blocks(load())
    texts = [text_of(b) for b in bl]
    # title page
    assert texts[:6] == ["Massenstreik, Partei und Gewerkschaften", "Von", "Rosa Luxemburg",
                         "Im Auftrage des Vorstandes der sozialdemokratischen Landesorganisation Hamburgs und "
                         "der Vorstände der sozialdemokratischen Vereine von Altona, Ottensen und Wandsbek",
                         "Verlag von Erdmann Dubber in Hamburg 1906", "I."], texts[:6]
    front = [P("heading", TITLE), P("heading", texts[3])]
    secs, cur, note = {}, None, None
    notes_all = {}
    for t in texts[5:]:
        if re.fullmatch(r"[IVX]+\.", t):
            cur = t[:-1]
            secs[cur] = {"body": [P("heading", t)], "notes": {}}
            continue
        m = re.match(r"^\[Fußnote (\d): ", t)
        if m:
            note = int(m.group(1))
            assert note == len(notes_all) + 1, note
            secs[cur]["notes"][note] = []
            notes_all[note] = cur
            t = t[m.end():]
        if note is not None:
            done = t.endswith("]")
            if done:
                t = t[:-1].rstrip()
            secs[cur]["notes"][note].append(P("note", t))
            if done:
                note = None
            continue
        assert "[" not in t.replace("[[F", "") and "]" not in t.replace("]]", ""), t[:80]
        secs[cur]["body"].append(P("p", t))
    assert list(secs) == ROMAN, list(secs)
    for sid, s in secs.items():
        refs = [int(n) for p in s["body"] for n in re.findall(r"\[\[F(\d)\]\]", p["text"])]
        assert refs == sorted(s["notes"]), (sid, refs, sorted(s["notes"]))
    return front, secs


# ---------------------------------------------------------------- writing

def meta(sid, title, title_en):
    return {"section": sid, "title_original": title, "title_en": title_en, "author": "Rosa Luxemburg",
            "date": "1906", "original_language": "de", "anchor_language": "de", "source_original": SRC,
            "source_en": "None yet: Patrick Lavin's translation (Detroit 1925) is not on a reachable mirror"}


def number(sid, paras, para0_heading=True):
    vs, _ = build_section(sid, sid, "de", paras, [], single=True, para0_heading=para0_heading)
    attach_apparatus(vs, {}, f"{sid}.", {})
    return vs


def main():
    front, secs = parse()
    vs = finalise(number("0", front))
    dump(WORK / "text" / "00-title.yaml", meta("0", TITLE, "The Mass Strike, the Political Party and the Trade Unions"), vs)
    total = len(vs)
    clean = {"0": [p["text"] for p in front]}
    print(f"0      {len(front):4} paragraphs {len(vs):5} verses")
    for i, sid in enumerate(ROMAN, start=1):
        s = secs[sid]
        vb = number(sid, s["body"])
        vn = []
        for n, paras in s["notes"].items():
            vn += number(f"{sid}.N{n}", paras, para0_heading=False)
        vs = finalise(vb + vn)
        dump(WORK / "text" / f"{i:02d}-{sid.lower()}.yaml", meta(sid, f"{sid}.", f"Part {sid}"), vs)
        total += len(vs)
        clean[sid] = {"body": [p["text"] for p in s["body"]],
                      "notes": {str(n): [p["text"] for p in ps] for n, ps in s["notes"].items()}}
        print(f"{sid:6} {len(s['body']) - 1:4} paragraphs {len(vb):5} verses   notes {len(s['notes'])} {len(vn):3} verses")
    assert USED == {a for a, _ in CORRECTIONS}
    assert NOBREAKS_USED == set(DE_NOBREAKS), set(DE_NOBREAKS) - NOBREAKS_USED
    assert BREAKS_USED == set(DE_BREAKS), set(DE_BREAKS) - BREAKS_USED
    print("total", total)
    CLEAN.mkdir(parents=True, exist_ok=True)
    (CLEAN / "de.json").write_text(json.dumps(clean, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
