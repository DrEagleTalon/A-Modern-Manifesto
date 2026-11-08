"""Check the verse files before anything is merged.

    python scripts/validate.py              # check everything
    python scripts/validate.py --update-lock   # record newly split verse ids (a/b suffixes)

Rules enforced (see VERSIFICATION.md and CONTRIBUTING.md):
  * every verse id is well formed and unique across the whole text
  * no id listed in text/verse-ids.lock may disappear (numbering is frozen)
  * a new id is only allowed as a split of a locked id: I.12.3 -> I.12.3a, I.12.3b
  * required fields exist, and `kind` / `modern_status` use the allowed values
  * `joined_to` points at an existing earlier verse, and joined verses keep `modern` empty
  * optional `readings` entries have the expected keys
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "text"
LOCK = TEXT / "verse-ids.lock"

ID_RE = re.compile(r"^(?:0|I|II|III|IV|N\d+|E\d+|P18\d\d|P18\d\d\.N\d+)\.\d+\.\d+[a-z]?$")
KINDS = {"heading", "p", "signature", "note"}
STATUSES = {"empty", "seed", "draft", "reviewed", "settled", "joined"}
REQUIRED = ["id", "kind", "de", "en", "modern", "modern_status", "notes"]
META = ["section", "title_de", "title_en", "original_language", "anchor_language", "source_de", "source_en", "verses"]
READING_KEYS = {"tradition", "rendering", "argument", "proposed_by"}


def load_all():
    files = sorted(TEXT.glob("*/*.yaml"))
    out = []
    for f in files:
        with f.open(encoding="utf-8") as fh:
            out.append((f, yaml.safe_load(fh)))
    return out


def main(update_lock=False):
    errors, warnings = [], []
    seen = {}
    order = []
    for f, doc in load_all():
        rel = f.relative_to(ROOT)
        for k in META:
            if k not in doc:
                errors.append(f"{rel}: missing top-level key '{k}'")
        ids_here = set()
        for i, v in enumerate(doc.get("verses", [])):
            where = f"{rel} verse #{i + 1}"
            for k in REQUIRED:
                if k not in v:
                    errors.append(f"{where}: missing field '{k}'")
            vid = str(v.get("id", ""))
            where = f"{rel} {vid}"
            if not ID_RE.match(vid):
                errors.append(f"{where}: malformed id")
            if vid in seen:
                errors.append(f"{where}: duplicate id (also in {seen[vid]})")
            seen[vid] = rel
            order.append(vid)
            if v.get("kind") not in KINDS:
                errors.append(f"{where}: kind must be one of {sorted(KINDS)}")
            st = v.get("modern_status")
            if st not in STATUSES:
                errors.append(f"{where}: modern_status must be one of {sorted(STATUSES)}")
            modern = (v.get("modern") or "").strip()
            if "joined_to" in v:
                if v["joined_to"] not in ids_here:
                    errors.append(f"{where}: joined_to '{v['joined_to']}' is not an earlier verse in this file")
                if modern:
                    errors.append(f"{where}: joined verse must leave `modern` empty (write it on {v['joined_to']})")
                if st != "joined":
                    errors.append(f"{where}: joined verse must have modern_status 'joined'")
            else:
                if st == "joined":
                    errors.append(f"{where}: modern_status 'joined' needs a joined_to field")
                if modern and st == "empty":
                    errors.append(f"{where}: has modern text but modern_status is 'empty' (use draft)")
                if not modern and st not in ("empty",):
                    errors.append(f"{where}: modern_status '{st}' but `modern` is empty")
            for r in v.get("readings", []) or []:
                missing = READING_KEYS - set(r)
                if missing:
                    errors.append(f"{where}: reading is missing {sorted(missing)}")
            if v.get("review") and not v.get("review_reason"):
                warnings.append(f"{where}: review flag without review_reason")
            ids_here.add(vid)

    # frozen numbering
    if LOCK.exists():
        locked = [ln.strip() for ln in LOCK.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
        lockset = set(locked)
        split_bases = {re.sub(r"[a-z]$", "", v) for v in seen if re.search(r"\d[a-z]$", v)}
        for vid in locked:
            if vid not in seen and vid not in split_bases:
                errors.append(f"locked verse id {vid} has been removed or renamed (ids are frozen; see VERSIFICATION.md)")
        new = [vid for vid in order if vid not in lockset]
        for vid in new:
            base = re.sub(r"[a-z]$", "", vid)
            if base == vid or base not in lockset:
                errors.append(f"new verse id {vid} is not a split (a/b/c suffix) of a locked id")
        if update_lock and new and not errors:
            with LOCK.open("a", encoding="utf-8") as fh:
                for vid in new:
                    fh.write(vid + "\n")
            print(f"lock: recorded {len(new)} new split id(s)")
    elif update_lock:
        LOCK.write_text("# Frozen verse ids. Never delete or edit a line. See VERSIFICATION.md.\n" + "\n".join(order) + "\n", encoding="utf-8")
        print(f"lock: created with {len(order)} ids")

    # glossary references must point at real verses
    gpath = ROOT / "glossary" / "terms.yaml"
    if gpath.exists():
        for entry in yaml.safe_load(gpath.read_text(encoding="utf-8")) or []:
            for ref in entry.get("verses", []):
                if str(ref) not in seen and f"{ref}a" not in seen:
                    errors.append(f"glossary '{entry.get('term')}': verse {ref} does not exist")
            if entry.get("status") not in ("open", "interim", "decided"):
                errors.append(f"glossary '{entry.get('term')}': status must be open, interim or decided")

    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(seen)} verses checked, {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(update_lock="--update-lock" in sys.argv))
