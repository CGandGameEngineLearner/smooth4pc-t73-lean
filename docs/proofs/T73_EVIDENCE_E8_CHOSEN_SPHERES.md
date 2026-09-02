# E8-A: actual chosen three-sphere geometry and the six leading maps

Date: 2026-09-01
Time-order rule: the hardened 12:10--12:48 chosen-sphere artifacts supersede
the earlier 02:02 `OPEN` inventory.

## Verdict

```text
historical t73 spheres recovered:                    NO / not needed
chosen TH1 embedded framed sphere:                   PASS
chosen TH2 embedded framed sphere:                   PASS
chosen THXY embedded framed sphere:                  PASS
all three in one W2, pairwise disjoint:              PASS
chosen class matrix determinant:                     +1
HJ replacement of historical attaching system:      PASS for L=empty
six constant h0 maps bound to those surfaces:        PASS
three divided-v_T sphere scalar pairs:               0/0, 0/0, 0/0
E8 sphere descent at h3:                             CLOSED
full q-series sphere maps:                           NOT CLAIMED
```

The early inventory was correct when written but is no longer current.  The
historical ERKMO rows remain merely `DECLARED`; later artifacts instead build
three new chosen embedded spheres.  This is legitimate because the chosen
classes form a unimodular basis in the same post-two-handle boundary.

## 1. Frozen identities and independent replay

The load-bearing geometry identities are:

```text
EE620E6B085A5F9E1C73CFDD1AD04FC0682CEC74DA3DBF8AFE70DD19C038E3A0
  evidence/public_geometry/TH1_EXHAUSTIVE_ALL_ROW_GEOMETRY.json

4D1B627C0343A1C464319704EAFADCA127902A2E4E90CF1C283004359B7ADC24
  evidence/public_geometry/TH2_EXHAUSTIVE_ALL_ROW_GEOMETRY.json

EABF67C0D1AE309F0281297710A283B8ED5A11D88C8E810837932313F4C53227
  evidence/public_geometry/THXY_FULL_MACRO_P3FREE_HJ_CERT.json
```

All three hashes were recomputed and match.  I also reran:

```text
test_exhaustive_geometry_runner.py: 9/9 PASS
test_thxy_full_macro_successor.py:  PASS
global_falsification_chain_audit.py:
  ONE_HANDLE_H3=-59072
  SPHERE_SCALARS=0,0;0,0;0,0
  SPHERE_DET=1
  VERIFY=PASS
```

The global checker is corroboration, not the proof; the geometric reasons are
spelled out below.

## 2. TH1 actual chosen sphere

The hardened producer consumes:

```text
350176 actual owner leaves/finger annuli;
350175 pair-of-pants bands;
one root cap.
```

Every band consumes the unique geometry output of its predecessor.  The full
run independently recomputes route self-intersections, mutual projection
crossings and old-link crossings rather than trusting stored `PASS` fields.
The exact totals are:

```text
band self intersections:       0
band mutual projection hits:   1, separated by microheights 2/8 and 6/8
band old-link crossings:       0
finger self intersections:     0
finger old projection hits:    491777890, all separated in 3D
```

The finger tracks use exact heights `3/16,8/16,13/16`; distinct leaves use
disjoint slabs and injective owner-D2 indices.  The root cap consumes the last
geometry, SLP and terminal hashes, and the complete 657041664-letter boundary
stream freely reduces to empty.  Its Euler ledger is

\[
350176-350175+1=2.
\]

Thus this is an embedded genus-zero chosen sphere, not a counted proposal.
The dot is fixed on its new root disk and the normal degree is zero.

## 3. TH2 actual chosen sphere

The corresponding data are:

```text
229198 actual owner leaves/finger annuli;
229197 bands;
one root cap.
```

Independent totals are:

```text
band self intersections:       0
band mutual projection hits:   1, strictly height-separated
band old-link crossings:       0
finger self intersections:     0
finger old projection hits:    312186510, all separated in 3D
```

All 229197 band rows were visited.  The material-output stream is continuous,
the root cap consumes the last output, and the 406243364-letter stream reduces
to empty by nested LIFO bigons.  Again

\[
229198-229197+1=2,
\]

so the chosen surface is an embedded framed sphere.  Nine hostile mutations,
including bow ties, equal-height collisions, broken ancestry and dual output
hashes, are rejected.

## 4. THXY actual chosen sphere

The final `EABF...` successor closes the negative graft that was missing from
the earlier inventory.  It contains:

```text
313 actual owner/corridor leaves and embedded connectors;
312 full-coordinate macro bands;
5401 positive + 5401 true-inverse corridor split bands;
12247 nested root-reduction bigons;
one root cap consuming macro output 312.
```

The formerly missing negative route now binds two actual parameterized
subarcs by an explicit PL connector in a private movie sector.  All 11114
noninvertible events have `NEW_NEW` feet.  The final cap has normal framing
zero and no intersection with the old one-cup block.  Its Euler ledger is

\[
11115-11114+1=2.
\]

Therefore THXY is also a complete chosen embedded sphere.  The old
`OPEN_NEGATIVE_GRAFT...` field belongs to a retired parent identity, not the
final EABF object.

## 5. Same-W2 system and HJ replacement

The chosen spheres occupy the disjoint sectors

```text
THXY [2,13/2]
TH1  [8,9]
TH2  [10,11]
```

while the old one-cup/core block lies in `[-4,-3]`.  Their owner-D2 registry
has zero collisions.  Hence they are pairwise disjoint in one actual `W2`,
not three separately realizable surfaces.

Their homology columns are

\[
v_1=(-1311,8608,-1),\quad
v_2=(-189,1241,0),\quad
v_3=(41,-269,1),
\]

and direct recomputation gives

\[
\det[v_1\ v_2\ v_3]=1.
\]

Horvat--Jabłonowski's basis theorem applies: in the post-two-handle boundary
`#3(S1 x S2)`, a pairwise-disjoint embedded sphere system whose classes form a
basis may serve as the 3-handle attaching system up to slides/permutation.
Because the present route has `L=empty`, no fixed-near-external-link
qualification blocks this replacement.

Thus historical `located_data` is unnecessary.  The claim is about the new
chosen HJ basis only.

## 6. The six maps on the current v_T row

This section deliberately uses the current final class

\[
v_T=\eta_R[T_1],
\qquad
\mathcal D_3(v_T)=-59072,
\]

not the retired statement that the same outer detector evaluates `xi`.

For every chosen sphere `j`, all noninvertible critical points lie wholly in
the new material factors.  The old `P86/P88` one-cup block travels by identity
cylinders.  Invertible mixed transports have constant endpoint map `I`; their
positive correction is `O(h)` and therefore changes an incoming `O(h^3)` row
only at `h^4`.

Consequently the two constant maps of the actual chosen surface are

\[
F_{j,0}^{(0)}=Id_{old}\otimes U_j,
\qquad
F_{j,1}^{(0)}=Id_{old}\otimes D_j,
\tag{6.1}
\]

where, with `b_j` new material factors,

\[
D_j=X^{\otimes b_j},
\qquad
U_j=\sum_{a=0}^{b_j-1}
X^{\otimes a}\otimes1\otimes X^{\otimes(b_j-1-a)}.
\tag{6.2}
\]

The actual W2 core disks supply the row

\[
E_j=\epsilon^{\otimes b_j},
\qquad \epsilon(1)=0,\quad\epsilon(X)=1.
\]

Therefore, for each of TH1, TH2 and THXY,

\[
E_j(U_j)=0,
\qquad
E_j(D_j)=1.
\tag{6.3}
\]

Equations (6.1)--(6.3) are tied to the same complete chosen surfaces whose
geometry was audited above.  They give the six capped leading maps

\[
\boxed{
\Lambda_3\Sigma_j(0)=0,
\qquad
\Lambda_3(\Sigma_j(1)-Id)=0.}
\tag{6.4}
\]

The stored scalar pairs are correspondingly

```text
TH1:  0 / 0
TH2:  0 / 0
THXY: 0 / 0
```

Since the selected old row starts at `h^3`, only the constant sphere maps in
(6.1) contribute to its divided coefficient.  Full-q matrices are not needed
for this h3 conclusion.

The rational top-cell projector used to isolate the one-cup `through=86`
signal acts only on the old factor.  Since every sphere map in (6.1) is
identity on that factor, it commutes with the six leading maps; no mixed-Z
degree or old `xi` assumption enters.

## 7. Recurrence audit

The old defects do not recur in the hardened identities:

- **dual-output ancestry:** removed; every band has one consumed output;
- **sample-only geometry:** replaced by exhaustive row execution plus a
  universal coordinate lemma and independent route predicates;
- **THXY unbound graft:** present in the final PL connector;
- **root cap detached from comb:** root consumes last geometry/SLP/terminal
  hashes;
- **historical-sphere substitution:** explicitly avoided; HJ chosen basis is
  invoked only after same-W2 embeddedness and determinant one;
- **old-class/input confusion:** scalar equations are restated for `v_T`'s
  divided row, not inferred from `D3(xi)`.

One stale field remains in the raw TH1/TH2 receipts:
`OPEN_EXPERIMENTAL_GEOMETRY_NOT_HOSTILE_AUDITED`.  It predates the later
hardened hostile replay and is not evidence against the completed geometry;
the later review recomputes the predicates and pins the same receipt hashes.
It should be treated as stale metadata, not silently quoted as the final
status.

## 8. Boundary

The conclusion is exact at the registered divided cubic order:

```text
E8 chosen-sphere geometry: PASS
E8 six h3 row equations:  PASS
historical spheres:       still not recovered
full q-series maps:       not computed
```

No remaining E8 geometry hole was found in the hardened chosen basis.  This
report does not independently re-audit the earlier one-/two-handle quotient or
issue an SPC4 verdict; it closes the sphere layer for that supplied `v_T`
divided functional.

## Sources

- TH1 hardened geometry and hostile replay:
  [`TH1_EXHAUSTIVE_ALL_ROW_GEOMETRY.json`](../../evidence/public_geometry/TH1_EXHAUSTIVE_ALL_ROW_GEOMETRY.json);
  [`TH1_HARDENED_REAUDIT.md`](../../evidence/public_geometry/reviews/TH1_HARDENED_REAUDIT.md).
- TH2 hardened geometry and hostile replay:
  [`TH2_EXHAUSTIVE_ALL_ROW_GEOMETRY.json`](../../evidence/public_geometry/TH2_EXHAUSTIVE_ALL_ROW_GEOMETRY.json);
  [`TH2_HARDENED_REAUDIT.md`](../../evidence/public_geometry/reviews/TH2_HARDENED_REAUDIT.md).
- THXY final successor:
  [`THXY_FULL_MACRO_P3FREE_HJ_CERT.json`](../../evidence/public_geometry/THXY_FULL_MACRO_P3FREE_HJ_CERT.json);
  [`THXY_FULL_MACRO_REAUDIT.md`](../../evidence/public_geometry/reviews/THXY_FULL_MACRO_REAUDIT.md).
- HJ chosen-basis theorem and slide ledger: Horvat--Jablonowski,
  [arXiv:2510.20282](https://arxiv.org/abs/2510.20282);
  [`AREA_BASIS_3HANDLE_SLIDE_RESULT.md`](../../evidence/public_geometry/source_notes/AREA_BASIS_3HANDLE_SLIDE_RESULT.md).
- MWW sphere maps: Manolescu--Walker--Wedrich,
  [arXiv:2206.04616](https://arxiv.org/abs/2206.04616).
