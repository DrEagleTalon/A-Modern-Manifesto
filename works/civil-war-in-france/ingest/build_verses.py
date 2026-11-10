"""One-time ingest for The Civil War in France (CWF).

Marx wrote all three addresses of the General Council of the International in English:
    A1  First Address on the Franco-Prussian War, 23 July 1870
    A2  Second Address on the Franco-Prussian War, 9 September 1870
    I-IV  The Civil War in France, read to the General Council on 30 May 1871, in its four numbered parts
    N1 N2  Marx's two notes printed after the 1871 Address (newspaper reports of the massacres; the
           General Council's letter to The Times on Jules Favre's circular)
So the original column IS the English and there is no historical-translation column.

The exception is P1891, Engels's introduction to the third German edition (Berlin 1891), which Engels wrote
in German. Its original column holds the German (MEW 22, pp. 188-199) and its English column is empty: the
Marxists Internet Archive English of it is abridged and of uncertain rights.

Engels's 1871 German translation of the Address (MEW 17) is fetched but not used: it is a translation, and the
work has no column for it. Its one footnote (on "tickets-of-leave") is Engels's note to the German edition and
is not in the English original, so it is left out too.

English source: the Marxists Internet Archive transcription of the 1871 English edition (Zodiac and Brian
Baggins; proofed by Matthew Carmody 2009). Everything MIA adds in square brackets (chapter titles
and glosses) is dropped with its endnotes; the removed glosses are logged in sources/clean/. Wrong
readings in MIA are fixed only through CORRECTIONS, each listed in SOURCES.md.

Run once; after the lock file exists the YAML in text/ is the source of truth.
"""
import json
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
REPO = WORK.parents[1]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
from mew import parse_mew, parse_mia  # noqa: E402
import versify  # noqa: E402
from versify import P, attach_apparatus, build_section, dump, finalise  # noqa: E402

# The shared splitter ends a sentence after a three-digit number ("... in 1848."). In P1891.13 that is wrong
# once: "durch das 137. Bataillon der Nationalgarde". Rejoin it here rather than change scripts/lib.
JOIN_AFTER = ("durch das 137.",)
_split = versify.split_sentences


def split_sentences(text, lang):
    out = []
    for s in _split(text, lang):
        if out and out[-1].endswith(JOIN_AFTER):
            out[-1] = out[-1] + " " + s
        else:
            out.append(s)
    return out


versify.split_sentences = split_sentences

RAW = WORK / "sources" / "raw"
CLEAN = WORK / "sources" / "clean"
SRC_EN = ("Karl Marx for the General Council of the International Working Men's Association, English editions of "
          "1870 and 1871, public domain; Marxists Internet Archive transcription (Zodiac and Brian Baggins, "
          "proofed by Matthew Carmody 2009; CC BY-SA)")
SRC_DE = "MEW 22, S. 188-199 (Dietz, Berlin) via mlwerke.de; Engels, original German, after the third German edition, Berlin 1891"

# Repairs to the MIA English, each listed in SOURCES.md. (old, new); every old string must occur.
CORRECTIONS = [
    ("The war plot of July [19] 1870", "The war plot of July 1870"),               # MIA's added date
    ("as foreseen by Voltaire.(See news articles)", "as foreseen by Voltaire."),  # MIA's link to the notes
    ("the Anti-Jacobin war [1792] and", "the Anti-Jacobin war and"),               # MIA's added years
    ("until the June [1848] massacres", "until the June massacres"),
    ("used it for the June [1848] massacres", "used it for the June massacres"),
    ("and the jail- accoucheur", "and the jail-accoucheur"),
    ("to France: ‘These are criminals!", "to France: 'These are criminals!"),
    ("victory of defeat will prove", "victory or defeat will prove"),
    ("in numbers unequally in any battle", "in numbers unequalled in any battle"),
    ("expulsion for the Paris bar", "expulsion from the Paris bar"),
    ("In September 4, 1870, when the working men", "On September 4, 1870, when the working men"),
    ("The women, rushing out of the ranks", "The woman, rushing out of the ranks"),
    ("\"Sir. - On June 6, 1871", "\"Sir, - On June 6, 1871"),       # the salutation is not a sentence
    # words MIA dropped, restored as the sentences read in the standard editions
    ("The state power, apparently soaring high above society and the very hotbed",
     "The state power, apparently soaring high above society, was at the same time itself the greatest scandal of that society and the very hotbed"),
    ("regulate national production upon common plan", "regulate national production upon a common plan"),
    ("Theirs, that monstrous gnome", "Thiers, that monstrous gnome"),
    ("the petty strategems", "the petty stratagems"),
    ("its last hinderances", "its last hindrances"),
    ("not only to supercede the monarchical", "not only to supersede the monarchical"),
    ("than to supercede universal suffrage", "than to supersede universal suffrage"),
    ("parasitic excresence", "parasitic excrescence"),
    ("irresistably tending", "irresistibly tending"),
    ("its literary bonhome", "its literary bohème"),
    ("the International was found \"September 28", "the International was founded \"September 28"),
    ("This sort of maneuvre", "This sort of manoeuvre"),
    ("quoted by Jules favre", "quoted by Jules Favre"),
    ("before the laws courts", "before the law courts"),
    # signature block of the 1871 Address: MIA ran a two-column list of names into one line
    ("A. Ser- Railler", "A. Serraillier"),
    ("Eugene Dupont, For France Zevy Maurice, For Hungary Karl Marx, For Germany And Anton Zabicki, For Poland Holland "
     "James Cohen, For Denmark Fred. Engels, For Belgium And J.G. Eccarius, For The United Spain States Hermann Jung, "
     "For Switzerland P. Giovacchini, For Italy",
     "Eugene Dupont, for France; Karl Marx, for Germany and Holland; Fred. Engels, for Belgium and Spain; "
     "Hermann Jung, for Switzerland; P. Giovacchini, for Italy; Zevy Maurice, for Hungary; Anton Zabicki, for Poland; "
     "James Cohen, for Denmark; J.G. Eccarius, for the United States"),
    ("Hermann Jung, Chairman John Weston, Treasurer George Harris, Financial Secretary J. George Eccarius, General Secretary",
     "Hermann Jung, Chairman; John Weston, Treasurer; George Harris, Financial Secretary; J. George Eccarius, General Secretary"),
]
# Repairs to the MEW German (transcription slips at mlwerke.de), listed in SOURCES.md.
CORRECTIONS_DE = [
    ("Am 31.Oktober", "Am 31. Oktober"),
    ("- Am 1.April", "- Am 1. April"),
    ("auf der Westfront vor, Paris, bemächtigt", "auf der Westfront vor Paris, bemächtigt"),
]
USED = set()

# paragraphs set as signatures (not split into sentences, not translated as prose)
SIGNATURES = ("Vive la Republique!", "The General Council", "M. J. Boon,", "Corresponding Secretaries:", "Eugene Dupont,",
              "Hermann Jung, Chairman", "Office: 256 High Holborn", "I am, Sir, your obedient servant", "London", "June 12th, 1871")
MIA_HEADINGS = ("The First Address", "The Second Address", "The Third Address", "News Stories", "June 8-12, 1871")


def fix(text, table):
    for a, b in table:
        if a in text:
            text = text.replace(a, b)
            USED.add(a)
    return text


def english(name, log):
    paras, removed = parse_mia(RAW / "en" / f"{name}.html")
    log[name] = removed
    out = []
    for p in paras:
        t = fix(p["text"], CORRECTIONS).strip()
        t = re.sub(r"(?<= )\u2013(?= |$)", "-", t)     # MIA's spaced en dash, as parse_mia does mid-line
        if not t or not re.search(r"[A-Za-z]", t):
            continue                    # MIA's "[...]" lines and emptied bracket headings
        if p["kind"] == "heading":
            if t in ("Authors Notes", "Editorial Notes"):
                break                   # MIA's endnotes follow
            if t.startswith(MIA_HEADINGS):
                continue
        kind = p["kind"]
        if kind == "p" and (t.startswith(SIGNATURES) and (len(t) < 200 or t.startswith(("M. J. Boon", "Eugene Dupont")))):
            kind = "signature"
        out.append({"kind": kind, "text": t})
    return out


def meta(section, title, date, author="Karl Marx", lang="en"):
    if lang == "en":
        return {"section": section, "title_original": title, "title_en": title, "author": author, "date": date,
                "original_language": "en", "anchor_language": "en", "source_original": SRC_EN,
                "source_en": "None needed: the original is in English"}
    return {"section": section, "title_original": title, "title_en": "Introduction by Frederick Engels (1891 edition)",
            "author": author, "date": date, "original_language": "de", "anchor_language": "de", "source_original": SRC_DE,
            "source_en": "None: no public-domain English translation of this introduction is used yet"}


def write(sid, heading, paras, fname, title, date, counts):
    A = [P("heading", heading)] + [P(p["kind"], p["text"]) for p in paras]
    vs, _ = build_section(sid, sid, "de", A, [], lang_a="en", single=True)
    attach_apparatus(vs, {}, "", {})
    vs = finalise(vs)
    dump(WORK / "text" / fname, meta(sid, title, date), vs)
    counts[sid] = (len(A), len(vs))
    print(sid, len(A), "paragraphs", len(vs), "verses")
    return vs


def main():
    CLEAN.mkdir(parents=True, exist_ok=True)
    log, counts = {}, {}

    # ---------------- P1891: Engels's introduction, German original
    de, notes, variants = parse_mew(RAW / "de" / "me22_188.htm", signature_re=r"^(London, am|F\. Engels)")
    assert not notes and not variants
    # drop the rule of dashes that separates the narrative from the analysis (no words, nothing to translate)
    de = [p for p in de if re.search(r"[A-Za-zÄÖÜäöüß]", re.sub(r"\[\[[A-Z]\d+\]\]", "", p["de"]))]
    for p in de:
        p["de"] = fix(p["de"], CORRECTIONS_DE)
    A = [P("heading", "Einleitung [zu \"Der Bürgerkrieg in Frankreich\" von Karl Marx (Ausgabe 1891)]")] + [P(p["kind"], p["de"]) for p in de]
    vs, _ = build_section("P1891", "P1891", "de", A, [], single=True)
    attach_apparatus(vs, {}, "P1891.", {})
    vs = finalise(vs)
    dump(WORK / "text" / "00-introduction" / "1891.yaml",
         meta("P1891", A[0]["text"], "1891-03-18", "Friedrich Engels", "de"), vs)
    counts["P1891"] = (len(A), len(vs))
    print("P1891", len(A), "paragraphs", len(vs), "verses")

    # ---------------- the two addresses on the war
    write("A1", "The First Address, July 23, 1870", english("ch01", log), "01-addresses-on-the-war/1-first-address.yaml",
          "First Address of the General Council on the Franco-Prussian War", "1870-07-23", counts)
    write("A2", "The Second Address, September 9, 1870", english("ch02", log), "01-addresses-on-the-war/2-second-address.yaml",
          "Second Address of the General Council on the Franco-Prussian War", "1870-09-09", counts)

    # ---------------- The Civil War in France, parts I-IV
    for i, (sid, ch) in enumerate([("I", "ch03"), ("II", "ch04"), ("III", "ch05"), ("IV", "ch06")], start=1):
        write(sid, sid, english(ch, log), f"02-civil-war-in-france/{i}-{sid.lower()}.yaml",
              f"The Civil War in France, part {sid}", "1871-05-30", counts)

    # ---------------- Marx's notes I and II after the Address
    notes, cur = {}, None
    for p in english("news", log):
        if p["kind"] == "heading" and p["text"] in ("I", "II"):
            cur = p["text"]
            notes[cur] = []
            continue
        notes[cur].append(p)
    assert list(notes) == ["I", "II"], list(notes)
    write("N1", "I", notes["I"], "02-civil-war-in-france/5-note-i.yaml", "The Civil War in France, note I", "1871-06", counts)
    write("N2", "II", notes["II"], "02-civil-war-in-france/6-note-ii.yaml", "The Civil War in France, note II", "1871-06", counts)

    missing = [a for a, _ in CORRECTIONS + CORRECTIONS_DE if a not in USED]
    assert not missing, missing
    (CLEAN / "mia_insertions_removed.json").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    print("total", sum(v for _, v in counts.values()), "verses;", "paragraphs:", {k: v[0] for k, v in counts.items()})


if __name__ == "__main__":
    main()
