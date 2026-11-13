"""One-time ingest for The Condition of the Working Class in England (CWC).

German  MEW 2, pp. 225-506 (Dietz, Berlin 1972), via the mlwerke.de mirror: the text of the first edition
        (Leipzig 1845), with the readings of the second edition (Stuttgart 1892) and MEW's corrections given
        in angle brackets on the page; these become the `variants` of the verse they sit in. Engels's footnotes
        ("Anmerkungen F. E."), including those he added in 1887 and 1892, are <section>.N<n> as in MEW.
English Florence Kelley Wischnewetzky's translation (New York 1887), in the London edition of March 1892
        (Swan Sonnenschein) with Engels's English preface of 1892, as transcribed by Project Gutenberg
        (ebook 17306, ASCII) from the 1943 Allen & Unwin reprint. Public domain.

Sections (MEW does not number the chapters; the numbers here follow the order of the book):
  P1892  Engels's preface to the English edition of 1892, written in English. No German column: the German
         preface of 1892 (MEW 22) is a different text and is not in the sources yet.
  D      the dedication "To the Working-Classes of Great Britain", written in English in 1845. Only MEW's
         German translation is in the sources, so the German column holds that and the English is empty.
  P1845  Engels's preface of 1845. German only: the 1892 English edition leaves it out.
  E      the Introduction.
  I to XI  the eleven chapters, from "The Industrial Proletariat" to "The Attitude of the Bourgeoisie".
Paragraph 0 of each section is its heading.

The mlwerke.de pages of MEW 2 use a different markup from the volumes the shared reader was written for
(page numbers as <306>, notes linked as #O<n>, editorial matter in angle brackets), so this ingest has its
own reader for them. scripts/lib is not changed.

All sections with both languages are aligned sentence by sentence across paragraph breaks (flat=True).

Run once. After the lock file exists the YAML in text/ is the source of truth.
"""
import functools
import html as htmllib
import json
import math
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
REPO = WORK.parents[1]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
import segment  # noqa: E402
import versify  # noqa: E402
from align import strip as align_strip  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402
from versify import P, attach_apparatus, build_section, dump, finalise  # noqa: E402

RAW = WORK / "sources" / "raw"
CLEAN = WORK / "sources" / "clean"

# Local to this ingest; the shared rules in scripts/lib are not changed.
segment.ABBR["de"] = segment.ABBR["de"] | {"sog", "Kap", "Anm", "ff", "evid", "Guard", "Rep", "Aug", "Sept", "Okt", "Nov",
                                           "Dez", "Jan", "Febr", "inkl", "Pfd", "sh", "d", "Fahr", "Insp", "Fabrikinsp",
                                           "Ges", "ebd", "Esq", "Hon", "Sir", "Rev", "Thl", "Comm", "App", "Bd", "a", "O",
                                           "Grafsch", "Ld", "jun", "sen", "Co", "St", "Tab", "Kapt", "Lieut", "Mrs",
                                           "Vgl", "c", "vol", "chapt", "chap", "Prin", "Princ", "Popul", "Manuf", "Philos",
                                           "Engl", "Manag", "Reg", "Gen", "Pop", "pag", "Child", "Ch", "Empl",
                                           "Inq", "Fact", "Comm", "Rept", "Commiss", "Factor", "Rd"}
segment.ABBR["en"] = segment.ABBR["en"] | {"Ibid", "ch", "chap", "Chap", "ff", "Sec", "Esq", "Hon", "Rev", "Rep", "App",
                                           "evid", "loc", "cit", "Co", "Jun", "Sen", "s", "d", "lbs", "Lieut",
                                           "Capt", "Col", "Gen", "Messrs", "Bart", "pp", "Ld", "Bros", "Rd", "MR"}

TRAIL_MARK = re.compile(r"(?:\s*\[\[[A-Z]\d+\]\])+$")
MARKS = re.compile(r"\s*\[\[[A-Z]\d+\]\]")

# ---------------------------------------------------------------- German (MEW 2 pages)

PAGES = {"D": "me02_229.htm", "P1845": "me02_232.htm", "E": "me02_237.htm", "I": "me02_253.htm", "II": "me02_256.htm",
         "III": "me02_306.htm", "IV": "me02_320.htm", "V": "me02_324.htm", "VI": "me02_360.htm", "VII": "me02_408.htm",
         "VIII": "me02_430.htm", "IX": "me02_456.htm", "X": "me02_473.htm", "XI": "me02_486.htm"}

# Markup defects in the mlwerke.de pages, repaired in memory before parsing (the raw files stay untouched).
HTML_FIXES = [
    # IV: the anchor of note 1 is missing, so the note would be lost
    ("me02_320.htm", '<P>(1)</A> <EM>Archibald Alison', '<P><A NAME="O1">(1)</A> <EM>Archibald Alison'),
    # VIII: the link to note 5 is broken by a misplaced SMALL tag
    ("me02_430.htm", '<A HREF="#O5"><SMALL></A><A NAME="Z5">(5)</A></SMALL>', '<A HREF="#O5">(5)</A>'),
    # III: the anchor for p. 314 lacks its closing quote mark, which swallows the page number
    ("me02_306.htm", '<A NAME="S314><STRONG>', '<A NAME="S314"><STRONG>'),
    # VIII: the page between 442 and 444 is numbered 277
    ("me02_430.htm", "feuerten sie <STRONG>&lt;277&gt;</STRONG> auf diese", "feuerten sie <STRONG>&lt;443&gt;</STRONG> auf diese"),
    # XI: a stray comma after the quotation from the Times would join it to the next paragraph
    ("me02_486.htm", 'in acht nehmen!" ,</P>', 'in acht nehmen!"</P>'),
]
USED_HTML = set()

# Words that MEW breaks across a page number without a hyphen ("Überflüs <319> sigen"); the page marker is
# moved in front of the re-joined word. Each entry is (page, first half, second half).
SPLIT_WORDS = [("319", '"Überflüs', 'sigen"')]
USED_SPLIT = set()

# Transcription errors in the mlwerke.de text. Listed in SOURCES.md.
CORRECTIONS_DE = [
    # MEW's own misprints in two editorial notes: the second edition is of 1892
    ("(1845 und 1882) irrtümlich 77", "(1845 und 1892) irrtümlich 77"),
    ("(1845 und 1882) irrtümlich 225", "(1845 und 1892) irrtümlich 225"),
    ("(1845) und (1892) irrtumlich: 1835", "(1845) und (1892) irrtümlich: 1835"),
    ("Armengesetz- Novelle", "Armengesetz-Novelle"),
    # X.8.14: the editorial completion of "Northern Star" ends in "l" for "]", which leaves a bracket open
    ('"N[orthern] S[tarl"', '"N[orthern] S[tar]"'),
    # letters misread in the transcription (found by a spelling check of rare words and by reading)
    ("die Spekulation steiger die Preise noch m hr", "die Spekulation steigert die Preise noch mehr"),
    ("als wären ein pur Tausend Millionen", "als wären ein paar Tausend Millionen"),
    ("ein gewöhnliches Hemd 1 2/2 Pence", "ein gewöhnliches Hemd 1 1/2 Pence"),
    ("deren Fußhoden mindestens", "deren Fußboden mindestens"),
    ("täglich dingender", "täglich dringender"),
    ("Arbeiterdistrikten agiterte", "Arbeiterdistrikten agitierte"),
    ("direkt ausgeprochen", "direkt ausgesprochen"),
    ('"Wealth of Nationa"', '"Wealth of Nations"'),
    ("Londen 1833", "London 1833"),
    ("marschiger Agrikultursistrikt", "marschiger Agrikulturdistrikt"),
    ("the Working Clssses", "the Working Classes"),
    ("Examination of Infant Labeur", "Examination of Infant Labour"),
    ("vor der Britsh Association", "vor der British Association"),
    ("Manchester genannt und faßt eher über", "Manchester genannt und fast eher über"),
    ("sehen die Laute einander", "sehen die Leute einander"),
    ("in den kommunistischen Zutand", "in den kommunistischen Zustand"),
    ("Schwächung des Unterleibe,", "Schwächung des Unterleibs,"),
    ("Armengesetz-Kommision", "Armengesetz-Kommission"),
    ("(a. a. 0. [p. 133])", "(a. a. O. [p. 133])"),
    ("Sie lenken - 0 Schand'!", "Sie lenken - O Schand'!"),
    # stray or wrong punctuation
    ("es sei Rachitis. aber die Menge", "es sei Rachitis, aber die Menge"),
    ("dazu beitragen. den Arbeiter", "dazu beitragen, den Arbeiter"),
    ("in demselben schmutzigen. und unansehnlichen", "in demselben schmutzigen und unansehnlichen"),
    ("an der England leidet, ist. derselbe", "an der England leidet, ist derselbe"),
    ("was sie nimmt. und es kommen", "was sie nimmt, und es kommen"),
    ("festgebunden. wurden", "festgebunden wurden"),
    ("aufgenommen. zu werden", "aufgenommen zu werden"),
    ('Vgl, "Report of Commission', 'Vgl. "Report of Commission'),
    ("By the Rev, Rd. Parkinson", "By the Rev. Rd. Parkinson"),
    ("die,kühne Bauerschaft", "die 'kühne Bauerschaft"),
    ('"l. daß ich Gelegenheit', '"1. daß ich Gelegenheit'),
]
# the letter l for the digit 1 in numbers ("l844", "l8l7/l8"); each place is listed in SOURCES.md
DIGIT_L = [(re.compile(r"\bl(?=\d)"), "1"), (re.compile(r"(?<=\d)l(?=\d)"), "1")]
DIGIT_L_COUNT = [0]
USED = set()

# Angle-bracket matter that records another edition's reading or a MEW correction becomes a variant;
# everything else in angle brackets is an editorial gloss (a translation of an English phrase) and is kept
# in the text in square brackets, as the shared reader does for MEW's |...| insertions.
VARIANT_RE = re.compile(r"^\s*(?:\(1[89]\d\d|\(1845|Im Original|In de[nr] englischen|Bei Engels|so bei Engels)")


def _decode(name):
    data = (RAW / "de" / name).read_bytes()
    try:
        t = data.decode("utf-8")
    except UnicodeDecodeError:
        t = data.decode("latin-1")
    t = t.replace("\r", "")
    for f, a, b in HTML_FIXES:
        if f == name:
            assert a in t, (name, a)
            t = t.replace(a, b)
            USED_HTML.add((f, a))
    return t


def _table(m):
    """A table becomes one paragraph: cells joined by spaces, rows by ' / '."""
    rows = []
    for tr in re.findall(r"<TR\b.*?</TR>", m.group(0), flags=re.I | re.S):
        cells = [_plain(td) for td in re.findall(r"<TD\b[^>]*>(.*?)</TD>", tr, flags=re.I | re.S)]
        cells = [c for c in cells if c]
        if cells:
            rows.append(" ".join(cells))
    return "<P CLASS=TABLE>" + " / ".join(rows) + "</P>"


def _plain(fragment):
    s = BeautifulSoup(fragment, "html.parser").get_text(" ")
    s = s.replace("\xa0", " ").replace("\xad", "").replace("\t", " ")
    return re.sub(r"\s+", " ", s).strip()


def _text(fragment):
    fragment = re.sub(r"(?<=[A-Za-zäöüÄÖÜß;])</?(?:I|B|SMALL|SUP|U|EM|STRONG)>(?=[a-zäöüß&])", "", fragment, flags=re.I)
    s = _plain(fragment)
    s = re.sub(r"\s+([,.;:!?)])", r"\1", s)
    s = re.sub(r"\(\s+", "(", s)
    return s.strip()


def read_de(sid):
    """Paragraphs [{kind, de}], notes {n: [paragraphs]}, variants {n: {editions, reading}}, title, images."""
    name = PAGES[sid]
    t = _decode(name)
    title = re.search(r"<H2[^>]*>(.*?)</H2>", t, flags=re.I | re.S)
    title = _text(title.group(1)) if title else None
    cut = re.search(r"<P>\s*<HR>\s*</P>", t, flags=re.I)
    body, notes_html = (t[:cut.start()], t[cut.end():]) if cut else (t, "")
    body = body[body.upper().index("</H2>") + 5:] if title else body[body.upper().index("<BODY"):]
    body = re.sub(r"<BODY[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</BODY>.*", "", body, flags=re.I | re.S)
    images = len(re.findall(r"<IMG\b", body, flags=re.I))
    body = re.sub(r"<IMG\b[^>]*>", " ", body, flags=re.I)
    body = re.sub(r"<TABLE\b.*?</TABLE>", _table, body, flags=re.I | re.S)
    body = re.sub(r"<H3[^>]*>(.*?)</H3>", r"<P CLASS=H3>\1</P>", body, flags=re.I | re.S)
    # note references: <A HREF="#O3"> ... (3) ... </A>, in several shapes
    nref = 0

    def ref(m):
        nonlocal nref
        nref += 1
        return f" [[F{m.group(1)}]] "
    body = re.sub(r'<A[^>]*HREF="#O(\d+)"[^>]*>(?:\s*<SMALL>)?\s*(?:O\d+\s*</A>\s*)?(?:<A[^>]*NAME="Z\d+"[^>]*>)?\s*\(\d+\)\s*(?:</A>\s*)*(?:</SMALL>\s*)?(?:</A>)?',
                  ref, body, flags=re.I)
    body = re.sub(r"<BR\s*/?>", " / ", body, flags=re.I)
    paras = []
    for m in re.finditer(r"<P\b([^>]*)>(.*?)(?=<P\b|</BODY>|$)", body, flags=re.I | re.S):
        attr, inner = m.group(1), m.group(2)
        txt = _text(inner)
        if not txt or not re.search(r"[A-Za-zÄÖÜäöüß0-9]", txt):
            continue
        kind = "heading" if "H3" in attr else "p"
        paras.append({"kind": kind, "de": txt, "table": "TABLE" in attr})
    notes = {}
    if notes_html:
        notes_html = re.sub(r"<TABLE\b.*?</TABLE>", _table, notes_html, flags=re.I | re.S)
        notes_html = re.sub(r'<A[^>]*HREF="#Z\d+"[^>]*>\s*&lt;=\s*</A>', " ", notes_html, flags=re.I)
        parts = re.split(r'<A[^>]*NAME="O(\d+)"[^>]*>', notes_html, flags=re.I)
        for k in range(1, len(parts), 2):
            n = parts[k]
            chunk = re.sub(r"</BODY>.*", "", parts[k + 1], flags=re.I | re.S)
            ps = []
            for m in re.finditer(r"(?:^|<P\b[^>]*>)(.*?)(?=<P\b|$)", chunk, flags=re.I | re.S):
                x = _text(m.group(1))
                if re.fullmatch(r"Anmerkungen F\. E\.:?", x):
                    continue        # the heading of the notes, caught inside note 1's anchor on two pages
                x = re.sub(r"^(?:<=\s*)?\(\d+\)?\s*", "", x) if not ps else x
                x = re.sub(r"\s*<=$", "", x).strip()
                if x and re.search(r"[A-Za-zÄÖÜäöüß0-9]", x):
                    ps.append(x)
            assert n not in notes, (sid, n)
            notes[n] = ps
    return title, paras, notes, nref, images


def markup(text, variants):
    """MEW 2's page numbers <306> become [[S306]]; angle-bracket matter becomes a variant [[T<n>]] or a gloss [...];
    a word broken across a page number is re-joined with the page marker in front of it."""
    for a, b in CORRECTIONS_DE:
        if a in text:
            text = text.replace(a, b)
            USED.add(a)
    for rx, rep in DIGIT_L:
        text, k = rx.subn(rep, text)
        DIGIT_L_COUNT[0] += k
    text = re.sub(r"<\s*(\d{3})\s*>", r" [[S\1]] ", text)

    def ang(m):
        inner = m.group(1).strip()
        if VARIANT_RE.match(inner):
            n = str(len(variants) + 1)
            eds = re.match(r"^\((1[89]\d\d(?:\)? und \(?1[89]\d\d)?)\)\s*:?\s*(.*)$", inner)
            eng = re.match(r"^In de[nr] englischen Ausgaben? (?:von )?(1887)(?: und (1892))?", inner)
            if eds:
                editions = " and ".join(re.findall(r"1[89]\d\d", eds.group(1)))
                reading = eds.group(2)
            elif eng:
                editions = "English " + " and ".join(y for y in eng.groups() if y)
                reading = inner
            elif inner.startswith("Im Original (1845)"):
                editions, reading = "1845", inner
            elif inner.startswith("Bei Engels"):
                editions, reading = "1845 and 1892", inner
            else:
                editions, reading = "MEW", inner
            variants[n] = {"editions": editions, "reading": reading}
            return f" [[T{n}]] "
        return f" [{inner}]"
    text = re.sub(r"<([^<>]*)>", ang, text)
    # "Unregel- [[S385]] mäßigkeiten": hyphenated word broken by a page number
    text = re.sub(r"(\w*[A-Za-zäöüß])-\s*(\[\[S\d+\]\])\s*(?!und\b|oder\b|bis\b)([a-zäöüß])", r"\2 \1\3", text)
    for page, a, b in SPLIT_WORDS:
        pat = f"{a} [[S{page}]] {b}"
        if pat in re.sub(r"\s+", " ", text):
            text = re.sub(r"\s+", " ", text).replace(pat, f"[[S{page}]] {a}{b}")
            USED_SPLIT.add(page)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?)])", r"\1", text)
    return text




JOINS = []


def german(sid):
    """Section paragraphs and notes with markers, after CORRECTIONS. Paragraphs that MEW breaks around a set-off
    quotation (one that ends mid-sentence, or the next one starts in lower case) are joined, as in the OF ingest."""
    title, paras, notes, nref, images = read_de(sid)
    variants = {}
    for p in paras:
        p["de"] = markup(p["de"], variants)
        if re.match(r"^(Friedrich Engels|F\. Engels|Barmen, |Eine Dame$)", MARKS.sub("", p["de"]).strip()) and len(p["de"]) < 80:
            p["kind"] = "signature"
    for n in notes:
        notes[n] = [markup(x, variants) for x in notes[n]]
    out, joins = [], 0
    for p in paras:
        prev = TRAIL_MARK.sub("", out[-1]["de"]).strip() if out else ""
        t = MARKS.sub("", p["de"]).strip()
        # after a table only a lower-case start continues the sentence
        if out and out[-1]["kind"] == "p" and p["kind"] == "p" and not re.match(r"^\d+\. ", t) and (
                (re.search(r"[\w,;]$", prev) and not out[-1].get("table")) or re.match(r'^"?[a-zäöüß]', t)):
            out[-1]["de"] = out[-1]["de"] + " " + p["de"]
            out[-1]["table"] = p["table"]
            joins += 1
            JOINS.append((sid, prev[-40:], t[:40]))
        else:
            out.append(p)
    return {"title": title, "paras": out, "notes": notes, "variants": variants, "joined": joins, "images": images}


# ---------------------------------------------------------------- sentence splitting

NO_BREAK = [
    # English sums of money: "1 pounds 6s. 6d.; 1 pounds 2s. 6d." (VII.12.7)
    (r"\b\d+(?:s|d)\.$", r"\d+(?:s|d)\."),
]
BREAKS = {"de": [], "en": []}


def _open(s, a, b):
    s = MARKS.sub("", s)
    return s.count(a) > s.count(b)


def _split(text, lang):
    """The shared splitter, plus repairs kept local to this work (as in the OF ingest):
    - a page marker after an ordinal or abbreviation hides it from the abbreviation check; re-join those pieces;
    - never cut inside a square bracket or an open parenthesis;
    - in tables and lists set with ' / ' between lines, a line that ends a sentence ends the verse."""
    out = []
    for s in segment.split_sentences(text, lang):
        if out and TRAIL_MARK.search(out[-1]):
            prev = TRAIL_MARK.sub("", out[-1]).rstrip()
            if prev.endswith(".") and not segment._is_boundary(prev, s, lang):
                out[-1] = out[-1] + " " + s
                continue
        if out and (_open(out[-1], "[", "]") or _open(out[-1], "(", ")") or any(re.search(a, out[-1]) and re.match(b, s) for a, b in NO_BREAK)):
            out[-1] = out[-1] + " " + s
            continue
        out.append(s)
    res = []
    for s in out:
        res += [x for x in re.split(r'(?<=[.!?])(?:\s*\[\[[A-Z]\d+\]\])*\s+/\s+(?=["„A-ZÄÖÜ])', s) if x]
    for b in BREAKS.get(lang, []):
        res = [x for s in res for x in ([s[:s.index(b) + len(b)].strip(), s[s.index(b) + len(b):].strip()] if b in s and not s.endswith(b) else [s])]
    return res


versify.split_sentences = _split


# ---------------------------------------------------------------- English (Gutenberg plain text)

# Defects in the Gutenberg text, listed in SOURCES.md.
CORRECTIONS_EN = []
USED_EN = set()

EN_HEADS = {"P1892": "PREFACE", "E": " INTRODUCTION", "I": "THE INDUSTRIAL PROLETARIAT.", "II": "THE GREAT TOWNS.",
            "III": "COMPETITION.", "IV": "IRISH IMMIGRATION.", "V": "RESULTS.",
            "VI": "SINGLE BRANCHES OF INDUSTRY.  FACTORY HANDS.", "VII": "THE REMAINING BRANCHES OF INDUSTRY.",
            "VIII": "LABOUR MOVEMENTS.", "IX": "THE MINING PROLETARIAT.", "X": "THE AGRICULTURAL PROLETARIAT.",
            "XI": "THE ATTITUDE OF THE BOURGEOISIE TOWARDS THE PROLETARIAT."}
EN_SECTIONS = list(EN_HEADS)
EN_TITLES = {"P1892": "Preface [to the English edition of 1892]", "E": "Introduction"}


def gutenberg():
    t = (RAW / "en" / "gutenberg_17306.txt").read_text(encoding="ascii").replace("\r", "")
    for a, b in CORRECTIONS_EN:
        assert a in t, a
        t = t.replace(a, b)
        USED_EN.add(a)
    lines = t.split("\n")
    end_body = lines.index("TRANSLATORS NOTE.")
    start_notes = lines.index("Footnotes.")
    end_notes = next(i for i, ln in enumerate(lines) if ln.startswith("***END OF THE PROJECT GUTENBERG"))
    starts = {}
    for i, ln in enumerate(lines[:end_body]):
        for sid, head in EN_HEADS.items():
            if ln == head and sid not in starts:
                starts[sid] = i
    assert list(starts) == EN_SECTIONS, list(starts)
    bounds = [starts[s] for s in EN_SECTIONS] + [end_body]

    def paras(chunk):
        """Paragraphs from blank-line blocks. A line ending in a hyphen is joined to the next without a space:
        the transcription keeps the printed hyphen of compounds broken at a line end ("labouring-classes")."""
        out, cur = [], []
        for ln in chunk + [""]:
            if ln.strip():
                cur.append(ln.strip())
            elif cur:
                txt = ""
                for x in cur:
                    txt += x if txt.endswith("-") else (" " + x if txt else x)
                out.append(re.sub(r"\s+", " ", txt).replace("_", "").strip())
                cur = []
        return out

    keys = []
    notes = {}
    key = None
    for p in paras(lines[start_notes + 1:end_notes]):
        m = re.match(r"^\{(\d+[a-z]?)\}\s+(.*)$", p)
        if m:
            key = m.group(1)
            keys.append(key)
            notes[key] = [m.group(2)]
        else:
            notes[key].append(p)
    EN = {}
    for k, sid in enumerate(EN_SECTIONS):
        out = []
        for p in paras(lines[bounds[k] + 1:bounds[k + 1]]):
            if not re.search(r"[A-Za-z]", p):
                continue           # "* * * * *" separators
            kind = "p"
            if re.fullmatch(r"F\. ENGELS\.(?: January 11th, 1892\.)?", p):
                kind = "signature"
            out.append({"kind": kind, "text": p})
        title = EN_TITLES.get(sid) or EN_HEADS[sid].strip()
        heads = [title]
        if sid == "VI":
            heads = ["SINGLE BRANCHES OF INDUSTRY.", "FACTORY HANDS."]
        EN[sid] = {"title": heads, "paras": out}
    return EN, notes, keys


def en_markers(text, keys):
    """Wischnewetzky's {n} note references become [[U<k>]], k the note's place in the list of notes."""
    def sub(m):
        return f" [[U{keys.index(m.group(1)) + 1}]]"
    return re.sub(r"\s*\{(\d+[a-z]?)\}", sub, text)


# ---------------------------------------------------------------- alignment helpers

import align as _align  # noqa: E402

# Wischnewetzky sometimes turns one of Engels's long sentences into four; the shared aligner allows three at
# most. A 1:4 bead is added for this work only (the list is extended in memory, scripts/lib is not changed).
_align.BEADS.append((1, 4))
_align.PRIOR[(1, 4)] = 7.0
# Speed only: anchors of a sentence group are cached; results are the same as without the cache.
_align.anchors = functools.lru_cache(maxsize=None)(_align.anchors)

# Lexical anchors, as in the OF ingest: Latin- and Greek-derived cognates (first six letters after a light
# spelling normalisation) and a small German-English word list for the words this book keeps returning to.
# Each shared anchor is weighted by how rare it is in the section (IDF). Local to this work.
LEXICON = """
arbeiter arbeiterin | worker working-m workm operative hands labourer laborer
arbeit | work labour labor toil
fabrik | factor mill
fabrikant | manufacturer master mill-owner employer
lohn löhn | wage
kind kinder | child
knabe knaben junge | boy lad
mädchen | girl
frau frauen weib weiber | woman women wife wives
mann männer | man men husband
mutter | mother
vater | father
familie | famil
stadt städte | town city cities
straße straßen | street
gasse gassen | lane alley
hof höfe | court yard
haus häuser | house
wohnung | dwelling house lodging
keller | cellar
zimmer stube | room
bett | bed
fenster | window
tür | door
dach | roof
mauer wand | wall
stunde stunden | hour
woche | week
jahr | year
tag täg | day daily
nacht | night
krank | disease ill sick
tod tot sterb | death dead die mortality
arzt ärzt | physician doctor surgeon
brot | bread
fleisch | meat flesh
kartoffel | potato
nahrung | food nourish
kleid | cloth
kohle | coal
grube bergwerk | mine pit colliery
bergleute bergmann grubenarbeit | miner collier
weber | weaver
spinner spinnerei | spinn
maschine | machine
baumwoll | cotton
wolle woll | wool
seide | silk
eisen | iron
spitze | lace
strumpf | stocking hosier
nadel näh | needle sew
gesetz | law act bill
armengesetz | poor law poor-law
arbeitshaus | workhouse
irländer irisch irland | irish ireland
elend | misery wretched
arm armut | poor povert
reich | rich wealth
geld | money
preis | price
pfund | pound
schilling | shilling
verbrechen verbrecher | crime criminal
polizei | police
richter friedensrichter | judge magistrate justice
schule | school
kirche | church
gott | god
trunk betrunk | drunk drink intemper
branntwein | gin spirits
wasser | water
luft | air
schmutz | filth dirt
fluß | river
bauer | farmer peasant
pächter | tenant farmer
land | land country
boden | soil land ground
korngesetz | corn law
konkurrenz | competition
krise krisis | crisis
streik turnout arbeitseinstellung | strike turn-out turnout
verbindung union | union
chartis | chartis
sozialis | socialis
kapital | capital
profit gewinn | profit
handel | trade commerce
industrie | industr manufactur
bourgeois | bourgeois middle-class
proletar | proletar working-class
england englisch | england english
schottland schottisch | scotland scotch scottish
london | london
manchester | manchester
"""
_LEX = []
for _ln in LEXICON.strip().splitlines():
    _de, _en = _ln.split("|")
    _LEX.append((tuple(_de.split()), tuple(_en.split())))


@functools.lru_cache(maxsize=None)
def _features(s, lang):
    raw = align_strip(s).lower()
    words = re.findall(r"[a-zäöüß-]+", raw)
    t = raw.translate(str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "ss", "k": "c", "z": "c", "é": "e", "è": "e"}))
    t = t.replace("ph", "f").replace("th", "t")
    feats = {"c:" + w[:6] for w in re.findall(r"[a-z]{6,}", t)}
    for i, (de, en) in enumerate(_LEX):
        keys = de if lang == "de" else en
        if any(w.startswith(k) for w in words for k in keys):
            feats.add(f"l:{i}")
    return frozenset(feats)


IDF = {}


def set_idf(A_paras, B_paras):
    df, n = {}, 0
    for paras, lang in ((A_paras, "de"), (B_paras, "en")):
        for p in paras:
            for s in versify.para_sentences(p["text"], lang, p["kind"]):
                n += 1
                for f in _features(s, lang):
                    df[f] = df.get(f, 0) + 1
    IDF.clear()
    IDF.update({f: math.log((n + 1) / (c + 1)) for f, c in df.items()})


ANCHOR_WEIGHT, ANCHOR_CAP = 0.35, 12.0
_base_cost = versify.cross_lang_cost


def _cost(A, B, ratio):
    base = _base_cost(A, B, ratio)

    def f(a_items, b_items):
        c = base(a_items, b_items)
        if a_items and b_items:
            shared = _features(" ".join(a_items), "de") & _features(" ".join(b_items), "en")
            c -= ANCHOR_WEIGHT * min(sum(IDF.get(x, 0.0) for x in shared), ANCHOR_CAP)
        return c
    return f


versify.cross_lang_cost = _cost

# Places where the length-based alignment slips and the script can say what is right: a run of verses
# (first, last) and the verses in it that start an English group, with the number of English sentences each
# takes. The English text is only redistributed, never changed. (The method of the EB and OF ingests.)
REALIGN = [
    # the "surplus" sentence opens Wischnewetzky's second sentence but belongs to III.11.10; her "Most of the
    # markets are distant ones" starts III.11.12, which runs on to "two thousand million new consumers"
    ("III.11.9", "III.11.12", [("III.11.9", 1), ("III.11.10", 3), ("III.11.11", 1), ("III.11.12", 6)]),
    # the "surplus population" sentence and the crossing-sweepers' machine slip one verse early
    ("III.12.6", "III.12.9", [("III.12.6", 1), ("III.12.7", 1), ("III.12.8", 2), ("III.12.9", 2)]),
    # "To sum up briefly the facts thus far cited" opens the summary paragraph II.81.1
    ("II.80.10", "II.81.3", [("II.80.10", 1), ("II.81.1", 9), ("II.81.2", 2), ("II.81.3", 2)]),
    # the two Birmingham schoolmistresses and the noise in the schools
    ("VII.18.3", "VII.18.6", [("VII.18.3", 2), ("VII.18.4", 1), ("VII.18.5", 1), ("VII.18.6", 2)]),
    # Alison quoted: the German runs his two sentences on the rich and the poor into V.36.6; the English has
    # nothing for Engels's link "Nach einer längeren Sittenschilderung fährt unser Autor fort"
    ("V.36.6", "V.37.1", [("V.36.6", 2), ("V.36.7", 1), ("V.37.1", 0)]),
    # the weaver's letter: Engels prints it in four run-on sentences, Wischnewetzky re-translates it in
    # seventeen; split at the German sentence ends ("Er sas und Stoppfte", "Und ig Die frau", "Ja junge")
    ("VI.11.1", "VI.12.2", [("VI.11.1", 2), ("VI.11.2", 3), ("VI.11.3", 8), ("VI.11.4", 4), ("VI.12.1", 1), ("VI.12.2", 1)]),
    # Sharp's numbered points: point (5) closes his statement in VI.36.1
    ("VI.36.1", "VI.37.1", [("VI.36.1", 5), ("VI.37.1", 1)]),
    # serf and free worker: Wischnewetzky splits most of Engels's comparisons in two and has no English for
    # Mead's poem that closes the chapter (VI.77.1 to VI.86.1), so the length-based match ran on into the poem
    ("VI.76.3", "VI.86.1", [("VI.76.3", 2), ("VI.76.4", 2), ("VI.76.5", 2), ("VI.76.6", 2), ("VI.76.7", 1), ("VI.76.8", 2),
                            ("VI.76.9", 1), ("VI.76.10", 1), ("VI.76.11", 1), ("VI.76.12", 1), ("VI.76.13", 1), ("VI.76.14", 1),
                            ("VI.77.1", 0), ("VI.77.2", 0), ("VI.78.1", 0), ("VI.79.1", 0), ("VI.80.1", 0), ("VI.81.1", 0),
                            ("VI.82.1", 0), ("VI.83.1", 0), ("VI.84.1", 0), ("VI.85.1", 0), ("VI.86.1", 0)]),
]
USED_REALIGN = set()
# Verses the English leaves out, as found when regrouping
OMITTED = {
    "V.37.1": "Wischnewetzky's English goes straight on with Alison and has nothing for this sentence.",
    "VI.77.1": "The English of 1887 and 1892 leaves out Mead's poem and the two sentences that introduce it (VI.77.1 to VI.86.1).",
}


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
            if v["id"] in OMITTED:
                v["en_note"] = OMITTED[v["id"]]
            if v["id"] in counts and counts[v["id"]] == 0:
                continue          # no English at all: said in en_note, not a doubtful match
            if v["id"] in counts and (size[v["id"]], counts[v["id"]]) != (1, 1):
                v["align"], v["review"] = f"{size[v['id']]}:{counts[v['id']]}", True
                v["review_reason"] = f"{size[v['id']]} de sentence(s) matched to {counts[v['id']]} en sentence(s); regrouped by the ingest (see REALIGN)"


# ---------------------------------------------------------------- notes

def pair_notes(vs, de_notes, keys, en_notes):
    """Pair Engels's notes in MEW with Wischnewetzky's footnotes. The German and English note references of a
    section are lined up in order (a monotonic alignment that may leave either side unpaired). A pair scores
    3 when both references sit in the same verse, 2 for each shared number, 1 for each shared name or anchor
    (cognate, lexicon word), less half a point for each verse between them; references more than four verses
    apart, or scoring under 1.5, are not paired. Returns {German note: English key}."""
    F = [(i, n) for i, v in enumerate(vs) for n in re.findall(r"\[\[F(\d+)\]\]", v["_de_raw"])]
    U = [(i, keys[int(k) - 1]) for i, v in enumerate(vs) for k in re.findall(r"\[\[U(\d+)\]\]", v["_en_raw"])]

    def names(t):
        return {w.lower() for w in re.findall(r"\b[A-Z][a-z]{2,}\b", t)} - {"the", "der", "die", "das", "and", "und", "von"}

    def score(f, u):
        (i, n), (iu, key) = f, u
        if abs(i - iu) > 4:
            return None
        de_txt, en_txt = " ".join(de_notes.get(n, [])), " ".join(en_notes[key])
        shared = _features(de_txt, "de") & _features(en_txt, "en")
        nums = set(re.findall(r"\b\d{2,4}\b", de_txt)) & set(re.findall(r"\b\d{2,4}\b", en_txt))
        sc = 3 * (i == iu) + 2 * len(nums) + min(len(shared | (names(de_txt) & names(en_txt))), 4) - 0.5 * abs(i - iu)
        return sc if sc >= 1.5 else None

    nf, nu = len(F), len(U)
    D = [[0.0] * (nu + 1) for _ in range(nf + 1)]
    back = [[None] * (nu + 1) for _ in range(nf + 1)]
    for x in range(nf + 1):
        for y in range(nu + 1):
            best = (D[x][y], None)
            if x and D[x - 1][y] >= best[0]:
                best = (D[x - 1][y], "f")
            if y and D[x][y - 1] >= best[0]:
                best = (D[x][y - 1], "u")
            if x and y:
                sc = score(F[x - 1], U[y - 1])
                if sc is not None and D[x - 1][y - 1] + sc > best[0]:
                    best = (D[x - 1][y - 1] + sc, "p")
            if x or y:
                D[x][y], back[x][y] = best
    pairs, x, y = {}, nf, nu
    while x or y:
        step = back[x][y]
        if step == "p":
            pairs[F[x - 1][1]] = U[y - 1][1]
            x, y = x - 1, y - 1
        elif step == "f":
            x -= 1
        else:
            y -= 1
    return pairs


# Pairs the scoring gets wrong, checked by reading both notes: {section: {German note: English key or None}}.
NOTE_PAIRS = {
    # "The Artizan", 1843 / "The Artisan", October, 1842: same monthly, spelling and year differ
    "II": {"5": "35b"},
    # Wischnewetzky's {100b} cites Alison's Principles, which the German does not cite here; {100c} is the
    # British Association article (German N3); the German N4 repeats N2 and has no English
    "V": {"3": "100c", "4": None, "13": "117a", "15": "120"},
    # Engels's reply to the manufacturers: he hangs it on the end of Mead's poem, which the English leaves out
    "VI": {"19": "186"},
    # Wakefield's "Swing Unmasked": the English reference sits a paragraph earlier
    "X": {"1": "264"},
}
USED_PAIRS = set()


NOTE_EDITION = re.compile(r"^\((1887|1892)(?: Fußnote)?\)\s*|^\((1887) Fußnote\)\s*")


# ---------------------------------------------------------------- writing

SRC_DE = "MEW 2, S. 225-506 (Dietz, Berlin 1972) via mlwerke.de; text of the first edition (Leipzig 1845), readings of the second edition (Stuttgart 1892) as variants"
SRC_EN = "Florence Kelley Wischnewetzky's translation (New York 1887) in the London edition of 1892 (Swan Sonnenschein), Project Gutenberg ebook 17306 (public domain)"
DATES = {"P1892": "1892-01-11", "D": "1845-03-15", "P1845": "1845-03-15"}


def meta(sid, title_de, title_en, ol="de", anchor="de", src_de=SRC_DE, src_en=SRC_EN):
    return {"section": sid, "title_original": title_de, "title_en": title_en, "author": "Friedrich Engels",
            "date": DATES.get(sid, "1844-11/1845-03"), "original_language": ol, "anchor_language": anchor,
            "source_original": src_de, "source_en": src_en}


def flags(vs):
    return sum(1 for v in vs if v.get("review"))


def place_en_notes(vs, keys, en_notes, paired_keys, placed):
    for v in vs:
        for k in re.findall(r"\[\[U(\d+)\]\]", v["_en_raw"]):
            key = keys[int(k) - 1]
            placed.add(key)
            if key in paired_keys:
                continue
            text = " ".join(en_notes[key])
            v["en_note"] = (v.get("en_note", "") + f" English note {{{key}}}: {text}").strip()


def note_section(sid, n, paras, en_paras, variants, src_note):
    """Verses of one of Engels's notes; English from the paired Wischnewetzky note, if any."""
    edition = ""
    m = NOTE_EDITION.match(MARKS.sub("", paras[0]).strip())
    if m:
        edition = next(g for g in m.groups() if g)
    A = [P("note", t) for t in paras]
    if en_paras:
        B = [P("note", t) for t in en_paras]
        set_idf(A, B)
        nv, _ = build_section("N", f"{sid}.N{n}", "de", A, B, flat=True, para0_heading=False)
    else:
        nv, _ = build_section("N", f"{sid}.N{n}", "de", A, [], single=True, para0_heading=False)
        nv[0]["en_note"] = src_note
    attach_apparatus(nv, variants, f"{sid}.N{n}.", {})
    if edition:
        for v in nv:
            v["note_edition"] = f"added by Engels in {edition}" if edition == "1892" else "note of the English edition of 1887, in English"
    return nv


SECTIONS = ["P1892", "D", "P1845", "E", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
FILES = {"P1892": "00-front/1-p1892.yaml", "D": "00-front/2-d.yaml", "P1845": "00-front/3-p1845.yaml"}
for _i, _s in enumerate(SECTIONS[3:]):
    FILES[_s] = f"01-condition/{_i:02d}-{_s.lower()}.yaml"
TITLES_EN = {"D": "To the Working-Classes of Great Britain", "P1845": "Preface [1845]", "I": "The Industrial Proletariat",
             "II": "The Great Towns", "III": "Competition", "IV": "Irish Immigration", "V": "Results",
             "VI": "Single Branches of Industry. Factory Hands", "VII": "The Remaining Branches of Industry",
             "VIII": "Labour Movements", "IX": "The Mining Proletariat", "X": "The Agricultural Proletariat",
             "XI": "The Attitude of the Bourgeoisie towards the Proletariat"}


def build_front(sid, EN, report):
    if sid == "P1892":
        en = EN["P1892"]
        A = [P("heading", en["title"][0])] + [P(p["kind"], p["text"]) for p in en["paras"]]
        vs, _ = build_section(sid, sid, "en", A, [], single=True, lang_a="en")
        attach_apparatus(vs, {}, f"{sid}.", {})
        vs = finalise(vs)
        report[sid] = (len(vs), 0, 0, len(A), len(A), 0)
        return vs, meta(sid, "", en["title"][0], ol="en", anchor="en",
                        src_de="None: Engels wrote this preface in English; his German preface of 1892 (MEW 22) is a different text and is not in the sources used yet",
                        src_en="Engels's own English, in the London edition of 1892 (Swan Sonnenschein), Project Gutenberg ebook 17306"), None
    g = german(sid)
    A = [P("heading", g["title"])] + [P(p["kind"], p["de"]) for p in g["paras"]]
    vs, _ = build_section(sid, sid, "de", A, [], single=True)
    attach_apparatus(vs, g["variants"], f"{sid}.", {})
    if sid == "D":
        vs[0]["en_note"] = "Engels wrote the dedication in English; his English text is not in the sources used yet. The German is MEW's translation."
        m = meta(sid, g["title"], TITLES_EN[sid], ol="en", anchor="de",
                 src_de="MEW 2, S. 229-231 (Dietz, Berlin 1972) via mlwerke.de; German is MEW's editorial translation of Engels's English, NOT an original",
                 src_en="None: Engels's English text of 1845 is not in the sources used yet")
    else:
        vs[0]["en_note"] = "The English edition of 1892 leaves out this preface."
        m = meta(sid, g["title"], TITLES_EN[sid], src_de="MEW 2, S. 232-234 (Dietz, Berlin 1972) via mlwerke.de; preface to the first edition (Leipzig 1845)",
                 src_en="None: the 1892 English edition leaves this preface out")
    vs = finalise(vs)
    report[sid] = (len(vs), 0, 0, len(A), 0, g["joined"])
    return vs, m, g


def build(sid, EN, en_notes, keys, placed, report):
    g = german(sid)
    en = EN[sid]
    A = [P("heading", g["title"])] + [P(p["kind"], p["de"]) for p in g["paras"]]
    B = [P("heading", t) for t in en["title"]] + [P(p["kind"], en_markers(p["text"], keys)) for p in en["paras"]]
    set_idf(A, B)
    vs, _ = build_section(sid, sid, "de", A, B, flat=True)
    realign(vs)
    pairs = pair_notes(vs, g["notes"], keys, en_notes)
    for n, key in NOTE_PAIRS.get(sid, {}).items():
        USED_PAIRS.add((sid, n))
        for other in [m for m, k in pairs.items() if k == key and m != n]:
            del pairs[other]
        if key:
            pairs[n] = key
        else:
            pairs.pop(n, None)
    place_en_notes(vs, keys, en_notes, set(pairs.values()), placed)
    attach_apparatus(vs, g["variants"], f"{sid}.", {})
    nverses = 0
    for n, paras in g["notes"].items():
        key = pairs.get(n)
        en_paras = [en_markers(x, keys) for x in en_notes[key]] if key else []
        nv = note_section(sid, n, paras, en_paras, g["variants"], "Not paired with a footnote of the 1892 English. Wischnewetzky's footnotes that the ingest could not pair are kept in en_note on the verse they belong to.")
        if key:
            nv[0]["en_note"] = (nv[0].get("en_note", "") + f" English note {{{key}}}.").strip()
            placed.add(key)
        vs += nv
        nverses += len(nv)
    vs = finalise(vs)
    report[sid] = (len(vs), flags(vs), nverses, len(A), len(B), g["joined"])
    return vs, meta(sid, g["title"], TITLES_EN.get(sid, en["title"][0])), g


def main():
    CLEAN.mkdir(parents=True, exist_ok=True)
    EN, en_notes, keys = gutenberg()
    placed, total, report, clean_de, nflags = set(), 0, {}, {}, 0
    only = sys.argv[1:]          # for checking: build only the sections named; the full run takes all
    for sid in SECTIONS:
        if only and sid not in only:
            continue
        if sid in ("P1892", "D", "P1845"):
            vs, m, g = build_front(sid, EN, report)
        else:
            vs, m, g = build(sid, EN, en_notes, keys, placed, report)
        if g:
            clean_de[sid] = g
        dump(WORK / "text" / FILES[sid], m, vs)
        total += len(vs)
    if only:
        return
    missing = set(keys) - placed
    assert not missing, sorted(missing)
    assert USED == {a for a, _ in CORRECTIONS_DE}, {a for a, _ in CORRECTIONS_DE} - USED
    assert USED_HTML == {(f, a) for f, a, _ in HTML_FIXES}
    assert USED_PAIRS == {(s, n) for s, d in NOTE_PAIRS.items() for n in d}
    print("letter l read as digit 1:", DIGIT_L_COUNT[0])
    assert USED_SPLIT == {p for p, _, _ in SPLIT_WORDS}
    assert USED_REALIGN == {r[0] for r in REALIGN}, {r[0] for r in REALIGN} - USED_REALIGN
    (CLEAN / "de.json").write_text(json.dumps(clean_de, ensure_ascii=False, indent=1), encoding="utf-8")
    (CLEAN / "en.json").write_text(json.dumps({"sections": EN, "notes": en_notes}, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, (n, f, nn, pa, pb, j) in report.items():
        print(f"{k:6} {n:5} verses {f:4} to review  {nn:3} note verses  paragraphs de {pa} en {pb}  joined {j}")
        nflags += f
    print("total", total, "verses", nflags, "to review")


if __name__ == "__main__":
    main()
