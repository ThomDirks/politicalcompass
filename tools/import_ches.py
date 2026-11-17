"""Import Chapel Hill Expert Survey waves (1999-2024) as snapshots.

Downloads the CHES trend file (cached in .cache/), maps CHES items to PCompass
facets using data/ches_mapping.json and writes a 'ches' snapshot per party and
wave into data/actors. Existing 'ches' snapshots are replaced; hand-scored
snapshots are never touched. Safe to run repeatedly.

Usage: python tools/import_ches.py
"""
import csv, io, json, os, urllib.request

from actorio import ROOT, load_all, save

mapping = json.load(open(os.path.join(ROOT, "data", "ches_mapping.json"), encoding="utf-8"))
model = json.load(open(os.path.join(ROOT, "data", "model.json"), encoding="utf-8"))
FACET_IDS = [f["id"] for a in model["axes"] for f in a["facets"]]
URL = mapping["source"]["url"]
CACHE = os.path.join(ROOT, ".cache", os.path.basename(URL))


def fetch():
    if not os.path.exists(CACHE):
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        print("downloading", URL)
        urllib.request.urlretrieve(URL, CACHE)
    with open(CACHE, encoding="latin-1") as f:
        return list(csv.DictReader(f))


def num(row, var):
    v = (row.get(var) or "").strip()
    if v in ("", "."):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def tf(x, kind):
    if kind == "t10":
        return (x - 5) * 20
    if kind == "eu7":
        return (4 - x) / 3 * 100
    raise ValueError(kind)


def clamp(x):
    return max(-100, min(100, round(x)))


def snapshot(row):
    facets, raw = {}, {}
    for fid in FACET_IDS:
        spec = mapping["facets"].get(fid)
        if not spec:
            facets[fid] = None
            continue
        vals = []
        for var in spec["vars"]:
            x = num(row, var)
            if x is not None:
                raw[var] = round(x, 2)
                vals.append(tf(x, spec["t"]))
                if spec.get("combine") == "first":
                    break
        facets[fid] = [clamp(sum(vals) / len(vals)), "h"] if vals else None
    proxies = {}
    for ax, spec in mapping["proxies"].items():
        x = num(row, spec["var"])
        if x is not None:
            raw[spec["var"]] = round(x, 2)
            proxies[ax] = clamp(tf(x, spec["t"]))
    year = int(row["year"])
    return {
        "year": year,
        "label": f"CHES {year}" + (f" (as {row['party']})" if row.get("_rename") else ""),
        "method": "ches",
        "basis": f"Chapel Hill Expert Survey {year}, expert means. Facets without a matching CHES item are null.",
        "facets": facets,
        "proxies": proxies,
        "ches": {"party_id": row["party_id"], "party": row["party"], "items": raw},
        "sources": [{"title": mapping["source"]["title"], "url": mapping["source"]["homepage"]}],
    }


def main():
    rows = fetch()
    actors = load_all()
    touched = set()
    for a in actors.values():
        before = len(a["snapshots"])
        a["snapshots"] = [s for s in a["snapshots"] if s["method"] != "ches"]
        if len(a["snapshots"]) != before:
            touched.add(a["id"])

    added = 0
    for m in mapping["parties"]:
        aid = m["actor"]
        if aid not in actors:
            new = m.get("new")
            if not new:
                print("skip, unknown actor without 'new' block:", aid)
                continue
            actors[aid] = {
                "id": aid, "type": "party", "name": new["name"], "full_name": new["full_name"],
                "country": aid.split("-")[0].upper(), "active": new["active"],
                "predecessors": [], "successors": [new["successor"]] if new.get("successor") else [],
                "status": "ches-only", "snapshots": [],
            }
        actor = actors[aid]
        for row in rows:
            if row["country"] != m["c"] or row["party_id"] != m["p"]:
                continue
            if "years" in m and row["year"] not in m["years"]:
                continue
            if row["party"].lower() not in (actor["name"].lower(), "") and aid in ("de-linke", "uk-reform"):
                row["_rename"] = True
            actor["snapshots"].append(snapshot(row))
            touched.add(aid)
            added += 1

    for aid in sorted(touched):
        save(actors[aid])
    print(f"{added} CHES snapshots written across {len(touched)} actors")


if __name__ == "__main__":
    main()
