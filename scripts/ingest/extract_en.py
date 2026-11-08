"""Extract the English text (Moore/Engels 1888 translation + prefaces) into clean paragraph JSON.

Input:  sources/raw/en/mia_manifesto_1888.txt
        (Marxists Internet Archive transcription, proofed against the 1888 English
        edition by Andy Blunden 2004; one paragraph per line; footnotes at the end)
Output: sources/clean/en.json

Footnote markers (* † ‡) are converted to [[note-id]] markers using the fixed
mapping below, so they line up with the German note numbers from MEW.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "sources" / "raw" / "en" / "mia_manifesto_1888.txt"

PREFACE_HEADINGS = {
    "Preface to The 1872 German Edition": "P1872",
    "Preface to The 1882 Russian Edition": "P1882",
    "Preface to The 1883 German Edition": "P1883",
    "Preface to The 1888 English Edition": "P1888",
    "Preface to The 1890 German Edition": "P1890",
    "Preface to The 1892 Polish Edition": "P1892",
    "Preface to The 1893 Italian Edition": "P1893",
}

# Order in which footnote markers occur in the text -> note id.
# German MEW numbers the Manifesto notes (1)-(8); "E1" is an English-only note
# (Engels explains the English word "guild-master"; there is no German counterpart).
MARKER_ORDER = [
    ("P1883", "F1"), ("P1888", "F1"),
    ("CM", "F1"), ("CM", "F2"), ("CM", "E1"), ("CM", "F3"), ("CM", "F4"),
    ("CM", "F5"), ("CM", "F6"), ("CM", "F7"), ("CM", "F8"),
]

SIGNATURE = re.compile(r"^(Karl Marx|Frederick Engels|F\. Engels|[A-Z][a-z]+ \d{1,2}, \d{4}, London|London, [A-Z][a-z]+ \d{1,2}, \d{4})")


# Obvious transcription slips in the MIA text, corrected here and listed in SOURCES.md.
CORRECTIONS = [
    ("national independence Therefore", "national independence. Therefore"),
]


def clean(s: str) -> str:
    for a, b in CORRECTIONS:
        s = s.replace(a, b)
    s = s.replace("﻿", "").replace("\xa0", " ").strip()
    s = re.sub(r"(?<=[a-z!.,])\d(?=[\s,;:.]|$)", "", s)    # MIA end-note numbers glued to words
    s = re.sub(r"(\w)' s\b", r"\1's", s)                      # PDF artefact: "men' s"
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def main():
    lines = SRC.read_text(encoding="utf-8").split("\n")
    body, notes_raw = [], []
    in_notes = False
    for ln in lines:
        t = clean(ln)
        if not t:
            continue
        if re.match(r"^[*†‡]\s", t) and len(t) > 40:
            in_notes = True
        if in_notes:
            if re.match(r"^[*†‡]\s", t):
                notes_raw.append([re.sub(r"^[*†‡]\s*", "", t)])
            else:
                notes_raw[-1].append(t)
        else:
            body.append(t)

    secs = {}
    cur = None
    marker_i = 0
    for t in body:
        if t in PREFACE_HEADINGS:
            cur = PREFACE_HEADINGS[t]
            secs[cur] = {"id": cur, "paragraphs": [{"kind": "heading", "en": t}]}
            continue
        if t == "Manifesto of the Communist Party":
            cur = "CM"
            secs[cur] = {"id": cur, "paragraphs": [{"kind": "heading", "en": t}]}
            continue
        kind = "p"
        if cur == "CM" and (re.match(r"^(I|II|III|IV)\. [A-Z][a-z]", t) and len(t) < 110 and not t.endswith(".")
                            or re.match(r"^(\d\.|[ABC]\.) [A-Z][\w\-\" ]+ ?$", t) and len(t) < 60 and not re.match(r"^\d\. [A-Z][a-z]+ (of|in|on)\b", t)):
            kind = "heading"
        if cur != "CM" and SIGNATURE.match(t) and len(t) < 60:
            kind = "signature"
        # footnote markers -> [[id]]
        def sub(m):
            nonlocal marker_i
            sec, nid = MARKER_ORDER[marker_i]
            marker_i += 1
            return f" [[{nid}]]"
        t = re.sub(r"[*†‡]", sub, t)
        t = re.sub(r"\s+([,.;:!?])", r"\1", t).strip()
        secs[cur]["paragraphs"].append({"kind": kind, "en": t})

    assert marker_i == len(MARKER_ORDER), (marker_i, len(MARKER_ORDER))
    # Notes appear in the same order as the markers; F3 and F7 have two paragraphs
    # (1888 English note + 1890 German note), already grouped by the parser.
    for (sec, nid), paras in zip(MARKER_ORDER, notes_raw):
        secs[sec].setdefault("notes", {})[nid] = paras
    (ROOT / "sources" / "clean" / "en.json").write_text(json.dumps(secs, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in secs.items():
        print(k, len(v["paragraphs"]), "paras", len(v.get("notes", {})), "notes")


if __name__ == "__main__":
    main()
