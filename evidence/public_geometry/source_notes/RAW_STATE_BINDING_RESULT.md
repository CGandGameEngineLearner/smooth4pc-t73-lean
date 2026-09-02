# Actual raw-state / core-attachment binding

## Verdict

```text
actual state s0=(alpha=0,r=e_m2+e_rxy):       CONSTRUCTED
named raw representative tilde(v)_s0:         CONSTRUCTED
not obtained from Phi surjectivity:           YES
core-attachment movie:                        EXPLICIT MWW CORE DISKS
Theta_s0(tilde(v))=u_h, u_h mod h=e0-e5:      PROVED
raw degree 498 -> cabled degree 494:           PROVED
remaining E3 premise:                         NONE (strict foam scope remains E4)
```

## 1. Exact raw summand

Use owner order `(m2,m3,rxy,ryz,rzx)` and

\[
\alpha=0,
\qquad
r=e_{m2}+e_{rxy}=(1,0,1,0,0).
\]

Then

\[
k^-=r-\alpha^-=r,
\qquad
k^+=r+\alpha^+=r.
\]

Thus the raw boundary link in `partial W1` is exactly one negative and one
positive framed physical copy of `m2`, and one negative and one positive copy
of `rxy`.  It is the actual link whose gate cut was checked directly in
`D:/tmp/t73_actual_cable_unit/ACTUAL_PD_CABLE_UNIT_CERT.json`.

For `N=2`, MWW's raw state summand is

\[
C_{s0}=
\mathcal S^2_0
\left(W_1;K(r,r),\eta^r;\mathbb Q\right)\{-4\},
\tag{1}
\]

because `(1-N)(2|r|+|alpha|)=-4`.  In the one-handlebody `W1`, `H_2(W1)=0`;
the oppositely oriented cables are nullhomologous and MWW's class `eta^r` is
the unique relative class specified at `kirby.tex:320-329` (compare the
one-handlebody specialization at `kirby.tex:392-400`).

## 2. Named element before the cabled quotient

Cut `K(r,r)` along the y/z belt spheres.  In the summand with standard z
wickets and seam

\[
T_1=B_{act}^{-1}U_{(0,5)},
\]

the actual balanced Hattori equivalence gives the explicit homology element

\[
v_T=H_{T_1,T_1}^{-1}
\left(Id_U\otimes X^{\otimes227}\right)
\in
KhR_2\left(R\cup T_1\cup\overline{T_1};\mathbb Q\right).
\tag{2}
\]

Let `Glue_1h` be the concrete gluing map in the proof of MWW's one-handle
theorem: it reseals the two copies of each inserted tangle through the
one-handles.  MWW defines this map before proving it is an isomorphism
(`1handles.tex:250-276`); it is not a choice of a preimage under a surjection.
Define

\[
\boxed{
\widetilde v_{s0}:=
Glue_{1h}\bigl(T_1,v_T\bigr)\{-4\}
\in C_{s0}.}
\tag{3}
\]

Formula (3) is the required named raw representative.  A lasagna description
is literal: use the B4 filling representing (2), with the identity on the
open cup factor and 227 separately labelled `X` circle factors, and glue its
y/z boundary balls through the corresponding one-handles.  No cabled
relation has yet been imposed.

## 3. Core attachment

Let `iota_s0:C_s0 -> C_cabled` be the summand inclusion followed by the
cabled quotient.  MWW's map

\[
\Phi:\mathcal C_{cabled}\xrightarrow{\cong}
\mathcal S^2_0(W_2;\varnothing,(0,0))
\]

is defined on this representative by attaching precisely four disks:

```text
negative rxy cable -> negative parallel of the rxy 2-handle core;
positive rxy cable -> positive parallel of that core;
negative m2 cable  -> negative parallel of the m2 core;
positive m2 cable  -> positive parallel of that core.
```

This is MWW's definition, not an existence argument
(`kirby.tex:359-369`).  The disks use the actual owner framings and are
pairwise disjoint in the two distinct 2-handles.  The input balls and labels
of (3) are unchanged.

## 4. Commuting shadow movie

Apply the actual Hattori movie before gluing.  Since
`B_act T1=U`, it changes the labelled cut filling to

\[
Id_U\otimes X^{\otimes227}.
\]

The 227 z-z connector disks are disjoint from the four W2 core disks.  Hence
attaching the W2 cores, performing the Hattori rectangle isotopy, and capping
the z-only circles commute by disjoint-support interchange.  The relative
movie is fixed on the insertion disks, so this statement also commutes with
`Glue_1h`.  Strict BHPW functoriality fixes the single movie sign.

The BPW vertical-to-horizontal trace sends `Id_U` to the actual cup map, and
each z-only cap applies `epsilon(X)=1`.  Consequently

\[
\Theta_{s0}(\widetilde v_{s0})
=Sh_{s0}\Phi\iota_{s0}(\widetilde v_{s0})
=u_h,
\qquad
u_h\bmod h=e_0-e_5\in Q(88,86)=M_1(88).
\tag{4}
\]

This is equality for the named filling (3), not a claim that `Phi` is
surjective and therefore has some suitable preimage.

## 5. Degree ledger

The factors of (2) have the following absolute/raw degrees:

```text
Id_U in the Hom object:                    0
remove Hom's built-in p_y=44 shift:      -44
227 separate X labels:                  +227
raw closure degree:                       183
one-handle theorem shift p_y+p_z:        +315 = 44+271
class in Sz(W1;K(r,r)):                   498
raw cabled summand shift for |r|=2:        -4
tilde(v)_s0 in C_s0:                      494
```

MWW's `Phi` is grading preserving with the displayed cabled shift built into
its domain.  Therefore the core-attached class remains in absolute quantum
degree 494.  Equation (4) writes only its normalized endpoint vector; it does
not reset the absolute lasagna grading to zero.

## 6. Sources and boundary

- raw state/cabled relation: `D:/tmp/r6/mww_handle_src/kirby.tex:320-357`;
- literal core-disk definition of `Phi`: `kirby.tex:359-378`;
- one-handle gluing representative: `D:/tmp/r6/mww_handle_src/1handles.tex:242-293`;
- vertical-horizontal trace: `D:/tmp/r6/bpw_src/shadows/vertical.tex:11-58`;
- exact degree evidence:
  `D:/tmp/r6/agents/finite_type_leading/ORDINARY_SHADOW_HATTORI_CHAIN_RESULT.md:100-115`
  and `D:/tmp/r6/grading_attack/ledger/Q494_SPHERE_GRADING_LEDGER.md:45-60`.

The construction closes E3.  It still uses the globally stated strict foam
functoriality E4 for equality of the two composite movies; no additional raw
state or core-attachment premise remains.
