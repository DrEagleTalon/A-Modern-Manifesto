"""One-time ingest for Critique of the Gotha Programme (CGP).

German  Marx's letter to Bracke and his marginal notes (MEW 19, pp. 13-32, Dietz, Berlin 1962), printed in
        MEW from Marx's manuscript, with the 1891 Neue Zeit readings as variants and the passages Engels
        left out in 1891 in angle brackets < >. Text from the zeno.org transcription of MEW 19 as mirrored
        by MARX-EBOOKS (docs/MEW-ZENO/19/ME19-013.html and ME19-015.html). The mlwerke.de page of the same
        volume (me19_013.htm) is kept as a collation copy only: whoever converted it read MEW's angle
        brackets as HTML tags, so eleven bracketed passages, and with them several whole paragraphs, are
        missing or scrambled there. Engels's foreword of 1891 (MEW 22, pp. 90-91) comes from mlwerke.de,
        whose page for it is sound.
English None. No public-domain English is on a reachable mirror yet; the modern draft is translated
        from the German.

Sections:
  P1891  Engels's foreword to the first printing (Die Neue Zeit, 1891).
  B      Marx's covering letter to Wilhelm Bracke, 5 May 1875.
  I to IV  the marginal notes, by Marx's own numerals. In I, paragraph 0 holds two headings: the title of
           the notes (I.0.1) and the numeral (I.0.2). In the other sections paragraph 0 is the numeral.
The passages of the Gotha draft that Marx quotes before commenting are ordinary paragraphs (kind p).

Run once. After the lock file exists the YAML in text/ is the source of truth.
"""
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

WORK = Path(__file__).resolve().parents[1]
REPO = WORK.parents[1]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
import segment  # noqa: E402
import versify  # noqa: E402
from mew import parse_mew  # noqa: E402
from versify import P, attach_apparatus, build_section, dump, finalise  # noqa: E402

RAW = WORK / "sources" / "raw" / "de"
SRC_ZENO = ("MEW 19, S. {pages} (Dietz, Berlin 1962), zeno.org transcription via the MARX-EBOOKS mirror; "
            "from Marx's manuscript, 1891 readings as variants, passages left out in 1891 in < >")
SRC_EN = "None: no public-domain English translation on a reachable mirror yet"

# Local to this ingest; the shared rules in scripts/lib are not changed.
segment.ABBR["de"] = segment.ABBR["de"] | {"sog"}

# Transcription slips in the zeno.org text, repaired here and listed in SOURCES.md. Each repair agrees with
# the mlwerke.de transcription of MEW 19 and, where that page has the passage, with a third transcription
# (MARX-EBOOKS MEW/19/ME19-015.html).
CORRECTIONS = [
    ("von hier auslenken", "von hier aus lenken"),
    ("von den Verfechtern[[T3]]", "von den Vorfechtern[[T3]]"),   # the 1891 variant itself reads "Verfechtern"
    ("diese Mißstände zu vermelden", "diese Mißstände zu vermeiden"),
    ("schreiben: jeder nach seinen Fähigkeiten", "schreiben: Jeder nach seinen Fähigkeiten"),
    ("Ich bin weltläufiger", "Ich bin weitläufiger"),
    ("großen Industrie - gegen über Feudalen", "großen Industrie - gegenüber Feudalen"),
    ("das Heilsmittel des Propheten", "das Heilmittel des Propheten"),
    ("zeigen schon die Worte:\"Die", "zeigen schon die Worte: \"Die"),
]

# A MEW page start that the zeno.org page has no anchor for, taken from the mlwerke.de copy (|25|).
# The starts of pages 16, 27 and 28 are marked in neither copy; verses there carry the page before.
PAGE_FIXES = [
    ('an Lassalles "ehernes Lohngesetz" zu glauben', 'an Lassalles "ehernes [[S25]] Lohngesetz" zu glauben'),
]


# ---------------------------------------------------------------- zeno.org pages

def _clean(fragment):
    fragment = re.sub(r"<br\s*/?>", " ", fragment)
    s = BeautifulSoup(fragment, "html.parser").get_text("")
    s = s.replace("\xa0", " ").replace("\xad", "").replace("﻿", "")
    for a, b in (("»", '"'), ("«", '"'), ("„", '"'), ("“", '"'), ("‹", "<"), ("›", ">"), ("–", "-")):
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:!?)])", r"\1", s)
    s = re.sub(r"\(\s+", "(", s)
    return s


def parse_zeno(name):
    """Paragraphs and variants of a zeno.org MEW page. Inline markers as in parse_mew:
    [[S17]] page 17 starts here, [[T2]] 1891 variant A2 attaches here."""
    html = (RAW / name).read_text(encoding="utf-8")
    body, _, aside = html.partition("<aside")
    variants = {}
    for m in re.finditer(r'<p class="fni"><a [^>]*id="fnA(\d+)">A\d+</a>\s*<i>\((\d{4})\)</i>\s*(.*?)</p>', aside, re.S):
        variants[m.group(1)] = {"editions": m.group(2), "reading": _clean(m.group(3))}
    body = re.sub(r'<sup><a href="#fnA(\d+)"[^>]*>A\d+</a></sup>', r"[[T\1]]", body)
    # zeno.org anchors mark where a page ENDS (<a id="S17"> stands where MEW page 18 begins), except an anchor
    # at the head of a section, which names the page the section starts on. Turn both into page starts.
    body = re.sub(r'(<(?:p|h4|blockquote)\b[^>]*>\s*)<a id="S(\d+)"></a>', r"\1 [[S\2]] ", body)
    body = re.sub(r'<a id="S(\d+)"></a>(?=\s*(?:<h4|<p\b))', lambda m: f" [[S{m.group(1)}]] ", body)
    body = re.sub(r'<a id="S(\d+)"></a>', lambda m: f" [[S{int(m.group(1)) + 1}]] ", body)
    body = re.sub(r"(\w+)-\s*(\[\[S\d+\]\])\s*([a-zäöüß])", r"\2 \1\3", body)   # word broken at a page
    paras, pending, pos = [], "", 0
    for m in re.finditer(r"<(h4|p|blockquote)\b([^>]*)>(.*?)</\1>", body, re.S):
        between = body[pos:m.start()]
        pending += " ".join(re.findall(r"\[\[S\d+\]\]", between))
        pos = m.end()
        tag, attr, inner = m.groups()
        if 'class="que"' in attr:
            continue
        text = _clean(pending + " " + inner)
        pending = ""
        tail = re.search(r"(?:\s*\[\[S\d+\]\])+$", text)     # a page that starts after the paragraph
        if tail:
            pending, text = tail.group(0).strip(), text[:tail.start()].rstrip()
        if not re.sub(r"\[\[[A-Z]\d+\]\]", "", text).strip():
            pending = (text + " " + pending).strip()
            continue
        kind = "heading" if tag == "h4" else ("signature" if 'class="rgt"' in attr else "p")
        for a, b in CORRECTIONS + PAGE_FIXES:
            text = text.replace(a, b)
        paras.append(P(kind, text))
    # a page that would start after the last paragraph is dropped: nothing of the text is on it.
    # A page anchor on the first paragraph under a section numeral belongs to the numeral.
    for h, p in zip(paras, paras[1:]):
        m = re.match(r"^((?:\[\[S\d+\]\]\s*)+)", p["text"])
        if h["kind"] == "heading" and m:
            h["text"], p["text"] = m.group(1).strip() + " " + h["text"], p["text"][m.end():]
    return paras, variants


# ---------------------------------------------------------------- sentences

def _split(text, lang):
    """The shared splitter, plus rules kept local to this work:
    - a sentence may end inside or just before one of MEW's angle-bracket passages ("hält. <Man wollte
      ... lassen.> Man weiß"); the shared rules only look for quotes and brackets there;
    - "etc." ends the sentence when a capital follows, except in "die materiellen etc. Bedingungen";
    - a quoted answer in lower case after a question mark stays with the question (I.61.2);
    - a page marker between two sentences moves to the start of the second."""
    out = []
    for s in segment.split_sentences(text, lang):
        parts = re.split(r"(?<=[.!?])\s+(?=<[A-ZÄÖÜ\"])|(?<=[.!?]>)\s+(?=[A-ZÄÖÜ\"<])|(?<=\betc\.)\s+(?=[A-ZÄÖÜ])(?!Bedingungen)", s)
        for p in parts:
            if out and p and re.match(r'^"[a-zäöüß]', p) and out[-1].endswith("?"):
                out[-1] += " " + p                        # 'was? "die Arbeit".' is one sentence
            elif p:
                out.append(p)
    # a page that starts between two sentences belongs to the second one
    for i in range(len(out) - 1):
        m = re.search(r"(?:\s*\[\[S\d+\]\])+$", out[i])
        if m:
            out[i], out[i + 1] = out[i][:m.start()].rstrip(), m.group(0).strip() + " " + out[i + 1]
    return out


versify.split_sentences = _split


# ---------------------------------------------------------------- build

def meta(sid, title_original, title_en, author, date, source):
    return {"section": sid, "title_original": title_original, "title_en": title_en, "author": author, "date": date,
            "original_language": "de", "anchor_language": "de", "source_original": source, "source_en": SRC_EN}


def section(sid, paras, variants, page, pids=None):
    vs, _ = build_section(sid, sid, "de", paras, [], single=True, pids=pids)
    attach_apparatus(vs, variants, f"{sid}.", {"p": page})
    return finalise(vs)


def main():
    out = WORK / "text"
    total, counts = 0, {}

    # Engels's foreword, MEW 22
    de_f, notes, var = parse_mew(RAW / "me22_090.htm", signature_re=r"^(London|Fr\. Engels)")
    assert not notes and not var
    A = [P("heading", "[Vorwort zu Karl Marx' \"Kritik des Gothaer Programms\"]")] + [P(p["kind"], p["de"]) for p in de_f]
    vs = section("P1891", A, {}, "90")
    for v in vs:
        v["en_note"] = "No public-domain English of this foreword is used." if v["id"] == "P1891.0.1" else v.get("en_note")
        if v["en_note"] is None:
            del v["en_note"]
    dump(out / "00-foreword" / "1891.yaml",
         meta("P1891", A[0]["text"], "Engels's foreword (1891)", "Friedrich Engels", "1891-01-06",
              "MEW 22, S. 90-91 (Dietz, Berlin 1963) via mlwerke.de; from Die Neue Zeit, 9. Jg., 1. Bd., Nr. 18, 1890-1891"), vs)
    counts["P1891"] = len(vs)

    # Letter to Bracke, MEW 19 pp. 13-14
    letter, var_b = parse_zeno("ME19-013.html")
    assert letter[0]["kind"] == "heading" and not var_b
    vs = section("B", letter, {}, "13")
    dump(out / "01-letter" / "bracke.yaml",
         meta("B", letter[0]["text"], "Letter to Wilhelm Bracke", "Karl Marx", "1875-05-05", SRC_ZENO.format(pages="13-14")), vs)
    counts["B"] = len(vs)

    # Marginal notes, MEW 19 pp. 15-32
    notes_p, variants = parse_zeno("ME19-015.html")
    assert versify.clean_text(notes_p[0]["text"]).startswith("Randglossen") and versify.clean_text(notes_p[1]["text"]) == "I"
    secs, cur = [], None
    for i, p in enumerate(notes_p):
        numeral = versify.clean_text(p["text"])
        if p["kind"] == "heading" and re.fullmatch(r"\[?(I|II|III|IV)\]?", numeral):
            cur = {"sid": numeral.strip("[]"), "paras": [p] if i > 1 else [notes_p[0], p]}
            secs.append(cur)
        elif cur:
            cur["paras"].append(p)
    assert [s["sid"] for s in secs] == ["I", "II", "III", "IV"], [s["sid"] for s in secs]
    titles = {"I": "Marginal notes, I", "II": "Marginal notes, II", "III": "Marginal notes, III", "IV": "Marginal notes, IV"}
    page = "15"
    for n, s in enumerate(secs, start=1):
        sid, paras = s["sid"], s["paras"]
        pids = [f"{sid}.0", f"{sid}.0"] + [f"{sid}.{k}" for k in range(1, len(paras) - 1)] if sid == "I" else None
        vs = section(sid, paras, variants, page, pids=pids)
        if sid == "I":
            vs[1]["id"] = "I.0.2"
        last = [v.get("mew_page") for v in vs if v.get("mew_page")][-1]
        page = last.split("-")[-1]
        title_o = versify.clean_text(paras[1]["text"] if sid == "I" else paras[0]["text"])
        dump(out / "02-marginal-notes" / f"{n}-{sid.lower()}.yaml",
             meta(sid, f"Randglossen zum Programm der deutschen Arbeiterpartei, {title_o}", titles[sid], "Karl Marx",
                  "1875-04/05", SRC_ZENO.format(pages="15-32")), vs)
        counts[sid] = len(vs)
    total = sum(counts.values())
    print("CGP", total, "verses:", counts)
    joined = "\n".join(p["text"] for p in letter + notes_p)
    for a, b in CORRECTIONS + PAGE_FIXES:
        assert b in joined and (a in b or a not in joined), f"repair not applied: {a!r}"
    found = set()
    for p in notes_p:
        found |= set(re.findall(r"\[\[T(\d+)\]\]", p["text"]))
    print("variants placed:", len(found), "of", len(variants), "; not in the text:", sorted(set(variants) - found, key=int))


if __name__ == "__main__":
    main()
