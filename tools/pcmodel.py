"""Shared scoring logic: axis scores, type codes, current snapshots, centres."""
import json, os

from actorio import ROOT

MODEL = json.load(open(os.path.join(ROOT, "data", "model.json"), encoding="utf-8"))
AXES = MODEL["axes"]
AXIS_IDS = [a["id"] for a in AXES]
FACET_AXIS = {f["id"]: a["id"] for a in AXES for f in a["facets"]}
FACET_IDS = list(FACET_AXIS)
BAND = MODEL["scale"]["centre_band"]


def axis_scores(facets, proxies=None):
    """Mean of available facets per axis, falling back to a proxy.
    facets: {facet_id: [score, conf] | number | None}.
    Returns {axis: (score or None, n_facets, used_proxy)}."""
    proxies = proxies or {}
    out = {}
    for a in AXES:
        vals = []
        for f in a["facets"]:
            v = facets.get(f["id"])
            if v is None:
                continue
            vals.append(v[0] if isinstance(v, list) else v)
        if vals:
            out[a["id"]] = (sum(vals) / len(vals), len(vals), False)
        elif a["id"] in proxies:
            out[a["id"]] = (proxies[a["id"]], 0, True)
        else:
            out[a["id"]] = (None, 0, False)
    return out


def snapshot_axes(snap):
    return axis_scores(snap["facets"], snap.get("proxies"))


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
    """Latest hand-scored snapshot, else the latest snapshot."""
    hand = [s for s in actor["snapshots"] if s["method"] == "hand"]
    return (hand or actor["snapshots"])[-1]


def load_frames():
    frames = {}
    d = os.path.join(ROOT, "data", "countries")
    for name in sorted(os.listdir(d)):
        fr = json.load(open(os.path.join(d, name), encoding="utf-8"))
        frames[fr["code"]] = fr
    return frames


def centre(frame, actors):
    total = sum(frame["parties"].values())
    c = {ax: 0.0 for ax in AXIS_IDS}
    for pid, w in frame["parties"].items():
        sc = snapshot_axes(current(actors[pid]))
        for ax in AXIS_IDS:
            c[ax] += sc[ax][0] * w / total
    return c


# ---------- political types (4 dimensions bracketing the 8 axes) ----------

TYPES = json.load(open(os.path.join(ROOT, "data", "types.json"), encoding="utf-8"))
TYPE_BY_CODE = {t["code"]: t for t in TYPES["types"]}


def dimension_scores(axes):
    """axes: {axis: (score, ...)} or {axis: score}. Returns {dim_id: score or None}."""
    out = {}
    for d in TYPES["dimensions"]:
        vals = []
        for ax in d["axes"]:
            v = axes.get(ax)
            v = v[0] if isinstance(v, tuple) else v
            if v is not None:
                vals.append(v)
        out[d["id"]] = sum(vals) / len(vals) if vals else None
    return out


def _letter(d, v):
    if d["kind"] == "three":
        if v <= -d["band"]:
            return d["neg"]["letter"]
        if v >= d["band"]:
            return d["pos"]["letter"]
        return d["mid"]["letter"]
    return d["neg"]["letter"] if v < 0 else d["pos"]["letter"]


def political_type(axes, suffix=False):
    """Type code from the camp (economy x culture) and power, e.g. CPI.
    With suffix=True the future letter is added: CPI-e. None if data is missing."""
    dims = dimension_scores(axes)
    if any(v is None for v in dims.values()):
        return None
    code = "".join(_letter(d, dims[d["id"]]) for d in TYPES["dimensions"] if d["kind"] != "suffix")
    if suffix:
        fut = [d for d in TYPES["dimensions"] if d["kind"] == "suffix"][0]
        code += "-" + _letter(fut, dims[fut["id"]])
    return code
