"""Build the additional (mostly smaller and historical) parties from data/parties_extra.json.

These parties are scored at topic level: `s` gives one score per axis
(ECO SOC LIB MIG INT CLI TEC DEM) that every facet of that axis takes,
`f` sets single facets where the party clearly differs inside a topic,
`w` is salience per axis (1 to 5) and `n` holds notes per axis.
Topic-level facets get confidence "l", explicit facets "m".
Facets for issues that did not exist yet in the snapshot year are left empty.

Writes data/actors/<country>/<id>.json (type "party"). Refuses to overwrite
a party that was not created by this script.

Usage: python tools/build_parties_extra.py
"""
import json, os

from actorio import ROOT, load_all, save
from pcmodel import AXIS_IDS, FACET_AXIS
from build_people import ERA

SRC = json.load(open(os.path.join(ROOT, "data", "parties_extra.json"), encoding="utf-8"))


def clamp(v):
    return max(-100, min(100, round(v)))


def main():
    existing = load_all()
    for p in SRC["parties"]:
        old = existing.get(p["id"])
        if old and not old.get("extra"):
            raise SystemExit(f"{p['id']} already exists and was not built by this script")
        snaps = []
        for s in p["snapshots"]:
            scores = dict(zip(AXIS_IDS, s["s"]))
            facets = {}
            for fid, ax in FACET_AXIS.items():
                if fid in s.get("f", {}):
                    facets[fid] = [clamp(s["f"][fid]), "m"]
                else:
                    facets[fid] = [clamp(scores[ax]), "l"]
            for fid, since in ERA:
                if s["year"] < since:
                    facets[fid] = None
            notes = {ax: s.get("n", {}).get(ax, f"Scored at topic level from the party's programme ({s['label']}).") for ax in AXIS_IDS}
            snaps.append({
                "year": s["year"], "label": s["label"], "method": "hand",
                "basis": "Scored by hand at topic level from programmes and record, with single parts set where the party differs. Draft.",
                "salience": dict(zip(AXIS_IDS, s["w"])), "facets": facets, "notes": notes,
                "sources": [{"title": f"Wikipedia: {p.get('wiki', p['full_name'])}",
                             "url": "https://en.wikipedia.org/wiki/" + p.get("wiki", p["full_name"]).replace(" ", "_")}],
            })
        actor = {
            "id": p["id"], "type": "party", "extra": True, "name": p["name"], "full_name": p["full_name"],
            "country": p["id"].split("-")[0].upper(), "active": p["active"],
            "predecessors": p.get("pred", []), "status": "draft", "snapshots": snaps,
        }
        if p.get("succ"):
            actor["successors"] = p["succ"]
        save(actor)
    print(len(SRC["parties"]), "extra parties written")


if __name__ == "__main__":
    main()
