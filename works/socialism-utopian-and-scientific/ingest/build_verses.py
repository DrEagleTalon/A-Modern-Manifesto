"""One-time ingest for Socialism: Utopian and Scientific (SUS).

German  MEW 19, pp. 177-228 (Dietz, Berlin 1962), via the mlwerke.de mirror: Engels's text in the
        fourth German edition (1891), Marx's preface to the French edition of 1880 (MEW's German
        translation of Marx's French) and Engels's preface to the first German edition (1882).
English Edward Aveling's authorised translation (London 1892, with Engels's special introduction,
        which Engels wrote in English), in the Charles H. Kerr reprint of 1908 as transcribed by
        Project Gutenberg (ebook 39257). Public domain.

Sections:
  P1880  Marx's preface to the French edition. German only (MEW translation of the French).
  P1882  Engels's preface to the first German edition. German only: Aveling did not translate it.
  P1892  Engels's special introduction to the English edition, written in English. The English
         sets the verses; the German column is empty until MEW 22's translation is added.
  I II III  Engels's three chapters, German anchor, Aveling aligned sentence by sentence.
Engels's footnotes are <section>.N<n> as in MEW. One note exists only in the English (Aveling's
"Note, l. c., p. 70." in chapter I) and is I.E1, following the Manifesto's E1.

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
from align import strip as align_strip  # noqa: E402
from mew import parse_mew as _parse_mew  # noqa: E402
from versify import P, attach_apparatus, build_section, dump, finalise, note_verses  # noqa: E402

RAW = WORK / "sources" / "raw"
CLEAN = WORK / "sources" / "clean"

# Local to this ingest; the shared rules in scripts/lib are not changed.
# "2200 Millionen Pfd. St." (III.N5) and "Frankfurt a. M." (P1892.N2) stay inside their sentences.
segment.ABBR["de"] = segment.ABBR["de"] | {"Pfd"}
segment.ABBR["en"] = segment.ABBR["en"] | {"a"}

TRAIL_MARK = re.compile(r"(?:\s*\[\[[A-Z]\d+\]\])+$")


def _split(text, lang):
    """The shared splitter, plus repairs kept local to this work:
    - when a page marker follows an ordinal or abbreviation ("seit dem 15. [[S212]] Jahrhundert") the
      abbreviation check does not see it and cuts the sentence; re-join those pieces;
    - never cut inside a square bracket, and hang a bracketed MEW reference ("[Siehe: ...]") on the
      sentence it follows instead of starting the next sentence with it;
    - places where a sentence ends on an abbreviation and the splitter misses it (EN_BREAKS, DE_BREAKS)."""
    out = []
    for s in segment.split_sentences(text, lang):
        if out and TRAIL_MARK.search(out[-1]):
            prev = TRAIL_MARK.sub("", out[-1]).rstrip()
            if prev.endswith(".") and not segment._is_boundary(prev, s, lang):
                out[-1] = out[-1] + " " + s
                continue
        if out and (NO_BREAK.search(out[-1]) or _open_bracket(out[-1])):
            out[-1] = out[-1] + " " + s
            continue
        out.append(s)
    fixed = []
    for s in out:
        m = re.match(r"^(\[(?!\[)[^\]]*\])\s*(.*)$", s)
        if fixed and m and lang == "de":
            fixed[-1] = fixed[-1] + " " + m.group(1)
            if m.group(2):
                fixed.append(m.group(2))
        else:
            fixed.append(s)
    for b in (EN_BREAKS if lang == "en" else DE_BREAKS):
        fixed = [x for s in fixed for x in ([s[:s.index(b) + len(b)].strip(), s[s.index(b) + len(b):].strip()] if b in s else [s])]
    return fixed


def _open_bracket(s):
    s = re.sub(r"\[\[[A-Z]\d+\]\]", "", s)
    return s.count("[") > s.count("]")


EN_BREAKS = ["special causes, effects, etc.", "1840, p. 535.]"]
# German sentence ends the splitter cannot see because the last word is an abbreviation.
DE_BREAKS = ["die Frauen spannen Flachs, Wolle usw."]
# "300.000 Pfd.St. (6.000.000 M.) Gewinn": a closing bracket after an abbreviation counts as a sentence end.
# "Neue Rheinische Zeitung. Politisch-ökonomische Revue" is one title (P1880.5).
NO_BREAK = re.compile(r"\(6\.000\.000 M\.\)$|\"Neuen Rheinischen Zeitung\.$")
versify.split_sentences = _split


# Cognate anchors. The shared cost function anchors on names and numbers only; in Engels's prose many
# sentences share Latin-derived words (Dialektik/dialectic, Produktion/production, Metaphysiker/metaphysician)
# that pin the alignment down. Added here, for this work only.
def _cognates(s):
    s = align_strip(s).lower()
    s = s.translate(str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "ss", "k": "c", "z": "c"}))
    s = s.replace("ph", "f").replace("th", "t")
    return {w[:6] for w in re.findall(r"[a-z]{6,}", s)}


def _cost(A, B, ratio):
    base = _base_cost(A, B, ratio)

    def f(a_items, b_items):
        c = base(a_items, b_items)
        if a_items and b_items:
            shared = len(_cognates(" ".join(a_items)) & _cognates(" ".join(b_items)))
            c -= COGNATE_WEIGHT * min(shared, 6)
        return c
    return f


COGNATE_WEIGHT = 0.5
_base_cost = versify.cross_lang_cost
versify.cross_lang_cost = _cost

# Transcription errors in the mlwerke.de text (the MARX-EBOOKS/MLRAW copy has the same readings).
# Listed in SOURCES.md.
CORRECTIONS_DE = [
    ("großen ranzösischen Revolution", "großen französischen Revolution"),
    ("Schicht desselben, die, besitzende Bourgeoisie", "Schicht desselben, die besitzende Bourgeoisie"),
    ("sondern in, Veränderungen der Produktions-", "sondern in Veränderungen der Produktions-"),
    ("aus dem Überfluß selbst entspringt \".", "aus dem Überfluß selbst entspringt\"."),
    ("in der Gesellschaft- diese Tatsache", "in der Gesellschaft - diese Tatsache"),
    ("Aber \"der Oberfluß wird", "Aber \"der Überfluß wird"),
    ("mit der Welt nun erst gekommen.. (Hegel", "mit der Welt nun erst gekommen.\" (Hegel"),
]
USED = set()


def parse_mew(path, **kw):
    """parse_mew, then the CORRECTIONS, then re-join paragraphs that MEW breaks around a set-off quotation
    (a paragraph that ends mid-sentence, or one that starts in lower case, continues the one before)."""
    paras, notes, variants = _parse_mew(path, **kw)
    for p in paras:
        for a, b in CORRECTIONS_DE:
            if a in p["de"]:
                p["de"] = p["de"].replace(a, b)
                USED.add(a)
    for k, lines in notes.items():
        for i, t in enumerate(lines):
            for a, b in CORRECTIONS_DE:
                if a in t:
                    lines[i] = t = t.replace(a, b)
                    USED.add(a)
    out = []
    for p in paras:
        t = TRAIL_MARK.sub("", p["de"]).strip()
        if out and out[-1]["kind"] == "p" and p["kind"] == "p" and (
                not re.search(r"[.!?:\")]$", TRAIL_MARK.sub("", out[-1]["de"]).strip()) or re.match(r'^"?[a-zäöü]', t)):
            out[-1]["de"] = out[-1]["de"] + " " + p["de"]
        else:
            out.append(p)
    return out, notes, variants


SRC_DE = "MEW 19, S. 177-228 (Dietz, Berlin) via mlwerke.de; text of the fourth German edition (1891)"
SRC_EN = ("Edward Aveling's authorised translation (London 1892), Charles H. Kerr reprint (Chicago 1908), "
          "Project Gutenberg ebook 39257 (public domain)")

# Defects in the Gutenberg text, listed in SOURCES.md. Gutenberg writes the pound sign as "L".
CORRECTIONS_EN = [
    ("L300,000", "£300,000"),
    ("L2,200,000,000", "£2,200,000,000"),
    ("L6,100,000,000", "£6,100,000,000"),
    ("L8,500,000,000", "£8,500,000,000"),
    ("L22,750,000", "£22,750,000"),
]

# English footnote markers -> the German note they translate. Aveling's [3] has no German note.
EN_NOTE_MAP = {"1": ("I", "F1"), "2": ("I", "F2"), "3": ("I", "E1"),
               "4": ("III", "F1"), "5": ("III", "F2"), "6": ("III", "F3"), "7": ("III", "F4"), "8": ("III", "F5")}
# Variants in MEW 19 carry no edition label; the reading names the edition, so label it here.
VARIANT_EDITIONS = {"P1880": "1880 (Revue socialiste, signed by Lafargue)", "II": "1880 (French edition)",
                    "III": "1878 (Anti-Dühring)"}


# ---------------------------------------------------------------- English (Gutenberg plain text)

def gutenberg():
    t = (RAW / "en" / "gutenberg_39257.txt").read_text(encoding="ascii").replace("\r", "")
    for a, b in CORRECTIONS_EN:
        assert a in t, a
        t = t.replace(a, b)
    lines = t.split("\n")
    marks = [i for i, ln in enumerate(lines) if ln in ("INTRODUCTION", "FOOTNOTES:", "SOCIALISM", "I", "II", "III")]
    end = next(i for i, ln in enumerate(lines) if ln.strip().startswith("*       *") and i > marks[-1])
    names = [lines[i] for i in marks]
    assert names == ["INTRODUCTION", "FOOTNOTES:", "SOCIALISM", "I", "FOOTNOTES:", "II", "III", "FOOTNOTES:"], names
    cut = marks + [end]

    def paras(a, b):
        out, cur = [], []
        for ln in lines[a + 1:b] + [""]:
            if ln.strip():
                cur.append(ln)
                continue
            if cur:
                indented = cur[0].startswith("   ")
                text = re.sub(r"\s+", " ", " ".join(x.strip() for x in cur)).strip()
                text = text.replace("_", "")
                out.append({"text": text, "indented": indented})
                cur = []
        return out

    def notes(a, b):
        out, key = {}, None
        for p in paras(a, b):
            m = re.match(r"^\[([A-Z0-9])\] (.*)$", p["text"])
            if m:
                key = m.group(1)
                out[key] = [m.group(2)]
            else:
                out[key].append(p["text"])
        return out

    def body(ps):
        """Fold indented list items back into the paragraph they belong to (the summary in III)."""
        out = []
        for p in ps:
            if p["indented"] and out and re.match(r"^[A-D]\. ", p["text"]):
                out[-1] = out[-1] + " " + p["text"]
            else:
                out.append(p["text"])
        return out

    return {"P1892": body(paras(cut[0], cut[1])), "P1892.notes": notes(cut[1], cut[2]),
            "I": body(paras(cut[3], cut[4])), "I.notes": notes(cut[4], cut[5]),
            "II": body(paras(cut[5], cut[6])),
            "III": body(paras(cut[6], cut[7])), "III.notes": notes(cut[7], cut[8])}


def en_markers(text, sid):
    """[A]..[C] in the 1892 introduction become F1..F3 (Engels's English notes). In the chapters, Aveling's
    [1]..[8] become [[G<n>]] for a note that matches German note n (the German marker decides where the
    footnote is listed; see en_note_places) and [[E1]] for the note that exists only in the English."""
    def sub(m):
        k = m.group(1)
        if k.isalpha():
            return f" [[F{ord(k) - 64}]]"
        sec, mark = EN_NOTE_MAP[k]
        assert sec == sid, (k, sid)
        return f" [[E{mark[1:]}]]" if mark.startswith("E") else f" [[G{mark[1:]}]]"
    return re.sub(r"\[([A-C1-8])\]", sub, text)


def en_note_places(vs, sid):
    """Where Aveling puts a note marker on a different verse from MEW, say so in en_note."""
    for v in vs:
        for n in re.findall(r"\[\[G(\d+)\]\]", v["_en_raw"]):
            if f"[[F{n}]]" not in v["_de_raw"]:
                v["en_note"] = (v.get("en_note", "") + f" Aveling's 1892 English attaches note {sid}.N{n} here.").strip()


# ---------------------------------------------------------------- writing

def meta(section, title_de, title_en, author, date, anchor="de", src_de=SRC_DE, src_en=SRC_EN):
    return {"section": section, "title_original": title_de, "title_en": title_en, "author": author, "date": date,
            "original_language": anchor if section != "P1880" else "fr", "anchor_language": anchor,
            "source_original": src_de, "source_en": src_en}


def note_section(sid, nid, de_paras, en_paras, anchor="de"):
    if anchor == "de" and not en_paras:
        vs, _ = build_section("N", f"{sid}.N{nid}", "de", [P("note", t) for t in de_paras], [], single=True, para0_heading=False)
        return vs
    if anchor == "en":
        vs, _ = build_section("N", f"{sid}.{nid}", "en", [P("note", t) for t in en_paras], [], single=True, para0_heading=False)
        return vs
    return note_verses(f"{sid}.N{nid}", de_paras, en_paras)


# Places where the length-based alignment picks the wrong verse and the script can say which is right:
# (verse, verse it really belongs to, verse that should get the English it was given instead).
REGROUP = [
    # Aveling folds "So daß z.B. ..." into his sentence for I.16.9, so "Fourier, as we see" belongs to I.17.1
    ("I.16.10", "I.16.9", "I.17.1"),
]


def regroup(vs):
    by = {v["id"]: v for v in vs}
    for vid, head, nxt in REGROUP:
        if vid not in by:
            continue
        v, h, n = by[vid], by[head], by[nxt]
        if n.get("joined_to") != vid or n["en"]:
            print("regroup not needed:", vid)
            continue
        n["en"], n["_en_raw"] = v["en"], v["_en_raw"]
        for k in ("joined_to", "align", "review", "review_reason"):
            n.pop(k, None)
        v["en"], v["_en_raw"] = "", ""
        for k in ("align", "review", "review_reason"):
            v.pop(k, None)
        v["joined_to"] = head
        a, b = h.get("align", "1:1").split(":")
        h["align"] = f"{int(a) + 1}:{b}"
        h["review"] = True
        h["review_reason"] = f"{h['align'].split(':')[0]} de sentence(s) matched to {b} en sentence(s); regrouped by the ingest (see REGROUP)"


# English sentences the aligner hung on the wrong side of a verse boundary: (verse, next verse, sentence).
# The sentence moves from the end of the first verse to the start of the second, or back.
MOVE_EN = [
    ("I.5.3", "I.6.1", "One thing is common to all three."),
    ("III.10.8", "III.10.9", "The women spun flax, wool, and so forth."),
]


def move_en(vs):
    by = {v["id"]: v for v in vs}
    for a, b, sent in MOVE_EN:
        if a not in by:
            continue
        va, vb = by[a], by[b]
        if va["_en_raw"].rstrip().endswith(sent):
            va["_en_raw"] = va["_en_raw"].rstrip()[: -len(sent)].rstrip()
            vb["_en_raw"] = sent + " " + vb["_en_raw"]
        elif vb["_en_raw"].lstrip().startswith(sent):
            vb["_en_raw"] = vb["_en_raw"].lstrip()[len(sent):].lstrip()
            va["_en_raw"] = va["_en_raw"].rstrip() + " " + sent
        else:
            print("move not needed:", a)
            continue
        for v in (va, vb):
            v["en"] = versify.clean_text(v["_en_raw"])
            n_en = len(versify.para_sentences(v["en"], "en", v["kind"]))
            for k in ("align", "review", "review_reason"):
                v.pop(k, None)
            if n_en != 1:
                v["align"], v["review"] = f"1:{n_en}", True
                v["review_reason"] = f"1 de sentence(s) matched to {n_en} en sentence(s); regrouped by the ingest (see MOVE_EN)"


def label_variants(variants, sid):
    for v in variants.values():
        if not v["editions"]:
            v["editions"] = VARIANT_EDITIONS.get(sid, "")
    return variants


def flags(vs):
    return sum(1 for v in vs if v.get("review"))


def main():
    CLEAN.mkdir(parents=True, exist_ok=True)
    EN = gutenberg()
    total, nflags = 0, 0
    report = {}

    # ---------------- P1880: Marx's preface to the French edition (German only)
    de, notes, var = parse_mew(RAW / "de" / "me19_181.htm", signature_re=r"^(Karl Marx)$")
    label_variants(var, "P1880")
    A = [P("heading", "[Vorbemerkung zur französischen Ausgabe (1880)]")] + [P(p["kind"], p["de"]) for p in de]
    vs, _ = build_section("P1880", "P1880", "de", A, [], single=True)
    attach_apparatus(vs, var, "P1880.", {})
    vs = finalise(vs)
    vs[0]["en_note"] = "Title as given in MEW. No public-domain English of this preface is used."
    dump(WORK / "text" / "00-prefaces" / "1880.yaml",
         {**meta("P1880", A[0]["text"], "Preface to the French edition (1880), by Karl Marx", "Karl Marx", "1880-05-04/05",
                 src_de="MEW 19, S. 181-185 (Dietz, Berlin) via mlwerke.de; MEW's German translation of Marx's French, NOT an original",
                 src_en="None: no public-domain English translation")}, vs)
    total += len(vs)
    report["P1880"] = (len(vs), flags(vs))

    # ---------------- P1882: Engels's preface to the first German edition (German only)
    de, notes, var = parse_mew(RAW / "de" / "me19_186.htm")
    A = [P("heading", "Vorwort zur ersten Auflage [in deutscher Sprache (1882)]")] + [P(p["kind"], p["de"]) for p in de]
    vs, _ = build_section("P1882", "P1882", "de", A, [], single=True)
    attach_apparatus(vs, var, "P1882.", {})
    for nid, paras in notes.items():
        vs += note_section("P1882", nid, paras, [])
    vs = finalise(vs)
    dump(WORK / "text" / "00-prefaces" / "1882.yaml",
         meta("P1882", A[0]["text"], "Preface to the first German edition (1882)", "Friedrich Engels", "1882-09-21",
              src_en="None: Aveling's 1892 English does not include this preface"), vs)
    total += len(vs)
    report["P1882"] = (len(vs), flags(vs))

    # ---------------- P1892: Engels's special introduction, written in English
    paras = EN["P1892"]
    A = [P("heading", "Introduction [to the English edition of 1892]")]
    for t in paras:
        kind = "signature" if re.fullmatch(r"F\. ENGELS\.|April 20th, 1892\.", t) else "p"
        A.append(P(kind, en_markers(t, "P1892")))
    vs, _ = build_section("P1892", "P1892", "en", A, [], single=True)
    attach_apparatus(vs, {}, "P1892.", {})
    for k, paras in EN["P1892.notes"].items():
        vs += note_section("P1892", f"N{ord(k) - 64}", [], paras, anchor="en")
    vs = finalise(vs)
    dump(WORK / "text" / "00-prefaces" / "1892.yaml",
         meta("P1892", "", "Special Introduction to the English edition (1892)", "Friedrich Engels", "1892-04-20", anchor="en",
              src_de="None yet: Engels wrote this introduction in English. MEW 22's German translation can be added as a reference column",
              src_en=SRC_EN + "; Engels's own English"), vs)
    total += len(vs)
    report["P1892"] = (len(vs), flags(vs))

    # ---------------- I, II, III
    pages = [("I", "me19_189.htm"), ("II", "me19_202.htm"), ("III", "me19_210.htm")]
    titles_en = {"I": "I", "II": "II", "III": "III"}
    clean = {"en": EN, "de": {}}
    for i, (sid, fname) in enumerate(pages, start=1):
        de, notes, var = parse_mew(RAW / "de" / fname)
        label_variants(var, sid)
        clean["de"][sid] = {"paras": de, "notes": notes, "variants": var}
        A = [P("heading", sid)] + [P(p["kind"], p["de"]) for p in de]
        B = [P("heading", titles_en[sid])] + [P("p", en_markers(t, sid)) for t in EN[sid]]
        vs, _ = build_section(sid, sid, "de", A, B, flat=True)
        regroup(vs)
        move_en(vs)
        en_note_places(vs, sid)
        attach_apparatus(vs, var, f"{sid}.", {})
        en_notes = EN.get(f"{sid}.notes", {})
        by_de = {EN_NOTE_MAP[k][1]: v for k, v in en_notes.items()}
        for nid, paras in notes.items():
            if sid == "III" and nid == "5":
                paras = table_note(paras)
            en_paras = by_de.get(f"F{nid}", [])
            if sid == "III" and nid == "5":
                en_paras = [" ".join(en_paras[:4]), *en_paras[4:]]
            vs += note_section(sid, nid, paras, en_paras)
        if "E1" in by_de:
            ev, _ = build_section("N", f"{sid}.E1", "en", [P("note", t) for t in by_de["E1"]], [], single=True, para0_heading=False)
            for v in ev:
                v["en_note"] = "Aveling's 1892 English only; MEW has no note here"
            vs += ev
        vs = finalise(vs)
        dump(WORK / "text" / "01-socialism-utopian-and-scientific" / f"{i}-{sid.lower()}.yaml",
             meta(sid, sid, titles_en[sid], "Friedrich Engels", "1880-01/03; revised 1882 and 1891"), vs)
        total += len(vs)
        report[sid] = (len(vs), flags(vs))
    (CLEAN / "de.json").write_text(json.dumps(clean["de"], ensure_ascii=False, indent=1), encoding="utf-8")
    (CLEAN / "en.json").write_text(json.dumps(clean["en"], ensure_ascii=False, indent=1), encoding="utf-8")
    assert USED == {a for a, _ in CORRECTIONS_DE}, {a for a, _ in CORRECTIONS_DE} - USED
    for k, (n, f) in report.items():
        print(k, n, "verses", f, "to review")
        nflags += f
    print("total", total, "verses", nflags, "to review")


def table_note(paras):
    """MEW sets Giffen's figures as a table (one cell per paragraph). Keep each row as one sentence."""
    head, rest = paras[0], paras[1:]
    cells = [c for c in rest[:-1]]
    rows = [" ".join(cells[k:k + 4]) + "." for k in range(0, len(cells), 4)]
    assert len(rows) == 3 and all(r.split()[0] in ("1814", "1865", "1875") for r in rows), rows
    return [head + " " + " ".join(rows), rest[-1]]


if __name__ == "__main__":
    main()
