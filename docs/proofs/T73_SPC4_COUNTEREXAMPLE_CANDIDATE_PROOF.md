# T73 SPC4 counterexample candidate proof

**Status:** `CANDIDATE_PROOF_PENDING_INDEPENDENT_REVIEW`

## 1. Conditional theorem, scope, and notation

This document proves a conditional implication. It does not report an
unconditional counterexample, a formally verified counterexample, or external
acceptance.

> **Conditional theorem.** Let \(X=X(41,189,73)\). Assume the external
> geometric and functorial premises **E4--E12** listed in Section 15. Sections
> 2--3 discharge the balanced Hattori input E1/E2; Section 4 constructs the
> coefficient quantum-trace comparison and its divided cubic functional;
> Section 5 constructs the selected raw-state binding E3. Section 9
> proves the weak sphere-basis deduction from the E7 handle-realization input.
> Then the
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
inclusion followed by the cabled quotient map, and let \(\Phi\) be MWW's
cabled-quotient/core-attachment isomorphism. These maps are distinct from the
raw endpoint shadow.

For a cut tangle \(R_s\), MWW's one-handle theorem gives an isomorphism
\(\Gamma_s\) from its coefficient \(HH_0\) to the unshifted raw summand. When a
coefficient quantum shadow \(\mathsf S_s\) is supplied, define

\[
C_s \xrightarrow{\ \Gamma_s^{-1}\ }
HH_0(\mathcal A_s;M_{R_s})
\xrightarrow{\ \mathsf S_s\ }E_s,
\qquad \Theta_s^{\rm raw}:=\mathsf S_s\Gamma_s^{-1}.
\tag{1.2}
\]

The arrows in (1.2) include the one-handle and displayed cabled grading
normalizations; Section 5 writes them numerically at \(s_0\).

Section 5 constructs (1.2) at the selected state. E6 and E8, not E3, require
a coherent family of such raw shadows compatible with every beta, psi, and
sphere map. Below the superscript is suppressed: \(\Theta_s\) always means this
raw map, not a map already descended through the cabled quotient. The final
presentation starts from \(\bigoplus_s C_s\), not from endpoint spaces.

<a id="balanced-hattori-coefficient"></a>
## 2. Balanced Hattori coefficient

Let \(U=U_{(0,5)}:P_{86}\to P_{88}\) be the physical oriented cup. For each
selected owner, MWW's \(K_i(1,1)\) is the pair of oppositely oriented
boundaries of one actual framed tubular annulus. Cut those annuli at the
matched \(y/z\) gate fibers and use the fixed \(z\)-wickets.

Each \(y\)-touching connector is the pair of long sides of a literal annulus
subrectangle. Adding its \(z\)-wicket and its prescribed noncrossing
\(y\)-boundary chord gives a properly embedded disk. Distinct connectors give
disjoint subrectangles, and the boundary chords do not interleave. Thus the 44
disks on each side are simultaneous. They standardize the paired paths to a
motion of 44 wickets, whose induced 88-endpoint framed tangle is denoted
\(B_{\rm act}\). Reversing the motion is its inverse. The 227 \(z\)-\(z\)
subrectangles close to pairwise-disjoint product-framed disks, hence to an
ordered split \(U^{227}\).

The connector classification is checked directly against the actual
2,126,291-crossing Gauss order in
`D:/tmp/t73_actual_cable_unit/ACTUAL_PD_CABLE_UNIT_CERT.json`; it recovers
exactly 88 \(y\)-\(z\) and 227 \(z\)-\(z\) connectors. Simultaneous disk
embeddedness follows from their being literal subrectangles of the actual
framed annuli, not from a certificate status field. The proof does not name
the open braid word or the unknown framing integer. Any hidden
pure braid or full twist remains inside \(B_{\rm act}\) and is not forgotten.

The framing supplies a global product parametrization of each tubular annulus.
Choose the gate cuts as product fibers. The product coordinate between the
west and east disk systems is a framed isotopy fixed on the insertion disks
and their endpoint collars; isotopy extension gives one relative movie

\[
\mathfrak h:
R\simeq_{\rm rel}
B_{\rm act}\sqcup B_{\rm act}^{\vee}\sqcup U^{227}.
\tag{2.h}
\]

Reversing the product coordinate and the boundary orientation gives the
framed pivotal adapter

\[
\vartheta:B_{\rm act}^{\vee}\xrightarrow{\cong}B_{\rm act}^{-1}.
\tag{2.p}
\]

Thus the west/east standardizations are not two independently chosen units:
they are the source and target of the same annulus motion. Integral framing
twists alter that motion but preserve (2.h)--(2.p).

Consequently **[P]**, using strict functoriality E4, the actual cut supplies
the action- and grading-compatible family together with a typed automorphism

\[
B_{\rm act}\in\operatorname{Aut}_{\mathcal A}(P_{88}),\qquad
B_{\rm act}^{-1}B_{\rm act}=B_{\rm act}B_{\rm act}^{-1}
=\operatorname{Id}_{P_{88}},\qquad B_{\rm act}^\vee=B_{\rm act}^{-1},
\tag{2.0}
\]

where the last equality is the chosen framed pivotal identification. The
coefficient equivalence is

\[
H_{T,T'}:M_R(T,T')\xrightarrow{\cong}
\left(
\operatorname{Hom}_{\mathcal A}(B_{\rm act}\circ T,B_{\rm act}\circ T')
\{-44\}
\right)
\otimes_{\mathbb Q}A^{\otimes227},
\qquad A=\mathbb Q[X]/(X^2).
\tag{2.1}
\]

Use the convention
\(M_R(T,T')=\operatorname{KhR}_2(R\cup T'\cup\overline T)\), compatible with
\(\operatorname{Hom}(T,T')=\operatorname{KhR}_2(T'\cup\overline T)\).
Extending the literal annulus cut by identities on \(T,T'\) identifies the
source with
\((B_{\rm act}T')\cup\overline{(B_{\rm act}T)}\sqcup U^{227}\).
The shift \(\{-44\}\) removes the built-in \(p(N-1)=44\) normalization of
\(\operatorname{Hom}_{\mathcal A}\), so (2.1) is the raw closure grading.
Field monoidality gives (2.1), and gluing locality gives both MWW action
squares. This is two-sided. It is not
\(M_R(T,T')=\operatorname{Hom}(T,B_{\rm act}T')\), and it uses no fictitious
mate \(\mathbf1\to B_{\rm act}\). The ambient formulas are at
`D:/tmp/r6/mww_handle_src/1handles.tex:173-229,242-299,420-430`.

<a id="actual-diagonal-class"></a>
## 3. Actual diagonal class

Let \(W:P_{88}\to P_{88}\) be the physical point-push braid. Choose the
categorical inverse of \(B_{\rm act}\) and set

\[
T_1=B_{\rm act}^{-1}\circ U,
\qquad
T_0=B_{\rm act}^{-1}\circ W\circ U.
\tag{3.1}
\]

Then, without any commutation assumption,

\[
B_{\rm act}T_1=U,
\qquad
B_{\rm act}T_0=WU.
\tag{3.1b}
\]

For \(i=0,1\), define the diagonal representative and its coefficient-trace
class

\[
v_i=H_{T_i,T_i}^{-1}
\left(\operatorname{Id}_{B_{\rm act}T_i}\otimes X^{\otimes227}\right)
\in M_R(T_i,T_i),
\qquad
\eta_R[T_i]=[v_i]\in HH_0(\mathcal A;M_R).
\tag{3.2}
\]

The selected input is \(T=T_1\) and \(v_T=v_1\), so
\([v_T]_{\rm coeff}=\eta_R[T_1]\).

Here \(X^{\otimes227}\) means separate labels, never the vanishing product
\(X^{227}\). Since \(M_R\) is already \(\operatorname{KhR}_2\) homology,
both \(v_i\) are homogeneous elements/classes **[P]** in

\[
HH_0(\mathcal A;M_R)=
\left(\bigoplus_{S}M_R(S,S)\right)/\langle fg-gf\rangle.
\tag{3.3}
\]

The identity-to-trace construction is MWW's Chern/Hattori class
(`D:/tmp/r6/mww_handle_src/1handles.tex:783-787`). The literal Section 2
equivalence binds both classes in (3.2) to the actual transported-annulus
coefficient **[P]**.

<a id="vertical-horizontal-trace"></a>
## 4. Vertical-horizontal trace

BPW's vertical trace and natural functor to horizontal trace send
\(p\xrightarrow{\alpha}Fp\) to \(\operatorname{Sh}[p,\alpha]\)
(`D:/tmp/r6/bpw_src/shadows/vertical.tex:11-58`). Applying that theorem to the
literal Section 2 representable coefficient gives the ordinary trace **[P]**

\[
\eta_R[T_1]\longmapsto
\operatorname{Id}_{U}\otimes X^{\otimes227},
\qquad
\eta_R[T_0]\longmapsto
\operatorname{Id}_{WU}\otimes X^{\otimes227}.
\tag{4.1}
\]

Since \(\epsilon(X)=1\), the 227 counits send this to \(\operatorname{Id}_U\).
Denote the resulting one-handle trace class by \([v_T]_{1h}\).

The generic endpoint comparison is obtained without identifying the internal
grading with a scalar. Let \(\zeta\) be the quantum-trace parameter,
\(R_\zeta=\mathbb Q[\zeta,\zeta^{-1}]\), and use the quantum degree as the
pregrading while retaining the homological degree separately. Define

\[
 q\!\operatorname{Tr}_\zeta(\mathcal A;M_R)=
 \frac{\displaystyle\bigoplus_T M_R(T,T)\otimes R_\zeta}
 {\left\langle
 M_R(1,f)m-\zeta^{|f|_q}M_R(f,1)m
 \right\rangle},
 \tag{4.2}
\]

where \(f:S\to T\) is homogeneous and \(m\in M_R(T,S)\). Both displayed
terms are diagonal. Right-exact base change of this explicit cokernel gives

\[
 q\!\operatorname{Tr}_\zeta(\mathcal A;M_R)
 \otimes_{R_\zeta}R_\zeta/(\zeta-1)
 \cong HH_0(\mathcal A;M_R).
 \tag{4.3}
\]

This is the MWW enriched coefficient coend itself: the underlying bigraded
Hom spaces, coefficient spaces, and gluing actions are unchanged, and only
the scalar \(\zeta^{|f|_q}\) specializes to one.

There is a concrete quantum shadow on (4.2). If

\[
 H_{T,S}(m)=\sum_j a_j\otimes z_j,
 \qquad a_j:B_{\rm act}T\to B_{\rm act}S,
\]

set

\[
 \mathsf S_\zeta([m])=
 \sum_j\epsilon^{\otimes227}(z_j)\,
 \mathsf Q\!\left(\operatorname{tr}_\zeta(a_j)\right).
 \tag{4.4}
\]

Here \(\mathsf Q\) is BPW's quantum vertical-to-horizontal trace followed by
the strict BHPW endpoint functor. The two E1 action squares send the two terms
of a relation in (4.2) to

\[
 \operatorname{tr}_\zeta(B_{\rm act}f\circ a_j)
 \quad\text{and}\quad
 \zeta^{|f|_q}\operatorname{tr}_\zeta(a_j\circ B_{\rm act}f),
\]

which agree by the defining quantum-trace relation
(`D:/tmp/r6/bpw_src/traces/graded.tex:90-108`). Thus (4.4) is a map on the
coefficient quotient, not a \(K_0\)-only evaluation. BHPW's strict endpoint
functor and natural Chern square identify its target with the actual weight-86
quantum \(HH_0\) modules
(`D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/intro.tex:386-421`;
`D:/tmp/r6/bpw_src/quantum/qannulus.tex:289-309`).

Complete at \(\zeta=1+h\). The selected identity and the 227 counits give

\[
\mathsf S_h([v_T]_{1h})=u_h,
\qquad u_h\bmod h=u=e_0-e_5\in Q(88,86)=M_1(88).
\tag{4.5}
\]

Fix the normalized Artin-word endpoint operator \(\rho_h(W)\) and normalized
cap \(\widehat C(h)\). This is a chosen linear postcomposition on the fixed
endpoint target; equality with any projectively normalized cabling map is not
used here. Since every pure generator is \(I+O(h)\) and \(W\in\Gamma_3\),

\[
\rho_h(W)-I\in h^3\operatorname{End}(Q(88,86)[[h]])
\tag{4.6}
\]

on the entire endpoint module. Hence

\[
 \mathcal D_h=\widehat C(h)(\rho_h(W)-I)\mathsf S_h
\]

has image in \(h^3\mathbb Q[[h]]\). Divide the whole map by \(h^3\), reduce
modulo \(h\), and use (4.3). This gives an ordinary individual-class
functional

\[
 \mathcal D_3:HH_0(\mathcal A;M_R)\longrightarrow\mathbb Q.
\tag{4.7}
\]

Lift independence follows because two lifts differ by \(hy\), whose divided
values differ by \(h\mathcal D'_h(y)\). Therefore the coefficient-level
ordinary-cyclic/generic-endpoint bridge and 227 counits are **[P]**. Section 5
constructs its selected raw-state binding E3; the global strict foam scope
remains E4.

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

The actual coefficient boundary has one negative and one positive cable on
each of \(m_2\) and \(r_{xy}\), and no others. In MWW's notation

\[
k^-=r-\alpha^-,\qquad k^+=r+\alpha^+.
\]

Thus **[P]** the unique state is

\[
s_0=(\alpha=0,r=e_{m_2}+e_{r_{xy}}),\qquad |r|=2.
\tag{5.2}
\]

Let

\[
\Gamma_{s_0}:HH_0(\mathcal A;M_R)\xrightarrow{\cong}
\mathcal S^2_0\!\left(W_1;K(r,r),\eta^r;\mathbb Q\right),
\qquad \deg_q\Gamma_{s_0}=315
\tag{5.3}
\]

be the literal gluing isomorphism in MWW's one-handle theorem
(`D:/tmp/r6/mww_handle_src/1handles.tex:242-299`). Define the named raw element

\[
\widetilde v_{s_0}:=
\Gamma_{s_0}(\eta_R[T_1])\{-4\}\in C_{s_0}.
\tag{5.4}
\]

This is the labelled filling resealed through the actual one-handles, not a
preimage selected from surjectivity. The cabled shift is forced by MWW's
formula

\[
(1-N)(2|r|+|\alpha|)=(1-2)(4)=-4,
\]

so \(\widetilde v_{s_0}\) has degree \(498-4=494\). Equations (4.4)--(4.5)
and (5.3) give **[P]**, under the already separate strict-functoriality scope
E4,

\[
\Theta_{s_0}^{\rm raw}(\widetilde v_{s_0})=u_h,
\qquad u_h\bmod h=u=e_0-e_5.
\tag{5.5}
\]

The coefficient class, one-handle class, shifted raw-state representative,
and final quotient class remain distinct objects. Equation (5.5) does not
claim that the raw shadow has descended through beta/psi; that responsibility
belongs to E6.

<a id="point-push-cubic"></a>
## 6. Point-push cubic

Put \(h=\zeta-1\), \(t=\zeta^{-2}\), and \(\varepsilon=t-1\). The finite word audit
supplies **[F2]**

\[
f(\varepsilon):=\ell(\rho(W)-I)u
=7384\varepsilon^3+O(\varepsilon^4),
\tag{6.1}
\]

including vanishing coefficients in degrees 0, 1, and 2. The finite audit alone
does not prove an operator assertion; the whole-module divisibility used in
Section 4 follows separately from \(W\in\Gamma_3\) and the pure-generator
filtration. Since \(\varepsilon=-2h+3h^2-4h^3+O(h^4)\), **[P]**

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
## 9. The actual fixed-Y sphere basis (weak E7)

The weak existence/basis deduction needs neither the synthetic owner matrix
nor HJ. Premise **E7** is now narrowed to the assertion that the delivered
smooth handle presentation is the actual punctured candidate, has exactly
three 3-handles after
\(W_2\), no 4-handle in the punctured presentation, and outgoing boundary
\(S^3\) (`D:/tmp/s4pc_ruler/ENGINE/kirby_master/cs_presentation.py:9-14,66-76`
and `D:/tmp/s4pc_ruler/ENGINE/out/t73_eps0.erkmo.json:179-199,285-289`).
Turn the cobordism

\[
Y=\partial W_2\longrightarrow S^3
\]

upside down. It is a cobordism from \(S^3\) obtained by attaching exactly
three 1-handles, so **[P]**

\[
Y\cong \#_3(S^1\times S^2).
\tag{9.1}
\]

The three actual 3-handle attaching spheres are the belt spheres of those
dual 1-handles. Consequently they already are a simultaneous, smoothly
embedded, pairwise-disjoint basis of
\(H_2^{\rm sph}(Y;\mathbb Z)\cong\mathbb Z^3\). Coorientations can be chosen
independently and the 3-handle attaching framing is unique. Thus **[P]** the
basis conclusion follows from the E7 handle-realization premise. The cited
builder/ERKMO bytes record the handle counts but do not by themselves prove
that realization; certificate status is not used as its proof.

It does **not** supply simple endpoint maps. The historical synthetic
K1/K2/th2/C3 construction is not used here: its 63-source tree construction
is obstructed by \(\det[K1,K2,th2]=189\) and
\(\det[K1,K2,th3]=-40\). All owner-coordinate, direct-Q, and map-level claims
remain in E8.

<a id="direct-q-sphere-cocone"></a>
## 10. Direct-Q sphere cocone

For the easy hemisphere \(\Delta_+\), MWW already proves the split-unknot cap
formula on every cabled summand
(`D:/tmp/r6/mww_handle_src/kirby.tex:613-648`): undotted is zero and dotted is
the identity. The maps below are therefore the hard
\(\Phi^{-1}\Psi_{\Delta_-}\Phi\), equivalently the actual \(\Sigma_-\) maps of
`kirby.tex:650-684`.

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

It packages the state-dependent endpoint coordinates, owner-copy ordering,
sign, \(\Sigma_-\) factorization, and mixed-square data. The final boundary
link is empty, so no old-link-relative premise remains; nevertheless a
boundary diffeomorphism standardizing the spheres need not extend over
\(W_2\), and does not identify the state-dependent \(\Sigma_-\) maps. For
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
routes reach the same state. Under **E5**, **E6**, the proved Section 9 basis,
and **E8**, translating (10.6) through
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
Sections 4--5 give
\(\Theta_{s_0}(\widetilde v_{s_0})=u+O(h)\). Premise **E9**
gives \(W_{s_0}-I=O(h^3)\), so the \(O(h)\) shadow correction begins in
order four after applying \(W_{s_0}-I\). Consequently (6.1)--(6.2) bind the
finite scalar to the family:

\[
\kappa_{s_0}(\widetilde v_{s_0})
=[h^3]\ell(\rho_h(W)-I)u=-59072.
\tag{11.5}
\]

Under **E5**, **E6**, **E8**, and **E9**, (8.3)--(8.7),
(10.6)--(10.7), (11.2)--(11.2b), the orbit
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
**[P]**, conditional on **E5**, **E6**, and **E8--E10**, that

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
**[P]**, under **E4--E12**, that

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
| E1 balanced Hattori | **[P] `proved_in_document`** | actual paired-annulus disk system: Section 2 and `D:/tmp/t73_actual_cable_unit/ACTUAL_PD_CABLE_UNIT_CERT.json`; MWW formulas: `D:/tmp/r6/mww_handle_src/1handles.tex:173-229,242-299,420-430` | the unknown braid/framing is retained inside \(B_{\rm act}\), not identified or discarded |
| E2 diagonal binding | **[P]** | Section 3; Hattori identity: `D:/tmp/r6/mww_handle_src/1handles.tex:783-787` | selected input is \(T_1=B_{\rm act}^{-1}U\), never \(\xi\) |
| E3 selected raw-state binding | **[P] `proved_in_document`** | state and named representative: Section 5; MWW one-handle isomorphism `D:/tmp/r6/mww_handle_src/1handles.tex:242-299`; state formula `D:/tmp/r6/mww_handle_src/kirby.tex:320-345` | quotient descent is not hidden here; it remains in E6/E8 |
| E4 strict scope | **[E]** | `D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/equivalence.tex:468-493` | exact foam scope remains explicit |
| F1 degree | **[F] `finite_verified`** | `D:/tmp/r6/agents/finite_type_leading/ORDINARY_SHADOW_HATTORI_CHAIN_RESULT.md:100-115`; `D:/tmp/r6/grading_attack/ledger/Q494_SPHERE_GRADING_LEDGER.md:45-60`; `AuditArithmetic.lean:87-91` | \(-44+227+315-4=494\), with the state binding proved in Section 5 |
| F2 scalar | **[F]** | `D:/tmp/r6/eta_t1_delta3_reaudit/ETA_T1_DELTA3_DECISION.md#2-exact-raw-word-calculation` | scalar, not global operator valuation |
| E5 intrinsic \(\nu\) | **[E]** | algebra: `D:/tmp/r6/agents/finite_type_leading/bphw_1903_src/sections/preliminaries.tex:610-633` | actual-map binding is candidate-specific |
| E6 beta/psi | **[E]** | MWW: `D:/tmp/r6/mww_handle_src/kirby.tex:265-345` | whole-domain equations remain premises |
| E7 actual handle realization / fixed-Y basis | **[E]** | declared handle data: `D:/tmp/s4pc_ruler/ENGINE/kirby_master/cs_presentation.py:9-14,66-76`, `D:/tmp/s4pc_ruler/ENGINE/out/t73_eps0.erkmo.json:179-199,285-289`; basis deduction: Section 9 | realization remains external; once granted, existence/basis is proved and no simple map follows |
| F3 synthetic determinant | **[F]** | `AuditArithmetic.lean:59-60` | historical check, not consumed by the revised proof; implies no map statement |
| E8 direct-Q/shadow | **[E]** | easy hemisphere: `D:/tmp/r6/mww_handle_src/kirby.tex:613-648`; hard map/core square: `:650-684` | exact residual is whole-source factorization of \(\Phi^{-1}\Psi_{\Delta_-}\Phi\), plus coherent \(\Theta_s,Q_s\) |
| E9 cubic naturality | **[E]** | whole-endpoint \(h^3\) valuation: Section 4; diagnostic: `D:/tmp/r6/agents/qhh_naturality_hostile/HOSTILE_FULL_DOMAIN_DESCENT_AUDIT.md#6-is-pure-braid-ioh-enough` | the normalized changing-state/Reynolds-edge identities (11.2b) remain unproved |
| E10 complete MWW quotient | **[E]** | `D:/tmp/r6/mww_handle_src/kirby.tex:459-489,705-759` | completeness is required on all raw state summands |
| E11 graded four-handle | **[E]** | `D:/tmp/r6/mww_handle_src/kirby.tex:418-426` | rational bidegree-\((0,0)\) form stays explicit |
| E12 rational S4 and graded diffeomorphism | **[E]** | grading/invariant: `D:/tmp/r6/mww_handle_src/kirby.tex:8-57`; field scope: `D:/tmp/r6/mww_handle_src/1handles.tex:15-20`, `D:/tmp/r6/mww_handle_src/introduction.tex:128-134`; four/S4: `D:/tmp/r6/mww_handle_src/kirby.tex:418-431` | direct rational statement remains a premise, not an inferred base change |
| E13 CS bridge | **[E]** | `D:/tmp/r6/QSC/kpr/cs_2404.05096.txt:128-151`; finite determinants: `AuditArithmetic.lean` | homotopy-sphere bridge is external |
| P1 descent | **[P] `proved_in_document`** | Sections 11--12 | conditional on E5, E6, E8--E10; Section 9 supplies the basis deduction from E7 |
| P2 nonstandard | **[P]** | Sections 13--14 | conditional on E4--E12 |

The 13 explicit HTML anchors above match the manifest consumer IDs. The
manifest is the frozen v1 allocation: this revised proof discharges its E1/E2
inputs and the coefficient part formerly assigned to E3 by the
paired-annulus/quantum-trace argument, and
splits its coarse E7
owner/direct-Q clause between the narrowed E7 realization input and E8.

## 16. Honest closing status

Finite arithmetic and the scalar are **[F]**. The balanced coefficient input,
weak fixed-Y sphere-basis deduction, Frobenius, Reynolds-ratio,
coefficient-extraction, and quotient deductions are **[P]**. The hard
hemisphere cocone, changing-endpoint operator data, and rational final
comparison remain **[E]**. Therefore the status remains

```text
CANDIDATE_PROOF_PENDING_INDEPENDENT_REVIEW
```

Even zero-`sorry` Lean proves only the conditional implication unless the
remaining **E4--E13** premises are proved. This document
claims neither formal verification nor external acceptance.

## 17. Decisive post-audit boundary

The subsequent premise attacks give the following mathematical, rather than
procedural, status.

1. **E1 is closed without naming the braid.** The actual paired annulus
   subrectangles give simultaneous proper disks, hence an unknown but genuine
   wicket-braid unit \(B_{\rm act}\), its pivotal inverse, and 227 split disk
   factors. Hidden pure-braid/framing data remain inside \(B_{\rm act}\).

2. **Weak E7 is a conditional deduction.** If the delivered punctured smooth
   handle realization really has exactly the declared three 3-handles to
   \(S^3\), its actual attaching spheres are the belt-sphere basis after turning
   the cobordism upside down. The serialized object declares, but does not
   geometrically construct, those attaching spheres.

3. **E3 is closed at the raw-state level.** The coefficient quantum trace, its
   specialization to ordinary MWW \(HH_0\), the individual endpoint map, the
   divided cubic functional, and the named degree-494 representative in the
   forced state \(s_0\) are constructed. This does not assert beta/psi or
   sphere descent; those are E6 and E8.

4. **E8 is the decisive three-handle map.** MWW computes the easy
   \(\Delta_+\) hemisphere. No existing artifact proves that the hard
   \(\Phi^{-1}\Psi_{\Delta_-}\Phi\) map on every actual cabled state is a
   split-tree operator up to one coherent vertex transport. A Peiffer word and
   the unimodular matrix \(I-\Lambda^2A\) does not supply the missing embedded,
   framed actual-to-canonical corridors; knotting a carrier preserves those
   algebraic data and destroys a product-annulus conclusion.

5. **Two proposed shortcuts fail.** Unimodularity of the ordinary
   \(3\)-to-\(2\) boundary matrix does not imply clean geometric \(2/3\)-handle
   cancellation; group-ring/intersection and embedded-slide data are missing.
   Restricting to quantum degree \(494\) is not a finite computation, because
   dotted psi stabilization and the three-handle lift lattice remain in the
   same normalized degree.

6. **The old early-psi kill does not apply.** The current selected seam
   \(U_{(0,5)}\) joins an \(r_{xy}\) endpoint to an \(m_2\) endpoint. Removing
   either owner destroys that cross-owner cup; in endpoint weights the proposed
   lower blocks are \(Q(84,86)=0\) and \(Q(4,86)=0\). An owner-local
   \(\psi^{[0]}\) ribbon and owner beta cannot create this connectivity. Thus
   the historical \(u_\Omega\in\operatorname{im}\psi^{[0]}\) result concerns a
   different input and is retired for \(v_T\). Full E6 image membership remains
   open.

Consequently the displayed implication is a sound conditional theorem, but
the current mathematics does **not** establish an SPC4 counterexample.

## 18. Relative-lift no-go and the only viable escape

Let a relative marked mapping-class group \(G_{\rm rel}\) act on a module \(V\)
through \(\rho\), and let

\[
\pi:G_{\rm rel}\twoheadrightarrow G_{\rm coarse},\qquad K=\ker\pi.
\]

Here \(G_{\rm coarse}\) retains the incidence, endpoint permutation, pair
linking, framing totals, Peiffer augmentation, and the matrix \(D\), while
\(K\) contains the pure-braid/point-push information forgotten by those data.

**No-go theorem.** If a row \(\lambda\in V^*\) is invariant under \(K\), or
factors through the coinvariants \(V_K\), then for every \(W\in K\) and every
\(u\in V\),

\[
\lambda(\rho(W)-I)u=0.
\tag{18.1}
\]

Indeed \(\lambda\rho(W)=\lambda\); equivalently,
\((\rho(W)-I)u\) is zero in \(V_K\). More generally, any construction that is
claimed to depend only on the coarse datum and to give the same answer for
every relative lift must annihilate the complete \(K\)-relation span.

For T73, the point-push \(W\) has identity endpoint permutation and zero
recorded pair-linking/framing totals, but its full Artin word is nontrivial.
Thus it lies in the kernel of the coarse E8 records, while

\[
[h^3]\,\ell(\rho_h(W)-I)u=-59072.
\tag{18.2}
\]

Equation (18.2) proves that this kernel is not harmless presentation noise.
In particular, any proposed descent that declares every unseen relative lift
irrelevant while keeping a fixed \(u,\ell\) is incompatible with the computed
signal.

There is one valid escape: **equivariant transport, not invariance**. For a
fully marked movie \(a:p\to q\) with induced isomorphism \(R_a\), transport all
data together,

\[
W_q=R_aW_pR_a^{-1},\qquad
u_q=R_au_p,\qquad
\ell_q=\ell_pR_a^{-1}.
\tag{18.3}
\]

Then

\[
\ell_q(W_q-I)u_q=\ell_p(W_p-I)u_p.
\tag{18.4}
\]

The same covariance must hold statewise for every psi/sphere edge and for the
MWW \(\Phi/\Theta\) maps. Loop holonomy is harmless only when it transports all
of these objects coherently.

Section 2 avoids this no-go for E1 by retaining the unknown relative lift
inside \(B_{\rm act}\); it never asks the kernel to act trivially. The escape
does not close E8/E9. The fiber of the coarse record
need not be one connected torsor: locally knotted carriers can share all
recorded coarse data without being related by a relative ambient movie. Hence
one must still construct a coherent E8/E9 edge family in the actual component.
Torsor language removes gauge choice after those objects exist; it cannot
manufacture them.
