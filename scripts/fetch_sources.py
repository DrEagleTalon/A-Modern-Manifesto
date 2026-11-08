"""Download a work's raw source files listed in catalog.yaml into works/<id>/sources/raw/.

    python scripts/fetch_sources.py <work-id>          # fetch, write sources/MANIFEST.yaml
    python scripts/fetch_sources.py <work-id> --list   # show what would be fetched

Source forms understood in catalog.yaml (`sources.original`, `sources.english`, `sources.german`):

  mlwerke:me08/me08_111.htm                one MEW page from github.com/wertform/mlwerke.de
  mlwerke:me21/me21_025.htm..me21_173.htm  every MEW page in that range (inclusive)
  mia:en/archive/marx/works/1880/soc-utop/ every .html page in that Marxists Internet Archive folder
  gutenberg:Socialism--Utopian-and-Scientific_39257   the plain-text book from github.com/GITenberg

Anything after a space ("... and following", "(note)") is ignored, so catalog entries can carry a remark.
Folder and range listings come from a blob-less clone of the mirror kept in .cache/ (not committed).
Files are stored as fetched, byte for byte; MANIFEST.yaml records URL, size and SHA-256.
"""
import hashlib
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache"
MIRRORS = {
    "mlwerke": ("https://github.com/wertform/mlwerke.de.git", "https://raw.githubusercontent.com/wertform/mlwerke.de/HEAD/me/", "me/"),
    "mia": ("https://github.com/MARX-EBOOKS/marx-ebooks.github.io.git", "https://raw.githubusercontent.com/MARX-EBOOKS/marx-ebooks.github.io/HEAD/", ""),
}


def tree(name):
    """File list of a mirror, from a blob-less shallow clone (fast: no file contents are downloaded)."""
    repo, _, _ = MIRRORS[name]
    d = CACHE / name
    if not (d / ".git").exists():
        CACHE.mkdir(exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", "--depth", "1", repo, str(d)], check=True)
    out = subprocess.run(["git", "-C", str(d), "ls-tree", "-r", "HEAD", "--name-only"], capture_output=True, text=True, check=True)
    return out.stdout.split("\n")


def expand(spec):
    """Return list of (url, local relative path)."""
    spec = spec.split(" ")[0]
    kind, _, rest = spec.partition(":")
    if kind == "gutenberg":
        n = rest.rsplit("_", 1)[1]
        return [(f"https://raw.githubusercontent.com/GITenberg/{rest}/master/{n}.txt", f"gutenberg_{n}.txt")]
    if kind not in MIRRORS:
        raise SystemExit(f"unknown source kind in {spec!r}")
    _, raw, prefix = MIRRORS[kind]
    if ".." in rest:
        a, b = rest.split("..")
        folder = a.rsplit("/", 1)[0]
        b = b if "/" in b else f"{folder}/{b}"
        files = sorted(f[len(prefix):] for f in tree(kind)
                       if f.startswith(prefix + folder + "/") and f.endswith((".htm", ".html")) and a <= f[len(prefix):] <= b)
    elif rest.endswith("/"):
        files = sorted(f for f in tree(kind) if f.startswith(rest) and f.endswith((".html", ".htm")) and "/" not in f[len(rest):])
    else:
        files = [rest]
    return [(raw + f, f.split("/")[-1]) for f in files]


def fetch(url):
    # Project Gutenberg files may be named <n>.txt, <n>-0.txt (UTF-8) or <n>-8.txt (Latin-1)
    tries = [url]
    if "GITenberg" in url and url.endswith(".txt"):
        tries += [url[:-4] + "-0.txt", url[:-4] + "-8.txt"]
    for i, u in enumerate(tries):
        try:
            with urllib.request.urlopen(u, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError:
            if i == len(tries) - 1:
                raise


def main(work_id, list_only=False):
    cat = yaml.safe_load((ROOT / "catalog.yaml").read_text(encoding="utf-8"))
    entry = next((e for e in cat if e["id"] == work_id), None)
    if entry is None:
        raise SystemExit(f"{work_id} is not in catalog.yaml")
    dest = ROOT / "works" / work_id / "sources"
    manifest = []
    for role, specs in (entry.get("sources") or {}).items():
        sub = {"original": entry["original_language"], "english": "en", "german": "de"}.get(role, role)
        for spec in specs:
            for url, name in expand(spec):
                path = dest / "raw" / sub / name
                print(("would fetch " if list_only else "fetch ") + url)
                if list_only:
                    continue
                data = fetch(url)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                manifest.append({"file": str(path.relative_to(dest)), "role": role, "url": url,
                                 "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    if not list_only:
        (dest / "MANIFEST.yaml").write_text(
            f"# Fetched {date.today().isoformat()} by scripts/fetch_sources.py from catalog.yaml. Raw files are never edited.\n"
            + yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
        print(f"{len(manifest)} file(s) written to {dest.relative_to(ROOT)}/raw")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], "--list" in sys.argv)
