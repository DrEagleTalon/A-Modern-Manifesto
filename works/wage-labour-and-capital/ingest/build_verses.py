"""One-time ingest for Wage Labour and Capital (WLC).

German  MEW 6, pp. 397-423: Marx's text in Engels's 1891 edition, with every 1849
        Neue Rheinische Zeitung reading recorded as a variant; MEW 22, pp. 202-209:
        Engels's 1891 introduction. Both via the mlwerke.de mirror.
English Harriet E. Lothrop's translation (New York Labor News, 1902) as edited and
        transcribed by the Marxists Internet Archive.

Sections follow the five newspaper instalments (NRZ nos. 264-267 and 269, 5-11 April
1849), which is how Marx actually divided the text. Lothrop's chapter headings (I-IX)
are not in the German; they are kept as en_note on the verse where each chapter starts.

Run once. After the lock file exists the YAML in text/ is the source of truth.
"""
import json
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
REPO = WORK.parents[1]
sys.path.insert(0, str(REPO / "scripts" / "lib"))
from align import strip  # noqa: E402
from mew import parse_mew, parse_mia  # noqa: E402
from versify import P, attach_apparatus, build_section, dump, finalise  # noqa: E402

RAW = WORK / "sources" / "raw"
CLEAN = WORK / "sources" / "clean"

# Instalments: first variant marker of each one, and its newspaper data
INSTALMENTS = [
    ("I", "1", "264", "5. April 1849", "5 April 1849"),
    ("II", "33", "265", "6. April 1849", "6 April 1849"),
    ("III", "48", "266", "7. April 1849", "7 April 1849"),
    ("IV", "62", "267", "8. April 1849", "8 April 1849"),
    ("V", "84", "269", "11. April 1849", "11 April 1849"),
]
# English (Lothrop/MIA) often breaks one German paragraph into several
WIDE = [(1, 4), (1, 5), (1, 6), (4, 1)]
EN_CHAPTERS = ["ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch08", "ch09"]

SRC_EN = ("Harriet E. Lothrop, Wage-Labor and Capital, New York Labor News Co., 1902 (public domain), "
          "in the Marxists Internet Archive edition (proofed by Alek Blain, 2006; CC BY-SA), which modernises some wording and currency")


# Defects in the MIA text, repaired from the 1902 Lothrop edition (archive.org scan
# wagelaborcapital00marx_2) and listed in SOURCES.md.
CORRECTIONS = [
    ("It is evident that the small manufacturers and thereby increasing",
     "It is evident that the small manufacturer cannot at the same time be a big manufacturer. "
     "That the interest on capital decreases in the same ratio in which the mass and number of capitals increase, "
     "that it diminishes with the growth of capital, that therefore the small capitalist can no longer live on his interest, "
     "but must consequently throw himself upon industry by joining the ranks of the small manufacturers and thereby increasing"),
    ("grow every leaner", "grow ever leaner"),
    ("were values were values", "were values"),
    ("but not for a stipulated payment", "but for a stipulated payment"),
]


def tidy_en(paras):
    """Apply CORRECTIONS; fold list items and block quotes back into their paragraph,
    so English paragraphs look like the German ones they translate."""
    out = []
    for p in paras:
        p = dict(p)
        for a, b in CORRECTIONS:
            p["text"] = p["text"].replace(a, b)
        prev = out[-1] if out else None
        continues = prev is not None and prev["kind"] == "p" and p["kind"] == "p" and (
            p.get("cls") == "indentb" or not re.search(r"[.!?\"')]$", prev["text"]))
        if continues:
            prev["text"] = prev["text"] + " " + p["text"]
        else:
            out.append(p)
    return out


def meta(section, title_de, title_en, source_de, author, date):
    return {"section": section, "title_de": title_de, "title_en": title_en, "author": author, "date": date,
            "original_language": "de", "anchor_language": "de", "source_de": source_de, "source_en": SRC_EN}


def main():
    CLEAN.mkdir(parents=True, exist_ok=True)
    log = {"mia_insertions_removed": {}}

    # ---------------- Engels's 1891 introduction
    de_i, _, _ = parse_mew(RAW / "de" / "me22_202.htm")
    en_i, rem = parse_mia(RAW / "en" / "mia_intro.html")
    en_i = tidy_en(en_i)
    log["mia_insertions_removed"]["intro"] = rem
    A = [P("heading", "Einleitung [zu Karl Marx' \"Lohnarbeit und Kapital\", Ausgabe 1891]")] + [P(p["kind"], p["de"]) for p in de_i]
    B = [P("heading", "Introduction by Frederick Engels (1891 edition)")] + [P(p["kind"], p["text"]) for p in en_i if p["kind"] != "heading"]
    vs, _ = build_section("P1891", "P1891", "de", A, B, flat=True)
    attach_apparatus(vs, {}, "P1891.", {})
    vs = finalise(vs)
    dump(WORK / "text" / "00-introduction" / "1891.yaml",
         meta("P1891", A[0]["text"], B[0]["text"], "MEW 22, S. 202-209 (Dietz, Berlin) via mlwerke.de; Engels, original German",
              "Friedrich Engels", "1891-04-30"), vs)
    print("P1891", len(vs), "verses", sum(1 for v in vs if v.get("review")), "to review")

    # ---------------- Marx's text
    de_m, _, variants = parse_mew(RAW / "de" / "me06_397.htm")
    for k, v in variants.items():
        if not v["editions"]:
            v["editions"] = "1849 (NRZ)"
    starts = {}
    for i, p in enumerate(de_m):
        for sec, first, *_ in INSTALMENTS:
            if f"[[T{first}]]" in p["de"]:
                starts[i] = sec
    assert len(starts) == 5, starts
    pids, sec_of, counters, cur = [], [], {}, None
    for i, p in enumerate(de_m):
        cur = starts.get(i, cur)
        counters[cur] = counters.get(cur, 0) + 1
        pids.append(f"{cur}.{counters[cur]}")
        sec_of.append(cur)

    en_paras, chapter_starts = [], {}   # index of first English paragraph -> Lothrop chapter heading
    for ch in EN_CHAPTERS:
        paras, rem = parse_mia(RAW / "en" / f"mia_{ch}.html")
        paras = tidy_en(paras)
        log["mia_insertions_removed"][ch] = rem
        for p in paras:
            if p["kind"] == "heading":
                if ch == "ch02":            # the one heading that is also in the German
                    en_paras.append(p)
                else:
                    chapter_starts[len(en_paras)] = f"Lothrop 1902, chapter {EN_CHAPTERS.index(ch) + 1}: {p['text']}"
                continue
            en_paras.append(p)
    (CLEAN / "de.json").write_text(json.dumps({"intro": de_i, "marx": de_m, "variants": variants}, ensure_ascii=False, indent=1), encoding="utf-8")
    (CLEAN / "en.json").write_text(json.dumps({"intro": en_i, "marx": en_paras, "chapter_starts": chapter_starts, **log}, ensure_ascii=False, indent=1), encoding="utf-8")

    A = [P(p["kind"], p["de"]) for p in de_m]
    B = [P(p["kind"], p["text"]) for p in en_paras]
    ratio = sum(len(strip(p["text"])) for p in B) / sum(len(strip(p["text"])) for p in A)
    vs, owner = build_section("M", "M", "de", A, B, ratio=ratio, pids=pids, flat=True)

    # Lothrop chapter headings -> en_note on the verse owning the chapter's first English sentence
    from versify import para_sentences
    sent_start, n = {}, 0
    for bi, p in enumerate(B):
        sent_start[bi] = n
        n += len(para_sentences(p["text"], "en", p["kind"]))
    by_id = {v["id"]: v for v in vs}
    for bi, label in chapter_starts.items():
        vid = owner.get(sent_start.get(bi, -1))
        if vid:
            by_id[vid]["en_note"] = (by_id[vid].get("en_note", "") + " " + label).strip()

    attach_apparatus(vs, variants, "", {})
    # a join may not cross an instalment boundary: keep the verse on its own and point to the English
    for v in vs:
        j = v.get("joined_to")
        if j and j.split(".")[0] != v["id"].split(".")[0]:
            del v["joined_to"]
            v["en"] = ""
            v["en_note"] = (v.get("en_note", "") + f" The 1902 English renders this sentence together with {j}.").strip()
            v["review"] = True
            v["review_reason"] = "English shared with a verse in the previous instalment"
    # section headings (editorial: the instalment's newspaper issue) and split into files
    for sec, first, nr, de_date, en_date in INSTALMENTS:
        part = [v for v in vs if v["id"].split(".")[0] == sec]
        head = {"id": f"{sec}.0.1", "kind": "heading",
                "de": f"[{sec}] Neue Rheinische Zeitung Nr. {nr}, {de_date}",
                "en": f"[{sec}] Neue Rheinische Zeitung No. {nr}, {en_date}",
                "en_note": "Editorial heading: the newspaper instalment. Not printed in the 1891 pamphlet."}
        part = finalise([head] + part)
        for v in part:
            if v["id"] == f"{sec}.0.1":
                v["modern_status"] = "empty"
        title_en = f"Instalment {sec} (NRZ No. {nr}, {en_date})"
        dump(WORK / "text" / "01-wage-labour-and-capital" / f"{INSTALMENTS.index((sec, first, nr, de_date, en_date)) + 1}-nrz-{nr}.yaml",
             meta(sec, f"Lohnarbeit und Kapital, Neue Rheinische Zeitung Nr. {nr}, {de_date}", title_en,
                  "MEW 6, S. 397-423 (Dietz, Berlin) via mlwerke.de: text of Engels's 1891 edition; 1849 newspaper readings attached as variants",
                  "Karl Marx", "1849-04"), part)
        print(sec, len(part), "verses", sum(1 for v in part if v.get("review")), "to review")


if __name__ == "__main__":
    main()
