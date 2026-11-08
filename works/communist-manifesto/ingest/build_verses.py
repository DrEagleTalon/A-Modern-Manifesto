"""Stage 3: versify the German anchor text and align English and the modern seed draft.

Reads  sources/clean/de.json, sources/clean/en.json, manifesto/A-Modern-Manifesto.md
Writes text/**/*.yaml  (the master files contributors edit)

Run once to create the numbering. After v1.0 the verse files are the source of
truth and this script must NOT be re-run over them (numbering is frozen).
"""
import json
import re
import sys
from pathlib import Path

import yaml

WORK = Path(__file__).resolve().parents[1]          # works/communist-manifesto
REPO = WORK.parents[1]
ROOT = WORK                                          # text/ and sources/ live in the work folder
sys.path.insert(0, str(REPO / "scripts" / "lib"))
from align import strip  # noqa: E402
from versify import (P, add_modern, attach_apparatus, build_section, clean_text, dump,  # noqa: E402
                     finalise, note_verses)

DE = json.loads((ROOT / "sources/clean/de.json").read_text(encoding="utf-8"))
EN = json.loads((ROOT / "sources/clean/en.json").read_text(encoding="utf-8"))
MODERN_SRC = REPO / "manifesto/A-Modern-Manifesto.md"   # the original rewrite (was README.md)

PREFACE_META = {
    "P1872": ("Vorwort [zur deutschen Ausgabe von 1872]", "de", "MEW 18, S. 95-96", "Karl Marx and Friedrich Engels", "1872-06-24"),
    "P1882": ("Vorrede [zur zweiten russischen Ausgabe von 1882]", "de", "MEW 19, S. 295-296", "Karl Marx and Friedrich Engels", "1882-01-21"),
    "P1883": ("Vorwort [zur deutschen Ausgabe von 1883]", "de", "MEW 21, S. 3-4", "Friedrich Engels", "1883-06-28"),
    "P1888": ("Vorrede [zur englischen Ausgabe von 1888]", "en", "MEW 21, S. 352-359", "Friedrich Engels", "1888-01-30"),
    "P1890": ("Vorwort [zur vierten deutschen Ausgabe von 1890]", "de", "MEW 22, S. 52-59", "Friedrich Engels", "1890-05-01"),
    "P1892": ("Vorwort [zur zweiten polnischen Ausgabe von 1892]", "de", "MEW 22, S. 282-283", "Friedrich Engels", "1892-02-10"),
    "P1893": ("An den italienischen Leser [Vorwort zur italienischen Ausgabe von 1893]", "fr", "MEW 22, S. 365-366", "Friedrich Engels", "1893-02-01"),
}

CHAPTERS = [
    ("0", "0-preamble", "Manifest der Kommunistischen Partei", "Manifesto of the Communist Party"),
    ("I", "1-bourgeois-and-proletarians", "Bourgeois und Proletarier", "Bourgeois and Proletarians"),
    ("II", "2-proletarians-and-communists", "Proletarier und Kommunisten", "Proletarians and Communists"),
    ("III", "3-socialist-and-communist-literature", "Sozialistische und kommunistische Literatur", "Socialist and Communist Literature"),
    ("IV", "4-position-of-the-communists", "Stellung der Kommunisten zu den verschiedenen oppositionellen Parteien",
     "Position of the Communists in Relation to the Various Existing Opposition Parties"),
]

def de_chapters():
    """Split MEW Manifesto paragraphs into preamble + 4 chapters, merging 'I' + title headings."""
    paras = DE["CM"]["paragraphs"]
    out = {"0": [{"kind": "heading", "de": "Manifest der Kommunistischen Partei"}]}
    cur = "0"
    i = 0
    while i < len(paras):
        p = paras[i]
        if p["kind"] == "heading" and re.fullmatch(r"(I|II|III|IV)", clean_text(p["de"])):
            cur = clean_text(p["de"])
            title = paras[i + 1]["de"]
            out[cur] = [{"kind": "heading", "de": f"{cur}. {title}"}]
            i += 2
            continue
        out[cur].append(p)
        i += 1
    return out


def en_chapters():
    paras = EN["CM"]["paragraphs"]
    out, cur = {"0": []}, "0"
    for p in paras:
        m = re.match(r"^(I|II|III|IV)\. ", p["en"])
        if p["kind"] == "heading" and m:
            cur = m.group(1)
            out[cur] = []
        out[cur].append(p)
    return out


def modern_chapters():
    txt = MODERN_SRC.read_text(encoding="utf-8")
    txt = txt[txt.index("## Preamble"):]
    out, cur = {}, None
    for block in re.split(r"\n\s*\n", txt):
        b = block.strip()
        if not b or b == "---":
            continue
        b = b.replace("**", "")
        if b.startswith("## Preamble"):
            cur = "0"
            out[cur] = [{"kind": "heading", "text": "Manifesto of the Communist Party"}]
            continue
        m = re.match(r"^## (I|II|III|IV)\. (.*)$", b)
        if m:
            cur = m.group(1)
            out[cur] = [{"kind": "heading", "text": f"{m.group(1)}. {m.group(2)}"}]
            continue
        if b.startswith("#"):
            out[cur].append({"kind": "heading", "text": b.lstrip("# ").strip()})
            continue
        for line in b.split("\n"):           # some paragraphs are single-line-broken in the seed
            if line.strip():
                out[cur].append({"kind": "p", "text": line.strip()})
    return out


# ---------------------------------------------------------------- core

def main():
    stats = {"verses": 0, "review": 0}
    # ---- prefaces
    for sid, (title_de, orig, mew, author, date) in PREFACE_META.items():
        de_p = [P("heading", title_de)] + [P(p["kind"], p["de"]) for p in DE[sid]["paragraphs"]]
        en_p = []
        for p in EN[sid]["paragraphs"]:
            if sid == "P1890" and p["en"].startswith("[Reprint of the 1882 Russian Edition"):
                for q in EN["P1882"]["paragraphs"][1:]:
                    if q["kind"] == "p" or q["en"].startswith("January"):
                        en_p.append(P(q["kind"], q["en"]))
                continue
            en_p.append(P(p["kind"], p["en"]))
        anchor = "en" if sid == "P1888" else "de"
        A, B = (de_p, en_p) if anchor == "de" else (en_p, de_p)
        verses, _ = build_section(sid, sid, anchor, A, B)
        if sid == "P1890":
            # mark verses whose English was supplied from the 1882 preface
            in_block = False
            for v in verses:
                if v["_de_raw"].lstrip().startswith('"Die erste russische Ausgabe'):
                    in_block = True
                if in_block:
                    v["en_note"] = "English supplied from P1882 (the MIA text prints only a placeholder here; Engels's 1890 back-translation differs slightly)"
                if in_block and "21. Januar 1882" in v["_de_raw"]:
                    in_block = False
        attach_apparatus(verses, DE[sid]["variants"], f"{sid}.", {})
        # preface notes
        note_vs = []
        for nid, paras in DE[sid]["notes"].items():
            en_raw_notes = EN.get(sid, {}).get("notes", {}).get(f"F{nid}", [])
            an = "en" if sid == "P1888" else "de"
            if sid == "P1888" and nid == "2":
                # bibliographic note that MEW prints in English: it IS the English, there is no German
                nv = note_verses(f"{sid}.N{nid}", [], [paras[0]], anchor="en")
                for v in nv:
                    v.pop("review", None); v.pop("review_reason", None); v.pop("align", None)
                    v["en_note"] = "Engels's English bibliographic note (MEW prints it in English); no German text"
            else:
                nv = note_verses(f"{sid}.N{nid}", paras, en_raw_notes, anchor=an)
            attach_apparatus(nv, {}, f"{sid}.", {})
            note_vs += nv
        verses = finalise(verses + note_vs)
        meta = {
            "section": sid,
            "title_de": title_de,
            "title_en": EN[sid]["paragraphs"][0]["en"],
            "author": author,
            "date": date,
            "original_language": orig,
            "anchor_language": anchor,
            "source_de": f"{mew} (Dietz, Berlin) via mlwerke.de" + ("; German is MEW's editorial translation, NOT an original" if orig != "de" else ""),
            "source_en": "Marxists Internet Archive transcription" + (" of Engels's own English" if sid == "P1888" else "; English is a later translation (Progress Publishers, Moscow 1969), licence unverified"),
        }
        if sid != "P1888":
            meta["en_label"] = "English (later translation, Progress 1969)"
        dump(ROOT / "text" / "00-prefaces" / f"{sid[1:]}.yaml", meta, verses)
        stats["verses"] += len(verses)
        stats["review"] += sum(1 for v in verses if v.get("review"))
        print(sid, len(verses), "verses", sum(1 for v in verses if v.get("review")), "to review")

    # ---- Manifesto
    dch, ech, mch = de_chapters(), en_chapters(), modern_chapters()
    total_de = sum(len(strip(p["de"])) for ps in dch.values() for p in ps)
    total_en = sum(len(strip(p["en"])) for ps in ech.values() for p in ps)
    ratio = total_en / total_de
    page_state = {}
    for cid, fname, tde, ten in CHAPTERS:
        A = [P(p["kind"], p["de"]) for p in dch[cid]]
        B = [P(p["kind"], p["en"]) for p in ech[cid]]
        verses, owner = build_section(cid, cid, "de", A, B, ratio=ratio)
        attach_apparatus(verses, DE["CM"]["variants"], "", page_state)
        add_modern(verses, owner, ech[cid], mch.get(cid, []))
        verses = finalise(verses)
        meta = {
            "section": cid,
            "title_de": tde,
            "title_en": ten,
            "author": "Karl Marx and Friedrich Engels",
            "date": "1848-02",
            "original_language": "de",
            "anchor_language": "de",
            "source_de": "MEW 4, S. 459-493 (Dietz, Berlin), text of the 1890 German edition, the last edited by Engels, via mlwerke.de; 1848/1872/1883/1888 variants from MEW's apparatus",
            "source_en": "Samuel Moore and Friedrich Engels, English edition of 1888; Marxists Internet Archive transcription proofed against the 1888 edition by Andy Blunden (2004), CC BY-SA",
            "source_modern": "Seeded from A Modern Manifesto (Yusuf Talan Saunders), a paraphrase of the 1888 English; not yet checked against the German",
        }
        dump(ROOT / "text" / "01-manifesto" / f"{fname}.yaml", meta, verses)
        stats["verses"] += len(verses)
        stats["review"] += sum(1 for v in verses if v.get("review"))
        print(cid, len(verses), "verses", sum(1 for v in verses if v.get("review")), "to review",
              sum(1 for v in verses if v["modern"]), "with modern seed")

    # ---- Engels's notes to the Manifesto
    note_vs = []
    en_notes = EN["CM"]["notes"]
    for nid, paras in DE["CM"]["notes"].items():
        nv = note_verses(f"N{nid}", paras, en_notes.get(f"F{nid}", []))
        attach_apparatus(nv, {}, "", {})
        note_vs += nv
    # English-only note E1 (guild-master)
    nv = note_verses("E1", [], en_notes["E1"], anchor="en")
    attach_apparatus(nv, {}, "", {})
    for v in nv:
        v.pop("review", None); v.pop("review_reason", None); v.pop("align", None)
        v["en_note"] = "English-only note: Engels explains the English word 'guild-master'; the German text needs no note (Zunftbürger)"
    note_vs += nv
    note_vs = finalise(note_vs)
    meta = {
        "section": "N",
        "title_de": "Anmerkungen von Engels",
        "title_en": "Notes by Engels",
        "author": "Friedrich Engels",
        "date": "1888/1890",
        "original_language": "en (1888 notes) / de (1890 notes)",
        "anchor_language": "de",
        "source_de": "MEW 4 footnotes. Notes marked 'zur englischen Ausgabe von 1888' are MEW's German translation of Engels's English",
        "source_en": "Marxists Internet Archive. 1890 notes in English are later translations",
    }
    dump(ROOT / "text" / "01-manifesto" / "9-notes-by-engels.yaml", meta, note_vs)
    stats["verses"] += len(note_vs)
    print("notes", len(note_vs))
    print(stats)


if __name__ == "__main__":
    main()
