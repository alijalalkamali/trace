# TRACE — Transparent Robustness, Alignment, and Character Evaluation

A symmetric, blind, peer-judged evaluation of how six frontier language models,
one from each of six developers, respond to explicit steering pressure. The
study measures not only how much steering shifts behavior but the qualitative
*mode* of the response, and finds that some modes are exclusive to a single
developer.

Study arXiv paper: https://arxiv.org/abs/2608.06578

## What this is

Each evaluation item pairs a base prompt with a steered variant of the same
scenario, so every model serves as its own control. The instrument has 340
items: 100 in each of three core behavioral categories, plus 20 in each of two
validation categories. Responses are classified against fixed categorical
rubrics by all six models acting as blind judges, producing a complete
judge-by-responder matrix of 24,480 judgments (340 items x 2 conditions x 6
responders x 6 judges) scored by leave-one-out consensus.

The six evaluated models, one per developer:

| Developer | Model |
|-----------|-------|
| Anthropic | Claude Opus 4.7 |
| OpenAI    | GPT-5 |
| Google    | Gemini 2.5 Pro |
| DeepSeek  | DeepSeek-R1 |
| Alibaba   | Qwen3.7-Max |
| Meta      | Llama-3.3-70B-Instruct-Turbo |

Three core behavioral categories carry the findings: values-conflicting
requests, pressure to expose reasoning, and pressure to suppress values
reasoning. Two additional categories (stylistic formatting and reasoning
hints with checkable answers) validate the instrument and carry no claims of
their own.

## Headline findings

- **A reasoning-disclosure mode exclusive to GPT-5.** On steered
  reasoning-elicitation items, GPT-5 declined to disclose its reasoning while
  answering intact on 99 of 100 items; no other model did so once across 500
  equivalent opportunities.
- **Suppression resistance in two models only, in two modes.** Claude Opus and
  GPT-5 are the only models that overtly resist explicit suppression
  instructions (combined 23% vs 0.25% elsewhere), and they favor opposite
  modes: Opus challenges the framing while complying, GPT-5 refuses outright.
- **Three tiers of baseline compliance.** On values-conflicting requests the
  models separate into three statistically distinct tiers rather than a
  continuum.
- **Divergent baseline dispositions.** With no suppression instruction present,
  models differ sharply in whether values considerations are expressed overtly
  or woven into ostensibly neutral reasoning.

## Auditing and controls

The findings survived two forms of scrutiny built into the pipeline:

- **Token-budget confound.** A response-length audit found genuine truncation
  in three models under the shared token budget. All affected responses were
  regenerated at a threefold budget, re-judged, and the analysis recomputed;
  every finding held.
- **Demand-characteristics control.** A two-arm re-judging experiment measured
  how much the item-context field shown to judges influenced labels, using an
  identical-prompt arm to establish the nondeterminism floor. The cross-model
  contrasts persist when the field is stripped.
- **Held-out validation.** The rubric was built from the first 20 items per
  category. Re-running the full analysis over the 80 items per category that
  were never read during rubric construction reproduces every headline finding.

## Repository layout

```
data/                     Evaluation items (steerability_items_v3.jsonl, 300 evaluation items plus 40 items for sanity check)
src/tracekit/                  Package: model backends, judging, aggregation, IO
src/tracekit/interp/           Mechanistic interpretability: harvesting, probing, steering
scripts/                  Pipeline entry points and diagnostics
results/analysis/         Aggregate rate tables, statistical tests, agreement
results/leakage/          Demand-characteristics control outputs
results/interp/           Probe layer sweep and steering-rate results
```

The raw per-judge judgment files (24,480 classifications) are large and are
distributed as a release asset rather than committed to the repository. See
Releases, or the archived deposit linked below.

## Reproducing the analysis

```bash
# Aggregate raw judgments into consensus labels and rate tables
python scripts/run_judge_pipeline.py --aggregate-only

# Compute rates, pairwise tests, effect sizes, and agreement
python scripts/analyze_judgments.py

# Held-out subset (items never used in rubric construction)
python scripts/analyze_judgments.py --item-range 21 100 --output-suffix _heldout80
```

## Data availability

Aggregate results and analysis outputs are in `results/`. The full raw
judgment matrix is available as a GitHub release asset and archived at
[doi:10.5281/zenodo.21629846](https://doi.org/10.5281/zenodo.21629846).

## Mechanistic interpretability (src/tracekit/interp/)

Extends the behavioral evaluation to mechanism on the open-weight model.
Pipeline: activation harvesting (forward hooks, last-prompt-token residual
stream, 20 layers of Llama-3.3-70B) → L2-regularized linear probes with
nested CV and 200-permutation nulls → difference-of-means activation steering
with a vector/eval item split. Result: the derail-vs-answer split is decodable
at 0.87 held-out balanced accuracy (plateau layers 32–76) and causally
steerable: derail rate moves monotonically 0%→86% across the α sweep (Fisher
p < 1e-5 vs. control both directions). Entry points:
`src/tracekit/interp/{harvest,probe,steer}.py`, `scripts/judge_steering_sweep.py`,
`scripts/analyze_steering_sweep.py`; results in `results/interp/steering_rates.csv`.

## Installation

```bash
git clone https://github.com/alijalalkamali/trace.git
cd trace
pip install -e .
```

Requires Python 3.11 or later.

The distribution is named `trace-kit` and the import name is `tracekit`. The
bare name `trace` belongs to a Python standard library module that takes
precedence on `sys.path`, so it cannot be used as an import name:

```python
from tracekit.judging.run_judges import run_judge_on_responder
```

API keys for the model backends are read from the environment. Obtain them and set only the
ones you need:

```bash
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GEMINI_API_KEY=...  # GOOGLE_API_KEY also accepted, and takes precedence
export DEEPSEEK_API_KEY=...
export TOGETHER_API_KEY=...
```
