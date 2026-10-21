# Paid prediction-policy TTL and exact finite segmentation

Registered 6 October 2026 after A/B conditional-gate results, before schedule results. This is an altered TTL/paid-latent hypothesis, not a claim to implement learned lexical memory or an absolute optimum. No original neural parameters change. All original data and jobs are preserved.

## Mechanism and legality

Use the same fully normalized Q16 fixed candidates as conditional_gate_v1. The encoder may inspect a whole segment to choose its prediction policy, because it sends that choice and segment duration before the segment. The decoder therefore knows the policy legitimately. It computes the same prefix-derived spelling/syntax features and native baseline probability; original core updates still follow decoded original text. Side bits never masquerade as original text updates.

Divide the original WRT byte positions into deterministic 1024-byte units, with a final short unit. Before the first completed page/title synchronization, every option is exact native identity. A program consists of contiguous segments covering all units. Each segment carries a policy ID and positive unit count. For a K-option family, prior probability is 1/2 on identity and 1/[2(K-1)] on every other option. Encode duration with an Elias-gamma integer code, costing 1+2 floor(log2 length) bits. The reader knows total original WRT byte count and stops after exactly covering it. A global one-bit mode selects either ordinary identity-only coding or the segmentation program. Header/interface details need an actual production implementation before promotion.

Let A_c(j) be the accumulated Q16 log-likelihood gain in bits of policy c through unit j. The optimal net segment-program gain in this finite grammar is

D(0)=0;
D(j)=max_{0<=i<j,c} [D(i)+A_c(j)-A_c(i)-L_ID(c)-L_gamma(j-i)].

An induction on the last segment proves this global minimum codelength within the declared grammar. The output saving is max(0,D(B))-1 bits, including global mode. This is distinct from an unpaid best-expert oracle. Costs of candidate code, graph reconstruction/storage and native runtime are additional. Floating gain arithmetic is research instrumentation; exact integer archive comparison is the acceptance gate.

## Registered comparisons

Solve four separate K=25 programs (generic, random+run, grammar joint, geometry+run) and a K=97 combined family (one identity plus 24 nonneutral entries from each arm, even when some predictions coincide). All choices and durations are priced. The large combined family pays a larger policy code. Report fixed best expert, homogeneous mixture, unpriced block oracle, priced optimum, number of segments and all selected spans separately. No family or slice is claimed untouched: A/B develop; C/D have been examined. This schedule is optimized per encoded input, so its transmitted selection bits, not an unpriced held-out choice, make it a legitimate corpus-specific codec proposal.

## Engineering and promotion gates

Reuse the tested causal parser and fixed candidate implementation without changing them; cache cumulative per-unit gains only for encoder search. Decoder need not store or receive those research arrays. Independently exhaust all compositions/policy assignments on a small synthetic grid and compare the DP. Include first partial synchronization, incomplete code/escape at EOF, one-unit segments, full neutral mode, and exact segment coverage. Record source/binary/input hashes, CPU/user/system/RSS and all header charges.

If net gains do not cover a compact production module, no native package is claimed. If promising, integrate the header/policy schedule in a single real range stream with an immutable baseline predictor trajectory, verify zero mode and independent full decode, then confirm fresh production regions. Larger grain, causal schema-aligned boundaries, better source features, and a title-conditioned policy prior are distinct next variants with separately charged descriptors. A schedule gain alone does not prove spelling geometry or grammar helps: compare its increment above generic and random schedules.
