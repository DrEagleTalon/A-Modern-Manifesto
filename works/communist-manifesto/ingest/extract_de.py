"""Extract German text (MEW, via the mlwerke.de mirror) into clean paragraph JSON.

Input:  sources/raw/de/*.htm  (Latin-1 HTML from the mlwerke.de mirror of MEW)
Output: sources/clean/de.json

Markers kept inline for the next stage:
  [[F2]]   Engels footnote 2 is attached here
  [[T14]]  MEW text-variant 14 starts here (earlier/later edition reading)
  [[S462]] MEW page 462 starts here
"""
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]   # works/communist-manifesto
RAW = ROOT / "sources" / "raw" / "de"

# section id -> (file, MEW volume, original language of the German text)
FILES = {
    "P1872": ("me18_095.htm", 18, "de"),
    "P1882": ("me19_295.htm", 19, "de"),
    "P1883": ("me21_003.htm", 21, "de"),
    "P1888": ("me21_352.htm", 21, "en"),   # MEW German is a translation of Engels's English
    "P1890": ("me22_052.htm", 22, "de"),
    "P1892": ("me22_282.htm", 22, "de"),
    "P1893": ("me22_365.htm", 22, "fr"),   # MEW German is a translation of Engels's French
    "CM": ("me04_459.htm", 4, "de"),
}


def mark(html: str) -> str:
    html = re.sub(r'<A[^>]*HREF="#F(\d+)"[^>]*>(?:<[^>]+>)*\(\d+\)(?:<[^>]+>)*</A>', r" [[F\1]] ", html, flags=re.I)
    html = re.sub(r'<A[^>]*HREF="#T(\d+)"[^>]*>(?:<[^>]+>)*\{\d+\}(?:<[^>]+>)*</A>', r" [[T\1]] ", html, flags=re.I)
    html = re.sub(r'<A[^>]*NAME="S(\d+)"[^>]*>\s*(<B>)?\s*\|\d+\|\s*(</B>)?\s*</A>', r" [[S\1]] ", html, flags=re.I)
    html = re.sub(r'\|(\d{1,3})\|', r" [[S\1]] ", html)  # bare page markers
    # words hyphenated across a MEW page break: "Un- |366| abhängigkeit" -> "[[S366]] Unabhängigkeit"
    html = re.sub(r"(\w+)-\s*(\[\[S\d+\]\])\s*(?:<[^>]+>\s*)*([a-zäöü&])", r"\2 \1\3", html)
    html = re.sub(r'<A[^>]*HREF="#Z[FT]\d+"[^>]*>.*?</A>', " ", html, flags=re.I | re.S)  # back links
    return html


def text_of(fragment: str) -> str:
    s = BeautifulSoup(fragment, "html.parser").get_text(" ")
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:!?)])", r"\1", s)
    s = re.sub(r"\(\s+", "(", s)
    s = s.replace("<=", "").strip()
    # MEW marks editorial insertions with |...|; show them as [...]
    s = re.sub(r"\|([^|\[\]]+)\|", r"[\1]", s)
    return s


def blocks(html: str):
    """Yield (tag, inner_html) for H3/H4/H5/P blocks in document order."""
    for m in re.finditer(r"<(H[345]|P)\b[^>]*>(.*?)(?=<H[345]\b|<P\b|<HR\b|</BODY>)", html, flags=re.I | re.S):
        yield m.group(1).upper(), m.group(2)


def extract(sec, fname, vol, orig):
    raw = (RAW / fname).read_text(encoding="latin-1").replace("\r", "")
    html = mark(raw)
    paras, notes, variants = [], {}, {}
    state = "pre"
    cur_note = None
    for tag, inner in blocks(html):
        txt = text_of(inner)
        if not txt:
            continue
        if state == "pre":
            if "[[S" in txt and not txt.startswith("Seitenzahlen"):
                state = "body"
            else:
                continue
        if state == "body":
            if re.match(r"^(Fußnoten|Textvarianten)", txt):
                state = "apparatus"
                continue
            if re.search(r'NAME="F\d+"', inner, re.I) or re.search(r'NAME="T\d+"', inner, re.I):
                state = "apparatus"
            elif txt.startswith("MLWerke") or txt.startswith("Marx/Engels - Werke"):
                break
            else:
                kind = "heading" if tag.startswith("H") else "p"
                paras.append({"kind": kind, "de": txt})
                continue
        if state == "apparatus":
            if txt.startswith("Textvarianten") or txt.startswith("MLWerke"):
                cur_note = None
                if txt.startswith("MLWerke"):
                    break
                continue
            mf = re.search(r'NAME="F(\d+)"', inner, re.I)
            mt = re.search(r'NAME="T(\d+)"', inner, re.I)
            if mf:
                cur_note = mf.group(1)
                body = re.sub(r"^\(\d+\)\s*", "", txt)
                notes[cur_note] = [body]
            elif mt:
                cur_note = None
                body = re.sub(r"^\{\d+\}\s*", "", txt)
                mm = re.match(r"\(([^)]*)\)\s*(.*)$", body)
                variants[mt.group(1)] = {"editions": mm.group(1) if mm else "", "reading": (mm.group(2) if mm else body).strip()}
            elif cur_note:
                notes[cur_note].append(txt)
    # Signatures / place-date lines at the end of prefaces
    for p in paras:
        if re.match(r"^(London|Karl Marx|Friedrich Engels|F\. Engels|Karl Marx\s*-?\s*F\. Engels)", p["de"]) and len(p["de"]) < 80:
            p["kind"] = "signature"
    return {"id": sec, "mew_volume": vol, "de_original_language": orig, "paragraphs": paras,
            "notes": notes, "variants": variants}


def main():
    out = {sec: extract(sec, *spec) for sec, spec in FILES.items()}
    dest = ROOT / "sources" / "clean" / "de.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for sec, d in out.items():
        print(sec, len(d["paragraphs"]), "paras", len(d["notes"]), "notes", len(d["variants"]), "variants", file=sys.stderr)


if __name__ == "__main__":
    main()
