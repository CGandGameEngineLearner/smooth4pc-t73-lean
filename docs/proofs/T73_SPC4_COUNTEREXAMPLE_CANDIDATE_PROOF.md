# T73 SPC4 counterexample candidate proof

**Status:** `CANDIDATE_PROOF_PENDING_INDEPENDENT_REVIEW`

## 1. Conditional theorem, scope, and notation

This document proves a conditional implication. It does not report an
unconditional counterexample, a formally verified counterexample, or external
acceptance.

> **Conditional theorem.** Let \(X=X(41,189,73)\). Assume the external
> geometric and functorial premises **E1--E12** listed in Section 15. Then the
> MWW lasagna module of \(X\) over \(\mathbb Q\) contains a nonzero homogeneous
> class of quantum degree \(494\). Hence \(X\) is not diffeomorphic to the
> standard \(S^4\). If one also assumes the Cappell--Shaneson homotopy-sphere
> theorem in the form **E13**, then \(X\) is a conditional counterexample to
> smooth four-dimensional Poincare.

Every assertion has exactly one status:

| tag | exact meaning |
|---|---|
| **[P] `proved_in_document`** | follows here from previously displayed hypotheses and equations |
| **[F] `finite_verified`** | exact finite calculation with a named recomputation path |
| **[E] `external_theorem`** | geometric, functorial, or field-coefficient premise kept as an explicit hypothesis |

A certificate status never substitutes for an **[E]** premise.

Let \(\mathcal A\) be the two-gate tangle category with the fixed
\(P_{86}\to P_{88}\) boundary convention. For a finite state
\(s=(\alpha,r)\), define the **raw MWW state summand**

\[
C_s:=
\mathcal S^2_0\!\left(
W_1;
K(r-\alpha^-,r+\alpha^+)\cup L,\eta^r;
\mathbb Q
\right)
\{-(2|r|+|\alpha|)\}.
\tag{1.1}
\]

This is the \(N=2\) specialization of MWW's summand in
`D:/tmp/r6/mww_handle_src/kirby.tex:320-345`; it is not itself the cabled
quotient. Let \(\iota_s:C_s\to\mathcal C_{\rm cabled}\) be the summand
inclusion followed by the cabled quotient map. For every state keep three
types visible:

\[
C_s \xrightarrow{\Phi_s:=\Phi\iota_s} \mathcal W_s
    \xrightarrow{\operatorname{Sh}_s} E_s,
\qquad \Theta_s:=\operatorname{Sh}_s\Phi_s.
\tag{1.2}
\]

Here \(\Phi\) is MWW's cabled-quotient/core-attachment comparison,
\(\mathcal W_s\) is its state target, and \(E_s\) is the fixed-weight endpoint
space. The final presentation starts from \(\bigoplus_s C_s\), not from
endpoint spaces.

<a id="balanced-hattori-coefficient"></a>
## 2. Balanced Hattori coefficient

Let \(U=U_{(0,5)}:P_{86}\to P_{88}\) be the physical oriented cup. Cutting
the actual transported framed annuli gives open part \(B\sqcup B^\vee\) and
227 split circles. The required input **[E1]** is the action- and
grading-compatible family together with a typed automorphism

\[
B\in\operatorname{Aut}_{\mathcal A}(P_{88}),\qquad
B^{-1}B=BB^{-1}=\operatorname{Id}_{P_{88}},\qquad B^\vee=B^{-1},
\tag{2.0}
\]

where the last equality is the chosen framed pivotal identification. The
coefficient equivalence is

\[
H_{T,T'}:M_R(T,T')\xrightarrow{\cong}
\operatorname{Hom}_{\mathcal A}(B\circ T,B\circ T')
\otimes_{\mathbb Q}A^{\otimes227},
\qquad A=\mathbb Q[X]/(X^2).
\tag{2.1}
\]

This is two-sided. It is not
\(M_R(T,T')=\operatorname{Hom}(T,BT')\), and it uses no fictitious mate
\(\mathbf1\to B\). MWW supplies the ambient one-handle/HH\(_0\) formula
(`D:/tmp/r6/mww_handle_src/1handles.tex:242-299,420-430`), not this
candidate-specific balanced identification; (2.1) therefore remains **E1**.

<a id="actual-diagonal-class"></a>
## 3. Actual diagonal class

Choose a categorical inverse and set

\[
T=B^{-1}\circ U,\qquad B\circ T=U.
\tag{3.1}
\]

Define

\[
v_T=H_{T,T}^{-1}
\left(\operatorname{Id}_{B\circ T}\otimes X^{\otimes227}\right)
\in M_R(T,T).
\tag{3.2}
\]

Here \(X^{\otimes227}\) means separate labels, never the vanishing product
\(X^{227}\). Under **E1**, (3.2) is a cycle and determines
\([v_T]_{\mathrm{coeff}}\) in

\[
HH_0(\mathcal A;M_R)=
\left(\bigoplus_{S}M_R(S,S)\right)/\langle fg-gf\rangle.
\tag{3.3}
\]

The identity-to-trace construction is MWW's Chern/Hattori class
(`D:/tmp/r6/mww_handle_src/1handles.tex:783-787`). Binding (3.2) to the actual
transported-annulus class is the separate premise **[E2]**.

<a id="vertical-horizontal-trace"></a>
## 4. Vertical-horizontal trace

BPW's vertical trace and natural functor to horizontal trace send
\(p\xrightarrow{\alpha}Fp\) to \(\operatorname{Sh}[p,\alpha]\)
(`D:/tmp/r6/bpw_src/shadows/vertical.tex:11-58`). The candidate application
**[E3]** is

\[
[v_T]_{\mathrm{coeff}}\longmapsto
\operatorname{Id}_{U}\otimes X^{\otimes227}.
\tag{4.1}
\]

Since \(\epsilon(X)=1\), the 227 counits send this to \(\operatorname{Id}_U\).
Denote the resulting one-handle trace class by \([v_T]_{1h}\). In its base
endpoint coordinates,

\[
\operatorname{Sh}_{1h}([v_T]_{1h})=u+O(h),
\qquad u=e_0-e_5\in E_{s_0}=Q(88,86)=M_1(88).
\tag{4.2}
\]

The counit evaluation is **[P]** after **E3**; identification with the actual
cup is still external.

<a id="strict-functoriality"></a>
## 5. Strict functoriality and grading ledger

BHPW states strict functoriality for tangle cobordisms
(`D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/equivalence.tex:468-487`).
Its use for every foam, sign, endpoint adapter, and core-attachment movie here
is retained as **[E4]**; the broader foam scope is separately noted at
`D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/equivalence.tex:489-493`.

The numerical degree ledger is exact **[F1]**:

\[
-44+227=183,\quad44+271=315,\quad183+315=498.
\tag{5.1}
\]

The raw \(-44\), 227 labels, one-handle shift \(+315=44+271\), and later
shift \(-4\) are independently itemized at
`D:/tmp/r6/agents/finite_type_leading/ORDINARY_SHADOW_HATTORI_CHAIN_RESULT.md:100-115`
and
`D:/tmp/r6/grading_attack/ledger/Q494_SPHERE_GRADING_LEDGER.md:45-60`;
`AuditArithmetic.lean:87-91` checks the last subtraction. Thus
\([v_T]_{1h}\) has quantum degree 498.

The candidate-specific assertion that the actual lift occurs at
\(s_0=(\alpha=0,r=e_{m_2}+e_{r_{xy}})\), hence \(|r|=2\), is included in
**E3** rather than inferred from this arithmetic. At that state the \(N=2\)
cabled shift is the finite-verified \(-4\). The raw-state representative

\[
\widetilde v_{s_0}\in C_{s_0}
\tag{5.2}
\]

has degree \(498-4=494\). The coefficient class, one-handle class, raw-state
representative, and final quotient class are distinct objects. Premises
**E3--E4** include the typed cabled binding

\[
\Theta_{s_0}(\widetilde v_{s_0})=u+O(h).
\tag{5.4}
\]

<a id="point-push-cubic"></a>
## 6. Point-push cubic

Put \(h=q-1\), \(t=q^{-2}\), and \(\varepsilon=t-1\). The finite word audit
supplies **[F2]**

\[
f(\varepsilon):=\ell(\rho(W)-I)u
=7384\varepsilon^3+O(\varepsilon^4),
\tag{6.1}
\]

including vanishing coefficients in degrees 0, 1, and 2. It does not prove
the operator assertion \(\rho(W)-I=O(\varepsilon^3)\) on every endpoint
space. Since \(\varepsilon=-2h+3h^2-4h^3+O(h^4)\), **[P]**

\[
[h^3]f(\varepsilon(h))=(-2)^3\,7384=-59072\ne0.
\tag{6.2}
\]

Recompute with

```powershell
python -B D:\tmp\r6\eta_t1_delta3_reaudit\recompute_eta_t1_delta3.py --write
```

and see
`D:/tmp/r6/eta_t1_delta3_reaudit/ETA_T1_DELTA3_DECISION.md#2-exact-raw-word-calculation`.
The input is \([v_T]_{\mathrm{coeff}}\), not
\(\xi=\eta_R[T_0]-s_{\rm inv}\eta_R[T_1]\). The latter already contains one
\((\rho(W)-I)\); the same detector introduces its square, whose first nonzero
\(\varepsilon\)-term has degree six, so \(\delta_3(\xi)=0\) **[F2]**.

<a id="relative-nu-ledger"></a>
## 7. Intrinsic relative defect ledger

For a physical-copy word \(x\in E_s\), let \(d_s(x)\) be its total number of
labels \(1\), and let \(b_s\) be the mandatory state baseline fixed before any
old/new factorization. Define

\[
\nu_s(x)=d_s(x)-b_s.
\tag{7.1}
\]

This is intrinsic to material-copy data, not the label count in a chosen
factor \(F_s\). The head \(u\) has \(\nu_{s_0}=0\). At constant order,

\[
\Delta(X)=X\otimes X,\qquad
\Delta(1)=1\otimes X+X\otimes1.
\tag{7.2}
\]

Premise **[E5]** binds actual maps to this ledger: dotted psi/sphere
insertions preserve \(\nu=0\), undotted insertions increase it by one, and
the constant row vanishes on \(\nu\ge1\). Formula (7.2) proves the canonical
algebra **[P]**; its actual-map binding is **E5**. No \(M_0(88)\) source is
introduced.

<a id="beta-psi-cocone"></a>
## 8. Constant beta/psi cocone and Reynolds normalization

At state \(s\), let

\[
G_s=\prod_i(S_{k_{s,i}^-}\times S_{k_{s,i}^+}),\qquad
\mathsf R_s^0=\frac1{|G_s|}\sum_{g\in G_s}P_s(g),
\tag{8.1}
\]

where \(P_s\) is the genuine physical-copy permutation representation. There
is no separate map from \(S_k\) into the coloured braid group. For a row
\(r\), put \(\mathsf R_s^{0,*}r=r\mathsf R_s^0\), and for an occupancy vector
\(a\), put

\[
O_s(a)=\prod_{i,\pm}{k_{s,i}^{\pm}\choose a_i^{\pm}}.
\tag{8.2}
\]

Reynolds averaging uses physical copies, never the 2 or 42 internal gate
passages. Choose vertex coordinates
\(Q_s:E_s\xrightarrow{\cong}E_s^{\rm can}\). Write
\(\bar\lambda_s^a\) for the canonical row on orbit \(a\) and
\(\lambda_s^a=\bar\lambda_s^aQ_s\). For a **forward** psi stabilization
\(e:s\to t=s+e_i\), the canonical target row is defined orbitwise by

\[
\bar\lambda_t^a=
\frac{O_t(a)}{O_s(a)}\,
\mathsf R_t^{0,*}
\left(
\operatorname{zeroext}_e(\bar\lambda_s^a)\otimes E_b
\right),
\qquad
\lambda_t^a=\bar\lambda_t^aQ_t,
\tag{8.3}
\]

when both orbit sizes are nonzero. Here \(E_b=\epsilon^{\otimes b}\), and
\(\operatorname{zeroext}_e\) is the typed extension of the persistent row to
the new physical-copy coordinates. If \(O_s(a)=0\), there is no source-orbit
equation and the newly appearing target row is set to zero. If
\(O_s(a)>0\) but \(O_t(a)=0\), the target row is also zero and annihilation of
the actual edge image is required explicitly in **E6**. No zero denominator
is used. On present orbits the factors telescope **[P]**:

\[
\frac{O_t(a)}{O_s(a)}\frac{O_r(a)}{O_t(a)}
=\frac{O_r(a)}{O_s(a)}.
\tag{8.4}
\]

Let \(\lambda_s=\sum_a\lambda_s^a\). The Frobenius identities and (8.3)
give the canonical constant pullbacks **[P]**

\[
\bar\lambda_t\psi_{e,0}^{0,\rm can}=0,
\qquad
\bar\lambda_t\psi_{e,0}^{1,\rm can}=\bar\lambda_s.
\tag{8.5}
\]

Let

\[
B_s^{\rm actual}(b):C_s\to C_s,
\qquad
\Psi_e^{d,\rm actual}:C_s\to C_t
\]

be the actual beta and forward-psi maps, with endpoint maps
\(\widehat\beta_s(b)\) and \(\widehat\psi_e^d\). Premise **[E6]** consists of
the typed shadow equations

\[
\Theta_sB_s^{\rm actual}(b)=\widehat\beta_s(b)\Theta_s,
\qquad
\Theta_t\Psi_e^{d,\rm actual}=\widehat\psi_e^d\Theta_s,
\tag{8.6}
\]

the leading action

\[
\widehat\beta_s(b)=P_s(\bar b)+O(h),
\tag{8.7}
\]

where \(\bar b\in G_s\) is the material-copy permutation, and the binding of
the actual constant psi maps to (8.5), namely
\(Q_t\widehat\psi_{e,0}^dQ_s^{-1}=\psi_{e,0}^{d,\rm can}\). It also includes actual mixed-square
compatibility whenever two forward stabilizations, or a forward psi and a
sphere edge, reach the same state. Canonical orbit-factor compatibility
follows from (8.4); its geometric binding is not silently inferred. The
quotient relation is the symmetric equality generated by each forward psi
map. No reverse psi operator is defined, and no exact finite-\(h\) pure-braid
cocone is claimed.

<a id="fixed-y-hj-basis"></a>
## 9. Fixed-Y HJ basis

HJ's basis criterion is at
`D:/tmp/r6/agents/hj_scope_hostile/hj_v3_source/version_23_RM.tex:644-674`.
The displayed matrix is unimodular, \(|\det|=1\), **[F3]**. The row-major
orientation pinned in `AuditArithmetic.lean` gives \(+1\); the alternate
column/orientation convention in the local HJ audit gives \(-1\). Only
unimodularity is used. The
candidate premise **[E7]** is stronger: in one fixed \(Y=\partial W_2\), the
three spheres are simultaneously embedded, pairwise disjoint, represent the
basis, carry the required relative-link, owner-point, orientation, framing,
and sign data, and satisfy the HJ replacement hypotheses.

HJ alone does not give direct-Q. Candidate-specific open locations remain in
`D:/tmp/r6/agents/unimodular_easy_spheres/FINAL_CHOSEN_HJ_BASIS_TOPOLOGY_AUDIT.md`
under `Gate 2`, `Gate 3`, `Gate 5`, and conditional `Gate 6`; these are
unresolved boundaries, not supporting theorem citations.

<a id="direct-q-sphere-cocone"></a>
## 10. Direct-Q sphere cocone

Keep the actual maps fixed. For a signed sphere edge \(e:s\to t\), write

\[
C_e^{d,\mathrm{actual}}:C_s\to C_t,\qquad
\widehat C_e^d:E_s\to E_t.
\tag{10.1}
\]

Let \(Q_s:E_s\xrightarrow{\cong}E_s^{\rm can}\), and write the canonical
target as \(E_s^{\rm can}=P_s^{\rm persistent}\otimes F_s\). Define insertion
**operators**, not elements used as maps,

\[
\iota_e^0(x)=x\otimes\Delta^{b_e-1}(1),\qquad
\iota_e^1(x)=x\otimes\Delta^{b_e-1}(X).
\tag{10.2}
\]

The direct-Q premise **[E8]** consists of two separate typed equations:

\[
Q_t\widehat C_e^dQ_s^{-1}
=\operatorname{Id}_{\rm persistent}\otimes\iota_e^d,
\tag{10.3}
\]

\[
\Theta_t C_e^{d,\mathrm{actual}}
=\widehat C_e^d\Theta_s.
\tag{10.4}
\]

It packages the fixed-\(Y\), relative-link, owner-point, sign, and
factorization data; it is not implied by HJ. For
\(E_b=\epsilon^{\otimes b}\), **[P]**

\[
E_b\Delta^{b-1}(1)=0,\qquad E_b\Delta^{b-1}(X)=1.
\tag{10.5}
\]

Together with the canonical orbit-row definition (8.3), this gives **[P]**

\[
\bar\lambda_t
(\operatorname{Id}_{\rm persistent}\otimes\iota_e^0)=0,
\qquad
\bar\lambda_t
(\operatorname{Id}_{\rm persistent}\otimes\iota_e^1)=\bar\lambda_s.
\tag{10.6}
\]

For a sphere edge, the target orbit rows use the same formula (8.3), with the
typed zero extension and \(E_b\) supplied by (10.2). Premise **E8** includes
the actual sphere/sphere and sphere/psi mixed-square bindings whenever two
routes reach the same state. Under **E5--E8**, translating (10.6) through
(10.3)--(10.4) gives the whole-source actual constant equations

\[
\lambda_t\widehat C_e^0=0,
\qquad \lambda_t\widehat C_e^1=\lambda_s.
\tag{10.7}
\]

The six stored selected scalar zeros do not prove (10.7). The missing
whole-source object is identified at
`D:/tmp/r6/agents/qhh_naturality_hostile/HOSTILE_FULL_DOMAIN_DESCENT_AUDIT.md#9-minimum-missing-equations-and-object`.
Only constant/cubic path coherence is required; no exact finite-\(h\) path
claim is made.

<a id="changing-endpoint-naturality"></a>
## 11. Typed changing-endpoint naturality and cubic family

For a forward psi edge the typed shadow square is (8.6); for a sphere edge it
is (10.4). MWW supplies
the abstract core-attachment comparison because the lower cobordism is the
upper surface union added cores
(`D:/tmp/r6/mww_handle_src/kirby.tex:650-684`); its simultaneous candidate
instantiation remains **E8**.

Let \(W_s(h):E_s\to E_s\) be the point-push word operator. For a
changing-endpoint psi or sphere edge, write \(\widehat D_e(h)\) for its
endpoint map. Premise **[E9]** is

\[
W_t(h)\widehat D_e(h)=\widehat D_e(h)W_s(h),
\qquad W_s(h)-I=h^3K_s+O(h^4)
\tag{11.1}
\]

on the whole typed space. The scalar audit (6.1) does not prove the second
operator statement. Extracting the cubic term gives **[P]**

\[
K_t\widehat D_{e,0}=\widehat D_{e,0}K_s.
\tag{11.2}
\]

The groups of physical copies differ across a changing-state edge, so (11.2)
alone does not move \(\mathsf R_t^0\) through \(\widehat D_{e,0}\). Premise
**E9** also contains the normalized row-level cubic identities

\[
\lambda_tK_t\mathsf R_t^0\widehat D_{e,0}^{0}=0,
\qquad
\lambda_tK_t\mathsf R_t^0\widehat D_{e,0}^{1}
=\lambda_sK_s\mathsf R_s^0.
\tag{11.2b}
\]

They hold on the whole source for every forward psi edge and every signed
sphere edge, with the orbit factors and absent-orbit convention of (8.3)
included. Equation (11.2b) is an external changing-state premise, not a
consequence of the constant counit identities or of selected scalar receipts.

Use (11.2) only for changing-endpoint psi/sphere maps; beta uses Reynolds.
Extend \(\lambda_s\) coefficientwise to
\(\widehat\lambda_s:E_s[[h]]\to\mathbb Q[[h]]\). Define the cubic endpoint
row using the constant Reynolds projector

\[
\kappa_s^E(y)=
[h^3]\widehat\lambda_s
\bigl((W_s(h)-I)\mathsf R_s^0y\bigr),
\tag{11.3}
\]

and on the actual raw state summand set \(\kappa_s=\kappa_s^E\Theta_s\).
Because \(\mathsf R_s^0P_s(\bar b)=\mathsf R_s^0\), equation (8.7) shows
that an actual beta changes the projected input only by \(O(h)\). Multiplying
by \(W_s-I=O(h^3)\) pushes that residual to order four. Thus beta descent
uses a genuine finite group average and no nonexistent group section or
\(K\)-beta equation.

At the base state fix

\[
\ell=e_{87}^*-e_2^*,
\qquad \lambda_{s_0}=\ell,
\qquad W_{s_0}(h)=\rho_h(W).
\tag{11.4}
\]

There is one positive and one negative physical copy of each active owner,
so the relevant constant Reynolds projector fixes the seed row. Premise
**E3** gives \(\Theta_{s_0}(\widetilde v_{s_0})=u+O(h)\). Premise **E9**
gives \(W_{s_0}-I=O(h^3)\), so the \(O(h)\) shadow correction begins in
order four after applying \(W_{s_0}-I\). Consequently (6.1)--(6.2) bind the
finite scalar to the family:

\[
\kappa_{s_0}(\widetilde v_{s_0})
=[h^3]\ell(\rho_h(W)-I)u=-59072.
\tag{11.5}
\]

Under **E5--E9**, (8.3)--(8.7), (10.6)--(10.7), (11.2)--(11.2b), the orbit
normalizations, and constant/cubic path coherence separately give **[P]**

\[
\kappa_s(B_s^{\mathrm{actual}}(b)x-x)=0,
\tag{11.6a}
\]

\[
\kappa_t(\Psi_e^{0,\mathrm{actual}}x)=0,
\qquad
\kappa_t(\Psi_e^{1,\mathrm{actual}}x)-\kappa_s(x)=0,
\tag{11.6b}
\]

\[
\kappa_t(C_e^{0,\mathrm{actual}}x)=0,
\qquad
\kappa_t(C_e^{1,\mathrm{actual}}x)-\kappa_s(x)=0.
\tag{11.6c}
\]

These hold for all beta, psi, and sphere generators in their distinct typed
domains.

<a id="mww-quotient"></a>
## 12. Exhaustive MWW quotient and descent

Let \(\mathcal C=\bigoplus_sC_s\). Let \(\mathcal R_{2h}\) be spanned by all

\[
B_s^{\rm actual}(b)x-x,
\qquad
\Psi_e^{0,\rm actual}x,
\qquad
\Psi_e^{1,\rm actual}x-x,
\tag{12.1a}
\]

and let \(\mathcal R_{3h}\) be spanned by all

\[
C_e^{0,\mathrm{actual}}x,\qquad
C_e^{1,\mathrm{actual}}x-x.
\tag{12.1b}
\]

Quantifiers range over every finite state, every owner braid, every forward
psi stabilization, each specified signed sphere edge, and every source
vector. The equivalence relation generated by a forward psi equality is
symmetric; no reverse psi map is added. Their completeness and quotient universal property are
**[E10]**, sourced in
`D:/tmp/r6/mww_handle_src/kirby.tex:331-378,459-489,705-759`.

Define \(\kappa:\mathcal C\to\mathbb Q\) statewise. Equations (11.6a)--(11.6c) prove
**[P]**, conditional on **E5--E10**, that

\[
\mathcal R_{2h}+\mathcal R_{3h}\subseteq\ker\kappa.
\]

Thus **[P]** there is a unique

\[
\bar\kappa:\mathcal C/(\mathcal R_{2h}+\mathcal R_{3h})\to\mathbb Q,
\qquad \kappa=\bar\kappa\pi,
\tag{12.2}
\]

where \(\pi\) is the quotient map.

The explicit base binding (11.4)--(11.5) gives

\[
\bar\kappa(\pi(\widetilde v_{s_0}))=-59072\ne0.
\tag{12.3}
\]

Therefore **[P]** \(\pi(\widetilde v_{s_0})\ne0\) in quantum degree 494.
This is conditional algebra from exhaustive cocone equations; it is not a
claim that those candidate-specific equations were internally proved.

<a id="four-handle-comparison"></a>
## 13. Four-handle comparison

MWW states that a four-handle induces an isomorphism
(`D:/tmp/r6/mww_handle_src/kirby.tex:418-426`). Premise **[E11]** is
the exact rational, grading statement: this is an isomorphism of bidegree
\((0,0)\). It preserves the nonzero quantum-494 class; it does not move that
class to bidegree \((0,0)\).

<a id="standard-s4-control"></a>
## 14. Standard-S4 control and conclusion

MWW gives the integral computation concentrated in bidegree zero
(`D:/tmp/r6/mww_handle_src/kirby.tex:428-431`). MWW defines the invariant and
its bigrading at `D:/tmp/r6/mww_handle_src/kirby.tex:8-57`, and explicitly
works over a field for the one-handle reduction at
`D:/tmp/r6/mww_handle_src/1handles.tex:15-20` and
`D:/tmp/r6/mww_handle_src/introduction.tex:128-134`. The direct rational
statement used here is nevertheless premise **[E12]**, not an unproved
base-change inference:

\[
\mathcal S^2_{0,q}(S^4;\mathbb Q)=0\qquad(q\ne0).
\tag{14.1}
\]

Premise **E12** also includes graded diffeomorphism invariance. Combining
(12.3), the bidegree-\((0,0)\) four-handle isomorphism, and (14.1) proves
**[P]**, under **E1--E12**, that

\[
X(41,189,73)\not\cong_{\rm diff}S^4.
\tag{14.2}
\]

Separately, **[E13]** is the Cappell--Shaneson theorem that the finite-verified
conditions \(\det A=\det(A-I)=1\) for the pinned matrix imply that
\(X(41,189,73)\) is a homotopy sphere. With **E13**, (14.2) is a conditional
SPC4 counterexample. The primary statement is Proposition 2.1 at
`D:/tmp/r6/QSC/kpr/cs_2404.05096.txt:128-151`; the determinant arithmetic is
checked in `AuditArithmetic.lean`.

## 15. Dependency and source/evidence table

| ID | status | role and anchor | unresolved boundary |
|---|---|---|---|
| E1 balanced Hattori | **[E] `external_theorem`** | ambient formula: `D:/tmp/r6/mww_handle_src/1handles.tex:242-299,420-430` | candidate \(B\sqcup B^\vee+227\) identification, typed invertibility, and framed \(B^\vee=B^{-1}\) binding are not proved there |
| E2 diagonal binding | **[E]** | Hattori identity: `D:/tmp/r6/mww_handle_src/1handles.tex:783-787` | candidate inverse image remains a premise |
| E3 BPW trace/cup/state binding | **[E]** | `D:/tmp/r6/bpw_src/shadows/vertical.tex:11-58` | actual 227-cap movie and \(s_0=(0,e_{m_2}+e_{r_{xy}})\) binding are extra |
| E4 strict scope | **[E]** | `D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/equivalence.tex:468-493` | exact foam scope remains explicit |
| F1 degree | **[F] `finite_verified`** | `D:/tmp/r6/agents/finite_type_leading/ORDINARY_SHADOW_HATTORI_CHAIN_RESULT.md:100-115`; `D:/tmp/r6/grading_attack/ledger/Q494_SPHERE_GRADING_LEDGER.md:45-60`; `AuditArithmetic.lean:87-91` | actual state binding is in E3 |
| F2 scalar | **[F]** | `D:/tmp/r6/eta_t1_delta3_reaudit/ETA_T1_DELTA3_DECISION.md#2-exact-raw-word-calculation` | scalar, not global operator valuation |
| E5 intrinsic \(\nu\) | **[E]** | algebra: `D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/preliminaries.tex:610-633` | actual-map binding is candidate-specific |
| E6 beta/psi | **[E]** | MWW: `D:/tmp/r6/mww_handle_src/kirby.tex:265-345` | whole-domain equations remain premises |
| E7 fixed-Y HJ | **[E]** | HJ: `D:/tmp/r6/agents/hj_scope_hostile/hj_v3_source/version_23_RM.tex:644-674` | local audit Gates 2,3,5,6 remain open/conditional |
| F3 determinant | **[F]** | `AuditArithmetic.lean:59-60` | determinant implies neither E7 nor E8 |
| E8 direct-Q/shadow | **[E]** | MWW core square: `D:/tmp/r6/mww_handle_src/kirby.tex:650-684` | HJ does not prove the factorization |
| E9 cubic naturality | **[E]** | diagnostic: `D:/tmp/r6/agents/qhh_naturality_hostile/HOSTILE_FULL_DOMAIN_DESCENT_AUDIT.md#6-is-pure-braid-ioh-enough` | F2 proves neither the global operator valuation nor the normalized Reynolds-edge identities (11.2b) |
| E10 complete MWW quotient | **[E]** | `D:/tmp/r6/mww_handle_src/kirby.tex:459-489,705-759` | completeness is required on all raw state summands |
| E11 graded four-handle | **[E]** | `D:/tmp/r6/mww_handle_src/kirby.tex:418-426` | rational bidegree-\((0,0)\) form stays explicit |
| E12 rational S4 and graded diffeomorphism | **[E]** | grading/invariant: `D:/tmp/r6/mww_handle_src/kirby.tex:8-57`; field scope: `D:/tmp/r6/mww_handle_src/1handles.tex:15-20`, `D:/tmp/r6/mww_handle_src/introduction.tex:128-134`; four/S4: `D:/tmp/r6/mww_handle_src/kirby.tex:418-431` | direct rational statement remains a premise, not an inferred base change |
| E13 CS bridge | **[E]** | `D:/tmp/r6/QSC/kpr/cs_2404.05096.txt:128-151`; finite determinants: `AuditArithmetic.lean` | homotopy-sphere bridge is external |
| P1 descent | **[P] `proved_in_document`** | Sections 11--12 | conditional on E5--E10 |
| P2 nonstandard | **[P]** | Sections 13--14 | conditional on E1--E12 |

The 13 explicit HTML anchors above exactly match the manifest consumer IDs.

## 16. Honest closing status

Finite arithmetic and the scalar are **[F]**. Frobenius, Reynolds-ratio,
coefficient-extraction, and quotient deductions are **[P]**. Geometric
typing, exhaustive cocones, changing-endpoint operator data, and rational
final comparison are **[E]**. Therefore the status remains

```text
CANDIDATE_PROOF_PENDING_INDEPENDENT_REVIEW
```

Even zero-`sorry` Lean proves only the conditional implication unless
**E1--E13** are formalized or imported from trusted libraries. This document
claims neither formal verification nor external acceptance.
