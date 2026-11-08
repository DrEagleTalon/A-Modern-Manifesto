"""One-time ingest for Value, Price and Profit (VPP).

Marx wrote and read this paper in English (General Council of the International, June 1865); Eleanor Marx
published it in 1898 with a preface by Edward Aveling. So the original column IS the English and there is
no historical-translation column. MEW's German (vol. 16) is an editorial translation and is left out.

Source: the Marxists Internet Archive text (public-domain 1898 text; MIA transcription CC BY-SA), proofed by
Brandon Poole 2009. MIA's own introduction (from a 1969 edition) and MIA's endnotes are not used.

Sections: P1898 (Aveling's preface), 0 (Marx's preliminary remarks), I-XIV (Marx's numbered sections).
Run once; after the lock file exists the YAML in text/ is the source of truth.
"""
import json
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
REPO = WORK.parents[1]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
from mew import parse_mia  # noqa: E402
from versify import P, attach_apparatus, build_section, dump, finalise  # noqa: E402

RAW = WORK / "sources" / "raw" / "en"
SRC = ("Karl Marx, Value, Price and Profit, ed. Eleanor Marx Aveling (London 1898), public domain; "
       "Marxists Internet Archive transcription (proofed by Brandon Poole, 2009; CC BY-SA)")
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV"]


def meta(section, title, author, date):
    return {"section": section, "title_original": title, "title_en": title, "author": author, "date": date,
            "original_language": "en", "anchor_language": "en", "source_original": SRC,
            "source_en": "None needed: the original is in English"}


def write(sid, title, paras, fname, author, date):
    vs, _ = build_section(sid, sid, "de", [P(p["kind"], p["text"]) for p in paras], [], lang_a="en", single=True)
    attach_apparatus(vs, {}, "", {})
    vs = finalise(vs)
    dump(WORK / "text" / fname, meta(sid, title, author, date), vs)
    print(sid, len(vs), "verses")
    return len(vs)


def main():
    removed = {}
    pre, rem = parse_mia(RAW / "preface.html", keep_classes=("information",))
    removed["preface"] = rem
    pre = [p for p in pre if p["text"] != "Preface"]
    write("P1898", "Preface by Edward Aveling (1898)", [{"kind": "heading", "text": "Preface by Edward Aveling (1898)"}] + pre,
          "00-preface/1898.yaml", "Edward Aveling", "1898")

    sections, cur = [], None
    for ch in ("ch01", "ch02", "ch03"):
        paras, rem = parse_mia(RAW / f"{ch}.html")
        removed[ch] = rem
        for p in paras:
            if p["kind"] == "heading":
                m = re.match(r"^([IVX]+)\. (.+)$", p["text"])
                sid = m.group(1) if m else "0"
                cur = {"sid": sid, "title": p["text"], "paras": [p]}
                sections.append(cur)
            elif cur is not None:
                cur["paras"].append(p)
    assert [s["sid"] for s in sections] == ["0"] + ROMAN, [s["sid"] for s in sections]
    total = 0
    for i, s in enumerate(sections):
        total += write(s["sid"], s["title"], s["paras"], f"01-value-price-and-profit/{i:02d}-{s['sid'].lower()}.yaml",
                       "Karl Marx", "1865-06")
    (WORK / "sources" / "clean").mkdir(parents=True, exist_ok=True)
    (WORK / "sources" / "clean" / "mia_insertions_removed.json").write_text(json.dumps(removed, ensure_ascii=False, indent=1), encoding="utf-8")
    print("total", total)


if __name__ == "__main__":
    main()
