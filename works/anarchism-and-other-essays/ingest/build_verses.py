"""One-time ingest for Anarchism and Other Essays (AOE).

Emma Goldman wrote these essays in English and published them as a book with the Mother Earth
Publishing Association, New York, in 1910. So the original column IS the
English and there is no historical-translation column, as in VPP and CWF.

Source: Project Gutenberg ebook 2162 (plain ASCII text, produced by Eva), mirrored at
github.com/GITenberg/Anarchism-and-Other-Essays_2162. The transcription does not say which printing it
follows. It sets italics in capitals ("the LIVING John Browns") and has no accents. The capitals are kept
as transcribed; SOURCES.md explains why.

Sections:
  B        Hippolyte Havel's "Biographic Sketch" (headed "Emma Goldman" in the book), dated
           New York, December 1910. Paragraph 0 is its heading.
  P1910    Goldman's Preface.
  I to XII the twelve essays in the order of the book's contents. Goldman did not number them; the
           numbers are the library's. Paragraph 0 is the essay title.
Footnotes are numbered afresh in each essay and sit inside it as <essay>.N<number>, for example III.N2.

Verse quotations (Mackay, Wilde, the American anthem and others) keep their line breaks as " / ".
Attributions and datelines under a quotation are verses of kind `signature`.

Left out: the Gutenberg header and licence, the title page and the table of contents.

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

RAW = WORK / "sources" / "raw" / "en" / "gutenberg_2162.txt"
CLEAN = WORK / "sources" / "clean"

SRC = ("Emma Goldman, Anarchism and Other Essays, with a biographic sketch by Hippolyte Havel (New York: "
       "Mother Earth Publishing Association, 1910), public domain; Project Gutenberg ebook 2162")

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
# Headings as the book sets them over each essay (in capitals); written here in title case.
TITLES = ["Anarchism: What It Really Stands For", "Minorities Versus Majorities",
          "The Psychology of Political Violence", "Prisons: A Social Crime and Failure",
          "Patriotism: A Menace to Liberty", "Francisco Ferrer and The Modern School",
          "The Hypocrisy of Puritanism", "The Traffic in Women", "Woman Suffrage",
          "The Tragedy of Woman's Emancipation", "Marriage and Love",
          "The Modern Drama: A Powerful Disseminator of Radical Thought"]
SLUGS = ["anarchism", "minorities-versus-majorities", "psychology-of-political-violence", "prisons",
         "patriotism", "francisco-ferrer", "hypocrisy-of-puritanism", "traffic-in-women", "woman-suffrage",
         "tragedy-of-womans-emancipation", "marriage-and-love", "modern-drama"]

# Obvious errors in the transcription, listed in SOURCES.md. Applied to the joined paragraph text.
# Names and spellings that only look odd are kept.
CORRECTIONS = [
    ("men like Wendel Phillips", "men like Wendell Phillips"),        # B: letter dropped; "Wendell" in II
    ("framed by Josiah Warrn,", "framed by Josiah Warren,"),          # B: letter dropped
    ("THE BALLAD OF READING GOAL", "THE BALLAD OF READING GAOL"),      # IV: letters transposed
    ("in Galworthy's JUSTICE", "in Galsworthy's JUSTICE"),             # XII: letter dropped; "Galsworthy" elsewhere
]

# Local to this ingest; the shared rules in scripts/lib are not changed.
# Abbreviations that do not end a sentence here: "Wm. C. Owen", "Rev. Parkhurst", "Gen. Funston",
# "Mlle. Meunier", "Prof. Ehrlich", "the Reliance-Sterling Mfg. Co.".
segment.ABBR["en"] = segment.ABBR["en"] | {"Wm", "Rev", "Gen", "Mlle", "Prof", "Mfg"}
# Sentence ends the shared splitter cannot see (an abbreviation or a number before the full stop):
# split between the two halves of each pair. Each pair occurs once in the book.
EN_BREAKS = [
    ("No.", "Did they all three"),                     # III.13: "No." as an answer
    ("No.", "The Mazzinians were"),
    ("Russians, etc.", "When the child"),              # V.6
    ("in Japan from 12 to 14.", "On the other hand"),  # V.11
    ("$16.40 for 1901-5.", "It is morally certain"),   # V.12
    ("saloons, etc.", "And what is the result"),       # VIII.2
    ("trades, etc.", "What wonderful accomplishment"),  # IX.35
]
# Book titles in the footnotes stay with the author's name that follows them
# ("CRIME AND CRIMINALS. W. C. Owen.").
EN_NOBREAKS = ["CRIME AND CRIMINALS.", "THE PSYCHOLOGY OF SEX.", "EQUAL SUFFRAGE."]
BREAKS_USED = set()
# Signatures, attributions and datelines: one verse each, never split.
SIGNATURES = ["GEORGE JACOB HOLYOAKE.", "HIPPOLYTE HAVEL.", "New York, December, 1910.", "Emma Goldman",
              "JOHN HENRY MACKAY.", "The Prison Cell, Oct. 4, 1909.", "FERRER."]
SIG_SEEN = []
# The title of Mackay's poem at the head of essay I is a heading of its own, as in CB's subsections.
HEADINGS = ["ANARCHY."]


def _split(text, lang):
    out = segment.split_sentences(text, lang)
    for a, b in EN_BREAKS:
        res = []
        for s in out:
            k = s.find(a + " " + b)
            if k >= 0:
                BREAKS_USED.add((a, b))
                res += [s[:k + len(a)].strip(), s[k + len(a):].strip()]
            else:
                res.append(s)
        out = res
    merged = []
    for s in out:              # a split the shared rules make inside a citation: rejoin it
        if merged and any(merged[-1].endswith(nb) for nb in EN_NOBREAKS):
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)
    return merged


def _para_sentences(text, lang, kind):
    if kind in ("heading", "signature"):
        return [text]
    return _split(text, lang)


versify.para_sentences = _para_sentences

USED = set()
# Signatures, attributions and datelines: one verse each, never split.
SIGNATURES = ["GEORGE JACOB HOLYOAKE.", "HIPPOLYTE HAVEL.", "New York, December, 1910.", "Emma Goldman",
              "JOHN HENRY MACKAY.", "The Prison Cell, Oct. 4, 1909.", "FERRER."]
SIG_SEEN = []
# The title of Mackay's poem at the head of essay I is a heading of its own, as in CB's subsections.
HEADINGS = ["ANARCHY."]
# First lines of the verse quotations; their line breaks are kept as " / ".
POEMS = ["Ever reviled, accursed, ne'er understood,", "My country, 'tis of thee,",
         "The vilest deeds, like poison weeds,", "Out of his mouth a red, red rose!",
         "A dying age and a living truth,"]


# ---------------------------------------------------------------- reading the Gutenberg text

def load():
    t = RAW.read_bytes().decode("ascii").replace("\r", "")
    lines = t.split("\n")
    start = lines.index("EMMA GOLDMAN")
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


def join(lines, poem=False):
    s = (" / " if poem else " ").join(x.strip() for x in lines)
    s = re.sub(r"\[(\d+)\]", r" [[F\1]]", s)
    s = re.sub(r"\s+", " ", s).strip()
    return fix(s)


def paras_of(block):
    """One block of the transcription -> list of paragraphs. Splits off attributions set far to the right."""
    first = block[0].strip()
    sig = []
    while len(block) > 1 and re.match(r"^ {25,}\S", block[-1]):
        sig.insert(0, block[-1].strip())
        block = block[:-1]
    if first in POEMS:
        out = [P("p", join(block, poem=True))]
    else:
        t = join(block)
        out = [P("signature" if t in SIGNATURES else "heading" if t in HEADINGS else "p", t)]
    out += [P("signature", join([s])) for s in sig]
    SIG_SEEN.extend(p["text"] for p in out if p["kind"] == "signature")
    return out


def parse():
    bl = blocks(load())
    heads = {}
    for i, b in enumerate(bl):
        t = " ".join(x.strip() for x in b)
        if t == "EMMA GOLDMAN":
            heads["B"] = i
        elif t == "PREFACE":
            heads["P1910"] = i
        elif t in [x.upper() for x in TITLES]:
            heads[ROMAN[[x.upper() for x in TITLES].index(t)]] = i
    order = ["B", "P1910"] + ROMAN
    assert list(heads) == order, list(heads)
    idx = [heads[k] for k in order] + [len(bl)]
    secs = {}
    for k, a, b in zip(order, idx, idx[1:]):
        secs[k] = bl[a + 1:b]
    return secs


def section(sid, bl):
    """Body paragraphs and footnotes of one section."""
    body, notes, cur = [], {}, None
    for b in bl:
        t = " ".join(x.strip() for x in b)
        m = re.match(r"^\[(\d+)\] ", t)
        if m:
            cur = int(m.group(1))
            assert cur == len(notes) + 1, (sid, cur)
            notes[cur] = [P("note", join(b)[len(f"[[F{cur}]]"):].strip())]
            continue
        assert cur is None, (sid, t[:60])     # notes come last
        body += paras_of(b)
    refs = [int(n) for p in body for n in re.findall(r"\[\[F(\d+)\]\]", p["text"])]
    assert refs == list(range(1, len(notes) + 1)) == sorted(notes), (sid, refs, sorted(notes))
    return body, notes


# ---------------------------------------------------------------- writing

def meta(sid, title, author, date):
    return {"section": sid, "title_original": title, "title_en": title, "author": author, "date": date,
            "original_language": "en", "anchor_language": "en", "source_original": SRC,
            "source_en": "None needed: the original is in English"}


def number(sid, paras, para0_heading=True):
    vs, _ = build_section(sid, sid, "de", paras, [], lang_a="en", single=True, para0_heading=para0_heading)
    attach_apparatus(vs, {}, f"{sid}.", {})
    return vs


def main():
    secs = parse()
    files = {"B": ("00-front/1-biographic-sketch.yaml", "Emma Goldman", "Biographic Sketch", "Hippolyte Havel", "1910-12"),
             "P1910": ("00-front/2-preface.yaml", "Preface", "Preface", "Emma Goldman", "1910")}
    for i, sid in enumerate(ROMAN):
        files[sid] = (f"01-essays/{i + 1:02d}-{sid.lower()}-{SLUGS[i]}.yaml", TITLES[i], TITLES[i], "Emma Goldman", "1910")
    clean, total, counts = {}, 0, {}
    for sid, bl in secs.items():
        fname, heading, title, author, date = files[sid]
        body, notes = section(sid, bl)
        vb = number(sid, [P("heading", heading)] + body)
        vn = []
        for n, paras in notes.items():
            vn += number(f"{sid}.N{n}", paras, para0_heading=False)
        vs = finalise(vb + vn)
        dump(WORK / "text" / fname, meta(sid, title, author, date), vs)
        counts[sid] = (len(body), len(vb), len(notes), len(vn))
        total += len(vs)
        clean[sid] = {"body": [p["text"] for p in body], "notes": {str(n): [p["text"] for p in ps] for n, ps in notes.items()}}
        print(f"{sid:6} {len(body):4} paragraphs {len(vb):5} verses   notes {len(notes):2} {len(vn):4} verses")
    missing = [a for a, _ in CORRECTIONS if a not in USED]
    assert not missing, missing
    assert SIG_SEEN == SIGNATURES, SIG_SEEN
    assert BREAKS_USED == set(EN_BREAKS), set(EN_BREAKS) - BREAKS_USED
    print("total", total)
    CLEAN.mkdir(parents=True, exist_ok=True)
    (CLEAN / "en.json").write_text(json.dumps(clean, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
