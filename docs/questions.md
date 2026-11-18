# Questions and scoring

The question bank lives in [`data/questions.json`](../data/questions.json). A readable version of every statement is in [`question-list.md`](question-list.md).

## What's in the bank

- **96 statements**, three per facet, plus 8 consistency checks in the full test, answered on a 7-point scale from *strongly disagree* (−3) to *strongly agree* (+3). *No opinion* skips the statement.
- **8 salience questions**, one per axis: "How much do these topics matter to you?", from *not at all* (0) to *it decides my vote* (4).
- **Quick mode**: one statement per facet, 32 in total. **Deep mode**: all 96.
- **27 country versions** that swap in a local example (the Mietpreisbremse, nitrogen, small boats, Paris withdrawal) while measuring the same thing.

## Country versions

Some debates are specific to a country, and some statements only make sense in one country. A statement can have a country version that replaces the general text. A country version can push in its own direction: in the Netherlands the abortion statement is about taking abortion out of the criminal code, in Germany about §218, in the UK about removing it from criminal law for providers too, in the US about legality nationwide. Each answer is scored with the direction of the version that was shown.

General statements are written as concepts or debate points, so they still work where something is already legal ("Ending a pregnancy in the first months should be the woman's decision alone"). The validator checks that every topic stays balanced in every country, not just in the general version.

## Answer consistency (full test)

The full test adds **8 check statements** that restate an earlier statement in other words, half of them as its mirror image. They aren't scored. The consistency score combines:

- how closely each check answer matches the original
- whether answers within a topic point the same way
- a penalty when more than 70% of all answers are identical

Scores of 85 and up count as high, 70 to 84 as medium, below 70 as low. In simulation, careful respondents score 98 to 100 and careless ones at most about 71, with 86% of careless ones flagged as low. These thresholds should be revisited once real answers exist. Quick mode has no checks and shows no score.

## How the statements are written

- **Balanced direction.** On every axis, six statements push towards one pole when you agree and six towards the other. In quick mode it's two and two. Some people tend to agree with whatever they read, and this cancels that tendency out. The validator refuses an unbalanced bank.
- **One idea per statement.** No "and" that joins two positions, so you don't have to agree with half a sentence.
- **Trade-offs spelled out where they matter.** "The minimum wage should go up substantially, even if some jobs disappear" measures more than "the minimum wage should go up", which almost everyone agrees with.
- **No party names, no labels.** Statements describe policies, not camps. "Left", "right", "woke" or "elite" never appear as cues.
- **Neutral tone in both directions.** Each side's statement should sound like something a reasonable supporter would actually say.
- **Plain English.** No jargon. Where a technical term is needed it gets explained in the sentence.

## Scoring

1. **Facet score**: each answer is multiplied by the statement's direction (+1 or −1). The facet score is the mean of those values, scaled to −100..+100. Skipped statements don't count.
2. **Axis score**: the mean of the four facets.
3. **Type code**: one letter per axis, as described in [model.md](model.md#type-code).
4. **Country view**: each axis score compared with the selected country's centre, for example "towards Restrictive (+35 from the centre)".

## Matching

Your facet scores are compared with every party's current profile. Each facet difference is weighted by how much you care about its axis (your salience answer; 2 if you skip it, 0 removes the axis). Similarity runs from 0 to 100.

A party is only ranked if its profile covers at least half of what you answered. That keeps parties with only CHES data (which covers 20 of 32 facets) from looking closer than they are. Current parties in your country are ranked first. Historical and minor parties are listed separately.

## Testing

`tools/score.py --selftest` creates a simulated supporter for every party, answering each statement the way that party's profile suggests, and checks whether the party comes out on top. `--noise 1` or `--noise 2` adds random error to every answer and skips about one in ten statements, 50 times per party. Results with the current data:

| Mode | Noise | Own party first | Own party in top 3 |
|---|---|---:|---:|
| Deep | 0 | 100% | 100% |
| Quick | 0 | 100% | 100% |
| Deep | 1 | 98% | 100% |
| Quick | 1 | 92% | 100% |
| Deep | 2 | 92% | 100% |
| Quick | 2 | 77% | 97% |

The parties that get mixed up are the ones you would expect: D66 and Volt, PVV and DNA, SNP and Plaid Cymru, Reform UK and Restore Britain.

This only shows that the questions can tell the party profiles apart. Whether the statements measure what they claim to measure in real people needs real response data (see [model.md](model.md#validation-later)).

## Try it

```
python tools/score.py --simulate de-spd          # answers as a typical SPD supporter would
python tools/score.py my-answers.json            # score your own answers
```
