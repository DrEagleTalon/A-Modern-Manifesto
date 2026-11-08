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
    sections = {str(d.get('section')) for _, d in docs} | {v.split('.')[0] for v in order}
    return order, sections


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


# ------------------------------------------------------------------ commentary and renderings

COMMENTARY = ROOT / "commentary"
RENDERINGS = ROOT / "renderings"
TRADITIONS = ROOT / "traditions.yaml"
KINDS_C = {"gloss", "translation", "exegesis", "context", "application", "critique", "development"}
RELATIONS = {"extends", "revises", "supersedes"}
STATUS_C = {"proposed", "accepted", "disputed", "retired"}
STATUS_R = {"draft", "reviewed"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TARGET = re.compile(r"^([A-Z]{2,6})(?: ([^\s-]+)(?:-([^\s]+))?)?$")


def resolve_target(t, works):
    """'CM' (whole work), 'CM II' (section), 'CM II.66.1' (verse), 'CM II.65.1-II.81.1' (range)."""
    m = TARGET.match(str(t).strip())
    if not m or m.group(1) not in works:
        return f"unknown work in '{t}'"
    w = works[m.group(1)]
    a, b = m.group(2), m.group(3)
    if a is None:
        return None
    if b is None and "." not in a:
        return None if a in w["sections"] else f"no section '{a}' in {m.group(1)}"
    for x in (a, b):
        if x is not None and x not in w["order"]:
            return f"no verse {m.group(1)} {x}"
    if b is not None and w["order"][b] < w["order"][a]:
        return f"range '{t}' runs backwards"
    return None


def load_traditions(errors):
    if not TRADITIONS.exists():
        errors.append("traditions.yaml is missing")
        return {}
    trads, codes = {}, set()
    for t in yaml.safe_load(TRADITIONS.read_text(encoding="utf-8")) or []:
        for k in ("slug", "code", "name", "description"):
            if not t.get(k):
                errors.append(f"traditions.yaml: entry {t.get('slug', '?')} missing '{k}'")
        if t.get("slug") in trads or t.get("code") in codes:
            errors.append(f"traditions.yaml: duplicate slug or code for {t.get('slug')}")
        trads[t.get("slug")] = t
        codes.add(t.get("code"))
    return trads


def check_commentary(works, errors):
    trads = load_traditions(errors)
    by_prefix = {p: w["id"] for p, w in works.items()}
    entries, n_c, n_r = {}, 0, 0
    files = [f for f in sorted(COMMENTARY.glob("*/*.yaml"))] if COMMENTARY.exists() else []
    # pass 1: collect ids so responds_to / see_also can point anywhere
    loaded = []
    for f in files:
        rel = f.relative_to(ROOT)
        doc = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        trad, work = doc.get("tradition"), str(doc.get("work", ""))
        if trad != f.parent.name:
            errors.append(f"{rel}: tradition '{trad}' must match its folder '{f.parent.name}'")
        if trad not in trads:
            errors.append(f"{rel}: tradition '{trad}' is not in traditions.yaml")
        if f.stem == "_library":
            if work != "*":
                errors.append(f"{rel}: _library.yaml must have work: \"*\"")
        elif work not in by_prefix or by_prefix[work] != f.stem:
            errors.append(f"{rel}: work '{work}' must be the prefix of works/{f.stem}")
        for e in doc.get("entries", []) or []:
            key = f"{trad}:{e.get('id')}"
            if not SLUG.match(str(e.get("id", ""))):
                errors.append(f"{rel}: entry id '{e.get('id')}' must be lower-case words joined by hyphens")
            if key in entries:
                errors.append(f"{rel}: duplicate entry id {key}")
            entries[key] = rel
            loaded.append((rel, trad, e))
    for rel, trad, e in loaded:
        n_c += 1
        where = f"{rel} {e.get('id')}"
        if e.get("kind") not in KINDS_C:
            errors.append(f"{where}: kind must be one of {sorted(KINDS_C)}")
        for k in ("title", "body", "targets", "authors", "status"):
            if not e.get(k):
                errors.append(f"{where}: missing '{k}'")
        if e.get("status") not in STATUS_C:
            errors.append(f"{where}: status must be one of {sorted(STATUS_C)}")
        for t in e.get("targets", []) or []:
            msg = resolve_target(t, works)
            if msg:
                errors.append(f"{where}: target {msg}")
        if e.get("kind") == "development":
            if e.get("relation") not in RELATIONS:
                errors.append(f"{where}: development entries need relation: extends | revises | supersedes")
            if not e.get("by"):
                errors.append(f"{where}: development entries need `by` (what extends, revises or supersedes it)")
        elif "relation" in e:
            errors.append(f"{where}: `relation` is only for development entries")
        refs = list(e.get("see_also", []) or []) + list(e.get("by", []) or [])
        if e.get("responds_to"):
            refs.append(e["responds_to"])
        for r in refs:
            r = str(r)
            if re.match(r"^[a-z0-9-]+:[a-z0-9-]+$", r):
                if r not in entries:
                    errors.append(f"{where}: refers to entry {r}, which does not exist")
            elif TARGET.match(r.split(" ")[0] if " " not in r else r) and r.split(" ")[0] in works:
                msg = resolve_target(r, works)
                if msg:
                    errors.append(f"{where}: reference {msg}")
            # anything else is a free-text source (a book outside the library), allowed
    rfiles = sorted(RENDERINGS.glob("*/*.yaml")) if RENDERINGS.exists() else []
    for f in rfiles:
        rel = f.relative_to(ROOT)
        doc = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        trad, work = doc.get("tradition"), str(doc.get("work", ""))
        if trad != f.parent.name or trad not in trads:
            errors.append(f"{rel}: tradition '{trad}' must match its folder and be in traditions.yaml")
        if work not in by_prefix or by_prefix[work] != f.stem:
            errors.append(f"{rel}: work '{work}' must be the prefix of works/{f.stem}")
            continue
        if not doc.get("principles"):
            errors.append(f"{rel}: say in `principles` how this rendering differs from the shared draft")
        seen = set()
        for v in doc.get("verses", []) or []:
            n_r += 1
            vid = str(v.get("verse", ""))
            if vid not in works[work]["order"]:
                errors.append(f"{rel}: no verse {work} {vid}")
            if vid in seen:
                errors.append(f"{rel}: verse {vid} rendered twice")
            seen.add(vid)
            if not v.get("text"):
                errors.append(f"{rel} {vid}: empty text")
            if v.get("status") not in STATUS_R:
                errors.append(f"{rel} {vid}: status must be draft or reviewed")
    return n_c, n_r


def main(argv):
    errors, warnings = [], []
    index, prefixes, works = {}, {}, {}
    init_target = argv[argv.index("--init-lock") + 1] if "--init-lock" in argv else None
    total = 0
    for wdir, meta, docs in load_works():
        p = meta.get("prefix")
        if p in prefixes:
            errors.append(f"citation prefix {p} used by both {prefixes[p]} and {wdir.name}")
        prefixes[p] = wdir.name
        order, sections = check_work(wdir, meta, docs, errors, warnings,
                                     update_lock="--update-lock" in argv, init_lock=(init_target == wdir.name))
        index[p] = set(order)
        works[p] = {"id": wdir.name, "order": {v: i for i, v in enumerate(order)}, "sections": sections}
        total += len(order)
    check_adaptations(index, errors)
    n_c, n_r = check_commentary(works, errors)
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(index)} work(s), {total} verses, {n_c} commentary entries, {n_r} rendered verses checked: "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
