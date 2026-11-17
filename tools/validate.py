"""Validate PCompass data and generate reports.

Usage:
  python tools/validate.py            check data, print the current overview
  python tools/validate.py --report   also write docs/party-overview.md,
                                      docs/drift.md and docs/calibration.md
"""
import json, os, sys

from actorio import ROOT, load_all

model = json.load(open(os.path.join(ROOT, "data/model.json"), encoding="utf-8"))
AXES = model["axes"]
AXIS_IDS = [a["id"] for a in AXES]
FACET_AXIS = {f["id"]: a["id"] for a in AXES for f in a["facets"]}
FACET_IDS = list(FACET_AXIS)
LO, HI = model["scale"]["min"], model["scale"]["max"]
BAND = model["scale"]["centre_band"]
CURRENT_FROM = 2015  # hand snapshots from this year on must score every facet
errors = []


def err(msg):
    errors.append(msg)


# ---------- scoring ----------

def axis_scores(snap):
    """Axis score = mean of available facets. Falls back to a CHES proxy.
    Returns {axis: (score or None, n_facets, used_proxy)}."""
    out = {}
    for a in AXES:
        vals = [snap["facets"][f["id"]][0] for f in a["facets"] if snap["facets"].get(f["id"])]
        if vals:
            out[a["id"]] = (sum(vals) / len(vals), len(vals), False)
        elif a["id"] in snap.get("proxies", {}):
            out[a["id"]] = (snap["proxies"][a["id"]], 0, True)
        else:
            out[a["id"]] = (None, 0, False)
    return out


def type_code(scores):
    letters = []
    for a in AXES:
        s = scores[a["id"]][0]
        if s is None:
            letters.append("?")
        else:
            letters.append("x" if abs(s) < BAND else (a["neg"]["letter"] if s < 0 else a["pos"]["letter"]))
    return "".join(letters[:4]) + "-" + "".join(letters[4:])


def current(actor):
    """Latest hand-scored snapshot, else latest snapshot."""
    hand = [s for s in actor["snapshots"] if s["method"] == "hand"]
    return (hand or actor["snapshots"])[-1]


# ---------- checks ----------

actors = load_all()
for aid, a in actors.items():
    for key in ("id", "type", "name", "full_name", "country", "active", "status", "snapshots"):
        if key not in a:
            err(f"{aid}: missing '{key}'")
    if not a.get("snapshots"):
        err(f"{aid}: no snapshots")
        continue
    for ref in a.get("predecessors", []) + a.get("successors", []):
        if ref not in actors:
            err(f"{aid}: unknown linked actor {ref}")
    for s in a["snapshots"]:
        tag = f"{aid} {s.get('year')} {s.get('method')}"
        if set(s.get("facets", {})) != set(FACET_IDS):
            err(f"{tag}: facet keys differ from model")
            continue
        for fid, val in s["facets"].items():
            if val is None:
                if s["method"] == "hand" and s["year"] >= CURRENT_FROM:
                    err(f"{tag}: {fid} is null in a current hand snapshot")
                continue
            if not (isinstance(val, list) and len(val) == 2 and LO <= val[0] <= HI and val[1] in model["confidence"]):
                err(f"{tag}: bad value for {fid}: {val}")
        if s["method"] == "hand":
            for ax in AXIS_IDS:
                if not 1 <= s.get("salience", {}).get(ax, 0) <= 5:
                    err(f"{tag}: salience {ax} missing or out of 1..5")
                if not s.get("notes", {}).get(ax):
                    err(f"{tag}: note {ax} missing")
        elif s["method"] != "ches":
            err(f"{tag}: unknown method")

frames = {}
for path in sorted(os.listdir(os.path.join(ROOT, "data/countries"))):
    fr = json.load(open(os.path.join(ROOT, "data/countries", path), encoding="utf-8"))
    for pid in fr["parties"]:
        if pid not in actors:
            err(f"countries/{path}: unknown party {pid}")
    frames[fr["code"]] = fr

if errors:
    print("\n".join(errors))
    sys.exit(1)


# ---------- reports ----------

def fmt(cell):
    s, n, proxy = cell
    if s is None:
        return "·"
    mark = "ᵖ" if proxy else ("~" if n < 2 else "")
    return f"{s:+.0f}{mark}"


def centre(fr):
    total = sum(fr["parties"].values())
    c = {ax: 0.0 for ax in AXIS_IDS}
    for pid, w in fr["parties"].items():
        sc = axis_scores(current(actors[pid]))
        for ax in AXIS_IDS:
            c[ax] += sc[ax][0] * w / total
    return {ax: (v, 4, False) for ax, v in c.items()}


HEAD = "| Party | Code | " + " | ".join(AXIS_IDS) + " |\n|---|---|" + "---:|" * len(AXIS_IDS)

ov = []
for code, fr in frames.items():
    ov.append(f"\n## {fr['name']}\n\n{HEAD}")
    for pid in sorted(fr["parties"], key=lambda p: -fr["parties"][p]):
        sc = axis_scores(current(actors[pid]))
        ov.append(f"| {actors[pid]['name']} | `{type_code(sc)}` | " + " | ".join(fmt(sc[ax]) for ax in AXIS_IDS) + " |")
    cen = centre(fr)
    ov.append(f"| *Centre* | `{type_code(cen)}` | " + " | ".join(f"*{fmt(cen[ax])}*" for ax in AXIS_IDS) + " |")
    ov.append(f"\nCentre weights: {fr['weight_basis']}")
former = [a for a in actors.values() if all(a["id"] not in fr["parties"] for fr in frames.values())]
ov.append(f"\n## Former and minor parties\n\n{HEAD}")
for a in sorted(former, key=lambda a: (a["country"], (a["active"].get("from") or 0))):
    snap = current(a)
    sc = axis_scores(snap)
    yrs = f"{a['active'].get('from') or '?'}–{a['active'].get('to') or ''}"
    ov.append(f"| {a['name']} ({a['country']}, {yrs}) | `{type_code(sc)}` | " + " | ".join(fmt(sc[ax]) for ax in AXIS_IDS) + " |")
overview = "\n".join(ov)

dr = []
for a in sorted(actors.values(), key=lambda a: (a["country"], a["name"])):
    if len(a["snapshots"]) < 2:
        continue
    dr.append(f"\n### {a['name']} ({a['country']})\n\n| Year | Source | " + " | ".join(AXIS_IDS) + " |\n|---|---|" + "---:|" * len(AXIS_IDS))
    for s in a["snapshots"]:
        sc = axis_scores(s)
        src = "hand" if s["method"] == "hand" else "CHES"
        dr.append(f"| {s['year']} | {src}: {s['label']} | " + " | ".join(fmt(sc[ax]) for ax in AXIS_IDS) + " |")
drift = "\n".join(dr)

cal_rows, cal_detail = [], []
for a in sorted(actors.values(), key=lambda a: (a["country"], a["name"])):
    hand = [s for s in a["snapshots"] if s["method"] == "hand" and s["year"] >= 2025]
    ches = [s for s in a["snapshots"] if s["method"] == "ches" and s["year"] == 2024]
    if not hand or not ches:
        continue
    h, c = hand[-1], ches[-1]
    diffs = {f: h["facets"][f][0] - c["facets"][f][0] for f in FACET_IDS if h["facets"].get(f) and c["facets"].get(f)}
    mad = sum(abs(d) for d in diffs.values()) / len(diffs)
    big = sorted(((f, d) for f, d in diffs.items() if abs(d) >= 35), key=lambda x: -abs(x[1]))
    cal_rows.append((a, mad, len(diffs), big))
cal = ["| Party | Facets compared | Mean abs. difference | Largest gaps (hand minus CHES) |", "|---|---:|---:|---|"]
for a, mad, n, big in cal_rows:
    gaps = ", ".join(f"{f} {d:+d}" for f, d in big[:5]) or "none ≥ 35"
    cal.append(f"| {a['name']} ({a['country']}) | {n} | {mad:.0f} | {gaps} |")
calibration = "\n".join(cal)

n_snap = sum(len(a["snapshots"]) for a in actors.values())
print(f"OK: {len(actors)} actors, {n_snap} snapshots, {len(frames)} country frames")
print(overview)

if "--report" in sys.argv:
    legend = " · ".join(f"{a['id']} {a['neg']['letter']}/{a['pos']['letter']} = {a['neg']['label']}/{a['pos']['label']}" for a in AXES)
    marks = (f"Letters: {legend}. **x** = within ±{BAND} of zero, **?** = no data.\n\n"
             "Marks: **~** = axis based on a single facet, **ᵖ** = CHES proxy (overall left/right or GAL-TAN) "
             "because no facet items exist for that year, **·** = no data.\n")
    gen = "Generated by `tools/validate.py --report`. Do not edit by hand.\n\n"
    with open(os.path.join(ROOT, "docs/party-overview.md"), "w", encoding="utf-8") as f:
        f.write("# Party overview\n\n" + gen +
                "Current profile per party: the latest hand-scored snapshot, or the latest CHES snapshot for parties "
                "without one. Axis scores are the mean of the available facets. All hand scores are drafts.\n\n"
                + marks + overview + "\n")
    with open(os.path.join(ROOT, "docs/drift.md"), "w", encoding="utf-8") as f:
        f.write("# Drift over time\n\n" + gen +
                "Every snapshot of every party with more than one. CHES rows cover only the facets CHES asks about "
                "(see `data/ches_mapping.json`), so compare CHES rows with CHES rows first. 1999 and 2002 only have "
                "proxies for Economy and Social values. Hand rows score every facet. Scales are absolute: a party "
                "from 1936 is measured against today's anchors, not against its own time.\n\n" + marks + drift + "\n")
    with open(os.path.join(ROOT, "docs/calibration.md"), "w", encoding="utf-8") as f:
        f.write("# Calibration: hand scores vs CHES 2024\n\n" + gen +
                "Compares the current hand-scored snapshot with the CHES 2024 snapshot on facets both cover. "
                "Gaps can be real change since 2024 (new leaders, new coalitions) or scoring error.\n\n" + calibration + "\n")
    print("\nwrote docs/party-overview.md, docs/drift.md, docs/calibration.md")
