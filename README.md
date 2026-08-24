# Vision Dataset Studio

[![CI](https://github.com/ratnesh-ml/vision-dataset-studio/actions/workflows/test.yml/badge.svg)](https://github.com/ratnesh-ml/vision-dataset-studio/actions/workflows/test.yml)

Vision Dataset Studio is a data-centric computer-vision app that audits an
image folder before model training. It creates a manifest, measures image
dimensions, brightness, contrast, and a lightweight blur proxy, groups exact
duplicates by SHA-256, and produces a review queue with reasons.

> The innovation is not another classifier notebook. It is a small workflow
> for finding bad data before bad data becomes a model problem.

## Quality pipeline

```text
image folder -> manifest -> quality signals -> duplicate groups -> review queue -> clean export
```

| Signal | Why it matters |
| --- | --- |
| Width/height | Catches malformed or unexpectedly tiny inputs |
| Brightness/contrast | Surfaces blank, overexposed, or low-information images |
| Blur proxy | Flags images that may be unhelpful for training |
| SHA-256 | Finds exact duplicate files without trusting filenames |
| Review reason | Makes each exclusion explainable to a human |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
vision-studio make-sample sample_images --count 12
vision-studio audit sample_images --output reports/audit.json --html reports/audit.html
pytest -q
```

Open `reports/audit.html` in a browser. The optional FastAPI surface can be
started with `uvicorn vision_studio.api:app --reload` and exposes
`/health` and `/audit?folder=sample_images`.

## Portfolio evidence

The report separates *quality signals* from *decisions*. A low-contrast image
is flagged for review, not silently deleted. The exported manifest keeps the
reason, threshold, and computed value so a reviewer can change the policy
without rerunning feature extraction.

## Limitations and next experiments

The blur score is a simple variance-of-gradient proxy, not a learned quality
model. The duplicate detector catches exact duplicates but not near-duplicates.
Next steps include perceptual hashing, class-balance checks, label audits,
embedding-based outlier review, and a small browser labeling surface.


## Contribution and verification

The repository includes contributor guidance in [`CONTRIBUTING.md`](CONTRIBUTING.md). GitHub Actions compiles the source and runs the test suite on every push and pull request. Use synthetic or permission-cleared images only.


## License

MIT. See [LICENSE](LICENSE) and [INSPIRED_BY.md](INSPIRED_BY.md).
