"""Build profiles of politicians and public figures from data/people.json.

Each person starts from a party snapshot of their era (base actor + year)
and is adjusted where their own documented views differ:
  axes:   shift every facet of an axis by a number of points
  facets: set a facet to a specific score
Adjusted parts get their own note; the rest says the profile follows the party.
Facets for issues that did not exist yet in the person's year are left empty.

Writes data/actors/<country>/<id>.json (type "person"). Safe to rerun.

Usage: python tools/build_people.py
"""
import json, os

from actorio import ROOT, load_all, save
from pcmodel import AXES, FACET_AXIS

PEOPLE = json.load(open(os.path.join(ROOT, "data", "people.json"), encoding="utf-8"))
AXIS_NAME = {a["id"]: a["name"] for a in AXES}
ERA = [("tec_ai", 2010), ("tec_big", 2005), ("cli_intl", 1990), ("cli_amb", 1985), ("cli_pay", 1985), ("tec_bio", 1975), ("int_eu", 1950), ("tec_nuc", 1945)]


def base_snapshot(actor, year):
    hand = [s for s in actor["snapshots"] if s["method"] == "hand"]
    exact = [s for s in hand if s["year"] == year]
    if exact:
        return exact[0]
    before = [s for s in hand if s["year"] <= year]
    return (before or hand)[-1]


def clamp(v):
    return max(-100, min(100, round(v)))


def main():
    actors = load_all()
    for p in PEOPLE["people"]:
        if p.get("base"):
            base_actor = actors[p["base"]]
            base = base_snapshot(base_actor, p["base_year"])
            src = base["facets"]
        else:
            # no party to start from: score each axis directly from the person's views
            base_actor, base = None, {"salience": p.get("salience", {a["id"]: 2 for a in AXES})}
            src = {fid: [p["scores"][ax], "l"] for fid, ax in FACET_AXIS.items()}
        facets = {}
        for fid, val in src.items():
            if val is None:
                facets[fid] = None
                continue
            score, conf = val
            ax = FACET_AXIS[fid]
            score += p.get("axes", {}).get(ax, 0)
            if fid in p.get("facets", {}):
                score = p["facets"][fid]
            changed = base_actor is None or ax in p.get("axes", {}) or fid in p.get("facets", {})
            facets[fid] = [clamp(score), "l" if changed else ("m" if conf == "h" else conf)]
        for fid, since in ERA:
            if p["year"] < since:
                facets[fid] = None
        notes = {}
        for a in AXES:
            ax = a["id"]
            if ax in p.get("notes", {}):
                notes[ax] = p["notes"][ax]
            elif base_actor is None:
                notes[ax] = f"Scored from {p['name']}'s stated views."
            else:
                notes[ax] = f"In line with the {base_actor['name']} profile ({base['label']})."
        actor = {
            "id": p["id"], "type": "person", "kind": p.get("kind", "politician"), "name": p["name"], "full_name": p["role"],
            "country": p["id"].split("-")[0].upper(), "active": p["active"], "party": p.get("party", p.get("base")),
            "predecessors": [], "status": "draft",
            "snapshots": [{
                "year": p["year"], "label": p["label"], "method": "hand",
                "basis": (f"Starts from the {base_actor['name']} profile ({base['label']}), adjusted where {p['name']}'s own stated views differ. Views only, not actions."
                          if base_actor else f"Scored directly from {p['name']}'s stated views, speeches and writing. Views only, not actions."),
                "salience": base["salience"], "facets": facets, "notes": notes,
                "sources": [{"title": f"Wikipedia: {p['name']}", "url": "https://en.wikipedia.org/wiki/" + p.get("wiki", p["name"]).replace(" ", "_")}],
            }],
        }
        save(actor)
    print(len(PEOPLE["people"]), "people written")


if __name__ == "__main__":
    main()
