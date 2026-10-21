# Native inline final-Q16 residual, registered6October2026

Advance only the frozen neural_valid head from the separate weak-source
confirmation: C/D512K exactQ16gains63.987319271/61.732765608B, both positive
and better than generic. Those are replay losses, not archived/package savings.
Coefficients stay exactly binary64[.0015585303798630623,-.008865910048333772,1].
Do not refit or widen the box in this branch.

Copy the already verified source observer tree without its objects/binaries.
Add an external-Q16method to Predictor, called **after** Encoder/Decoder obtain
their usual native integerp from the unchanged Predict(). Capture the current
byte-mixer probability at the same pre-target observation point. Maintain one
bool equal to the previous completed hidden row's validity: initializefalse,
set!last_of_piece only at the existing completed-byte transformer transition.
This reproduces the prior-byte flag without reading target/trace files. Reset,
out-of-vocabulary and article/window boundaries must use the existing contract.

At the external call useell=log(p/(65536-p)); normalize/clamp the neural
logit-difference identically, with the intermediatefloat32cast used by the
registered feature array. Computez=ell+theta0+theta1*ell+theta2*feature;
q=clamp(floor(65536*sigmoid(z)+.5),1,65535). Use binary64math and preserve the
float32 feature cast. A test-only zero mode returns integerp directly, avoiding
a quantization round trip. Never feed the external correction back into the
original predictor/model/SSE updates. No dictionary, sidechannel or trace file
is required by inference; the trace envs are observation only.

First prove zero-mode A/B32K archive and all integer probabilities identical
to native reference and independently decode each. Then encode/decode the
frozen candidate on C/D512K. Candidate integer trace must match the previously
frozen independent replay SHA exactly; every decoded byte must match raw input.
Record archive byte delta, coder overhead versus ideal loss, CPU/wall/RSS,
whole lab binary/source hash and additional state. Check explicit invalid/reset
feature law and unaffected core hidden-state traces. Failures remain preserved
before a separately named repair; no coefficient reselection on C/D.

A successful lab binary is still not a submitted production package. Report
its binary delta against a matched build; coefficients embedded in that delta
must not be charged twice as a separate file. A clean no-instrumentation/loader
build, actual submitted-size accounting, warmed/full payload and complete
CPU/RAM rules remain gates. Raw feature/trace files are research data, never
free decoder inputs. No20%or global compression optimum follows from this tiny
residual. Spending0, no model/data deletion or paid rental.
