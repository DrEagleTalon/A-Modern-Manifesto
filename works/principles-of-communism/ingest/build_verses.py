"""One-time ingest for Principles of Communism (PC).

German: MEW 4, pp. 361-380, printed from Engels's manuscript (end of October to November 1847), via the
mlwerke.de mirror (UTF-8 page without page anchors). MEW's editorial footnote references "(1)" to "(8)" are
removed from the text: they are the editors' notes, not Engels's.

There is no public-domain English translation (Paul Sweezy's of 1952 is protected), so the English column is
empty and the modern draft is translated straight from the German.

Sections: 0 (title) and Q1-Q25, one per question. In each, paragraph 0 is Engels's question and the
following paragraphs are his answer.
"""
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
REPO = WORK.parents[1]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
from versify import P, attach_apparatus, build_section, dump, finalise  # noqa: E402

RAW = WORK / "sources" / "raw" / "de" / "me04_361.htm"
SRC = "MEW 4, S. 361-380 (Dietz, Berlin) via mlwerke.de; printed from Engels's manuscript. MEW editorial notes removed"


def paragraphs():
    t = RAW.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", t, flags=re.S | re.I):
        s = re.sub(r"<[^>]+>", "", m.group(1))
        s = re.sub(r"\s+", " ", s).strip()
        if not s:
            continue
        if s.startswith("Geschrieben Ende Oktober"):
            break
        s = re.sub(r"\s?\((\d)\)", "", s)               # MEW editorial note refs
        out.append(s)
    start = next(i for i, s in enumerate(out) if s.startswith("1. Frage"))
    return out[start:]


def main():
    sections, cur = [], None
    for s in paragraphs():
        m = re.match(r"^(\d+)\. Frage: ", s)
        if m:
            cur = {"sid": f"Q{m.group(1)}", "paras": [P("heading", s)]}
            sections.append(cur)
        else:
            cur["paras"].append(P("p", s))
    assert [x["sid"] for x in sections] == [f"Q{i}" for i in range(1, 26)]
    title = [P("heading", "Grundsätze des Kommunismus")]
    vs, _ = build_section("0", "0", "de", title, [], single=True)
    attach_apparatus(vs, {}, "", {})
    meta = lambda sid, t: {"section": sid, "title_original": t, "title_en": "", "author": "Friedrich Engels",  # noqa: E731
                           "date": "1847-10/11", "original_language": "de", "anchor_language": "de",
                           "source_original": SRC, "source_en": "None: no public-domain English translation"}
    dump(WORK / "text" / "00-title.yaml", {**meta("0", "Grundsätze des Kommunismus"), "title_en": "Principles of Communism"}, finalise(vs))
    total = len(vs)
    for i, sec in enumerate(sections, start=1):
        vs, _ = build_section(sec["sid"], sec["sid"], "de", sec["paras"], [], single=True)
        attach_apparatus(vs, {}, "", {})
        vs = finalise(vs)
        q = sec["paras"][0]["text"]
        dump(WORK / "text" / f"q{i:02d}.yaml", {**meta(sec["sid"], q), "title_en": f"Question {i}"}, vs)
        total += len(vs)
    print("PC", total, "verses in", len(sections) + 1, "sections")


if __name__ == "__main__":
    main()
