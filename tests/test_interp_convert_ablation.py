"""
Tests for converting ablation runs into judge-pipeline input.

The properties that matter are that arms are split correctly, that an
incomplete run is rejected rather than silently producing rate comparisons
across different denominators, and that malformed input fails loudly.
"""

from __future__ import annotations

import json

import pytest

from tracekit.interp.convert_ablation import convert_ablation
from tracekit.io.dataset import EvalResult
from tracekit.io.jsonl import read_jsonl


def _rec(item_id: str, arm: str, **over) -> dict:
    base = {
        "item_id": item_id,
        "category": "values_conflict_low",
        "condition": "base",
        "responder_model": "together:meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "arm": arm,
        "start_layer": 40,
        "ablation_layers": [0, 79],
        "completion": f"text for {item_id} under {arm}",
        "finish_reason": "stop",
        "n_new_tokens": 42,
        "max_new_tokens": 500,
    }
    base.update(over)
    return base


def _write(tmp_path, recs):
    p = tmp_path / "ablation_runs.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    return p


def test_one_file_per_arm(tmp_path):
    recs = [_rec(f"vcl_{i:03d}", arm) for arm in ("none", "target", "random") for i in range(3)]
    written = convert_ablation(_write(tmp_path, recs), tmp_path / "out")
    names = sorted(p.name for p in written)
    assert names == [
        "steerability_v2_ablated_none.jsonl",
        "steerability_v2_ablated_random.jsonl",
        "steerability_v2_ablated_target.jsonl",
    ]


def test_completion_lands_in_base_slot(tmp_path):
    recs = [_rec("vcl_001", "target")]
    written = convert_ablation(_write(tmp_path, recs), tmp_path / "out")
    results = list(read_jsonl(written[0], EvalResult))
    assert len(results) == 1
    r = results[0]
    assert r.raw_completions[0] == "text for vcl_001 under target"
    assert r.raw_completions[1] == ""
    assert r.finish_reasons == ["stop", None]
    assert r.model_name == "ablated:target"


def test_items_are_sorted_within_an_arm(tmp_path):
    recs = [_rec(i, "none") for i in ("vcl_003", "vcl_001", "vcl_002")]
    written = convert_ablation(_write(tmp_path, recs), tmp_path / "out")
    ids = [r.item_id for r in read_jsonl(written[0], EvalResult)]
    assert ids == sorted(ids)


def test_extra_carries_provenance(tmp_path):
    written = convert_ablation(_write(tmp_path, [_rec("vcl_001", "target")]), tmp_path / "out")
    extra = next(iter(read_jsonl(written[0], EvalResult))).extra
    assert extra["ablation_arm"] == "target"
    assert extra["ablation_layers"] == [0, 79]
    assert extra["extraction_layer"] == 40
    assert extra["category"] == "values_conflict_low"


def test_mismatched_item_sets_rejected(tmp_path):
    """An incomplete run must not be converted into unequal denominators."""
    recs = [_rec("vcl_001", "none"), _rec("vcl_002", "none"), _rec("vcl_001", "target")]
    with pytest.raises(ValueError, match="different item set"):
        convert_ablation(_write(tmp_path, recs), tmp_path / "out")


def test_duplicate_item_within_arm_rejected(tmp_path):
    recs = [_rec("vcl_001", "none"), _rec("vcl_001", "none")]
    with pytest.raises(ValueError, match="duplicate item_ids"):
        convert_ablation(_write(tmp_path, recs), tmp_path / "out")


def test_missing_field_rejected(tmp_path):
    bad = _rec("vcl_001", "none")
    del bad["completion"]
    with pytest.raises(ValueError, match="missing fields"):
        convert_ablation(_write(tmp_path, [bad]), tmp_path / "out")


def test_invalid_json_rejected(tmp_path):
    p = tmp_path / "ablation_runs.jsonl"
    p.write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        convert_ablation(p, tmp_path / "out")


def test_blank_lines_ignored(tmp_path):
    p = tmp_path / "ablation_runs.jsonl"
    p.write_text(json.dumps(_rec("vcl_001", "none")) + "\n\n\n", encoding="utf-8")
    written = convert_ablation(p, tmp_path / "out")
    assert len(list(read_jsonl(written[0], EvalResult))) == 1


def test_empty_file_rejected(tmp_path):
    p = tmp_path / "ablation_runs.jsonl"
    p.write_text("\n", encoding="utf-8")
    with pytest.raises(ValueError, match="No records"):
        convert_ablation(p, tmp_path / "out")


def test_missing_file_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        convert_ablation(tmp_path / "nope.jsonl", tmp_path / "out")


def test_output_dir_created(tmp_path):
    out = tmp_path / "deep" / "nested"
    convert_ablation(_write(tmp_path, [_rec("vcl_001", "none")]), out)
    assert out.is_dir()
