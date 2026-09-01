# QSTAR R7 legality adjudication

Verdict: `CHAIN_SURVIVES_L2_L3 / NO_LEGAL_STANDARD_NONZERO_FOUND`  
Scope: the registered point-push serialization and the 22 enumerated L3
collar/order objects only.  This is not a proof that every standard member or
every possible legal collar has zero detector.

## 1. Identity, order and timing

- reviewed source:
  `QSTAR_R7_LEAN_RISK_AUDIT_20260901.md`
- source SHA-256:
  `08CC525165B7CA45F26C28D845C8A0E8D304F3904D99EF2756EC69ED440199F3`
- source bytes: `8599`
- pre-search criteria timestamp: `2026-09-01 21:04:19 +09:00`
- pre-search criteria commit: `cf4a990cca9a693e0c32b6cd8a978942cd03168a`
- pre-search criteria SHA-256:
  `0A84F6DE883736F55B1892C99353916AF24339C2BB4BCBDCA159EB6766CA941D`
- independent L2 checker created: `2026-09-01 21:09:51 +09:00`
- adjudication close: `2026-09-01 21:31:46 +09:00`
- measured post-freeze duration: `27 min 27 s`

The initial source-open time was not separately persisted; it predates the
criterion freeze and is not reconstructed after the fact.

The frozen criteria are in
`docs/proofs/QSTAR_R7_LEGALITY_CRITERIA_PRESEARCH_20260901.md`.
They were committed before the L2/L3 generators and detailed results were
opened.  No criterion depends on a zero or nonzero detector value.

## 2. What “legal” means

The bearing requirements are structural:

1. same actual framed handle presentation, `W1` filling, oriented based cut
   tangle, collar endpoints, labels, normal field and insertion point;
2. serialization is a linear extension of the geometric movie order;
3. only disjoint-support events with a strict interchange theorem may swap;
4. braid replacement requires equality in the based labelled braid/tangle
   category, not equality of a closure, permutation, word reduction or homology;
5. every coordinate change transports `W`, `u`, `Theta`, `ell` and the
   insertion point together;
6. collar changes require an actual relative framed isotopy and the same
   filling preimage; a relative mapping-class or framing twist is a different
   object.

These conditions imply, rather than assume, equality of the scalar series. If
`W'=PWP^-1`, `u'=Pu` and `ell'=ell P^-1`, then

`ell' (W'-I) u' = ell (W-I) u`.

Thus `delta_3` is well-defined within the legal convention class whenever the
registered naturality squares hold.

## 3. L2: two t73 orders

### Decision

| object | legality | epsilon profile start | first anomaly | delta_3 |
|---|---|---:|---:|---:|
| registered `oriented_point_push` | **LEGAL** | `[0,0,0,7384]` | 3 | **-59072** |
| emitter `source_sweep_movie.expanded_Artin_word_B44` | **ILLEGAL** as a serialization of that movie | `[0,0,-168,7624]` | 2 | -58976, non-bearing |

The independent checker exited `0` and reproduced both rows exactly.

### Reason

The emitter sorts crossings by increasing `x`.  The actual point-push
traverses segment 6 in increasing `x`, then segment 2 in decreasing `x`.
Consequently the emitter reverses the 168 incoming `L` events.  They share the
moving W1 strand and are not disjoint-support events; no strict interchange
permits that reversal.  The source artifact itself records:

`emitter order is not point-push chronology`.

The AM comparison also replaces only the word while freezing `u`, `ell`,
`Theta` and the insertion coordinates, violating simultaneous transport.

Therefore the registered value is `-59072` and the registered first anomaly
is degree 3.  The degree-two emitter result does not create a legal/legal
disagreement, so L2 does not make `delta_3` ill-defined.

Provenance differs as well.  `-59072` has the executable chain

`T73_COLLAR_BRAID.json -> verify_t73_collar_braid.py ->
recompute_eta_t1_delta3.py -> ETA_T1_DELTA3_CERT.json`.

The `-58976` number is independently reproducible, but it is not calculated
or stored by `am_equal_treatment_audit.py` or
`AM_EQUAL_TREATMENT_NUMBERS.json`; it appears only in the prose AM report.

Boundary retained: the actual framed coefficient `R`, M2 framing adapter and
time-parametrized four-cable R2 movie are not constructed.  L2 establishes
the registered source-level point-push value, not its full manifold promotion.

## 4. L3: the 22 standard-member outputs

Counts under the precommitted criteria:

```text
LEGAL             0
ILLEGAL          19
NOT ESTABLISHED   3
```

| # | branch | order | verdict | decisive reason |
|---:|---|---|---|---|
| 1 | exact_move65_incl_Hilden_50 | FWD | ILLEGAL | certified only through movie 65; source35/source9 remain |
| 2 | exact_move65_incl_Hilden_50 | REV | ILLEGAL | list reversal is neither chronology, inverse nor certified interchange |
| 3 | cross_owner_mod_Hilden_46 | FWD | ILLEGAL | incomplete prefix; removes actual Hilden transport while freezing the detector |
| 4 | cross_owner_mod_Hilden_46 | REV | ILLEGAL | same defect plus unsupported reversal |
| 5 | short_incl_Hilden_14 | FWD | ILLEGAL | braid-equal to #1 but still only a movie65 prefix |
| 6 | short_incl_Hilden_14 | REV | ILLEGAL | unsupported reversal |
| 7 | short_cross_owner_10 | FWD | ILLEGAL | incomplete prefix and removes Hilden transport |
| 8 | short_cross_owner_10 | REV | ILLEGAL | same defect plus unsupported reversal |
| 9 | cond_through_s35_54 | FWD | ILLEGAL | conditionally fills source35 but leaves source9 unresolved |
| 10 | cond_through_s35_54 | REV | ILLEGAL | incomplete and unsupported reversal |
| 11 | cond_both_disks_60 | FWD | NOT ESTABLISHED | two product disks, ball chart, framing and actual filling are unconstructed |
| 12 | cond_both_disks_60 | REV | ILLEGAL | no such reverse movie was generated |
| 13 | cond_both_disks_mod_Hilden_56 | FWD | ILLEGAL | deletes actual Hilden factor without covariant transport |
| 14 | cond_both_disks_mod_Hilden_56 | REV | ILLEGAL | same defect plus unsupported reversal |
| 15 | ball_follows_full_incl_Hilden_80 | FWD | NOT ESTABLISHED | strongest candidate; lacks kappa_y, move disks, H_t, same-filling preimages and naturality |
| 16 | ball_follows_full_incl_Hilden_80 | REV | ILLEGAL | reverses full cable word, not the generated terminal-order branch |
| 17 | ball_follows_mod_Hilden_76 | FWD | ILLEGAL | deletes Hilden factor while freezing detector coordinates |
| 18 | ball_follows_mod_Hilden_76 | REV | ILLEGAL | same defect plus unsupported reversal |
| 19 | reverse_terminal_full_80 | FWD | NOT ESTABLISHED | graph order exists, but framed MM11 movie and same filling are unproved |
| 20 | reverse_terminal_full_80 | REV | ILLEGAL | second unsupported reversal of the cable word |
| 21 | ball_exterior_prequotient_50 | FWD | ILLEGAL | loses six prescribed cooriented ball intersections; different input |
| 22 | ball_exterior_prequotient_50 | REV | ILLEGAL | different input plus unsupported reversal |

The first bearing source statement is

`same_Wone_filling_preimage_premise = NOT_SERIALIZED_OR_CONSTRUCTED`.

The same source expressly lacks the parameterized input ball, every embedded
move disk and ambient isotopy, the post-move ball chart, pinch ownership, the
half-circle band, transported normal framing and a common naturality square.

All three `NOT ESTABLISHED` forward candidates begin below order 3 in the AM
calculation.  Even if later actualized, they would not yet instantiate the
registered `Gamma_3` antecedent.  They therefore are not presently a
`STANDARD_MEMBER_GAMMA3_NONZERO_COLLAR`.

### Consequence

The 22 nonzero numbers do not kill the detector chain: none comes from a
verified legal standard-member convention.  This does not prove that no such
legal standard convention exists.  It removes exactly these 22 objects and
leaves the named global search question unresolved.

The positive upgrade is correspondingly narrow: the actual oriented
source-sweep convention distinguishes t73 from ANCHOR-537 at the registered
point-push gate, and the value is invariant under genuinely legal coordinate
changes.  No claim is made for all standard homotopy four-spheres.

## 5. Lean compile receipt

The missing on-disk receipt is now supplied at
`docs/proofs/QSTAR_R7_LEAN_COMPILE_RECEIPT_20260901.md`; the complete raw
`T73Audit` output is at
`docs/proofs/QSTAR_R7_T73AUDIT_RAW_20260901.txt`.

Summary:

- full unittest: exit `0`, `2/2 OK`, `417.949 s` wall time;
- independent project-module build: `14/14` exit `0`;
- direct `T73Audit.lean`: exit `0`;
- `#print axioms` reports: `38`;
- allowlist only: `propext`, `Classical.choice`, `Quot.sound`;
- `sorryAx`: absent;
- project tracked changes at audited HEAD: `0`.

Dependency disclosure:

- mathlib tracked changes: `0`;
- mathlib untracked root probes: `45`;
- eight package repositories: manifest HEADs matched and dirty count `0`.

Thus compilation and the axiom claim are now evidenced for the named host
state, but this is not a hermetic clean-clone replay.  The earlier count `126`
is not the state observed by the receipt; the environment remains dirty in the
strict sense because of the 45 untracked probes.

## 6. Final judgment

1. `delta_3` is well-defined inside the registered legal convention class.
2. For the fixed t73 point-push, the bearing result is
   `first anomaly = 3`, `delta_3 = -59072`.
3. L2 does not invalidate the chain.
4. L3 supplies no legal standard-member counterexample among its 22 outputs.
5. The broad nonexistence of a legal standard-member `Gamma_3` nonzero collar
   is not proved.
6. Lean still proves a conditional pipeline rather than any geometry
   inhabitant; the new receipt changes evidence quality, not theorem scope.

No sphere/control experiment numbered 5 was run, in accordance with the task
ordering.
