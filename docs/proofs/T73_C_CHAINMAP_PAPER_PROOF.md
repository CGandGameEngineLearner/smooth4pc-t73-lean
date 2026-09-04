# Attempted paper-level proof of the C comparison

Date: 2026-09-04

## Outcome

The finite Burau calculation and the abstract representable-coefficient
reduction are reproducible, but the C comparison cannot presently be closed
from the repository.  The earliest missing object is an actual chain-level
coefficient-bimodule isomorphism

\[
H_{T,T'}:C_R(T,T')\longrightarrow
C(FT,FT')\otimes C(S^1)^{\otimes 227}
\]

defined for the genuine MWW cut coefficient, natural for both gluing actions.
The code records endpoints of 44 product arcs and two disjoint support boxes;
it does not define either chain complex, a foam map between them, or the
naturality homotopies.  Consequently no honest paper proof can yet identify
the endpoint Burau coefficient 2624 with a functional on the MWW quotient.

This note separates the valid conditional categorical construction from the
candidate-specific inputs that remain absent.

## 1. Exact target statement

Let `C` be one fixed, explicitly specified dg tangle/foam category over
`Q[q,q^{-1}]`.  For every pair of boundary tangles `T,T'`, let `C_R(T,T')`
be the complex whose homology is the MWW one-handle coefficient

\[
M_R(T,T')=\operatorname{KhR}_2(R\cup T'\cup\bar T).
\]

A proof of C requires all of the following data.

1. A chain map `H_{T,T'}` as displayed above, not merely an isomorphism of
   dimensions or homology groups.
2. Chain-level commutative squares

   \[
   H_{S,T'}L_f=(L_{Ff}\otimes1)H_{T,T'},\qquad
   H_{T,U}R_g=(R_{Fg}\otimes1)H_{T,T'}
   \]

   for every homogeneous foam/tangle morphism `f,g`, with the required
   pregrading factors.
3. Compatibility with the quantum cyclic relation, so that `H` induces a
   map on the quantum trace and then on the ordinary coefficient `HH_0` after
   specialization.
4. A defined vertical-to-horizontal/endpoint map in the precise BPW/BHPW
   categories, including duality, orientation and pivotal conventions.
5. Naturality for every MWW beta and psi generator at every finite cable
   state, on the whole source rather than only the selected vector.
6. A derivation of every pivotal sign, `q`-power and absolute grading shift.
7. Evaluation on the selected genuine MWW class equal to the independently
   computed endpoint scalar 2624.

Only after these seven items are proved does the quotient universal property
produce the functional used by the obstruction theorem.

## 2. What the C1/C2 code proves

`scripts/certify_t73_c1_cut_link.py` verifies a finite pairing table for 44
recorded `y` and `z` arcs, plus 227 recorded leftover circles.  It checks
rational coordinates, labels and hashes against the selected P0 cut data.

`scripts/certify_t73_c2_comparison.py` states its limitation in its module
docstring: the construction is “not a chain-level Blanchet--Khovanov complex
of the actual W2 cut.”  Its `H` object consists of 44 records with a start-arc
hash, an end-arc hash and a `PASS` string.  The verifier checks those hashes
and that two axis-aligned support boxes are disjoint from bounding boxes of
the recorded arcs and circles.  It never constructs `C_R`, `C`, a foam, a
differential, a chain map, or a naturality homotopy.

The fields called `action_squares` are assigned `status: PASS` after the two
support boxes are created.  Disjoint support is useful geometric evidence for
an interchange argument, but is not the interchange chain map or a proof that
the maps agree in the precise MWW/BHPW category.

The Lean file `Smooth4PC/RepresentableCoefficient.lean` proves the algebraic
fact that the Hochschild quotient of an already-given representable
coefficient has the expected form.  It accepts the coefficient equivalence as
input and does not construct the candidate-specific `H`.

Thus the exact first missing datum is:

> **C-H1.** Definitions of the actual complexes `C_R(T,T')` and
> `C(FT,FT')`, together with explicit chain maps `H_{T,T'}` and proofs of the
> two action squares for arbitrary homogeneous `f,g`.

## 3. Scope of the published trace and functoriality results

BPW Proposition 3.20/3.21 gives trace/shadow constructions under the stated
dual and locally pregraded hypotheses.  BPW Theorem E acts on oriented
cablings of a fixed framed annular link.  BHPW Theorem 4.6 supplies strict
functoriality for its specified tangle complex.  These results remove a
projective sign once the relevant objects and cobordisms have been placed in
that theory.

They do not identify the geometrically named MWW coefficient `M_R` with the
paper's endpoint Hom-space.  In particular, strict functoriality does not
construct C-H1.  A paper proof must explicitly instantiate the categorical
hypotheses and show that both sides of each action square are the same foam or
are connected by a specified chain homotopy.

Conditional on C-H1 and the BPW dual/pregrading hypotheses, the formal route

\[
q\operatorname{Tr}(\mathcal C;M_R)
 \longrightarrow q\operatorname{Tr}(\mathcal C;
 \operatorname{Hom}(F-,F-))
 \longrightarrow \operatorname{End}(U)
\]

is standard: apply `H`, the trace/shadow comparison, the 227 counits, and the
endpoint representation.  The repository supplies enough abstract algebra to
show that a natural row then descends.  It does not supply C-H1 itself.

## 4. Missing all-cable geometric data

The explicit C1 rectangles are built only for the selected state

\[
s_0=e_{m_2}+e_{r_{xy}},
\]

which has 44 paired passages and 227 leftovers.  The all-state discussion in
the manuscript introduces owner counts

\[
n_y=(42,189,2,2,0),\qquad n_z=(269,1271,2,2,0)
\]

and then asserts that parallel copies of the P0 rectangles give an isomorphism
`H_r` for every cable state.  No finite artifact constructs the additional
owner-specific product data required for the 189 `m_3` passages, the two
`r_yz` passages, or arbitrary mixtures and multiplicities.  Nor is there a
uniform tubular-neighbourhood theorem with verified hypotheses that derives
all of them from the 44 selected rectangles.

The next missing datum is therefore:

> **C-H2.** For every owner and every primitive paired passage, an actual
> framed product rectangle in one common cut boundary, plus a proof that
> arbitrary parallel copies remain disjoint and induce the claimed `H_r`
> naturally under all beta/psi operations.

Without C-H2, equations claimed for “every finite cable state” are not
supported by the selected-state certificate.

## 5. Endpoint and pivotal coefficients

`scripts/build_t73_endpoint_transport.py` assigns

```text
pivotal_sign = 1
q_power = 0
```

for every physical endpoint.  These values are not computed from the stored
orientation, framing or BPW/BHPW pivotal formulas.  Mutation testing only
shows that changing an assumed coefficient changes the output.

The third missing datum is:

> **C-H3.** A convention table and derivation assigning the pivotal morphism,
> sign and `q`-degree to every oriented endpoint, cup, cap and closure used by
> every cable state.

This matters because the earlier `-59072`/`2624` discrepancy was caused by
endpoint indexing, and because the detector is sensitive to these maps.

## 6. Absolute grading

The Manolescu--Neithalath erratum corrects the rational comparison by the
writhe shift

\[
\operatorname{KhR}_N(L)\otimes\mathbb Q
\cong \operatorname{KhR}^{\mathbb Q}_N(L)\{-(N-1)w(L)\}.
\]

The fact that the selected pure braid has total writhe zero does not determine
the writhe correction for every mixed-orientation closure and every source and
target complex in C-H1/C-H2.  A complete proof needs:

> **C-H4.** A diagram-by-diagram grading ledger in one convention, including
> writhe, cup/cap, circle, one-handle and cabling shifts, proving that `H`, all
> beta/psi maps and the detector are homogeneous and that the final absolute
> degree is 494.

## 7. Finite value and conditional conclusion

The public Artin/Burau code genuinely reconstructs the long word and computes
the endpoint-model coefficient 2624.  The Magnus/Andreadakis check also
correctly establishes the third-order property of that recorded word.  Lean
checks the final identity `(-2)^3(-328)=2624` and the abstract quotient lemma.

These facts prove the following conditional statement:

> If C-H1 through C-H4 are constructed and the selected MWW class maps to the
> recorded endpoint vector, then the divided cubic row is a homogeneous
> functional on the complete MWW two-handle quotient and evaluates to 2624 on
> that class.

They do not prove the antecedent.  The current paper must therefore retain C
as a hypothesis.  Closing C requires new chain-level/categorical and
all-cable geometric data, not a more detailed explanation of the existing
`PASS` fields.

