# What decoded-prefix memory can and cannot buy

This provides a theoretical interpretation, not an empirical entropy estimate
or a proven compression lower bound for enwik9. The prefix-derived memory
experiments and residual diagnostics are the available measurements.

## Distinguish raw history from the predictor's representation

Let H be the complete decoded history and M=f(H) a deterministic memory.
Then conditional mutual information I(W;M|H)=0: memory adds no information
outside the history. This does NOT mean that it cannot improve a finite
predictor. Let B=g(H) instead be the restricted representation actually used
by a baseline model. It may omit relations that M retains. Under a specified
data-generating distribution, I(W;M|B) can be positive.

Thus an assertion such as "99% of words already appeared" is insufficient.
The compressor needs to select the next word from alternatives using the
available prefix; mere membership in the seen vocabulary does not supply
that selection. Mining the actual decoded words, their titles and relations
can be useful. Mining a model's incorrect guesses supplies a deterministic
feature of the same history and only helps if that feature improves its
finite approximation. It must never substitute the guess for the actual
decoded symbol.

## The log-loss decomposition

For normalized baseline P0(W|B), normalized candidate P1(W|B,M), and true
conditional distributions P*, expected ideal gain in bits is

    E log2[P1(W|B,M)/P0(W|B)]
      = I(W;M|B)
        + E_B KL_bits(P*(W|B) || P0(W|B))
        - E_(B,M) KL_bits(P*(W|B,M) || P1(W|B,M)).

The first term is additional predictive information retained by memory;
the second allows correction of the baseline's approximation error; the last
charges candidate approximation error. These terms cannot be read off a
list of difficult words, repetition rates or an unpaid best-context oracle.
A uniform empirical sample of one unique high-dimensional state per corpus
position can trivially memorize outcomes, so naive mutual-information
estimation on those states does not establish an attainable coding gain.
Only a priced, causal executable and measured likelihood/package can do that.

If all actual gains came from the133,922,554 ASCII-word events, the accepted
record's strict20% target would require approximately1.20 final bits saved
per word before extra components. A rank16 int8 residual table alone adds
about.0851bits/word across two copies, so the planning threshold rises to
about1.28 before code, scales, other weights and changes in runtime. This is
a budget conversion, not a claim that the information or a feasible predictor
exists. Word-span categories overlap; never add their residual budgets.

## A realizable test of memory content

Keep the same parser, model weights, capacity and operations in paired arms:
no memory; empty memory; causal real memory; identically sized shuffled
contents; exact-string donors; title/link-only donors; learned summaries.
Treat empty slots as real allocated capacity and account for retrieval work.
For shuffled contents, preserve availability constraints and identify the
shuffle policy; never allow a future article to become a donor by shuffling.
A post-hoc shuffled-content ablation is diagnostic unless its decoder can
construct the same shuffle. It cannot itself be a compression submission.

Measure all event outcomes, including failed retrievals, literal words, syntax,
escape and case costs. Record gain by first-current-article mentions, nearby
repeats, distant repeats and literal spelling, plus total gain. The per-class
analysis explains a mechanism; total normalized likelihood selects it.
For a frozen baseline, use independent slices before integrating into the
native coder. A retrieval oracle establishes at most a restricted diagnostic
ceiling and must include a paid selector in any claimed realizable result.

Trainable memory selection may use future recurrence/gain as a TARGET during
training; it may not use those future labels as inference inputs. Infer from
completed decoded facts, record availability offsets, and assert those offsets
are less than or equal to the current position. Price trained selector weights
and architecture code in every required package copy.

## Selection, TTL and compute

The useful quantity is expected remaining final-bit gain conditional on the
current available prefix, minus the operational cost of storing/querying the
item. Prefix-derived storage is free of transmitted bits only when reconstructed
deterministically; it still consumes RAM, CPU and implementation bytes. Use a
bounded memory and deterministic replacement. Exponential decay and hard
expiration are different policies; specify which event advances their clocks.

For a fixed family of normalized specialists j, a Bayesian prequential mixture
updates from observed likelihoods and pays selection regret. Its likelihood
satisfies L_mix <= L_j - log2 pi_j under the exact corresponding whole-stream
mixture. Splitting by decoder-known contexts creates separate regret terms;
changing expert identity or forgetting schedules changes the model and needs
its own contract. A convenient half-mass neutral expert limits deterioration
but does not guarantee improvement. Best-per-event selection without encoded
choices is not that mixture.

CPU-limited evaluation should maintain a Pareto frontier of complete bytes,
each executable's independently calibrated runtime, warmed RSS and disk.
Without a measured margin below the runtime/RAM limits, a richer memory or
larger frozen model cannot be recommended as a qualifying solution even when
its sampled neural loss is lower.
