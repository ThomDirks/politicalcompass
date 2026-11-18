"""Simulate respondents to see how the types fill up and how the
consistency score behaves. This tests the design against assumptions,
not against real people.

Respondent mix:
  party-like  start from a random current party's profile, plus personal noise
  mixed       each axis drawn independently (cross-pressured views)
  careless    random answers, or the same answer to everything

Usage: python tools/simulate.py [n]
"""
import json, os, random, sys
from collections import Counter

from actorio import ROOT, load_all
from pcmodel import AXES, FACET_AXIS, FACET_IDS, TYPE_BY_CODE, axis_scores, current, load_frames, alignments
from score import local_for, score_answers, items_for
ITEMS = items_for(quick=False)

Q = json.load(open(os.path.join(ROOT, "data", "questions.json"), encoding="utf-8"))
CHECKS = Q["checks"]
rng = random.Random(7)
actors, frames = load_all(), load_frames()
current_parties = [actors[pid] for fr in frames.values() for pid in fr["parties"]]


def clamp(v, lo=-3, hi=3):
    return max(lo, min(hi, v))


def latent(kind):
    if kind == "party":
        p = rng.choice(current_parties)
        base = current(p)["facets"]
        return p["country"], {f: max(-100, min(100, base[f][0] + rng.gauss(0, 30))) for f in FACET_IDS}
    cc = rng.choice(list(frames))
    axis_pos = {a["id"]: rng.uniform(-70, 70) for a in AXES}
    return cc, {f: max(-100, min(100, axis_pos[FACET_AXIS[f]] + rng.gauss(0, 20))) for f in FACET_IDS}


def respond(kind):
    answers = {}
    if kind == "careless":
        mode = rng.choice(["random", "flat"])
        flat = rng.choice([0, 1, 2])
        cc = rng.choice(list(frames))
        for it in ITEMS + CHECKS:
            answers[it["id"]] = flat if mode == "flat" else rng.randint(-3, 3)
        return cc, answers
    cc, pos = latent(kind)
    for it in ITEMS:
        key = local_for(it, cc)[1]
        v = pos[it["facet"]] / 100 * 3 * key * 0.8  # people answer a little more cautiously than they think
        answers[it["id"]] = clamp(round(v + rng.gauss(0, 0.8)))
    for c in CHECKS:
        a = answers[c["pair"]]
        answers[c["id"]] = clamp(round((a if c["same"] else -a) + rng.gauss(0, 0.7)))
    return cc, answers


def consistency(answers, cc):
    pairs = []
    for c in CHECKS:
        a, b = answers.get(c["pair"]), answers.get(c["id"])
        if a is None or b is None:
            continue
        exp = a if c["same"] else -a
        pairs.append(1 - max(0, abs(b - exp) - 1) / 5)
    by = {}
    for it in ITEMS:
        v = answers.get(it["id"])
        if v is not None:
            by.setdefault(it["facet"], []).append(v * local_for(it, cc)[1])
    fac = [1 - max(0, (max(v) - min(v)) - 2) / 4 for v in by.values() if len(v) > 1]
    vals = list(answers.values())
    same = Counter(vals).most_common(1)[0][1] / len(vals)
    mean = lambda x: sum(x) / len(x) if x else 1
    score = 100 * (0.5 * mean(pairs) + 0.5 * mean(fac))
    if same > 0.7:
        score *= 0.6
    return round(max(0, min(100, score)))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    kinds = ["party"] * 6 + ["mixed"] * 3 + ["careless"]
    types, cons, align = Counter(), {"party": [], "mixed": [], "careless": []}, []
    for _ in range(n):
        kind = rng.choice(kinds)
        cc, ans = respond(kind)
        facets = score_answers(ans, cc)
        axes = {a: s for a, (s, _, _) in axis_scores({f: v for f, v in facets.items()}).items()}
        al = alignments(axes)
        if kind != "careless":
            types[al[0][0]] += 1
            align.append(al[0][1])
        cons[kind].append(consistency(ans, cc))
    tot = sum(types.values())
    print(f"Type spread over {tot} non-careless respondents:")
    for t in TYPE_BY_CODE:
        share = types[t] / tot * 100
        print(f"  {t} {TYPE_BY_CODE[t]['name']:<17} {share:5.1f}%  {'#' * round(share)}")
    align.sort()
    print(f"\nAlignment with closest type: median {align[len(align)//2]:.0f}%, lowest 10% below {align[len(align)//10]:.0f}%")
    print("\nConsistency score (full test):")
    for k, v in cons.items():
        v.sort()
        low = sum(x < 70 for x in v) / len(v) * 100
        print(f"  {k:<9} median {v[len(v)//2]:3d}   flagged low: {low:4.1f}%")


if __name__ == "__main__":
    main()
