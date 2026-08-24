from fastapi import FastAPI, Query

from .core import audit_folder

app = FastAPI(title="Vision Dataset Studio", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.get("/audit")
def audit(folder: str = Query(..., min_length=1)):
    return audit_folder(folder)

