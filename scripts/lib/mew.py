"""Readers for the two HTML sources most works in this library come from.

MEW (Marx/Engels Werke, Dietz Verlag) as transcribed at mlwerke.de
    parse_mew(path) -> paragraphs, footnotes, variants
    Inline markers kept for the versifier:
        [[F2]]   author footnote 2 attaches here
        [[T14]]  editorial text-variant 14 starts here (another edition reads differently)
        [[S462]] MEW page 462 starts here

Marxists Internet Archive (MIA) work pages
    parse_mia(path) -> list of {"kind", "text"}, list of removed editorial insertions
"""
import re
from pathlib import Path

from bs4 import BeautifulSoup


# ------------------------------------------------------------------ MEW

def _mark(html: str) -> str:
    html = re.sub(r'<A[^>]*HREF="#F(\d+)"[^>]*>(?:<[^>]+>)*\(\d+\)(?:<[^>]+>)*</A>', r" [[F\1]] ", html, flags=re.I)
    # variants are linked as #T<n> (most volumes) or #M<n> (MEW 6)
    html = re.sub(r'<A[^>]*HREF="#[TM](\d+)"[^>]*>(?:<[^>]+>)*\{\d+\}(?:<[^>]+>)*</A>', r" [[T\1]] ", html, flags=re.I)
    html = re.sub(r'<A[^>]*NAME="S(\d+)"[^>]*>\s*(<B>)?\s*\|\d+\|\s*(</B>)?\s*</A>', r" [[S\1]] ", html, flags=re.I)
    html = re.sub(r'\|(\d{1,3})\|', r" [[S\1]] ", html)            # bare |462|
    html = re.sub(r'&lt;(\d{1,3})&gt;', r" [[S\1]] ", html)         # MEW 6 style <397>
    html = re.sub(r"(\w+)-\s*(\[\[S\d+\]\])\s*(?:<[^>]+>\s*)*([a-zäöü&])", r"\2 \1\3", html)
    html = re.sub(r'<A[^>]*HREF="#Z[FTM]\d+"[^>]*>.*?</A>', " ", html, flags=re.I | re.S)
    return html


WORD_SPLIT_TAG = re.compile(r"(?<=[A-Za-zäöüÄÖÜß;])</?(?:I|B|SMALL|SUP|U|EM|STRONG)>(?=[a-zäöüß&])", re.I)


def _text(fragment: str) -> str:
    fragment = WORD_SPLIT_TAG.sub("", fragment)        # "Arbeits<I>kraft</I>" is one word
    s = BeautifulSoup(fragment, "html.parser").get_text(" ")
    s = s.replace("\xa0", " ").replace("\xad", "")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:!?)])", r"\1", s)
    s = re.sub(r"\(\s+", "(", s)
    s = s.replace("<=", "").strip()
    s = re.sub(r"\|([^|\[\]]+)\|", r"[\1]", s)      # MEW editorial insertion |...| -> [...]
    return s


def _blocks(html: str):
    for m in re.finditer(r"<(H[345]|P)\b([^>]*)>(.*?)(?=<H[345]\b|<P\b|<HR\b|</BODY>)", html, flags=re.I | re.S):
        yield m.group(1).upper(), m.group(2), m.group(3)


def parse_mew(path: Path, signature_re=r"^(London|Karl Marx|Friedrich Engels|F\. Engels)"):
    data = Path(path).read_bytes()
    try:                                   # most mlwerke pages are Latin-1, some are UTF-8
        raw = data.decode("utf-8")
    except UnicodeDecodeError:
        raw = data.decode("latin-1")
    raw = raw.replace("\r", "")
    html = _mark(raw)
    paras, notes, variants = [], {}, {}
    state, cur_note = "pre", None
    for tag, attr, inner in _blocks(html):
        txt = _text(inner)
        if not txt:
            continue
        if state == "pre":
            if "[[S" in txt and not txt.startswith("Seitenzahlen"):
                state = "body"
            else:
                continue
        if state == "body":
            if re.match(r"^(Fußnoten|Textvarianten|In der \")", txt):
                state = "apparatus"
                continue
            if re.search(r'NAME="[FTM]\d+"', inner, re.I):
                state = "apparatus"
            elif txt.startswith("MLWerke") or txt.startswith("Marx/Engels - Werke"):
                break
            else:
                kind = "heading" if tag.startswith("H") or ("CENTER" in attr.upper() and len(txt) < 120) else "p"
                paras.append({"kind": kind, "de": txt})
                continue
        if state == "apparatus":
            if txt.startswith(("Textvarianten", "MLWerke", "In der")):
                cur_note = None
                if txt.startswith("MLWerke"):
                    break
                continue
            mf = re.search(r'NAME="F(\d+)"', inner, re.I)
            mt = re.search(r'NAME="[TM](\d+)"', inner, re.I)
            if mf:
                cur_note = mf.group(1)
                notes[cur_note] = [re.sub(r"^\(\d+\)\s*", "", txt)]
            elif mt:
                cur_note = None
                body = re.sub(r"^\{\d+\}\s*", "", txt)
                mm = re.match(r"\(([^)]*)\)\s*(.*)$", body)
                variants[mt.group(1)] = {"editions": mm.group(1) if mm else "", "reading": (mm.group(2) if mm else body).strip()}
            elif cur_note:
                notes[cur_note].append(txt)
    for p in paras:
        if re.match(signature_re, p["de"]) and len(p["de"]) < 80:
            p["kind"] = "signature"
    return paras, notes, variants


# ------------------------------------------------------------------ MIA

INSERTION = re.compile(r"\s*\[(?!\d+\])[^\[\]]{3,}\]")


def parse_mia(path: Path, keep_classes=()):
    """Paragraphs of a marxists.org work page. Drops navigation, MIA footnotes and
    MIA's square-bracket editorial insertions (returned separately so they can be logged)."""
    html = Path(path).read_text(encoding="utf-8", errors="replace").replace("﻿", "")
    html = re.sub(r"<sup[^>]*>.*?</sup>", "", html, flags=re.S | re.I)          # end-note refs
    cut = re.search(r"<h3>\s*Footnotes", html, flags=re.I)
    if cut:
        html = html[:cut.start()]
    out, removed = [], []
    for m in re.finditer(r"<(h[1-6]|p)\b([^>]*)>(.*?)(?=<h[1-6]\b|<p\b|<hr\b|</body>)", html, flags=re.S | re.I):
        tag, attr, inner = m.group(1).lower(), m.group(2), m.group(3)
        cls = re.search(r'class="([^"]+)"', attr)
        cls = cls.group(1) if cls else ""
        if cls in ("title", "footer", "information", "skip", "toc", "link") and cls not in keep_classes:
            continue
        text = BeautifulSoup(inner, "html.parser").get_text(" ")
        text = re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()
        if not text:
            continue
        for ins in INSERTION.findall(text):
            removed.append(ins.strip())
        text = INSERTION.sub("", text)
        text = re.sub(r"“\s+", "“", re.sub(r"\s+”", "”", text))      # MIA pads curly quotes with spaces
        text = re.sub(r'([.!?,;]) "(?=\s|$)', r'\1"', text)                # ...wages. " -> ...wages."
        text = re.sub(r'(^|[\s:(])" (?=[A-Za-z])', r'\1"', text)            # : " The -> : "The
        text = re.sub(r"\s+([,.;:!?)])", r"\1", text).replace("“", '"').replace("”", '"').replace("’", "'").replace(" – ", " - ")
        kind = "heading" if tag.startswith("h") else ("signature" if cls == "sig" else "p")
        if tag == "h4" and text.lower().startswith("by "):
            continue
        out.append({"kind": kind, "text": text, "cls": cls})
    return out, removed
