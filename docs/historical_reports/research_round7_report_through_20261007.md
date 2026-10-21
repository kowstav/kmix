<!-- current-native-and-rarity-start -->
Updated2026-10-06T15:06:38.167328+00:00: 118completed finite native fitted heads,27online role policies;
source-conditioned31head fit:COMPLETE31heads; best priced A/B42.446535646B; advancementFalse. Rarity census:COMPLETE_RARITY_CENSUS_DIAGNOSTIC; launchPID1192; read its manifest, no masking training yet.
Current ledger96 =95historical families +newA96; every family remainsOPEN.
Read research_round8_5090_hours_and_rarity_plan.md for the direct coverage,
GPU-hour and masking answers. No qualifying archive/20%gain; budget70/spent0.
<!-- current-native-and-rarity-end -->

<!-- session355735431-summary-start -->
> Latest integrated research, 2026-10-06T12:09:15.241318+00:00: newest session355735431; 62native/cache heads complete;
> canonical11head atom screen fails its registered gate. Strong paired-error
> branch:running; verify actual manifest/process. Attachment fully read;
> see research_round8_attachment_assessment.md and
> research_round8_attachment_training_addendum.md for cost mining,
> objective-safe replay, curriculum controls, causal synthetic tasks and export
> gates. Full correct lexical inverse PASS; full native entropy qualification
> stillOPEN. All95families OPEN; no20%result; budget$70/spent$0; deletionsNONE.
> Current handoff: research_round8_session355735431_handoff.md. Historical stream,
> PID and incomplete-preparation claims below are superseded by the checkpoint.
<!-- session355735431-summary-end -->

<!-- native-extension-integration -->
> **6October native extension:**51cache-head variants completed; none advances
> after priced A/B selection. Correct lexical stream587138826B now reproduces
> all1B original bytes exactly through its full preprocessing inverse. Full
> entropy coding remains open. Registered dictionary-atom cache experiment is
> running on that corrected stream. New pending competitor reports95914051B;
> complete source/results and new targets: research_round8_report.md sections16–18.
> All95families unfinished, no20%/qualifying result,$0spending,no deletions.
<!-- native-extension-integration-end -->

<!-- round8-integration-start -->
> **Round8 continuation,6October2026:** New actual experiments, repaired feature
> semantics, independent mathematical checks, finite optima, frozen semantic
> signal and remaining qualification gates are in
> [research_round8_report.md](research_round8_report.md).
> [The95-family continuation program](research_round8_idea_program.md) assigns
> stronger descendants and tests to every recoverable idea; none is fully explored.
> No record/package/20% improvement is asserted. Core weights stay frozen;
> no paid rental or deletion. Read the current checkpoint for live/completed jobs.
> Earlier running-status paragraphs below are historical.
<!-- round8-integration-end -->

# Hutter Prize research, round 7 — evidence and compression plan

> **6 October evidence-audit correction:** See [the detailed rounds1–7 idea audit](/C:/Users/91707/Downloads/compression_cmix/research_round1_to_round7_idea_audit.md). Its source review finds that round4's enwik8 totals include one model copy and entropy-estimated weights, rather than a finished qualifying package; its largest half-precision retrieval bank needs14.86GB for keys alone. The historical20.27% weak-baseline likelihood comparison and2.3% one-copy description-length comparison must not be presented as record/package gains. The central learned relation, suppression, survival, shared residual and content-first infilling mechanisms remain untrained. The audit distinguishes95 recoverable families, all three requested assessments and missing round1/effort evidence. No new compression result is asserted.

Updated 5 October 2026. Working report; new session355386999 is accessible,
all four2M native compressions and independent decodes pass. A repaired neural
pilot and new idea-file echo tests are running. A 20% improvement has not
been demonstrated. No new neural training or paid GPU rental has occurred.
Numbers described as likelihood savings exclude new decoder code and CPU unless
explicitly stated otherwise. All measured samples are from enwik9.

The new Kaggle session was recovered from the preserved files. This round
completed four residual word/context atlases, frozen-neural calibration screens,
normalized field and line-edit screens, native final-bit tracing, and controls
for the structural expert's extra mixer. A published, more specialized weight
codec has been reproduced and verified on the original checkpoint. Its result is credited to FX4's
authors; reproducing and combining it is engineering progress, not a new
compression discovery.

## The objective and the benchmark

The official accepted total remains **100,424,672 bytes** on the
[Hutter Prize site](https://www.hutter1.net/prize/), checked 5 October 2026.
The site's rules count the compressor plus the self-extracting compressed data,
require at least a 1% reduction, and impose single-core time, memory and disk
limits. The [detailed rules](https://www.hutter1.net/prize/hrules.htm) require
each program separately to finish in less than 70,000/T hours, where T is the
machine's Geekbench 5 score. The main page summarizes roughly 50 hours on a
single CPU core, under 10 GB RAM and under 100 GB temporary disk. Record
compression and decompression separately; a combined 50-hour budget would be
the wrong interpretation. Faster GPUs during research do not make a
GPU-dependent submitted decoder eligible.

The [large text compression benchmark](https://mattmahoney.net/dc/text.html)
also lists pending totals of 99,313,750 for lexth11c and 99,312,424 for zmix 1.0.
These were also rechecked on 5 October and are separate from the accepted
prize record. Published times on an
author's hardware need comparison on the judge's machine; a displayed raw time
is not by itself a qualification verdict. Most earlier lab screens use the
original FX2 neural checkpoint with an FXCM-v26 classical port. The later
isolated lexical build reproduces actual lexth11c checkpoint inference on four
32K cold samples with exact native round trips. Neither set establishes a full
qualifying archive.

A strict reduction greater than 20% relative to the accepted score requires

    S_new <= 80,339,737 bytes,
    S_old - S_new >= 20,084,935 bytes.

Against the strongest pending published total, 99,312,424 bytes, a strict
greater-than-20% reduction instead requires at most **79,449,939 bytes**.
Track both targets. Meeting the accepted-record target alone could miss the
pending-record target by 889,798 bytes; never switch denominators silently.

The original payload is 93,770,082 bytes. If fixed components stay unchanged,
the payload must shrink by approximately **21.42%**. With 586,459,020 post-WRT
symbols, the required saving is **0.27398244 bits per WRT symbol**. Even removing
both entire original weight copies would save only 5,861,304 bytes and would
destroy their prediction benefit. Model-storage tweaks alone cannot meet the
overall target.

For any candidate, price the actual submitted representation:

    8 S = L_payload + L_other_archive_data + L_S1.

In the current packaging, executable, dictionary and neural weights occur in
both S1 and S2; article order occurs in S1. Thus the useful planning objective is

    J = sum_t -log2 P_final(x_t | x_<t)
        + 2 R_weights + 2 R_executable + 2 R_dictionary
        + R_order + R_headers + R_other.

Final arithmetic-coder quantization and framing are measured separately; a
likelihood estimate is not an exact archive size. Do not add gains from
overlapping experts without a joint run, and do not substitute standalone
neural cross-entropy for the final mixer's cost.

## What the previous reports establish

The supplied `hutter_round6_report.md` contains the requested round-6 report.
Its strongest concrete results are a 3,369,451-byte compressor candidate,
3,169,936 bytes of fixed S2 components, and 274,829 bytes saved over separately
coded structural tail regions. The projected full saving was 624–765 KB,
approximately 0.62–0.76%. The report correctly labels the FXCM text gains and
full combination as projections; no full-stream compress/decompress proves
that projected score.

Two conclusions need narrower wording. The failed short QAT continuation does
not prove that a full retrain is necessary: its matched lambda=0 control also
deteriorated, and data sampling, prior coverage and optimizer state were not
equivalent to the original training. Similarly, weak neural/exact-context cache
results reject those particular caches, not all causal memory mechanisms.

Round 6's structural patch adds a mixer and an input unconditionally. Disabling
the expert does not restore the unpatched topology. Round 7 therefore compares
unpatched, patched-neutral and active builds. The neutral C/D controls increase
the native archives by **10 and 14 bytes**, respectively. The active controls
also increase the C/D archives by exactly 10 and 14 bytes, with identical
cost arrays to patched-neutral. These main-text slices do not activate the
tail specialists. Results are in `research_round7_sx_topology_controls.json`.
This controls a real source of main-text regression, even though its observed
size is small. Warm full-stream behavior remains unmeasured.

## Where the model still spends bits

Each atlas maps observed ASCII word spans through the actual WRT dictionary
back to final-coder cost. The assignment sum is checked against the total;
it is an attribution of already measured costs, not a new predictive model.
ASCII spans include tag words and fragments of non-ASCII words, so the labels
must not be read as a complete linguistic tokenization. Article histories
start cold at each slice; first seen in a slice does not mean first in enwik9.

| Measurement | A | B |
|---|---:|---:|
| Post-WRT bytes | 2,000,000 | 2,000,000 |
| Decoded bytes in word atlas | 2,815,331 | 3,502,104 |
| ASCII word occurrences | 332,424 | 513,255 |
| Distinct ASCII word types | 19,348 | 21,111 |
| Baseline final likelihood, bytes | 193,366.172 | 427,095.009 |
| Share of final bits in word spans | 77.42% | 82.20% |

Per-occurrence difficulty and total cost give different priorities. Common
words such as *the*, *of*, *and*, *king* and *emperor* can dominate total cost
because they occur often. Names such as *Cuauhtlatoatzin* and *Ixtlilxochitl*
cost approximately 77 and 75 bits per occurrence in A; B has difficult technical
words including *anycast*, *routable* and *texting* at approximately 24, 22 and
22 bits per occurrence. Expensive one-off names merit a spelling channel, but
optimizing only spectacular rare errors can miss most aggregate savings.

The context atlas separates useful causal situations:

| Share of all baseline bits | B | C | D |
|---|---:|---:|---:|
| Word first seen in slice prefix | 9.88% | 9.96% | 13.68% |
| Previously seen word, first mention in current article | 38.85% | 36.99% | 39.53% |
| Same-article repeat within 1,024 WRT bytes | 25.71% | 26.03% | 23.13% |
| Same-article repeat beyond 1,024 WRT bytes | 7.74% | 8.99% | 8.90% |

These selected rows form disjoint occurrence classes, but other diagnostic
classes in the JSON overlap. The restricted strategy that improves only
same-article word repetitions beyond 1,024 symbols has at most roughly 9% of
the sampled bit budget, even if it makes those events free. This is a bound
for that restricted class, not a bound for every long-context mechanism.

The larger opportunity is selecting familiar words when entering a different
article, choosing an entity's related facts, and resolving unfamiliar spelling
without paying an unrelated dictionary code. That approximately 37–40% budget
is a research direction, not an obtainable saving: choosing the correct word
still costs information, and other predictors already exploit part of it.

## Assessment of the community suggestions

The community's memory and TTL ideas contain useful mechanisms. Their claim
that already seen vocabulary makes the remaining archive largely unnecessary
confuses possession of a word with prediction of which word comes next.

For 200,000 equally likely known alternatives, specifying the choice still
requires log2(200000) = 17.61 bits. The archive contains an entropy-coded choice
sequence, model/code/dictionary data and framing; it is not merely a list of
unique words. Our existing full-corpus inventory has approximately 1.171 million
case-folded ASCII types and 133.9 million occurrences; about 99.13% of occurrences
are repetitions. Distinct-type coverage was approximately 23.3%, 38.2%, 61.6%
and 82.9% after 10%, 25%, 50% and 75% of the stream. Repetition prevalence is
already high and does not imply that the next choice is cheap.

Use **previously decoded actual symbols** for a shared memory. Both ends know
them. Previous guesses that were wrong are also reproducible if the numerical
procedure is deterministic, but they usually provide a worse fact store.
A miner K_t=f(x_<t,theta) is legitimate without a transmitted pointer because
both ends can run it. In information terms,

    I(X_t; K_t | X_<t, theta) = 0.

This does not make the miner useless. A finite model retains a statistic M_t,
not the entire prefix; I(X_t;K_t | M_t,theta) can be positive. Memory helps by
recovering a useful statistic that the model failed to retain or access.

Searching the future target for the best hint and giving that hint to the
decoder for free is invalid. A pointer/selection policy must be reproducible
from the prefix or be encoded. For a chosen sequence of hint IDs k_t, price
L(k_t | prefix); for a learned policy, price its quantized parameters and code.
Fixed-corpus overfitting is allowed in principle, but overfitting stored in a
large policy is compression only if saved payload exceeds its description cost.

TTL becomes precise as a bounded policy: store completed facts or article
profiles, estimate future usefulness from decoded queries, and evict using
deterministic age/relevance counters. A 1,024-token attention window does not
mean this checkpoint has no older memory: most layers use recurrent KDA state.
Arbitrarily injecting text into the frozen transformer changes its positions,
PPMD prior alignment and recurrent state; retraining or an externally mixed
memory distribution is needed unless those changes are measured and mirrored.

Morphological or algebraic word relations are useful when they give a
normalized conditional spelling/word distribution. Anagram canonicalization
loses letter order. Given a length-m multiset with counts n_j, restoring order
can require log2(m! / product_j n_j!) bits. Those residual bits and the
choice of reference word must be paid. Character composition should preserve
positions, prefixes, suffixes, script and case, with a semantic component for
relations that spelling alone cannot supply. Assertions/conjunctions become
useful only after specifying a causal rule and its probability distribution.

Changing dictionary labels alone does not reduce a fixed complete-word model's
assigned information. For an invertible code mapping T, define
Q(y)=P(T^-1(y)); then -log2Q(T(w))=-log2P(w). Morphology-aware labels can help
a limited predictor learn shared structure, but that is a change in its
probability model. Reassigning a pretrained checkpoint's byte labels without
measuring that change is not a compression proof. This is why the proposed
spelling/semantic composer preserves the existing classical WRT stream.

OCR is a poor default for a text corpus. Rendering adds a representation and
font/layout choices; ordinary OCR is not exactly invertible. Any useful image
scheme must carry exact textual correction residuals and count its model and
renderer. No evidence here suggests this beats direct text modeling.

## Frozen-model experiments completed this round

The field and line channels operate on completed old donors. Activation keys
come only from already decoded prefixes. An edit channel sums over all allowed
alignments; it does not inspect the target to choose one free alignment.

For donor position j, deletion d advances without emission, insertion i emits
from the baseline without advancing, substitution u emits from the baseline
and advances, and copy 1-d-i-u emits the donor byte and advances. Forward
deletion closure is vbar[j]=v[j]+d*vbar[j-1]; emissions are normalized and the
final donor state falls back to the baseline. A Bayesian sequence mixture over
49 fixed experts per context includes a neutral expert and pays adaptation.

For any sequence mixture with initial weights pi_k,

    q_t = sum_k pi_{k,t} p_{k,t},
    pi_{k,t+1} proportional to pi_{k,t} p_{k,t}(x_t),
    L_q <= min_k [ L_k - log2 pi_k ].

The update occurs after decoding. This is a real normalized predictor. An
unpaid best expert chosen separately for each unknown event has no such coding
interpretation.

The final confirmed likelihood savings below are **bytes per 2M-symbol slice**;
positive means smaller. The field screens were rerun after fixing a slice-EOF
defect, so an unfinished field is never silently treated as completed.

| Causal family | A | B | C | D |
|---|---:|---:|---:|---:|
| Balanced title/link/schema point-copy mixture | -2.261 | +1.902 | +0.649 | -1.910 |
| Same fields, marginalized edit mixture | -3.495 | +0.007 | -0.808 | -3.527 |
| Prefix-keyed line exact copy | -1.548 | +1.029 | +1.001 | +0.201 |
| Prefix-keyed line edit | -2.822 | +3.701 | +10.262 | +3.711 |
| Line edit, mask digits in observed key | -2.728 | +3.286 | +10.387 | +3.715 |

The line memory is bounded at 16 MB payload / 64K keys with at most two donors;
the first four bytes of each line are paid before retrieval. Even its unpaid
per-event diagnostic oracle has only a few hundred bytes of benefit per
sample. This particular donor family has neither measured gain nor an oracle
budget close to 20%. The result does not rule out much better schema/entity
representations or integration as internal mixer signals.

Frozen neural temperature trials from 0.6 to 1.5 leave temperature=1 as the best
fixed choice on A/B. Global Bayesian mixtures cost about 0.396 bytes, and the
entropy-context mixtures cost approximately 2.5 bytes. These are standalone
neural likelihood measurements, not final-archive changes.

Final-bit traces record the coder's actual quantized probability. The trace
cost reconstructs the accumulated final cost within roughly 5e-5 bits. A
causal mixture of temperatures and count-based calibration experts gives
**30.194 bytes on A and 4.279 on B** for the consistent bit-position-only
policy. These are small gross likelihood gains. The unpaid best expert per
unknown bit would appear to save approximately 27%, but it chooses using the
answer and is invalid; it is not our result.

The edit kernel agrees with 180 Python insertion/deletion/substitution tests
to under 2.85e-14 bits. Native baseline C/D archives are 431,075 / 413,364 bytes.
The rebuilt lab's costs closely reproduce the saved baseline, but floating
point/compiler effects make them not bit-identical. Every production claim
therefore needs a matched binary comparison and a round trip.

## Weight-container result and remaining verification

The initial generic exact packing survey found no win: its best complete
alternative was 289 bytes larger per copy. That is a statement about the tested
family, not a proof of optimality. The
[public FX4 repository](https://github.com/naveenbijalwan/fx4-cmix-transformer)
provides a specialized FX2TFWC5 codec: each Q4 tensor selects an adaptive tree,
an embedded 15-symbol histogram, or that histogram with causal column counts.
The histogram and encoding flag are stored; column state is reconstructed
from shape and preceding weights. RoPE reconstruction and all tensor values
are unchanged. Source is pinned to commit
`f6bca0d40d9532dd9a0bfa101abe374d2ca8be7f`; original GPLv3 source and license are
preserved under `research_round7_sources`.

The Python reproduction on the original model yields **2,902,452 bytes**, down
from **2,930,652**, exactly **28,200 bytes per copy**. All 434 tensor byte arrays
match after decoding, and re-encoding the original v2 container reproduces its
entire original byte stream. The candidate BF16 model shrinks from 2,874,742 to
**2,846,543 bytes**, saving 28,199 per copy. Independent C++ old/new loaders
serialize every decoded tensor identically for both models, including RoPE.

The same native neural inference on an 8,192-symbol prefix produces identical
3,358,720-byte probability files and identical 956-byte archives. All linked
objects other than the weight loader are unchanged. Matched unprofiled lab
executables packed with UPX 3.96 LZMA are 183,412 / 184,180 bytes, an incremental
768-byte loader cost per copy. This gives **54,864 bytes** net for the reference
and **54,862 bytes** for the BF16 candidate across two copies. This is measured
component accounting in the lab build; final PGO production packaging and the
complete archive remain unverified. It is approximately 0.055% of the accepted
total, far short of 20%. Results are preserved in the codec, native-verification,
native-inference and package-screen JSON files.

The shared rule for storage improvements is

    net saving = 2 * old_weight_bytes - 2 * new_weight_bytes
                 - 2 * incremental_packed_loader_bytes
                 - additional_headers_or_other_data.

A loader link failure in the first verification attempt was corrected by
including its existing weights_io dependency. Both logs are kept. No candidate
or production executable was overwritten.

## Search direction with a larger possible bit budget

The new causal association suffix screen saves **7.554 / 54.905 / 75.124 /
29.940 likelihood bytes** on A/B/C/D before code and runtime. It covers
22.94% /22.90% /23.43% /25.34% of the sampled baseline bits. Global frequency,
article counts, previous-atom followers, four/sixteen recent content atoms and
known title atoms are controls within the same normalized family. B/C/D gain
primarily on repeats; previously seen atoms first in the article lose
21.371 /47.538 /51.681 bytes. This simple association graph does not solve the
main first-mention problem.

WRT's first code byte does not always determine code length: some two/three
byte code paths share it. The initial integration parser failed on that detail.
It was corrected, and unknown leaf length was removed from activation contexts.
Mixed-prefix normalization and parser tests now cover both paths. A separate
root-code family charges all literal/case/syntax/escape failures and activates
before the first byte using only prior event category and article age. A
candidate-masking family removes already decoded article atoms from the
distribution, while repeated targets explicitly pay fallback. The
root test completed with **-2.413 /+14.574 /+15.270 /+8.125 bytes** on A/B/C/D.
It covers99.5–99.99% of sampled costs after synchronization, so its failure is
not explained by the suffix-only coverage limit. Candidate masking completed
with **-1.945 /+15.815 /+16.005 /+8.852 bytes**. B/C/D first mentions of known
words gain45.866 /30.383 /10.213 bytes, but literal/syntax/case events lose
40.988 /32.466 /15.371 bytes. All fixed global policies lose to neutral on
these samples. Neither family supports a large compression claim.

For the original discretization `n=unsigned(1+65534*p)`, the final-bit traces
also bound the benefit of using higher precision with the same predictor.
Allowing a conservative float-rounding margin and an unpaid per-bit choice
of the most favorable probability inside its bin gives at most **57.492 /
59.566 bytes** on A/B, approximately0.030% /0.014% of baseline likelihood.
This is a deliberately optimistic upper bound for probability precision on
these samples, not an achieved coding result or a bound on arbitrary new
models. See `research_round7_precision_bound.py` and its saved JSON.

A bounded post-training sparsification test exported three Q4 variants
and completed matched native inference on A/B32768-symbol prefixes. It uses
no SGD or scale updates, but changes predictor weights. The complete
storage-versus-payload plan is `research_round7_ptq_plan.md`.

| Variant | Stored weights, bytes | Two-copy storage saving | Added final likelihood bytes A | Added final likelihood bytes B |
|---|---:|---:|---:|---:|
| BF16 candidate baseline | 2,846,543 | 0 | 0 | 0 |
| Zero magnitude-one MLP-down codes | 2,735,672 | 221,742 | 130.255 | 185.406 |
| Same on MLP-up/down | 2,628,767 | 435,552 | 288.270 | 442.338 |
| Zero all Q4 codes of magnitude at most two | 2,001,203 | 1,690,680 | 1,490.782 | 3,242.953 |

The baseline native archives are3170 /8456 bytes. Corresponding modified
archives are3300 /8641,3458 /8898 and4660 /11699. Thus the 29.7% weight-file
reduction damages payload prediction substantially; it is neither improved
model quality nor a20% archive result. The gentlest change can tolerate only
about12.39 added bytes per32768-symbol sample at full-file break-even, versus
the measured130–185. These are cold short samples, not a full-stream penalty
estimate. Every candidate fails this initial storage-versus-payload gate;
none is promoted to a full run. Original models and candidate outputs remain
intact. See `research_round7_ptq_native_results.json`.

The preserved source archive also contains the actual lexth11c checkpoint:
`models/lex_h1_run11.tfwc2`,2978039 bytes, magicFX2TFWC3, SHA256
`948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71`.
Its nonuniform codebooks, 8-bit embedding tables and dynamic activation scales
require the matching native configuration. An exact C5 conversion retains all
435 serialized tensor arrays and original order but grows to2978979 bytes,
losing940 bytes per copy before loader cost. The earlier FX2 codec gain must
not be transferred to this stronger checkpoint. A matched isolated lexical
build completed with the matching configuration and unchanged checkpoint.
After translating the wrapper options into the actual C++ macros, a forced
full compile with QMAT_CODEBOOK=1,QMAT_WMAX=21,QMAT_SMALL_W8=1,
TF_ACTQ_DYN=1,TF_AVX512=1 passed all four32768-symbol native round trips.
Native archives are **3109 /8222 /8990 /9264 bytes** on A/B/C/D; ideal costs
are3072.175 /8184.612 /8952.574 /9227.258 bytes. Peak RSS on these small
samples is5.65–5.81millionKiB, and roughly66–70user CPU seconds per run.
The earlier BF16 lab A/B archives are3170 /8456 bytes. This comparison changes
both checkpoint and classical configuration; it does not isolate a neural-model
effect or establish a full score. Source/scope/resource evidence is preserved
in `research_round7_lex_native_results.json`. Two-million-symbol controls
were launched on C/D then A/B, with independent decodes queued afterward.
The new session confirms all four compressions completed with exact32K
prefix-cost parity. A/B/C/D archives are187401/437079/447061/439381 bytes;
ideal costs187363.087/437041.141/447023.932/439343.313 bytes. User CPU is
1091.92–1195.96 seconds and peak RSS6041512–6043580KiB on these cold2M
samples. The results and four8MB cost traces are preserved locally. They
cannot be subtracted from earlier warm-neural reference costs and labeled a
model improvement. The old session interrupted C/D decodes; no completed
decode result survived. Its persistent C/D archives are reused. Only missing
A/B ephemeral archives are being regenerated against saved costs before
independent full-slice decodes. Recovery details/hashes are in
`research_round7_lex_2m_recovery_manifest.json`; no original asset was deleted.
C/D independent2M decodes now pass the exact original byte length and SHA256.
User CPU is1222.538/1220.699 seconds, RSS6041196/6039588KiB. Evidence is
`research_round7_lex_native_2m_recovered_results.json`; A/B regeneration and
independent decodes remain running. This validates cold-slice interoperability
across the two sessions, not the full benchmark or every CPU platform.
The
unprofiled lab output still requires separate production PGO/package and
full-stream verification. Initial instrumentation assumed older interfaces
and stopped; a missing generated comment prefix, the extra raw-bit coder API,
and the new buffered loop were corrected. The first native range check also
rejected direct use of wrapper TF_CODEBOOK/TF_SMALL_W8 names as C++ macros;
their correct QMAT_* translation above was audited before accepting any
coding result. Failure copies/logs remain available.
GNU time was installed after its absence stopped the first resource-measured
launch before any cmix process began; completed compilation was reused.

The priced article-topic family also fails. It freezes32 TF-IDF clusters plus
one global content profile from2785 A/B article regions, with up to256 integer-
weighted dictionary atoms each. Seven mixing strengths yield231 specialist
choices. A future-informed encoder choice is explicitly paid:1bit for neutral,
9bits for a specialist. Every literal/case/syntax/escape event pays fallback.
The finished zlib table is21844 bytes per copy. After selector costs, A/B/C/D
lose **231.275 /114.586 /89.628 /61.994 bytes**, before table/code overhead.
Only1/3/1/1 regions choose a specialist. The table alone adds43688 bytes across
the two package copies. Results are in `research_round7_topic_selector_results.json`;
the construction, selector code and possible conditional-latent training
objective are detailed in `research_round7_article_latent_plan.md`.
This rejects the tested sparse topical prior, not all possible learned
article-conditioning architectures. No extra native topic system is warranted.

There is no general computable optimizer over unrestricted shortest programs.
A precisely bounded finite program/runtime family has a finite exhaustive
search in principle, but is infeasible at this scale. We can certify a best
tested candidate in an explicit family, not an absolute global maximum.

Use residual budget before expensive search: if an expert can improve only
events whose total baseline cost is B_E, even a perfect prediction of those
events saves at most B_E before its own overhead. Prune small-budget families
early. For larger families, charge the donor, rule, latent alignment or learned
selector; never count an oracle score as attainable savings.

The preferred architecture branch is specified in
`research_round7_word_model_plan.md`. Keep the exact existing WRT/classical
stream, move expensive neural state updates to completed lexical events, and
use a small byte/spelling/syntax head between events. A normalized word model
can induce byte probabilities on the dictionary's actual prefix tree:

    P(b | a,h) = sum_{w: c(w) starts with a b} P(w | h)
                 / sum_{w: c(w) starts with a} P(w | h).

Literal, escape, case and control branches have explicit mass. The word state
updates only after a causally recognizable completion; the byte state updates
after every observed byte. A hierarchical head avoids evaluating every word
at every byte. The representation combines a position-aware spelling composer
with a small quantized semantic code. A rank-16 int8 table for 44,515 dictionary
words costs 712,240 bytes per copy before scales/code; both copies require
about 0.019432 bits/WRT-symbol of gain merely to break even.

The stream has approximately 4.379 WRT symbols per ASCII word occurrence. This
is an optimistic opportunity to spend more reasoning per lexical event at
similar compute, not a speedup guarantee: punctuation, OOV spelling and syntax
events still require work. Exact normalization, full-word versus hierarchical
heads, integer mass construction, mixed two/three-byte WRT intervals and tiled
training loss are specified in `research_round7_word_head_precision_plan.md`.
The global rank-16 head would require approximately 95.4 trillion scalar
multiply-accumulates and 5.96 trillion exponentials across 133.9 million words;
these are operation counts, not timings. The dictionary-tree head evaluates
at most 320 child scores on a dictionary path but may have different modeling
capacity. Price each head's actual parameters, including any learned biases.
A KDA state can retain an article's semantics while
bounded prior-article profiles retrieve entity/field distributions when the
current decoded title or completed link supplies a query. No future title or
unknown target word may be used for selection.

Test semantic memory against empty, shuffled, exact-string and same-budget
content controls. Limit total memory, including indexes and payload, to the
verified remaining RSS budget, rather than allocating another nominal 128 MB
on top of a near-limit decoder. Query at a few lexical/structural boundaries,
not by scanning all articles each byte. Every extra CPU operation affects the
prize feasibility.

Before this architecture, the remaining no-neural-retraining directions are
priced corpus macro/edit programs, causal numeric relations in tables, and
bounded cross-article semantic/co-occurrence predictors mixed externally.
The detailed finite-family tests and failure gates are in
`research_round7_theory.md`. These are hypotheses with potentially larger
coverage; none has a demonstrated 20% result. A changed word code or title
ordering must also pay its new dictionary/order and must account for the
frozen neural model receiving a different stream.

## Training under the $70 ceiling

The full plan is `research_round7_training.md`. Allocate **$4 to throughput and
export pilots, $12 to matched controls and the rate objective, $36 to the
winning continuation, $8 to export/evaluation and $10 contingency**. These are
spending caps, not reservations. Actual rental offers, storage and transfer
costs must be checked when renting. No rental has been started.

The reported original run used 208 RTX5090 GPU-hours; copying it fits $60 only
below approximately $0.288/hour before other charges. A focused continuation
is the appropriate budget scale. Repair token-weighted full-piece sampling,
complete prior coverage and checkpoint/optimizer restoration before increasing
capacity. A lambda=0 control must retain the baseline before spending on a
weight-rate sweep.

For a neural proxy measured in bits, use

    J_proxy = sum_t CE_bits(theta; x_t) + 2 R_quantized_weights(theta).

If CE is averaged over N symbols, divide the entire rate term by N. Lambda=1
is the direct bit-cost accounting coefficient under those definitions;
lambda=30 is an experiment, not a universally correct compression objective.
The proxy is useful for training but only final-coder NLL and exact exported
package size select the winner. Validate quantized codebook shape, BF16
rounding, PPMD priors, KDA reset/prefill, optimizer continuation and native CPU
inference parity before comparing candidates.

The architecture pilot uses word/byte hierarchical heads and bounded memory
only after the sampling/export control is trustworthy. Stop a costly branch
when matched evaluation shows no net payload-minus-model saving. Additional
budget is justified only by measured improvements and a throughput estimate,
not by an assumption that more training will produce a 20% result.

## Storage cleanup and recovery

Exactly six old, regenerable enwik8 probability matrices were deleted in the
previous session, each **2,158,737,536 bytes**, totaling **12,952,425,216 bytes**:

1. `/kaggle/working/hutter_lab/exp4/pmix_tok_dtok_distrib_ce_long2_ext.npy`
2. `/kaggle/working/hutter_lab/exp4/pmix_e2.npy`
3. `/kaggle/working/hutter_lab/exp4/pmix_e3.npy`
4. `/kaggle/working/hutter_lab/exp4/pmix_tok_dtok_distrib_ce_long3_r.npy`
5. `/kaggle/working/hutter_lab/exp4/pmix_tok_dtok_distrib_ce_long4_r.npy`
6. `/kaggle/working/hutter_lab/exp4/pmix_tok_dtok_distrib_ce_long_big.npy`

Reason: these were dense outputs from old experiments that could be regenerated
from retained scripts/models. Source, checkpoints, metrics and enwik9 assets
were preserved. Paths were resolved and checked as regular non-symlink files
within the intended directory and not open by active jobs. The fsynced deletion
ledger and before/after free space are preserved. No further cleanup of
pre-existing assets has occurred in this continuation. Native coders normally
remove their own generated temporary input files; the new lexical controls
retain these scratch files explicitly. A slow owned Python scorer was stopped only
after its faster native replacement passed parity.

The new session retains the preserved enwik9 ZIP, source/checkpoint tarball,
round-6 candidate, dictionary/order and all four probability slices. Selected
lexical source/model files were restored into isolated ephemeral build trees.
The original
large sparse training-prior files were not in the saved artifact. Training
must regenerate or deliberately replace them; their existence cannot be
assumed. Native research jobs have been capped at two simultaneous instances
because each reaches roughly 8.4 GB RSS. Sparse PPMD working files are large in
apparent size and are not compact preserved results.

## Required evidence before a record claim

Freeze source, model, dictionary, order, compiler flags and all seeds. Build
portable deterministic CPU inference; approximate reciprocal instructions
must not introduce cross-vendor probability differences. Run matched complete
compression and decompression and compare all 1,000,000,000 original bytes.
Count exact S1 and S2 files, peak RSS, actual disk allocation and one-core time
on the reference environment. Include global warm histories and the structural
tail. Component tests, cold slices and projected bytes cannot replace this.

The checkpoint file tracks jobs and subsequent results. An hourly follow-up
for the requested research week is configured, respecting account, execution,
approval and spending limits. It is not a promise of uninterrupted access:
Kaggle sessions expire and a new signed session may be needed. At4October
22:34UTC, the managed Goal still reports `usageLimited`, despite the restored
session connection. It has not been resumed automatically. The authorized
Kaggle validation jobs launched in this human-requested continuation may finish,
but autonomous Goal execution requires the user to resume that Goal in Codex.
The5October05:31UTC Goal read still reports the same usageLimited state.
After the earlier account-review reset, approved read-only status inspection
failed its kernel WebSocket connection; both /api/kernels and the saved
controller-log API returned HTTP404. This establishes inaccessible proxy
access, not job termination or data loss. The compact local evidence is
`research_round7_access_20261005T024430Z.json`. A fresh live Kaggle URL retaining
hp_round7 was requested once and supplied by the human as session355352151.
That access block is resolved. The direct human continuation recovers existing
native validation and adds residual/runtime diagnostics in the ordinary thread;
the managed Goal was not resumed or replaced. No cleanup deletion, neural SGD
or paid rental occurred. Existing and newly completed evidence remains local.
Research remains incomplete; no20% or absolute-optimum result is claimed.

## New residual diagnostics against the actual lexical checkpoint

The full tables and precise scope are in
`research_round7_lex_residual_findings.md`. Actual native final-coded word spans
carry77.258/82.198/82.028/85.295% of A/B/C/D bits. Words seen earlier in the
slice but first in the current article carry43.237/38.688/36.845/38.937%.
These are observed-cost categories, not side information for a predictor.
Every word-span attribution matches the union of its encoded bytes within
1e-4bits; XML tag words count as ASCII words and slice-first is not globally
new. The new checkpoint has no separately saved neural-cost trace here.

The anagram idea has a measured limited scope: a distinct anagram donor
earlier in the same article exists for only.080/.417/.426/.649% of all paid
bits. Earlier donors within the diagnosed2M slice cover4.463/6.053/7.051/8.941%.
A mechanism restricted to those spans cannot exceed that sampled bit budget,
even with free perfect prediction. This is not a bound on full warmed memory
or models influencing other positions. Letter order and donor/rule choice
still need coding; no tested anagram compression gain is claimed.

Repeated difficult words includebonaventura,pocahontas,uunet,anycast,
alexanderson,radiotelephone,groundskeeper andeavesdropping. Their total costs
remain small beside aggregate common words: in sliceD,"the" costs69740.84bits
over34378 occurrences, whereas"groundskeeper" costs128.66bits over6. Target
aggregate avoidable cost rather than individual spectacular surprises. An
article-conditioned word/spelling/syntax head plus bounded lexical memory has
the larger relevant budget, but the failed topic-only control already shows
that raw unigram topicality is insufficient.

Preserved exact source recipes and the T4 FP32/SDPA harness were recovered for
the training pilot. Current Python3.12.13/Torch2.10+cu128/Triton3.6 differ from
the archived project declaration Python3.11/Torch2.12, and T4 lacks native
BF16. Minimal pinned FLA/typing wheel availability and requirements were
audited without installation or model execution. Do not upgrade the complete
stack blindly, substitute neural outputs for true PPMD priors, or use an
unmatched GPU probability path to select a paid continuation. Native export,
piece resets, row alignment and final-coder controls remain mandatory gates.
The subsequent minimal probe installed only fla-core0.5.1/jaxtyping0.3.11/
wadler-lindig0.1.3 into an isolated ephemeral site. Global Torch is unchanged.
All three preserved checkpoints pass strict structural loading:6M12layers192,
8M16layers192 and10M12layers256. This proves shape compatibility; unstored
larger-model hyperparameters remain assumptions. A no-SGD pilot is queued
after native recovery. It generates actual native reference/lexical
probabilities and PPMD priors, tests full prior equality, and gates larger-model
GPU logits on a6M native/GPU control. Its outputs will be sampled neural
diagnostics, with full package/CPU accounting still required.

A separate no-neural-retraining branch replaces paid article-topic hints with
full-support latent word counts learned from the decoded prefix. Eight/sixteen
topics have whole-article retention or exponential decay127/128 and255/256
per completed dictionary atom; these are decay time scales, not hard expiry
after128/256 words and not a count of all ASCII words. Responsibilities
are quantized to integers totaling4096. All dictionary, literal, syntax, case
and escape choices are charged by a normalized neutral/specialist mixture.
The dictionary-derived rank/hash priors are deterministic; no topic table or
future article selector is stored. The equations and native subtree plan are
in `research_round7_causal_latent_plan.md`. Native code and warmed CPU/RAM
costs remain unmeasured, so this is a screen rather than an accepted archive.

An initial synchronization defect was found in the reused root scorer: it
activated at the beginning of the first page marker, before that marker had
been completely observed. Only the owned exploratory latent screen was
stopped; all files were preserved and native recovery kept running. The v2
scorer activates after the complete decoded marker and checks post-marker
byte accounting. Earlier tiny root/new-mention gains are provisional pending
that correction. No result from the superseded latent run is promoted.

V2 loses1.562/2.462bytes on completed B/C. Auditing its prior strength shows
that the global prior can outweigh learned topic counts by roughly128/256
times for balanced8/16topics. An isolated V3 instead normalizes that prior
and gives each topic a fixed64-word pseudocount, allowing learned mass to
grow with prefix exposure. Its initial predictions equal V2. The same event
charging, alpha mixture, completed-prefix semantics and integer accounting
are retained. One B/C comparison is queued behind existing jobs; the equations
and assumptions are in `research_round7_causal_latent_plan.md`. This corrects
an experiment-design weakness; it does not promise a semantic breakthrough.

`research_round7_residual_topic_tilt_plan.md` specifies a separate conditional
correction: tilt the baseline's bit odds by a topic-versus-global subtree
density ratio, then normalize both outcomes. This can preserve syntax already
learned by the baseline, unlike a standalone topic unigram. Its local bit
normalizer is explicit and its probabilities differ from a globally tilted
word model; neither has been tested here. A native final-bit trace and
identity/round-trip/resource checks are prerequisites. Observed word costs
alone cannot evaluate the global word normalizer, and omitting that term
would give invalid apparent savings.

The information-theoretic interpretation and matched memory controls are in
`research_round7_memory_information_plan.md`. A memory derived from the full
decoded prefix adds no outside information, yet can recover relations omitted
by a finite predictor's state. Expected log-loss improvement separates this
conditional information from baseline and candidate approximation errors.
Repetition frequency alone estimates none of those terms.

The human supplied `idea_arch_1.txt` and `idea_arch_2.txt`; both were read in
full. Their probability-space placement/echo/residual proposals are being
tested as distinct finite families. The operational registry, mathematical
corrections, all completed/pending experiments, controls, commands and restart
requirements are in `research_round7_pre_experiment_report.md`. The corrected
topic V2 loses2.497/1.562/2.462/2.485B A/B/C/D; fixed-prior V3 still loses
1.539/2.457B B/C, so neither is promoted. Four2M independent native decodes
now pass length/SHA256. These validate sampled WRT coding, not full enwik9.

The first neural pilot failed on an -e-only boundary-save flag used with -n.
Its repaired V2 preserves the failure, validates token-derived complete marker
boundaries and excludes only the uncoded EOF row from parity. Both native
controls now succeed with exactly matching PPMD priors. A separate K8 structural
echo screen uses prefix/suffix, deletion signatures, independent letter moments
and matched random controls, plus exact/rank/global controls. Its128-slot
states decay at127/128 per completed dictionary atom. All outcomes, including
partial EOF code/escape prefixes, are charged. The following completed results
supersede the initial pending state; no trained residual controller or signed
word tilt has been evaluated yet.

At5October08:58UTC the repaired neural pilot has completed but FAILS numerical
fidelity: mean absolute actual-cost difference.0260231bits/symbol, max2.01116,
mean native-to-GPU KL.00220386bits and max probability difference.353175.
Its predeclared gate correctly skipped larger checkpoints. Matching priors,
complete-reset rows and row-shift diagnostics narrow the investigation but do
not fix it; results/probability evidence/source hashes are preserved.

The original K8 lexical echo screen completes all four2M native-cost slices:
A -2.496659B, B +4.567020B, C +.097715B, D +2.099424B. Total+4.267500 ideal
bytes before package/runtime costs is insufficient for native integration.
The separate causal256-word lag diagnostic covers only5–19% of suffix costs
for individual structural channels, with substantial matched-random coverage.
This is hypothetical support cost, not achievable saving; overlapping
relations/lag bins cannot be added. Exact-repeat coverage reaches about22–23%
on B/C but already includes many easy repeated words and no selection cost.

A consequential implementation defect was measured and repaired: the capped
moment graph recovers only3.947% of exhaustive top8 neighbors over133 fixed
dictionary queries. Independent integer moments, exact-square-root feature
quantization Q1024 and bounded exhaustive score blocks recover99.248% of the
original float-score neighbors. Scores stay below2^24, allowing mathematically
exact FP32 dot products and deterministic integer score/ID ties. Research GPU
construction takes6.17s with267MB peak allocation; CPU-only reconstruction of
every356120 neighbor ID and score matches exactly in30.67s on one core, with
832904KiB peak prototype RSS. This validates candidate construction, not a
compression breakthrough or native prize implementation. A fixed echo
comparison using this corrected graph is active as PID390. At09:07UTC its
A/B results are-2.496619/+4.542207 ideal bytes; C/D remain pending. Improved
neighbor retrieval has not produced a meaningful compression gain on A/B.

Even exhaustive moments rank know1063rd for no; nearest spelling moments do
not encode the proposed phonetic/semantic relation automatically. Normalized
moment collisions also lose length information. The subsequent high-value
hypothesis is directed, context-conditioned placement and normalized residual
odds, with phonetic/length features as separately controlled inputs. Mere
similarity, availability and keep-alive mass are insufficient. Current/Pending
methods, outputs, costs, restart commands and $70 gates are fully documented in
`research_round7_pre_experiment_report.md`. No paid compute, retraining or new
deletion has occurred; no20% model/package reduction is demonstrated.

Read-only follow-up5October09:10UTC: the existing corrected-echo job remains
active with no newly completed slice; A/B results are unchanged, C/D pending.
The managed Goal still reports usageLimited; no new research job, retraining,
spending, deletion or Goal mutation was performed during this heartbeat.


## New community placement proposals and measured continuation,5October13:38UTC

The proposals contain a valid causal mechanism: decoded words can generate
timed candidates and syntax can select/suppress them. Their examples are not
evidence of a substantial residual gain. Structural similarity does not
automatically encode semantics; glyph moments are linear transforms of letter
moments, and the five proposed polynomial moments have rank3. Literal Wordle
guess/correction is a different probability model, without an inherent entropy
advantage. Direction, distance, normalization, selector cost and delayed causal
updates matter. The precise derivations and code are in
research_round7_placement_theory_and_experiments.md.

Recovered completed I03b gains only4.243968124 ideal bytes/8M before overhead.
The actual new directed lag test I04 loses7.847331710B/8M. A subsequent
quantized final-bit residual pilot loses4.017518270B/64K, after exact native
archive/byte-cost/independent-decode controls passed on both32K slices. These
results reject deployment of these tested versions; they do not prove that
every placement, retrieval or trained residual architecture is futile.

The new trace instrumentation preserves original predictors and outputs final
uint16 p(bit=1) before Perceive. V1's missing timing utility failure is retained;
V2 reused its build with Linux wait4 and explicit -d. Native trace user times
66.852/66.098s, peaks5651732/5798496KiB; both archives/costs match reference
exactly and independent decoded inputs match. Traces and dictionary are local.
Four2M final-bit collections are now active under controllerPID1097; C/D native
children1101/1102 were active13:36UTC and A/B queued. Archive bytes/cost arrays
must match preserved controls completely before any trace is used as evidence.

A subtle placement issue was tested rather than ignored: I/i is literal and
absent from this dictionary, so DICT lags differ from English word lags. A
separate full-ASCII audit counted1,884,022 words in these four2M slices and no
now→know/know→now at word lags1–4. The's dictionary codes average1.907 bits,
of's1.094; all12 named/common DICT labels carry only5.456% of full native ideal
bits. These restricted sampled budgets, excluding other words/literals/case,
are not global bounds. Broader content-word first mentions remain the larger
target. Local assessments preserve both lag units explicitly.

No meaningful/20% compression breakthrough or absolute optimum is claimed.
No neural retraining, paid rental, project deletion or Goal mutation occurred.
The pre-experiment registry includes all exact sources, jobs, parameters,
tests, failures, gates and continuation steps. Reuse active native work.


## Measured constructor results and current handoff,5October2026

Updated 2026-10-05T14:23:29.109612+00:00. I11/I11b/I11c all COMPLETE; no constructor or native trace
process remains active. The three experiments made56 matched-codec packet
comparisons over four2M original WRT slices. All56 exact raw reconstructions
and compressor roundtrips PASS; every candidate is larger on every slice.
The following aggregate compares each fixed representation with its own
matched original-source codec. These are not cmix/Hutter record deltas.

| Representation | zlib9 increase | LZMA6 increase |
|---|---:|---:|
| Framed gaps: direct | +21.623% | +20.415% |
| Framed gaps: ordered_templates | +18.847% | +21.493% |
| Framed gaps: multiset_plus_order | +19.473% | +22.204% |
| Two-byte marker: direct | +6.121% | +7.882% |
| Two-byte marker: constructor_word_table | +3.559% | +5.788% |
| One-byte marker: direct | +4.628% | +6.695% |
| One-byte marker: constructor_word_table | +2.066% | +4.601% |


The one-byte-marker paid word-table variant is the least costly skeleton:
zlib original3,623,465B vs candidate3,698,340B (+74,875B,2.066%);
LZMA original2,894,828B vs candidate3,028,020B (+133,192B,4.601%).
Incremental decoder/program cost is excluded from these packet differences,
so adding it cannot rescue these already negative results. Per-slice values,
source/dependency/input/cost hashes and timing are in the preserved JSONs.

The fixed176-word lexicon matches629,700 of1,884,022 ASCII word events
(including markup), but its disjoint original word/case spans carry17.200%
of the sampled native ideal bits. The per-slice shares are7.922/18.083/
17.777/19.690%. This is an accounting result for this heuristic and these
slices, not a universal function-word inventory or whole-corpus bound.
With every other cost fixed, even zero-cost encoding of just these selected
spans cannot deliver20% on this sample. A20% overall target needs gains on
content/structure too, or a different broader scope with measured headroom.

87.345% of1,254,326 constructor gaps have length zero or one, offering no
permutation sharing. Merging ordered case-folded tuples into multisets reduces
distinct template counts by only2.883–6.167% within the four slices. The
observational H(order|multiset) total is11,573.927bits. This is a fitted
descriptive statistic, not an untransmitted probability table or achieved
code length. The pilot's exact raw multiset code pays order ranks; a better
contextual order model could reduce their cost. It does not remove the paid
content stream, slot/escape information or lost cross-channel correlations.

I11 consumed175.321 prototype CPU seconds and176.164 wall seconds; I11b
45.423/45.432 and I11c40.640/40.649s. Reported process peak RSS is593,568/
593,696/593,952KiB. These are Python experiment/runtime peaks and include
process setup/inheritance; they are not measured standalone C++ decoder
requirements, full-corpus runtime, or a qualifying CPU package. No new
parser/weights, neural training, rental, deletion or Goal mutation occurred.

The native final-bit collector also completed all four2M slices with PASS.
All128MB of uint16 traces and8MB original inputs are local; all source input,
trace and preserved native archive hashes match. Independent local blockwise
reconstruction validates64M actual coded-bit probabilities in[1,65535] and
maximum byte-cost error below9.54e-7bits (fixed gate1e-4). Native archives and
EVERY prior float32 byte cost are identical to the preserved baselines.
Individual native user CPU is1236.291/1312.900/1292.865/1313.031s for A/B/C/D;
peak RSS max6,043,696KiB. This proves measurement identity, not new compression.
Local evidence: research_round7_finalbit_local_validation.json and
research_round7_lex_finalbit_2m_v1_{manifest,results}.json.

### Next steps and stopping gates for this hypothesis

Do not repeat the losing static layouts or spend$70 merely to reproduce their
generic-codec screens. A still valid hypothesis is a compact CONDITIONAL gap
model exploiting paid decoded left/right content and a better content model.
It needs a new joint distribution Q_C(C)Q_A(A|C)Q_G(G|C,A) and total-length
evaluation, not the old transformer's scores applied to reordered bytes.
The controlled no-retraining alternative is a prefix-only syntax/template
residual on the original final-bit coder, with normalized integer probabilities.

I12 prefix-only constructor-run expert remains PLANNED, not running. It should
use completed ASCII words (including literal I/i), a fixed constructor lexicon,
bounded ordered run/trie state, left content class/ID and punctuation/markup
state. Commit a word only when the decoded separator establishes its boundary;
never choose an expert from the target's future word/length/POS. Maintain a
neutral expert and a global non-constructor fallback; preserve nonzero support.
Build the expert's full word-trie branch probabilities and compare its binary
log-odds to its global-prior expert, then apply a clipped signed residual to
the actual native uint16 p. Quantize every candidate and mixture. Do not add
independent word gains or use a target-dependent activation mask. Test neutral
byte-for-byte identity, all escape/case/EOF bits, sparse memory rescaling and
reset semantics first. Preregister state/row caps and scales; screen A/B32K,
then larger regions ONLY if a priced signal survives. Freeze on development
and confirm on new E/F regions; these A/B/C/D are already examined research
data. A positive screen still needs a native archive, independent decode,
full package bytes and CPU/RAM verification.

Existing pending I04b retrieval/I06 syntax-source-surprise/I07 memory controls/
I08 phonetics/I09 hazards/I10 trained shared residual/P01–P05 retain their
own registered gates. Prioritize high-cost content/first-mention residuals
alongside grammar, given the measured constructor budget. The staged$70
training plan remains unchanged, with no spending or promised rental rates.

### Exact recovery commands and evidence

Use the newest user-supplied session credential only via HP_KAGGLE_BASE, and
the existing kaggle_research_client.mjs bridge. Kernel currently
788f499d-4818-4c63-974e-bc26b298ddf0, session355454655. Read-only status RPC:
research_round7_constructor_all_active_status.py for I11/I11b/native trace;
research_round7_constructor_skeleton_v2_status.py for I11c. All are complete;
no launcher should be run again against its existing exclusive directory.

Directories/logs: constructor_split_v1 / constructor_split_v1_controller.log;
constructor_skeleton_v1 / constructor_skeleton_v1_controller.log;
constructor_skeleton_v2 / constructor_skeleton_v2_controller.log;
lex_finalbit_2m_v1 / lex_finalbit_2m_v1_controller.log, all below hp_round7.
Preserved compact outputs are locally prefixed research_round7_ plus the
corresponding directory/log names. Sources, launches and preregistrations are
also local. I11c source was generated by checked anchor replacements without
editing the measured I11b source. No deletion was needed; persistent free
space at the final existing-job check exceeded8.7GB.

Local reproduction/validation with the bundled Python:

    python research_round7_constructor_assess.py
    python research_round7_constructor_skeleton_assess.py v1
    python research_round7_constructor_skeleton_assess.py v2
    python research_round7_finalbit_local_validate.py

The first constructor assessment has now verified all four local original
inputs, costs, source and result equality. The final-bit validator independently
checks probability alignment/reconstruction and hashes. Constructor source
scripts use Linux resource accounting; run full original experiments on Kaggle
or Linux rather than silently deleting that instrumentation on Windows.
Managed Goal remains usageLimited; no automated continuation may bypass it.
Latest user-directed continuation performed this work, without resuming it.
No20% gain, absolute optimum or qualifying archive breakthrough is claimed.

Read-only heartbeat5October14:27UTC confirmed the latest session remains
accessible and saved completion manifests/source identities are unchanged.
Goal remains usageLimited; no new jobs, training, spending, deletion or Goal
mutation occurred. The already-requested resume action was not requested again.
Compact status receipt: research_round7_heartbeat_20261005T142734Z.json.

Heartbeat5October16:47UTC: Goal still usageLimited, and no new experiment was
launched. Remote manifest checks returned no diagnostic text and a restricted
kernel-list fetch failed; this does not establish session expiry. All prior
completed results are local; no new measured result was retrieved. Preserve
the existing pending resume request without repeating it. Diagnostic receipt:
research_round7_heartbeat_20261005T164733Z.json. No spending/training/deletions.

<!-- final-batch-20261005-start -->
## Completed measured batch

Finalized 2026-10-05T19:19:30.342424+00:00; Kaggle session355529591. Positive values mean savings. All quantities below are bytes, not percentages of enwik9 unless explicitly stated.

| Final-coder screen | A (2M) | B (2M) | C (2M) | D (2M) | Total |
|---|---:|---:|---:|---:|---:|
| Shared causal experts (actual uint16) | -1.019695 | +0.009157 | +0.141542 | +2.600291 | +1.731295 |
| Corrected root/new-mention (ideal event likelihood) | -2.493234 | +16.568967 | +12.846215 | +14.969378 | +41.891326 |
| A/B-fitted 512B integer calibration (ridge64) | +28.998475 | +46.746481 | +35.678382 | +36.744528 | +148.167866 |

Shared experts:3393.031207CPU user seconds for four2M screens, peak96,700KiB. Their best fixed non-identity arm is the mildly negative anagram correction in every slice, and it still loses2.219/5.580/6.499/8.560B. Positive online mixture results do not establish a profitable packaged expert. Root/new-mention fixed non-neutral arms also all lose. Root wall time is1736.529s; independent process CPU and peak RSS were not captured for that screen and are not invented. Its bounded graph capacities are4096rows/262144edges per graph. Neither prototype is promoted.

Finite numeric programs lose0.498887388ideal bytes in aggregate over8M; every fixed numeric arm loses. The four frozen template packets reconstruct raw bytes exactly but are larger than matched generic-codec baselines: zlib9 +4.10/+5.54/+5.30/+4.88%; LZMA6 +5.75/+4.69/+4.48/+4.05%. Even the relaxed native covered-cost minus two pool copies is negative on all four. No native macro result is claimed.

### Native confirmation on fresh E/F

| Slice | Input bytes | Actual archive saving | Ideal saving | Candidate CPU s | Decode CPU s | Decode peak RSS KiB |
|---|---:|---:|---:|---:|---:|---:|
| E | 65536 | -1 | -0.607207 | not captured; reused E | 79.867374 | 5895500 |
| F | 65536 | -3 | -3.235477 | 81.47264 | 79.385122 | 5730136 |

Neutral candidate/reference archive and every final probability match exactly; all candidate integers match independent rational replay; both independent raw decodes reconstruct the exact inputs. The A/B table was frozen before E/F. Fresh confirmation does not justify promotion: small old-region likelihood gains are not a significant archive improvement. Model cost is512B per stored copy, two copies in the current package; the laboratory wrapper adds1016executable bytes before final packing and option overhead. No full-package net saving is measured. The original transformer weights were never changed. E compression timings were lost when v3 failed before persisting its row; v4 reused these completed outputs and reports the timing as unavailable rather than repeating them.

### Training-data storage and provenance

Old-FX2 preparation and inverse are complete:586,459,020transformed bytes invert to all1,000,000,000original bytes with SHA256159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc. This is a preprocessing roundtrip; there is no full entropy-coded qualifying candidate. Preparation CPU568.392895s/RSS7,120,448KiB; inverse CPU245.599285s/RSS1,515,868KiB.

The262144-row native-prior probe takes4.043254CPU seconds/RSS1,136,116KiB and yields107,479,040B of genuine float16 priors. Raw Zstandard9 stores50,901,611B (47.35957% of raw), with four-block in-memory decode0.285259s. All48 tested representation/codec cases round-trip exactly. LZMA3 is smaller but slower. Full Zstandard9 storage extrapolates113.875GB if the early-sample ratio holds; this is not a capacity guarantee. No full priors or production lexical-order data have been prepared. Training-data storage reductions are excluded from submitted archive improvements.

### Concrete continuation and remaining work

Read `research_round7_finetuning_execution_plan.md` and `research_round7_training_contract.json`. The plan contains exact data shifts, legal-piece sampling, loader read-amplification controls, native/GPU layer parity, F0 load/export identity, conservative32-update F1 screens, two-copy MDL units, conditional F2–F5arms, optimizer/checkpoint schedules, token-throughput pricing, strict CPU/RAM/disk accounting and the$4/$12/$36/$8/$10budget caps. No GPU rental, neural training or expense has occurred.

The finite registered bounded batch is complete. P01 full production package/reference validation remains gated; P03 larger suffix/word-head/native improvements are unimplemented beyond the measured calibration arm; P05 production lexical full stream and complete exact priors remain pending. Full learned hazard/counterfactual TTL, link-key retrieval, pair-HMM/geometry architectures and bidirectional two-pass neural training are hypotheses, not completed experiments. Their narrower screens are described explicitly. The numerical neural parity gate still fails, so the first recommended work is fidelity repair and F0/F1, not a long paid run.

Evidence: `research_round7_completed_20261005T1912.zip` (SHA256d4c2ade0be91480c3620049dc4cfea905b8259a6a1cdeebd7db39ea46e1ef3cf), its hash-checked40-file index, `research_round7_native_calibration_20261005` and `research_round7_final_batch_summary.json`. Exclusive launch directories and failed attempts are preserved. No manual project deletion or managed Goal mutation. Signed session credentials remain outside reports.
<!-- final-batch-20261005-end -->

Research-direction audit,6October2026 IST: see
`research_round7_record_breaking_next_stage.md`. The actual learned relation,
contextual rejection, survival and residual architectures in the idea files
have not been trained; negative fixed-boost screens do not exhaust them.
No matched full-history production comparison has been executed. The next
independent-head pilot can use native causal features/final probabilities
without waiting for a faithful GPU port of the core model. Paid article-level
latents and a fully priced content-first grammar codec are new hypotheses,
not measured results. The54.9KB packing result belongs to the older FX2 Q4
model, not a validated lexical C3 package saving. No new job, neural training,
paid expense, deletion or Goal mutation is claimed in this direction audit.
