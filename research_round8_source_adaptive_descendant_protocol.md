# Pending descendant: causal adaptation of the measured source residual

Status: mathematical/engineering protocol, **not executed**. This extends the
fixed wider residual; it does not label that residual an absolute optimum.
Previously viewed C/D and E/F outcomes cannot be called untouched confirmation.

The fixed law is ell=log(p/(65536-p)), f=float32(clip(logit(nn)-ell,-12,12)/12)
times previous-byte validity, q=sigmoid(ell+a+b*ell+c*f). The measured wider
coefficients are a=.0016181118716570748, b=-.007454085408717222,
c=2.3818512619982752. Original core updates stay unchanged. Both sources are
known before the target bit, permitting a legal external probability correction.

First test a causal two-expert mixture of the exact native Q16 law and the frozen
wider law. Start weights w0=(.5,.5). After observing y, update

    w_post(k) = w_prior(k)*q_k(y) / sum_j w_prior(j)*q_j(y).

Before final mixture rounding, Bayesian mixing has the exact sequence identity

    P_mix(y_1:T) = sum_k w0(k)*P_k(y_1:T)
    L_mix <= min_k [L_k-log2(w0(k))].

This is a finite-expert guarantee, not a future-bit oracle or an architecture
optimum. Compute final Q16 rounding tax explicitly; do not relabel this bound
as an integer-coder guarantee. Updates use each expert's integer outcome law.

Then test fixed-share forgetting: w_next=(1-epsilon)*w_post+epsilon*w0.
For a half-life H **bits**, epsilon=1-2^(-1/H). Register epsilon=0 and a small
grid. Known decoded boundaries may start episodes; unknown future boundaries
may not. This makes TTL precise without storing future hints. Compare fixed
wider, native, no-forgetting, reversed/delayed-source and matched-state controls.
Only if utility drift is measured, add a small shared-coefficient multiplier
grid or causal roles. Charge grid code, parameters, selectors and inference.

An alternative branch updates three coefficients with a causal regularized
natural-gradient step. Cache x=(1,ell,f) and the prediction before the bit;
update exactly once after its outcome. A local rule is

    g_t = (q_t-y_t)*x_t
    F_t = rho*F_(t-1)+(1-rho)*q_t*(1-q_t)*x_t*x_t^T+ridge*I
    Delta theta = -eta*F_t^-1*[g_t+lambda*(theta-theta0)].

Use positive definite 3x3 Fisher state, prior regularization and a declared
KL/trust-region cap. This quadratic approximation supplies no global online
optimum certificate. Keep it separate from fixed-share until each helps.
Failed word-cache screens are not evidence for adding their banks to either.

Exact decoder contract: derive sources solely from decoded history, never from
exported traces. Preserve Predict/Perceive, core updates, byte/piece boundaries
and source-valid reset semantics. Cache the same pre-target feature and weight
state; update after the outcome in a fixed order. Use stable double log weights
or scaled positive weights. Keep every legal bit outcome reachable.

Begin with causal replay and normalization/zero/regret checks. Freeze a policy
before new independent slices. Require native zero-mode identity, every Q16
prediction matching replay, independent exact decode and unchanged core hidden
state. Then measure warm/full archive, packed package size, whole CPU and RAM.
Semantic state is small; only whole measured peak establishes compliance.

Include both coefficient copies and selectors in pilot amortization. Once
embedding is measured, count those bytes once through executable size. Do not
scale cold gains linearly, call growth of a tiny residual gain a 20% archive
improvement, or assert that this protocol exhausts TTL/retention architectures.
