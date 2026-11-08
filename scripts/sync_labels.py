"""Create or update the repository's labels from the library's own data.

    python scripts/sync_labels.py OWNER/REPO            # apply
    python scripts/sync_labels.py OWNER/REPO --dry-run  # show what would change

Labels come from three places, so they never drift from the content:
  .github/labels.yml        fixed labels (kinds of commentary, topics, states)
  works/*/work.yaml         one "work: <PREFIX>" label per work
  traditions.yaml           one "tradition: <slug>" label per tradition (same slug as the folders)

Uses the GitHub CLI (`gh api`), which GitHub Actions provides with GH_TOKEN. Existing labels that are not in
this list (GitHub's defaults, or ones added by hand) are left alone.
"""
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parents[1]


def wanted():
    labels = yaml.safe_load((ROOT / ".github" / "labels.yml").read_text(encoding="utf-8"))
    for wy in sorted((ROOT / "works").glob("*/work.yaml")):
        w = yaml.safe_load(wy.read_text(encoding="utf-8"))
        labels.append({"name": f"work: {w['prefix']}", "color": "1d76db", "description": f"{w['title']} ({w['year']})"[:100]})
    for t in yaml.safe_load((ROOT / "traditions.yaml").read_text(encoding="utf-8")):
        labels.append({"name": f"tradition: {t['slug']}", "color": "bfd4f2", "description": f"{t['name']}. Code {t['code']}."[:100]})
    return labels


def gh(args, data=None):
    cmd = ["gh", "api", *args]
    if data is not None:
        cmd += ["--input", "-"]
    r = subprocess.run(cmd, input=json.dumps(data) if data is not None else None, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or r.stdout.strip())
    return json.loads(r.stdout) if r.stdout.strip() else None


def main(repo, dry):
    have = {l["name"].lower(): l for l in gh([f"repos/{repo}/labels?per_page=100", "--paginate"]) or []}
    created = updated = 0
    for l in wanted():
        cur = have.get(l["name"].lower())
        if cur is None:
            print("create", l["name"])
            if not dry:
                gh(["-X", "POST", f"repos/{repo}/labels"], l)
            created += 1
        elif cur.get("color", "").lower() != l["color"].lower() or (cur.get("description") or "") != l["description"]:
            print("update", l["name"])
            if not dry:
                gh(["-X", "PATCH", f"repos/{repo}/labels/{quote(cur['name'], safe='')}"],
                   {"new_name": l["name"], "color": l["color"], "description": l["description"]})
            updated += 1
    print(f"{created} created, {updated} updated{' (dry run)' if dry else ''}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], "--dry-run" in sys.argv)
