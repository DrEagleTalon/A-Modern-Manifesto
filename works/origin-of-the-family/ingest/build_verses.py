"""One-time ingest for The Origin of the Family, Private Property and the State (OF).

German  MEW 21, pp. 25-173 (Dietz, Berlin 1962), via the mlwerke.de mirror: Engels's text of the fourth
        edition (Stuttgart 1892), with the first-edition (1884) readings as variants. Engels's preface to the
        first edition (MEW 21, pp. 27-29) and his preface to the fourth edition (MEW 22, pp. 211-222, also
        printed in Die Neue Zeit, 1891, as "Zur Urgeschichte der Familie").
English Ernest Untermann's translation (Charles H. Kerr, Chicago 1902; 1908 printing), as transcribed by
        Project Gutenberg (ebook 33111, ASCII). Public domain. Untermann's own preface is left out; his
        translator's notes and the references he set as footnotes are kept as en_note on the verse they sit in.

Sections:
  P1884  Engels's preface to the first edition.
  P1891  Engels's preface to the fourth edition.
  I to IX  Engels's nine chapters. Paragraph 0 is the chapter title.
Engels's footnotes are <section>.N<n> as in MEW (P1884.N1, P1891.N1, II.N1 to II.N3 ...). Untermann translates
all of them except P1891.N1; his versions fill the English column of the note verses.

All sections are aligned sentence by sentence across paragraph breaks (flat=True): Untermann re-paragraphs
freely, often splitting one of Engels's long paragraphs in two or three.

Run once. After the lock file exists the YAML in text/ is the source of truth.
"""
import functools
import json
import math
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
segment.ABBR["de"] = segment.ABBR["de"] | {"sog", "Kap", "lib", "cap", "Anm", "ff", "Ges", "Bde", "Jahrh", "a", "O", "ebd", "ib"}
segment.ABBR["en"] = segment.ABBR["en"] | {"l", "c", "Ibid", "ch", "Chap", "lib", "cap", "ff", "Sec"}

TRAIL_MARK = re.compile(r"(?:\s*\[\[[A-Z]\d+\]\])+$")
MARKS = re.compile(r"\s*\[\[[A-Z]\d+\]\]")


# ---------------------------------------------------------------- MEW pages

# Markup defects in the mlwerke.de pages, repaired in a copy before parsing (the raw files stay untouched).
HTML_FIXES = [
    # P1891: Engels's footnote on Morgan is printed but not linked, so the shared reader would drop it
    ("me22_211.htm", "verheimlicht wird.<SMALL><SUP>(1)</P>", 'verheimlicht wird.<A HREF="#F1">(1)</A></P>'),
    ("me22_211.htm", "<SMALL><SUP><P>(1)</SMALL></SUP> Auf der R", '<P><A NAME="F1">(1)</A> Auf der R'),
    # P1891.3: the Romanian title and translator's name are garbled (control characters for the Romanian letters),
    # and a FONT tag sits inside the page anchor for p. 212
    ("me22_211.htm", 'propnet\x01\x03\x01cii, private <A NAME="S212"></FONT><B>|212|</A></B><FONT FACE="Times New Roman"> \x01_i a statului',
     'proprietăţii private <A NAME="S212"><B>|212|</A></B> şi a statului'),
    ("me22_211.htm", "Joan N\x01\x03dejde", "Joan Nădejde"),
    # II: the Serbian words for the head of the household community and his wife
    ("me21_036.htm", "(doma\x01in)", "(domaćin)"),
    ("me21_036.htm", "(doma\x01ica)", "(domaćica)"),
    ("me21_036.htm", "des Doma\x01in ist", "des Domaćin ist"),
    # VII: Slavonic "žena" (woman)
    ("me21_127.htm", "slawisch \x01~ena", "slawisch žena"),
    # IV: two page anchors open their bar outside the link ("|<A NAME="S100"><B>100|")
    ("me21_098.htm", '|<A NAME="S100"><B>100|', '<A NAME="S100"><B>|100|'),
    ("me21_098.htm", '|<A NAME="S102"><B>102|', '<A NAME="S102"><B>|102|'),
    # IV: the shared reader takes a paragraph opening 'In der "' for the start of MEW's apparatus and stops
    # there, which would lose the last three paragraphs of the chapter; a [[K0]] marker in front prevents that
    ("me21_098.htm", '<P>In der "Ilias"', '<P>[[K0]]In der "Ilias"'),
]
USED_HTML = set()


def _prepare(name, tmp):
    """Copy a MEW page as UTF-8 with HTML_FIXES applied. Three pages are 8-bit; their only bytes in the
    0x80-0x9F range are 0x97 (a dash), used for the separator lines between parts of a chapter."""
    data = (RAW / "de" / name).read_bytes()
    try:
        t = data.decode("utf-8")
    except UnicodeDecodeError:
        t = data.decode("latin-1").replace("\x97", "-")
    t = t.replace("\r", "")
    # a word broken across a page anchor whose first half ends in an HTML entity ("m&ouml;g- |149| lich"):
    # the shared reader re-joins only plain letters, so move the anchor in front of the whole word here
    t = re.sub(r'((?:\w|&[a-z]+;)+)-\s*(<A NAME="S\d+">\s*<B>\s*\|\d+\|\s*</A>\s*</B>)\s*((?:[a-zäöüß]|&[a-z]+;))', r"\2 \1\3", t)
    for f, a, b in HTML_FIXES:
        if f == name:
            assert a in t, (name, a)
            t = t.replace(a, b)
            USED_HTML.add((f, a))
    p = Path(tmp) / name
    p.write_text(t, encoding="utf-8")
    return p


# Transcription errors in the mlwerke.de text. Listed in SOURCES.md.
CORRECTIONS_DE = [
    ("auf diesen Punkt zurück,", "auf diesen Punkt zurück."),
    ("Selbst die rohsten Volker,", "Selbst die rohsten Völker,"),
    ("daß. soviel wir wissen", "daß, soviel wir wissen"),
    ("noch verwickeitere Hypothesen", "noch verwickeltere Hypothesen"),
    ("diesen hochschottischcn Clan", "diesen hochschottischen Clan"),
    ("Diese Veränderungen. sind der Art", "Diese Veränderungen sind der Art"),
    ("alle Männer der ändern zu ihren", "alle Männer der andern zu ihren"),
    ("mit jedem ändern Stamm", "mit jedem andern Stamm"),
    ("wie sehr alle ändern Formen", "wie sehr alle andern Formen"),
    ("In beiden Fallen aber", "In beiden Fällen aber"),
    ("in manchen Fallen fehlt", "in manchen Fällen fehlt"),
    ("aber in allen Fallen war die Gens", "aber in allen Fällen war die Gens"),
    ("und in allen Fallen wesentlich", "und in allen Fällen wesentlich"),
    ("in beiden Fallen die zehnfache", "in beiden Fällen die zehnfache"),
    ("einen so mächtigen Einnuß", "einen so mächtigen Einfluß"),
    ("die südamenkanischen Völker", "die südamerikanischen Völker"),
    ("vierzig nordamerinkanischen Stämmen", "vierzig nordamerikanischen Stämmen"),
    ("sondem auf ökonomische", "sondern auf ökonomische"),
    ("noch eine fortgeschnttnere Arbeitsteilung", "noch eine fortgeschrittnere Arbeitsteilung"),
    ("mit der Masse des Rollstoffs", "mit der Masse des Rohstoffs"),
    ('vom Weltuntergang, der "Völuspâ.', 'vom Weltuntergang, der "Völuspâ".'),
]
USED = set()


def parse_mew(name, tmp, **kw):
    """parse_mew on the prepared page; then the CORRECTIONS; drop separator lines; re-join paragraphs that MEW
    breaks around a set-off quotation (a paragraph that ends mid-sentence, or the next one starts in lower case).
    Numbered list items are never joined to the item before."""
    paras, notes, variants = _parse_mew(_prepare(name, tmp), **kw)
    for p in paras:
        p["de"] = p["de"].replace("[[K0]]", "").strip()
        for a, b in CORRECTIONS_DE:
            if a in p["de"]:
                p["de"] = p["de"].replace(a, b)
                USED.add(a)
    for lines in notes.values():
        for i, x in enumerate(lines):
            for a, b in CORRECTIONS_DE:
                if a in x:
                    lines[i] = x = x.replace(a, b)
                    USED.add(a)
    paras = [p for p in paras if re.search(r"[A-Za-zÄÖÜäöüß]", MARKS.sub("", p["de"]))]
    out, joins = [], 0
    for p in paras:
        prev = TRAIL_MARK.sub("", out[-1]["de"]).strip() if out else ""
        t = MARKS.sub("", p["de"]).strip()
        if out and out[-1]["kind"] == "p" and p["kind"] == "p" and not re.match(r"^\d+\. ", t) and (
                re.search(r"[\w,;]$", prev) or re.match(r'^"?[a-zäöüß]', t)):
            out[-1]["de"] = out[-1]["de"] + " " + p["de"]
            joins += 1
        else:
            out.append(p)
    for v in variants.values():
        v["editions"] = v["editions"].replace("l884", "1884")
        v["reading"] = re.sub(r"\s*\[\[F(\d+)\]\]", r" (\1)", v["reading"]).strip()
    return out, notes, variants, joins


# ---------------------------------------------------------------- sentence splitting

def _split(text, lang):
    """The shared splitter, plus repairs kept local to this work:
    - when a page marker follows an ordinal or abbreviation ("am 2. [[S170]] Dezember") the abbreviation
      check does not see it and cuts the sentence; re-join those pieces;
    - never cut inside a square bracket or an open parenthesis;
    - a short bracketed reference at the start of a piece ("(S. 140.)") hangs on the sentence it cites;
    - the sentence ends in BREAKS, which the splitter cannot see, are cut."""
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
        m = re.match(r"^(\([^()]{1,60}\)\.?)\s*(.*)$", s)
        if out and m:
            out[-1] = out[-1] + " " + m.group(1)
            if m.group(2):
                out.append(m.group(2))
            continue
        out.append(s)
    # a run of one-word list items ("1. Wolf. 2. Bear. 3. Turtle.", III.4.2) stays one sentence
    items = []
    for s in out:
        if items and re.search(r"(?:^|\s)\d+\. [A-Z][a-z-]+\.$", items[-1]) and re.match(r"^\d+\. [A-Z][a-z-]+\.$", s):
            items[-1] = items[-1] + " " + s
        else:
            items.append(s)
    out = items
    for b in BREAKS.get(lang, []):
        out = [x for s in out for x in ([s[:s.index(b) + len(b)].strip(), s[s.index(b) + len(b):].strip()] if b in s and not s.endswith(b) else [s])]
    return out


def _open(s, a, b):
    s = MARKS.sub("", s)
    return s.count(a) > s.count(b)


NO_BREAK = [
    # P1891.4.6: the title 'Researches into the Early History of Mankind etc. etc.' ends in a quote mark
    (r'etc\. etc\."$', r"\(1865\)"),
    # II.84.8: "der Code Napoleon Art. 312:"
    (r"Code Napoleon Art\.$", r"312:"),
]
BREAKS = {"de": [], "en": []}
versify.split_sentences = _split


# ---------------------------------------------------------------- English (Gutenberg plain text)

# Defects in the Gutenberg text, listed in SOURCES.md.
CORRECTIONS_EN = [
    ("Broedbr munu berjask", "Broedhr munu berjask"),
]
USED_EN = set()

SECTIONS = ["P1884", "P1891", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
EN_START = {"P1884": "AUTHOR'S PREFACE TO THE FIRST EDITION, 1884.", "P1891": "AUTHOR'S PREFACE TO THE FOURTH EDITION, 1891."}
# Untermann's footnotes that translate Engels's own notes: English note number -> (section, MEW note number)
AUTHOR_NOTES = {1: ("P1884", 1), 7: ("II", 1), 12: ("II", 2), 13: ("II", 3), 24: ("IV", 1), 26: ("VI", 1),
                27: ("VII", 1), 28: ("VII", 2), 30: ("VIII", 1), 34: ("VIII", 2),
                37: ("IX", 1), 38: ("IX", 2), 39: ("IX", 3), 45: ("IX", 4), 46: ("IX", 5)}


def gutenberg():
    t = (RAW / "en" / "gutenberg_33111.txt").read_text(encoding="ascii").replace("\r", "")
    for a, b in CORRECTIONS_EN:
        assert a in t, a
        t = t.replace(a, b)
        USED_EN.add(a)
    lines = t.split("\n")
    end = next(i for i, ln in enumerate(lines) if ln.startswith("End of the Project Gutenberg EBook"))
    starts = {}
    for i, ln in enumerate(lines[:end]):
        for sid, head in EN_START.items():
            if ln == head:
                starts[sid] = i
        m = re.match(r"^CHAPTER ([IVX]+)\.$", ln)
        if m:
            starts[m.group(1)] = i
    assert list(starts) == SECTIONS, list(starts)
    bounds = [starts[s] for s in SECTIONS] + [end]

    def paras(chunk):
        out, cur = [], []
        for ln in chunk + [""]:
            if ln.strip():
                cur.append(ln.strip())
            elif cur:
                out.append(re.sub(r"\s+", " ", " ".join(cur)).replace("_", "").strip())
                cur = []
        return out

    EN, notes = {}, {}
    for k, sid in enumerate(SECTIONS):
        chunk = lines[bounds[k] + 1:bounds[k + 1]]
        cut = next((i for i, ln in enumerate(chunk) if ln in ("FOOTNOTES:", "FOOTNOTE:")), len(chunk))
        body, foot = paras(chunk[:cut]), [p for p in paras(chunk[cut + 1:]) if p != "THE ORIGIN OF THE FAMILY"]
        title = None
        if sid not in EN_START:
            title = f"CHAPTER {sid}. {body.pop(0)}"
        out = []
        for p in body:
            if p in ("THE ORIGIN OF THE FAMILY", "THE END.") or not re.search(r"[A-Za-z]", p):
                continue           # running title, end mark, "* * *" separators
            if sid == "P1884" and p == "FREDERICK ENGELS.":
                continue           # MEW prints the 1884 preface unsigned
            kind = "p"
            if re.fullmatch(r"(?:[IVX]+|\d)\. [A-Z][A-Z ]+\.", p):
                kind = "heading"
            elif re.fullmatch(r"FREDERICK ENGELS\.|London, June 16th, 1891\.", p):
                kind = "signature"
            out.append({"kind": kind, "text": p})
        # II: Untermann sets the four family forms as headings ("1. THE CONSANGUINE FAMILY.");
        # in the German they open the paragraph, so they are folded into the paragraph that follows
        fixed = []
        for p in out:
            if fixed and fixed[-1]["kind"] == "heading" and re.match(r"^\d\. ", fixed[-1]["text"]) and sid == "II":
                fixed[-1] = {"kind": "p", "text": fixed[-1]["text"] + " " + p["text"]}
            else:
                fixed.append(p)
        key = None
        for p in foot:
            m = re.match(r"^\[(\d+)\] (.*)$", p)
            if m:
                key = int(m.group(1))
                notes[key] = [m.group(2)]
            else:
                notes[key].append(p)
        EN[sid] = {"title": title, "paras": fixed}
    return EN, notes


def en_markers(text, sid):
    """Untermann's [n] become [[G<k>]] for a note that translates Engels's note k in this section and
    [[U<n>]] for his own notes and references."""
    def sub(m):
        n = int(m.group(1))
        if n in AUTHOR_NOTES:
            sec, k = AUTHOR_NOTES[n]
            assert sec == sid, (n, sid)
            return f" [[G{k}]]"
        return f" [[U{n}]]"
    return re.sub(r"\[(\d+)\]", sub, text)


def author_note(paras):
    """Untermann's version of one of Engels's notes, without his label."""
    first = paras[0]
    # "Author's note to the fourth edition." is kept: it renders Engels's own "Zur vierten Auflage." (VII.N1)
    if first.startswith("Author's note. "):
        first = first[len("Author's note. "):]
    elif first == "Author's note.":
        return paras[1:]
    return [first] + paras[1:]


def place_en_notes(vs, sid, notes, placed):
    for v in vs:
        for n in re.findall(r"\[\[U(\d+)\]\]", v["_en_raw"]):
            n = int(n)
            body = " ".join(notes[n])
            label = "Translator's note."
            if body.startswith(label):
                text = f"Untermann's note [{n}]: {body[len(label):].strip()}"
            else:
                text = f"Untermann's footnote [{n}]: {body}"
            v["en_note"] = (v.get("en_note", "") + " " + text).strip()
            placed.add(n)
        for k in re.findall(r"\[\[G(\d+)\]\]", v["_en_raw"]):
            if f"[[F{k}]]" not in v["_de_raw"]:
                v["en_note"] = (v.get("en_note", "") + f" Untermann's 1902 English attaches note {sid}.N{k} here.").strip()


# ---------------------------------------------------------------- alignment helpers

# Untermann often turns one of Engels's sentences into four (IV.1.6); the shared aligner allows three at most.
# A 1:4 bead is added for this work only (the list is extended in memory, scripts/lib is not changed).
import align as _align  # noqa: E402
_align.BEADS.append((1, 4))
_align.PRIOR[(1, 4)] = 7.0


# Speed only: the anchor and cognate sets of a sentence group are cached, since II and IX are long and the
# aligner asks for the same groups many times. Results are the same as without the cache.
_align.anchors = functools.lru_cache(maxsize=None)(_align.anchors)


# Lexical anchors. The shared cost function anchors on names and numbers only. Engels's German and Untermann's
# English share many Latin- and Greek-derived words (Gens/gens, Phratrie/phratry, Monogamie/monogamy), used as
# cognate anchors as in the SUS and EB ingests. On top of that, a small German-English word list (LEXICON)
# for the words this book keeps returning to (Frau/woman, Stamm/tribe, Ehe/marriage, Eigentum/property).
# Each shared anchor is weighted by how rare it is in the section (IDF), so that "gens", which is in every
# other sentence, says little and "Hekatäus" or "Dikäarchos" says a lot. Local to this work.
LEXICON = """
frau weib frauen weiber weibl gattin | woman women wife wives female
mann männer männl gatte gatten | man men husband male
kind kinder | child
mutter mütter mütterl | mother maternal
vater väter väterl | father paternal
bruder brüder | brother
schwester | sister
sohn söhne | son
tochter töchter | daughter
onkel oheim | uncle
neffe | nephew
enkel | grandchild grandson
ehe heirat verheirat | marri wedlock wedding
stamm stämm | tribe
volk völker | people nation
staat | state
gesellschaft gesellschaftl | society social
eigentum eigentüm | property propert
besitz | possess property
reichtum reichtüm | wealth riches
reich | rich
arm | poor
sklav | slave
arbeit | labor work
krieg | war
heer | army
heerführer | chief commander
rat räte | council
gesetz | law
recht | right law
land länder | land countr
boden grund | soil land ground
geld | money
handel händler | trade merchant commerce
kaufleute kaufmann | merchant
vieh herde herden | cattle herd stock
ackerbau | agricultur tillage
eisen | iron
stadt städte | city town
dorf dörfer | village
haus häuser haushalt | house household
gott götter | god
erb erbin erbschaft | inherit heir
tod tot sterb | death dead die
blut | blood
verwandt | relat kin
abstamm | descent descend
geschlecht | sex gens
jung | young
alt | old ancient
neu | new
geschichte geschichtl | histor
barbar | barbar
wild | savage
zivilis | civiliz
sprache | language dialect
name namen | name
gemeinsam | common
religi | religi
priester | priest
könig | king
adel adlig | nobl
bauer bauern | peasant farmer
bürger | citizen
grieche griech | greek grecian
römer römisch rom | roman rome
deutsch germanen | german
kelt | celt
irokes | iroquois
indian | indian
amerika | americ
athen | athen attic
gallier gallien | gaul
"""
_LEX = []
for _ln in LEXICON.strip().splitlines():
    _de, _en = _ln.split("|")
    _LEX.append((tuple(_de.split()), tuple(_en.split())))


@functools.lru_cache(maxsize=None)
def _features(s, lang):
    """Anchor features of a sentence group: cognate stems and lexicon concepts."""
    raw = align_strip(s).lower()
    words = re.findall(r"[a-zäöüß]+", raw)
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
    """Document frequency of each feature over the section's sentences, both languages together."""
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


# Places where the length-based alignment slips and the script can say what is right. Each entry is a run of
# verses (first, last) and the verses in it that start an English group, with the number of English sentences
# each takes; the other verses in the run join the head before them. The English text is only redistributed,
# never changed: the run must hold exactly that many English sentences. (The method of the EB ingest.)
REALIGN = [
    # I: "2. Mittelstufe." is the head of Untermann's "2. Middle Stage: Commencing with ...", not part of I.6.5
    ("I.6.5", "I.7.2", [("I.6.5", 2), ("I.7.1", 1)]),
    # Untermann turns Engels's long sentence on Bachofen's propositions into seven; his "Although Bachofen ...
    # did not formulate these propositions so clearly, still he proved their correctness" covers P1891.9.5 and
    # the first half of P1891.9.6
    ("P1891.9.4", "P1891.9.6", [("P1891.9.4", 7), ("P1891.9.5", 1), ("P1891.9.6", 1)]),
    # Agassiz's anecdote: one English sentence too early from "On being introduced" to "They know about their mother"
    ("II.46.1", "II.47.2", [("II.46.1", 1), ("II.46.2", 1), ("II.46.3", 3), ("II.47.1", 2), ("II.47.2", 2)]),
    # "The women did not leave the house" opens II.77.5, which Untermann renders in five sentences
    ("II.77.4", "II.77.5", [("II.77.4", 1), ("II.77.5", 5)]),
    # "This is a legal impossibility" ends VI.18.4; Untermann runs "Mommsen fühlt dies auch" into the quotation
    ("VI.18.4", "VI.19.1", [("VI.18.4", 2), ("VI.18.5", 1)]),
    # "The latter was everything, the former a negligible quantity" ends IX.9.11
    ("IX.9.10", "IX.9.12", [("IX.9.10", 3), ("IX.9.11", 3), ("IX.9.12", 1)]),
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
        if first == "P1891.9.4":
            v = group[1]
            v["review"] = True
            v["review_reason"] = "the English sentence also covers the first half of P1891.9.6 (\"still he proved their correctness\"); regrouped by the ingest (see REALIGN)"


# ---------------------------------------------------------------- writing

SRC_DE = "MEW 21, S. 25-173 (Dietz, Berlin 1962) via mlwerke.de; text of the fourth edition (Stuttgart 1892), 1884 readings as variants"
SRC_EN = "Ernest Untermann's translation (Charles H. Kerr, Chicago 1902; 1908 printing), Project Gutenberg ebook 33111 (public domain)"

PAGES = {"P1884": "me21_027.htm", "P1891": "me22_211.htm", "I": "me21_030.htm", "II": "me21_036.htm", "III": "me21_085.htm",
         "IV": "me21_098.htm", "V": "me21_107.htm", "VI": "me21_117.htm", "VII": "me21_127.htm", "VIII": "me21_141.htm",
         "IX": "me21_152.htm"}
TITLES_DE = {"P1884": "Vorwort zur ersten Auflage 1884", "P1891": "[Vorwort zur vierten Auflage 1891]",
             "I": "I. Vorgeschichtliche Kulturstufen", "II": "II. Die Familie", "III": "III. Die irokesische Gens",
             "IV": "IV. Die griechische Gens", "V": "V. Entstehung des athenischen Staats", "VI": "VI. Gens und Staat in Rom",
             "VII": "VII. Die Gens bei Kelten und Deutschen", "VIII": "VIII. Die Staatsbildung der Deutschen",
             "IX": "IX. Barbarei und Zivilisation"}
TITLES_EN = {"P1884": "Author's Preface to the First Edition, 1884", "P1891": "Author's Preface to the Fourth Edition, 1891"}
SRC_PREF = {"P1884": "MEW 21, S. 27-29 (Dietz, Berlin 1962) via mlwerke.de; preface to the first edition (Hottingen-Zürich 1884)",
            "P1891": "MEW 22, S. 211-222 (Dietz, Berlin 1963) via mlwerke.de; preface to the fourth edition (Stuttgart 1892), first printed in Die Neue Zeit, 1891"}
DATES = {"P1884": "1884-05", "P1891": "1891-06-16"}
VARIANT_EDITIONS = {"P1891": "1891 (Die Neue Zeit)"}


def meta(sid, title_de, title_en):
    return {"section": sid, "title_original": title_de, "title_en": title_en, "author": "Friedrich Engels",
            "date": DATES.get(sid, "1884-03/05; revised 1891"), "original_language": "de", "anchor_language": "de",
            "source_original": SRC_PREF.get(sid, SRC_DE), "source_en": SRC_EN}


def flags(vs):
    return sum(1 for v in vs if v.get("review"))


def build(sid, tmp, EN, en_notes, placed, report, clean_de):
    """Verses of one section, with notes, ready for dump()."""
    sig = r"^(London, |Friedrich Engels$)"
    de, notes, var, joins = parse_mew(PAGES[sid], tmp, signature_re=sig)
    for v in var.values():
        if not v["editions"]:
            v["editions"] = VARIANT_EDITIONS.get(sid, "1884")
    clean_de[sid] = {"paras": de, "notes": notes, "variants": var, "joined": joins}
    en = EN[sid]
    A = [P("heading", TITLES_DE[sid])] + [P(p["kind"], p["de"]) for p in de]
    title_en = en["title"] or EN_START[sid]
    B = [P("heading", title_en)] + [P(p["kind"], en_markers(p["text"], sid)) for p in en["paras"]]
    set_idf(A, B)
    vs, _ = build_section(sid, sid, "de", A, B, flat=True)
    realign(vs)
    for (s, ref), vid in UNLINKED_VARIANTS.items():
        if s == sid:
            v = next(x for x in vs if x["id"] == vid)
            words = versify.clean_text(v["_de_raw"]).split()[:4]
            v["de_variants"] = [{"ref": f"T{ref}", "editions": var[ref]["editions"], "reading": var[ref]["reading"],
                                 "base_text": "‸ " + " ".join(words) + " …"}]
    place_en_notes(vs, sid, en_notes, placed)
    attach_apparatus(vs, var, f"{sid}.", {})
    for nid, paras in notes.items():
        en_n = next((n for n, (s, k) in AUTHOR_NOTES.items() if s == sid and str(k) == nid), None)
        if en_n:
            nv = note_verses(f"{sid}.N{nid}", paras, author_note(en_notes[en_n]))
            attach_apparatus(nv, var, f"{sid}.N{nid}.", {})
            vs += nv
            placed.add(en_n)
        else:
            nv, _ = build_section("N", f"{sid}.N{nid}", "de", [P("note", t) for t in paras], [], single=True, para0_heading=False)
            attach_apparatus(nv, var, f"{sid}.N{nid}.", {})
            nv[0]["en_note"] = "Untermann's 1902 English does not translate this note."
            vs += nv
    vs = finalise(vs)
    report[sid] = (len(vs), flags(vs), sum(1 for v in vs if v["kind"] == "note"), len(A), len(B), joins)
    return vs, title_en


# VII: MEW's variant 1 (the 1884 edition lacks the chapter's opening up to "Hier nur einige kurze Notizen")
# has no link in the body of the mlwerke.de page; it belongs at the start of the chapter.
UNLINKED_VARIANTS = {("VII", "1"): "VII.1.1"}


def main():
    CLEAN.mkdir(parents=True, exist_ok=True)
    EN, en_notes = gutenberg()
    placed, total, report, clean_de, nflags = set(), 0, {}, {}, 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, sid in enumerate(SECTIONS):
            vs, title_en = build(sid, tmp, EN, en_notes, placed, report, clean_de)
            if sid.startswith("P"):
                path = WORK / "text" / "00-prefaces" / f"{sid[1:]}.yaml"
            else:
                path = WORK / "text" / "01-origin-of-the-family" / f"{i - 1}-{sid.lower()}.yaml"
            dump(path, meta(sid, TITLES_DE[sid], TITLES_EN.get(sid, title_en)), vs)
            total += len(vs)
    missing = set(en_notes) - placed
    assert not missing, sorted(missing)
    assert USED == {a for a, _ in CORRECTIONS_DE}, {a for a, _ in CORRECTIONS_DE} - USED
    assert USED_HTML == {(f, a) for f, a, _ in HTML_FIXES}
    assert USED_REALIGN == {r[0] for r in REALIGN}, {r[0] for r in REALIGN} - USED_REALIGN
    (CLEAN / "de.json").write_text(json.dumps(clean_de, ensure_ascii=False, indent=1), encoding="utf-8")
    (CLEAN / "en.json").write_text(json.dumps({"sections": EN, "notes": en_notes}, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, (n, f, nn, pa, pb, j) in report.items():
        print(f"{k:6} {n:5} verses {f:4} to review  {nn:3} note verses  paragraphs de {pa} en {pb}  joined {j}")
        nflags += f
    print("total", total, "verses", nflags, "to review")


if __name__ == "__main__":
    main()
