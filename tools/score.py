"""Score a set of answers and match them against parties.

Answers file (JSON):
  {
    "country": "NL",
    "answers":  { "eco_own_1": 2, "eco_own_2": -1, "...": null },   # -3..3, null = no opinion
    "salience": { "ECO": 3, "MIG": 1, "...": 2 }                    # 0..4, optional
  }

Usage:
  python tools/score.py answers.json
  python tools/score.py --simulate nl-vvd [--quick]   answer as a party would
  python tools/score.py --selftest [--quick] [--noise 1]
      every party's simulated supporter should match that party; --noise adds
      random answer noise (50 trials per party) to test how well parties separate
"""
import json, os, sys

from actorio import ROOT, load_all
from pcmodel import AXES, AXIS_IDS, FACET_AXIS, FACET_IDS, axis_scores, type_code, current, load_frames, centre

QUESTIONS = json.load(open(os.path.join(ROOT, "data", "questions.json"), encoding="utf-8"))
ITEMS = QUESTIONS["items"]
DEFAULT_SALIENCE = 2
MIN_COVERAGE = 0.5  # share of the user's weighted facets a party must cover to be ranked


def items_for(quick=False):
    return [i for i in ITEMS if i["quick"] or not quick]


def text_for(item, country=None):
    return item.get("local", {}).get(country, item["text"])


def score_answers(answers):
    """Facet score = mean of (answer x key) / 3 x 100 over answered items."""
    sums = {f: [] for f in FACET_IDS}
    for item in ITEMS:
        v = answers.get(item["id"])
        if v is None:
            continue
        sums[item["facet"]].append(v * item["key"])
    return {f: (round(sum(v) / len(v) / 3 * 100) if v else None) for f, v in sums.items()}


def similarity(user_facets, salience, actor_facets):
    """Salience-weighted similarity, 0..100. None if the party covers too little."""
    num = den = full = 0.0
    for f in FACET_IDS:
        u = user_facets.get(f)
        if u is None:
            continue
        w = salience.get(FACET_AXIS[f], DEFAULT_SALIENCE)
        full += w
        p = actor_facets.get(f)
        if p is None or w == 0:
            continue
        num += w * abs(u - p[0])
        den += w
    if den == 0 or den / full < MIN_COVERAGE:
        return None
    return 100 - (num / den) / 2


def match(user_facets, salience, actors, frames, country=None):
    rows = []
    for a in actors.values():
        if country and a["country"] != country:
            continue
        snap = current(a)
        sim = similarity(user_facets, salience, snap["facets"])
        if sim is None:
            continue
        in_frame = any(a["id"] in fr["parties"] for fr in frames.values())
        rows.append((sim, a, snap, in_frame))
    rows.sort(key=lambda r: -r[0])
    return rows


def relative(user_axes, frame, actors):
    c = centre(frame, actors)
    out = {}
    for a in AXES:
        u = user_axes[a["id"]][0]
        if u is None:
            continue
        d = u - c[a["id"]]
        if abs(d) < 10:
            out[a["id"]] = "around the centre"
        else:
            pole = a["neg"]["label"] if d < 0 else a["pos"]["label"]
            out[a["id"]] = f"{'strongly ' if abs(d) >= 30 else ''}towards {pole} ({d:+.0f} from the centre)"
    return out


def simulate(actor, quick=False, noise=0, rng=None):
    """Answer every item the way a supporter would. noise=n adds a random
    -n..n to each answer and skips about one in ten items."""
    facets = current(actor)["facets"]
    answers = {}
    for item in items_for(quick):
        p = facets.get(item["facet"])
        if p is None:
            answers[item["id"]] = None
            continue
        v = round(p[0] / 100 * 3 * item["key"])
        if noise:
            if rng.random() < 0.1:
                answers[item["id"]] = None
                continue
            v += rng.randint(-noise, noise)
        answers[item["id"]] = max(-3, min(3, v))
    salience = current(actor).get("salience", {})
    return answers, {ax: min(4, max(0, s - 1)) for ax, s in salience.items()}


def report(answers, salience, country, actors, frames, top=5):
    facets = score_answers(answers)
    axes = axis_scores(facets)
    print("Type code:", type_code(axes))
    print("Axes:", "  ".join(f"{ax} {axes[ax][0]:+.0f}" if axes[ax][0] is not None else f"{ax} ·" for ax in AXIS_IDS))
    if country in frames:
        rel = relative(axes, frames[country], actors)
        print(f"Compared with {frames[country]['name']}:")
        for ax, txt in rel.items():
            print(f"  {ax}: {txt}")
    rows = match(facets, salience, actors, frames, country)
    print("Closest current parties:")
    for sim, a, snap, in_frame in [r for r in rows if r[3]][:top]:
        print(f"  {sim:5.1f}  {a['name']} ({a['country']})")
    print("Closest historical or minor parties:")
    for sim, a, snap, in_frame in [r for r in rows if not r[3]][:3]:
        print(f"  {sim:5.1f}  {a['name']} ({a['country']}, {snap['label']})")


def selftest(actors, frames, quick, noise=0, trials=1):
    import random
    from collections import Counter
    rng = random.Random(42)
    tot1 = tot3 = n = 0
    for code, fr in frames.items():
        for pid in fr["parties"]:
            first = top3 = 0
            confused = Counter()
            for _ in range(trials):
                answers, sal = simulate(actors[pid], quick, noise, rng)
                rows = [r for r in match(score_answers(answers), sal, actors, frames, code) if r[3]]
                ids = [r[1]["id"] for r in rows]
                first += ids[0] == pid
                top3 += pid in ids[:3]
                if ids[0] != pid:
                    confused[actors[ids[0]]["name"]] += 1
            tot1 += first; tot3 += top3; n += trials
            mix = ", ".join(f"{k} {v}" for k, v in confused.most_common(2))
            print(f"{code} {actors[pid]['name']:<16} first {first/trials:4.0%}  top-3 {top3/trials:4.0%}" + (f"   confused with: {mix}" if mix else ""))
    mode = "quick" if quick else "deep"
    print(f"\n{mode} mode, noise {noise}: own party first {tot1/n:.0%}, in top 3 {tot3/n:.0%}")


def main():
    actors, frames = load_all(), load_frames()
    quick = "--quick" in sys.argv
    if "--selftest" in sys.argv:
        noise = int(sys.argv[sys.argv.index("--noise") + 1]) if "--noise" in sys.argv else 0
        selftest(actors, frames, quick, noise, trials=50 if noise else 1)
    elif "--simulate" in sys.argv:
        a = actors[sys.argv[sys.argv.index("--simulate") + 1]]
        answers, sal = simulate(a, quick)
        print(f"Simulated supporter of {a['name']} ({'quick' if quick else 'deep'} mode)\n")
        report(answers, sal, a["country"], actors, frames)
    else:
        data = json.load(open(sys.argv[1], encoding="utf-8"))
        report(data.get("answers", {}), data.get("salience", {}), data.get("country"), actors, frames)


if __name__ == "__main__":
    main()
