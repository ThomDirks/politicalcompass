"""Calibrate current hand-scored snapshots against CHES 2024.

Rule: where a hand score and the CHES 2024 score for the same facet differ by
GAP or more, the hand score becomes the average of the two and its confidence
drops to 'm'. Exceptions with a documented reason keep the hand score. Each
change is recorded in the snapshot under "calibration", and a snapshot that
already has a calibration record is skipped, so the script is safe to rerun.

Parties without their own CHES row can be compared with the mean of their
predecessors (PRO = PvdA + GroenLinks).

Usage: python tools/calibrate_ches.py
"""
from actorio import load_all, save

GAP = 35
YEAR = 2024
PROXY_PARENTS = {"nl-pro": ["nl-pvda", "nl-gl"]}
KEEP = {
    ("nl-pvv", "dem_direct"): "Binding referendum is in the PVV programme.",
    ("nl-sp", "dem_direct"): "Binding referendum is a long-standing SP programme point.",
    ("nl-fvd", "dem_direct"): "Binding referendums are FvD's founding issue.",
    ("uk-reform", "eco_lab"): "Reform's 2026 pledge to repeal Labour's worker protections postdates CHES 2024.",
    ("uk-reform", "eco_tax"): "Reform's 2026 shift under Jenrick (restore two-child cap) postdates CHES 2024.",
}


def ches_facets(actors, aid):
    def get(a):
        s = [s for s in a["snapshots"] if s["method"] == "ches" and s["year"] == YEAR]
        return s[0]["facets"] if s else None
    if aid in PROXY_PARENTS:
        parts = [get(actors[p]) for p in PROXY_PARENTS[aid]]
        if not all(parts):
            return None, None
        out = {}
        for fid in parts[0]:
            vals = [p[fid][0] for p in parts if p.get(fid)]
            out[fid] = [round(sum(vals) / len(vals)), "h"] if len(vals) == len(parts) else None
        return out, " + ".join(PROXY_PARENTS[aid])
    f = get(actors[aid])
    return f, "own"


def main():
    actors = load_all()
    changed = 0
    for aid, a in sorted(actors.items()):
        hand = [s for s in a["snapshots"] if s["method"] == "hand" and s["year"] >= 2025]
        if not hand or "calibration" in hand[-1]:
            continue
        ches, basis = ches_facets(actors, aid)
        if not ches:
            continue
        snap = hand[-1]
        record = {"against": f"CHES {YEAR} ({basis})", "rule": f"average where gap >= {GAP}", "adjusted": {}, "kept": {}}
        for fid, cv in ches.items():
            hv = snap["facets"].get(fid)
            if not cv or not hv or abs(hv[0] - cv[0]) < GAP:
                continue
            if (aid, fid) in KEEP:
                record["kept"][fid] = {"hand": hv[0], "ches": cv[0], "reason": KEEP[(aid, fid)]}
                continue
            new = round((hv[0] + cv[0]) / 2)
            record["adjusted"][fid] = {"hand": hv[0], "ches": cv[0], "new": new}
            snap["facets"][fid] = [new, "m"]
            changed += 1
        snap["calibration"] = record
        save(a)
    print(f"{changed} facet scores adjusted")


if __name__ == "__main__":
    main()
