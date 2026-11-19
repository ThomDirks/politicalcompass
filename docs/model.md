# PCompass model

This document describes how PCompass measures political views and how parties and politicians are profiled. The machine-readable version of everything below lives in [`data/model.json`](../data/model.json).

## Idea

Most political quizzes squeeze everyone onto one or two lines. PCompass works more like a personality test: eight broad axes, each split into four facets, so two people who both score "centre-right" can still look very different underneath.

Positions are measured on **absolute** scales. Whether someone is "left" or "right" depends on the country they compare themselves to, so that label is calculated afterwards from a country frame. A mainstream US Democrat and a Dutch social democrat get the same treatment: both are scored on the same scales, and the frame decides what those scores mean locally.

## Axes and facets

Every score runs from −100 to +100. The negative pole comes first.

| # | Axis | − pole | + pole | Facets |
|---|------|--------|--------|--------|
| 1 | Economy | C Collective | M Market | ownership of key sectors, market regulation and housing, labour, tax and welfare |
| 2 | Social values | P Progressive | T Traditional | family and gender, LGBTQ rights, religion in public life, personal morality laws |
| 3 | Liberty vs order | F Freedom | O Order | surveillance and privacy, policing and justice, limits on speech, emergency powers |
| 4 | Migration and identity | W Welcoming | R Restrictive | immigration levels, asylum, integration, national culture |
| 5 | International | G Global | N National | supranational integration, trade, alliances and defence, development aid |
| 6 | Climate and environment | E Ecological | D Developmental | climate ambition, transition costs and mandates, nature and agriculture, climate deals |
| 7 | Technology | S Sceptical | A Accelerating | AI and automation, biotech, nuclear and new energy tech, power of big tech |
| 8 | Democracy and institutions | I Institutional | V Vox populi | trust in institutions, direct democracy, power of the courts, centralisation |

Each facet has written anchors for −100, 0 and +100 in `model.json`. The anchors are what makes scores comparable across countries, so they describe concrete policy, not labels.

Some notes on choices:

- **Limits on speech** counts restrictions from every direction. Hate speech laws push a party towards +100, and so do protest bans or campus speech rules.
- **Alliances and defence** treats leaving NATO the same whether the reason is pacifism or nationalism. The facet measures the position, not the motive.
- **Centralisation** does not fit neatly under democracy and institutions. It stays there for now and gets checked once real response data exists.
- **Environment** has its own axis because green parties are a major party family in three of the four starting countries.

## Axis scores

An axis score is the mean of its four facets. Facets carry equal weight for now. Once response data exists, weights can be estimated instead of assumed.

## Political types

There are **eighteen types**, arranged on a map of **nine camps** by economy (Collective, Balanced, Market) and culture (Progressive, Neutral, Traditional), and split within each camp by power: **I** Institutional or **S** Sovereigntist. Codes read like `CPI` or `MNS`.

### Closest alignment, not a box

Every type has a **typical profile**: an average position on all eight axes, stored in [`data/types.json`](../data/types.json). A person or party is aligned with the type whose profile is closest, measured as the weighted mean distance across the eight axes (climate and technology count half). The result is shown as an **alignment percentage**, 100 minus half that distance, together with the next closest type.

Because the profile covers all eight axes, mixed views stay visible instead of averaging out. The results page shows a meter per axis with the person's position, the typical profile of their type and the national average. Someone like Pim Fortuyn aligns with the Independent, and the meters show where he differs: much more progressive on social values, more restrictive on migration.

The small letter after the code (**e** Ecological or **g** Growth) comes from the person's own climate and technology scores, not from the type.

### Descriptions

Each type is described from its own point of view, in a positive light. A political view isn't wrong for being held, and the purpose of the test is to help people recognise where they stand, not to persuade them. Type pages and results also place the type in the selected country: how the typical profile compares with the national average, and which parties come closest there.

Parties get a type the same way, from their current profile, including former parties. A type describes policy positions only, not how a party gained or used power.

### Checking the spread

`tools/simulate.py` generates respondents (party-like, mixed and careless), answers the questions for them and reports how the types fill up and how the consistency score behaves. With the current design every type is reachable, the centre types take about 9% each, and the median alignment is around 90%. This tests the design against assumptions, not against real people.

## Salience

Positions alone miss half the picture. Two voters with the same views differ if one only cares about migration and the other only about housing. Every actor and every user gets a salience weight from 1 to 5 per axis.

For users, salience is asked directly ("how much does this matter to you?"). It weights the matching and also acts as the filter: setting an axis to 0 removes it.

For parties, salience reflects how central the axis is to their programme and campaigns.

## Country frames

A country frame (`data/countries/<code>.json`) holds:

- the parties and a weight for each (vote share at the last national election, or current seats where a party split since; the basis is written in each frame)
- a **centre** per axis, calculated as the weighted mean of those parties
- local topics per axis, used to write country-specific example questions

Relative labels come from the distance to the centre. A user at −30 on Economy is close to the centre in the Netherlands but clearly left of centre in the US. The underlying score does not change between frames, only its interpretation.

## Actors: parties and people

Every party or politician is an **actor** with one file in `data/actors/<country>/<id>.json`. An actor holds its identity (name, country, years active, predecessors and successors) and a list of dated **snapshots**. Politicians and public figures use the same format with `type: "person"` (see [People](#people)).

```json
{
  "id": "uk-labour",
  "type": "party",
  "name": "Labour",
  "country": "UK",
  "active": { "from": 1900, "to": null },
  "predecessors": [],
  "status": "draft",
  "snapshots": [
    { "year": 1945, "method": "hand", "label": "Attlee era", "facets": { "eco_own": [-85, "m"], "...": null } },
    { "year": 2019, "method": "ches", "label": "CHES 2019", "facets": { "eco_reg": [-80, "h"], "...": null }, "proxies": { "ECO": -70 } },
    { "year": 2026, "method": "hand", "label": "Current (Nov 2026)", "facets": { "...": [0, "m"] } }
  ]
}
```

Each facet score is `[score, confidence]`: **h** (clear, documented position), **m** (direction known, size estimated) or **l** (thin evidence). `null` means no data for that facet in that snapshot.

### Two kinds of snapshots

**Hand-scored (`method: "hand"`).** Scored against the facet anchors from programmes, votes and conduct in office. Every current snapshot scores all 32 facets. Historical snapshots leave a facet `null` only when the issue did not exist yet (AI in 1936, climate deals in 1965). Hand snapshots also carry salience and a short note per axis.

**Expert survey (`method: "ches"`).** Imported from the Chapel Hill Expert Survey trend file, 1999 to 2024, with `tools/import_ches.py`. CHES asks about 20 of the 32 facets (mapping in `data/ches_mapping.json`); the rest stay `null`. In 1999 and 2002 CHES only asked overall economic left/right, GAL-TAN and EU position, so those snapshots carry axis **proxies** for Economy and Social values instead of facet detail. The raw CHES values are stored in each snapshot for transparency.

### Calibration

The current hand scores were checked against CHES 2024 with `tools/calibrate_ches.py`. Where the two differed by 35 points or more on a facet, the score became the average of both, unless there is a documented reason to keep the hand score (for example a policy change after 2024). Every adjustment and every exception is recorded in the snapshot under `calibration`. `docs/calibration.md` lists the remaining differences.

### Drift

Because every actor has dated snapshots, PCompass can show how a party moved over time: Labour from Attlee to Foot to Blair to Corbyn and Starmer, or the VVD's swing on migration. `docs/drift.md` lists every snapshot per party. Things to keep in mind when reading drift:

- Compare like with like. CHES rows only cover the facets CHES asks about, and early waves only have proxies. A jump between a CHES row and a hand row can partly be the change of method.
- Scales are absolute. A 1936 party is measured against today's anchors, so most historical parties look traditional on social values. That is accurate in absolute terms. Reading a party relative to its own time needs historical country frames, which are a later step.
- Merged parties keep their history through `predecessors`: PRO links to PvdA and GroenLinks, CDA to KVP and ARP, Die Linke to the SED via the PDS.

### Historical parties

Former parties are included when they were large or historically significant: for example NSDAP, KPD, Zentrum and SED in Germany; NSB, KVP, ARP, CPN, LPF, PvdA and GroenLinks in the Netherlands; BUF, SDP, UKIP and BNP in the UK; and the Dixiecrats in the US. They are scored on the same scales as current parties, which makes it possible to show plainly where an answer pattern overlaps with, for example, fascist or communist programmes. Profiles of totalitarian parties describe their programme and conduct in office factually, including persecution and genocide where relevant.

### Smaller and historical parties scored at topic level

43 further parties are kept in `data/parties_extra.json` and built with `tools/build_parties_extra.py`: Northern Irish parties, the German minor parties that stood in 2025, Weimar parties (DNVP, DDP, DVP, USPD), Dutch parties that merged into GroenLinks, CDA and ChristenUnie (PPR, PSP, CHU, GPV), protest parties (Boerenpartij, Leefbaar Nederland, BVNL), and American third parties from the Whigs and Know Nothings to the Libertarians, Greens and Forward. They get one score per topic, with single parts set where the party clearly differs inside a topic, so their confidence is lower than for the main parties. Parties that stood at the last national election are in the country frame at their vote share (0 where they won no seats under a seat-based frame), which hardly moves the centre but lists them as current.

### People

178 politicians and public figures, current and past, from the four countries, with at least five for every type (the validator enforces this). They are written in `data/people.json` and built into `data/actors/` by `tools/build_people.py`. Each person has one snapshot at a moment in their career (Thatcher in 1987, Merkel in 2015, Fortuyn in 2002).

- **Views, not actions.** A person is scored on what they said and stood for: speeches, writing, the programmes they ran on. What they did with power is not scored. This is the opposite of party snapshots, which also use record in office.
- **From a party, then adjusted.** Most people start from their party's hand snapshot closest to their era (`base`, `base_year`). `axes` moves every facet of an axis by a number of points, `facets` sets single facets, and every change carries a note. Unchanged parts follow the party, with confidence lowered one step. Rutte, for example, starts from today's VVD and moves 15 points towards open on migration and towards global on international affairs.
- **Scored directly.** People without a fitting party, such as writers, campaigners and independents (Chomsky, Friedman, Snowden, Perot), get an absolute score per axis in `scores`, with low confidence.
- **Era.** Facets for issues that did not exist yet are left empty: AI before 2010, big tech before 2005, EU integration before 1950, climate deals before 1985-1990, nuclear power before 1945. Like historical parties, historical people are measured on today's scales, so many look traditional on social values.
- **No regime leaders.** Leaders of the totalitarian parties are not included as people. Those parties stay in as party profiles.

`docs/people.md` lists every person with their type and next closest type.

## Export

The Export page turns a finished test into a printable A4 report (Save as PDF from the print window): type, alignment, next closest type and consistency; the meters against the typical member of the type; all 32 parts with the closest standpoint text from the facet anchors; the closest parties (own country, all four, former) and people; **standpoints you share**, the current parties and people within 12 points of you on each part, with their overall match so cross-camp agreement is visible; **common ground across camps**, actors under 75% overall who sit within 10 points on four parts or more; and every answer with the statement as shown.

## Possible simplification

Eight axes may be too many for the main result screen. Since every axis is the mean of its facets, axes can later be **bracketed** into fewer groups (for example an economic, a cultural and an institutional block) without rescoring anything. This is still open.

## Matching

A user is compared with each actor per facet. The distance on an axis is weighted by the user's salience for that axis. Matching at facet level means a party that agrees with you on economy but not on migration shows up as such, instead of disappearing into an average.

## Questions

96 statements (three per facet) on a 7-point agree/disagree scale, balanced per axis so that agreeing with everything does not push anyone in one direction, plus a salience question per axis. Quick mode uses 32 of them. Country frames swap in local examples while measuring the same facet. Details, scoring and test results: [questions.md](questions.md).

## Validation (later)

Once people take the test:

- check that statements within a facet hang together (internal consistency)
- check that the eight axes really measure different things (factor analysis)
- revisit facet weights and the centralisation facet
