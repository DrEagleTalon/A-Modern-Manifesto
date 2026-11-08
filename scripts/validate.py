"""Check every work and every adaptation before anything is merged.

    python scripts/validate.py                     # check everything
    python scripts/validate.py --update-lock       # record new split ids (a/b suffixes)
    python scripts/validate.py --init-lock <work>  # create the lock file for a newly ingested work

Rules (see VERSIFICATION.md and CONTRIBUTING.md):
  works/<work>/work.yaml    required keys, unique citation prefix
  works/<work>/text/**.yaml every verse id well formed and unique within the work;
                            ids in verse-ids.lock never disappear; new ids only as a/b splits;
                            required fields and allowed values; joined_to rules; readings shape
  works/<work>/glossary.yaml verse references exist
  adaptations/*/*.md        every citation like "WLC II.4.2" points at a real verse
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKS = ROOT / "works"
ADAPT = ROOT / "adaptations"

ID_RE = re.compile(r"^(?:0|[A-Z][A-Z0-9]*)(?:\.[NE]\d+)?\.\d+\.\d+[a-z]?$")
KINDS = {"heading", "p", "signature", "note"}
STATUSES = {"empty", "seed", "draft", "reviewed", "settled", "joined"}
REQUIRED = ["id", "kind", "original", "en", "modern", "modern_status", "notes"]
META = ["section", "title_original", "title_en", "original_language", "anchor_language", "source_original", "source_en", "verses"]
WORK_KEYS = ["id", "prefix", "title", "authors", "year", "original_language", "base_text", "columns", "status"]
READING_KEYS = {"tradition", "rendering", "argument", "proposed_by"}
CITE_RE = re.compile(r"\b([A-Z]{2,6}) ((?:0|[A-Z][A-Z0-9]*)(?:\.[NE]\d+)?\.\d+\.\d+[a-z]?)\b")


def load_works():
    works = []
    for wy in sorted(WORKS.glob("*/work.yaml")):
        meta = yaml.safe_load(wy.read_text(encoding="utf-8"))
        files = sorted((wy.parent / "text").glob("**/*.yaml"))
        docs = [(f, yaml.safe_load(f.read_text(encoding="utf-8"))) for f in files]
        works.append((wy.parent, meta, docs))
    return works


def check_work(wdir, meta, docs, errors, warnings, update_lock=False, init_lock=False):
    rel = lambda p: p.relative_to(ROOT)  # noqa: E731
    for k in WORK_KEYS:
        if k not in meta:
            errors.append(f"{rel(wdir / 'work.yaml')}: missing '{k}'")
    seen, order = {}, []
    for f, doc in docs:
        for k in META:
            if k not in doc:
                errors.append(f"{rel(f)}: missing top-level key '{k}'")
        ids_here = set()
        for i, v in enumerate(doc.get("verses", [])):
            for k in REQUIRED:
                if k not in v:
                    errors.append(f"{rel(f)} verse #{i + 1}: missing field '{k}'")
            vid = str(v.get("id", ""))
            where = f"{rel(f)} {vid}"
            if not ID_RE.match(vid):
                errors.append(f"{where}: malformed id")
            if vid in seen:
                errors.append(f"{where}: duplicate id (also in {seen[vid]})")
            seen[vid] = rel(f)
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
                if not modern and st != "empty":
                    errors.append(f"{where}: modern_status '{st}' but `modern` is empty")
            for r in v.get("readings", []) or []:
                missing = READING_KEYS - set(r)
                if missing:
                    errors.append(f"{where}: reading is missing {sorted(missing)}")
            if v.get("review") and not v.get("review_reason"):
                warnings.append(f"{where}: review flag without review_reason")
            ids_here.add(vid)

    lock = wdir / "verse-ids.lock"
    if init_lock and not lock.exists():
        lock.write_text("# Frozen verse ids. Never delete or edit a line. See VERSIFICATION.md.\n" + "\n".join(order) + "\n", encoding="utf-8")
        print(f"{meta.get('prefix')}: lock created with {len(order)} ids")
    if lock.exists():
        locked = [ln.strip() for ln in lock.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
        lockset = set(locked)
        split_bases = {re.sub(r"[a-z]$", "", v) for v in seen if re.search(r"\d[a-z]$", v)}
        for vid in locked:
            if vid not in seen and vid not in split_bases:
                errors.append(f"{meta.get('prefix')}: locked verse id {vid} has been removed or renamed (ids are frozen)")
        new = [vid for vid in order if vid not in lockset]
        for vid in new:
            base = re.sub(r"[a-z]$", "", vid)
            if base == vid or base not in lockset:
                errors.append(f"{meta.get('prefix')}: new verse id {vid} is not a split (a/b/c suffix) of a locked id")
        if update_lock and new and not errors:
            with lock.open("a", encoding="utf-8") as fh:
                fh.write("\n".join(new) + "\n")
            print(f"{meta.get('prefix')}: recorded {len(new)} new split id(s)")
    elif docs:
        errors.append(f"{rel(wdir)}: no verse-ids.lock (run validate.py --init-lock {wdir.name} once the first numbering is final)")

    g = wdir / "glossary.yaml"
    if g.exists():
        for entry in yaml.safe_load(g.read_text(encoding="utf-8")) or []:
            for ref in entry.get("verses", []):
                if str(ref) not in seen and f"{ref}a" not in seen:
                    errors.append(f"{rel(g)} '{entry.get('term')}': verse {ref} does not exist")
            if entry.get("status") not in ("open", "interim", "decided"):
                errors.append(f"{rel(g)} '{entry.get('term')}': status must be open, interim or decided")
    return set(seen)


def check_adaptations(index, errors):
    for md in sorted(ADAPT.glob("*/*.md")):
        if md.parent.name.startswith("_"):
            continue
        text = md.read_text(encoding="utf-8")
        for prefix, vid in CITE_RE.findall(text):
            if prefix not in index:
                continue        # not a library citation (e.g. an acronym)
            if vid not in index[prefix] and f"{vid}a" not in index[prefix]:
                errors.append(f"{md.relative_to(ROOT)}: cites {prefix} {vid}, which does not exist")


def main(argv):
    errors, warnings = [], []
    index, prefixes = {}, {}
    init_target = argv[argv.index("--init-lock") + 1] if "--init-lock" in argv else None
    total = 0
    for wdir, meta, docs in load_works():
        p = meta.get("prefix")
        if p in prefixes:
            errors.append(f"citation prefix {p} used by both {prefixes[p]} and {wdir.name}")
        prefixes[p] = wdir.name
        ids = check_work(wdir, meta, docs, errors, warnings,
                         update_lock="--update-lock" in argv, init_lock=(init_target == wdir.name))
        index[p] = ids
        total += len(ids)
    check_adaptations(index, errors)
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(index)} work(s), {total} verses checked, {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
