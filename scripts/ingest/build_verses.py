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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from segment import split_sentences  # noqa: E402
from align import align, cross_lang_cost, same_lang_cost, strip  # noqa: E402

DE = json.loads((ROOT / "sources/clean/de.json").read_text(encoding="utf-8"))
EN = json.loads((ROOT / "sources/clean/en.json").read_text(encoding="utf-8"))
MODERN_SRC = ROOT / "manifesto/A-Modern-Manifesto.md"   # the original rewrite (was README.md)

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

MARK = re.compile(r"\[\[([A-Z])(\d+)\]\]")


def clean_text(s: str) -> str:
    s = MARK.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:!?)])", r"\1", s)
    return s


# ---------------------------------------------------------------- inputs

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

class Section:
    def __init__(self, sid, anchor, prefix):
        self.sid, self.anchor, self.prefix = sid, anchor, prefix
        self.verses = []
        self.other_owner = {}   # index of other-language sentence -> verse id (head)

    def vid(self, pnum, snum):
        return f"{self.prefix}.{pnum}.{snum}"


def para_sentences(text, lang, kind):
    if kind in ("heading", "signature"):
        return [text]
    return split_sentences(text, lang)


def build_section(sid, prefix, anchor, A_paras, B_paras, note_prefix="", review_cost=6.0, ratio=None, para0_heading=True):
    """A_paras/B_paras: list of {kind, text}. Returns list of verse dicts and owner map."""
    a_lang = anchor
    b_lang = "en" if anchor == "de" else "de"
    la = sum(len(strip(p["text"])) for p in A_paras) or 1
    lb = sum(len(strip(p["text"])) for p in B_paras) or 1
    ratio = ratio or lb / la
    pbeads = align([p["text"] for p in A_paras], [p["text"] for p in B_paras], cross_lang_cost(None, None, ratio))

    # paragraph numbers for the anchor side
    pnums, n = [], 0
    for i, p in enumerate(A_paras):
        if i == 0 and p["kind"] == "heading" and para0_heading:
            pnums.append(0)
        else:
            n += 1
            pnums.append(n)

    verses, owner = [], {}
    b_sent_global = 0
    for a_idx, b_idx, pcost in pbeads:
        A_s = []   # (para index, sentence text)
        for ai in a_idx:
            for s in para_sentences(A_paras[ai]["text"], a_lang, A_paras[ai]["kind"]):
                A_s.append((ai, s))
        B_s = []
        for bi in b_idx:
            for s in para_sentences(B_paras[bi]["text"], b_lang, B_paras[bi]["kind"]):
                B_s.append((bi, s))
        if not A_s:      # other-language paragraph without anchor: attach to previous verse
            if verses:
                v = verses[-1]
                v["_b"] = (v.get("_b", "") + " " + " ".join(s for _, s in B_s)).strip()
                v["review"] = True
                v.setdefault("_why", []).append(f"{b_lang} text with no {a_lang} counterpart appended here")
            b_sent_global += len(B_s)
            continue
        sbeads = align([s for _, s in A_s], [s for _, s in B_s], cross_lang_cost(None, None, ratio)) if B_s else [([k], [], 99) for k in range(len(A_s))]
        # sentence numbers inside each paragraph
        counters = {}
        local_vids = []
        for ai, s in A_s:
            counters[ai] = counters.get(ai, 0) + 1
            local_vids.append(sid_v := f"{prefix}.{pnums[ai]}.{counters[ai]}")
            verses.append({"id": sid_v, "kind": A_paras[ai]["kind"], "_a": s, "_b": "", "_bsrc": A_paras[ai].get("bnote")})
        base = len(verses) - len(A_s)
        for sa, sb, c in sbeads:
            text_b = " ".join(B_s[k][1] for k in sb)
            if not sa:
                # attach to the previous verse inside this bead (or the first one)
                prev = [x for x in sbeads[: sbeads.index((sa, sb, c))] if x[0]]
                head = verses[base + (prev[-1][0][-1] if prev else 0)]
                head["_b"] = (head["_b"] + " " + text_b).strip()
                head["review"] = True
                head.setdefault("_why", []).append(f"extra {b_lang} sentence with no {a_lang} counterpart")
                for k in sb:
                    owner[b_sent_global + k] = head["id"]
                continue
            head = verses[base + sa[0]]
            head["_b"] = text_b
            for k in sa[1:]:
                verses[base + k]["_join"] = head["id"]
            for k in sb:
                owner[b_sent_global + k] = head["id"]
            if (len(sa), len(sb)) != (1, 1):
                head["align"] = f"{len(sa)}:{len(sb)}"
                head["review"] = True
                head.setdefault("_why", []).append(f"{len(sa)} {a_lang} sentence(s) matched to {len(sb)} {b_lang} sentence(s)")
            elif c > review_cost:
                head["review"] = True
                head.setdefault("_why", []).append("length/anchor mismatch, check the match")
        b_sent_global += len(B_s)
    # finalise into de/en fields
    out = []
    for v in verses:
        d = {"id": v["id"], "kind": v["kind"]}
        de_raw = v["_a"] if anchor == "de" else v["_b"]
        en_raw = v["_b"] if anchor == "de" else v["_a"]
        d["_de_raw"], d["_en_raw"] = de_raw, en_raw
        d["de"] = clean_text(de_raw)
        d["en"] = clean_text(en_raw)
        if "_join" in v:
            d["joined_to"] = v["_join"]
        for k in ("align", "review"):
            if k in v:
                d[k] = v[k]
        if v.get("_why"):
            d["review_reason"] = "; ".join(dict.fromkeys(v["_why"]))
        if v.get("_bsrc"):
            d["en_note"] = v["_bsrc"]
        out.append(d)
    return out, owner


def attach_apparatus(verses, variants, note_prefix, page_state):
    """Turn inline markers into structured fields; track MEW page numbers."""
    for v in verses:
        de_raw, en_raw = v.pop("_de_raw"), v.pop("_en_raw")
        start_page = page_state.get("p")
        pages = [m.group(2) for m in MARK.finditer(de_raw) if m.group(1) == "S"]
        lead = re.match(r"^\s*\[\[S(\d+)\]\]", de_raw)
        if lead:
            start_page = lead.group(1)
        if pages:
            page_state["p"] = pages[-1]
        if start_page:
            v["mew_page"] = start_page if (not pages or pages == [start_page]) else f"{start_page}-{pages[-1]}"
        notes = []
        for m in MARK.finditer(de_raw + " " + en_raw):
            if m.group(1) in "FE":
                nid = f"{note_prefix}{'N' if m.group(1) == 'F' else 'E'}{m.group(2)}"
                if nid not in notes:
                    notes.append(nid)
        if notes:
            v["footnotes"] = notes
        vs = []
        for m in MARK.finditer(de_raw):
            if m.group(1) == "T":
                var = variants.get(m.group(2))
                if not var:
                    continue
                after = clean_text(de_raw[m.end():])
                ctx = " ".join(after.split()[:5])
                vs.append({"ref": f"T{m.group(2)}", "editions": var["editions"], "reading": var["reading"], "base_text": ctx + " …"})
        if vs:
            v["de_variants"] = vs


def add_modern(verses, owner, en_paras, mod_paras):
    """Align modern seed paragraphs/sentences to English and drop them onto verses."""
    by_id = {v["id"]: v for v in verses}
    pbeads = align([p["en"] if "en" in p else p["text"] for p in en_paras], [p["text"] for p in mod_paras], same_lang_cost())
    en_global = 0
    for e_idx, m_idx, _ in pbeads:
        E_s = []
        for ei in e_idx:
            E_s += para_sentences(en_paras[ei]["en"], "en", en_paras[ei]["kind"])
        M_s = []
        for mi in m_idx:
            M_s += para_sentences(mod_paras[mi]["text"], "en", mod_paras[mi]["kind"])
        if not E_s:
            continue
        if not M_s:
            en_global += len(E_s)
            continue
        sbeads = align(E_s, M_s, same_lang_cost())
        last_head = None
        for se, sm, _ in sbeads:
            text = " ".join(M_s[k] for k in sm)
            if se:
                head = owner.get(en_global + se[0])
                last_head = head or last_head
            else:
                head = last_head or owner.get(en_global)
            if head and text:
                v = by_id[head]
                v["modern"] = (v.get("modern", "") + " " + text).strip()
        en_global += len(E_s)


ATTRIB = re.compile(r"\s*\[\s*(Anmerkung von Engels[^\]]*|Engels, [^\]]*[Ee]dition[^\]]*|Note by Engels[^\]]*|Engels, (?:English|German) Edition \d{4})\s*\]")


def split_attrib(paras):
    """Split note paragraphs at Engels-attribution brackets; return [(text, attribution)]."""
    out = []
    for t in paras:
        pos = 0
        for m in ATTRIB.finditer(t):
            chunk = t[pos:m.start()].strip()
            if chunk:
                out.append([chunk, m.group(1).strip().rstrip(".")])
            elif out:
                out[-1][1] = m.group(1).strip().rstrip(".")
            pos = m.end()
        rest = t[pos:].strip()
        if rest:
            out.append([rest, ""])
    return out


def edition_key(attr):
    yrs = re.findall(r"18[89]\d", attr)
    return yrs[0] if yrs else ""


def note_verses(prefix, de_paras, en_paras, anchor="de"):
    D = split_attrib(de_paras)
    E = split_attrib(en_paras)
    if len(D) > 1 and len(E) == len(D):
        order = [edition_key(a) for _, a in D]
        E.sort(key=lambda x: order.index(edition_key(x[1])) if edition_key(x[1]) in order else 99)
    if anchor == "de":
        A, B = [P("note", t) for t, _ in D], [P("note", t) for t, _ in E]
        attrs, other_attrs = [a for _, a in D], [a for _, a in E]
    else:
        A, B = [P("note", t) for t, _ in E], [P("note", t) for t, _ in D]
        attrs, other_attrs = [a for _, a in E], [a for _, a in D]
    keysA = [edition_key(a) for a in attrs]
    keysB = [edition_key(a) for a in other_attrs]
    if A and B and all(keysA) and all(keysB):
        # pair paragraphs by edition (1888 note with 1888 note, 1890 with 1890)
        vs = []
        for i, (pa, ka) in enumerate(zip(A, keysA), start=1):
            match = [pb for pb, kb in zip(B, keysB) if kb == ka]
            part, _ = build_section("N", prefix, anchor, [pa], match, para0_heading=False)
            for v in part:
                v["id"] = re.sub(r"\.1\.(\d+)$", rf".{i}.\1", v["id"])
                if "_join" in v:
                    v["_join"] = re.sub(r"\.1\.(\d+)$", rf".{i}.\1", v["_join"])
                if "joined_to" in v:
                    v["joined_to"] = re.sub(r"\.1\.(\d+)$", rf".{i}.\1", v["joined_to"])
                if not match:
                    v["en_note" if anchor == "de" else "de_note"] = f"No {'English' if anchor == 'de' else 'German'} text of this note in the source used"
            vs += part
    else:
        vs, _ = build_section("N", prefix, anchor, A, B, para0_heading=False)
    for v in vs:
        pi = int(v["id"].split(".")[-2]) - 1
        a = attrs[pi] if pi < len(attrs) else ""
        if not a and other_attrs:
            a = other_attrs[min(pi, len(other_attrs) - 1)]
        if a:
            v["note_edition"] = a
    return vs


def finalise(verses):
    out = []
    for v in verses:
        d = {"id": v["id"], "kind": v["kind"], "de": v["de"], "en": v["en"]}
        if "joined_to" in v:
            d["joined_to"] = v["joined_to"]
            d["modern"] = ""
        else:
            d["modern"] = v.get("modern", "")
        d["modern_status"] = "seed" if d["modern"] else ("joined" if "joined_to" in v else "empty")
        d["notes"] = ""
        for k in ("note_edition", "footnotes", "de_variants", "mew_page", "en_note", "align", "review", "review_reason"):
            if k in v:
                d[k] = v[k]
        out.append(d)
    return out


def dump(path, meta, verses):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = dict(meta)
    doc["verses"] = verses
    with path.open("w", encoding="utf-8") as f:
        f.write("# Master file. Edit the `modern` and `notes` fields; see CONTRIBUTING.md.\n")
        f.write("# Verse ids are frozen. Never renumber; see VERSIFICATION.md.\n")
        yaml.dump(doc, f, allow_unicode=True, sort_keys=False, width=100000, default_flow_style=False)


def P(kind, text, **kw):
    d = {"kind": kind, "text": text}
    d.update(kw)
    return d


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
