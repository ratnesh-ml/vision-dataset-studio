# Contributing

Thanks for helping improve Vision Dataset Studio. Prefer focused pull requests that improve a quality signal, review-queue rule, report output, or API contract, and include a regression test.

Before opening a pull request, run:

```bash
pip install -e ".[dev]"
python -m compileall -q src
pytest -q
```

Use synthetic or permission-cleared images only. Do not commit private datasets, personal images, credentials, or generated reports containing sensitive metadata. When changing a metric or flag, document the interpretation and update the README and limitations section.
