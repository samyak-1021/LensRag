"""Serve the latest evaluation summary to the dashboard.

The report itself is produced offline by ``python -m app.eval.runner`` (or in CI)
and written to ``data/eval/summary.json``. Keeping generation out of the request
path means the dashboard is instant and the API needs no heavy eval dependencies.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from app.config import BACKEND_DIR
from app.schemas import EvalSummary

router = APIRouter(prefix="/eval", tags=["eval"])

SUMMARY_PATH = BACKEND_DIR / "data" / "eval" / "summary.json"


@router.get("/summary", response_model=EvalSummary)
async def eval_summary() -> EvalSummary:
    if not SUMMARY_PATH.exists():
        raise HTTPException(status_code=404, detail="No evaluation has been run yet.")
    return EvalSummary.model_validate(json.loads(SUMMARY_PATH.read_text()))
