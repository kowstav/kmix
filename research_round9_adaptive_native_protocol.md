# R9 causal adaptive source: preregistered native test

Status: actual native implementation queued, after replay selection locked.
Selected law: 5 experts (native, 0.5/1/1.5/2 times frozen wider log-odds
correction), uniform initial weights, posterior after each bit, fixed-share
epsilon=1-2^(-1/262144) in units of bits. No future word, oracle hint or
neural training is used. The original model updates remain unchanged.

C/D/E/F replay gains vs fixed wide were +66.62/+59.77/+61.25/+119.53B
per512KiB. These are likelihood gains, not actual package bytes. E/F were
previously observed in other fits, so new G/H are registered before running:
canonical offsets65000000 and375000000, length524288bytes each. No
position search or further policy fitting is allowed on G/H.

Use a new isolated native tree in /root scratch. Build with the identical
compiler, classical/transformer defines and floating-point options, retaining
all changed sources. Run a32KiB neutral-mode reference and independent decode.
On each G/H cold slice first generate observation-only teacher native archive,
Q16,19source channels and193byte hidden-state records. Compute the previously
frozen adaptive Q16 replay. Then encode with the actual adaptive implementation
and require every Q16 probability to match replay, with unchanged hidden state.
Decode in a separate directory/process; compare every decoded byte, every Q16
and hidden-state record. Record CPU, wall, peak whole-process RSS and file SHA.

Store traces in root scratch because working disk has less than1GB free;
preserve compact results, exact executed sources, binary and archives locally.
Preserve models/data and every failure. No deletion is authorized by this
protocol. Measure actual lab executable size; this is not a packed production
stub delta. A wider/full warm run and official package/resource accounting are
still needed before any prize/percentage improvement claim.

The exact update observes the bit once, immediately before original Perceive.
Known-bit preprocessing/pretraining does not create an external prediction and
does not update the adaptive bank. Raw coder modes must not accidentally update
it. Neutral mode returns the original integer law and leaves state untouched.
Posterior order is fixed and compiled without fast-math for the adaptive helper
if a trace mismatch reveals contraction/reassociation sensitivity.
