# T73 Counterexample Proof Consolidation Design

## Goal

Produce one self-contained, source-indexed candidate proof that the
`X(41,189,73)` Cappell--Shaneson homotopy sphere has a nonzero
Khovanov--lasagna class in quantum degree `494`, and therefore is not
diffeomorphic to the standard `S^4`.

The deliverable must distinguish three statuses mechanically:

1. a theorem proved in the written argument;
2. a finite calculation checked by code or Lean; and
3. an external theorem invoked from MWW, BHPW/BPW, or
   Horvat--Jablonowski.

No status string, certificate field, or declared interface may stand in for a
proof.

## Proof normal form

The proof will use the following single chain.

1. Let `R` be the actual balanced coefficient supplied by the transported
   framed annuli.  Its Hattori cut has the two-sided form
   `B union dual(B)` plus `227` split circles.  Hence

   ```text
   M_R(T,T') = Hom(BT,BT') tensor A^(tensor 227),
   A = Q[X]/(X^2).
   ```

2. For `T = inverse(B) U_(0,5)`, let `H_(T,T)` be the balanced Hattori
   equivalence and define

   ```text
   v_T = inverse(H_(T,T))(Id_(BT) tensor X^(tensor 227)) in M_R(T,T).
   ```

   Here `X^(tensor 227)` is a tensor of `227` separate circle labels, never
   the vanishing algebra product `X^227`.  The class `[v_T]` is its image in
   coefficient `HH_0`.  This
   avoids the invalid one-sided formula `M_R(T,T)=Hom(T,BT)` and does not
   require a fictitious map `1 -> B` or a full natural transformation
   `eta_R`.

3. BPW vertical-to-horizontal trace, the `227` counits, and strict BHPW
   functoriality send `[v_T]` to the actual cup vector
   `u=e_0-e_5+O(h)` in `Q(88,86)=M_1(88)`.  Its one-handle degree is `498`;
   the cabled shift is `-4`, giving degree `494`.

4. The exact point-push calculation gives

   ```text
   [h^3] ell (rho_h(W)-I) u = -59072 != 0.
   ```

   The input is `[v_T]`.  It is never replaced by `xi`;
   applying the same relative detector to `xi` introduces `(W-I)^2` and has
   zero cubic coefficient.

5. On the actual fixed source `M_1(88)`, reindex the mandatory endpoint
   defect as relative degree `nu=0`.  Dotted `psi1` and dotted sphere maps add
   only `X` labels and preserve this head.  Undotted `psi0` and undotted sphere
   maps add one further `1`, landing in `nu=1`.  Physical-copy beta actions
   preserve `nu`; Reynolds normalization uses cable copies, never the `2/42`
   internal gate-passage counts.

6. Construct a new pairwise-disjoint determinant-one HJ sphere basis in one
   fixed `partial W2`.  For each cabled state `s`, let

   ```text
   Q_s : V_s_actual -> V_s_canonical
   ```

   be an actual framed linear equivalence induced by the fixed owner-point
   braid.  Define one target row

   ```text
   Lambda_s : V_s_actual -> Q
   ```

   by transporting the canonical Reynolds/counit row through `Q_s`.  For an
   edge `e:s->t`, define its actual sphere map literally as

   ```text
   C_e^d : V_s_actual -> V_t_actual
   C_e^d = inverse(Q_t) (Id_persistent tensor split_tree_e^d) Q_s.
   ```

   The counit identities on the whole source are

   ```text
   epsilon^b Delta^(b-1)(1) = 0,
   epsilon^b Delta^(b-1)(X) = 1.
   ```

   The common cocone target is `Q`.  The proof must check the complete MWW
   generator list, on the whole typed source:

   ```text
   Lambda_s beta_s(b) = Lambda_s,
   Lambda_t psi_e^0 = 0,
   Lambda_t psi_e^1 = Lambda_s,
   Lambda_t C_e^0 = 0,
   Lambda_t C_e^1 = Lambda_s,
   ```

   for every owner braid, every psi edge, all three signed sphere edges, all
   finite cable states, and both lattice directions.  These equations, plus
   the quotient universal properties, exhaust the beta/psi/three-handle
   relation submodule; testing only the selected vector is forbidden.

   The same vertex potentials make all sphere/sphere, sphere/psi, and psi/psi
   squares flat.  The typed changing-endpoint comparisons are

   ```text
   Phi_t C_e_cabled = C_e_W2 Phi_s,
   W_t C_e = C_e W_s,
   K_t C_e_0 = C_e_0 K_s,
   ```

   where `K_s` is the cubic coefficient of `W_s-I`.  MWW's core-attachment
   diagram and strict functoriality must prove these equations for every
   source vector, not merely supply a commuting-picture label.

7. Conditional on the explicitly cited geometric balanced-Hattori theorem,
   the fixed-`Y` HJ/direct-`Q` theorem, MWW's handle formulas, and BPW/BHPW
   strict functoriality, the resulting cubic row is a well-defined rational linear functional on
   the complete MWW quotient and takes value `-59072` on the chosen class.
   Therefore a nonzero homogeneous `q=494` class survives all three-handles.
   The detector is homogeneous of absolute degree zero as a scalar map on the
   fixed `q=494` summand.  MWW's four-handle isomorphism preserves the absolute
   bigrading and this class.  Since the standard `S^4`
   module is concentrated in bidegree `(0,0)`, graded diffeomorphism
   invariance rules out a diffeomorphism to `S^4`.

## Files

- Create `docs/proofs/T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md` for the
  unified mathematical argument, with primary-source line anchors and an
  explicit dependency table.
- Create `Smooth4PC/AugmentationCocone.lean` for the finite Frobenius,
  Reynolds-telescope, and cubic-conjugation lemmas that can honestly be
  kernel checked without formalizing three-manifold topology.
- Create `Smooth4PC/HattoriBalancedInput.lean` for the balanced-coefficient
  typing and degree arithmetic, with the geometric Hattori equivalence kept
  as a narrowly typed, visible theorem parameter until formally constructed.
- Modify `Smooth4PC/ConditionalChain.lean` only after the new lemmas compile;
  do not weaken its theorem type or hide geometric premises.
- Create `audit/t73_proof_dependency_manifest.json` and tests that reject the
  one-sided coefficient model, the `xi` input swap, the `M_0` source, the
  retired `-28864` scalar, and a path-dependent edge braid.

## Verification

The mathematical document is accepted only after two independent reviews:

1. a source/type review of the balanced Hattori coefficient and the
   `M_R(T,T') = Hom(BT,BT') tensor A^(tensor 227)` identification;
2. a hostile proof review of the full quotient quantifiers and the standard
   `S^4` comparison.

The Lean portion must compile with zero `sorry`, `admit`, project axioms, or
opaque proof shortcuts.  Passing Lean proves only the algebra explicitly
encoded there; the final report must not call the result fully formalized
until the geometric source theorems are also formalized or imported from a
trusted library.

## Completion language

- `CANDIDATE_PROOF_INTERNALLY_CLOSED`: the written theorem chain and all
  finite calculations survive the two reviews.
- `FORMALLY_VERIFIED_COUNTEREXAMPLE`: the complete chain, including geometric
  Hattori and HJ/direct-`Q` inputs, is checked in a proof assistant with no
  unresolved hypotheses.
- `EXTERNALLY_ACCEPTED_COUNTEREXAMPLE`: independent experts have verified the
  proof.  This repository cannot assign that status to itself.
