# One-cup cell quotient: actual survival through one- and two-handle relations

Date: 2026-09-01
Scope: full MWW one-handle coefficient `HH_0`, followed by the two-handle
beta/psi quotient, through the divided cubic functional.  Sphere relations are
not included.

## Verdict

```text
selected final class:                              v_T = eta_R[T1]
relative xi as input to the same D3:               NOT the final class
full P44 left/right one-handle action:              ALREADY QUOTIENTED IN HH0
two-handle beta, all finite cable levels at h3:     KILLED BY COCONE
psi0 action-closed ideal through bound:             <=84
selected one-cup cell through degree:               86
psi1 compatibility:                                CORE RETRACTION / IDENTITY
actual divided quotient functional:                CONSTRUCTED
functional value on [v_T]:                         -59072
nonzero after one+two-handle quotient:              PROVED
generic t=3 rank used as proof:                     NO
sphere/full four-manifold conclusion:               NOT CLAIMED
```

The earlier mixed two-cup class fails because the action-closed `psi0` ideal
fills its entire through-84 cell.  The one-cup class lies in the next cell,
through degree 86.  Temperley--Lieb composition cannot raise through degree,
so the same failure mechanism cannot reach it.

## 1. Objects and the input-confusion firewall

Let `B_actual` be the actual E1 open coefficient unit and let

\[
U:P_{86}\longrightarrow P_{88}
\]

be the selected oriented one-cup tangle.  Put

\[
T_1=B_{actual}^{-1}U,
\qquad
v_T=H_{T_1,T_1}^{-1}
(\operatorname{Id}_U\otimes X^{\otimes227}).
\tag{1.1}
\]

Its coefficient trace class is

\[
[v_T]=\eta_R[T_1]\in HH_0(\mathcal C;M_R),
\]

and its endpoint shadow is the cup vector

\[
Sh([v_T])=u=e_0-e_5\in S^{(87,1)}.
\tag{1.2}
\]

Let `P_86:F_86 -> F_86` be a rational cell projector on endpoint `qHH_0`,
with image the `S^(87,1)` top cell and kernel containing `F_84`.  Define the
actual divided **top-cell** detector

\[
\mathcal D_3(x)=
[h^3]\,\widehat C_{87,2}(h)
(\rho_h(W)-I)P_{86}Sh_h(x).
\tag{1.3}
\]

The selected shadow already lies in the top cell, so inserting `P_86` does
not change its value.  The exact raw-word calculation gives

\[
\boxed{\mathcal D_3([v_T])=-59072.}
\tag{1.4}
\]

Now distinguish the relative class

\[
\xi=\eta_R[T_0]-s\eta_R[T_1],
\qquad
Sh(\xi)=(\rho_h(W)-I)u.
\tag{1.5}
\]

Applying the **same** detector (1.3) gives

\[
\mathcal D_3(\xi)
=[h^3]\widehat C(\rho_h(W)-I)^2u=0,
\tag{1.6}
\]

because `W-I=O(h^3)`.  The number `-59072` can also be read from `xi` by the
different plain-shadow functional `[h3] C Sh`, but that is not (1.3).

Therefore the final class for the present quotient proof is `[v_T]`, not
`xi`.  Equations (1.4) and (1.6) prevent the old input mix-up.

## 2. Full one-handle action is already handled

MWW's one-handle category has all tangles with the fixed oriented boundary
`P44`; its morphisms include the full left/right tangle actions.  At `q=1`,
the sign-preserving permutation quotient contains

\[
S_{44}^-\times S_{44}^+,
\]

not merely the provenance labels `rxy/m2`.

This action does not need to be quotient a second time.  The coefficient trace
is by definition

\[
HH_0(\mathcal C;M_R)=
\frac{\bigoplus_T M_R(T,T)}
{\langle L_f(m)-R_f(m)\rangle},
\tag{2.1}
\]

for **every** typed one-handle morphism `f`.  The quantum shadow respects these
relations before the endpoint quotient and cap are applied.  The rational cell
projector `P_86` and endpoint cap are linear postcompositions.  Thus (1.3) is
an actual functional on the full one-handle `HH_0`, not a row tested only
against a finite braid subgroup.

The uniform divisibility

\[
\rho_h(W)-I\in h^3\operatorname{End}(E_h)
\]

on the whole endpoint module makes division by `h^3` well defined; lift
independence after specialization is the cokernel argument in the Rees source
ledger.  Hence (1.4), an exact nonzero integer, replaces the old generic
`t=3` rank as the nonvanishing proof.

## 3. The through-degree firewall against psi0

Filter the oriented Temperley--Lieb/BN endpoint category by through degree.
Composition on either side cannot increase through degree.  The one-cup tangle
`U` has

\[
\operatorname{th}(U)=86.
\tag{3.1}
\]

An `rxy` balanced pair creation adds four y endpoints and necessarily creates
at least two cups.  Its image therefore has through degree at most 84.  An
`m2` creation adds more paired passages and has an equal or lower bound.  Thus

\[
\operatorname{th}
\left(\mathcal C\,\operatorname{im}\psi_i^{[0]}\,\mathcal C\right)
\le84
\tag{3.2}
\]

for every gate-crossing owner `i` (`rxy`, `ryz`, `m2`, `m3`).  Because
left/right actions preserve the filtration, (3.2) holds for their
**action-closed** psi0 ideals, not merely their initial columns.

The zero-gate owner `rzx` is a separate local factor and must not be smuggled
into (3.2).  For `L=empty`, its added balanced pair is the split complex
`A tensor A`.  Its two core counits satisfy (4.2) on the whole factor, so
`rzx-psi0` is zero and `rzx-psi1` has a left inverse.  Hence it also cannot
kill the base class, but for the Frobenius/core reason rather than a drop in
through degree (`D:/tmp/rzx_pair/RESULT.md`).

Let

\[
\operatorname{gr}_{86}=F_{86}/F_{84}.
\]

The shadow of `[v_T]` is the nonzero standard vector `e0-e5` in the
`S^(87,1)` top cell of `gr86`.  Every psi0 image maps to zero in this quotient.
This is precisely why the full-sign-parabolic calculation that kills
`S^(86,2)` does not kill the one-cup class.

The insertion of `P_86` in (1.3) is essential.  A literal diagrammatic cap on
the unprojected endpoint module can retain lower-turnback components; the cap
alone does not annihilate `F84`.  The quotient functional is nevertheless an
actual linear functional after the genuine qHH shadow.  No claim is made that
`P_86` itself is represented by one physical foam.

No evaluation at a generic numerical `t` is used in this argument.

## 4. Two-handle beta and psi1

At the base state the active owners each have one negative and one positive
physical copy, so their groups are `B_(1,1)`.  The constant permutation
quotient is trivial and every pure generator acts as

\[
I+O(h).
\]

Since the detector begins with `W-I=O(h^3)`, a beta correction changes it only
in order four.  Therefore

\[
\mathcal D_3(\beta_i(b)x)=\mathcal D_3(x).
\tag{4.1}
\]

At higher multiplicities, use the actual physical-copy common target and the
finite Reynolds average over signed copy selections.  The stable
standardization remainder is pure and again starts one order later.  Orbit
normalizations telescope along every owner path.

For a forward pair addition, MWW's local maps and the two W2 core counits obey

\[
(\epsilon\otimes\epsilon)\psi^{[0]}=0,
\qquad
(\epsilon\otimes\epsilon)\psi^{[1]}=I.
\tag{4.2}
\]

The raw degree `+2` of `psi1` is cancelled by the cabled shift `-2`; hence its
total degree is zero.  Equation (4.2) gives a left inverse to `psi1` and makes
the statewise rows satisfy

\[
\Lambda_{s+e_i}^{(3)}\psi_i^{[0]}=0,
\qquad
\Lambda_{s+e_i}^{(3)}\psi_i^{[1]}
=\Lambda_s^{(3)}.
\tag{4.3}
\]

Disjoint owner supports and the orbit telescope make all addition squares
commute.  This is the leading W2 core-evaluation cocone; it does not use the
rejected claim that a raw all-state endpoint shadow alone proves the quotient.

## 5. The actual quotient functional

Let

\[
\mathscr Q_{12}=
\left(\bigoplus_s HH_0(\mathcal C_s;M_{R_s})\right)
\Big/
\langle\beta x-x,\ \psi^{[0]}x,\ \psi^{[1]}x-x\rangle
\tag{5.1}
\]

denote the one-handle coefficient traces followed by the two-handle cabled
relations.  Sections 2--4 give a well-defined rational functional

\[
\overline{\mathcal D}_3:\mathscr Q_{12}\longrightarrow\mathbb Q
\tag{5.2}
\]

whose base row is (1.3).  In particular,

\[
\boxed{
\overline{\mathcal D}_3([v_T])=-59072\ne0.}
\tag{5.3}
\]

Therefore

\[
\boxed{[v_T]\ne0\text{ after the full one-handle and two-handle quotient}.}
\tag{5.4}
\]

This is an actual quotient nonvanishing theorem, not a generic matrix-rank
proxy.

The class is homogeneous of final MWW degree `(0,494)`: identity degree zero,
Hom closure `-44`, 227 `X` labels `+227`, one-handle shift `+315`, cabled shift
`-4`.

## 6. Controls and remaining boundary

For the standard/identity branch, `W=I`, so the same detector is identically
zero.  This is a useful control but not yet the final S4 comparison: the three
sphere relations still have to be annihilated by the same functional.

What is now proved:

- full one-handle `HH_0` descent;
- full action-closed psi0 exclusion by through degree;
- all-level beta/psi leading cocone;
- exact nonzero quotient value `-59072` on `[v_T]`.

What is not proved:

- full formal-q descent beyond the cubic coefficient;
- descent through any of the three sphere maps;
- nonzero class in the closed four-manifold invariant;
- SPC4 falsification.

The next gate is the sphere quotient.  It is not another beta/psi or
one-handle action calculation.

## Sources

- Full action ideal and through-degree firewall:
  [`TL_CELL_IDEAL_CLOSURE_RESULT.md`](../../evidence/public_geometry/source_notes/TL_CELL_IDEAL_CLOSURE_RESULT.md).
- Coefficient qTrace and divided detector:
  `D:/tmp/mr_rees_construct/MR_REES_QUANTUM_TRACE_SOURCE_LEDGER.md:26-125`.
- Input distinction `v_T` versus `xi`:
  [`ETA_T1_DELTA3_DECISION.md`](../../evidence/public_geometry/source_notes/ETA_T1_DELTA3_DECISION.md).
- Physical base class and degree:
  `D:/tmp/raw_state_binding/RAW_STATE_BINDING_RESULT.md` and
  [`ORDINARY_SHADOW_HATTORI_CHAIN_RESULT.md`](../../evidence/public_geometry/source_notes/ORDINARY_SHADOW_HATTORI_CHAIN_RESULT.md).
- Leading W2 core quotient factorization:
  `D:/tmp/w2_core_factor/RESULT.md`.
- MWW beta/psi/core relations:
  Manolescu--Walker--Wedrich, [arXiv:2206.04616](https://arxiv.org/abs/2206.04616), handle-presentation section.
