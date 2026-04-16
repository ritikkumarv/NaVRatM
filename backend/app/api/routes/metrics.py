"""Detection-performance metrics endpoint."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter

from app.api.routes.applications import _APPS, _ensure_seeded
from app.core.pipeline import process_application as run_pipeline
from app.data.seed_data import SEED_APPLICATIONS
from app.models.schemas import DeclaredValues, ExtractedFields

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["metrics"])


@router.get("/metrics")
async def get_metrics():
    """Process all seed apps through the pipeline and compare against ground truth."""
    _ensure_seeded()

    # Ground truth from seed data
    ground_truth: dict[str, dict] = {}
    for seed in SEED_APPLICATIONS:
        ground_truth[seed["id"]] = {
            "fraud_label": seed.get("fraud_label", False),
            "fraud_type": seed.get("fraud_type", "clean"),
        }

    tp = fp = tn = fn = 0
    pattern_counts: dict[str, dict] = {}
    total_time = 0.0
    processed = 0

    for app_id, app in list(_APPS.items()):
        gt = ground_truth.get(app_id)
        if gt is None:
            continue

        # Run pipeline for unprocessed apps
        if app.get("risk_score") is None:
            declared = DeclaredValues(**app["declared"])
            extracted_docs: list[tuple[str, ExtractedFields]] = []
            for doc in app.get("documents", []):
                ext = doc.get("extracted")
                if ext:
                    source = doc.get("source", doc.get("type", "unknown"))
                    try:
                        fields = ExtractedFields(**ext)
                    except Exception:
                        continue
                    extracted_docs.append((source, fields))

            t0 = time.time()
            try:
                profile = await run_pipeline(app_id, declared, extracted_docs, _APPS)
                app["risk_score"] = profile.risk_score
                band_val = (
                    profile.risk_band.value
                    if hasattr(profile.risk_band, "value")
                    else profile.risk_band
                )
                app["risk_band"] = band_val
                app["risk_factors"] = [f.model_dump() for f in profile.factors]
                app["anomalies"] = [a.model_dump() for a in profile.anomalies]
                app["network_flags"] = [n.model_dump() for n in profile.network_flags]
            except Exception as exc:
                log.warning("Pipeline failed for %s: %s", app_id, exc)
                continue
            total_time += time.time() - t0

        processed += 1

        band = app.get("risk_band", "low")
        predicted_positive = band in ("high", "critical")
        actual_positive = gt["fraud_label"]

        if predicted_positive and actual_positive:
            tp += 1
        elif predicted_positive and not actual_positive:
            fp += 1
        elif not predicted_positive and actual_positive:
            fn += 1
        else:
            tn += 1

        ft = gt["fraud_type"]
        if ft not in pattern_counts:
            pattern_counts[ft] = {"total": 0, "detected": 0}
        pattern_counts[ft]["total"] += 1
        if (actual_positive and predicted_positive) or (
            not actual_positive and not predicted_positive
        ):
            pattern_counts[ft]["detected"] += 1

    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2.0 * precision * recall / max(precision + recall, 1e-9)

    return {
        "total_apps_processed": processed,
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "processing_time_avg_seconds": round(total_time / max(processed, 1), 3),
        "per_pattern_breakdown": pattern_counts,
    }
