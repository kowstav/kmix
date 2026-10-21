# Continuous-strength descendant, registered 6 October 2026

The semantic graph and clean-title pilots failed the registered finite gate.
Their smallest positive relation strength was 0.25. This leaves weak residuals
and jointly adjusted intercept/temperature untested. The following fits a tiny
statistical head, not the original transformer. Fitted coefficients are model
information and must be counted; this is no-core-retraining, not no fitting.

Export records from the exact repaired semantic observer before observing each
bit: uint16 native p, uint8 decoded label, six little-endian float32 residuals
(semantic last content, shuffled last, spelling last, semantic topic, shuffled
topic, constructor run). Set relation/run features to zero outside clean text.
No posterior changes the core or source features. Serialize fields individually,
27 bytes per scored bit, to avoid struct padding. Every bit after the completed
sync marker is present, including EOF fragments. Research labels are targets,
never predictor inputs. A/B/C/D first 128 KiB use unchanged native traces.

For each semantic/spelling/shuffled arm take X=[1,logit(p),a,b] and fixed base
offset l=logit(p). Fit theta in [-1,1]^4 on combined A/B only:

 f(theta)=sum_t [softplus(l_t+X_t theta)-y_t(l_t+X_t theta)].

This function is convex, with gradient X'(sigmoid(l+Xtheta)-y) and positive
semidefinite Hessian X' diag(q(1-q)) X. L-BFGS-B is a numerical solver, not itself
a proof of convergence. Independently evaluate the supporting-hyperplane bound:
 LB=f(theta)+min_{v in box} gradient'(v-theta).
 The minimum is at v_i=-1 if gradient_i>=0 else +1. Thus
 0 <= f(theta)-f* <= gradient'(theta-v).

Report the bound in bits and bytes, require <=0.05 byte before calling the
continuous development optimum certified. If this fails, preserve it as an
uncertified numerical result and improve solver precision/conditioning. A zero
feature's coefficient or a rank-deficient Hessian does not invalidate convexity.
The guarantee concerns the declared box, the recorded float32 features and ideal
Bernoulli likelihood, not unrestricted contexts or globally shortest archives.

Evaluate exact Q16 rounding on A/B and C/D with the frozen A/B coefficients.
Report continuous gain, integer gain, per-slice sign, semantic increment over
generic/shuffled/spelling controls, max neutral equality and price four binary64
coefficients =32 bytes per shipped copy plus a mode/arm selector. Actual archive
framing, loader, graph and CPU/RAM are additional. Also fit a generic head with
only intercept/temperature under the same box; charge its actual coefficient
count. Do not give each test slice its own untransmitted refit. C/D are previously
examined confirmation, not untouched holdouts. No new native candidate is promoted
without actual code and margin; promising later tests need fresh G/H and warm
production history. No rental, deletion or Goal mutation.

Independent checks: finite-difference gradient, random Hessian quadratic forms,
supporting-plane bound against a dense one-dimensional grid, identity q16 exact,
parser/feature hash reproduction and input record sizes. The result determines
whether another strength/gate search is justified, not whether all descendants
of semantics, placement or memory are impossible.
