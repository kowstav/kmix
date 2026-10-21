"""Build the authoritative report/96-idea ledger from preserved evidence."""
import pathlib,json,datetime,hashlib
P=pathlib.Path(__file__).resolve().parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(name):
 p=P/name
 return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else {}
jobs={key:read('research_round9_'+file+'_results.json') for key,file in [
 ('sequence','sequence_v1'),('hidden_TTL','hidden_sequence_v2'),('adaptive_replay','adaptive_source_v1'),('whole_word_alignment','full_word_alignment_v2'),('core_short','core_training_v2'),('core_long','core_extension_v1'),('native_adaptive','adaptive_native_v2'),('core_export','core_export_v2'),('core_native_codec','core_native_codec_v3'),('literal_split','literal_split_v1'),('known_literals','known_literals_v1'),('known_side_verify','known_literals_side_verify_v2'),('word_softmax','word_softmax_v1'),('word_softmax_descendant','word_softmax_v2'),('word_warmstart','word_warmstart_v1'),('title_memory','title_memory_v1'),('core_pipeline_profile','core_pipeline_profile_v1'),('distributed_core_data','distributed_core_data_v1'),('distributed_core','core_distributed_v2'),('word_events','word_events_v1'),('word_features','word_features_v1'),('native_layers','core_layer_probe_v1'),('GPU_layers_v2','core_layer_gpu_v2'),('GPU_layers_v3','core_layer_gpu_v3'),('GPU_layers_v4','core_layer_gpu_v4')]}
for key,file in [('core_selective','core_selective_v1'),('word_cache','word_cache_v1'),('model_order','model_order_v1')]:jobs[key]=read('research_round9_'+file+'_results.json')
program=read('research_round8_idea_program.json');assert len(program['entries'])==96
program.update(date=now,session=355735431,status='ONGOING_NOT_COMPLETE',core_retraining_this_turn=True,paid_rental_usd=0,all96_fully_explored=False,completion_contract='A finite tested descendant is not an absolute or best-possible descendant. Every family remains open until its explicit implementation, matched controls, decoder contract and cost gates are recorded.')
maps={
 'sequence':['A07','A22','A82','A83','A84'],
 'hidden_TTL':['A25','A28','A80','A83','A84'],
 'adaptive_replay':['A21','A22','A25','A35','A42','A62','A63','A82','A84'],
 'native_adaptive':['A21','A22','A25','A35','A42','A62','A63','A82','A84','A95'],
 'core_short':['A14','A36','A46','A90','A91','A93','A94','A96'],
 'core_long':['A14','A36','A46','A90','A91','A96'],
 'whole_word_alignment':['A67','A85','A90','A93','A94','A96'],
 'native_layers':['A93','A94'],
 'GPU_layers_v2':['A93','A94'],'GPU_layers_v3':['A93','A94'],'GPU_layers_v4':['A93','A94'],
 'core_export':['A17','A43','A46','A90','A93','A94','A96'],
 'word_events':['A29','A30','A64','A67','A72','A73','A74','A77','A78','A79','A80','A82','A85','A89'],
 'word_features':['A04','A05','A06','A29','A30','A34','A64','A72','A73','A74','A77','A78','A79','A82','A83','A84','A89'],
 'literal_split':['A85','A96'],'known_literals':['A85','A90','A91','A96'],'known_side_verify':['A85','A96'],
 'word_softmax':['A13','A67','A68','A70','A83','A84'],'word_softmax_descendant':['A13','A67','A68','A70','A83','A84'],
 'core_native_codec':['A17','A43','A46','A90','A93','A94','A96'],
 'distributed_core_data':['A67','A85','A90','A93','A94','A96'],'distributed_core':['A14','A36','A46','A90','A91','A93','A94','A96'],
 'word_warmstart':['A13','A67','A68','A70','A83','A84'],'title_memory':['A25','A28','A55','A57','A66','A71'],'core_pipeline_profile':['A17','A46','A93','A94','A95']}
limits={
 'sequence':'Eight widths/kinds, finite rungs and fixed64-byte block context. Does not implement every shared controller, architecture or long memory.',
 'hidden_TTL':'Ten widths/kinds; four learned/fixed EWMA decays, reset every128bytes. Does not establish persistent TTL beyond a block, optimal eviction or survival controller.',
 'adaptive_replay':'Eight finite posterior policies; source-replay likelihood only. Previously viewed C/D/E/F are fit-held-out, not untouched discovery data.',
 'native_adaptive':'Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.',
 'core_short':'Actual selected5.897M core, five loss-only masks,128steps,262KiBprefix only. Rare inputs remain visible in this branch. Later literal_split/known_literals and distributed_core test other masking subcases; those results must not be retroactively attributed here.',
 'core_long':'Six policies, two seeds and1152steps. Same early corpus and unresolved GPU/native numerical fidelity. Euclidean gradient projection with AdamW has no certified common-loss descent guarantee.',
 'whole_word_alignment':'Exact whole-word and literal/OOV spans on262KiBprefix, matched independently to native decoder. Corpus-wide training alignment remains pending.',
 'native_layers':'Observes4096native steps,205FP32priors and13activation stages. Observation only; no optimization claim.',
 'GPU_layers_v2':'Integer-dot forward improves first article, but later article probabilities still differ. No native parity PASS.',
 'GPU_layers_v3':'Correctly rounded division repairs initial embeddings substantially. Later quantization/recurrent mismatch remains.',
 'GPU_layers_v4':'Native RMS order and recurrent KDA inference diagnostic. Read recorded errors; no export/parity claim inferred.',
 'core_export':'Exact native-reader tensor roundtrip and native neural probability observations PASS. Important measurement correction: historical --transformer-only runs the network but Predict returns PPMD, so V2 archive sizes did not measure neural compression. V3 repairs that diagnostic and tests combined CM; do not promote V2 zero archive differences as neural results.',
 'word_events':'Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.',
 'word_features':'Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.',
 'literal_split':'Three actual reversible input-redaction cutoffs on65KiB, final CM encode/decode; positions, literals and container bytes paid. Unchanged model only, Python side wrapper, previously viewed prefix, unmeasured eligible executable cost. Negative finite result does not reject better side models or content-first architectures.',
 'known_literals':'Three raw-context known-literal cutoffs, one masked-context branch and one trained common specialist on65KiB. Native Predict/Perceive still run for skipped coded bytes, independent decode/core identity PASS. All5 lose after the current side price. Full production wrapper, stronger side law, fullwarm/package and independent corpus remain open.',
 'known_side_verify':'Independently parse the paid HPKNOWN container alone, reconstruct every mask/value byte, prove identity with files used in all5 executed native decodes and original reconstruction. No frequency table/original input needed to construct hints; eligible native side-loader/full package still pending.',
 'word_softmax':'Eight actual44515way word output heads, unchanged dictionary code tree and literal fallback; exact normalized probability and causality checks. Fixed.8dictionary/.2uniform literal law and.1expert gate cap; surviving random-basis heads lose versus adaptive reference. No native integration or full package.',
 'word_softmax_descendant':'Ten runs learn literal byte distribution, dictionary/literal gate, word temperature and native/expert gate capped.5, with byte-head control and pruned-kind model construction. Same six cold fragments, finite128/384/1152rungs. Native integration, production framing and fullwarm/package remain open.',
 'core_native_codec':'Repairs diagnostic-only bit law and independently tests trained weights in actual combined CM on three64KiB slices. V2 neural probability/tensor results remain valid, its archive claims were misnamed. Fullwarm/original-corpus/package, cross-CPU and eligible resources remain open.',
 'distributed_core_data':'Six512KiB fragments with exact whole-word labels, true separator boundaries and independently regenerated raw/redacted1392 PPMD priors. Neutral extraction reproduces earlier tokens/priors exactly. First partial article excluded, cold classical priors; not full warm corpus.',
 'distributed_core':'Six policies times two seeds,384steps, actual selected core on A/B, develop C/D and core-fit-held-out E/F. Genuine redacted input with its own regenerated priors; actual Adam proposal projection with matched unweighted control. Quantized/native parity and finite-step first-order guarantees remain unresolved; actual code/export required.',
 'word_warmstart':'Six spelling/independent/random models, direct44515class word CE on verified dictionary-only root first-code positions then full-bit mixture loss; two seeds and128/384rungs per phase. Supervised word CE alone is not compression. Full support/native integration/cost and fullwarm qualification remain open.',
 'title_memory':'Six persistent causal title-byte copy laws with lifetime through the article and bounded4096byte titles; normalized within-byte support; convex nonnegative mixture fit on A/B, select C/D. Identity wins and is confirmed E/F. This does not exhaust case-invariant semantic/entity memory, contextual gating, links, field reordering or native integration.',
 'core_pipeline_profile':'Queued zero-update raw/redacted E/F controls plus unchanged-weight packed training throughput, explicit per-document KDA/convolution/attention/RoPE isolation and foreach optimizer comparisons. lr0 and resident batch; not5090, CPU codec timing or improved archive.'}
maps.update(core_selective=['A17','A43','A46','A90','A91','A93','A94','A96'],word_cache=['A04','A05','A25','A28','A29','A30','A64','A66','A72','A73','A74','A78','A79','A80','A82','A85','A89'],model_order=['A17','A43','A46','A93','A94'])
limits.update(core_selective='Six groups/objectives times two seeds,384steps. Selective unembedding/gates/last block updates versus paired all-core higher-lr and native-code-cell excess-displacement penalty. Penalty proxies code flips,not measured compressed bits. Native export and archive pricing required.',word_cache='Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.',model_order='Recover original container tensor order and independently verify all native reader tensor bytes. Adaptive weight-code order changes must not be confused with training. Native identity permits compositional reuse of the already independently decoded archives.')
for e in program['entries']:
 e['fully_explored']=False;e['round9_evidence']=[]
 for job,ids in maps.items():
  if e['id'] in ids:
   result=jobs[job];e['round9_evidence'].append({'job':job,'status':result.get('status','IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT'),'pid':result.get('pid'),'limitations':limits[job]})
 e['round9_status']='OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION' if e['round9_evidence'] else 'OPEN_NOT_IMPLEMENTED_THIS_ROUND'
 e['next_required_test']=e['discriminating_test']
 e['promotion_contract']=['explicit prefix-only or paid-side-information law','normalized complete support including literals/OOVs','nonzero future-prefix noninterference and zero identity','matched capacity and representation controls','fit/development/independent confirmation separation','integer replay plus actual native independent decode','complete model/executable/side bytes and full warm CPU/RAM accounting']
program['deletions']=read('research_round9_core_checkpoint_relocation_manifest.json')
(P/'research_round9_idea_program.json').write_text(json.dumps(program,indent=2),encoding='utf-8')
ledger=['# All96 idea families: execution and remaining-work ledger',f'Generated {now}. Session355735431. No family is claimed fully explored.','This preserves the round1–7 audit and round8 evidence. Shared infrastructure is credited only to the finite subcase actually implemented. Read the source/result files for executed hyperparameters.']
for e in program['entries']:
 h=e['historical_evidence'];ledger.extend([f"\n## {e['id']} — {e['title']}",f"Status: **{e['round9_status']}**. Route {e['route']}; priority {e['priority']}.",f"**What rigor was actually evidenced:** {h.get('rigor_applied', 'New masking proposal: prior dictionary-only residual pilot did not test the original core or literals/OOVs.')}",f"**Actual testing versus required testing:** {h.get('actual_testing_and_needed_testing', 'Census and tiny dictionary-target residual pilot; exact full-word core masking, representative data, specialists and native package checks were still required.')}",f"**Combination work evidenced:** {h.get('combination_work', 'Common/rare gradient diagnostic on a tiny head; the actual shared-core and specialist combinations were unimplemented before round9.')}",f"**Stronger descendant to implement:** {e['stronger_descendant']}",f"**Discriminating experiment:** {e['discriminating_test']}",f"**Combination partners:** {', '.join(e['combination_partners'])}. Prerequisites: {'; '.join(e['prerequisites'])}."])
 if e['round9_evidence']:
  for r in e['round9_evidence']:ledger.append(f"- Round9 `{r['job']}`: {r['status']}; PID{r['pid']}. {r['limitations']}")
 else:ledger.append('No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.')
(P/'research_round9_all96_execution_ledger.md').write_text('\n\n'.join(ledger),encoding='utf-8')
report=f'''# Round9 implementation, experiments and continuation report

Generated {now}. Authorized Kaggle session355735431. Paid compute spent **$0**.

The earlier work did not complete thorough testing of all96 ideas. Some screens were proxies, and the selected-core import, exact literal/OOV labels and native export were unfinished. Those implementation gaps, rather than an impossibility result, explain the partial status. This round implements those missing dependencies and additional architecture combinations. It still does not establish best-possible descendants, equivalent LLM-scale research effort, an absolute optimum, a20% archive reduction or a new qualifying record.

The accompanying96-family ledger retains each idea's historical rigor, actual-versus-needed test, combination work, stronger descendant, prerequisites and remaining test. Architecture counts below count actual parameterized arms, not completed idea families.

## Measurement and mathematical contracts

For a binary event with native integer law p_t in[1,65535], the actual probability is p_t/65536. Score every observed bit, including hard/literal/OOV words: L=-sum_t log2(q_t(y_t)). The acceptance objective is **payload bytes plus every shipped model, executable, dictionary, side stream and duplicated asset**, subject to exact independent decoding and eligible CPU/RAM. A reduction in masked loss or common-word loss alone does not qualify.

Let ell_t=log(p_t/(65536-p_t)). The frozen wider source correction is delta_t=theta0+theta1*ell_t+theta2*f_t, with theta=(.0016181118716570748,-.007454085408717222,2.3818512619982752), and f_t=FP32(clip(logit(native_NN_t)-ell_t,-12,12)/12) gated by the previous completed byte's neural validity. Only current before-target sources and decoded history are inputs. The integer expert laws are rounded/clamped sigmoid(ell_t+a*delta_t), with a in{{.5,1,1.5,2}}, plus identity.

For the adaptive mixture q_t=sum_k w_tk p_tk, after observing y_t update v_tk=w_tk p_tk(y_t), then w_(t+1)k=(1-epsilon)*v_tk/sum_j v_tj+epsilon/K. Here K=5 and epsilon=1-2^(-1/262144). No future difficulty label selects an expert. With epsilon0, product_t q_t(y_t)=sum_k w_0k product_t p_tk(y_t); the independent replay checked this identity. Fixed share permits change of expert over time but adds regret; the finite8policy family is not a global optimum.

For word features, an event becomes available only after its delimiter's encoded bytes complete. Bag-letter statistics, first/last letters, fixed symbolic shape groups and constructor-run state are functions of already completed words. The combined residual is delta'_t=.5*tanh(H([native_sources, word_state, native_disagreement*word_state])). This tests algebra/placement sharing without giving the model a future word. The separate content-first/infill proposal requires a paid ordering/anchor stream or a deterministic decode schedule; this architecture does not implement that different factorization.

For masking, J_lambda=sum_i w_i CE_i/sum_i w_i. Word-frequency thresholds107,1392,8372 are supervision-only and include complete literal/OOV/case spans. They are not decoder inputs. Current masks change losses, not tokens or rare-word context. For mixed classes the necessary condition is N_C*Delta_H_C+N_R*Delta_H_R+8*Delta_package<0. Improved constructors cannot compensate for arbitrarily expensive rare words.

For projected gradients g_C,g_R, a Euclidean projected g'_R=g_R-min(g_C dot g_R,0)*g_C/||g_C||² obeys g_C dot g'_R>=0. The existing arm feeds this gradient through AdamW, so the actual momentum/preconditioned update has no such guaranteed common-loss inequality. A stronger controlled descendant must project the actual update in a frozen diagonal metric or use matched SGD controls. Non-smooth quantization and finite steps also limit any first-order claim.

## Actual implementations and exact procedures

**Causal sequence screen:** eight arms: MLP/GRU/causal attention/dilated TCN, widths32/64. Full bit loss, train A/B, develop C/D, freeze finalists before E/F. Batch16blocks of512bits; fixed64byte resets; AdamW lr.0003, weight decay.01; rungs128/384/1152 with8/4/2survivors. Nonzero-head future-prefix mutation and zero-head identity passed. TCN32's E/F incremental gain over the wider reference totals about-1.24B. Its roughly47KB compressed weight payload does not pay. This rejects those finite fitted arms, not all sequence models or this idea family. Sources: research_round9_sequence_worker.py and research_round9_sequence_v1_results.json.

**Native hidden/TTL screen:** ten arms MLP/GRU/learned four-decay TTL/fixed TTL/channel-permuted GRU, widths32/64. Inputs include all192native hidden channels after the previous byte, delayed byte surprise, previous byte embedding and current native sources. Batch16x128bytes, full bit loss; rungs128/384/1152 and10/4/2survivors. Decay targets1/8/64/512completed bytes, but block resets bound effective retention to128bytes. Fixed channel rotation is a relabeling control, not a semantic null. Best frozen finalists provide only fractions of a byte beyond the wider law; model bytes do not pay. Source: research_round9_hidden_sequence_worker_v2.py and its results.

**Adaptive no-retraining law:** eight posterior policies were evaluated on actual integer expert laws, selected only on A/B, then measured on fit-held-out C/D/E/F. Scaled5 H262144 saves an additional66.62/59.77/61.25/119.53B on those respective512KiB slices over the wider reference. These are likelihood results, not a full archive. New G65M and H375M offsets were frozen before observation; actual native coder integration and independent decode are in adaptive_native_v2. Read its current manifest before any claim.

**Numeric repair:** adaptive_native_v1 validation initially found190one-unit mismatches among4194304bit positions. Direct expert comparison found75expert differences caused by a reference-only weak-scalar float32 multiplication under NumPy. Explicit float64 restored the source-replay worker's coefficient law and made all expert integers match. Native binary, model, coefficients and policy were unchanged; the completed G encode was reused. Preserve adaptive_native_v1 and adaptive_strict_v1 failures and numeric_detail evidence. Do not characterize this as a new fitted improvement or delete failed evidence.

**Whole-word supervision:** independent annotated/native WRT decoders compare every decoded character and encoded-atom consumption. Full words are assembled across literal bytes, dictionary fragments, case controls and apostrophes; complete word-frequency labels map to their entire encoded span. The pilot has262138neural payload bytes after six outer header bytes, including18484literal/OOV encoded word bytes. The original native prior failure on an out-of-alphabet outer header is preserved; v2 explicitly removes only those six framing bytes. Priors are current actual205-way dense native probabilities, not sparsified approximations.

**Actual selected-core finetuning:** recovered original model code and packed lexical tensors; imported all199parameters,5897145total scalars, from the actual selected weight asset SHA948847d9... rather than an unrelated checkpoint. Architecture12layers,width192,d_mlp768, nineKDA/threewindow-attention blocks, learned15level codebook grid.25,8bit small tables, fixed native BF16 row scales and QKV scales. Quantized forward uses STE shadow parameters. Five policies at128steps, lr1e-5, AdamW wd0, grad clip1, matched sampled article-prefix states through4096tokens, final256target loss. Article-level20% development split; same262KiBprefix corpus. Every128step arm slightly worsened ordinary full loss from .5932896bits/symbol. Checkpoints are preserved locally.

**Longer masks/interference:** six arms, seeds6506/6507,128/384/1152rungs, matching training examples per seed. Arms: unweighted,107half,1392half,1392zero,8372half and actual shared-core gradient projection. First seed at1152: unweighted total.59204489, common.42922333, rare2.14548039;107half total.59273922/common.42506939/rare2.19243002;1392zero total.64397079/common.41583180/rare2.82058144. Zero rare loss helps common words but loses substantially overall. Results are diagnostic until native measurement and broader corpus replication. Read core_extension_v1 rather than launching duplicates.

**Native/GPU precision:** captured4096actual step records containing205FP32priors, initial embedding plus12block outputs and205FP32probabilities. Observation leaves the native probability stream unchanged. Integer-valued FP32 dot products eliminate fake-quant floating accumulation error; bounded partial sums below2^24 are required. Explicit FP64 quotient then FP32 cast restores native division rounding at quantizer thresholds. Initial embeddings improve from a.00434max error to below1e-6, but later layers still diverge. The next diagnostic uses native8lane FMA RMS summation and fused recurrent KDA inference. This backend is not declared bit-exact. Native model export and actual codec evaluation can still evaluate trained weights without substituting GPU scores.

**Native checkpoint export:** zero update must reproduce every native tensor byte, including unchanged configuration, BF16scale/codebook and RoPE data. Trained shadows are snapped to the original codebook or int8levels, preserved native scales and raw FP32constants. Pack with the existing container codec, unpack using the actual C++ reader, and assert the raw tensor SHA. Compare native neural-only archives and independent decoded bytes for first-seed unweighted/107half/1392zero. This deliberately exposes common-versus-rare cost using the deployed neural codec. Final combined CM and independent corpus gates remain required.

**Letter/glyph/constructor combinations:** word_events_v1 independently decodes/compares the canonical prefix through the final D window, emitting only complete words within six512KiB slices. word_features_v1 starts A/B fitting only once an E190M event proves A/B extraction passed103.16M. C/D/E/F scoring waits for the complete extraction PASS. Nine arms, two seeds6706/6707, same32width model and matched rungs128/384; best two per seed continue1152. Arms: native-source control, identity, bag+positions, glyph groups, constructor grammar, spelling+grammar, spelling×native-source interaction, all features, deterministic random-word-vector sharing control. Inputs contain no frequency/rare/body/next-word labels. First16slice bytes and crossing words are excluded. Fixed constructor labels are heuristics; they do not identify every true noun or grammar word. Symbolic glyph features do not test OCR or CNN. Native final-bit integration and model cost remain pending.

## Current job snapshot

| Job | Status | PID | Completed rungs/candidates |
|---|---|---:|---:|
'''
for key,j in jobs.items():report+=f"| {key} | {j.get('status','LOCAL_SNAPSHOT_PENDING')} | {j.get('pid','')} | {len(j.get('rungs',j.get('candidates',j.get('native_candidates',[]))))} |\n"
report+='''
This is a saved snapshot, not a live process claim. Inspect remote manifests and actual PID before reuse/launch. All workers write immutable rung checkpoints and manifests. root scratch is outside the20GB working quota but is not automatically carried to the next Kaggle session; locally preserved evidence and verified bundles are the recovery source.

## Remaining implementation queue and combined strategy

1. Finish current two-seed core, word-feature and exact native adaptive/export jobs. Preserve model, optimizer, RNG, source, config, binary and compact results with SHA manifests. Correct implementation failures with new version names; reuse completed costly traces/encodes.
2. Extend whole-word supervision and exact native priors to distributed article strata, reset-aware contexts and longer tokens; preserve a final untouched confirmation pool. The prefix pilot cannot settle corpus-scale masking or architecture potential.
3. Implement explicit input-redaction versus loss-only masking, common/rare output specialists and a normalized soft router with unmasked total-loss objective. The router must be predictable before the target; encoder-only rarity cannot choose its branch for free. A true constants stream must pay positions, literal bytes and metadata and reconstruct all original contexts.
4. Test the actual-update gradient projection or matched-SGD descendant; compare total/common/rare loss and actual native package. Continue representative unweighted training as its control. Test learned scales/codebooks only with compressed weight cost and native reader parity.
5. Build actual word-event softmax/spelling composer through the unchanged WRT tree, with exact fallback and integer normalization. Then combine constructor-run state, associative word graph, long prefix memory and native source disagreement. Generic byte residuals cannot stand in for these unimplemented architectures.
6. Develop content-first grammar infilling as its own reversible factorization. Store/order anchors and gap lengths first, then code constructors conditioned on decoded left/right anchors, with permutation/multiset/subset counts priced. Compare ordered templates and a null order-aware model; do not feed future content into a left-to-right decoder for free.
7. Build revision/title/schema copy/edit and symbolic numeric experts with arbitrary-tail fallback. Strong metadata/title descendants are still unimplemented this round; the96ledger names all their contracts and dependencies. Include field reordering/copy residual/side bytes rather than screening raw correlations alone.
8. Jointly ablate surviving laws under the final coder. Adding individual measured gains is invalid because the mixture/weights/context change their conditional benefit. Retrain/refit only on designated development data; price a single shared implementation and all duplicated assets.
9. Qualify finalists on warm full history, all587138826canonical bytes, actual self-contained archive/package, exact original1B SHA, CPU time and peak RAM on eligible hardware. The old C3 peak leaves only615424B under decimal10GB, so cold6GB memory is not sufficient evidence. Rebalance classical allocation and benchmark if new state exceeds that margin.

No paid rental begins merely because a GPU is faster. The $70 plan first requires a measured tokens/s and memory benchmark on a ready implementation. Use15–60minute architecture rungs and matched token budgets, then2–4hour confirmation candidates and longer final continuation only for survivors. A provisional12–24hours of shortlists plus8–16hours of finalists is not a price quote or an estimate for exhaustive96idea research. Reserve$10, impose a$60compute cap including storage/transfer, and allocate from an actual verified all-in hourly price. No such5090benchmark or rental has occurred. The final training plan depends on these native tests and cannot promise20%compression.

## Preservation, deletions and next-agent instructions

Eleven core_training_v2 checkpoint files were copied and SHA-verified in root scratch and the local workspace before their redundant working-disk paths were unlinked. About736MB of working space was recovered; no checkpoint content, original corpus or original selected model was deleted. The exact11source/destination/size/SHA entries are in research_round9_core_checkpoint_relocation_manifest.json. Do not repeat the earlier statement “no filesystem deletions”:11redundant paths were removed after preservation. No other project content was intentionally deleted in this round.

Correct complete native build dependencies are155files, ZIP1106710B, SHA7ae01f60e7f7e4813f1c14c5869af94349c755eff370cfb7b7a3434bbbba0eb3. The earlier archive omitted cpp_infer and is not enough to rebuild. Original training source and actual packed tensor expansion were recovered from the preserved source archive. Isolated pinned runtime packages live in /root/hp_round9/runtime_site_v1; no global torch replacement was made.

Use kaggle_research_client.mjs with the session credential supplied only through HP_KAGGLE_BASE; never persist the signed URL. Text put is not a binary uploader. Use the binary uploader with SHA/CRC validation for archives. Use small detached workers via the Jupyter kernel, not a50second blocking long experiment. Only the latest human-supplied session is authoritative.

Read research_round7_checkpoint.md first, then this report and research_round9_idea_program.json. Inspect RUNNING/FAILED manifests and reuse live jobs; do not replay source generators that overwrite prior status. All96families remain open. Managed Goal is usageLimited and was not resumed/replaced/mutated; automated follow-ups must honor that limit. The requested week ends11October2026.
'''
report=report.replace('Current masks change losses, not tokens or rare-word context.','The short/core_long masks change losses only. The later literal_split, known_literals and distributed_core branches test genuinely redacted inputs or a paid constants stream; these are distinct experiments.')
report=report.replace('Read its current manifest before any claim.','The completed G/H native archives save168B and172B, respectively:340B on1MiB, with exact independent decoding and core/Q16 identity. This is a cold-slice result before new package costs, not a full-corpus or record result.')
report=report.replace('The next diagnostic uses native8lane FMA RMS summation and fused recurrent KDA inference.','The completed fourth diagnostic used native8lane FMA RMS summation and fused recurrent KDA inference; it did not solve parity and worsened the first article.')
report=report.replace('Compare native neural-only archives and independent decoded bytes for first-seed unweighted/107half/1392zero. This deliberately exposes common-versus-rare cost using the deployed neural codec.','V2 proved exact trained tensor import, native neural observations and independent PPMD-coded archive decoding for first-seed unweighted/107half/1392zero. Its archive comparison was initially mislabeled: historical --transformer-only still returns PPMD from Predictor::Predict. Consequently identical39756B archives are not a neural-compression result. core_native_codec_v3 repairs only that diagnostic probability route, independently decodes true neural archives and tests the same trained weights through the unchanged combined CM on A/B/E64KiB; its actual manifest controls current claims.')
report=report.replace('5. Build actual word-event softmax/spelling composer through the unchanged WRT tree, with exact fallback and integer normalization.','5. The actual44515way word output softmax/spelling composer is implemented in word_softmax_v1. Its fixed literal law and narrow gate performed poorly; word_softmax_v2 now tests learned literal law/gates/temperature and a byte-head control. Finish its recorded tests and exact native integration if gains pay. Then extend the model through the unchanged WRT tree, with exact fallback and integer normalization.')
report=report.replace('normalized common/rare experts with predictable router; explicit constant stream if reordered','distributed raw and actually redacted core variants plus known-literal bypass; separate normalized rare specialist still pending')
report=report.replace('research_round9_core_export_worker.py; zero tensor identity,3representative trained exports, native reader/neural codec','research_round9_core_export_v2_worker.py for tensor identity; research_round9_core_native_codec_v3_worker.py for corrected neural and final CM archives')
report += '''

## Later completed masking and word-architecture work

Actual input masking is no longer only a proposed or loss-only test. literal_split_v1 replaces complete rare encoded word spans by spaces, independently compresses/decodes the main stream with the final CM, and restores every original byte from a paid side stream. Cuts107/1392/8372 lose2106/4451/6814B on65536B. The side codec is zlib9 and is not asserted optimal.

known_literals_v1 is a stronger descendant: decode the rare bytes first, insert them into original context, and execute all native Predict/Perceive updates while skipping their arithmetic intervals. The all-unknown control reproduces the original archive exactly. Original-context hidden trajectories and independent decode match for all3cutoffs. Their net losses after side/container costs are1430/3125/4985B. Redacted-context1392 loses3985B. The already-trained1392zero common specialist reduces the raw-context main archive3770B to3616B, a154B local benefit, but its full split still loses2971B and its model adds85927B per copy. This demonstrates a finite specialist effect, not a successful split or a rejection of stronger constants-first laws. A native sequential side-loader and better side probability/order models remain open.

word_features_v1 completed18runs and40checkpoints. Every E/F finalist has negative joint incremental gain against the wider law; the best grammar seed totals about-0.162B. Learned symbolic letter/glyph/constructor features in these small residual heads therefore do not pay their models. This neither tests a raster OCR model nor exhausts long-memory placement or content-first infilling.

word_softmax_v1 completed8runs/14checkpoints with exact44515way normalized output laws and prefix-tree marginalization. Surviving random-basis heads lose4.264B and5.772B jointly on E/F relative to the stronger causal adaptive law. A stronger descendant, word_softmax_v2, removes its fixed-uniform-literal limitation, learns literal byte probabilities, dictionary/literal mixing and word scale, widens the context gate from.1 to.5, and includes a byte-head control. Ten runs, seeds6906/6907, rungs128/384/1152; select best2/seed then1/seed using C/D, confirm E/F only after selection. These are still finite cold diagnostic models and require native integration if promising.

distributed_core_data_v1 prepared six512KiB fragments from canonical WRT offsets A/B/C/D/E/F. Whole-word body labels include dictionary, literal/OOV and case spans. Raw and genuinely redacted1392 inputs get separate native PPMD prior extraction; an unmodified-prefix neutral control matches existing tokens and priors exactly. Training/evaluation excludes the initial partial article and begins at observed native reset boundaries. A/B train, C/D develop, E/F are held out from core fitting but have been viewed by other families; no untouched discovery claim. These are cold classical priors, not full warm-history training data.

core_distributed_v1 failed during setup because importing the original core replaced its distributed-data manifest variable. No training ran in that failed worker; the failure is preserved. The repaired core_distributed_v2 reuses all prepared data and imports all199parameters/5897145scalars. Its12runs compare raw unweighted, raw1392half, raw1392zero, redacted1392full, redacted1392common and projected actual Adam update, seeds7006/7007, checkpoints128/384. Same sampled article prefixes/targets per seed. Priors are regenerated on redacted inputs, so the model does not receive original-stream context through a stale prior. Redaction still needs the paid side stream for full original reconstruction.

For the corrected gradient descendant, let d=theta_old-theta_Adam and g_C be the current common-loss shadow gradient. Project d*=d-min(g_C dot d,0)g_C/||g_C||² and set theta_new=theta_old-d*. This addresses the earlier mistake of projecting gradients before Adam's momentum/preconditioner. It satisfies the first-order surrogate halfspace in exact arithmetic; shadow float32 rounding, finite step, quantizer discontinuities and native likelihood still require measurement. The actual before/after dot products are recorded. A theorem about a surrogate is not an archive guarantee.

All96families still retain explicit open descendants in the ledger. Completed parameterized runs and shared dependencies must never be counted as96exhausted ideas. Metadata/title/copy/edit, genuine glyph/OCR, paid latent schedules, full constructor-set/order models, long-memory eviction and joint native integration still have missing implementations.
'''
report+='''

## Additional descendants, corrections and training plan

The corrected diagnostic neural archives are teacher20626B, unweighted20264B,
107half20289B,1392zero22001B on262138B. Gains362/337/-1375B concern that exposed
prefix and exclude model/package growth. Final combined CM and B/E are separate.

The learned-literal/gate word_softmax_v2 completed10runs/16checkpoints; its two
E/F finalists lose5.132B and3.312B relative to the adaptive reference. The stronger
word_warmstart_v1 directly optimizes dictionary-class CE before full-bit training,
addressing gradient starvation when the native/expert gate almost closes. Six
spelling/independent/random runs use seeds7106/7107, word batch256 and bit batch128,
128/384rungs in each phase. Exact event/code matches prevent joined/OOV labels from
being treated as dictionary roots. Every input remains before-target; supervision
labels are never inputs. Evaluate and select by full bit cost, not word CE alone.

title_memory_v1 completed six no-retraining persistent-title copy laws. Titles are
collected only after decoded title-tag bytes, bounded4096B, retained to next title
or page-end. Dictionary-code substring histograms/suffix lengths1/2/4/8/longest
produce normalized byte/bit laws with positive support. One bounded mixture scalar
per law is fit convexly on A/B; identity wins C/D and stays identity E/F. This is
an actual persistent copy law, not a hidden-similarity proxy, but it does not exhaust
case-invariant title entities, contextual placement gates or linked-article memory.

known_literals_side_verify_v2 independently parses each counted side container and
derives all mask/value bytes without the original data or word census. Those files
are byte-identical to the files used by the executed independent native decodes,
and the decoded/restored original hash matches for all5cases. This closes the hint
provenance gap through compositional identity; eligible native wrapper pricing still
requires work. No expensive identical decode was rerun just to repeat that evidence.

core_pipeline_profile_v1 is queued after GPU0 training: record missing zero-update
E/F raw/redacted controls, then test per-document RoPE/KDA/convolution/attention
isolation and packed batches of1/4/8, caps256/1024, Adam lr0, foreach false/true.
Separate GPU outputs and first-document future noninterference must pass before
timing that packed variant. This is a real original-core pipeline benchmark, not
a claim of5090performance or full-corpus/native parity.

Read **research_round9_training_and_5090_plan.md** for detailed short-rung training,
mask/side specialists, word warm-start, actual-update projection, rate-aware QAT,
joint factorial tests, measured timing and$70allocation. It distinguishes a
shortlist allowance from exhaustive96idea cost. Actual marketplace quote and
ready-workload throughput are prerequisites to paid execution; spending remains$0.
The detailed Hutter rule currently uses70000/T hours rather than the FAQ's older
100hour wording. Use its exact package formulas and self-contained CPU/RAM/HDD
contracts: https://hutter1.net/prize/hrules.htm . The official search index lists
July2026total100424672B; the local95914051B competitor remains a distinct stricter
competitive target whose current award status was not independently verified.

Compact evidence bundle1 is locally verified:49361182B,379entries, SHA
f6ecb95b5d2ebc22ee8b5ae7b67e7758d406a4416082dc3dabb6b48db9701f33.
ZIP CRC and every entry's SHA passed. It predates the later title/warm-start/profile
and trained-core archives; those need a second preservation snapshot. Current
linked checkpoint preservation is reported below; source/helper paths are retained.
'''
extra=P/'research_round9_latest_measurements.md'
if extra.exists():report+='\n\n'+extra.read_text(encoding='utf-8')
report+='\n\n## Snapshot of implemented jobs\n\n| Job | Saved status | PID | Recorded checkpoints |\n|---|---|---:|---:|\n'
for key,j in jobs.items():report+=f"| {key} | {j.get('status','AWAITING_LOCAL_RESULT')} | {j.get('pid','')} | {len(j.get('rungs',[]))+len(j.get('word_rungs',[]))} |\n"
verified=read('research_round9_downloaded_models_verified.json')
report+=f"\nVerified local large-model preservation: {verified.get('verified_files','unknown')} files, {verified.get('bytes','unknown')} bytes. This completed download precedes later word-softmax/distributed checkpoints, which require additional preservation. Source paths, failed workers and manifests remain reproducible evidence.\n"
(P/'research_round9_report.md').write_text(report,encoding='utf-8')
pre='''# Pre-experiment and continuation protocol — round9

The integrated report contains equations, exact source/configuration, why each experiment is needed, controls, rungs, selection, archive qualification and resource/deletion accounting. Read its implementation section before running a worker. The96-family ledger gives each still-open descendant and dependency. A saved status does not prove a process is alive.

| Queue item | Why | Source / procedure | Dependency and acceptance |
|---|---|---|---|
| Adaptive native G/H | Test finite-expert state under actual entropy coder | research_round9_adaptive_native_validation_v2_worker.py; reuse unchanged G encode and correctedFP64 reference | ExactQ16/core identity and independent decode; then full warm/package/resources |
| Two-seed core masks | Distinguish common-word interference from total compression | research_round9_core_extension_worker.py;6arms,2seeds,1152steps, matched examples | Original selected core imported; scores diagnostic until native export |
| Core export | Test learned weights under deployed native arithmetic | research_round9_core_export_v2_worker.py for tensors; core_native_codec_v3 worker for corrected neural and final CM laws | V2 diagnostic archive used PPMD; exact read/independent decode, then final CM/fresh corpus |
| GPU arithmetic localization | Improve training fidelity rather than assuming it | layer_gpu worker versions2–4; integer GEMM, roundeddivision,8laneRMS,recurrentKDA |4096observed native records; observation identity; discrepancies must remain explicit |
| Whole-word event extraction | Make lexical history causal and literals/OOVs complete | research_round9_word_events_worker.py and word_events.cpp | Every decoded char/encoded boundary equals native; words only after delimiter |
| Word/glyph/placement combinations | Test the community ideas with structural sharing and controls | research_round9_word_feature_worker.py;9armsx2seeds,128/384,4finalists1152 | A/Bprefixproof before train; full events PASS before C/D/E/F; final native/model cost pending |
| Distributed core data | Make training broader | distributed_core_data worker:6canonical fragments, exact body-word spans, raw/redacted native priors | COMPLETE; first partial article excluded, cold priors; fullwarm still pending |
| Redacted inputs / rare specialist | Masking loss does not remove hard-word context | literal_split/known_literals completed; core_distributed_v2 trains genuine redaction | Side/main native decode PASS; current side models lose; full model/native package pending |
| Actual-update projection | Euclidean gradient theorem does not cover Adam | core_distributed_v2 projects actual Adam displacement with matched unweighted control | Record shadow gradient dot displacement before/after; native full loss still required |
| Word composer descendant | Test exact word output law beyond narrow byte proxies | word_softmax_v1 COMPLETE; word_softmax_v2 learns literal law/gates/temperature with byte control | Exact support and causality PASS; finish rungs, price active arrays, then native if profitable |
| Content-first grammar | Future anchors must be decoded before gap constructors | Paid anchors/gaps/order/template law; this architecture is still unimplemented | Reversible schedule, controls, full side/package and CPU/RAM |
| Direct word warm-start | Test nearly closed mixture-gate gradient starvation | word_warmstart_worker:6models,2seeds,word CE128/384 then full bit128/384 | COMPLETE; both frozen E/F finalists negative |
| Persistent title | Retain actual copy context beyond1024bytes | title_memory_worker:6laws,scalar ABfit,CDselect,EFconfirm | COMPLETE; identity wins; richer entities/context remain open |
| Selective updates | Preserve stored weights while improving full loss | core_selective_worker:6paired arms,2seeds,128/384; frozen-byte assertions | GPU1 running; native export and model/archive pricing required |
| Word donor cache | Stronger no-retrain letter/placement/TTL law | word_cache.cpp/worker:8laws,last256completed words,encoded prefix probabilities | CPU replay running; production causal parser/native integration required |
| Original model order | Adaptive tensor coder is order-sensitive | model_order_worker:original order,all native tensor SHA,packed byte price | Compositional archive reuse requires identical native tensors |

Do not mark the96ideas complete based on these shared tests. Do not start paid5090work before readiness and the user's later shortlist decision.
'''
(P/'research_round9_pre_experiment_report.md').write_text(pre,encoding='utf-8')
block=f'''<!-- canonical-status-start -->
## Current authoritative continuation — {now}

Round9 is active on Kaggle355735431. Read research_round9_report.md and the
96-family execution ledger; no family is fully explored and no20%/record claim exists.
Actual selected5.897Mcore full-word literal/OOV loss-mask finetuning IS NOW RUN.
Five128step arms and six-arm two-seed1152step extension COMPLETE on early prefix.
Input redaction and paid known-literal bypass/common-specialist native tests COMPLETE;
all current65KiB side splits lose after side cost; specialist main saves154B locally.
Distributed6fragment raw/redacted native priors COMPLETE, core_distributed_v2 active.
Eight source-sequence and ten native-hidden/TTL arms completed; none pays its model cost.
No-retraining Bayesian/fixed-share source replay improves all C/D/E/F fitsheldout;
actual fresh G/H coder/decode validation COMPLETE,168+172=340B/1MiB before package.
V1reference-only FP32scalar multiplication defect preserved; native binary unchanged.
Native tensor export, word events,18word-feature and8word-softmax runs COMPLETE;
word_softmax_v2 tests stronger learned-literal/gate descendants on GPU1.
That10run screen is COMPLETE and loses incrementally; word_warmstart_v1 COMPLETE,
direct-word/full-bit finalists lose24.78/24.89B jointly on E/F. Persistent title laws
COMPLETE: identity wins. core_pipeline_profile_v1 queued after GPU0 training.
V2diagnostic archives used PPMD despite transformer-only flag; core_native_codec_v3
COMPLETE,repairs diagnostic bit law and tests trained weights through final CM.
Ordinary/light-mask gains on A/B/E are105/14/20B and105/18/19B; zero mask loses.
core_selective_v1 GPU1 PID2821 tests selective groups/high-lr/code-cell penalty.
word_cache_v1 CPU PID2839 tests eight completed-word donor output laws.
model_order_v1 CPU PID2863 recovers original tensor packing order and exact price.
Those are snapshot PIDs; inspect remote status/process before reuse or restart.
Native/GPU arithmetic fidelity remains open; inspect manifests before any restart.
Eleven old pilot checkpoints preserved root+local, redundant working paths unlinked;
see exact deletion/relocation manifest. Original corpus/models preserved; spent$0.
Working last measured~956MBfree; large intermediates/checkpoints use root scratch.
Completed checkpoints locally SHA-preserved; latest count/bytes are in
research_round9_downloaded_models_verified.json. Later checkpoints require follow-up.
Compact bundle1 locally verified379entries; trained archives/new sources needbundle2.
All96remaining descendant/protocol/dependency entries are research_round9_idea_program.json.
Full warm/package, independent corpus and eligibleCPU/RAM qualification remain pending.
ManagedGoal remainsusageLimited and was not resumed/replaced/mutated.
Automated follow-ups must honor that limit; week ends11October2026.
Older status/PID/count entries below are historical.
<!-- canonical-status-end -->'''
checkpoint=P/'research_round7_checkpoint.md';s=checkpoint.read_text(encoding='utf-8');a=s.index('<!-- canonical-status-start -->');b=s.index('<!-- canonical-status-end -->')+len('<!-- canonical-status-end -->');checkpoint.write_text(s[:a]+block+s[b:],encoding='utf-8')
# Append the integrated round8 report once; all current detail lives in round9.
old=P/'research_round8_report.md';s=old.read_text(encoding='utf-8');marker='<!-- round9-authoritative-implementation -->'
if marker not in s:old.write_text(s+f'\n\n{marker}\n## Round9 implementation continuation\n\nActual selected-core finetuning, full-word literal/OOV labels and new sequence/TTL/word architecture implementations now exist. The prior status in this report is historical. Read research_round9_report.md and research_round9_all96_execution_ledger.md for current work, measured limits and every unfinished family. No20% or qualifying record result is asserted.\n',encoding='utf-8')
print(json.dumps({'updated':now,'entries':len(program['entries']),'all_fully_explored':False,'report_bytes':(P/'research_round9_report.md').stat().st_size,'ledger_bytes':(P/'research_round9_all96_execution_ledger.md').stat().st_size}))

