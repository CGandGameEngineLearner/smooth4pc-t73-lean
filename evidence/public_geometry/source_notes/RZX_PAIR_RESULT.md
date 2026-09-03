# The `r_zx` paired-cable exception

Date: 2026-09-01  
Scope: the two-crossing local PD at the end of the actual reduced diagram, one
negative/positive `r_zx` pair, its BN coefficient factor, and the MWW
`psi^[0]/psi^[1]` core evaluation.

## Verdict

```text
arcs 4252577/4252578 belong to:                 mu(r_zx)
two displayed crossings:                       negative Hopf meridian clasp
RII cancellable:                               NO
local linking number lk(r_zx,mu):              -1
mu(r_zx) part of scientific L=empty input:      NO (spectator marker)
r_zx after dropping spectator:                 crossingless 0-framed unknot
one +/- pair with L empty:                      split U^2
closed coefficient factor:                     A tensor A
psi0 followed by two core counits:              0
psi1 followed by two core counits:              1
R_ZX cut/split movie for actual L empty:        CONSTRUCTED
if mu is retained as a real boundary component: BLOCKED BY LINKING
```

Thus the unique zero-gate owner does not obstruct the actual scientific
`L=empty` cabled family.  It would obstruct the stronger claim for arbitrary
linked boundary `L`.

## 1. Identification of the two crossings

The last two PD entries are

```text
[7332,    4252577, 7331,    4252578]
[4252578, 7331,    4252577, 7332   ].
```

The component order in the delivery is

```text
gate_y, gate_z, r_xy, r_yz, r_zx, m2, m3,
mu(r_xy), mu(r_yz), mu(r_zx), mu(m2), mu(m3).
```

Arc labels are assigned component-by-component.  The frozen ranges are

```text
r_zx:      7331--7332
mu(r_xy):  4252573--4252574
mu(r_yz):  4252575--4252576
mu(r_zx):  4252577--4252578.
```

Hence both crossings are exactly between `r_zx` and `mu(r_zx)`.

An independent `spherogram.Link` calculation on these two PD entries gives

```text
components = 2
crossings  = 2
linking matrix = [[0,-1],[-1,0]]
writhe = -2
crossings after basic simplification = 2
```

The linking matrix agrees with
`t73_measurements.json` for both the collected and billiard realizations.
Since the signed crossing sum between the two components is `-2`, both
crossings are negative.  An RII pair has opposite signs and linking zero.
Therefore these crossings are not an RII artifact: they form the standard
negative Hopf meridian clasp.

Reproduction:

```python
import json, spherogram
j=json.load(open(r"D:\tmp\s4pc_ruler\DIAGRAM\out\t73_reduced_billiard.pd.json"))
L=spherogram.Link(j["pd"][-2:])
print(L.linking_matrix(), L.writhe())
L.simplify("basic")
print(len(L.crossings))
```

## 2. Is the meridian part of the coefficient input?

No, for the scientific target under audit.  In the delivered component ledger
`mu(r_zx)` has role `spectator`, while `r_zx` has role `2-handle`.  The diagram
builder's boundary check drops all components with role `spectator` by default
(`words_to_pd.py:678-712`).  These meridians were inserted to certify the
attaching curves/framing; they are not the MWW boundary link `L` when `L` is
empty.

This distinction matters.  Removing the spectator deletes both local
crossings.  The remaining `r_zx` component has:

```text
one-handle word length = 0;
self crossings = 0;
framing diagonal = 0.
```

The framing value is the `r_zx` diagonal of the reduced linking matrix in
`t73_measurements.json`.  Thus the scientific `r_zx` attaching component is a
crossingless zero-framed unknot in the 0-handle.

## 3. The actual closed coefficient factor

Take the product tubular neighborhood

\[
\nu(r_{zx})\cong S^1\times D^2
\]

with its zero framing.  Choose one negative and one positive longitude at two
nearby disk points.  Since the core is a zero-framed unknot, the two longitudes
form the zero-linked two-component unlink.  An explicit split movie is:

1. isotope the crossingless core to the standard planar circle;
2. identify its product framing with the planar zero framing;
3. move the positive and negative parallels to two standard disjoint planar
   circles using the product annulus, pushing the spanning disks to opposite
   normal levels;
4. keep the move fixed outside `nu(r_zx)`.

The result is the ordered oriented unlink

\[
U_-\sqcup U_+.
\tag{3.1}
\]

There is no open tangle factor for this owner.  Equivalently set
`B_rzx=Id` and `c_rzx=2`.  For every pre-existing coefficient/tangle object
`Y`, disjoint union and the BN monoidal functor give

\[
\boxed{
Kh(Y\sqcup U_-\sqcup U_+)
\cong Kh(Y)\otimes\mathcal A_-\otimes\mathcal A_+.}
\tag{3.2}

Here

\[
\mathcal A=\mathbb Q[X]/(X^2),
\quad
\deg_q(1)=1,
\quad
\deg_q(X)=-1
\]

up to the frozen global shift convention.  The local BN complex is concentrated
in homological degree zero:

\[
C_{BN}(U_-\sqcup U_+)=\mathcal A\otimes\mathcal A,
\qquad d=0.
\tag{3.3}

This is the required closed coefficient factor.  It is not inferred from
`wordlength=0`; it uses the separately checked facts “unknot, no self
crossings, framing zero” after removing a component that is explicitly marked
spectator.

For `r_zx` multiplicity `r`, choose nested product radii.  Every pair supplies
another disjoint `U^2`, so this owner contributes

\[
c_{rzx}(r)=2r_{rzx}.
\tag{3.4}

The split movie is fixed away from its tubular neighborhood and therefore is
two-sided action compatible with all pre-existing coefficient gluing maps.

## 4. The actual psi and core maps

MWW's `psi_rzx^[d]` adds one negative/positive parallel pair by the local
ribbon, with `d=0,1` dots.  Under (3.2), its BN map on the new factor is the
Frobenius coevaluation

\[
\begin{aligned}
\psi^{[0]}(1)&=1\otimes X+X\otimes1,\\
\psi^{[1]}(1)&=X\otimes X.
\end{aligned}
\tag{4.1}

After the `r_zx` two-handle is attached, MWW's `Phi` joins one individual core
disk to each new cable component.  On (3.3) these are the two counits

\[
\epsilon\otimes\epsilon,
\qquad
\epsilon(1)=0,
\quad
\epsilon(X)=1.
\tag{4.2}

Therefore, exactly—not merely on `K_0`—

\[
\boxed{
(\epsilon\otimes\epsilon)\psi^{[0]}(1)=0,
\qquad
(\epsilon\otimes\epsilon)\psi^{[1]}(1)=1.}
\tag{4.3}

These are the MWW `psi0=0`, `psi1=identity` relations.  The raw degrees are
`(0,0)` and `(0,2)`; adding one balanced pair changes the cabled shift by
`(0,-2)`, so the normalized degrees are `(0,-2)` and `(0,0)` respectively.

For arbitrary old `Y`, (4.1)--(4.3) tensor with `Id_Y`.  Hence they are actual
BN chain maps on the full coefficient, not scalar checks on a selected vector.

This supplies

```text
R_ZX_CLOSED_PAIR_RELATIVE_CUT_OR_SPLIT_MOVIE
```

for the actual `L=empty` problem and closes the missing `r_zx` psi direction.

## 5. What happens if the meridian is retained

If one changes the problem and includes `mu(r_zx)` as a genuine component of
`L`, the conclusion changes.  The two original crossings are a negative Hopf
clasp and cannot be removed.  Two `r_zx` parallels then give the three-component
negative keychain link: each outer component has linking number `-1` with the
same meridian and the two outer components have mutual linking zero.

Its BN complex has four negative crossings and may be written as the tensor
product over the shared meridian Frobenius object

\[
C_{BN}(H_-^{(1)})\otimes_{\mathcal A_{\mu}}
C_{BN}(H_-^{(2)}),
\tag{5.1}

equivalently as its 16-vertex cube of resolutions.  It is **not**

\[
C_{BN}(\mu)\otimes\mathcal A\otimes\mathcal A,
\]

because either factorization would force both linking numbers with `mu` to be
zero.  Thus the linked spectator blocks a split Hattori factor if it is promoted
to genuine boundary data.

The local `psi` ribbon and the two W2 core disks still exist, but before core
attachment they live in the non-split complex (5.1); one cannot pull out an
independent `A tensor A` coefficient factor.

This does not affect the current scientific target because the meridian is a
delivery-side spectator and `L=empty`.

## 6. Consequence for the all-balanced theorem

Combining this result with the product-gate theorem for `rxy,r_yz,m2,m3`
removes the only owner exception for the actual empty-boundary CS cabled
module.  The contributions are:

```text
gate-crossing owners: rectangle-cell Hattori factors;
r_zx:                closed split U^(2 r_zx) factor.
```

Therefore the all-balanced Hattori family now covers every finite
`r in N^5` **for `L=empty`**.  It does not extend unchanged to arbitrary
boundary links that link an attaching component; the meridian keychain is the
explicit counterexample to that broader wording.

## Sources

- Actual PD:
  `D:/tmp/s4pc_ruler/DIAGRAM/out/t73_reduced_billiard.pd.json`, last two entries.
- Component roles, framings and linking matrix:
  `D:/tmp/s4pc_ruler/DIAGRAM/out/t73_measurements.json`.
- Arc emission and spectator-removal rule:
  `D:/tmp/s4pc_ruler/DIAGRAM/words_to_pd.py:444-507,678-712`.
- MWW cable/psi definitions and core disks:
  `D:/tmp/r6/mww_handle_src/kirby.tex:240-283,359-369`.
