"""Shared validation for the corrected TESS provenance research notebooks.

Keep this file beside notebooks 02-08. It validates saved products; it never
downloads observations, changes feature values, or fits a model.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

SCIENCE_FIX_VERSION = "eligibility_fap_v1"
FAP_POLICY = "periodogram_search_bounds"
FEATURE_COLUMNS = (
    "QualityScore", "OriginalFluxMedian", "OriginalFluxStd", "CadenceCount",
    "TimeSpanDays", "MedianCadenceDays", "FluxStd", "FluxMedian", "FluxMad",
    "FluxP05", "FluxP90", "FluxP95", "FluxIqr", "FluxAmplitude",
    "FluxPercentAmplitude95To5", "FluxSkewness", "FluxKurtosis", "TailAsymmetry",
    "TailRatio", "EtaVonNeumann", "MaxAbsSlope", "MedianAbsSuccessiveDiff",
    "FractionBeyond1Std", "FractionBeyond2Std", "LsBestPeriod", "LsMaxPower",
    "LsFalseAlarmProbability", "LsPeriod2", "LsPeriod3", "LsPeakPowerGap12",
    "LsPeakPowerGap23", "LsPowerRatio21", "LsPowerRatio31", "LsPeriodRatio21",
    "LsPeriodRatio31", "PhaseCurveStd", "PhasePeakPhase", "PhaseTroughPhase",
    "PhasePeakToTroughPhaseDelta",
)
ABLATION_FEATURES = (
    "QualityScore", "CadenceCount", "TimeSpanDays", "MedianCadenceDays",
    "OriginalFluxMedian", "OriginalFluxStd",
)


def _json_default(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    raise TypeError(f"Cannot serialize {type(value).__name__} in a run manifest")


def _canonical(value):
    return json.loads(json.dumps(value, default=_json_default, sort_keys=True,
                                 allow_nan=False))


def _sha256(path):
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_fingerprints(paths):
    """Return exact hashes of the requested existing files."""
    if isinstance(paths, (str, Path)):
        paths = (paths,)
    return {str(Path(path).resolve()): _sha256(path) for path in paths}


def _atomic_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _canonical(payload)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp",
                                      dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return payload


def _read_json(path):
    try:
        with Path(path).open(encoding="utf-8") as stream:
            payload = json.load(stream)
        return payload if isinstance(payload, dict) else None
    except (OSError, ValueError, TypeError):
        return None


def eligible_rows(df, min_cadences=100):
    """Keep successful feature rows with a finite cadence count >= threshold."""
    required = {"FeatureStatus", "CadenceCount"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Eligibility requires columns: {missing}")
    count = pd.to_numeric(df["CadenceCount"], errors="coerce")
    status = df["FeatureStatus"].astype("string").str.strip().eq("ok").fillna(False)
    valid = status & np.isfinite(count.to_numpy(dtype=float, na_value=np.nan)) & count.ge(min_cadences)
    return df.loc[valid.fillna(False)].copy()


def assert_eligible(df, min_cadences=100):
    clean = eligible_rows(df, min_cadences=min_cadences)
    if len(clean) != len(df):
        raise AssertionError(
            f"{len(df) - len(clean)} ineligible feature rows reached a matched analysis; "
            "require successful extraction and at least 100 finite cadences before pairing."
        )


def require_feature_schema(df, columns=None):
    columns = list(FEATURE_COLUMNS if columns is None else columns)
    if len(columns) != len(set(columns)):
        raise ValueError("The predictor schema contains duplicate names")
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"Corrected feature table is missing predictors: {missing}")
    return columns


def feature_manifest_path(path):
    return Path(str(path) + ".science_fix.json")


def write_feature_manifest(path, *, inputs=(), metadata=None):
    """Stamp only a successfully written, scientifically corrected feature file."""
    path = Path(path)
    return _atomic_json(feature_manifest_path(path), {
        "science_fix_version": SCIENCE_FIX_VERSION,
        "fap_policy": FAP_POLICY,
        "feature_file": str(path.resolve()),
        "output_sha256": _sha256(path),
        "inputs": file_fingerprints(inputs),
        "metadata": metadata,
    })


def feature_cache_is_current(path, *, inputs=(), metadata=None):
    path = Path(path)
    record = _read_json(feature_manifest_path(path))
    if not record or not path.is_file():
        return False
    try:
        if (record.get("science_fix_version") != SCIENCE_FIX_VERSION
                or record.get("fap_policy") != FAP_POLICY
                or record.get("output_sha256") != _sha256(path)):
            return False
        recorded_inputs = record.get("inputs")
        if not isinstance(recorded_inputs, dict):
            return False
        # Downstream readers also validate the metadata inputs recorded by the
        # producer, even when they do not supply an explicit input list.
        expected_inputs = file_fingerprints(inputs if inputs else recorded_inputs)
        if recorded_inputs != expected_inputs:
            return False
        if metadata is not None and record.get("metadata") != _canonical(metadata):
            return False
    except (OSError, TypeError, ValueError):
        return False
    return True


def read_corrected_features(path):
    path = Path(path)
    if not feature_cache_is_current(path):
        raise ValueError(
            f"Missing, stale, or unversioned corrected feature cache: {path}. "
            "Rerun its producer (02 for baseline features, 05 for detrended "
            "features, or 06 for clipped features) with recomputation enabled. "
            "Do not add a sidecar to old feature values."
        )
    return pd.read_parquet(path)


def write_run_manifest(path, *, inputs=(), config=None, outputs=()):
    return _atomic_json(path, {
        "science_fix_version": SCIENCE_FIX_VERSION,
        "inputs": file_fingerprints(inputs),
        "config": config,
        "outputs": file_fingerprints(outputs),
    })


def run_cache_is_current(path, *, inputs=(), config=None, outputs=()):
    record = _read_json(path)
    if not record or record.get("science_fix_version") != SCIENCE_FIX_VERSION:
        return False
    try:
        return (record.get("inputs") == file_fingerprints(inputs)
                and record.get("config") == _canonical(config)
                and record.get("outputs") == file_fingerprints(outputs))
    except (OSError, TypeError, ValueError):
        return False
