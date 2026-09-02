# T73 historical candidate proof

**Status:** `HISTORICAL; CURRENT PAPER DISCHARGES P0/C/S/P3`

> The current proof allocation is the LaTeX paper and the research notes for
> the public AR P0 witness, the coefficient comparison C, and relative S.
> Historical G1/TH artifacts and the old status table below are not
> load-bearing.

OPEN entries below document the retired large-certificate route.

Entry point for all colocated derivations and pinned large inputs:
`T73_COUNTEREXAMPLE_MATERIALS_INDEX.md`.

## 1. Conditional theorem, scope, and notation

This document proves a conditional implication. It does not report an
unconditional counterexample, a formally verified counterexample, or external
acceptance.

> **Conditional theorem.** Let \(X=X(41,189,73)\). Use the HJ replacement,
> complete-quotient, four-handle and rational-control results
> **E7, E10--E13** listed in Section 15.
> Sections 2--5 discharge the balanced
> Hattori, diagonal and selected raw-state inputs E1--E3. Sections 7--8 prove
> the one-cup full-action and two-handle quotient formerly assigned to E5/E6.
> Sections 9--11 prove the actual-Gompf/DIAGRAM framed bridge, the chosen
> sphere realization and its divided cubic descent formerly assigned to
> E7--E9. Then the
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
| **[E] `cited_external_theorem`** | sourced theorem not reproved here; its hypotheses and exact application remain explicit |
| **[O] `open`** | named candidate-specific mathematical antecedent not yet constructed |

A certificate status never substitutes for a cited **[E]** theorem.

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
\(\Gamma_s\) from its coefficient \(HH_0\) to the unshifted raw summand.  For
every finite cabled state, take the coefficient quantum shadow
\(\mathsf S_s\) supplied by the BPW/BHPW quantum-Hochschild shadow and define

\[
C_s \xrightarrow{\ \Gamma_s^{-1}\ }
HH_0(\mathcal A_s;M_{R_s})
\xrightarrow{\ \mathsf S_s\ }E_s,
\qquad \Theta_s^{\rm raw}:=\mathsf S_s\Gamma_s^{-1}.
\tag{1.2}
\]

Here \(\mathsf S_s\) is an actual map, not an assumed Morita equivalence.
Let \(\mathcal A_s\) be the product of the gate tangle categories and let
\(M_{R_s}\) be MWW's coefficient bimodule.  The balanced cut boundary makes
\(R_s\) an endo-1-morphism \(F_{R_s}\), and pivotal closure gives, for all
objects \(T,T'\), the natural component identification

\[
\chi_{T,T'}:
M_{R_s}(T,T')
=\operatorname{Kh}_2(R_s\cup T'\cup\overline T)
\xrightarrow{\cong}
2\operatorname{Hom}(T,F_{R_s}T'),
\tag{1.2a}
\]

with the displayed MWW grading shift.  Under \(\chi\), the two MWW gluing
actions are respectively \(F_{R_s}(f)\circ m\) and \(m\circ f\).  Thus a
diagonal element \(m\in M_{R_s}(T,T)\) is a vertical-trace component, and the
universal vertical-to-horizontal trace kills exactly the coefficient
relations \(F_{R_s}(f)m-mf\).  This constructs \(\mathsf S_s\) on the full
coefficient \(HH_0\), without requiring cup diagrams to generate all tangle
objects or requiring \(\mathsf S_s\) to be injective.  For crossing tangles,
use the strict Khovanov complex and the induced Lefschetz preshadow in the
homotopy category.  The construction is first made in the quantum trace and
then specialized/completed at \(q=1+h\); ordinary \(HH_0\) is not silently
identified with the quantum trace.

The component formula and its action compatibility are the closure definition
of the Chen--Khovanov tangle bimodule
(BPW `homology/chen-khovanov.tex:53-92,290-303`) applied to MWW's
three-ball category and gluing bimodule
(`1handles.tex:240-299`).  No additive-generation assertion is used.

The arrows in (1.2) include the one-handle and displayed cabled grading
normalizations; Section 5 writes them numerically at \(s_0\).  BPW's
vertical-to-horizontal natural functor (shadows/vertical.tex:26-58),
functoriality of the horizontal trace (shadows/functoriality.tex:170-206),
its quantum universal form (shadows/graded.tex:101-110), and the definition
of the annular functor as
\(qHH_0\circ qhTr(F_{\rm CK})\)
(quantum/qannulus.tex:195-210) make the coefficient shadow functorial for
arbitrary horizontal-trace morphisms, including split and dotted surface
maps.  BHPW supplies strict functoriality for the underlying ordinary tangle
cobordisms (equivalence.tex:468-487).

Apply this composite to every cut component used in \(\Gamma_s\).  MWW's
one-handle cobordism construction (1handles.tex:320-413) proves that after
projection to the colimit the result is independent of the chosen cuts and
annihilates the source colimit relations.  Consequently, for every ordinary
state-changing surface map
\(\Psi_e:C_s\to C_t\), the whole-source square

\[
\Theta_t^{\rm raw}\Psi_e=F_e^{\rm end}\Theta_s^{\rm raw},
\tag{1.3}
\]

where \(F_e^{\rm end}\) is the induced endpoint-shadow map.  Equation (1.3)
does not assert that \(\Theta_s\) is injective or that an endpoint calculation
by itself proves a relation in \(C_s\); it supplies only the naturality needed
to pull an endpoint row back to the actual MWW source.  Below the superscript
is suppressed.  The final presentation still starts from
\(\bigoplus_s C_s\), not from endpoint spaces.

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

Consequently **[P]**, using the established ordinary-surface functorialities
listed in Section 5, the actual cut supplies
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
constructs its selected raw-state binding E3. No conjectural functoriality for
knotted webs or singular foams embedded in four-space is used.
The complete cokernel and lift-independence ledger is colocated as
`T73_EVIDENCE_QTRACE_SOURCE_LEDGER.md`.

<a id="strict-functoriality"></a>
## 5. Ordinary-surface functoriality and grading ledger

Every geometric consumer in this proof is an ordinary framed oriented surface
cobordism between tangles or links:

| consumer | object type | source |
|---|---|---|
| Section 2 annulus isotopy and action squares | tangle isotopy cylinders and annular surfaces | BHPW `equivalence.tex:468-487`; MWW `1handles.tex:173-232` |
| Section 4 trace/Chern square | algebraic vertical-to-horizontal trace and annular link cobordism | BPW `shadows/vertical.tex:11-58`, `traces/graded.tex:90-108`, `quantum/qannulus.tex:289-309`; BHPW `intro.tex:378-421` |
| Section 8 beta, psi and core maps | braid cylinders, ribbon bands and ordinary core disks | MWW `kirby.tex:118-173,265-283,349-378` |
| Sections 9--11 sphere maps | ordinary surfaces and two-handle core disks | MWW `kirby.tex:607-699` |

BHPW's theorem at `equivalence.tex:468-472` supplies strict functoriality for
the required tangle cobordisms. The conjectural extension at
`equivalence.tex:489-493` concerns knotted-web inputs and singular foams in
four-space; neither occurs here. Former premise E4 is therefore discharged by
the published ordinary/annular functorialities **[E]**.

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
and (5.3) give **[P]**, under the ordinary-surface functorialities just listed,

\[
\Theta_{s_0}^{\rm raw}(\widetilde v_{s_0})=u_h,
\qquad u_h\bmod h=u=e_0-e_5.
\tag{5.5}
\]

The coefficient class, one-handle class, shifted raw-state representative,
and final quotient class remain distinct objects. Equation (5.5) does not
claim that the raw shadow has descended through beta/psi; Sections 7--8 prove
that divided descent.
The exact state and degree binding is colocated as
`T73_EVIDENCE_RAW_STATE_BINDING.md`.

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

and see the colocated
`T73_EVIDENCE_ETA_T1_DELTA3.md#2-exact-raw-word-calculation`.
The input is \([v_T]_{\mathrm{coeff}}\), not
\(\xi=\eta_R[T_0]-s_{\rm inv}\eta_R[T_1]\). The latter already contains one
\((\rho(W)-I)\); the same detector introduces its square, whose first nonzero
\(\varepsilon\)-term has degree six, so \(\delta_3(\xi)=0\) **[F2]**.

<a id="relative-nu-ledger"></a>
## 7. One-cup cell quotient

The selected class is the one-cup class

\[
[v_T]=\eta_R[T_1],\qquad
\Theta_{s_0}(\widetilde v_{s_0})=u+O(h),\qquad
u=e_0-e_5\in S^{(87,1)}.
\tag{7.1}
\]

The old mixed two-cup \(S^{(86,2)}\) route is retired: the full
\(S_{44}^-\times S_{44}^+\) one-handle action closes the undotted psi ideal
over its entire through-84 cell. Likewise
\(\xi=\eta_R[T_0]-s_{\rm inv}\eta_R[T_1]\) is not the input to the divided
detector: applying the same outer \((W-I)\) gives
\([h^3]\ell(W-I)^2u=0\). Neither retired object is load-bearing below.

Filter the endpoint BN/Temperley--Lieb category by through degree. Composition
cannot raise this filtration. The physical cup \(U\) has

\[
\operatorname{th}(U)=86.
\tag{7.2}
\]

For each gate-crossing owner, undotted balanced-pair creation has at least two
cups, hence its full action-closed ideal lies in \(F_{84}\). Let \(P_{86}\)
be a rational endpoint projector with image the \(S^{(87,1)}\) top cell and
kernel containing \(F_{84}\). Define

\[
\mathcal D_3(x)=
[h^3]\,\widehat C_{87,2}(h)(\rho_h(W)-I)P_{86}\Theta_h(x).
\tag{7.3}
\]

The selected vector already lies in the top cell, so Section 6 gives

\[
\boxed{\mathcal D_3(\widetilde v_{s_0})=-59072.}
\tag{7.4}
\]

The zero-gate owner \(r_{zx}\) is separate. For \(L=\varnothing\), deleting
the artificial meridian spectator leaves a crossingless zero-framed unknot;
one balanced pair is the split complex \(A\otimes A\), with

\[
(\epsilon\otimes\epsilon)\psi^{[0]}=0,\qquad
(\epsilon\otimes\epsilon)\psi^{[1]}=\operatorname{Id}.
\tag{7.5}
\]

Equations (7.2)--(7.5), the full action-ideal calculation in
D:/tmp/r6/agents/finite_type_leading/TL_CELL_IDEAL_CLOSURE_RESULT.md, and
D:/tmp/rzx_pair/RESULT.md prove the former E5 firewall **[P]**. The projector
is a linear map after the genuine qHH shadow, not a claimed physical foam.

<a id="beta-psi-cocone"></a>
## 8. Two-handle beta/psi divided cocone

The full one-handle left/right action is already quotiented in coefficient
\(HH_0\). At the base two-handle state each active owner has one negative and
one positive physical copy. Its \(B_{(1,1)}\) constant quotient is trivial and
each pure generator acts as \(I+O(h)\). Since the detector begins at \(h^3\),

\[
\mathcal D_3(\beta_i(b)x)=\mathcal D_3(x).
\tag{8.1}
\]

At higher multiplicities, standardize actual physical copies by stable positive
shuffles, attach actual W2 core disks, and take the finite Reynolds average.
Orbit ratios telescope; distinct-owner squares commute by disjoint support.
Pure remainders are invisible to the divided cubic. The local core maps give

\[
(\epsilon\otimes\epsilon)\psi^{[0]}=0,\qquad
(\epsilon\otimes\epsilon)\psi^{[1]}=\operatorname{Id}.
\tag{8.2}
\]

The once-dotted raw degree \(+2\) cancels the cabled shift \(-2\), hence

\[
\Lambda_t^{(3)}\Psi_e^0=0,\qquad
\Lambda_t^{(3)}\Psi_e^1=\Lambda_s^{(3)}
\tag{8.3}
\]

for every finite state. This actual W2 core-evaluation cocone is proved in
`T73_EVIDENCE_ONE_CUP_E5_E6.md` (source SHA
6A63978D734EFF30B8F6C2E6F9800F9338B3499BA1CA4D6AF4880716468FE865,
with the local core factor checked in `T73_EVIDENCE_W2_CORE_FACTOR.md`,
source SHA
73F5D57A2074B133687018D1D8641FF2DA76ED5B01F055B6D89E7F086F10E129).
Sections 7--8 discharge former E5/E6 **[P]**.

<a id="fixed-y-hj-basis"></a>
## 9. Hardened chosen sphere basis

The historical ERKMO spheres remain only declared and are not used. Use the
three hardened chosen surfaces with receipt identities

\[
\begin{array}{ll}
\mathrm{TH1}:&\mathrm{EE620E6B085A5F9E1C73CFDD1AD04FC0682CEC74DA3DBF8AFE70DD19C038E3A0},\\
\mathrm{TH2}:&\mathrm{4D1B627C0343A1C464319704EAFADCA127902A2E4E90CF1C283004359B7ADC24},\\
\mathrm{THXY}:&\mathrm{EABF67C0D1AE309F0281297710A283B8ED5A11D88C8E810837932313F4C53227}.
\end{array}
\tag{9.1}
\]

TH1 has 350176 actual leaves, 350175 continuously chained bands and one root
cap; TH2 has 229198 leaves, 229197 bands and one root cap. Their hardened
runners recompute geometry predicates on every row. THXY has 11115 material
core disks, 11114 actual split bands and one root cap; its final successor
binds the formerly missing negative graft. Thus every chosen surface is
embedded, framed and genus zero **[F]**.

The actual ambient binding is proved in T73_GA1_DESCENDING_BRIDGE.md **[P]**.
Aitchison--Rubinstein's actual mapping-torus construction supplies the complete
bottom/top/base-handle product ribbons and their framings for

\[
m_i=t\,\phi_A(x_i)\,t^{-1}x_i^{-1}.
\tag{9.2b}
\]

Their linear-strip description identifies the top pieces with the exact C11
Christoffel paths \(Ae_i\); the frozen paths avoid the straightening ball.
The global Heegaard-feeding isotopy is carried by an explicit smooth
suspension diffeomorphism of the entire handle presentation. Any pure braid in
its lambda/mu tracks is retained in the resulting whole-boundary
diffeomorphism, not declared trivial. Laudenbach--Poenaru extends that
diffeomorphism over the four-dimensional one-handlebody, transporting the
complete labeled framed link. We may therefore work in the equivalent AR
product representative without fixing the commutator components pointwise.
Two actual product cancellations first delete \(t,t^{-1}\) and then implement
\(x\mapsto z\). They transport the product annuli and give a geometric split
zero-framed disk for \(r_{zx}\).

After the complete y/z disk cut, the actual product-rerouted tangle and the
frozen DIAGRAM have the same marked endpoint/successor data. The actual side
is boundary-parallel by the product-ribbon construction. The DIAGRAM side is
boundary-parallel by the exact global height order

\[
r_{xy}>r_{yz}>m_2>m_3
\tag{9.2a}
\]

so both are isotopic to the same marked trivial tangle. Tubular extension
transports the actual product framing. This is a whole-link,
component-preserving framed Kirby equivalence; it does not claim pointwise
fixing of the commutator components and does not use the emitter's uncertified
numeric blackboard framings.

All three therefore lie in the actual post-two-handle boundary
\(\partial W_2\cong\#_3(S^1\times S^2)\). They occupy disjoint sectors

\[
\mathrm{THXY}\subset[2,13/2],\quad
\mathrm{TH1}\subset[8,9],\quad
\mathrm{TH2}\subset[10,11],
\tag{9.2}
\]

and their actual \(H_2^{\rm sph}(\partial W_2)\) coordinates are

\[
v_1=(-1311,8608,-1),\quad
v_2=(-189,1241,0),\quad
v_3=(41,-269,1),\qquad
\det[v_1\ v_2\ v_3]=1.
\tag{9.3}
\]

Under the external Horvat--Jabłonowski embedded-sphere basis theorem E7
(version_23_RM.tex:644-675,1429-1497), this same-W2 pairwise-disjoint basis may
serve as the 3-handle attaching system up to slides and permutation. Since
\(L=\varnothing\), no external relative-link condition blocks replacement.
The AREA_BASIS arithmetic slide ledger is not used as a historical-sphere
connection. The same-W2 embeddedness is **[F]** and the determinant-one basis
consequence is **[P]**. The replacement implication remains the explicitly cited external
theorem **[E7]**.

<a id="direct-q-sphere-cocone"></a>
## 10. Six chosen-sphere rows

For each chosen sphere \(j\), all noninvertible critical points lie in new
material factors; the old one-cup block travels by identity cylinders.
Do not declare the remaining mixed braid or ambient-isotopy transport to be
the identity.  Write \(E_a^{\rm act}\) for the endpoint-shadow target of
\(\Theta_a:C_a\to E_a^{\rm act}\).  For every material-labelled cabled state
\(a\), fix once and for all the full actual-to-canonical transport
\(\widetilde Q_a(h)\), and denote its constant term by

\[
Q_{a,0}:E_a^{\rm act}\xrightarrow{\cong}E_a^{\rm can}.
\]

induced by the whole-boundary diffeomorphism of Section 9 followed by the
positive-permutation/owner-collar standardization with the frozen labels,
basepoints, total factor order and product framings.  Any nontrivial pure
braid is retained inside \(\widetilde Q_a(h)\); it is not declared trivial.
The two dot choices for one sphere use the same actual surface and hence the
same source and target transports.

Let
\(\Psi^{\rm raw}_{j,n,s}:C_s\to C_{t_j}\), \(n=0,1\), be the raw
state component of the actual MWW map for the zero- and one-dot versions of
sphere \(j\).  The induced maps after the beta/psi quotient will be denoted
\(\bar\Psi_{j,n}:W_1\to W_1\).  For \(b_j\) new factors, the constant
endpoint-shadow maps of the same actual surface are

\[
F_{j,0}^{(0)}=Q_{t_j,0}^{-1}
 (\operatorname{Id}_{old}\otimes U_j)Q_{s,0},\qquad
F_{j,1}^{(0)}=Q_{t_j,0}^{-1}
 (\operatorname{Id}_{old}\otimes D_j)Q_{s,0},
\tag{10.1}
\]

where

\[
D_j=X^{\otimes b_j},\qquad
U_j=\sum_{a=0}^{b_j-1}
X^{\otimes a}\otimes1\otimes X^{\otimes(b_j-1-a)}.
\tag{10.2}
\]

Actual W2 core disks give \(E_j=\epsilon^{\otimes b_j}\), so

\[
E_j(U_j)=0,\qquad E_j(D_j)=1.
\tag{10.3}
\]

The whole-source naturality (1.3), applied to the two actual sphere movies,
is

\[
Q_{t_j,0}\Theta_{t_j}\Psi^{\rm raw}_{j,n,s}
=(\operatorname{Id}_{old}\otimes T_{j,n})Q_{s,0}\Theta_s,
\qquad T_{j,0}=U_j,\quad T_{j,1}=D_j.
\]

This square uses MWW's one-handle cobordism functoriality and three-handle
comparison square together with BPW/BHPW shadow naturality; it is not inferred
from a scalar test.  Let \(r_s\) be the canonical old-factor divided row and
define rows on the actual MWW source summands by

\[
\lambda_s^{(3)}=r_sQ_{s,0}\Theta_s,\qquad
\lambda_{t_j}^{(3)}=(r_s\otimes E_j)Q_{t_j,0}\Theta_{t_j}.
\]

The target row is closure by the same actual W2 core disks appearing in
MWW's comparison square.  Substitution of the naturality square and (10.3)
now gives, on every vector of \(C_s\),

\[
\lambda_{t_j}^{(3)}\Psi^{\rm raw}_{j,0,s}=0,\qquad
\lambda_{t_j}^{(3)}\Psi^{\rm raw}_{j,1,s}=\lambda_s^{(3)}.
\tag{10.4}
\]

Thus (10.4) reduces exactly to (10.3), without treating \(\Theta_s\) as
injective or replacing \(C_s\) by an endpoint module.  This is an
identity of linear maps, not a check on \(v_T\) alone.  The three stored scalar
pairs \(0/0,0/0,0/0\) are only consequences of this whole-source statement.

The same disjoint-product interchange squares with every beta and psi movie
show that the direct-sum raw families preserve \(\mathcal R_{2h}\); hence they
induce the displayed \(\bar\Psi_{j,n}\) on \(W_1\).  The raw row family in
(10.4) is the one already descended in Section 8.  Applying the quotient
universal property therefore gives the actual \(W_1\)-level equations

\[
\boxed{
\ell_1\bar\Psi_{j,0}=0,\qquad
\ell_1(\bar\Psi_{j,1}-\operatorname{Id})=0.}
\tag{10.5}
\]

The arbitrary positive new--new split-tree algebra, including the coordinate
conjugation above, is kernel-checked in `Smooth4PC/T73SplitMovie.lean`; the
actual-movie and MWW identifications remain the geometric/published inputs.
No full-\(q\) sphere matrix is claimed or needed for the divided cubic.

<a id="changing-endpoint-naturality"></a>
## 11. Divided cubic compatibility

In canonical endpoint coordinates the maps in (10.1) act by the identity on the old
factor.  Thus they commute there with the top-cell projector, point-push
operator and selected cap row.  Conjugating back by the fixed statewise
\(\widetilde Q_a(h)\)'s and pulling back through \(\Theta_a\) gives the
corresponding actual-source statement; it does not
discard a mixed or pure braid.  Positive transport corrections start at
\(h^4\) after multiplication by the old \(h^3\) anomaly.

Thus (8.1)--(8.3) and the typed equations (10.4)--(10.5) are exactly the
changing-endpoint identities consumed by the divided functional.  The
standardization \(Q_{a,0}\) is defined independently at each state from the
frozen total factor order, not recursively from a path.  Independent
operations occupy disjoint product charts, their canonical inner maps commute
by interchange, and BHPW strict functoriality transports that interchange to
the actual square.  Hence no edge-local pure-braid holonomy is silently
discarded.  This statement is \(h^3\)-only and does not assert exact
full-series edge conjugacy or that a nontrivial pure braid is the identity.

<a id="mww-quotient"></a>
## 12. Exhaustive MWW quotient and descent

Let \(\mathcal C=\bigoplus_s C_s\) over all finite cable states, and let
\(\mathcal R_{2h},\mathcal R_{3h}\) be the MWW beta/psi and chosen-sphere
relation subspaces. E10 retains only the external completeness and quotient
universal property.

Define \(\Lambda_3:\mathcal C\to\mathbb Q\) by Sections 7--11. Equations
(8.1)--(8.3) prove \(\mathcal R_{2h}\subseteq\ker\Lambda_3\), and (10.5)
proves \(\mathcal R_{3h}\subseteq\ker\Lambda_3\). Hence **[P]**, conditional
only on E10,

\[
\bar\Lambda_3:
\mathcal C/(\mathcal R_{2h}+\mathcal R_{3h})\longrightarrow\mathbb Q,
\qquad \Lambda_3=\bar\Lambda_3\pi.
\tag{12.1}
\]

At the selected state,

\[
\boxed{\bar\Lambda_3(\pi(\widetilde v_{s_0}))=-59072\ne0.}
\tag{12.2}
\]

Thus the selected class survives all one-, two- and chosen three-handle
relations. Its absolute degree is

\[
-44+227+315-4=494.
\tag{12.3}
\]

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
**[P]**, using G1 and under **E7, E10--E12**, that

\[
X(41,189,73)\not\cong_{\rm diff}S^4.
\tag{14.2}
\]

Separately, **[E13]** is the Cappell--Shaneson theorem that the finite-verified
conditions \(\det A=\det(A-I)=1\) for the pinned matrix imply that
\(X(41,189,73)\) is a homotopy sphere. With **E13**, (14.2) is a conditional
SPC4 counterexample. A modern exact restatement is Proposition 2.1 at
`D:/tmp/r6/QSC/kpr/cs_2404.05096.txt:128-151`; the determinant arithmetic is
checked in `AuditArithmetic.lean`.

## 15. Dependency and source/evidence table

| ID | status | role | retained boundary |
|---|---|---|---|
| E1 balanced Hattori | **[P]** | Sections 2--3 | hidden braid/framing retained |
| E2 diagonal binding | **[P]** | Section 3 | input is \(v_T\), not \(\xi\) |
| E3 selected raw binding | **[P]** | Section 5 | closed at raw-state level |
| E4 ordinary functoriality | **[E]** | Section 5 published type-by-type results | conjectural four-space foam extension not used |
| F1 grading | **[F]** | Section 5 | exact degree 494 |
| F2 cubic | **[F]** | Section 6 | exact value -59072 |
| E5 one-cup cell firewall | **[P]** | Section 7 | mixed-Z route retired |
| E6 beta/psi cocone | **[P]** | Section 8 | divided \(h^3\) only |
| G1 actual-Gompf/DIAGRAM framed lift | **[O]** | Section 9 and T73_GA1_DESCENDING_BRIDGE.md | candidate argument; builder, full PD and framing/move witnesses are not public |
| E7 chosen HJ replacement | **OPEN** | HJ Theorem 5.3 is available, but its boundary, handle-count, irreducibility and spherical-basis hypotheses are not publicly instantiated | TH1/TH2/THXY objects are not published |
| E8 six sphere rows | **[O]** | Section 10 | divided \(h^3\) claim; candidate-specific sphere witnesses are not public |
| E9 edge naturality | **not independently required** | Section 11 | no full-\(q\) claim |
| E10 complete MWW quotient | **OPEN** | MWW Theorems 3.2 and 3.10 give the general presentation | `q01` and `q12` are not identified with the candidate-specific MWW maps |
| E11 graded four-handle | **PARTIAL** | MWW Proposition 3.4 gives the general four-handle isomorphism | the repository does not identify `G`, its rational \(N=2\) grading, and `fourIso` with that theorem in degree 494 |
| E12 rational \(S^4\) control | **PARTIAL** | MWW Corollary 3.5 gives \(\mathcal S^N_0(S^4)\cong\mathbb Z\), concentrated in bidegree zero | the abstract `G` is not identified with the rational \(N=2\) lasagna module |
| E13 CS bridge | **PARTIAL** | Iwaki Proposition 2.1 and the finite determinant checks apply to \(\Sigma_A^\varepsilon\) | identification of the frozen detector presentation with that \(\Sigma_A^\varepsilon\) depends on G1/P0 |

All thirteen manifest consumer anchors remain present. The manifest role labels
are a frozen allocation; this text records the newer discharge status without
editing that separate contract.

## 16. Honest closing status

This document records candidate arguments for the one-cup firewall, the
two-handle divided cocone, the actual-Gompf/DIAGRAM framed bridge, the chosen
HJ basis, and the six sphere equations at order \(h^3\).  The public tree does
not contain the geometric inputs needed to independently instantiate those
arguments, and it does not contain a comparison theorem identifying the
truncated Burau cubic with an MWW skein-lasagna evaluation.
Mixed \(Z\), relative \(\xi\), raw \(\nu\), vertex-potential and
unrestricted E9 routes are retired.

The remaining open premises include G1, the Burau--MWW comparison, E7--E10,
and the candidate-specific identifications required by E11--E13.
Therefore the status remains

CANDIDATE_PROOF_PENDING_INDEPENDENT_REVIEW

This is not a formally verified or externally accepted disproof. Under the
enumerated premises, Sections 12--14 give a nonzero degree-494 class and the
conditional conclusion. Independent review remains required.
