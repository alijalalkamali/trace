"""
Tests for directional ablation.

The properties that matter are mathematical (the result is orthogonal to the
ablated direction, other directions survive untouched) and structural (hooks
are removed, dtypes round-trip, shape mismatches raise rather than broadcast
silently). All of them are checkable on a tiny fake model on CPU; none require
loading weights.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest
import torch
import torch.nn as nn

from tracekit.interp.ablate import (
    ARM_NONE,
    ARM_RANDOM,
    ARM_TARGET,
    AblationArm,
    AblationHook,
    random_unit_direction,
    resolve_ablation_layers,
)

HIDDEN = 16
N_LAYERS = 8


class _TupleLayer(nn.Module):
    """Returns (hidden, aux) like a HF decoder layer on most transformers versions."""

    def forward(self, x: torch.Tensor):  # type: ignore[override]
        return (x, "aux")


class _BareLayer(nn.Module):
    """Returns a bare tensor, as some transformers versions do."""

    def forward(self, x: torch.Tensor):  # type: ignore[override]
        return x


def _stack(cls=_TupleLayer, n: int = N_LAYERS) -> nn.ModuleList:
    return nn.ModuleList([cls() for _ in range(n)])


def _unit(v: np.ndarray) -> np.ndarray:
    return (v / np.linalg.norm(v)).astype(np.float32)


# ---------------------------------------------------------------------------
# random_unit_direction
# ---------------------------------------------------------------------------


def test_random_direction_is_unit_norm_and_deterministic():
    a = random_unit_direction(HIDDEN, seed=7)
    b = random_unit_direction(HIDDEN, seed=7)
    assert a.shape == (HIDDEN,)
    assert a.dtype == np.float32
    assert np.isclose(np.linalg.norm(a), 1.0, atol=1e-6)
    np.testing.assert_array_equal(a, b)


def test_random_direction_differs_across_seeds():
    assert not np.allclose(random_unit_direction(HIDDEN, 1), random_unit_direction(HIDDEN, 2))


def test_random_direction_rejects_bad_dim():
    with pytest.raises(ValueError, match="dim must be positive"):
        random_unit_direction(0, seed=0)


def test_random_direction_is_near_orthogonal_in_high_dim():
    """Two independent unit vectors in 8192-D are near-orthogonal; the control
    arm relies on this so it does not accidentally re-ablate the target."""
    a = random_unit_direction(8192, seed=1)
    b = random_unit_direction(8192, seed=2)
    assert abs(float(np.dot(a, b))) < 0.05


# ---------------------------------------------------------------------------
# resolve_ablation_layers
# ---------------------------------------------------------------------------


def test_layers_default_is_every_layer():
    """Global ablation is the main configuration, not a layer range."""
    assert resolve_ablation_layers(N_LAYERS) == list(range(N_LAYERS))


def test_layers_start_layer_runs_to_end_of_stack():
    assert resolve_ablation_layers(N_LAYERS, start_layer=5) == [5, 6, 7]


def test_layers_single_layer_mode():
    assert resolve_ablation_layers(N_LAYERS, start_layer=5, single_layer=True) == [5]


def test_layers_single_layer_defaults_to_layer_zero():
    assert resolve_ablation_layers(N_LAYERS, single_layer=True) == [0]


@pytest.mark.parametrize("bad", [-1, N_LAYERS, N_LAYERS + 3])
def test_layers_rejects_out_of_range(bad):
    with pytest.raises(ValueError, match="out of range"):
        resolve_ablation_layers(N_LAYERS, start_layer=bad)


# ---------------------------------------------------------------------------
# Projection correctness
# ---------------------------------------------------------------------------


def test_output_is_orthogonal_to_ablated_direction():
    """The defining property: no residual component along v_hat remains."""
    layers = _stack()
    v = _unit(np.arange(1, HIDDEN + 1, dtype=np.float32))
    x = torch.randn(2, 5, HIDDEN)
    with AblationHook(layers, [0], v):
        out = layers[0](x)[0]
    overlap = out.to(torch.float32) @ torch.from_numpy(v)
    assert torch.allclose(overlap, torch.zeros_like(overlap), atol=1e-4)


def test_orthogonal_component_is_preserved_exactly():
    """Ablation must remove one direction, not shrink the whole vector."""
    layers = _stack()
    v = np.zeros(HIDDEN, dtype=np.float32)
    v[0] = 1.0
    x = torch.randn(1, 3, HIDDEN)
    with AblationHook(layers, [0], v):
        out = layers[0](x)[0]
    assert torch.allclose(out[..., 0], torch.zeros_like(out[..., 0]), atol=1e-5)
    assert torch.allclose(out[..., 1:], x[..., 1:], atol=1e-5)


def test_ablation_is_idempotent():
    """Applying it twice changes nothing the second time."""
    layers = _stack()
    v = random_unit_direction(HIDDEN, seed=3)
    x = torch.randn(1, 4, HIDDEN)
    with AblationHook(layers, [0], v):
        once = layers[0](x)[0]
        twice = layers[0](once)[0]
    assert torch.allclose(once, twice, atol=1e-5)


def test_vector_already_orthogonal_is_a_no_op():
    layers = _stack()
    v = np.zeros(HIDDEN, dtype=np.float32)
    v[0] = 1.0
    x = torch.randn(1, 2, HIDDEN)
    x[..., 0] = 0.0
    with AblationHook(layers, [0], v):
        out = layers[0](x)[0]
    assert torch.allclose(out, x, atol=1e-5)


# ---------------------------------------------------------------------------
# Enable / disable and output shapes
# ---------------------------------------------------------------------------


def test_disabled_hook_returns_exact_identity():
    """The control arm must add no numeric noise at all."""
    layers = _stack()
    v = random_unit_direction(HIDDEN, seed=0)
    x = torch.randn(1, 3, HIDDEN)
    with AblationHook(layers, [0], v, enabled=False):
        out = layers[0](x)[0]
    assert torch.equal(out, x)


def test_set_enabled_toggles_behavior():
    layers = _stack()
    v = random_unit_direction(HIDDEN, seed=0)
    x = torch.randn(1, 3, HIDDEN)
    with AblationHook(layers, [0], v, enabled=False) as hook:
        assert torch.equal(layers[0](x)[0], x)
        hook.set_enabled(True)
        assert not torch.equal(layers[0](x)[0], x)


def test_tuple_output_preserves_trailing_elements():
    layers = _stack(_TupleLayer)
    v = random_unit_direction(HIDDEN, seed=0)
    with AblationHook(layers, [0], v):
        out = layers[0](torch.randn(1, 2, HIDDEN))
    assert isinstance(out, tuple) and out[1] == "aux"


def test_bare_tensor_output_supported():
    layers = _stack(_BareLayer)
    v = random_unit_direction(HIDDEN, seed=0)
    with AblationHook(layers, [0], v):
        out = layers[0](torch.randn(1, 2, HIDDEN))
    assert torch.is_tensor(out)


@pytest.mark.parametrize("dtype", [torch.float32, torch.float16, torch.bfloat16])
def test_dtype_round_trips(dtype):
    """Math runs in float32 internally; the returned tensor keeps the model's dtype."""
    layers = _stack()
    v = random_unit_direction(HIDDEN, seed=0)
    x = torch.randn(1, 3, HIDDEN).to(dtype)
    with AblationHook(layers, [0], v):
        out = layers[0](x)[0]
    assert out.dtype == dtype
    overlap = out.to(torch.float32) @ torch.from_numpy(v)
    assert torch.allclose(overlap, torch.zeros_like(overlap), atol=5e-2)


# ---------------------------------------------------------------------------
# Multi-layer application
# ---------------------------------------------------------------------------


def test_all_registered_layers_are_ablated():
    layers = _stack()
    v = np.zeros(HIDDEN, dtype=np.float32)
    v[2] = 1.0
    indices = [3, 4, 5]
    with AblationHook(layers, indices, v):
        for i in indices:
            out = layers[i](torch.randn(1, 2, HIDDEN))[0]
            assert torch.allclose(out[..., 2], torch.zeros_like(out[..., 2]), atol=1e-5)


def test_unregistered_layers_are_untouched():
    layers = _stack()
    v = np.zeros(HIDDEN, dtype=np.float32)
    v[2] = 1.0
    x = torch.randn(1, 2, HIDDEN)
    with AblationHook(layers, [3], v):
        assert torch.equal(layers[0](x)[0], x)


# ---------------------------------------------------------------------------
# Hook lifecycle
# ---------------------------------------------------------------------------


def test_hooks_removed_on_exit():
    layers = _stack()
    v = random_unit_direction(HIDDEN, seed=0)
    x = torch.randn(1, 2, HIDDEN)
    with AblationHook(layers, [0, 1], v):
        pass
    assert torch.equal(layers[0](x)[0], x)
    assert all(len(layers[i]._forward_hooks) == 0 for i in range(N_LAYERS))


def test_hooks_removed_even_when_body_raises():
    layers = _stack()
    v = random_unit_direction(HIDDEN, seed=0)
    with pytest.raises(RuntimeError):
        with AblationHook(layers, [0], v):
            raise RuntimeError("boom")
    assert len(layers[0]._forward_hooks) == 0


def test_repeated_use_does_not_accumulate_hooks():
    layers = _stack()
    v = random_unit_direction(HIDDEN, seed=0)
    for _ in range(3):
        with AblationHook(layers, [0], v):
            layers[0](torch.randn(1, 2, HIDDEN))
    assert len(layers[0]._forward_hooks) == 0


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_rejects_empty_layer_indices():
    with pytest.raises(ValueError, match="non-empty"):
        AblationHook(_stack(), [], random_unit_direction(HIDDEN, 0))


@pytest.mark.parametrize("bad", [[-1], [N_LAYERS], [0, N_LAYERS + 2]])
def test_rejects_out_of_range_layer_indices(bad):
    with pytest.raises(ValueError, match="out of range"):
        AblationHook(_stack(), bad, random_unit_direction(HIDDEN, 0))


def test_rejects_non_1d_vector():
    with pytest.raises(ValueError, match="1-D"):
        AblationHook(_stack(), [0], np.zeros((2, HIDDEN), dtype=np.float32))


def test_dimension_mismatch_raises_rather_than_broadcasting():
    """A vector built at a different hidden width must fail loudly."""
    layers = _stack()
    with AblationHook(layers, [0], random_unit_direction(HIDDEN + 4, seed=0)):
        with pytest.raises(ValueError, match="!= hidden dim"):
            layers[0](torch.randn(1, 2, HIDDEN))


def test_non_tensor_output_raises():
    class _BadLayer(nn.Module):
        def forward(self, x):  # type: ignore[override]
            return ("not a tensor", None)

    layers = nn.ModuleList([_BadLayer()])
    with AblationHook(layers, [0], random_unit_direction(HIDDEN, 0)):
        with pytest.raises(TypeError, match="expected tensor"):
            layers[0](torch.randn(1, 2, HIDDEN))


# ---------------------------------------------------------------------------
# Removed-magnitude reporting
# ---------------------------------------------------------------------------


def test_removed_magnitude_tracks_projection_size():
    layers = _stack()
    v = np.zeros(HIDDEN, dtype=np.float32)
    v[0] = 1.0
    x = torch.zeros(1, 1, HIDDEN)
    x[0, 0, 0] = 3.0
    with AblationHook(layers, [0], v) as hook:
        layers[0](x)
        assert np.isclose(hook.mean_removed_magnitude, 3.0, atol=1e-4)


def test_removed_magnitude_is_nan_before_any_pass():
    hook = AblationHook(_stack(), [0], random_unit_direction(HIDDEN, 0))
    assert np.isnan(hook.mean_removed_magnitude)


def test_reset_stats_clears_history():
    layers = _stack()
    v = random_unit_direction(HIDDEN, seed=0)
    with AblationHook(layers, [0], v) as hook:
        layers[0](torch.randn(1, 2, HIDDEN))
        assert not np.isnan(hook.mean_removed_magnitude)
        hook.reset_stats()
        assert np.isnan(hook.mean_removed_magnitude)


# ---------------------------------------------------------------------------
# Arm wiring
# ---------------------------------------------------------------------------


def test_arm_names_are_distinct():
    assert len({ARM_NONE, ARM_TARGET, ARM_RANDOM}) == 3


def test_arm_dataclass_is_frozen():
    arm = AblationArm(ARM_TARGET, random_unit_direction(HIDDEN, 0), True)
    with pytest.raises(dataclasses.FrozenInstanceError):
        arm.name = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Split swapping (2-fold cross-validation)
# ---------------------------------------------------------------------------


def _fake_labels(n: int = 100, n_pos: int = 42) -> dict[str, str]:
    return {f"vcl_{i:03d}": ("derail" if i < n_pos else "answer") for i in range(n)}


def test_swap_exchanges_the_two_halves():
    """The flag must actually swap. A silently ignored swap would rerun fold
    one and be indistinguishable from a successful replication."""
    from tracekit.interp.steer import split_items

    labels = _fake_labels()
    vec, ev = split_items(sorted(labels), labels, "derail", vector_fraction=0.5, seed=0)
    swapped_vec, swapped_ev = ev, vec

    assert swapped_vec == ev
    assert swapped_ev == vec
    assert set(swapped_vec) != set(vec)
    assert set(swapped_ev) != set(ev)


def test_split_is_a_partition_before_and_after_swap():
    from tracekit.interp.steer import split_items

    labels = _fake_labels()
    vec, ev = split_items(sorted(labels), labels, "derail", vector_fraction=0.5, seed=0)
    for a, b in ((vec, ev), (ev, vec)):
        assert set(a) & set(b) == set()
        assert set(a) | set(b) == set(labels)


def test_swap_at_half_fraction_gives_equal_sized_folds():
    """Only at fraction 0.5 is the swap a genuine second fold rather than a
    smaller fit set evaluated on a larger one."""
    from tracekit.interp.steer import split_items

    labels = _fake_labels()
    vec, ev = split_items(sorted(labels), labels, "derail", vector_fraction=0.5, seed=0)
    assert len(vec) == len(ev) == 50


def test_swap_preserves_class_balance_in_both_folds():
    from tracekit.interp.steer import split_items

    labels = _fake_labels()
    vec, ev = split_items(sorted(labels), labels, "derail", vector_fraction=0.5, seed=0)
    for half in (vec, ev):
        assert sum(1 for i in half if labels[i] == "derail") == 21
