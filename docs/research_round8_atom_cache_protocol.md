# Registered dictionary-atom memory descendant — 6 October 2026

This is a new finite no-core-retraining experiment, not a claim that word memory is exhausted. Registration precedes reading its native outcomes. Use the verified lexical preparation, 587,138,826 bytes, SHA256 7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce. The full preprocessing inverse already reconstructs the original billion bytes exactly. Production entropy coding remains unexecuted.

## Why this changes the preceding failed cache

The preceding cache targets one encoded byte, even when a dictionary word occupies two or three bytes. Its hidden key can therefore describe an internal code position rather than the context before a word. This descendant holds one query fixed from the start of an encoded atom through its complete code. It inserts the key and complete target only after the final byte. A dictionary atom is an exact WRT token, not an asserted linguistic/POS word. Literal bytes, capitalization controls and escape payloads have explicit handling. A later lexical-word architecture remains open.

## Probability and engineering contract

Encode all 128 unescaped literal atoms and all 44,515 dictionary atoms as their existing physical one-to-three-byte codes. Pad codes with zero suffixes to a 24-bit integer, sort, and store only those integers. Prefix-free valid codes make any observed bit prefix an interval in this sorted array. A uint32 Fenwick tree holds completed-atom frequencies. If I is a prefix interval, the causal prior is

    g(I) = (count(I) + 0.5 * |I|) / (N + 0.5 * 44,643).

For the at-most-eight selected historical donors, normalized softmax weights sum to one. Let r(I) be their mass in interval I. With alpha=0.9,

    q(I) = 0.1*g(I) + 0.9*r(I).
    delta(prefix) = log(q(I1)/q(I0)) - log(g(I1)/g(I0)).

The existing final native probability p is changed only by a normalized Bernoulli logit residual: sigmoid(logit(p)+theta*clip(delta,-12,12)). No new categorical assertion about the native word distribution is needed. If either child is outside the valid atom language, the residual is zero. Escape payload bytes and the initial synchronization prefix also use identity. All eight bits, including partial final atoms, are accounted for.

Use the native q5[192] from the preceding completed byte, biased uint8 converted to signed coordinates. Its validity flag is required. Freeze the query and donor shortlist before the atom's first bit; do not consult the current atom, its length, cost, future hidden state or future spelling. Coordinate centering/variance come only from previous completed atoms. Both donors and query use the same current coordinates.

Nine predeclared sources: raw/centered/diagonally standardized K8 nearest neighbors, each with a matched same-bank target permutation; dictionary-atom recency; centered K8 error memory and its permutation. Tau=1000, K=8, alpha=0.9, FIFO=512. The error bank admits only completed dictionary atoms whose already-observed native cost exceeds two bits. Prefix Welford variance uses positive diagonal weights 1/(variance+1). Permutation is a deterministic circular shift of occupied-row targets; it preserves the occupied bank's target histogram exactly, including duplicate targets. Tie order is explicit.

Production feasibility is a separate gate. One bank plus sorted codes and Fenwick counts has a nominal design of about 464 KB, before allocator alignment, buffers, loader and code. The measured baseline has only 615,424 bytes below a conservative decimal 10 GB limit. The diagnostic computes two banks and controls and is not its production footprint. Existing KVI8 cannot be counted again. A selected implementation must reuse the loaded dictionary, allocate one chosen bank, and pass whole-program peak RAM and single-core timing. No complete native candidate is implied by a replay gain.

## Data and selection

Cold native 524,288-byte slices of the corrected stream: A=0, B=102,635,191 for development; C=310,000,000 and D=520,000,000 for conditional confirmation. First create matched unchanged-reference/observation-only A/B32K archives and independent decoding with identical hidden records. Generate full 512K native baseline archives/hidden/final-Q16 traces. These are cold-core slices, not warmed production state. Do not conflate them with the old transformed-stream G/H checks.

Fit generic and nine individual bounded convex logistic heads, plus one joint head, to A/B only. Box [-1,1], binary64 coefficients, two stored copies, four-bit selector (11 heads). Certify the ideal real-valued convex optimum by the supporting-plane bound; report Q16 rounding separately. Independently test gradients, PSD Hessian, neutral identity, prefix interval sums and future noninterference. Evaluate C/D candidate features only if the best A/B saving after coefficient copies/selector is at least 64 bytes. Otherwise preserve C/D baselines unexamined by candidate. No hyperparameter is selected from C/D.

Also report a fixed causal Bayesian aggregation with half the initial mass on identity and half shared over 40 predeclared corrections: four generic calibration candidates and four strengths {-0.125,0.25,0.5,1} for each of nine sources. Posterior updates occur after each decoded bit. Global and 24-context (bit position × atom-byte depth) versions are separate fixed policies. The ideal global mixture obeys L_mix <= L_identity + 1 bit per reset; Q16 rounding is measured and does not inherit that exact guarantee. These policies need no fitted coefficients but still pay their code/state/selection and full native costs. Their A/B runs are diagnostic; C/D advancement likewise requires at least 64 bytes before new code, a deliberately preliminary gate.

Every archive/data/model remains preserved. Spend $0, delete no project files. Preserve failures instead of silently relaunching duplicates. A positive pilot is followed by native coder integration, exact independent reconstruction, independent warmed slices and complete package accounting; it is never reported as record breaking by itself.
