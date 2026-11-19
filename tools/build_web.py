"""Build the website: inlines the data into web/template.html -> index.html.

The built index.html sits at the repository root, so GitHub Pages
("Deploy from a branch", main, / root) serves it at the site address.

Usage: python tools/build_web.py
"""
import json, os

from actorio import ROOT, load_all
from pcmodel import MODEL, FACET_IDS, load_frames

questions = json.load(open(os.path.join(ROOT, "data", "questions.json"), encoding="utf-8"))
types = json.load(open(os.path.join(ROOT, "data", "types.json"), encoding="utf-8"))
actors = load_all()
frames = load_frames()


def pack_snapshot(s):
    vals, conf = [], ""
    for f in FACET_IDS:
        v = s["facets"].get(f)
        vals.append(None if v is None else v[0])
        conf += "-" if v is None else v[1]
    out = {"y": s["year"], "l": s["label"], "m": s["method"], "f": vals, "c": conf}
    if s.get("proxies"):
        out["p"] = s["proxies"]
    if s.get("notes"):
        out["n"] = s["notes"]
    if s.get("salience"):
        out["s"] = s["salience"]
    if s.get("basis"):
        out["b"] = s["basis"]
    src = [x for x in s.get("sources", []) if x.get("url")]
    if src:
        out["src"] = src
    return out


data = {
    "axes": [
        {"id": a["id"], "name": a["name"], "neg": a["neg"], "pos": a["pos"],
         "facets": [{"id": f["id"], "name": f["name"], "neg": f["neg"], "mid": f["mid"], "pos": f["pos"]} for f in a["facets"]]}
        for a in MODEL["axes"]
    ],
    "facetIds": FACET_IDS,
    "band": MODEL["scale"]["centre_band"],
    "questions": questions,
    "types": types,
    "frames": {k: {"name": v["name"], "parties": v["parties"], "basis": v["weight_basis"]} for k, v in frames.items()},
    "actors": [
        {"id": a["id"], "type": a["type"], "kind": a.get("kind"), "party": a.get("party"),
         "name": a["name"], "full": a["full_name"], "country": a["country"],
         "active": a["active"], "pred": a.get("predecessors", []), "succ": a.get("successors", []),
         "snaps": [pack_snapshot(s) for s in a["snapshots"]]}
        for a in sorted(actors.values(), key=lambda a: a["id"])
    ],
}

tpl = open(os.path.join(ROOT, "web", "template.html"), encoding="utf-8").read()
js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
chars = open(os.path.join(ROOT, "web", "characters.js"), encoding="utf-8").read()
html = tpl.replace("/*__DATA__*/null", js).replace("/*__CHARACTERS__*/", chars)
assert "/*__DATA__*/" not in html and "/*__CHARACTERS__*/" not in html, "placeholder not found"
out = os.path.join(ROOT, "index.html")
open(out, "w", encoding="utf-8").write(html)
print(f"wrote index.html ({len(html) // 1024} KB)")
