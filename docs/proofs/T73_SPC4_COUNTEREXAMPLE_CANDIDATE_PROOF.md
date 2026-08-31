# T73 SPC4 Counterexample Candidate Proof

**Status:** `CANDIDATE_PROOF_PENDING_INDEPENDENT_REVIEW`

## 1. Notation and dependency ledger

Work over ℚ[[h]]. Let ᵉ be the two-gate tangle category with the frozen
`P_86 -> P_88` boundary convention, and let `M_R` be the MWW coefficient
bimodule of the actual balanced coefficient `R`. Its zeroth coefficient trace
is

\[
HH_0(\mathcal A;M_R)=
\left(\bigoplus_{T\in\operatorname{Ob}\mathcal A}M_R(T,T)\right)
/\langle\text{left--right action relations}\rangle .
\tag{1.1}
\]

Every premise below is labelled as one of:

| tag | meaning |
|---|---|
| **[E]** | external geometric or functorial theorem premise; it remains a visible Lean parameter until formalized |
| **[F]** | finite calculation independently recomputed from pinned data |
| **[D]** | primary-source theorem or definition, checked against the cited text |

A certificate status is never used as the sole justification for an
implication. The machine-readable classification is frozen in
`audit/t73_proof_dependency_manifest.json`.

Primary documentary anchors are MWW's one-handle and coefficient-trace
formulas (`D:/tmp/r6/mww_handle_src/1handles.tex:242-299,420-430`), BPW's
vertical-to-horizontal trace (`D:/tmp/r6/bpw_src/shadows/vertical.tex:11-58`),
and BHPW strictification
(`D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/equivalence.tex:468-493`).

## 2. Balanced Hattori coefficient and the diagonal class (v_T)

Let

\[
U=U_{(0,5)}:P_{86}\longrightarrow P_{88}
\]

be the physical oriented cup. The actual coefficient is the two boundary
components of one transported framed annulus. After the Hattori cut, its open
parts are an invertible tangle `B` and its framed pivotal dual, and the closed
part consists of 227 split circles. The load-bearing geometric input **[E]** is
the action-compatible, grading-preserving family

\[
H_{T,T'}:
M_R(T,T')\xrightarrow{\cong}
\operatorname{Hom}_{\mathcal A}(B\circ T,B\circ T')
\otimes_{\mathbb Q}A^{\otimes227},
\qquad A=\mathbb Q[X]/(X^2).
\tag{2.1}
\]

This is a two-sided identification using `B` and its dual. It is not the false
one-sided formula `M_R(T,T') = Hom(T,BT')`, and it does not require a
fictitious 2-morphism `1 -> B`.

Choose

\[
T=B^{-1}\circ U,
\qquad B\circ T=U.
\tag{2.2}
\]

Define the correctly typed diagonal element

\[
v_T=H_{T,T}^{-1}
\left(\operatorname{Id}_{B\circ T}\otimes X^{\otimes227}\right)
\in M_R(T,T).
\tag{2.3}
\]

Here `X^(tensor 227)` means 227 separate circle labels; it is never the
vanishing algebra product `X^227`. Since the identity chain map and every
circle label `X` are closed, `v_T` is closed. Its image in (1.1) is denoted
`[v_T]`.

Compatibility of (2.1) with the two MWW actions sends both action composites
to ordinary left and right composition by `B(f)`. Their difference is an
ordinary commutator, so `[v_T]` is a legitimate coefficient-`HH_0` class. This
balanced Hattori equivalence is an **[E]** premise until the transported
annulus and its 88 open rectangles are formalized.

## 3. Vertical--horizontal trace, strict functoriality, and the shadow (u)

BPW's vertical-to-horizontal construction **[D]**, applied through (2.1),
sends `[v_T]` to

\[
\operatorname{Id}_{B\circ T}\otimes X^{\otimes227}
=\operatorname{Id}_{U}\otimes X^{\otimes227}.
\tag{3.1}
\]

For `A=\mathbb Q[X]/(X^2)`, the counit is

\[
\epsilon(1)=0,\qquad \epsilon(X)=1.
\]

Hence the 227 actual caps give

\[
(\operatorname{Id}_U\otimes\epsilon^{\otimes227})
(\operatorname{Id}_U\otimes X^{\otimes227})
=\operatorname{Id}_U.
\tag{3.2}
\]

Strict BHPW functoriality **[E]/[D]** then gives, in the fixed endpoint block,

\[
qAKh_h(\operatorname{Sh}[v_T])(1)
=U_h(1)=u+O(h),
\qquad u=e_0-e_5,
\tag{3.3}
\]

with

\[
Q(88,86)=qHH_0(A_{88}^{86},A_{88}^{86})\cong M_1(88).
\tag{3.4}
\]

Equations (3.1)--(3.4) are a typed statement about the actual cup. The vector
calculation alone cannot replace the geometric Hattori and strict-functoriality
premises.

## 4. The (q=494) grading ledger

The grading arithmetic is finite **[F]**. The identity closure contributes
quantum degree `-44`; the 227 distinct `X` labels contribute `+227`. Thus

\[
q_{\rm raw}=-44+227=183.
\tag{4.1}
\]

The MWW one-handle shift is

\[
p_y+p_z=44+271=315,
\]

so the one-handle class has degree `498`. At the relevant cabled summand,
`\alpha=0`, `r=e_{m_2}+e_{r_{xy}}`, and `|r|=2`; for `N=2` the shift is `-4`.
Consequently

\[
\deg[v_T]=(0,183+315-4)=(0,494).
\tag{4.2}
\]

All later maps use this same rational MWW normalization. The deformation
terms `O(h)` change deformation order, not the underlying absolute quantum
grading.

## 5. The (-59072) point-push cubic and the \(\xi\) retraction

Put `h=q-1`, `t=q^(-2)`, and `\varepsilon=t-1`. The exact 45,360-letter
point-push calculation gives **[F]**

\[
[\varepsilon^3]\,\ell(\rho(W)-I)u=7384.
\tag{5.1}
\]

Since

\[
\varepsilon=-2h+3h^2-4h^3+O(h^4),
\]

we obtain

\[
[h^3]\,\ell(\rho_h(W)-I)u=(-2)^3\,7384=-59072\ne0.
\tag{5.2}
\]

The input in (5.2) is `[v_T]`, through its shadow `u`. It is not

\[
\xi=\eta_R[T_0]-s_{\rm inv}\eta_R[T_1].
\]

For that auxiliary difference, the shadow already contains one factor
`(\rho_h(W)-I)`:

\[
\Phi_h\operatorname{Sh}(\xi)=(\rho_h(W)-I)u.
\]

Applying the same relative detector introduces a second factor, so

\[
\Delta_h(\xi)=\ell(\rho_h(W)-I)^2u=O(h^6),
\qquad \Delta_3(\xi)=0.
\tag{5.3}
\]

The recomputation is in
`D:/tmp/r6/eta_t1_delta3_reaudit/recompute_eta_t1_delta3.py`; the typed
distinction is recorded in
`D:/tmp/r6/eta_t1_delta3_reaudit/ETA_T1_DELTA3_DECISION.md`.

## 6. The fixed source (M_1(88)) and relative degree \(\nu=0\)

The actual source is the whole fixed-weight module `M_1(88)`, never
`M_0(88)`. For every canonical cabled state write

\[
V_s^{\rm can}=M_1(88)\otimes F_s,
\tag{6.1}
\]

where `F_s` contains only the subsequently added Frobenius factors. Define
the relative defect

\[
\nu=\#\{\text{labels }1\text{ in }F_s\}.
\tag{6.2}
\]

The mandatory endpoint defect inside `M_1(88)` is not counted. Thus the whole
base module, in particular `u=e_0-e_5` and its cubic image, sits in relative
degree `\nu=0`.

At constant order,

\[
\Delta(X)=X\otimes X,
\qquad
\Delta(1)=1\otimes X+X\otimes1.
\tag{6.3}
\]

Consequently dotted `psi1` and dotted sphere maps add only `X` labels and
preserve `\nu=0`; undotted `psi0` and undotted sphere maps add exactly one new
`1` and land in `\nu=1`. The canonical row is defined to vanish on every
`\nu\ge1` summand. Physical-copy permutations preserve `\nu`, so they cannot
return an undotted image to the detected head. This is the whole-source typed
argument; the inadmissible `M_0/XX` control is outside its domain.

The primary Frobenius formulas are in
`D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/preliminaries.tex:610-633`;
the endpoint audit is
`D:/tmp/r6/agents/qhh_naturality_hostile/HOSTILE_FULL_DOMAIN_DESCENT_AUDIT.md:44-93,140-145`.

## 7. The full beta/psi cocone

Let `n_s` be the physical owner/sign copy-count vector at state `s`, and let
`a` be an occupied-copy orbit of the relative `\nu=0` row. Set

\[
O(n_s,a)=\prod_{i,\pm}{n_{s,i}^{\pm}\choose a_i^{\pm}}.
\tag{7.1}
\]

Reynolds averaging is over physical cable copies, never over the `2` or `42`
internal gate passages. For an edge `s->t`, normalize the dual row by

\[
d(s,t;a)=\frac{O(n_t,a)}{O(n_s,a)}.
\tag{7.2}
\]

The factors telescope:

\[
d(s,t;a)d(t,r;a)=d(s,r;a),
\tag{7.3}
\]

and reverse edges use the reciprocal. This covers every finite cable state
and both lattice directions.

Let `\lambda_s:V_s^{\rm actual}->\mathbb Q` be the transported normalized
row. On the entire typed source, the required two-handle equations are

\[
\lambda_s\circ\beta_s(b)=\lambda_s,
\qquad
\lambda_t\circ\psi_e^{[0]}=0,
\qquad
\lambda_t\circ\psi_e^{[1]}=\lambda_s.
\tag{7.4}
\]

The permutation part follows from Reynolds invariance and (6.2). A labelled
pure-braid residual is `I+O(h)` on the fixed-weight endpoint qHH module, so,
after multiplication by `W-I=O(h^3)`, it first affects order `h^4` and not the
cubic functional. Equation (7.4) is the claimed whole-source cocone premise
**[E]**; the orbit algebra (7.1)--(7.3) is the part to be proved in Lean.

The MWW relations are in
`D:/tmp/r6/mww_handle_src/kirby.tex:265-283,331-345`; a typed local audit is
`D:/tmp/r6/agents/qhh_naturality_hostile/TYPED_PSI_REYNOLDS_ENDPOINT_THEOREM.md`.

## 8. The fixed-(Y) HJ basis and direct-(Q) sphere cocone

The next input **[E]** is a pairwise-disjoint determinant-one sphere system in
one fixed `Y=\partial W_2`, with its owner-point and framing data. The HJ basis
criterion is anchored in
`D:/tmp/r6/agents/hj_scope_hostile/hj_v3_source/version_23_RM.tex:644-674`.
Its concrete fixed-`Y`/direct-`Q` instantiation for this candidate remains an
external theorem premise until formalized and independently reviewed.

For each state choose an actual framed equivalence

\[
Q_s:V_s^{\rm actual}\xrightarrow{\cong}V_s^{\rm can}
\tag{8.1}
\]

directly at that vertex. For a signed sphere edge `e:s->t` and dot choice
`d\in\{0,1\}`, define

\[
C_e^d=Q_t^{-1}
\bigl(\operatorname{Id}_{\rm persistent}\otimes T_e^d\bigr)Q_s,
\tag{8.2}
\]

where

\[
T_e^0=\Delta^{b_e-1}(1),
\qquad
T_e^1=\Delta^{b_e-1}(X).
\]

If `E_b=\epsilon^{\otimes b}`, then the Frobenius identities are

\[
E_b\Delta^{b-1}(1)=0,
\qquad
E_b\Delta^{b-1}(X)=1.
\tag{8.3}
\]

Transporting the canonical counit row through (8.1) yields the full-source
sphere equations

\[
\lambda_t\circ C_e^0=0,
\qquad
\lambda_t\circ C_e^1=\lambda_s
\tag{8.4}
\]

for all three spheres and their signed directions.

Because each `Q_s` is a vertex potential rather than a path-defined choice,
intermediate equivalences cancel on every composite. Disjoint split trees,
coassociativity, and (7.3) give sphere/sphere, sphere/psi, and psi/psi
flatness. A pure braid inserted on only one route would not be a vertex
coboundary and is explicitly excluded by this construction; endpoint
permutation alone would not suffice.

## 9. Changing-endpoint naturality: \(\Phi\), \(W\), and \(K\)

For every finite cable state `s`, let `\Phi_s` be the MWW core-attachment
comparison, let `W_s(h)` be the transported point-push operator, and let
`C_e(h):V_s->V_t` be any beta, psi, or signed sphere edge. The required
whole-source squares are

\[
\Phi_t C_e^{\rm cabled}=C_e^{W_2}\Phi_s,
\qquad
W_t(h)C_e(h)=C_e(h)W_s(h).
\tag{9.1}
\]

MWW's core-attachment diagram supplies the first general comparison
(`D:/tmp/r6/mww_handle_src/kirby.tex:650-684`). Identifying the concrete
direct-`Q` maps, endpoint coordinates, and strict signs with (9.1) is an
external theorem premise **[E]**, not a certificate inference.

Write

\[
W_s(h)-I=h^3K_s+O(h^4).
\tag{9.2}
\]

Taking the cubic coefficient of the second square gives

\[
K_tC_{e,0}=C_{e,0}K_s
\tag{9.3}
\]

on the entire source. BHPW's strictification is anchored in
`D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/equivalence.tex:468-493`;
its application to every foam used here remains part of the named
strict-functoriality premise.

Define the cubic scalar family, on the fixed absolute grading, by

\[
\kappa_s(x)=
[h^3]\,\lambda_s(h)(\rho_h(W_s)-I)\Phi_h\operatorname{Sh}_s(x).
\tag{9.4}
\]

Equations (7.4), (8.4), and (9.3) imply

\[
\kappa_s\beta_s(b)=\kappa_s,
\quad
\kappa_t\psi_e^{[0]}=0,
\quad
\kappa_t\psi_e^{[1]}=\kappa_s,
\tag{9.5}
\]

and, for each signed sphere edge,

\[
\kappa_tC_e^0=0,
\qquad
\kappa_tC_e^1=\kappa_s.
\tag{9.6}
\]

These are linear-map identities, not tests on `[v_T]` alone.

## 10. The MWW quotient universal property

Let

\[
\mathcal V=\bigoplus_s V_s
\]

over every finite cabled state in both lattice directions. Let
`\mathcal R_{2h}` be spanned by

\[
\beta_s(b)x-x,
\qquad
\psi_e^{[0]}x,
\qquad
\psi_e^{[1]}x-x,
\tag{10.1}
\]

for all states, owner braids, edges, and source vectors. Let
`\mathcal R_{3h}` be spanned, for all three spheres and all source vectors,
by

\[
C_e^0x,
\qquad C_e^1x-x.
\tag{10.2}
\]

These are the `N=2` MWW relations
(`D:/tmp/r6/mww_handle_src/kirby.tex:331-378,459-489,705-759`). Define
`\kappa:\mathcal V->\mathbb Q` by restriction to the statewise rows.
Equations (9.5)--(9.6) give

\[
\mathcal R_{2h}+\mathcal R_{3h}\subseteq\ker\kappa.
\]

The quotient universal property therefore supplies a unique

\[
\bar\kappa:
\mathcal V/(\mathcal R_{2h}+\mathcal R_{3h})\longrightarrow\mathbb Q.
\tag{10.3}
\]

For the balanced diagonal class,

\[
\bar\kappa(q[v_T])=-59072\ne0.
\tag{10.4}
\]

Thus `q[v_T]` is nonzero and remains homogeneous of absolute quantum degree
494. Selected scalar receipts alone would not establish (10.3); its
whole-source quantifiers come from the premises and equations stated above.

## 11. The four-handle map and the standard-(S^4) comparison

MWW proves that a four-handle induces an isomorphism
(`D:/tmp/r6/mww_handle_src/kirby.tex:418-426`). The graded version used here is
the external premise that this isomorphism preserves the same absolute
bigrading as (4.2). It therefore carries `q[v_T]` to a nonzero class

\[
z_{494}\in\mathcal S^2_{0,494}(X(41,189,73);\mathbb Q).
\tag{11.1}
\]

The standard-sphere computation is

\[
\mathcal S^2_0(S^4;\mathbb Z)\cong\mathbb Z
\]

concentrated in bidegree `(0,0)`
(`D:/tmp/r6/mww_handle_src/kirby.tex:428-431`). Hence

\[
\mathcal S^2_{0,q}(S^4;\mathbb Q)=0\qquad(q\ne0).
\tag{11.2}
\]

Since `494 != 0`, graded diffeomorphism invariance makes (11.1) incompatible
with a diffeomorphism to `S^4`. Conditional on all named external inputs,

\[
X(41,189,73)\not\cong_{\rm diff}S^4.
\tag{11.3}
\]

Together with the separately checked Cappell--Shaneson determinant conditions
and the external homotopy-sphere implication, this is a candidate
counterexample to smooth four-dimensional Poincare.

## 12. Remaining formalization and external-review status

**Status: `CANDIDATE_PROOF_PENDING_INDEPENDENT_REVIEW`.**

This document proves internally that:

- the complete cocone equations annihilate every displayed MWW generator;
- annihilation gives a quotient functional;
- the value `-59072` makes the quotient class nonzero;
- a nonzero degree-494 class, four-handle graded invariance, and the standard
  `S^4` support theorem imply non-diffeomorphism.

Finite verified inputs **[F]** are the point-push coefficient and nonzero
integer, the grading arithmetic, and the relevant determinant arithmetic.

The following remain visible external theorem premises **[E]/[D]**:

- the balanced Hattori equivalence (2.1) and its action compatibility;
- BPW vertical-to-horizontal trace and the 227 actual counits;
- strict BHPW functoriality in the exact cobordism scope used here;
- a fixed-`Y`, pairwise-disjoint determinant-one HJ basis for this candidate;
- direct-`Q` state equivalences, flat squares, and whole-source cocone maps;
- the typed `\Phi/W` squares at every finite state;
- the graded four-handle comparison, standard-`S^4` computation, and graded
  diffeomorphism invariance.

Lean may kernel-check the finite Frobenius/Reynolds algebra, cubic conjugation,
universal-property deductions, and the final conditional implication. Until
the geometric premises are also formalized or imported from a trusted
library, a zero-`sorry` build proves only a conditional theorem. It does not
justify `FORMALLY_VERIFIED_COUNTEREXAMPLE` or external acceptance.
