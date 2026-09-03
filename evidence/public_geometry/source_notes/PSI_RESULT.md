# Anchored-cap psi cocone

## Verdict

```text
base functional kappa_s0:                       GIVEN / CONSTRUCTED
raw owner-local retraction c_e:C_(s+e_i)->C_s: DOES NOT FOLLOW FROM MWW
reverse psi ribbon as c_e:                      FAILS LOCAL ALGEBRA AND DEGREE
two individual counit/core caps as c_e:         WRONG CODOMAIN (LIVE IN W2)
incoming psi kill at s0:                        REFUTED BY ZERO ENDPOINT SOURCES
full upward anchored cocone without qshadow:    NOT CONSTRUCTED
```

The proposed shortcut fails for a precise geometric reason: the local map
that evaluates the added pair by `epsilon tensor epsilon` is not a raw
cobordism in `I x partial W1`.

## 1. Two different surfaces

For a forward edge `e:s->t=s+e_i`, MWW defines

\[
\Psi_e^{[d]}:C_s\longrightarrow C_t
\]

from the ribbon between the new negative/positive parallels, with `d` dots
(`D:/tmp/r6/mww_handle_src/kirby.tex:275-283`). Its reverse is an actual raw
cobordism

\[
R_e^{op}:C_t\longrightarrow C_s.
\]

But `R_e^{op}` is not the desired counit row. At the local Frobenius level it
is the evaluation paired with the coevaluation ribbon, not two independent
disk counits. Composing it with the undotted creation does not give the
asserted zero/identity pair. Its raw MWW degree is zero; because the cabled
shifts differ by two, its normalized degree from `C_t` to `C_s` is `+2`, not
zero. Therefore it cannot satisfy

\[
c_e\Psi_e^{[1]}=Id
\]

as a degree-zero map.

The algebra that does satisfy

\[
(\epsilon\otimes\epsilon)\Delta(1)=0,
\qquad
(\epsilon\otimes\epsilon)\Delta(X)=1
\tag{1}
\]

uses two separate disk caps. A physical cable component is a parallel of the
possibly knotted attaching circle `K_i`; it does not bound a disk in
`partial W1`. Those disks exist only as parallel copies of the two-handle core
after passing to `W2`. They are exactly the disks attached by MWW's `Phi`
(`D:/tmp/r6/mww_handle_src/kirby.tex:359-369`). Thus (1) defines an
evaluation after core attachment, not a map `C_t->C_s` between raw summands.

Applying `Phi^{-1}` does not repair this. `Phi^{-1}` returns a class in the
cabled quotient, and its choice of intersections with the cores is defined
only modulo beta/psi relations. It does not canonically select the lower raw
summand `C_s`. Using it to define `c_e` would assume the psi quotient whose
cocone is being proved.

## 2. Degree obstruction

The two individual core/counit disks have raw quantum degree `-2` in total.
Together with the `+2` change from the target summand shift back to the source
shift, their normalized degree is zero, matching (1). This confirms that the
desired grading belongs to the W2-core evaluation.

The actual reverse W1 ribbon has raw degree zero and normalized degree `+2`.
The degree mismatch is an independent obstruction to replacing the core caps
by the reverse ribbon.

## 3. What is still proved at the anchor

The early incoming psi attack on the base class is nevertheless dead. The two
minimal predecessors have endpoint types

```text
(rxy,m2)=(0,1): Q(84,86)=0;
(rxy,m2)=(1,0): Q( 4,86)=0.
```

Raw shadow naturality implies that every map from either predecessor has zero
endpoint image. Since `kappa_s0` factors through the nonzero endpoint cup
block, on the entire predecessor modules

\[
\kappa_{s0}\Psi_{rxy}^{[d]}=0,
\qquad
\kappa_{s0}\Psi_{m2}^{[d]}=0,
\qquad d=0,1.
\]

Hence `vT` is not an incoming psi0 image. This local result does not provide
rows at higher states.

## 4. First missing object

The smallest sufficient replacement is not a raw cap cobordism. It is a
statewise family of linear rows

```text
ACTUAL_W2_CORE_EVALUATION_COCONE
```

on the cabled direct sum, constructed so that the two core disks in `Phi`
evaluate every newly added pair and so that the result is independent of the
raw summand representative. Equivalently, one may use the constructed
statewise q-shadow plus the actual W2 core maps. Either route must prove
beta/psi quotient compatibility; it cannot be replaced by maps `C_s->C_s0`
that do not geometrically exist.

## 5. Effect

The anchored raw-cap proposal is refuted. The base `-59072` class survives the
two incoming psi maps, but psi descent at all higher states still requires the
statewise core-evaluation/qshadow cocone. No beta or sphere conclusion is made.
