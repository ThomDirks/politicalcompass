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

## Type code

Each axis gives one letter, the pole the score leans towards. A score inside ±15 gives an **x**, so people near the middle are not forced into a box. The eight letters are shown in two groups of four:

```
ECO SOC LIB MIG - INT CLI TEC DEM
 C   P   F   W  -  G   E   A   I      e.g. CPFW-GEAI
```

The letters are a working set and may change.

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

## Actors: parties and politicians

Every party or politician is an **actor** with a profile in `data/actors/<country>/<id>.json`. Profiles are dated with a `period`, so the same party can have several profiles over time (Labour 1997 and Labour 2024, for example). Individual politicians use the same format, with `type: "politician"` and a link to their party.

```json
{
  "id": "nl-d66",
  "type": "party",
  "name": "D66",
  "country": "NL",
  "period": { "from": "2025", "to": null, "basis": "What the score is based on" },
  "status": "draft",
  "salience": { "ECO": 3, "SOC": 4, "...": 0 },
  "facets": { "eco_own": [15, "m"], "...": [0, "l"] },
  "notes": { "ECO": "Short evidence per axis", "...": "" },
  "sources": [{ "title": "...", "url": "..." }]
}
```

Each facet score has a confidence: **h** (clear, documented position), **m** (direction known, size estimated) or **l** (thin evidence).

### Status of the current profiles

The first profiles are **drafts**. They were scored by hand from party programmes, voting behaviour and public positions as of November 2026. They are a starting point, not a measurement. Before going live they should be calibrated against independent data:

- **Chapel Hill Expert Survey 2024** for NL, DE and UK parties. It covers economy, GAL-TAN, EU, immigration, environment, civil liberties, anti-elite rhetoric and judicial independence, which maps onto about half the facets.
- **Voting advice tools** (StemWijzer, Kieskompas, Wahl-O-Mat) where parties answer statements themselves.
- **Roll-call votes** for individual politicians later (Tweede Kamer, Bundestag and UK Parliament open data, Voteview for the US Congress).

## Matching

A user is compared with each actor per facet. The distance on an axis is weighted by the user's salience for that axis. Matching at facet level means a party that agrees with you on economy but not on migration shows up as such, instead of disappearing into an average.

## Questions (next step)

- 3 to 4 statements per facet, answered on a 7-point agree/disagree scale
- half of the statements per facet phrased so that agreeing points towards the − pole, half towards the + pole, to cancel out the tendency to agree with everything
- quick mode: about 32 statements, one per facet
- deep mode: the full set, about 110 statements
- country frames swap in local examples while measuring the same facet

## Validation (later)

Once people take the test:

- check that statements within a facet hang together (internal consistency)
- check that the eight axes really measure different things (factor analysis)
- revisit facet weights and the centralisation facet
