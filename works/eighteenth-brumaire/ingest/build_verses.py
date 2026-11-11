"""One-time ingest for The Eighteenth Brumaire of Louis Bonaparte (EB).

German  MEW 8, pp. 115-207 (Dietz, Berlin 1960), via the mlwerke.de mirror: Marx's text of the second
        edition (Hamburg 1869), with a few stylistic changes from the third edition (1885). Marx's preface
        to the second edition (MEW 16, pp. 358-360) and Engels's preface to the third edition (MEW 21,
        pp. 248-249), from the same mirror.
English Daniel De Leon's translation (New York Labor News, 1898), as transcribed by Project Gutenberg
        (ebook 1346, ASCII). Public domain. De Leon's own 1897 preface is not part of Marx's work and is
        left out; his inline glosses ([#n ...]) are kept as en_note on the verse they sit in.

Sections:
  P1869  Marx's preface to the second edition. German only: De Leon did not translate it.
  P1885  Engels's preface to the third edition. German only.
  I to VII  Marx's seven chapters, German anchor, De Leon aligned sentence by sentence (flat=True:
            De Leon re-paragraphs freely).
Marx's footnotes are <section>.N<n> as in MEW (P1869.N1, VII.N1 to VII.N4). For the four notes in VII
De Leon gives his own version of the same note, which fills the English column of the note verses.

Run once. After the lock file exists the YAML in text/ is the source of truth.
"""
import json
import re
import sys
import tempfile
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
segment.ABBR["de"] = segment.ABBR["de"] | {"Komp", "frs", "Abg"}
segment.ABBR["en"] = segment.ABBR["en"] | {"Gen", "Col", "Ex", "Jr"}

TRAIL_MARK = re.compile(r"(?:\s*\[\[[A-Z]\d+\]\])+$")


# ---------------------------------------------------------------- MEW pages

# Markup defects in the mlwerke.de pages, repaired before parsing (the raw files stay untouched):
HTML_FIXES = [
    # VI: one item of the closing schema ("Dritte Periode") has no <P>, so it would join the item before
    ("me08_176.htm", "</DIR>\n\n<LEM><EM>Dritte Periode", "</DIR>\n\n<P><LEM><EM>Dritte Periode"),
]


def _prepare(name, tmp):
    """Copy a MEW page with its markup normalised so the shared parse_mew reads it:
    - MEW 8 and 16 link Marx's footnotes as #M<n> with "(n)", the form parse_mew expects for footnotes is #F<n>;
    - page anchors carry <STRONG> inside or around them, which hides them from the hyphen re-joining;
    - emphasis tags are dropped (the reader shows plain text), so that "G<EM>eschichte" and
      "Februar<EM>-Regierung" stay whole words (and a stray tag in "4. Mai 1</I>848" goes)."""
    data = (RAW / "de" / name).read_bytes()
    try:
        t = data.decode("utf-8")
    except UnicodeDecodeError:
        t = data.decode("latin-1")
    # pp. 115-148 are Windows-1252: 0x96 is a dash (the UTF-8 pages write " - ") and 0x92 an apostrophe
    t = t.replace("\x96", "-").replace("\x92", "'").replace("\r", "")
    for f, a, b in HTML_FIXES:
        if f == name:
            assert a in t, (name, a)
            t = t.replace(a, b)
    t = re.sub(r'HREF="#M(\d+)">\((\d+)\)', r'HREF="#F\1">(\2)', t, flags=re.I)
    t = re.sub(r'NAME="M(\d+)"', r'NAME="F\1"', t, flags=re.I)
    t = re.sub(r'<A NAME="S\d+">\s*(?:<STRONG>)?\s*&lt;(\d+)&gt;\s*(?:</STRONG>)?\s*</A>(?:\s*</STRONG>)?', r"&lt;\1&gt;", t, flags=re.I)
    t = re.sub(r'<A NAME="S\d+">\s*</A>\s*<STRONG>\s*&lt;(\d+)&gt;\s*</STRONG>', r"&lt;\1&gt;", t, flags=re.I)
    t = re.sub(r"&lt;<STRONG>(\d+)&gt;", r"&lt;\1&gt;", t)
    t = re.sub(r"</?(?:EM|LEM|I|B)>", "", t, flags=re.I)
    t = re.sub(r"</?STRONG>", "", t, flags=re.I)
    # a word broken across a page marker: "Ordnungs- <138> partei" -> "<138> Ordnungspartei".
    # "St-Jean- <163> d'Angely" keeps its hyphen; "Drang- und" style pairs never cross a page here.
    t = re.sub(r"(\w+)-\s*&lt;(\d+)&gt;\s*(d')", r"&lt;\2&gt; \1-\3", t)
    t = re.sub(r"(\w+)-\s*&lt;(\d+)&gt;\s*((?:[a-zäöüß]|&[a-z]+;)\w*)", r"&lt;\2&gt; \1\3", t)
    p = Path(tmp) / name
    p.write_text(t, encoding="utf-8")
    return p


# Transcription errors in the mlwerke.de text. Listed in SOURCES.md.
CORRECTIONS_DE = [
    ("und sei Körper sich in die Nation auflöste", "und sein Körper sich in die Nation auflöste"),
    ("protestierte in Teil der französischen Bauern", "protestierte ein Teil der französischen Bauern"),
    ("\"C est le triomphe", "\"C'est le triomphe"),
    ("Gesellschaft vom 10! Dezember.", "Gesellschaft vom 10. Dezember!"),
    ("auf den Berg Sinai, führten", "auf den Berg Sinai führten"),
    ("die neuen Weltgeschichtsszene aufzuführen", "die neue Weltgeschichtsszene aufzuführen"),
    ("coup d'état <Staatstreichs>", "coup d'état <Staatsstreichs>"),
    ("dieser bürgerlichen Ordnung ist die Mittelklasse, Er weiß", "dieser bürgerlichen Ordnung ist die Mittelklasse. Er weiß"),
    ("an die Regentschaft oder Ludwig XV, zu erinnern", "an die Regentschaft oder Ludwig XV. zu erinnern"),
    # P1869: the preface to the 1869 edition is dated 1859 in the mirror; MEW 16 has 23 June 1869
    ("London, 23. Juni 1859", "London, 23. Juni 1869"),
]
USED = set()


def parse_mew(name, tmp, **kw):
    """parse_mew on the prepared page, then the CORRECTIONS, then re-join the paragraphs listed in JOIN_AFTER."""
    paras, notes, variants = _parse_mew(_prepare(name, tmp), **kw)
    for p in paras:
        for a, b in CORRECTIONS_DE:
            if a in p["de"]:
                p["de"] = p["de"].replace(a, b)
                USED.add(a)
    out = []
    for p in paras:
        if out and any(TRAIL_MARK.sub("", out[-1]["de"]).strip().endswith(j) for j in JOIN_AFTER):
            out[-1]["de"] = out[-1]["de"] + " " + p["de"]
            USED_JOIN.add(next(j for j in JOIN_AFTER if TRAIL_MARK.sub("", out[-1]["de"]).find(j) >= 0))
        else:
            out.append(p)
    return out, notes, variants


# Paragraphs that MEW breaks around a set-off quotation, re-joined to the sentence they finish.
JOIN_AFTER = ["und die Verhältnisse selbst rufen"]
USED_JOIN = set()


# VII: MEW prints the lines Marx cut in 1869 as an editorial paragraph in angle brackets. They are not part
# of the base text, so they become a variant on the last verse of the paragraph they once ended.
EDITION_1852 = re.compile(r"^<In der Erstausgabe New York 1852, endet dieser Absatz mit folgenden Zeilen, die 1869 von Marx weggelassen wurden: (.*?)\s*>$")


def take_1852(paras):
    out, cut = [], None
    for p in paras:
        m = EDITION_1852.match(p["de"])
        if m:
            cut = (len(out), m.group(1).strip())
            continue
        out.append(p)
    return out, cut


# ---------------------------------------------------------------- English (Gutenberg plain text)

# Defects in the Gutenberg text, listed in SOURCES.md.
CORRECTIONS_EN = [
    ("the \"Mountain\" of 1793-05,", "the \"Mountain\" of 1793-95,"),
    ("revolution of' February 24th", "revolution of February 24th"),
    ("the Executive power and\nthe royalists I need not", "the Executive power and\nthe royalists. I need not"),
    ("the \"Society of December 10\" This society", "the \"Society of December 10.\" This society"),
    ("an immediate\nexplanation Changarnier rises", "an immediate\nexplanation. Changarnier rises"),
    ("regular astrologers The National Assembly", "regular astrologers. The National Assembly"),
    ("His own Prime Minister. Odillon Barrot,", "His own Prime Minister, Odillon Barrot,"),
    ("the casting\nvote It now", "the casting\nvote. It now"),
    ("against the house\nof Mr. proletariat.", "against the\nproletariat."),
    ("\"Fuge, Tace, Oniesce!\"", "\"Fuge, Tace, Quiesce!\""),
    ("were Messieurs. Bourgeois & Small-Trader.", "were Messieurs Bourgeois & Small-Trader."),
    ("\"C'est Ic triomphe complet et definitif du Socialism!\"'", "\"C'est le triomphe complet et definitif du Socialism!\""),
    ("an individual turns I up,", "an individual turns up,"),
]

# De Leon's glosses in VII that render Marx's own footnotes VII.N1 to VII.N4.
DL_FOR_MARX = {("VII", "10"): "1", ("VII", "11"): "2", ("VII", "13"): "3", ("VII", "15"): "4"}
CHAPTERS = ["I", "II", "III", "IV", "V", "VI", "VII"]


def gutenberg():
    t = (RAW / "en" / "gutenberg_1346.txt").read_text(encoding="ascii").replace("\r", "")
    for a, b in CORRECTIONS_EN:
        assert a in t, a
        t = t.replace(a, b)
    lines = t.split("\n")
    marks = [i for i, ln in enumerate(lines) if ln in CHAPTERS]
    assert [lines[i] for i in marks] == CHAPTERS
    end = next(i for i, ln in enumerate(lines) if ln.startswith("End of the Project Gutenberg EBook"))
    cut = marks + [end]
    out, glosses = {}, []
    for k, sid in enumerate(CHAPTERS):
        paras, cur = [], []
        for ln in lines[cut[k] + 1:cut[k + 1]] + [""]:
            if ln.strip():
                cur.append(ln.strip())
            elif cur:
                paras.append(re.sub(r"\s+", " ", " ".join(cur)).strip())
                cur = []
        notes = {}

        def sub(m):
            n, body = m.group(1), m.group(2).strip()
            if (sid, n) in DL_FOR_MARX:
                notes[DL_FOR_MARX[(sid, n)]] = body
                return f" [[G{DL_FOR_MARX[(sid, n)]}]]"
            glosses.append({"section": sid, "n": n, "text": body})
            return f" [[D{len(glosses)}]]"
        paras = [re.sub(r"\s*\[#(\d+) ([^\]]*)\]", sub, p) for p in paras]
        out[sid] = {"paras": paras, "notes": notes}
    return out, glosses


def place_glosses(vs, glosses):
    """De Leon's inline glosses become en_note on the verse whose English holds them."""
    for v in vs:
        for n in re.findall(r"\[\[D(\d+)\]\]", v["_en_raw"]):
            g = glosses[int(n) - 1]
            v["en_note"] = (v.get("en_note", "") + f" De Leon's note [{g['n']}]: {g['text']}").strip()
            g["placed"] = v["id"]
        for n in re.findall(r"\[\[G(\d+)\]\]", v["_en_raw"]):
            if f"[[F{n}]]" not in v["_de_raw"]:
                v["en_note"] = (v.get("en_note", "") + f" De Leon attaches note {v['id'].split('.')[0]}.N{n} here.").strip()


# ---------------------------------------------------------------- alignment helpers

# Cognate anchors, as in the SUS ingest: Latin-derived words shared by Marx's German and De Leon's English
# (Bourgeoisie/bourgeoisie, Konstitution/Constitution, Legitimisten/Legitimists) pin the alignment down.
def _cognates(s):
    s = align_strip(s).lower()
    s = s.translate(str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "ss", "k": "c", "z": "c", "é": "e", "è": "e"}))
    s = s.replace("ph", "f").replace("th", "t")
    return {w[:6] for w in re.findall(r"[a-z]{6,}", s)}


COGNATE_WEIGHT = 0.5
_base_cost = versify.cross_lang_cost


def _cost(A, B, ratio):
    base = _base_cost(A, B, ratio)

    def f(a_items, b_items):
        c = base(a_items, b_items)
        if a_items and b_items:
            shared = len(_cognates(" ".join(a_items)) & _cognates(" ".join(b_items)))
            c -= COGNATE_WEIGHT * min(shared, 6)
        return c
    return f


versify.cross_lang_cost = _cost


def _split(text, lang):
    """The shared splitter, plus repairs kept local to this work:
    - when a page marker follows an ordinal or abbreviation ("am 2. [[S170]] Dezember") the abbreviation
      check does not see it and cuts the sentence; re-join those pieces;
    - never cut inside MEW's angle-bracket translations (<"Es lebe Napoleon! Es leben die Würste!">);
    - the pairs in NO_BREAK stay together (a repeated cry, a Latin tag with its German gloss);
    - a short bracketed reference at the start of a piece ("(A.a.O., § 9.)", "(Section 9.)") hangs on the
      sentence it cites instead of opening the next one;
    - a list letter ("a.", "b." in De Leon's schema at the end of VI) stays with the item it introduces."""
    out = []
    for s in segment.split_sentences(text, lang):
        if out and TRAIL_MARK.search(out[-1]):
            prev = TRAIL_MARK.sub("", out[-1]).rstrip()
            if prev.endswith(".") and not segment._is_boundary(prev, s, lang):
                out[-1] = out[-1] + " " + s
                continue
        if out and (_open_angle(out[-1]) or any(re.search(a, out[-1]) and re.match(b, s) for a, b in NO_BREAK)):
            out[-1] = out[-1] + " " + s
            continue
        m = re.match(r"^(\([^()]{1,60}\))\s*(.*)$", s)
        if out and m:
            out[-1] = out[-1] + " " + m.group(1)
            if m.group(2):
                out.append(m.group(2))
            continue
        out.append(s)
    merged = []
    for s in out:
        if merged and re.fullmatch(r"[a-d]\.", merged[-1]):
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)
    return merged


def _open_angle(s):
    s = re.sub(r"\[\[[A-Z]\d+\]\]", "", s)
    return s.count("<") > s.count(">")


NO_BREAK = [
    (r"Henri V!$", r"Henri V!"),
    (r"Henry V\.!$", r"Henry V!"),
    (r"\"Fuge, tace, quisce!$", r"Fliehe"),
    (r"\"Vive Napol(?:é|e)on!$", r"Vivent les saucissons"),
]


versify.split_sentences = _split


# Places where the length-based alignment slips by a sentence and the script can say what is right. Each
# entry is a run of verses (first, last) and the verses in it that start an English group, with the number of
# English sentences each takes; the other verses in the run join the head before them. The English text is
# only redistributed, never changed: the run must hold exactly that many English sentences.
REALIGN = [
    # De Leon ends his sentence with "Three main periods are unmistakable:", which opens Marx's next paragraph
    ("I.12.1", "I.13.1", [("I.12.1", 1), ("I.13.1", 2)]),
    # De Leon's one sentence from "So, on the occasion of his expedition against Strassburg" covers V.4.11-14
    ("V.4.10", "V.4.14", [("V.4.10", 1), ("V.4.11", 1)]),
    # one English sentence too late from "Thus the influence" to "The bulk of the Mountain"
    ("III.14.9", "III.16.5", [("III.14.9", 1), ("III.14.10", 1), ("III.15.1", 1), ("III.16.1", 1)]),
    # "All the same, the revolution is thoroughgoing" is VII.9.1, not VII.9.2
    ("VII.8.6", "VII.9.4", [("VII.8.6", 1), ("VII.9.1", 1), ("VII.9.2", 1), ("VII.9.3", 1)]),
    # "Along with the mortgage" (VII.24.1) to "A strong government, and heavy taxes are identical" (VII.24.3)
    ("VII.23.17", "VII.24.9", [("VII.23.17", 1), ("VII.24.1", 1), ("VII.24.2", 1), ("VII.24.3", 1), ("VII.24.4", 1)]),
]
USED_REALIGN = set()


def realign(vs):
    ids = [v["id"] for v in vs]
    for first, last, heads in REALIGN:
        if first not in ids:
            continue
        USED_REALIGN.add(first)
        group = vs[ids.index(first):ids.index(last) + 1]
        sents = [x for v in group if v["_en_raw"] for x in versify.para_sentences(v["_en_raw"], "en", v["kind"])]
        counts = dict(heads)
        assert group[0]["id"] in counts and sum(counts.values()) == len(sents), (first, len(sents), sents)
        k, size, cur = 0, {}, None
        for v in group:
            for f in ("joined_to", "align", "review", "review_reason"):
                v.pop(f, None)
            if v["id"] in counts:
                cur = v
                v["_en_raw"] = " ".join(sents[k:k + counts[v["id"]]])
                k += counts[v["id"]]
                size[v["id"]] = 1
            else:
                v["joined_to"], v["_en_raw"] = cur["id"], ""
                size[cur["id"]] += 1
            v["en"] = versify.clean_text(v["_en_raw"])
        for v in group:
            if v["id"] in counts and (size[v["id"]], counts[v["id"]]) != (1, 1):
                v["align"], v["review"] = f"{size[v['id']]}:{counts[v['id']]}", True
                v["review_reason"] = f"{size[v['id']]} de sentence(s) matched to {counts[v['id']]} en sentence(s); regrouped by the ingest (see REALIGN)"


# ---------------------------------------------------------------- writing

SRC_DE = "MEW 8, S. 111-207 (Dietz, Berlin 1960) via mlwerke.de; text of the second edition (1869)"
SRC_EN = "Daniel De Leon's translation (New York Labor News, 1898), Project Gutenberg ebook 1346 (public domain)"


def meta(section, title_de, title_en, author, date, src_de=SRC_DE, src_en=SRC_EN):
    return {"section": section, "title_original": title_de, "title_en": title_en, "author": author, "date": date,
            "original_language": "de", "anchor_language": "de", "source_original": src_de, "source_en": src_en}


def flags(vs):
    return sum(1 for v in vs if v.get("review"))


def main():
    CLEAN.mkdir(parents=True, exist_ok=True)
    EN, glosses = gutenberg()
    total, report, clean_de = 0, {}, {}
    with tempfile.TemporaryDirectory() as tmp:
        # ---------------- P1869: Marx's preface to the second edition (German only)
        de, notes, var = parse_mew("me16_358.htm", tmp, signature_re=r"^(London, |Karl Marx$)")
        clean_de["P1869"] = {"paras": de, "notes": notes}
        A = [P("heading", "Vorwort [zur zweiten Ausgabe (1869)]")] + [P(p["kind"], p["de"]) for p in de]
        vs, _ = build_section("P1869", "P1869", "de", A, [], single=True)
        attach_apparatus(vs, var, "P1869.", {})
        for nid, paras in notes.items():
            nv, _ = build_section("N", f"P1869.N{nid}", "de", [P("note", t) for t in paras], [], single=True, para0_heading=False)
            attach_apparatus(nv, {}, "", {})
            vs += nv
        vs = finalise(vs)
        vs[0]["en_note"] = "No public-domain English of this preface is used; De Leon's 1898 translation leaves it out."
        dump(WORK / "text" / "00-prefaces" / "1869.yaml",
             meta("P1869", A[0]["text"], "Preface to the second edition (1869)", "Karl Marx", "1869-06-23",
                  src_de="MEW 16, S. 358-360 (Dietz, Berlin 1962) via mlwerke.de; from the second edition, Hamburg 1869",
                  src_en="None: De Leon's 1898 English does not include this preface"), vs)
        total += len(vs)
        report["P1869"] = (len(vs), flags(vs))

        # ---------------- P1885: Engels's preface to the third edition (German only)
        de, notes, var = parse_mew("me21_248.htm", tmp, signature_re=r"^F\. E\.$")
        clean_de["P1885"] = {"paras": de, "notes": notes}
        A = [P("heading", "Vorrede zur dritten Auflage [(1885)]")] + [P(p["kind"], p["de"]) for p in de]
        vs, _ = build_section("P1885", "P1885", "de", A, [], single=True)
        attach_apparatus(vs, var, "P1885.", {})
        vs = finalise(vs)
        vs[0]["en_note"] = "No public-domain English of this preface is used; De Leon's 1898 translation leaves it out."
        dump(WORK / "text" / "00-prefaces" / "1885.yaml",
             meta("P1885", A[0]["text"], "Preface to the third edition (1885)", "Friedrich Engels", "1885",
                  src_de="MEW 21, S. 248-249 (Dietz, Berlin 1962) via mlwerke.de; from the third edition, Hamburg 1885",
                  src_en="None: De Leon's 1898 English does not include this preface"), vs)
        total += len(vs)
        report["P1885"] = (len(vs), flags(vs))

        # ---------------- I to VII
        pages = ["me08_115.htm", "me08_124.htm", "me08_135.htm", "me08_149.htm", "me08_159.htm", "me08_176.htm", "me08_194.htm"]
        for i, (sid, fname) in enumerate(zip(CHAPTERS, pages), start=1):
            de, notes, var = parse_mew(fname, tmp)
            de, cut1852 = take_1852(de)
            clean_de[sid] = {"paras": de, "notes": notes, "cut_1852": cut1852}
            A = [P("heading", sid)] + [P(p["kind"], p["de"]) for p in de]
            B = [P("heading", sid)] + [P("p", t) for t in EN[sid]["paras"]]
            vs, _ = build_section(sid, sid, "de", A, B, flat=True)
            realign(vs)
            place_glosses(vs, glosses)
            if cut1852:
                pnum, text = cut1852
                last = [v for v in vs if v["id"].startswith(f"{sid}.{pnum}.")][-1]
                words = versify.clean_text(last["_de_raw"]).split()[-4:]
                last["de_variants"] = [{"ref": "1852", "editions": "1852 (first edition, New York)",
                                        "reading": f"the paragraph goes on: {text}",
                                        "base_text": "… " + " ".join(words) + " ‸"}]
            attach_apparatus(vs, var, f"{sid}.", {})
            for nid, paras in notes.items():
                en_note = EN[sid]["notes"].get(nid)
                vs += note_verses(f"{sid}.N{nid}", paras, [en_note] if en_note else [])
            vs = finalise(vs)
            dump(WORK / "text" / "01-eighteenth-brumaire" / f"{i}-{sid.lower()}.yaml",
                 meta(sid, sid, sid, "Karl Marx", "1851-12/1852-03; revised 1869"), vs)
            total += len(vs)
            report[sid] = (len(vs), flags(vs))
    unplaced = [g for g in glosses if "placed" not in g]
    assert not unplaced, unplaced
    assert USED == {a for a, _ in CORRECTIONS_DE}, {a for a, _ in CORRECTIONS_DE} - USED
    assert USED_JOIN == set(JOIN_AFTER), set(JOIN_AFTER) - USED_JOIN
    assert USED_REALIGN == {r[0] for r in REALIGN}, {r[0] for r in REALIGN} - USED_REALIGN
    (CLEAN / "de.json").write_text(json.dumps(clean_de, ensure_ascii=False, indent=1), encoding="utf-8")
    (CLEAN / "en.json").write_text(json.dumps({"chapters": EN, "de_leon_notes": glosses}, ensure_ascii=False, indent=1), encoding="utf-8")
    nflags = 0
    for k, (n, f) in report.items():
        print(k, n, "verses", f, "to review")
        nflags += f
    print("total", total, "verses", nflags, "to review")


if __name__ == "__main__":
    main()
