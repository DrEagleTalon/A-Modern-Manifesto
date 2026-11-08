"""Shared versification helpers used by every work's one-time ingest script.

build_section() splits an anchor-language text into verses and aligns the other
language against it; attach_apparatus() turns inline [[X1]] markers into
footnote, variant and page fields; add_modern() drops a modern draft onto the
verses; finalise() and dump() write the master YAML files.
"""
import re

import yaml

from align import align, cross_lang_cost, same_lang_cost, strip  # noqa: F401
from segment import split_sentences

MARK = re.compile(r"\[\[([A-Z])(\d+)\]\]")


def clean_text(s: str) -> str:
    s = MARK.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:!?)])", r"\1", s)
    return s


# ---------------------------------------------------------------- inputs


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


def build_section(sid, prefix, anchor, A_paras, B_paras, note_prefix="", review_cost=6.0, ratio=None, para0_heading=True, pids=None, para_beads=None, flat=False, band=80):
    """A_paras/B_paras: list of {kind, text}. Returns list of verse dicts and owner map."""
    a_lang = anchor
    b_lang = "en" if anchor == "de" else "de"
    la = sum(len(strip(p["text"])) for p in A_paras) or 1
    lb = sum(len(strip(p["text"])) for p in B_paras) or 1
    ratio = ratio or lb / la
    if flat:
        # one bead over the whole text: sentences are aligned across paragraph breaks,
        # for translations whose paragraphing differs from the original
        pbeads = [(list(range(len(A_paras))), list(range(len(B_paras))), 0.0)]
    elif para_beads:
        from align import BEADS, PRIOR
        beads = BEADS + [b for b in para_beads if b not in BEADS]
        prior = {**PRIOR, **{b: 5.0 for b in para_beads if b not in PRIOR}}
        pbeads = align([p["text"] for p in A_paras], [p["text"] for p in B_paras], cross_lang_cost(None, None, ratio), beads, prior)
    else:
        pbeads = align([p["text"] for p in A_paras], [p["text"] for p in B_paras], cross_lang_cost(None, None, ratio))

    # paragraph addresses for the anchor side ("<prefix>.<n>"), unless the caller supplies them
    if pids is None:
        pids, n = [], 0
        for i, p in enumerate(A_paras):
            if i == 0 and p["kind"] == "heading" and para0_heading:
                pids.append(f"{prefix}.0")
            else:
                n += 1
                pids.append(f"{prefix}.{n}")

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
        sbeads = align([s for _, s in A_s], [s for _, s in B_s], cross_lang_cost(None, None, ratio), band=(band if flat else None)) if B_s else [([k], [], 99) for k in range(len(A_s))]
        # sentence numbers inside each paragraph
        counters = {}
        local_vids = []
        for ai, s in A_s:
            counters[ai] = counters.get(ai, 0) + 1
            local_vids.append(sid_v := f"{pids[ai]}.{counters[ai]}")
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
                # MEW puts the marker right after the word it concerns (or where text was
                # added or left out), so show words on both sides; the caret marks the spot.
                before = " ".join(clean_text(de_raw[:m.start()]).split()[-4:])
                after = " ".join(clean_text(de_raw[m.end():]).split()[:4])
                vs.append({"ref": f"T{m.group(2)}", "editions": var["editions"], "reading": var["reading"],
                           "base_text": f"… {before} ‸ {after} …".replace("…  ‸", "‸").strip()})
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
        # Output field names are language-neutral: `original` is the text in the work's
        # original language (German for Marx and Engels, Russian for Lenin ...).
        d = {"id": v["id"], "kind": v["kind"], "original": v["de"], "en": v["en"]}
        if "joined_to" in v:
            d["joined_to"] = v["joined_to"]
            d["modern"] = ""
        else:
            d["modern"] = v.get("modern", "")
        d["modern_status"] = "seed" if d["modern"] else ("joined" if "joined_to" in v else "empty")
        d["notes"] = ""
        for k in ("note_edition", "footnotes", "de_variants", "mew_page", "en_note", "de_note", "align", "review", "review_reason"):
            if k in v:
                d[RENAME.get(k, k)] = v[k]
        out.append(d)
    return out


RENAME = {"de_variants": "variants", "de_note": "original_note", "title_de": "title_original", "source_de": "source_original"}


def dump(path, meta, verses):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {RENAME.get(k, k): v for k, v in meta.items()}
    doc["verses"] = verses
    with path.open("w", encoding="utf-8") as f:
        f.write("# Master file. Edit the `modern` and `notes` fields; see CONTRIBUTING.md.\n")
        f.write("# Verse ids are frozen. Never renumber; see VERSIFICATION.md.\n")
        yaml.dump(doc, f, allow_unicode=True, sort_keys=False, width=100000, default_flow_style=False)


def P(kind, text, **kw):
    d = {"kind": kind, "text": text}
    d.update(kw)
    return d


