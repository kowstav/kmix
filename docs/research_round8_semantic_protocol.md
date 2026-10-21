# Frozen semantic graph: registered 6 October 2026

This is a new descendant of lexical algebra/geometry and context miners. It tests
whether corpus co-occurrence relationships add information that spelling alone
does not provide. The original compressor and transformer remain frozen. The
external pretrained representation and the derived graph are model information;
their shipped bytes must be included in both executable copies when applicable.

Source: Stanford's 2024 Wikipedia+Gigaword 50-dimensional GloVe release,
https://nlp.stanford.edu/data/wordvecs/glove.2024.wikigiga.50d.zip . Author page:
https://nlp.stanford.edu/projects/glove/ . Vectors are PDDL 1.0. Download and retain
the original zip, stream only dictionary-matching vectors, do not extract the
whole text corpus. Record download, graph, vector and source hashes. No rental,
deletion or transformer training. GPU graph construction is an encoder research
operation, not a permitted decoder requirement; the CPU decoder needs only IDs.

Map exactly the existing 44,515 dictionary IDs. Normalize vectors, take eight
highest cosine neighbors excluding the source and grammatical constructors and
requiring at least three letters. Missing source vectors use eight self IDs,
explicitly reported as fallback. Save uint16 little-endian graph and its text
equivalent; assess zlib and LZMA size, including framing later, not as a package.

Use the repaired, collision-free CleanExpert observer. Arms: generic calibration;
last completed content-word semantic neighbors; neighbor IDs shuffled within
the same frequency-rank band and spelling-length bucket; spelling geometry of
the same content word; semantic neighbors of title and most recent 16 content
words; corresponding shuffled neighbors. All use the identical constructor-run
feature, 25 frozen candidates, identical Bayesian context tree and q16 rule.
Each sparse word distribution is normalized against the same decoded-prefix
frequency prior; no unobserved word chooses a context or gate. Partial words,
entities and XML tags never become hints early. Current observed title is free
only because its bytes have already been coded.

Run parser/self-tests and exact normalization. Pilot A/B 131,072 bytes each with
native final integer traces. Report all six arms, global Bayesian mixtures and
all fixed-candidate costs; a retrospectively best fixed candidate is diagnostic
until its ID/prior cost is paid. Advance a semantic arm to ABCD 2M only if it beats
generic, its shuffled control and the spelling arm on each pilot and combined
by >=64 bytes.
Do not extrapolate failed gates as impossibility of semantic models. Positive
tests still require untouched G/H, full warm core, actual archive roundtrips,
graph/loader/container bytes, cold and full CPU/RAM accounting, and full package.

The reported full C3 peak is 9,765,024 KiB = 9,999,384,576 bytes. Only 615,424
bytes remain under a conservative decimal 10 GB interpretation. The uncompressed
eight-neighbor graph alone is 712,240 bytes. A qualifying implementation must use
compressed lookup, share existing buffers, or deliberately reduce another state
and measure its coding loss. This pilot does not satisfy that resource gate.

Higher-potential successors if this sparse graph loses: shared low-rank vectors
with calibrated signed relations, prefix-trained co-occurrence factors,
directed relation-conditioned cache selection, and finite paid article-topic
programs. These are distinct unexecuted experiments, not assumed victories.
