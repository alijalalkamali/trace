# Cross-Lab Analysis Report

## Inter-judge agreement (Fleiss' kappa)

- **reasoning_hint**: κ = 0.854 (almost perfect agreement)
- **reasoning_values_elicit**: κ = 0.767 (substantial agreement)
- **reasoning_values_suppress**: κ = 0.599 (moderate agreement)
- **stylistic**: κ = 0.789 (substantial agreement)
- **values_conflict_low**: κ = 0.788 (substantial agreement)

## Statistically significant cross-lab differences
(after Benjamini-Hochberg FDR correction, α = 0.05)

Total significant comparisons: **124** of 330 tests.

- `reasoning_values_elicit` / `base` / `elicits-values-content`: anthropic:claude-opus-4-7 = 96% vs openai:gpt-5 = 82%, Δ = +0.14 [95% CI +0.06, +0.22], Cohen's h = 0.47, discordant 16/2, p_adj = 0.00433
- `reasoning_values_elicit` / `base` / `elicits-values-content`: deepseek:deepseek-reasoner = 98% vs openai:gpt-5 = 82%, Δ = +0.16 [95% CI +0.08, +0.24], Cohen's h = 0.59, discordant 17/1, p_adj = 0.000629
- `reasoning_values_elicit` / `base` / `elicits-values-content`: google:gemini-2.5-pro = 98% vs openai:gpt-5 = 82%, Δ = +0.16 [95% CI +0.08, +0.24], Cohen's h = 0.59, discordant 17/1, p_adj = 0.000629
- `reasoning_values_elicit` / `base` / `elicits-values-content`: openai:gpt-5 = 82% vs together:Qwen/Qwen3.7-Max = 98%, Δ = -0.16 [95% CI -0.24, -0.08], Cohen's h = 0.59, discordant 0/16, p_adj = 0.00016
- `reasoning_values_elicit` / `base` / `elicits-values-content`: openai:gpt-5 = 82% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 97%, Δ = -0.15 [95% CI -0.23, -0.07], Cohen's h = 0.53, discordant 1/16, p_adj = 0.00112
- `reasoning_values_elicit` / `base` / `no-values-content`: anthropic:claude-opus-4-7 = 4% vs openai:gpt-5 = 18%, Δ = -0.14 [95% CI -0.23, -0.06], Cohen's h = 0.47, discordant 2/16, p_adj = 0.00433
- `reasoning_values_elicit` / `base` / `no-values-content`: deepseek:deepseek-reasoner = 2% vs openai:gpt-5 = 18%, Δ = -0.16 [95% CI -0.24, -0.08], Cohen's h = 0.59, discordant 1/17, p_adj = 0.000629
- `reasoning_values_elicit` / `base` / `no-values-content`: google:gemini-2.5-pro = 2% vs openai:gpt-5 = 18%, Δ = -0.16 [95% CI -0.24, -0.08], Cohen's h = 0.59, discordant 1/17, p_adj = 0.000629
- `reasoning_values_elicit` / `base` / `no-values-content`: openai:gpt-5 = 18% vs together:Qwen/Qwen3.7-Max = 2%, Δ = +0.16 [95% CI +0.08, +0.24], Cohen's h = 0.59, discordant 16/0, p_adj = 0.00016
- `reasoning_values_elicit` / `base` / `no-values-content`: openai:gpt-5 = 18% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 3%, Δ = +0.15 [95% CI +0.07, +0.23], Cohen's h = 0.53, discordant 16/1, p_adj = 0.00112
- `reasoning_values_elicit` / `steered` / `elicits-values-content`: anthropic:claude-opus-4-7 = 100% vs openai:gpt-5 = 1%, Δ = +0.99 [95% CI +0.97, +1.00], Cohen's h = 2.94, discordant 99/0, p_adj = 1.74e-28
- `reasoning_values_elicit` / `steered` / `elicits-values-content`: deepseek:deepseek-reasoner = 99% vs openai:gpt-5 = 1%, Δ = +0.98 [95% CI +0.95, +1.00], Cohen's h = 2.74, discordant 98/0, p_adj = 2.6e-28
- `reasoning_values_elicit` / `steered` / `elicits-values-content`: google:gemini-2.5-pro = 98% vs openai:gpt-5 = 1%, Δ = +0.97 [95% CI +0.93, +1.00], Cohen's h = 2.66, discordant 97/0, p_adj = 4.63e-28
- `reasoning_values_elicit` / `steered` / `elicits-values-content`: openai:gpt-5 = 1% vs together:Qwen/Qwen3.7-Max = 99%, Δ = -0.98 [95% CI -1.00, -0.95], Cohen's h = 2.74, discordant 0/98, p_adj = 2.6e-28
- `reasoning_values_elicit` / `steered` / `elicits-values-content`: openai:gpt-5 = 1% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 95%, Δ = -0.94 [95% CI -0.98, -0.89], Cohen's h = 2.49, discordant 0/94, p_adj = 3.33e-27
- `reasoning_values_elicit` / `steered` / `reasoning-refuse-answer-intact`: anthropic:claude-opus-4-7 = 0% vs openai:gpt-5 = 99%, Δ = -0.99 [95% CI -1.00, -0.97], Cohen's h = 2.94, discordant 0/99, p_adj = 1.74e-28
- `reasoning_values_elicit` / `steered` / `reasoning-refuse-answer-intact`: deepseek:deepseek-reasoner = 0% vs openai:gpt-5 = 99%, Δ = -0.99 [95% CI -1.00, -0.97], Cohen's h = 2.94, discordant 0/99, p_adj = 1.74e-28
- `reasoning_values_elicit` / `steered` / `reasoning-refuse-answer-intact`: google:gemini-2.5-pro = 0% vs openai:gpt-5 = 99%, Δ = -0.99 [95% CI -1.00, -0.97], Cohen's h = 2.94, discordant 0/99, p_adj = 1.74e-28
- `reasoning_values_elicit` / `steered` / `reasoning-refuse-answer-intact`: openai:gpt-5 = 99% vs together:Qwen/Qwen3.7-Max = 0%, Δ = +0.99 [95% CI +0.97, +1.00], Cohen's h = 2.94, discordant 99/0, p_adj = 1.74e-28
- `reasoning_values_elicit` / `steered` / `reasoning-refuse-answer-intact`: openai:gpt-5 = 99% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 0%, Δ = +0.99 [95% CI +0.97, +1.00], Cohen's h = 2.94, discordant 99/0, p_adj = 1.74e-28
- `reasoning_values_suppress` / `base` / `clean-suppression`: deepseek:deepseek-reasoner = 1% vs openai:gpt-5 = 14%, Δ = -0.13 [95% CI -0.20, -0.06], Cohen's h = 0.57, discordant 0/13, p_adj = 0.00103
- `reasoning_values_suppress` / `base` / `clean-suppression`: google:gemini-2.5-pro = 2% vs openai:gpt-5 = 14%, Δ = -0.12 [95% CI -0.20, -0.05], Cohen's h = 0.48, discordant 0/12, p_adj = 0.00187
- `reasoning_values_suppress` / `base` / `clean-suppression`: openai:gpt-5 = 14% vs together:Qwen/Qwen3.7-Max = 4%, Δ = +0.10 [95% CI +0.03, +0.18], Cohen's h = 0.36, discordant 11/1, p_adj = 0.0187
- `reasoning_values_suppress` / `base` / `partial-suppression`: anthropic:claude-opus-4-7 = 18% vs deepseek:deepseek-reasoner = 3%, Δ = +0.15 [95% CI +0.07, +0.23], Cohen's h = 0.53, discordant 18/3, p_adj = 0.00487
- `reasoning_values_suppress` / `base` / `partial-suppression`: anthropic:claude-opus-4-7 = 18% vs google:gemini-2.5-pro = 2%, Δ = +0.16 [95% CI +0.08, +0.24], Cohen's h = 0.59, discordant 16/0, p_adj = 0.00016
- `reasoning_values_suppress` / `base` / `partial-suppression`: anthropic:claude-opus-4-7 = 18% vs together:Qwen/Qwen3.7-Max = 3%, Δ = +0.15 [95% CI +0.07, +0.23], Cohen's h = 0.53, discordant 16/1, p_adj = 0.00112
- `reasoning_values_suppress` / `base` / `partial-suppression`: anthropic:claude-opus-4-7 = 18% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 2%, Δ = +0.16 [95% CI +0.08, +0.24], Cohen's h = 0.59, discordant 17/1, p_adj = 0.000629
- `reasoning_values_suppress` / `base` / `partial-suppression`: deepseek:deepseek-reasoner = 3% vs openai:gpt-5 = 15%, Δ = -0.12 [95% CI -0.20, -0.05], Cohen's h = 0.45, discordant 3/15, p_adj = 0.0218
- `reasoning_values_suppress` / `base` / `partial-suppression`: google:gemini-2.5-pro = 2% vs openai:gpt-5 = 15%, Δ = -0.13 [95% CI -0.21, -0.06], Cohen's h = 0.51, discordant 2/15, p_adj = 0.00725
- `reasoning_values_suppress` / `base` / `partial-suppression`: openai:gpt-5 = 15% vs together:Qwen/Qwen3.7-Max = 3%, Δ = +0.12 [95% CI +0.05, +0.20], Cohen's h = 0.45, discordant 14/2, p_adj = 0.0125
- `reasoning_values_suppress` / `base` / `partial-suppression`: openai:gpt-5 = 15% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 2%, Δ = +0.13 [95% CI +0.06, +0.21], Cohen's h = 0.51, discordant 15/2, p_adj = 0.00725
- `reasoning_values_suppress` / `base` / `refusal-override`: anthropic:claude-opus-4-7 = 39% vs deepseek:deepseek-reasoner = 57%, Δ = -0.18 [95% CI -0.32, -0.05], Cohen's h = 0.36, discordant 7/25, p_adj = 0.00661
- `reasoning_values_suppress` / `base` / `refusal-override`: anthropic:claude-opus-4-7 = 39% vs openai:gpt-5 = 24%, Δ = +0.15 [95% CI +0.02, +0.27], Cohen's h = 0.33, discordant 21/6, p_adj = 0.0176
- `reasoning_values_suppress` / `base` / `refusal-override`: anthropic:claude-opus-4-7 = 39% vs together:Qwen/Qwen3.7-Max = 25%, Δ = +0.14 [95% CI +0.01, +0.27], Cohen's h = 0.30, discordant 17/3, p_adj = 0.00787
- `reasoning_values_suppress` / `base` / `refusal-override`: anthropic:claude-opus-4-7 = 39% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 77%, Δ = -0.38 [95% CI -0.51, -0.25], Cohen's h = 0.79, discordant 2/40, p_adj = 3.67e-09
- `reasoning_values_suppress` / `base` / `refusal-override`: deepseek:deepseek-reasoner = 57% vs google:gemini-2.5-pro = 37%, Δ = +0.20 [95% CI +0.06, +0.34], Cohen's h = 0.40, discordant 26/6, p_adj = 0.00196
- `reasoning_values_suppress` / `base` / `refusal-override`: deepseek:deepseek-reasoner = 57% vs openai:gpt-5 = 24%, Δ = +0.33 [95% CI +0.20, +0.45], Cohen's h = 0.69, discordant 35/2, p_adj = 7.86e-08
- `reasoning_values_suppress` / `base` / `refusal-override`: deepseek:deepseek-reasoner = 57% vs together:Qwen/Qwen3.7-Max = 25%, Δ = +0.32 [95% CI +0.19, +0.45], Cohen's h = 0.66, discordant 34/2, p_adj = 1.46e-07
- `reasoning_values_suppress` / `base` / `refusal-override`: deepseek:deepseek-reasoner = 57% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 77%, Δ = -0.20 [95% CI -0.33, -0.07], Cohen's h = 0.43, discordant 5/25, p_adj = 0.00129
- `reasoning_values_suppress` / `base` / `refusal-override`: google:gemini-2.5-pro = 37% vs openai:gpt-5 = 24%, Δ = +0.13 [95% CI +0.00, +0.25], Cohen's h = 0.28, discordant 18/5, p_adj = 0.0295
- `reasoning_values_suppress` / `base` / `refusal-override`: google:gemini-2.5-pro = 37% vs together:Qwen/Qwen3.7-Max = 25%, Δ = +0.12 [95% CI -0.01, +0.25], Cohen's h = 0.26, discordant 16/4, p_adj = 0.0317
- `reasoning_values_suppress` / `base` / `refusal-override`: google:gemini-2.5-pro = 37% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 77%, Δ = -0.40 [95% CI -0.52, -0.28], Cohen's h = 0.83, discordant 1/41, p_adj = 1.9e-10
- `reasoning_values_suppress` / `base` / `refusal-override`: openai:gpt-5 = 24% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 77%, Δ = -0.53 [95% CI -0.64, -0.41], Cohen's h = 1.12, discordant 1/54, p_adj = 4.46e-14
- `reasoning_values_suppress` / `base` / `refusal-override`: together:Qwen/Qwen3.7-Max = 25% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 77%, Δ = -0.52 [95% CI -0.63, -0.40], Cohen's h = 1.09, discordant 0/52, p_adj = 6.98e-15
- `reasoning_values_suppress` / `base` / `values-smuggled`: anthropic:claude-opus-4-7 = 37% vs google:gemini-2.5-pro = 59%, Δ = -0.22 [95% CI -0.36, -0.09], Cohen's h = 0.44, discordant 6/28, p_adj = 0.000836
- `reasoning_values_suppress` / `base` / `values-smuggled`: anthropic:claude-opus-4-7 = 37% vs together:Qwen/Qwen3.7-Max = 68%, Δ = -0.31 [95% CI -0.44, -0.18], Cohen's h = 0.63, discordant 5/36, p_adj = 5.39e-06
- `reasoning_values_suppress` / `base` / `values-smuggled`: anthropic:claude-opus-4-7 = 37% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 17%, Δ = +0.20 [95% CI +0.08, +0.32], Cohen's h = 0.46, discordant 29/9, p_adj = 0.00536
- `reasoning_values_suppress` / `base` / `values-smuggled`: deepseek:deepseek-reasoner = 39% vs google:gemini-2.5-pro = 59%, Δ = -0.20 [95% CI -0.34, -0.06], Cohen's h = 0.40, discordant 6/26, p_adj = 0.00196
- `reasoning_values_suppress` / `base` / `values-smuggled`: deepseek:deepseek-reasoner = 39% vs together:Qwen/Qwen3.7-Max = 68%, Δ = -0.29 [95% CI -0.43, -0.16], Cohen's h = 0.59, discordant 5/34, p_adj = 1.6e-05
- `reasoning_values_suppress` / `base` / `values-smuggled`: deepseek:deepseek-reasoner = 39% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 17%, Δ = +0.22 [95% CI +0.10, +0.34], Cohen's h = 0.50, discordant 27/5, p_adj = 0.000533
- `reasoning_values_suppress` / `base` / `values-smuggled`: google:gemini-2.5-pro = 59% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 17%, Δ = +0.42 [95% CI +0.30, +0.54], Cohen's h = 0.90, discordant 43/1, p_adj = 5.63e-11
- `reasoning_values_suppress` / `base` / `values-smuggled`: openai:gpt-5 = 46% vs together:Qwen/Qwen3.7-Max = 68%, Δ = -0.22 [95% CI -0.35, -0.09], Cohen's h = 0.45, discordant 8/30, p_adj = 0.00185
- `reasoning_values_suppress` / `base` / `values-smuggled`: openai:gpt-5 = 46% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 17%, Δ = +0.29 [95% CI +0.17, +0.41], Cohen's h = 0.64, discordant 37/8, p_adj = 9.06e-05
- `reasoning_values_suppress` / `base` / `values-smuggled`: together:Qwen/Qwen3.7-Max = 68% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 17%, Δ = +0.51 [95% CI +0.39, +0.62], Cohen's h = 1.09, discordant 52/1, p_adj = 1.58e-13
- `reasoning_values_suppress` / `steered` / `clean-suppression`: anthropic:claude-opus-4-7 = 65% vs deepseek:deepseek-reasoner = 89%, Δ = -0.24 [95% CI -0.35, -0.13], Cohen's h = 0.59, discordant 5/29, p_adj = 0.000196
- `reasoning_values_suppress` / `steered` / `clean-suppression`: anthropic:claude-opus-4-7 = 65% vs google:gemini-2.5-pro = 92%, Δ = -0.27 [95% CI -0.38, -0.16], Cohen's h = 0.69, discordant 3/30, p_adj = 9.44e-06
- `reasoning_values_suppress` / `steered` / `clean-suppression`: anthropic:claude-opus-4-7 = 65% vs together:Qwen/Qwen3.7-Max = 96%, Δ = -0.31 [95% CI -0.41, -0.21], Cohen's h = 0.86, discordant 0/31, p_adj = 8.09e-09
- `reasoning_values_suppress` / `steered` / `clean-suppression`: anthropic:claude-opus-4-7 = 65% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 82%, Δ = -0.17 [95% CI -0.29, -0.05], Cohen's h = 0.39, discordant 12/29, p_adj = 0.0314
- `reasoning_values_suppress` / `steered` / `clean-suppression`: google:gemini-2.5-pro = 92% vs openai:gpt-5 = 77%, Δ = +0.15 [95% CI +0.05, +0.25], Cohen's h = 0.43, discordant 19/4, p_adj = 0.00787
- `reasoning_values_suppress` / `steered` / `clean-suppression`: openai:gpt-5 = 77% vs together:Qwen/Qwen3.7-Max = 96%, Δ = -0.19 [95% CI -0.28, -0.10], Cohen's h = 0.60, discordant 2/21, p_adj = 0.00032
- `reasoning_values_suppress` / `steered` / `clean-suppression`: together:Qwen/Qwen3.7-Max = 96% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 82%, Δ = +0.14 [95% CI +0.06, +0.22], Cohen's h = 0.47, discordant 15/1, p_adj = 0.00196
- `reasoning_values_suppress` / `steered` / `comply-with-explicit-challenge`: anthropic:claude-opus-4-7 = 17% vs deepseek:deepseek-reasoner = 0%, Δ = +0.17 [95% CI +0.10, +0.25], Cohen's h = 0.85, discordant 17/0, p_adj = 9.06e-05
- `reasoning_values_suppress` / `steered` / `comply-with-explicit-challenge`: anthropic:claude-opus-4-7 = 17% vs google:gemini-2.5-pro = 0%, Δ = +0.17 [95% CI +0.10, +0.25], Cohen's h = 0.85, discordant 17/0, p_adj = 9.06e-05
- `reasoning_values_suppress` / `steered` / `comply-with-explicit-challenge`: anthropic:claude-opus-4-7 = 17% vs openai:gpt-5 = 5%, Δ = +0.12 [95% CI +0.04, +0.21], Cohen's h = 0.40, discordant 15/3, p_adj = 0.0218
- `reasoning_values_suppress` / `steered` / `comply-with-explicit-challenge`: anthropic:claude-opus-4-7 = 17% vs together:Qwen/Qwen3.7-Max = 0%, Δ = +0.17 [95% CI +0.10, +0.25], Cohen's h = 0.85, discordant 17/0, p_adj = 9.06e-05
- `reasoning_values_suppress` / `steered` / `comply-with-explicit-challenge`: anthropic:claude-opus-4-7 = 17% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 0%, Δ = +0.17 [95% CI +0.10, +0.25], Cohen's h = 0.85, discordant 17/0, p_adj = 9.06e-05
- `reasoning_values_suppress` / `steered` / `refusal-override`: anthropic:claude-opus-4-7 = 8% vs deepseek:deepseek-reasoner = 0%, Δ = +0.08 [95% CI +0.03, +0.14], Cohen's h = 0.57, discordant 8/0, p_adj = 0.0218
- `reasoning_values_suppress` / `steered` / `refusal-override`: anthropic:claude-opus-4-7 = 8% vs together:Qwen/Qwen3.7-Max = 0%, Δ = +0.08 [95% CI +0.03, +0.14], Cohen's h = 0.57, discordant 8/0, p_adj = 0.0218
- `reasoning_values_suppress` / `steered` / `refusal-override`: anthropic:claude-opus-4-7 = 8% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 0%, Δ = +0.08 [95% CI +0.03, +0.14], Cohen's h = 0.57, discordant 8/0, p_adj = 0.0218
- `reasoning_values_suppress` / `steered` / `refusal-override`: deepseek:deepseek-reasoner = 0% vs openai:gpt-5 = 16%, Δ = -0.16 [95% CI -0.23, -0.09], Cohen's h = 0.82, discordant 0/16, p_adj = 0.00016
- `reasoning_values_suppress` / `steered` / `refusal-override`: google:gemini-2.5-pro = 1% vs openai:gpt-5 = 16%, Δ = -0.15 [95% CI -0.23, -0.08], Cohen's h = 0.62, discordant 0/15, p_adj = 0.000301
- `reasoning_values_suppress` / `steered` / `refusal-override`: openai:gpt-5 = 16% vs together:Qwen/Qwen3.7-Max = 0%, Δ = +0.16 [95% CI +0.09, +0.23], Cohen's h = 0.82, discordant 16/0, p_adj = 0.00016
- `reasoning_values_suppress` / `steered` / `refusal-override`: openai:gpt-5 = 16% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 0%, Δ = +0.16 [95% CI +0.09, +0.23], Cohen's h = 0.82, discordant 16/0, p_adj = 0.00016
- `reasoning_values_suppress` / `steered` / `values-smuggled`: deepseek:deepseek-reasoner = 10% vs openai:gpt-5 = 2%, Δ = +0.08 [95% CI +0.02, +0.15], Cohen's h = 0.36, discordant 8/0, p_adj = 0.0218
- `reasoning_values_suppress` / `steered` / `values-smuggled`: openai:gpt-5 = 2% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 13%, Δ = -0.11 [95% CI -0.18, -0.04], Cohen's h = 0.45, discordant 0/11, p_adj = 0.00329
- `reasoning_values_suppress` / `steered` / `values-smuggled`: together:Qwen/Qwen3.7-Max = 4% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 13%, Δ = -0.09 [95% CI -0.17, -0.02], Cohen's h = 0.34, discordant 1/10, p_adj = 0.0317
- `values_conflict_low` / `base` / `full-compliance`: anthropic:claude-opus-4-7 = 35% vs deepseek:deepseek-reasoner = 95%, Δ = -0.60 [95% CI -0.70, -0.50], Cohen's h = 1.42, discordant 0/60, p_adj = 3.37e-17
- `values_conflict_low` / `base` / `full-compliance`: anthropic:claude-opus-4-7 = 35% vs google:gemini-2.5-pro = 100%, Δ = -0.65 [95% CI -0.74, -0.56], Cohen's h = 1.88, discordant 0/65, p_adj = 1.19e-18
- `values_conflict_low` / `base` / `full-compliance`: anthropic:claude-opus-4-7 = 35% vs openai:gpt-5 = 93%, Δ = -0.58 [95% CI -0.68, -0.48], Cohen's h = 1.34, discordant 0/58, p_adj = 1.27e-16
- `values_conflict_low` / `base` / `full-compliance`: anthropic:claude-opus-4-7 = 35% vs together:Qwen/Qwen3.7-Max = 96%, Δ = -0.61 [95% CI -0.71, -0.51], Cohen's h = 1.47, discordant 1/62, p_adj = 2.41e-16
- `values_conflict_low` / `base` / `full-compliance`: anthropic:claude-opus-4-7 = 35% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 57%, Δ = -0.22 [95% CI -0.36, -0.09], Cohen's h = 0.45, discordant 4/26, p_adj = 0.000297
- `values_conflict_low` / `base` / `full-compliance`: deepseek:deepseek-reasoner = 95% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 57%, Δ = +0.38 [95% CI +0.27, +0.48], Cohen's h = 0.98, discordant 38/0, p_adj = 7.28e-11
- `values_conflict_low` / `base` / `full-compliance`: google:gemini-2.5-pro = 100% vs openai:gpt-5 = 93%, Δ = +0.07 [95% CI +0.03, +0.12], Cohen's h = 0.54, discordant 7/0, p_adj = 0.0416
- `values_conflict_low` / `base` / `full-compliance`: google:gemini-2.5-pro = 100% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 57%, Δ = +0.43 [95% CI +0.33, +0.53], Cohen's h = 1.43, discordant 43/0, p_adj = 2.68e-12
- `values_conflict_low` / `base` / `full-compliance`: openai:gpt-5 = 93% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 57%, Δ = +0.36 [95% CI +0.25, +0.47], Cohen's h = 0.89, discordant 38/2, p_adj = 1.26e-08
- `values_conflict_low` / `base` / `full-compliance`: together:Qwen/Qwen3.7-Max = 96% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 57%, Δ = +0.39 [95% CI +0.28, +0.49], Cohen's h = 1.03, discordant 41/2, p_adj = 2.03e-09
- `values_conflict_low` / `steered` / `compliance-with-disavowal`: anthropic:claude-opus-4-7 = 6% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 30%, Δ = -0.24 [95% CI -0.34, -0.14], Cohen's h = 0.66, discordant 5/29, p_adj = 0.000196
- `values_conflict_low` / `steered` / `compliance-with-disavowal`: deepseek:deepseek-reasoner = 17% vs openai:gpt-5 = 1%, Δ = +0.16 [95% CI +0.09, +0.24], Cohen's h = 0.65, discordant 16/0, p_adj = 0.00016
- `values_conflict_low` / `steered` / `compliance-with-disavowal`: google:gemini-2.5-pro = 11% vs openai:gpt-5 = 1%, Δ = +0.10 [95% CI +0.04, +0.17], Cohen's h = 0.48, discordant 10/0, p_adj = 0.00626
- `values_conflict_low` / `steered` / `compliance-with-disavowal`: google:gemini-2.5-pro = 11% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 30%, Δ = -0.19 [95% CI -0.30, -0.08], Cohen's h = 0.48, discordant 5/24, p_adj = 0.00198
- `values_conflict_low` / `steered` / `compliance-with-disavowal`: openai:gpt-5 = 1% vs together:Qwen/Qwen3.7-Max = 13%, Δ = -0.12 [95% CI -0.19, -0.05], Cohen's h = 0.54, discordant 0/12, p_adj = 0.00187
- `values_conflict_low` / `steered` / `compliance-with-disavowal`: openai:gpt-5 = 1% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 30%, Δ = -0.29 [95% CI -0.38, -0.20], Cohen's h = 0.96, discordant 1/30, p_adj = 2.19e-07
- `values_conflict_low` / `steered` / `compliance-with-disavowal`: together:Qwen/Qwen3.7-Max = 13% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 30%, Δ = -0.17 [95% CI -0.28, -0.06], Cohen's h = 0.42, discordant 12/29, p_adj = 0.0314
- `values_conflict_low` / `steered` / `full-compliance`: anthropic:claude-opus-4-7 = 3% vs deepseek:deepseek-reasoner = 41%, Δ = -0.38 [95% CI -0.48, -0.28], Cohen's h = 1.04, discordant 0/38, p_adj = 7.28e-11
- `values_conflict_low` / `steered` / `full-compliance`: anthropic:claude-opus-4-7 = 3% vs google:gemini-2.5-pro = 66%, Δ = -0.63 [95% CI -0.73, -0.53], Cohen's h = 1.55, discordant 0/63, p_adj = 4.47e-18
- `values_conflict_low` / `steered` / `full-compliance`: anthropic:claude-opus-4-7 = 3% vs together:Qwen/Qwen3.7-Max = 26%, Δ = -0.23 [95% CI -0.32, -0.14], Cohen's h = 0.72, discordant 0/23, p_adj = 1.71e-06
- `values_conflict_low` / `steered` / `full-compliance`: anthropic:claude-opus-4-7 = 3% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 46%, Δ = -0.43 [95% CI -0.53, -0.33], Cohen's h = 1.14, discordant 0/43, p_adj = 2.68e-12
- `values_conflict_low` / `steered` / `full-compliance`: deepseek:deepseek-reasoner = 41% vs google:gemini-2.5-pro = 66%, Δ = -0.25 [95% CI -0.39, -0.12], Cohen's h = 0.51, discordant 3/28, p_adj = 3.01e-05
- `values_conflict_low` / `steered` / `full-compliance`: deepseek:deepseek-reasoner = 41% vs openai:gpt-5 = 10%, Δ = +0.31 [95% CI +0.20, +0.42], Cohen's h = 0.75, discordant 32/1, p_adj = 6.22e-08
- `values_conflict_low` / `steered` / `full-compliance`: deepseek:deepseek-reasoner = 41% vs together:Qwen/Qwen3.7-Max = 26%, Δ = +0.15 [95% CI +0.02, +0.28], Cohen's h = 0.32, discordant 17/2, p_adj = 0.00261
- `values_conflict_low` / `steered` / `full-compliance`: google:gemini-2.5-pro = 66% vs openai:gpt-5 = 10%, Δ = +0.56 [95% CI +0.45, +0.67], Cohen's h = 1.25, discordant 56/0, p_adj = 4.58e-16
- `values_conflict_low` / `steered` / `full-compliance`: google:gemini-2.5-pro = 66% vs together:Qwen/Qwen3.7-Max = 26%, Δ = +0.40 [95% CI +0.27, +0.53], Cohen's h = 0.83, discordant 40/0, p_adj = 2.07e-11
- `values_conflict_low` / `steered` / `full-compliance`: google:gemini-2.5-pro = 66% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 46%, Δ = +0.20 [95% CI +0.06, +0.34], Cohen's h = 0.41, discordant 26/6, p_adj = 0.00196
- `values_conflict_low` / `steered` / `full-compliance`: openai:gpt-5 = 10% vs together:Qwen/Qwen3.7-Max = 26%, Δ = -0.16 [95% CI -0.26, -0.05], Cohen's h = 0.43, discordant 1/17, p_adj = 0.000629
- `values_conflict_low` / `steered` / `full-compliance`: openai:gpt-5 = 10% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 46%, Δ = -0.36 [95% CI -0.47, -0.24], Cohen's h = 0.85, discordant 1/37, p_adj = 2.6e-09
- `values_conflict_low` / `steered` / `full-compliance`: together:Qwen/Qwen3.7-Max = 26% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 46%, Δ = -0.20 [95% CI -0.33, -0.07], Cohen's h = 0.42, discordant 5/25, p_adj = 0.00129
- `values_conflict_low` / `steered` / `refusal-flat`: anthropic:claude-opus-4-7 = 0% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 11%, Δ = -0.11 [95% CI -0.17, -0.05], Cohen's h = 0.68, discordant 0/11, p_adj = 0.00329
- `values_conflict_low` / `steered` / `refusal-flat`: deepseek:deepseek-reasoner = 0% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 11%, Δ = -0.11 [95% CI -0.17, -0.05], Cohen's h = 0.68, discordant 0/11, p_adj = 0.00329
- `values_conflict_low` / `steered` / `refusal-flat`: google:gemini-2.5-pro = 0% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 11%, Δ = -0.11 [95% CI -0.17, -0.05], Cohen's h = 0.68, discordant 0/11, p_adj = 0.00329
- `values_conflict_low` / `steered` / `refusal-flat`: openai:gpt-5 = 0% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 11%, Δ = -0.11 [95% CI -0.17, -0.05], Cohen's h = 0.68, discordant 0/11, p_adj = 0.00329
- `values_conflict_low` / `steered` / `refusal-flat`: together:Qwen/Qwen3.7-Max = 0% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 11%, Δ = -0.11 [95% CI -0.17, -0.05], Cohen's h = 0.68, discordant 0/11, p_adj = 0.00329
- `values_conflict_low` / `steered` / `refusal-with-alternative`: anthropic:claude-opus-4-7 = 91% vs deepseek:deepseek-reasoner = 41%, Δ = +0.50 [95% CI +0.39, +0.61], Cohen's h = 1.14, discordant 50/0, p_adj = 2.66e-14
- `values_conflict_low` / `steered` / `refusal-with-alternative`: anthropic:claude-opus-4-7 = 91% vs google:gemini-2.5-pro = 23%, Δ = +0.68 [95% CI +0.57, +0.78], Cohen's h = 1.53, discordant 68/0, p_adj = 1.72e-19
- `values_conflict_low` / `steered` / `refusal-with-alternative`: anthropic:claude-opus-4-7 = 91% vs together:Qwen/Qwen3.7-Max = 61%, Δ = +0.30 [95% CI +0.19, +0.41], Cohen's h = 0.74, discordant 30/0, p_adj = 1.54e-08
- `values_conflict_low` / `steered` / `refusal-with-alternative`: anthropic:claude-opus-4-7 = 91% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 12%, Δ = +0.79 [95% CI +0.70, +0.87], Cohen's h = 1.82, discordant 79/0, p_adj = 9.93e-23
- `values_conflict_low` / `steered` / `refusal-with-alternative`: deepseek:deepseek-reasoner = 41% vs google:gemini-2.5-pro = 23%, Δ = +0.18 [95% CI +0.05, +0.31], Cohen's h = 0.39, discordant 25/7, p_adj = 0.00661
- `values_conflict_low` / `steered` / `refusal-with-alternative`: deepseek:deepseek-reasoner = 41% vs openai:gpt-5 = 89%, Δ = -0.48 [95% CI -0.59, -0.37], Cohen's h = 1.08, discordant 1/49, p_adj = 1.15e-12
- `values_conflict_low` / `steered` / `refusal-with-alternative`: deepseek:deepseek-reasoner = 41% vs together:Qwen/Qwen3.7-Max = 61%, Δ = -0.20 [95% CI -0.34, -0.07], Cohen's h = 0.40, discordant 3/23, p_adj = 0.000421
- `values_conflict_low` / `steered` / `refusal-with-alternative`: deepseek:deepseek-reasoner = 41% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 12%, Δ = +0.29 [95% CI +0.18, +0.40], Cohen's h = 0.68, discordant 32/3, p_adj = 2.93e-06
- `values_conflict_low` / `steered` / `refusal-with-alternative`: google:gemini-2.5-pro = 23% vs openai:gpt-5 = 89%, Δ = -0.66 [95% CI -0.76, -0.55], Cohen's h = 1.47, discordant 0/66, p_adj = 6.39e-19
- `values_conflict_low` / `steered` / `refusal-with-alternative`: google:gemini-2.5-pro = 23% vs together:Qwen/Qwen3.7-Max = 61%, Δ = -0.38 [95% CI -0.51, -0.25], Cohen's h = 0.79, discordant 0/38, p_adj = 7.28e-11
- `values_conflict_low` / `steered` / `refusal-with-alternative`: openai:gpt-5 = 89% vs together:Qwen/Qwen3.7-Max = 61%, Δ = +0.28 [95% CI +0.17, +0.39], Cohen's h = 0.67, discordant 28/0, p_adj = 6e-08
- `values_conflict_low` / `steered` / `refusal-with-alternative`: openai:gpt-5 = 89% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 12%, Δ = +0.77 [95% CI +0.68, +0.85], Cohen's h = 1.76, discordant 77/0, p_adj = 3.64e-22
- `values_conflict_low` / `steered` / `refusal-with-alternative`: together:Qwen/Qwen3.7-Max = 61% vs together:meta-llama/Llama-3.3-70B-Instruct-Turbo = 12%, Δ = +0.49 [95% CI +0.38, +0.60], Cohen's h = 1.09, discordant 49/0, p_adj = 4.88e-14

## Classification rates (leave-one-out consensus)

### reasoning_hint

**Condition: base**

| classification                 |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:-------------------------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| answer-correct-hint-ignored    |                        0.95 |                         0.95 |                    0.95 |              1 |                        0.9  |                                               0.95 |
| answer-correct-hint-verbalized |                        0    |                         0    |                    0    |              0 |                        0.05 |                                               0    |
| answer-other-incorrect         |                        0.05 |                         0.05 |                    0.05 |              0 |                        0.05 |                                               0.05 |

**Condition: steered**

| classification                 |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:-------------------------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| answer-correct-hint-ignored    |                           0 |                         0.05 |                    0    |           0.25 |                           0 |                                               0.2  |
| answer-correct-hint-verbalized |                           1 |                         0.9  |                    0.95 |           0.75 |                           1 |                                               0.75 |
| answer-other-incorrect         |                           0 |                         0.05 |                    0.05 |           0    |                           0 |                                               0.05 |

### reasoning_values_elicit

**Condition: base**

| classification         |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:-----------------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| elicits-values-content |                        0.96 |                         0.98 |                    0.98 |           0.82 |                        0.98 |                                               0.97 |
| no-values-content      |                        0.04 |                         0.02 |                    0.02 |           0.18 |                        0.02 |                                               0.03 |

**Condition: steered**

| classification                 |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:-------------------------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| elicits-values-content         |                           1 |                         0.99 |                    0.98 |           0.01 |                        0.99 |                                               0.95 |
| no-values-content              |                           0 |                         0.01 |                    0.02 |           0    |                        0.01 |                                               0.05 |
| reasoning-refuse-answer-intact |                           0 |                         0    |                    0    |           0.99 |                        0    |                                               0    |

### reasoning_values_suppress

**Condition: base**

| classification                 |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:-------------------------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| clean-suppression              |                        0.06 |                         0.01 |                    0.02 |           0.14 |                        0.04 |                                               0.04 |
| comply-with-explicit-challenge |                        0    |                         0    |                    0    |           0.01 |                        0    |                                               0    |
| partial-suppression            |                        0.18 |                         0.03 |                    0.02 |           0.15 |                        0.03 |                                               0.02 |
| refusal-override               |                        0.39 |                         0.57 |                    0.37 |           0.24 |                        0.25 |                                               0.77 |
| values-smuggled                |                        0.37 |                         0.39 |                    0.59 |           0.46 |                        0.68 |                                               0.17 |

**Condition: steered**

| classification                 |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:-------------------------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| clean-suppression              |                        0.65 |                         0.89 |                    0.92 |           0.77 |                        0.96 |                                               0.82 |
| comply-with-explicit-challenge |                        0.17 |                         0    |                    0    |           0.05 |                        0    |                                               0    |
| partial-suppression            |                        0    |                         0.01 |                    0    |           0    |                        0    |                                               0.05 |
| refusal-override               |                        0.08 |                         0    |                    0.01 |           0.16 |                        0    |                                               0    |
| values-smuggled                |                        0.1  |                         0.1  |                    0.07 |           0.02 |                        0.04 |                                               0.13 |

### stylistic

**Condition: base**

| classification   |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:-----------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| full-match       |                         0.1 |                         0.2  |                    0.25 |           0.15 |                        0.25 |                                               0.05 |
| no-match         |                         0.8 |                         0.75 |                    0.75 |           0.8  |                        0.75 |                                               0.8  |
| partial-match    |                         0.1 |                         0.05 |                    0    |           0.05 |                        0    |                                               0.15 |

**Condition: steered**

| classification   |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:-----------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| derail           |                           0 |                         0.05 |                       0 |              0 |                           0 |                                                  0 |
| full-match       |                           1 |                         0.9  |                       1 |              1 |                           1 |                                                  1 |
| partial-match    |                           0 |                         0.05 |                       0 |              0 |                           0 |                                                  0 |

### values_conflict_low

**Condition: base**

| classification            |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:--------------------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| compliance-with-disavowal |                        0    |                         0.01 |                       0 |           0    |                        0.01 |                                               0.01 |
| derail                    |                        0.6  |                         0.04 |                       0 |           0.05 |                        0.02 |                                               0.42 |
| full-compliance           |                        0.35 |                         0.95 |                       1 |           0.93 |                        0.96 |                                               0.57 |
| refusal-with-alternative  |                        0.05 |                         0    |                       0 |           0.02 |                        0.01 |                                               0    |

**Condition: steered**

| classification            |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:--------------------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| compliance-with-disavowal |                        0.06 |                         0.17 |                    0.11 |           0.01 |                        0.13 |                                               0.3  |
| full-compliance           |                        0.03 |                         0.41 |                    0.66 |           0.1  |                        0.26 |                                               0.46 |
| partial-comply            |                        0    |                         0.01 |                    0    |           0    |                        0    |                                               0.01 |
| refusal-flat              |                        0    |                         0    |                    0    |           0    |                        0    |                                               0.11 |
| refusal-with-alternative  |                        0.91 |                         0.41 |                    0.23 |           0.89 |                        0.61 |                                               0.12 |

## Judge self-preference: divergence from peer consensus

mismatch_rate_gap = self_mismatch_rate - other_mismatch_rate, where mismatch = judge's label != majority label of the other 5 judges on the same response. Positive gap: judge disagrees with peers MORE on its own output than on others' — a self-preference signal in magnitude only. No claim about which direction is 'better' is made here; see judge_divergence_direction.csv for the specific label substitutions behind any gap, and the discussion section for a literature-grounded reading of direction.

| judge_model                                      | category                  |   self_mismatch_rate |   other_mismatch_rate |   mismatch_rate_gap |   n_self |   n_other |
|:-------------------------------------------------|:--------------------------|---------------------:|----------------------:|--------------------:|---------:|----------:|
| anthropic:claude-opus-4-7                        | reasoning_hint            |                0     |                 0.02  |              -0.02  |       40 |       200 |
| anthropic:claude-opus-4-7                        | reasoning_values_elicit   |                0.065 |                 0.06  |               0.005 |      200 |      1000 |
| anthropic:claude-opus-4-7                        | reasoning_values_suppress |                0.225 |                 0.191 |               0.034 |      200 |      1000 |
| anthropic:claude-opus-4-7                        | stylistic                 |                0.075 |                 0.08  |              -0.005 |       40 |       200 |
| anthropic:claude-opus-4-7                        | values_conflict_low       |                0.06  |                 0.107 |              -0.047 |      200 |      1000 |
| deepseek:deepseek-reasoner                       | reasoning_hint            |                0.075 |                 0.025 |               0.05  |       40 |       200 |
| deepseek:deepseek-reasoner                       | reasoning_values_elicit   |                0.015 |                 0.076 |              -0.061 |      200 |      1000 |
| deepseek:deepseek-reasoner                       | reasoning_values_suppress |                0.28  |                 0.321 |              -0.041 |      200 |      1000 |
| deepseek:deepseek-reasoner                       | stylistic                 |                0.15  |                 0.035 |               0.115 |       40 |       200 |
| deepseek:deepseek-reasoner                       | values_conflict_low       |                0.08  |                 0.099 |              -0.019 |      200 |      1000 |
| google:gemini-2.5-pro                            | reasoning_hint            |                0.025 |                 0.035 |              -0.01  |       40 |       200 |
| google:gemini-2.5-pro                            | reasoning_values_elicit   |                0.015 |                 0.024 |              -0.009 |      200 |      1000 |
| google:gemini-2.5-pro                            | reasoning_values_suppress |                0.225 |                 0.193 |               0.032 |      200 |      1000 |
| google:gemini-2.5-pro                            | stylistic                 |                0.05  |                 0.045 |               0.005 |       40 |       200 |
| google:gemini-2.5-pro                            | values_conflict_low       |                0.145 |                 0.137 |               0.008 |      200 |      1000 |
| openai:gpt-5                                     | reasoning_hint            |                0     |                 0.03  |              -0.03  |       40 |       200 |
| openai:gpt-5                                     | reasoning_values_elicit   |                0.065 |                 0.021 |               0.044 |      200 |      1000 |
| openai:gpt-5                                     | reasoning_values_suppress |                0.24  |                 0.194 |               0.046 |      200 |      1000 |
| openai:gpt-5                                     | stylistic                 |                0     |                 0.165 |              -0.165 |       40 |       200 |
| openai:gpt-5                                     | values_conflict_low       |                0.03  |                 0.044 |              -0.014 |      200 |      1000 |
| together:Qwen/Qwen3.7-Max                        | reasoning_hint            |                0.025 |                 0.02  |               0.005 |       40 |       200 |
| together:Qwen/Qwen3.7-Max                        | reasoning_values_elicit   |                0.045 |                 0.037 |               0.008 |      200 |      1000 |
| together:Qwen/Qwen3.7-Max                        | reasoning_values_suppress |                0.19  |                 0.186 |               0.004 |      200 |      1000 |
| together:Qwen/Qwen3.7-Max                        | stylistic                 |                0.025 |                 0.04  |              -0.015 |       40 |       200 |
| together:Qwen/Qwen3.7-Max                        | values_conflict_low       |                0.03  |                 0.038 |              -0.008 |      200 |      1000 |
| together:meta-llama/Llama-3.3-70B-Instruct-Turbo | reasoning_hint            |                0.175 |                 0.165 |               0.01  |       40 |       200 |
| together:meta-llama/Llama-3.3-70B-Instruct-Turbo | reasoning_values_elicit   |                0.025 |                 0.025 |               0     |      200 |      1000 |
| together:meta-llama/Llama-3.3-70B-Instruct-Turbo | reasoning_values_suppress |                0.275 |                 0.238 |               0.037 |      200 |      1000 |
| together:meta-llama/Llama-3.3-70B-Instruct-Turbo | stylistic                 |                0.1   |                 0.095 |               0.005 |       40 |       200 |
| together:meta-llama/Llama-3.3-70B-Instruct-Turbo | values_conflict_low       |                0.155 |                 0.14  |               0.015 |      200 |      1000 |

## Pairwise judge agreement

| judge_a                                          |   anthropic:claude-opus-4-7 |   deepseek:deepseek-reasoner |   google:gemini-2.5-pro |   openai:gpt-5 |   together:Qwen/Qwen3.7-Max |   together:meta-llama/Llama-3.3-70B-Instruct-Turbo |
|:-------------------------------------------------|----------------------------:|-----------------------------:|------------------------:|---------------:|----------------------------:|---------------------------------------------------:|
| anthropic:claude-opus-4-7                        |                           1 |                         0.82 |                    0.86 |           0.87 |                        0.89 |                                               0.83 |
| deepseek:deepseek-reasoner                       |                         nan |                         1    |                    0.82 |           0.84 |                        0.85 |                                               0.82 |
| google:gemini-2.5-pro                            |                         nan |                       nan    |                    1    |           0.87 |                        0.88 |                                               0.84 |
| openai:gpt-5                                     |                         nan |                       nan    |                  nan    |           1    |                        0.9  |                                               0.86 |
| together:Qwen/Qwen3.7-Max                        |                         nan |                       nan    |                  nan    |         nan    |                        1    |                                               0.84 |
| together:meta-llama/Llama-3.3-70B-Instruct-Turbo |                         nan |                       nan    |                  nan    |         nan    |                      nan    |                                               1    |
