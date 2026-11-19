"""Validate PCompass data and generate reports.

Usage:
  python tools/validate.py            check data, print the current overview
  python tools/validate.py --report   also write docs/party-overview.md,
                                      docs/drift.md and docs/calibration.md
"""
import json, os, sys

from actorio import ROOT, load_all

from pcmodel import MODEL as model, AXES, AXIS_IDS, FACET_AXIS, FACET_IDS, BAND, snapshot_axes as axis_scores, type_code, current
import pcmodel

LO, HI = model["scale"]["min"], model["scale"]["max"]
CURRENT_FROM = 2015  # hand snapshots from this year on must score every facet
errors = []


def err(msg):
    errors.append(msg)


# ---------- checks ----------

actors = load_all()
for aid, a in actors.items():
    for key in ("id", "type", "name", "full_name", "country", "active", "status", "snapshots"):
        if key not in a:
            err(f"{aid}: missing '{key}'")
    if a.get("type") not in ("party", "person"):
        err(f"{aid}: type must be party or person")
    if a.get("type") == "person":
        if a.get("kind") not in ("politician", "public figure"):
            err(f"{aid}: kind must be politician or public figure")
        if a.get("party") and actors.get(a["party"], {}).get("type") != "party":
            err(f"{aid}: unknown party {a['party']}")
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

questions = json.load(open(os.path.join(ROOT, "data/questions.json"), encoding="utf-8"))
ids = set()
per_facet = {f: [] for f in FACET_IDS}
for item in questions["items"]:
    if item["id"] in ids:
        err(f"questions: duplicate id {item['id']}")
    ids.add(item["id"])
    if item["facet"] not in per_facet:
        err(f"questions: {item['id']} has unknown facet")
        continue
    if item["key"] not in (1, -1):
        err(f"questions: {item['id']} key must be 1 or -1")
    for cc in item.get("local", {}):
        if cc not in frames:
            err(f"questions: {item['id']} has a variant for unknown country {cc}")
    per_facet[item["facet"]].append(item)
for f, items in per_facet.items():
    if sum(i.get("full", True) for i in items) < 3:
        err(f"questions: facet {f} has fewer than 3 items in the full test")
    if sum(i["quick"] for i in items) != 1:
        err(f"questions: facet {f} needs exactly one quick-mode item")
    if not any(i.get("kind") == "concept" for i in items):
        err(f"questions: facet {f} has no concept statement")
    for i in items:
        if i.get("kind") not in ("concept", "policy"):
            err(f"questions: {i['id']} needs kind concept or policy")
        if i["quick"] and (i.get("kind") != "concept" or i.get("local")):
            err(f"questions: quick item {i['id']} must be a concept statement without country versions")
def eff_key(item, cc):
    loc = item.get("local", {}).get(cc)
    return loc["key"] if isinstance(loc, dict) else item["key"]


for cc in [None] + list(frames):
    for ax in AXIS_IDS:
        for mode, sel in (("full", lambda i: i.get("full", True)), ("quick", lambda i: i["quick"])):
            keys = [eff_key(i, cc) for f, items in per_facet.items() if FACET_AXIS[f] == ax for i in items if sel(i)]
            if sum(keys) != 0:
                err(f"questions: axis {ax} is unbalanced in {mode} mode for {cc or 'the general version'} ({keys.count(1)} towards + vs {keys.count(-1)} towards -)")
for c in questions.get("checks", []):
    pair = next((i for i in questions["items"] if i["id"] == c["pair"]), None)
    if not pair or not pair.get("full", True):
        err(f"questions: check {c['id']} must pair with a statement in the full test")
if {s["axis"] for s in questions["salience"]["items"]} != set(AXIS_IDS):
    err("questions: salience items must cover every axis")

T = pcmodel.TYPES
core = [d for d in T["dimensions"] if d["kind"] != "suffix"]
opts = [[d[k]["letter"] for k in ("neg", "mid", "pos") if k in d] for d in core]
expected = {""}
for o in opts:
    expected = {e + l for e in expected for l in o}
if set(pcmodel.TYPE_BY_CODE) != expected:
    err(f"types: type codes don't match the dimension letters ({len(expected)} expected)")
camps = {c["id"] for c in T["camps"]}
for t in T["types"]:
    if t["code"][:2] not in camps:
        err(f"types: {t['code']} has no camp")
    for c in t["clash"]:
        if c not in pcmodel.TYPE_BY_CODE:
            err(f"types: {t['code']} clashes with unknown type {c}")
for d in T["dimensions"]:
    for ax in d["axes"]:
        if ax not in AXIS_IDS:
            err(f"types: dimension {d['id']} uses unknown axis {ax}")

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
    return {ax: (v, 4, False) for ax, v in pcmodel.centre(fr, actors).items()}


HEAD = "| Party | Type | " + " | ".join(AXIS_IDS) + " |\n|---|---|" + "---:|" * len(AXIS_IDS)


def ptype(sc):
    code = pcmodel.political_type(sc, suffix=True)
    return f"{code} {pcmodel.TYPE_BY_CODE[code[:3]]['name']}" if code else "?"

ov = []
for code, fr in frames.items():
    ov.append(f"\n## {fr['name']}\n\n{HEAD}")
    for pid in sorted(fr["parties"], key=lambda p: -fr["parties"][p]):
        sc = axis_scores(current(actors[pid]))
        ov.append(f"| {actors[pid]['name']} | {ptype(sc)} | " + " | ".join(fmt(sc[ax]) for ax in AXIS_IDS) + " |")
    cen = centre(fr)
    ov.append(f"| *Centre* | {ptype(cen)} | " + " | ".join(f"*{fmt(cen[ax])}*" for ax in AXIS_IDS) + " |")
    ov.append(f"\nCentre weights: {fr['weight_basis']}")
former = [a for a in actors.values() if a["type"] == "party" and all(a["id"] not in fr["parties"] for fr in frames.values())]
ov.append(f"\n## Former and minor parties\n\n{HEAD}")
for a in sorted(former, key=lambda a: (a["country"], (a["active"].get("from") or 0))):
    snap = current(a)
    sc = axis_scores(snap)
    yrs = f"{a['active'].get('from') or '?'}–{a['active'].get('to') or ''}"
    ov.append(f"| {a['name']} ({a['country']}, {yrs}) | {ptype(sc)} | " + " | ".join(fmt(sc[ax]) for ax in AXIS_IDS) + " |")
overview = "\n".join(ov)

pe = ["| Person | Role | Year | Type | Next closest | " + " | ".join(AXIS_IDS) + " |", "|---|---|---:|---|---|" + "---:|" * len(AXIS_IDS)]
people = [a for a in actors.values() if a["type"] == "person"]
by_type = {}
for a in sorted(people, key=lambda a: (a["country"], a["name"])):
    snap = current(a)
    sc = axis_scores(snap)
    al = pcmodel.alignments(sc)
    by_type.setdefault(al[0][0], []).append(a["name"])
    nxt = pcmodel.TYPE_BY_CODE[al[1][0]]["name"]
    pe.append(f"| {a['name']} ({a['country']}) | {a['full_name']} | {snap['year']} | {ptype(sc)} ({al[0][1]:.0f}%) | {nxt} | " + " | ".join(fmt(sc[ax]) for ax in AXIS_IDS) + " |")
for code in pcmodel.TYPE_BY_CODE:
    if len(by_type.get(code, [])) < 5:
        err(f"people: type {code} has {len(by_type.get(code, []))} people, need at least 5")
pe_types = ["| Type | People |", "|---|---|"] + [f"| {code} {t['name']} | {len(by_type.get(code, []))}: {', '.join(by_type.get(code, []))} |" for code, t in pcmodel.TYPE_BY_CODE.items()]
people_md = "\n".join(pe_types) + "\n\n" + "\n".join(pe)
if errors:
    print("\n".join(errors))
    sys.exit(1)

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
print(f"OK: {len(actors) - len(people)} parties, {len(people)} people, {n_snap} snapshots, {len(frames)} country frames")
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
    ql = ["# Question list\n", gen.strip() + "\n", "Agreeing with a **+** statement moves you towards the + pole of the axis, a **−** statement towards the − pole. "
          "**Q** marks the statement used in quick mode (always a concept statement). Concept statements are about principles; policy statements are about current debates and will be rotated over time. Reserve statements are in the bank but not asked. Country versions replace the general text when that country is selected."]
    for a in AXES:
        ql.append(f"\n## {a['name']} ({a['neg']['label']} − / {a['pos']['label']} +)")
        for fct in a["facets"]:
            ql.append(f"\n**{fct['name']}**\n")
            for i in per_facet[fct["id"]]:
                tags = ("Q " if i["quick"] else "") + ("concept" if i.get("kind") == "concept" else "policy") + ("" if i.get("full", True) else ", reserve")
                ql.append(f"- `{i['id']}` {'+' if i['key'] > 0 else '−'} ({tags}): {i['text']}")
                for cc, t in i.get("local", {}).items():
                    if isinstance(t, dict):
                        ql.append(f"  - {cc} ({'+' if t['key'] > 0 else '−'}): {t['text']}")
                    else:
                        ql.append(f"  - {cc}: {t}")
    ql.append("\n## Consistency checks (full test only, not scored)\n")
    ql.append("Each check restates an earlier statement. **Same** means a consistent answer matches it, **mirror** means a consistent answer is its opposite.\n")
    for c in questions.get("checks", []):
        ql.append(f"- `{c['id']}` ({'same as' if c['same'] else 'mirror of'} `{c['pair']}`): {c['text']}")
    with open(os.path.join(ROOT, "docs/question-list.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(ql) + "\n")
    with open(os.path.join(ROOT, "docs/people.md"), "w", encoding="utf-8") as f:
        f.write("# People\n\n" + gen +
                "Politicians and public figures, scored on their stated views (speeches, writing, programmes they stood on), not on what they did in office. "
                "Most start from their party's profile in their era and are adjusted where their own views differ; people without a party are scored directly. "
                "See `data/people.json` for the adjustments and `data/actors/` for the result. Every type needs at least five people.\n\n" + people_md + "\n")
    print("\nwrote docs/party-overview.md, docs/people.md, docs/drift.md, docs/calibration.md, docs/question-list.md")
