# PCompass

A political orientation test that goes further than left/right and auth/lib. You see which of eighteen political types your views align with most closely (each with its own character), how you differ from that type on every topic, a profile on eight axes and 32 facets, and a comparison with current and historical parties and 134 politicians and public figures from the Netherlands, Germany, the United Kingdom and the United States.

Because "left" in one country can be "right" in another, scores are measured on absolute scales and then read against a country frame of your choice. Every party has dated snapshots, so you can also see how parties drifted over the years.

## Repository layout

| Path | What it holds |
|------|---------------|
| [`docs/model.md`](docs/model.md) | How the model works: axes, facets, scoring, type code, country frames, snapshots, drift |
| [`docs/party-overview.md`](docs/party-overview.md) | Current profile of every party, per country, plus former parties |
| [`docs/people.md`](docs/people.md) | Every person (politicians and public figures, current and past) with their type |
| [`docs/drift.md`](docs/drift.md) | Every snapshot of every party over time |
| [`docs/calibration.md`](docs/calibration.md) | Hand scores compared with the Chapel Hill Expert Survey 2024 |
| [`docs/questions.md`](docs/questions.md) | How the questions are written, scored, matched and tested |
| [`docs/question-list.md`](docs/question-list.md) | Every statement, readable |
| `data/model.json` | Axes, facets and the anchors that define each scale |
| `data/countries/` | Country frames: parties, weights, local topics |
| `data/actors/<country>/` | One file per party or person with all its snapshots |
| `data/people.json` | Source of the people profiles: base party and era, adjustments and notes |
| `data/ches_mapping.json` | How CHES items map onto PCompass facets |
| `data/types.json` | The nine camps and eighteen political types, their dimensions and descriptions |
| `data/questions.json` | The question bank: 109 statements (concept and policy), consistency checks, salience questions, country versions |
| `index.html` | The website, built from `web/template.html` and `web/characters.js` with `tools/build_web.py`. Live at https://thomdirks.github.io/politicalcompass/ |
| `tools/` | Import, calibration, validation, scoring and build scripts |

## Data sources

- **Hand-scored profiles** for current parties (November 2026) and for historical parties and eras.
- **Chapel Hill Expert Survey 1999-2024** for European parties: Jolly et al. and Rovny et al., [chesdata.eu](https://www.chesdata.eu/). The data is downloaded by the import script, not stored in this repository.

## Scripts

```
python tools/import_ches.py      # (re)import CHES snapshots
python tools/calibrate_ches.py   # calibrate new hand snapshots against CHES 2024
python tools/build_people.py     # rebuild people profiles from data/people.json
python tools/validate.py --report
python tools/score.py --selftest --noise 1   # can the questions tell parties apart?
python tools/score.py --simulate nl-vvd      # answer as a party's supporter would
python tools/simulate.py                     # how types fill up, how the consistency score behaves
python tools/build_web.py                    # rebuild index.html, then commit it to update the live site
```

## Status

Model spec, 56 parties with 230 snapshots, 134 people (at least five per type), a 109-statement question bank, eighteen types, and a printable export. All hand scores are drafts. The website is live at https://thomdirks.github.io/politicalcompass/.
