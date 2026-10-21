# Wider source weight: nested finite optimization,6October2026

The completed source fit's selected neural_valid coefficient is exactly at
its upper bound1. Its supporting-plane certificate proves the registered
[-1,1]box optimum, not that larger source weights fail. A principled stronger
descendant extends only this coefficient to[-12,12], retaining intercept and
native-logit slope[-1,1]. All three are refitted on the same frozen A/B events.
The original feature is float32(valid*clip(logit(neural)-logit(native),-12,12)/12).
Do not change its clipping or float32cast in this branch. The widened box
contains the old family; use the exact original feature and a generalized
supporting-plane box certificate. No retraining of the core or neural weights.

Interpretation: on unclipped cases the new range includes a full neural
logit-difference and signed rejection, instead of allowing only one twelfth
of it. These are normalized binary probabilities; this is not a claim about
an optimal word model. Record the old active-bound derivative and Hessian,
new coefficients/ideal certificate, exactQ16loss/tax and both prediction SHAs.
Charge both coefficient copies plus a6bit selector for31original choices
and this nested-bound choice. No actual code/shipping cost is removed.

Current C/D outcomes already belong to the narrow frozen-source experiment.
Do not reuse them as fresh confirmation of the widened family. Freeze the
wider result before generating newly registered E/F512KiB inputs at canonical
offsets190000000and430000000. Those source/native observations and actual
inline coding are conditional follow-up work, not executed by this fitter.
If development priced gain fails64B, preserve that decision. If it passes,
declare/reuse the E/F source-export controller and verify native controls,
then unchanged frozen coefficients on every E/F target. No further refit on
confirmation data. The narrow inline decoder job remains live and unchanged.

This is an explicit finite optimization/engineering improvement motivated by
an active constraint. All96families remainOPEN; no global optimum or20%claim.
Paid spending0, no deletion, no duplicate native inference.
