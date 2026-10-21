# What the new competitor changes in this research program

6 October 2026. Read-only audit of six preserved source files from cmix-neif1.0, commit `1c9ea5ed57ec9718bcb681d20b79e81a60b7a728`. No competitor code or model has been adopted or executed here. Its reported 95,914,051B result is pending verification, not an awarded/local result. Source provenance is in `research_round8_neif_tree.json`; the preserved files are under `research_round8_neif_source_audit/`.

## Causal reminders support the user's memory idea

The source implements a prompt automaton driven by decoded titles, headings, links and redirects. Parameters and feeding order belong to the training contract; the token alphabet has 208 entries and the prompt schedule has bounded budgets and reset conditions. This is a concrete way to retain useful decoded context without shipping repeated sentences. It still costs model/state, inference work and a compatible training distribution. Porting a reminder schedule to the existing 205-token core is not an equivalent frozen-model evaluation. [Prompt contract](https://github.com/marwoelk/cmix-neif-1.0/blob/1c9ea5ed57ec9718bcb681d20b79e81a60b7a728/src/tf1/tf1_prompt.h), [implementation](https://github.com/marwoelk/cmix-neif-1.0/blob/1c9ea5ed57ec9718bcb681d20b79e81a60b7a728/src/tf1/tf1_prompt.cpp).

Inference from this code: the user's TTL/context-miner direction deserves a trained, state-consistent test. Our finite title/neighbor screens do not implement the same architecture and cannot settle that family. A useful descendant is a causal reminder policy with an empty-reminder arm, matched repeated-token work, random reminders, and the same parameter budget. An offline encoder's future-dependent choice must be encoded; a decoder-built rule may instead learn deterministically from past decoded events. Additional synthetic prompt tokens require training/prior alignment, not just insertion into an existing state's update stream.

## An error-correction head has much more capacity than a tiny scalar gate

The competitor's bit head is a recurrent correction model with explicit staged features, sequence resets, observation after the bit and a trained/online transition. Its code isolates the correction from the underlying predictor's state updates, and caches sketches rather than recomputing a large projection per bit. These details directly inform the independent residual route in this project. [Bit-head source](https://github.com/marwoelk/cmix-neif-1.0/blob/1c9ea5ed57ec9718bcb681d20b79e81a60b7a728/src/bit_head.cpp).

Inference: the negative fixed-cache experiments reject specific signals and low-dimensional gates. They do not reject nonlinear state-conditioned error correction. Conversely, a recurrent residual's parameter count, staging features and online optimizer can exceed the remaining whole-program RAM or CPU budget. Begin with exact native trace observation, neutral output initialization and an equal-capacity generic control. The current paired-error memory solves a locally shared intercept; its mathematical root optimum is not the optimum of this recurrent class.

## Word structure and placement can be modeled, but not for free

The online word-label source uses a log-bilinear model with shared word embeddings, lagged context and a topic summary. Its declared vocabulary and embedding/node shapes imply approximately 71MB of raw float tables before other state. This is an architectural comparator, not spare memory in the current program. [Word-label implementation](https://github.com/marwoelk/cmix-neif-1.0/blob/1c9ea5ed57ec9718bcb681d20b79e81a60b7a728/src/word_label.cpp).

The current C3 native peak leaves only 615,424B below a decimal 10GB interpretation. A new large table therefore needs a measured trade against an existing allocation or a new lower-memory package. Existing KVI8 cannot be counted twice as a fresh saving. Do not compare nominal compressed model bytes to raw runtime table bytes as though they were interchangeable.

Inference: constructor/content roles are useful feature bases for a shared word predictor, relation gate or residual. The set-only formulation loses order and multiplicity. For a bag with m words and counts n_j, a generic ordering description can require log2(m!/product_j n_j!) bits; language context can reduce that conditional cost, but the ordering remains a coded event. An infill codec must first pay/decode its right anchors and slot boundaries. Its total factorization is L(content,slots)+L(ordered constructors|content,slots)+L(exact exceptions), plus model/code costs. Under an ideal joint distribution, changing a bijective coding order does not lower joint entropy; practical gains come from a lower approximation error or smaller model description.

## Letter algebra is a structured basis, not a guaranteed probability increase

Anagram, phonetic or subletter relations can define A(u,w), a deterministic relation kernel over decoded words. A valid proposed categorical mixture is q(w|h)=(1-g(h))*p(w|h)+g(h)*sum_i v_i(h)*A(u_i,w), with A rows normalized, v_i summing to one, g in [0,1], and spelling/fallback support fully accounted. For the native dictionary-code path, the categorical law must induce normalized child-bit probabilities on the existing prefix tree. Arbitrary boosts without a normalizer over all supported outcomes are not a codec.

The useful new hypothesis is to learn acceptance/rejection and signed residual evidence conditional on role, native confidence and code prefix. “No” and “know” can be related yet inappropriate in most contexts. Include false triggers and matched frequency/permutation controls. A low-rank or generated relation basis may reduce stored parameters; it earns promotion only if its own description plus the final payload is smaller. The attached curriculum proposal supplies an offline learning strategy for this gate, not proof of conditional information in those relations.

## Training chain informs the budget rather than guarantees a reproduction

The published training recipe describes a long multi-GPU chain with separate precision/export phases and schedule/optimizer continuity. At its stated four-card epoch rate, its 1,000 bf16 epochs alone correspond to roughly 400 GPU-hours before later phases. This arithmetic is a cost-scale inference from the author's recipe, not a measured throughput on our host. [Training recipe](https://github.com/marwoelk/cmix-neif-1.0/blob/1c9ea5ed57ec9718bcb681d20b79e81a60b7a728/training/tf/3_train/README.md).

The $70 project should first test small residuals on exact native features and warm-start only a compatible/exportable core. A scratch reproduction, a compatible checkpoint continuation and a small independent correction are different experiments. Each needs its own package, byte alphabet, priors, prompt schedule, precision and CPU/RAM manifest. This code audit creates better combination hypotheses; it is not a numerical forecast of post-training archive size.
