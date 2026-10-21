# P5 paid constructor-run templates with right-context backoff: frozen protocol v1

10 October 2026. Implements PENDING_EXPERIMENTS_HANDOFF.md §P5 as a new complete reversible
codec, `hutter_research/template_codec.py`, and job, `hutter_research/cpu_round14_template.py`.
The existing `constructor_codec.py` is unchanged and is the matched baseline.

## Codec (all costs paid in the archive)

* Paid channels identical to constructor_codec: lexicon, layout gaps, constructor/literal
  flags (fixes every run length), literal/OOV words, case; each is gzip in the archive.
* One range-coded run stream. For every maximal constructor run of length n (known from
  the flags), when a dictionary exists: a **branch flag** (adaptive binary, keyed by
  min(n,4)), then either
  - **direct**: the unchanged constructor_codec model (coarse anchor class, previous
    constructor, alpha 4); or
  - **template**: template id (adaptive, keyed (min(n,4), anchor class) with backoff to
    min(n,4) and global; support = filled slots), edit count e ≤ E (adaptive, keyed
    min(n,4), only when E > 0), then per edit: type sub/ins/del (adaptive), position
    (uniform over template length + 1), symbol for sub/ins (adaptive).
* After either branch the direct model is updated with the run's ids (post-observation),
  so direct statistics are branch-independent.
* Branch choice = minimum exact ideal code length under the current integer frequencies,
  including the branch flag, with ties to direct. The search over templates uses the
  actual run, which is legitimate because branch, id and edits are paid. Pruning is exact:
  a slot is skipped only when its unavoidable cost already reaches the best total.
* **Static dictionary**: an ordered constructor-run trie with exact multiplicity; templates
  are the top-K runs of length ≥ 2 by count × (length − 1), ties by id sequence. The
  gzip-serialized table is paid inside **every** archive. Tables are built from
  development regions only: leave-one-out on the development screen, and all sixteen
  development regions for confirmation.
* **Prefix dictionary** (separate descendant): sequential, future-free insertion of each
  decoded run of length ≥ 2, refreshing it if present, and least-recently-used eviction
  (ties: lowest slot). Insertion and eviction are identical in encoder and decoder.
  No table bytes.
* Anchor classes come from the content-first literal channel, which is paid before use.
  `right` = paid right anchor, `left` = left anchor, `wrong` = matched deterministic
  unrelated anchor (control).
* Container: 58-byte header. With no dictionary the run stream is byte-identical to
  constructor_codec coarse_<ctx>:4. The job asserts this for every such case; the archive
  is exactly 8 B larger, from the header.

## Grid (finite, pre-registered), 39 arms per region

* No dictionary × {left, right, wrong} — the equal baselines (3 arms).
* Static × cap {64, 256} × edit cap {0, 1, 2} × {left, right, wrong} (18 arms).
* Prefix × cap {64, 256} × edit cap {0, 1, 2} × {left, right, wrong} (18 arms).

## Data and protocol

* Regions: `cpu_round14_constructor.offsets()`, 32 spread 1 MiB slices of the original
  corpus (seed 1400831), identical to the 608 completed constructor archives. Even index
  = 16 development MiB; odd index = 16 confirmation MiB.
* Development screen: all 39 arms on the 16 development regions; four pinned lanes; every
  case independently decoded; gzip and zstd recorded per region.
* Measures: actual archive bytes (primary), channel sizes, template-branch usage, edits,
  CPU, RSS. The four-cell interaction for each (kind, cap, E), as in P3, with
  N = none-left, G = template-left, M = none-right, GM = template-right:
  I = B_G + B_M − B_N − B_GM.
* **Selection rule (fixed now).** Among template arms with ctx = right, pick the
  (kind, cap, E) with minimum total actual development bytes; ties go to the smaller cap,
  then the smaller E, then static. It advances to confirmation only if it beats none-right
  in total development bytes. Otherwise P5 confirmation is not run and the negative is
  recorded.
* Confirmation (separate frozen job, after selection): the selected (kind, cap, E) with
  right/left/wrong plus none right/left/wrong on the 16 confirmation regions; static
  tables rebuilt from all 16 development regions. Development data is never reused as
  confirmation.
* A complete 1 GB serialized inverse is run only after a meaningful full-code gain over
  zstd (none is expected: the constructor factorization already loses about 1 MB to zstd
  on 16 MiB). A tiny conditional grammar gain does not justify another full proxy run.

Resources: one private CPU notebook per stage, four pinned fork workers via
`initialize_lane`, thread variables 1, 10.3 h deadline, no GPU, no internet, $0. No
duplicate pushes, no quota bypass, no automatic retry. Scope: paid raw-text proxy, not the
native stream and not a package claim.
