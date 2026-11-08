"""Rule-based sentence segmentation for 19th-century German and English prose.

Kept deliberately simple and transparent so contributors can see why a verse
boundary falls where it does. Boundaries are frozen once published (see
VERSIFICATION.md); this code is only used to create the first numbering.
"""
import re

MARK = r"(?:\s*\[\[[A-Z]\d+\]\])*"   # footnote / variant / page markers that may follow punctuation

ABBR = {
    "de": {"z", "B", "d", "h", "usw", "u", "s", "w", "S", "Nr", "vgl", "Dr", "St", "ca", "bzw", "etc", "Hr", "resp", "Bd", "Aufl", "Mr", "M", "p", "pp"},
    "en": {"Mr", "Mrs", "Messrs", "St", "Dr", "viz", "e", "g", "i", "&c", "No", "p", "pp", "vol", "cf", "M", "Mme", "ed", "Vol", "etc"},
}

# Roman numerals and initials that end with a period but do not end a sentence.
NON_TERMINAL = re.compile(r"(?:\b[IVX]{1,4}|\b[A-Z]|\b\d{1,2})$")


def _is_boundary(before: str, after: str, lang: str) -> bool:
    if not after:
        return False
    m = re.search(r"([\w&]+)\.[\"'”’)]*$", before)
    closed = bool(re.search(r"\.[\"'”’)]+$", before))   # "... S. 19.)" or '... etc."' ends a sentence
    if m and not closed:
        tok = m.group(1)
        if tok in ABBR[lang]:
            return False
        if NON_TERMINAL.search(tok):
            # "18. März", "Ferdinand I.", "F. Engels", "2. Auflage", list items "1. Expropriation"
            # A number at the very end of a long sentence ("... in 1848.") is a real boundary.
            if re.fullmatch(r"\d{3,4}", tok):
                return True
            return False
    # next sentence must start with an upper-case letter, a quote, a bracket or a digit
    if before.count("(") > before.count(")"):
        return False      # never split inside an open parenthesis
    return bool(re.match(r"(?:[-–—]\s*)?[\"'„“‘(\[A-ZÄÖÜ0-9]", after))


def split_sentences(text: str, lang: str):
    text = text.strip()
    if not text:
        return []
    out, start = [], 0
    for m in re.finditer(r"[.!?]+[\"'”’»)]*" + MARK + r"(?=\s|$)", text):
        end = m.end()
        before = text[start:end]
        after = text[end:].lstrip()
        # "?" inside a quotation followed by lower case continues the sentence
        if _is_boundary(before.rstrip(), after, lang):
            out.append(text[start:end].strip())
            start = end
    rest = text[start:].strip()
    if rest:
        out.append(rest)
    # list items like "1. Expropriation ..." keep the number with the item
    merged = []
    for s in out:
        if merged and re.fullmatch(r"(\d{1,2}|[IVX]{1,4}|[a-c]\))\.?", merged[-1]):
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)
    return merged
