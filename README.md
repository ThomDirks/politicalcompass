# PCompass

A political orientation test that goes further than left/right and auth/lib. You get a profile on eight axes and 32 facets, a short type code, and a comparison with parties (and later politicians) from the Netherlands, Germany, the United Kingdom and the United States.

Because "left" in one country can be "right" in another, scores are measured on absolute scales and then read against a country frame of your choice.

## Repository layout

| Path | What it holds |
|------|---------------|
| [`docs/model.md`](docs/model.md) | How the model works: axes, facets, scoring, type code, country frames |
| [`docs/party-overview.md`](docs/party-overview.md) | Generated table of all party profiles per country |
| `data/model.json` | Axes, facets and the anchors that define each scale |
| `data/countries/` | Country frames: parties, weights, local topics |
| `data/actors/<country>/` | One profile per party (politicians later) |
| `tools/validate.py` | Checks all data and regenerates the overview |

## Status

Model spec and first draft profiles for 34 parties. The profiles still need to be calibrated against the Chapel Hill Expert Survey and voting advice tools. Next up: the question bank.

```
python tools/validate.py --report
```
