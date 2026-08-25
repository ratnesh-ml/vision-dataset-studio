# Vision Dataset Studio

[![CI](https://github.com/ratnesh-ml/vision-dataset-studio/actions/workflows/test.yml/badge.svg)](https://github.com/ratnesh-ml/vision-dataset-studio/actions/workflows/test.yml)

I built Vision Dataset Studio around a data-centric idea: before training another classifier, I should understand the images I am giving it. This project audits an image folder, turns signals into a review queue, and keeps the reason for every flag visible so a person can change the policy instead of trusting a silent deletion.

It creates a manifest, measures dimensions, brightness, contrast, and a lightweight blur proxy, groups exact duplicates by SHA-256, and produces an explainable review queue.

> The goal is not another classifier notebook. It is a small workflow for finding data problems before those problems become model problems.

## Quality pipeline

```text
image folder → manifest → quality signals → duplicate groups → review queue → clean export
```

| Signal | What I use it for |
| --- | --- |
| Width and height | Catch malformed or unexpectedly tiny inputs. |
| Brightness and contrast | Surface blank, overexposed, or low-information images. |
| Blur proxy | Flag images that may be weak training examples. |
| SHA-256 | Find exact duplicates without trusting filenames. |
| Review reason | Make every flag explainable to a human reviewer. |

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

vision-studio make-sample sample_images --count 12
vision-studio audit sample_images --output reports/audit.json --html reports/audit.html
pytest -q
```

Open `reports/audit.html` in a browser. The optional API can be started with:

```bash
uvicorn vision_studio.api:app --reload
```

It exposes `/health` and `/audit?folder=sample_images`.

## The product decision behind the report

I deliberately separate *quality signals* from *decisions*. A low-contrast image is flagged for review; it is not silently removed. The exported manifest retains the reason, threshold, and computed value, which lets a reviewer adjust a policy without re-running feature extraction.

## Limits and next steps

The blur score is a simple variance-of-gradient proxy, not a learned quality model. SHA-256 catches exact duplicates but not near-duplicates. A deeper iteration would add perceptual hashing, class-balance and label audits, embedding-based outlier review, and a small browser labeling surface.

Use only synthetic or permission-cleared images. This repository is a learning workflow, not a production data-governance system.

## Verification, contribution, and license

Run `pytest -q` locally; GitHub Actions compiles the source and runs the suite on pushes and pull requests. Contributor guidance is in [CONTRIBUTING.md](CONTRIBUTING.md).

MIT licensed. See [LICENSE](LICENSE) and [INSPIRED_BY.md](INSPIRED_BY.md).
