"""Shared helpers for reading and writing actor profiles."""
import glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTORS = os.path.join(ROOT, "data", "actors")


def actor_path(actor_id):
    country, slug = actor_id.split("-", 1)
    return os.path.join(ACTORS, country, slug + ".json")


def load_all():
    out = {}
    for path in sorted(glob.glob(os.path.join(ACTORS, "*", "*.json"))):
        with open(path, encoding="utf-8") as f:
            a = json.load(f)
        out[a["id"]] = a
    return out


def save(actor):
    path = actor_path(actor["id"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    actor["snapshots"].sort(key=lambda s: (s["year"], s["method"]))
    txt = json.dumps(actor, ensure_ascii=False, indent=2)
    # keep [score, "c"] pairs on one line
    txt = re.sub(r'\[\s*(-?\d+),\s*"(\w)"\s*\]', r'[\1, "\2"]', txt)
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt + "\n")
