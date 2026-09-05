# Running adversarial audit: `paper/spc4-t73-candidate/main.tex`

This file is the persistent long-term memory for a correctness audit begun
2026-09-04.  It is an audit ledger, not part of the paper.  Findings remain
open until independently resolved with primary-source or mechanically checked
evidence.

## Audit standard

- **Critical**: invalidates the main theorem or makes its proof incomplete.
- **Major**: a substantive false/unsupported theorem, citation, computation,
  or dependency, but not yet shown to invalidate the main theorem alone.
- **Minor**: exposition, attribution, or reproducibility defect that does not
  presently alter correctness.
- Status is one of `OPEN`, `CONFIRMED`, `RESOLVED`, `DISPUTED`, or `BLOCKED`.
- A repository certificate proves only the predicates actually checked by its
  verifier.  It is not evidence for geometric/topological semantics unless
  those semantics are independently connected to the encoded data.

## Scope map

| Workstream | Scope | Status |
|---|---|---|
| Global proof chain | theorem dependency graph, internal consistency, TeX | FIRST ADVERSARIAL PASS COMPLETE |
| Topology / P0 | Cappell--Shaneson identification, Kirby/PL geometry | TWO PASSES COMPLETE |
| Lasagna / citations | MWW/BPW/BHPW comparison and primary sources | TWO PASSES COMPLETE |
| Computation / Lean | finite value, scripts, certificates, formal boundary | FIRST PASS COMPLETE |

## Current verdict (updated 2026-09-05)

**The unconditional Trace-73 counterexample theorem is not proved.**  The
abstract linear-algebra implication is valid; the determinant calculation,
public-word Burau value `2624`, and Artin--Magnus/Andreadakis finite checks
replay.  The relevant published MWW handle theorems and classical topology
results appear sound within their stated hypotheses.

The construction work after the first audit has repaired the topological
typing of P0/E13: the Johnson mapping classes give an actual unlabelled AR
presentation, standard collar topology supplies the 44 marked vertical arcs,
the auxiliary braid is moved out of the attaching link and into C, and
transporting the complete AR upper handles gives E13/P3. The proof still fails
at independent categorical bridges:

1. no constructed BPW/BHPW/MWW coefficient-shadow map turning the Burau cubic
   into a functional on the genuine two-handle quotient (`D-03`--`D-05`);
2. no proof of the actual three-handle endpoint factorization on the whole
   MWW source (`D-06`);
3. the standard pivotal coefficients are now derived, but the relative split
   is not constructed and therefore the corrected absolute degree `223`
   remains conditional.

The repository's own source and git history confirm these are proof gaps, not
merely missing Lean packaging: the prior conditional theorem was promoted to
an unconditional claim by changing prose and expected status flags without
adding the missing constructions (F-015).

## Findings

### F-001 — P0 is simultaneously claimed discharged and explicitly declared open

- Severity: **Critical**
- Status: **CONFIRMED (internal textual contradiction)**
- Locations: `README.md` opening summary; `main.tex` abstract; theorem
  `Embedded candidate presentation, P0` and its proof.
- Evidence: the abstract says P0 is “discharged,” but the proof of P0 says
  “The geometric evidence required by this statement is presently OPEN.”
- Consequence: any unconditional conclusion requiring identification of the
  computed Johnson handle presentation with the Cappell--Shaneson sphere is
  unsupported unless a later proof really closes P0 and the earlier “OPEN” is
  a stale cross-reference.  This must be traced through the later theorem and
  its actual evidence, not repaired editorially.
- Required resolution: verify every premise of the later claimed P0 discharge,
  including that encoded combinatorial objects realize the asserted ambient
  framed handle presentation and that verifier predicates imply the geometric
  theorem.
- Revision note: during this audit, the working-tree `main.tex` was changed to
  remove the quoted `OPEN` sentence and replace it with a claim that later
  sections assemble the data.  This removes the literal contradiction in the
  current working copy but supplies none of the missing ambient verification
  identified in F-102--F-107.  The finding remains part of the audit history
  for starting commit `d7bbff8`; its mathematical consequence remains open.

### F-100 — The cited Cappell--Shaneson homotopy-sphere criterion is correctly stated, but applies only after geometric identification

- Severity: **Major (load-bearing scope condition); citation itself confirmed**
- Status: **CONFIRMED**
- Locations: `main.tex:164--181`, Theorem `hyp:P3` at `main.tex:279--290`,
  proof of Theorem `thm:joined` at `main.tex:315--324`, and
  `sec-published-results.tex:199--210`.
- Primary-source check: Iwaki, Proposition 2.1, states that the manifold
  \(\Sigma_A^\varepsilon\) obtained by surgery on the canonical section of the
  mapping torus is a homotopy 4-sphere iff \(\det(A-I)=\pm1\).  See
  https://arxiv.org/abs/2404.05096, Proposition 2.1 (HTML lines 85--102 in the
  arXiv rendering).  Iwaki also explicitly defines the input as an actual
  mapping-torus surgery, not an abstract matrix-labelled Kirby ledger.
- Evidence: direct arithmetic for the displayed matrix gives
  \(\det A=\det(A-I)=1\).  This validates the homotopy-sphere conclusion for
  the *standard surgery object* \(\Sigma_A^0\).  It does not identify the
  independently encoded `X_J` with that object.  The paper itself correctly
  acknowledges this at `main.tex:179--181` and `main.tex:288--289`.
- Dependency impact: the homotopy-sphere branch is sound only for
  \(\Sigma_A^0\).  Transporting the obstruction computed on `X_J` to that
  sphere depends entirely on the still-problematic P0/E13 diffeomorphism in
  F-103.

### F-101 — P0 remains explicitly open in several controlling statements despite being used as an unconditional theorem

- Severity: **Critical**
- Status: **CONFIRMED**
- Locations: proof of Theorem `hyp:P0`, `main.tex:245--249`; scope statement
  `main.tex:431--439`; proof of Proposition `prop:scope`, `main.tex:387--391`;
  appendix interface statement `main.tex:1665--1671`; contrary assertions in
  Theorem `thm:P0discharge`, `main.tex:977--986`, the main proof at
  `main.tex:315--324`, and the conclusion at `main.tex:1590--1596`.
- Evidence: `main.tex:246` says “geometric evidence ... is presently OPEN”;
  `main.tex:438--439` says P0 remains open; `main.tex:1665--1667` says the
  geometric inputs remain open.  Yet `thm:P0discharge` asserts P0 holds and
  the main theorem consumes it unconditionally.  These are not merely a Lean
  packaging distinction: the open statements expressly concern geometric
  evidence and geometric inputs.
- Dependency impact: P0 identifies the actual framed handle presentation,
  both Kirby movies, detector ball/cabling, and ultimately `X_J` with
  \(\Sigma_A^0\).  Until the contradiction is resolved by a genuine proof,
  the main counterexample theorem is unproved.

### F-102 — The P0 reconstruction verifier accepts semantic topology as declared strings/PASS fields

- Severity: **Critical**
- Status: **CONFIRMED**
- Locations: Appendix soundness lemma `main.tex:1604--1640`;
  `scripts/reconstruct_t73_p0.py:89--117`, `:132--175`, `:179--213`, and
  `:673--690`; `scripts/check_t73_p0_embedded_witness.py:1--6` and `:47--54`.
- Evidence: the checker explicitly says it “cannot prove PL embeddedness by
  itself.”  `verify_ball` checks a closed triangulated surface with Euler
  characteristic two, then accepts the ambient solid as a 3-ball merely when
  `certified_topological_type == "3-ball"`.  Pairwise strand disjointness,
  normal fields, and AR passage binding are accepted from stored `status =
  PASS` fields.  The final verifier requires only that `independent_checks`
  contain objects labelled PASS; unlike the separate structural checker, it
  does not authenticate a verifier or recompute those receipts.
- Genuine finite content: rational-coordinate parsing, monotonicity of the 44
  strand polylines, projected crossing chronology, and letter-for-letter
  braid equality are meaningful finite checks.
- Missing ambient content: that the supplied complex is the claimed embedded
  ball in the actual AR boundary; that normals define the required framed
  collar; and that the declared Kirby local models extend to ambient handle
  moves carrying the whole link.
- Dependency impact: a passing JSON certificate does not entail the hypotheses
  of the paper's P0 soundness lemma.  The proof of `thm:P0discharge` therefore
  promotes certificate syntax to ambient topology.

### F-103 — E13 “identification” is asserted by boolean/status assembly, not proved by an ambient PL homeomorphism or Kirby equivalence

- Severity: **Critical**
- Status: **CONFIRMED**
- Locations: `main.tex:981--986`, `main.tex:1535--1546`;
  `scripts/certify_t73_e13_close.py:425--475`, `:501--587`, `:589--646`, and
  `:698--731`; `scripts/certify_t73_e13_identification.py:189--271` and
  `:350--386`.
- Evidence: the E13 close script checks hashes and pre-existing PASS/status
  fields, constructs a list of prose-labelled pipeline stages, assigns every
  stage `status: PASS`, and then defines the identification test to succeed
  when no `resolved_maps` item is labelled OPEN (except the expressly open
  Lean topology field).  It finally writes
  `identified_with_Sigma_A_0: True`.  No map between 4-manifolds is constructed
  or verified, no complete sequence of legitimate Kirby moves is checked, and
  no theorem is invoked whose hypotheses turn the hash-linked objects into a
  diffeomorphism.  The wrapper then treats the child script's self-set boolean
  as proof (`certify_t73_e13_identification.py:257--262`) and again writes the
  desired identification (`:361--373`).
- Additional warning from the artifacts: both scripts' module docstrings say
  Lean topology remains uninhabited and “No counterexample is claimed”; the
  P3 generator explicitly says it is not a triangulation of 4-dimensional
  \(W_3\) and does not identify `X_J` with \(\Sigma_A^0\)
  (`scripts/certify_t73_p3_four_handle.py:12--14`).
- Dependency impact: this is the sole bridge that moves a purported nonzero
  lasagna class on `X_J` to the actual Cappell--Shaneson homotopy sphere.  Its
  failure invalidates the proof of `thm:joined` even if every finite braid and
  matrix computation is correct.

### F-104 — The P3/E13 chain conflates boundary duality with nonexistent 4-dimensional “1--3 canceling pairs”

- Severity: **Critical**
- Status: **CONFIRMED AS AN INVALID STATED HANDLE-CANCELLATION ARGUMENT**
- Locations: `main.tex:292--300`, `main.tex:1537--1546`;
  `scripts/certify_t73_p3_four_handle.py:2--14`, `:172--207`, and `:233--257`;
  `scripts/certify_t73_e13_close.py:557--583` and `:625--630`.
- Evidence: ordinary handle cancellation is between consecutive indices
  \(k\) and \(k+1\).  There is a legitimate *boundary-dual description* in
  which the attaching sphere of a 3-handle is the belt sphere of a 1-handle
  in an upside-down presentation of the boundary, and surgery on that sphere
  can change \(\#^p(S^1\times S^2)\) back to \(S^3\).  That shorthand does
  **not** make an actual index-1 and index-3 pair in the same 4-dimensional
  handle decomposition cancel.  For example, the closed handlebody with one
  handle in each of indices 0,1,3,4 is the standard handle decomposition of
  \(S^1\times S^3\), not \(S^4\).  The P3 script never states and verifies the
  dualization map; it simply infers `cancels: True` from a dual-loop
  intersection count.  More seriously, E13 first calls the two surviving
  railroad 1-handles “1-3 cancelled” and then introduces three “extra 1-3
  pairs.” If these are actual added handles, they are not canceling
  stabilizations; if they are only boundary-dual bookkeeping, the script has
  not supplied the equivalence with the original three CS 3-handles.
- Primary-source cross-check: Aitchison--Rubinstein p.7 describes
  complementary 1/2 pairs and, separately, complementary 2/3 pairs; it does
  not authorize 1/3 cancellation.  The source also says 3/4 attaching data are
  controlled via Laudenbach--Poenaru, not that a 3-handle cancels a 1-handle.
- Dependency impact: the claimed remaining boundary \(S^3\) may be a boundary
  surgery statement, but the asserted preservation/identification of the
  *4-manifold* is not established.  The stage-7/stage-8 E13 handle counts and
  hence the construction of `X_J` are unreliable.

### F-105 — P3 supplies a generic cubical 4-ball but no verified attaching homeomorphism to the actual boundary

- Severity: **Major**
- Status: **CONFIRMED**
- Locations: Theorem `hyp:P3` and proof, `main.tex:279--303`;
  `scripts/certify_t73_p3_four_handle.py:77--112` and `:233--257`.
- Evidence: `four_ball()` verifies elementary combinatorics and Euler
  characteristic of an abstract \(I^4\).  The result then declares its
  attaching map to be “the explicit cubical S3 left after” the alleged 1/3
  cancellations, but does not construct a simplicial/cubical homeomorphism
  from \(\partial I^4\) to the actual \(\partial W_3\).  The source docstring
  concedes that the artifact is not a triangulation of 4-dimensional \(W_3\).
  Euler characteristic zero of a purported boundary is not recognition of
  \(S^3\).
- Dependency impact: MWW's four-handle theorem can be applied only after an
  actual four-handle attachment along a spherical boundary component has been
  established.  The finite `I^4` record does not discharge that geometric
  premise.

### F-106 — The Johnson “PL homeomorphism” verifier does not establish a global PL homeomorphism of the torus

- Severity: **Critical**
- Status: **OPEN (strongly unsupported by the inspected verifier)**
- Locations: Lemma `P0a` and proof, `main.tex:924--947`;
  `scripts/verify_t73_pl_homeomorphism.py:40--70`, `:89--130`,
  `:133--166`, and `:182--282`.
- Evidence: the verifier checks positive Jacobians and recorded inverses on
  listed individual tetrahedra, and tests the *composite* inverse at only two
  sample points.  It does not visibly verify that source cells tile the
  claimed support, that affine formulas agree on every shared face, that
  images have disjoint interiors and cover the target, or that periodic face
  identifications give a well-defined global torus map.  The Heegaard-pair
  test is a finite owner table on 64 cube centers/384 tetrahedron
  barycentres; preservation of those samples is not by itself setwise
  preservation of the full handlebody subcomplexes.
- Dependency impact: without a certified global homeomorphism preserving the
  Heegaard pair and section neighborhood, the constructed transvection matrix
  product does not supply the geometric monodromy or the AR handle
  presentation used by P0/E13.

### F-107 — The two Kirby cancellation certificates check incidence syntax, not the full framed cancellation criterion

- Severity: **Critical**
- Status: **CONFIRMED**
- Locations: `main.tex:557--577`, Lemma `P0b` at `main.tex:949--961`;
  `scripts/reconstruct_t73_p0.py:179--213`.
- Evidence: the generic P0 verifier turns the belt sphere and attaching circle
  into sets of listed vertices, checks that those sets share exactly one
  vertex, and separately trusts `geometric_intersection == 1` plus PASS fields
  for `local_movie`, `owner_transport`, and `normal_field_transport`.  A single
  shared vertex does not certify transverse geometric intersection one in an
  ambient 3-manifold; it does not exclude intersections along edge interiors
  or prove the relevant attaching circle is otherwise disjoint from the belt
  sphere.  Nor does the checker derive the zero relative twist/framing or an
  ambient isotopy carrying all other attaching components through the slides.
- Primary-source boundary: Aitchison--Rubinstein p.7 supports the standard
  geometric 1/2 cancellation criterion and describes sliding other 2-handles
  off the 1-handle.  It does not prove that this repository's 6- and
  1513-band encoded movies satisfy the criterion.
- Dependency impact: word substitutions and component counts after the two
  alleged cancellations cannot be promoted to equality of framed handle
  presentations.  P0 and E13 remain unproved.

### F-002 — C and S are also stated as theorems with proofs that explicitly say their evidence is open

- Severity: **Critical**
- Status: **CONFIRMED (internal text)**
- Locations: `main.tex:251-277` (`hyp:P1`, `hyp:P2`), contrasted with
  `main.tex:1318-1327` and `main.tex:1525-1533` (`thm:Cdischarge`,
  `thm:Sdischarge`).
- Evidence: each early “Proof” consists of the sentence that the required
  geometric evidence is presently `OPEN`.  The later discharge proofs merely
  assert that named finite objects “give” or “realize” the required analytic
  maps; the missing implication must be audited rather than treated as a
  proved theorem.
- Consequence: the main theorem invokes C and S as supplied inputs to the
  abstract nonstandardness theorem, so either open obligation breaks the
  claimed nonzero closed-manifold class.
- Revision note: the current uncommitted `main.tex` replaces these `OPEN`
  sentences with summary assertions.  This is an editorial resolution of the
  contradiction, not a construction of the missing maps in F-201--F-204.

### F-003 — The repository's controlling status documents disagree on whether the main theorem is conditional

- Severity: **Critical**
- Status: **CONFIRMED (internal text)**
- Locations: `main.tex:305-324,1588-1596`; `README.md` opening summary;
  `docs/INDEPENDENT_REVIEW.md` “Review boundary”; and
  `docs/GEOMETRIC_INSTANTIATION_AUDIT.md` status/table/final paragraph.
- Evidence: `main.tex` declares an unconditional counterexample and says the
  lack of Lean instantiation does not make the mathematical statement
  conditional.  `docs/INDEPENDENT_REVIEW.md` says the repository supports
  only a statement *under explicitly listed geometric identifications*.
  `docs/GEOMETRIC_INSTANTIATION_AUDIT.md` says “No counterexample is claimed”
  and “`thm:joined` remains Conditional on a candidate
  `ExternalGeometry`.”  The README simultaneously calls geometric inputs
  discharged but reports the premise audit `OVERALL=OPEN` and an uninhabited
  `ExternalGeometry`.
- Consequence: this is not merely a formalization disclaimer.  The repository
  itself classifies the candidate-level bridge needed for the paper's main
  theorem as conditional/open.  Until every such bridge is independently
  proved, the unconditional Theorem `thm:joined` is not supported by the
  repository's own declared evidence boundary.

### F-004 — The paper explicitly says its geometric instances are not proved in its body

- Severity: **Critical**
- Status: **CONFIRMED (internal text)**
- Locations: `main.tex:147-149` and `main.tex:1665-1671`, versus abstract
  `main.tex:79-88`, final identification `main.tex:1537-1546`, and conclusion
  `main.tex:1590-1596`.
- Evidence: Contribution 3 states “the geometric instances are not proved in
  the body of the paper”; the final appendix states the geometric inputs in
  the central sections “remain OPEN.”  Yet the abstract and conclusion claim
  those same inputs are discharged and infer a counterexample.
- Consequence: on the manuscript's face, its unconditional theorem has
  admitted unproved premises.  Calling the gap merely an unconstructed Lean
  inhabitant cannot resolve the separate sentence that the instances are not
  proved mathematically in the paper.
- Revision note: the working-tree edit changed the appendix's `remain OPEN`
  sentence, but Contribution 3 at `main.tex:147-149` still says the geometric
  instances are not proved in the body.  The underlying gaps are independently
  confirmed elsewhere in this ledger.

### F-005 — Default paper build is not reproducible in the supplied workspace

- Severity: **Minor**
- Status: **CONFIRMED (environment-specific)**
- Location: `README.md` Build section and `scripts/build_papers.sh`.
- Reproduction: `bash scripts/build_papers.sh` on 2026-09-04 compiled the
  English PDF through the final LaTeX pass, but exited 1 when copying to
  `output/pdf/spc4-t73-candidate.pdf`: `Permission denied`.  The final TeX log
  had no unresolved citation/reference warnings after its passes.
- Consequence: the TeX source compiles, but the documented default command
  does not complete on this checkout.  This does not affect mathematical
  correctness.

### F-006 — The machine-readable proof manifest classifies nine candidate-specific load-bearing bridges as unproved external parameters

- Severity: **Critical**
- Status: **CONFIRMED (repository evidence)**
- Locations: `audit/t73_proof_dependency_manifest.json`, dependencies
  `balanced_hattori_equivalence`, `actual_diagonal_class`, `nu0_binding`,
  `beta_psi_cocone`, `fixed_y_hj_basis`, `direct_q_sphere_cocone`,
  `phi_w_naturality`, `bpw_vertical_horizontal_trace`, and
  `bhpw_strict_functoriality`; design document
  `docs/superpowers/specs/2026-08-31-t73-counterexample-proof-consolidation-design.md`.
- Evidence: all nine entries have status `external_theorem` and Lean role
  `explicit_parameter`; their only `source_paths` entry is an internal design
  document, not a primary mathematical source or proof.  That design says the
  conclusion is *conditional* on a geometric balanced-Hattori theorem and a
  fixed-`Y` HJ/direct-`Q` theorem, and explicitly requires two independent
  reviews before even `CANDIDATE_PROOF_INTERNALLY_CLOSED` status.
- Consequence: several premises needed to turn the finite cubic calculation
  into a functional on the genuine MWW quotient are recorded by the project's
  own dependency ledger as assumptions.  In particular, passing tests of the
  manifest can only confirm that the assumptions are listed; it cannot prove
  them.  The unconditional counterexample theorem is unsupported unless the
  manuscript supplies complete proofs of each bridge and the manifest is
  demonstrably stale.

### F-007 — The manuscript directly admits that the finite value 2624 is not yet identified with an MWW invariant

- Severity: **Critical**
- Status: **CONFIRMED (internal text)**
- Locations: `main.tex:368-390`, especially Proposition `prop:scope` and its
  purported proof; compare abstract `main.tex:82-83`, Diagram (28) and
  `main.tex:1315-1326`.
- Evidence: the finite-computation section says 2624 “is presently only the
  value of this geometry-bound Burau computation; it is not identified with
  an MWW divided cubic.”  The proof of Proposition `prop:scope` then says C
  “would identify it” and that this remains `OPEN`.  Later sections simply
  state that the identification and quotient descent hold.
- Consequence: without the open comparison, 2624 is only a number extracted
  from an auxiliary Burau model.  It supplies neither a linear functional on
  the genuine skein-lasagna quotient nor a nonzero four-manifold class, so the
  central obstruction argument does not start.
- Revision note: the working copy changed “would identify ... remain OPEN” to
  “identify” without adding the missing functor/naturality construction.
  F-201--F-203 establish the substantive gap against the cited primary sources.

### F-008 — The advertised “claim boundary” and “premise audit” checks are textual/self-attestation checks, not correctness checks

- Severity: **Major**
- Status: **CONFIRMED (code inspection and replay)**
- Locations: `scripts/check_t73_claim_boundary.py` and
  `scripts/audit_t73_premises.py`.
- Evidence: the claim-boundary script only requires/rejects literal substrings
  in `main.tex`; it never parses or validates a proof.  The premise script
  derives `proved: true` primarily from status strings and Boolean fields in
  committed JSON certificates, plus literal `| ... | **PASS**` markers in an
  internal Markdown completion audit.  It then compares its regenerated JSON
  with the committed JSON.  Running them printed
  `UNCONDITIONAL_PAPER_LEAN_PARTIAL` and `MATHEMATICAL_PASS_LEAN_PARTIAL`, but
  those outputs follow from the asserted markers rather than an independent
  proof of the geometric or analytic semantics.
- Consequence: these commands can enforce consistency of repository labels,
  but they cannot be cited as evidence that P0/C/S/E13 are mathematically
  true.  Any downstream document treating `PASS` as independent verification
  is circular.

### F-009 — The repository's geometric-evidence availability checker finds none of its 13 registered artifacts

- Severity: **Major (reproducibility/evidence provenance)**
- Status: **CONFIRMED on current checkout**
- Locations: `scripts/check_geometric_evidence.py`,
  `audit/geometric_evidence_manifest.json`, and the README “public
  availability check.”
- Reproduction: `python3 -B scripts/check_geometric_evidence.py` exited 1 and
  reported `SUMMARY=0/13 geometric witness artifacts available and
  hash-matched`, including missing P0 builder/input/full PD/cut/support/normal
  field/collar braid, P1 actual cable/Hattori movie, and all three P2 sphere
  artifacts.
- Consequence: the historical evidence route registered by this manifest is
  unreproducible here.  The repository says a Johnson route supersedes these
  artifacts, so absence alone does not refute that replacement; however it
  prevents this advertised check from corroborating the manuscript and makes
  the replacement's independent provenance especially important.

### F-010 — The P0 “PASS” certificate does not place its model ball or cancellations in the actual 4-manifold boundary

- Severity: **Critical**
- Status: **CONFIRMED by the repository's controlling premise-status note**
- Location: `docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md:23-33`.
- Evidence: after describing a triangulated cube, model strands, and local
  intersection-one movies, the note explicitly says the cube is *not* a
  separately certified subset `B ⊂ ∂W_2`; the cancellation movies are local
  models in `R^3` plus word identities.  It also leaves the
  Euclidean/mapping-torus identification open at line 69.
- Consequence: a model braid in an abstract cube and local cancellation
  templates do not prove that the same framed objects occur simultaneously in
  the boundary of the asserted handle decomposition.  This is precisely the
  ambient-geometric bridge required by P0, so the P0 certificate's `PASS`
  label overstates what its recorded object proves.

### F-011 — The C certificate expressly does not construct the actual cut-link isotopy or chain-level complex it needs

- Severity: **Critical**
- Status: **CONFIRMED by the repository's controlling premise-status note**
- Location: `docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md:35-43`.
- Evidence: the note says the C objects are “not an isotopy of a cut link in
  `∂W_2`” and “not a chain-level Blanchet--Khovanov complex of the actual W2
  cut.”  What is checked is a product-normal translate in the abstract P0
  cube, counts, support cubes, and a Lean reduction.
- Consequence: these finite objects do not establish the categorical
  identification claimed in `lem:C1`, Diagram (28), or the MWW comparison.
  Without an actual cut-link/chain-map bridge, the Burau row is not shown to be
  a functional on the genuine lasagna module.

### F-012 — The S and P3 certificates expressly omit the actual `∂W2`/4-dimensional `W2` movie and a triangulated `W3`

- Severity: **Critical**
- Status: **CONFIRMED by the repository's controlling premise-status note**
- Location: `docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md:45-63`.
- Evidence: the note says S is not an identification with the relevant
  `∂W_2` and not a triangulated four-dimensional `W2` lasagna movie.  It says
  P3 is not a triangulation of a four-dimensional `W3`, and that the P3
  certificate itself does not identify `X_J` with `Σ_A^0`.
- Consequence: abstract belt cubes, dual loops, counit labels, and handle-count
  records do not prove that the actual MWW three-/four-handle maps have the
  asserted geometry.  The survival of the class through S/P3 and its ownership
  by the Cappell--Shaneson manifold therefore remain unsupported.

### F-013 — The repository's detailed candidate-proof document explicitly says the needed comparison theorem and candidate identifications are absent

- Severity: **Critical**
- Status: **CONFIRMED (internal proof-status document)**
- Location: `docs/proofs/T73_SPC4_COUNTEREXAMPLE_CANDIDATE_PROOF.md:15-45,
  925-969`.
- Evidence: the document states that it proves only a conditional implication.
  Its dependency table leaves the actual framed lift, sphere replacement,
  complete quotient, and candidate-specific E11--E13 bridges open or partial.
  Its closing status says the public tree lacks the geometric inputs and “does
  not contain a comparison theorem identifying the truncated Burau cubic with
  an MWW skein-lasagna evaluation.”
- Consequence: this is a direct repository-level admission that the exact
  proof chain required by `thm:joined` is incomplete.  Later `PASS` strings do
  not themselves fill the absent mathematical constructions.

### F-014 — The dated premise-status note and current premise-audit JSON contradict each other about the theorem's status

- Severity: **Major (audit integrity)**
- Status: **CONFIRMED**
- Locations: `docs/proofs/T73_GEOMETRIC_PREMISE_STATUS_20260903.md:77-94`
  and current `audit/t73_premise_audit.json`.
- Evidence: the dated note says the counterexample is open, the JSON has
  `overall=OPEN`, and `counterexample_claim_proved=false`.  The current JSON
  instead has `overall=PASS_MATHEMATICAL_LEAN_PARTIAL` and
  `counterexample_claim_proved=true`, with different listed certificate
  digests.  The current generator merely regenerates the latter labels from
  committed status fields (F-008).
- Consequence: the repository lacks a coherent, append-only provenance trail
  explaining why the explicitly identified geometric gaps became proofs.
  Therefore current PASS metadata cannot be trusted as independent evidence;
  the underlying constructions must be reviewed from first principles.

### F-015 — The conditional theorem was changed to an unconditional counterexample by relabelling status text, without adding a proof of the open geometry

- Severity: **Critical**
- Status: **CONFIRMED by git history**
- Location: commit `6e6d6ef363aa3328e8c131ce154cc4e171332235`
  (“State the unconditional paper theorem with partial Lean scope”), especially
  diffs to `main.tex`, `audit/t73_premise_audit.json`,
  `scripts/audit_t73_premises.py`, and `scripts/check_t73_claim_boundary.py`.
- Evidence: immediately before this commit, `thm:joined` was explicitly
  conditional, its proof said P0--P2 remained open, and the audit reported
  `overall=OPEN`, `counterexample_claim_proved=false`.  The commit replaced
  that text with an unconditional theorem and changed the scripts' expected
  strings/Boolean constants to `PASS...`/`true`.  Its `main.tex` diff added no
  new construction or proof of P0, C, S, or the Burau--MWW bridge; indeed all
  earlier `remain \Open` admissions stayed in the resulting manuscript.
- Consequence: the change in claimed theorem status was not caused by new
  mathematical evidence in that commit.  Tests now pass because their required
  labels were changed in the same commit.  This is decisive evidence that the
  unconditional conclusion is an unsupported status promotion, not the output
  of a completed proof chain.

### F-016 — A concurrent working-tree edit again removes `OPEN` labels without adding the missing mathematical constructions

- Severity: **Major (audit/revision integrity)**
- Status: **CONFIRMED by working-tree diff at 2026-09-04 23:11 +08:00**
- Location: uncommitted changes to `paper/spc4-t73-candidate/main.tex`
  relative to `HEAD` (`d7bbff8`).
- Evidence: 24 lines were added and 16 removed.  The edit replaces the P0/C/S
  proof sentences and the computation/appendix `OPEN` sentences with prose
  saying later sections close them.  It adds no definition of the coefficient
  shadow, no BPW/BHPW/MWW action diagrams, no global PL homeomorphism check,
  no actual `W2`/`W3` triangulation, and no ambient Kirby equivalence.  The
  source and verifier defects F-102--F-107 and F-201--F-204 are untouched.
- Consequence: the current manuscript has fewer explicit self-contradictions
  than the starting snapshot, but its proof chain remains incomplete.  This
  audit preserves both states: findings based on the starting snapshot are
  marked with revision notes, while substantive findings are evaluated
  against the current working copy.

### F-017 — Paper now distinguishes executable certificates from their mathematical interpretation

- Severity: **Remediation**
- Status: **RESOLVED at the exposition/claim-boundary level; mathematical bridges remain OPEN**
- Location: new `main.tex` Section `sec:certificate-scope`, revised abstract,
  `thm:joined`, P0/C/S/P3 statements, certificate propositions, final
  identifications, and conclusion.
- Change: the paper now lists, for P0, C, S, P3 and E13, the exact verifier
  entry points, the finite predicates they reconstruct, and the additional
  ambient/categorical theorem required to interpret each certificate.  The
  top-level obstruction is stated conditionally rather than treating status
  strings as proofs.  The Lean wording now says it verifies the imported
  arithmetic `(-2)^3(-328)=2624`, not the long braid calculation.
- Fresh replay: P0 and C1/C2 passed; relative S passed; standard-sphere S
  failed `--check` solely because its committed upstream C/C1/C2 digests are
  stale; P3 reported E11/E12 PASS and E13 PARTIAL; E13 wrappers printed
  `IDENTIFIED_WITH_SIGMA=True` while the final wrapper also reported
  `MISSING_MAPS=1`.  The paper records these outputs without promoting them
  beyond their implemented contracts.
- Remaining impact: F-102--F-107 and F-201--F-204 are not mathematically
  resolved.  A future unconditional theorem still requires the actual global
  PL/Kirby and MWW comparison arguments.

### F-108 — The manuscript cites the wrong Cappell--Shaneson paper as the original source of Iwaki Proposition 2.1

- Severity: **Minor for truth; Major for the requested proof provenance**
- Status: **CONFIRMED**
- Locations: `main.tex:174--176`; `sec-published-results.tex:198--210`;
  bibliography entry `CappellShaneson1976` in `references.bib:12--22`.
- Source-chain evidence: Iwaki's own Proposition 2.1 cites Cappell--Shaneson,
  *There exist inequivalent knots with the same complement*, Ann. of Math.
  103 (1976), Section 3, together with Issa's 2017 thesis, Proposition 3.1.
  The present bibliography instead cites Cappell--Shaneson, *Some new
  four-manifolds*, Ann. of Math. 104 (1976), 61--72. These are distinct
  articles (DOIs 10.2307/1970942 and 10.2307/1971056 respectively).
- Mathematical assessment: the criterion as quoted is still correct and is
  stated directly by the published Iwaki source. The defect is a false
  original-source trail, not evidence against Iwaki's proposition.
- Required correction: add/cite the Annals 103 article (and preferably Issa
  Proposition 3.1 if relying on Iwaki's stated chain); do not label the Annals
  104 article as the original cited source for this proposition.

### F-109 — Iwaki confirms the standard form and table entry, but double-underlines the trace-73 candidate as unresolved

- Severity: **Minor (positive source verification and caveat)**
- Status: **CONFIRMED**
- Locations: `main.tex:151--159` and `main.tex:183--186`.
- Source-chain evidence: Iwaki Definition 2.5 defines
  \(X_{c,d,n}=\left[\begin{smallmatrix}0&a&b\\0&c&d\\1&0&n-c\end{smallmatrix}\right]\)
  with \(a,b\) fixed by the two determinant conditions. Substitution of
  \((c,d,n)=(41,189,73)\) gives exactly the manuscript's entries
  \(a=269,b=1240,n-c=32\). Iwaki's representative table for trace 73 lists
  `(41,189,73)` and double-underlines it.
- Crucial caveat: immediately before the table analysis Iwaki explains that a
  double underline means it is *uncertain* whether the special representative
  is equivalent to the standard class. Thus the table is reliable evidence
  for the parameterization, but affirmatively not a standardness or
  exoticness theorem. The manuscript states this caveat correctly.
- Source reliability: Iwaki says the trace 70--78 representatives were
  calculated with a displayed MAGMA procedure. This computational provenance
  is not needed for the present homotopy-sphere fact because the displayed
  matrix's two determinants are checked directly.

### F-110 — Johnson's theorem provides mapping-class generators, not the repository's relative PL representatives

- Severity: **Major**
- Status: **CONFIRMED (source/application scope mismatch)**
- Locations: `main.tex:626--654`, the 93-factor construction through
  `main.tex:898`, and Lemma `P0a` at `main.tex:924--947`.
- Primary-source statement: Johnson, Theorem 1, proves that
  \(\mathrm{Mod}(T^3,\Sigma)\) is generated by six automorphisms
  \(\alpha_{ij}\) plus \(\sigma,\tau\). The six \(\alpha_{ij}\) induce the
  elementary transvections generating \(SL(3,\mathbb Z)\); the other two are
  ambient-isotopy-trivial. This establishes existence of splitting-preserving
  mapping classes representing any product of elementary matrices.
- What it does not supply: Johnson does not give the manuscript's rational
  tetrahedral maps, support prisms, identity on a chosen section ball,
  constant normal fields, or the exact 93-factor relative isotopies and
  attaching-link transport. Nor does equality of products in
  \(SL(3,\mathbb Z)\) identify particular representatives relative to the
  protected ball.
- Dependency impact: the source is trustworthy for the search space and
  induced homology action, but all candidate-specific ambient claims still
  require the missing global PL and relative-isotopy verification in F-106.

### F-111 — Aitchison--Rubinstein proves the general handle recipe only under genuine embedded/symmetric geometric data

- Severity: **Major**
- Status: **CONFIRMED (source theorem trustworthy; candidate application unproved)**
- Locations: `main.tex:441--494`, `main.tex:513--555`, and
  `main.tex:557--577`.
- Primary-source chain: Aitchison--Rubinstein pp. 5--8 construct the mapping
  torus using cut spine arcs \(C_i-(R-\operatorname{int}R')\), disjoint cone
  disks, mapping-handle arcs, and simultaneously constructed framing annuli.
  Their p.7 argument uses actual attaching spheres meeting actual belt spheres
  once geometrically to cancel complementary 1/2 pairs. Section 3, Lemma 3.1,
  shows that a CS matrix in their canonical form has a linear torus map
  isotopic to a *symmetric* diffeomorphism preserving the chosen Heegaard
  structure; Lemma 3.2 supplies minimal straightening near the fixed point.
- Scope caveat: this source validates the recipe once those geometric objects
  exist. It does not say that a free-group word, transvection product, railroad
  projection, or collection of owner hashes is the required embedded framed
  link. In particular it supplies no theorem converting the repository's
  locally checked 93 PL factors into all of the pairwise-disjoint disks,
  annuli, mapping-handle arcs, and global ambient isotopies used in P0.
- Dependency impact: AR is not a flawed foundation here; the failure is the
  manuscript's unproved candidate-specific realization of its hypotheses.

### F-112 — Kirby's calculus supports the slide/framing rule but not the asserted 1519-band movie

- Severity: **Major**
- Status: **CONFIRMED (source theorem trustworthy; application unproved)**
- Locations: railroad linking Lemma `P0d-link`, `main.tex:910--920`, and the
  cancellation discussion `main.tex:557--577`.
- Primary-source scope: Kirby's 1978 paper defines framed links in \(S^3\),
  their 2-handlebodies, and the handle-slide move with the corresponding
  framing/linking-matrix update. This is the standard justification for
  band-summing an attaching component with a framed parallel and updating
  self-framing by the relevant linking terms.
- Gap: the equality \(\operatorname{lk}(m_2,r_{yz})=0\) is one scalar in one
  terminal projection. It does not show that every one of the six plus 1513
  selected bands is embedded and mutually schedulable, carries the declared
  parallel framing, has no unintended intersections, or realizes the stated
  whole-link ambient handle slides. Kirby's theorem classifies legitimate
  moves; it does not certify that an encoded move list is legitimate.
- Dependency impact: the citation cannot fill the certificate-semantic gap in
  F-107 or establish `thm:P0discharge`.

### F-113 — Laudenbach--Po\'enaru gives uniqueness of the upper handles only after the lower handlebody/boundary hypotheses are proved

- Severity: **Major**
- Status: **CONFIRMED (source theorem trustworthy; hypotheses missing here)**
- Locations: implicit through the AR construction cited at `main.tex:443--494`
  and the P3 assertions at `main.tex:279--303`, `main.tex:1535--1546`.
- Primary-source chain: Laudenbach--Po\'enaru Theorem A/A' says that gluing two
  4-dimensional 1-handlebodies along an arbitrary boundary diffeomorphism, or
  equivalently attaching the complete set of 3-handles and a 4-handle under
  its stated boundary hypothesis, gives \(S^4\). Its proof reduces boundary
  diffeomorphisms via free-group automorphisms and a theorem on embedded
  2-spheres; modern independent proofs restate the equivalent extension
  theorem: every diffeomorphism of \(\#^p(S^1\times S^2)\) extends over
  \(\natural^p(S^1\times B^3)\).
- Caveat: this does justify the familiar statement that, once a valid 0/1/2
  handlebody of a closed 4-manifold and the appropriate spherical boundary
  data are fixed, upper-handle gluing ambiguity is inessential. It does not
  recognize an arbitrary encoded boundary as \(S^3\), construct the required
  complete 3-handle system, or identify one lower handlebody with another.
  The original theorem's hypotheses are substantive; its own Lemma 5 warns
  that the relevant boundary diffeomorphism need not extend over the lower
  piece.
- Dependency impact: LP cannot rescue P3/E13 before P0, the actual
  \(\partial W_2\), and the complete attaching sphere system are independently
  established. No published erratum undermining the extension theorem was
  located; recent papers explicitly give new proofs of it.

### F-114 — The proof chain behind Iwaki Proposition 2.1 is noncircular and independently checkable

- Severity: **Minor (positive foundational verification)**
- Status: **CONFIRMED**
- Locations: `main.tex:164--179`, `sec-published-results.tex:198--210`, and
  Corollary `cor:homotopy-sphere` in `sec-finite-details.tex:76--90`.
- Proof-chain check: for the mapping torus, van Kampen gives the semidirect
  product presentation \(\mathbb Z^3\rtimes_A\mathbb Z\). Surgery on the
  section kills the circle generator; the remaining abelian generators are
  quotiented by \(A-I\), so the fundamental group is trivial exactly when
  \(A-I\) is unimodular. The Wang sequence for the torus bundle, followed by
  Mayer--Vietoris for replacing \(S^1\times D^3\) by
  \(D^2\times S^2\), gives integral homology of \(S^4\) under the same
  condition. A simply connected CW homology 4-sphere is homotopy equivalent
  to \(S^4\) by Hurewicz and Whitehead. Conversely, vanishing \(H_1\) forces
  `coker(A-I)=0`, hence \(\det(A-I)=\pm1\). The two framing parities do not
  alter these fundamental-group or homology calculations.
- Assessment: no smooth 4-dimensional Poincare assertion is used in this
  chain, so the homotopy-sphere criterion is not circular. This confirms the
  foundation for the *standard CS surgery object* while leaving the distinct
  `X_J` identification failure untouched.

## Source verification ledger

Primary sources and precise theorem statements will be entered here, including
the hypotheses used by the paper and whether the cited result actually supplies
them.

Topology-source checks completed 2026-09-04:

| Source | Result checked | Audit conclusion |
|---|---|---|
| Kazunori Iwaki, *Infinite families of standard Cappell--Shaneson spheres*, arXiv:2404.05096, Proposition 2.1 | Mapping-torus section surgery is a homotopy sphere iff `det(A-I)=+-1` | **MATCHES**, but only for the actual CS surgery object; it supplies no `X_J` identification (F-100). |
| I. R. Aitchison--J. H. Rubinstein, *Fibered knots and involutions on homotopy spheres*, Contemp. Math. 35 (1984), pp. 5--12 | Handle construction from a Heegaard-preserving representative; p.7 complementary handles | **PARTIAL SUPPORT ONLY**. The source supports the standard AR construction and geometric 1/2 (and 2/3) cancellation rules. It does not validate the repository's Johnson PL map, 1519 bands, railroad projection, or E13 chain (F-104, F-107). |
| Cappell--Shaneson, *Some new four-manifolds*, Ann. Math. 104 (1976), 61--72 | Original family/context | Bibliographic record confirmed at the Annals/DOI landing page. The manuscript uses Iwaki Proposition 2.1 for the precise short criterion. |

### F-200 — The quoted MWW 2/3/4-handle formulas are substantially accurate

- Severity: **Minor (positive verification / wording qualification)**
- Status: **CONFIRMED**
- Locations: `main.tex:399-429`, `main.tex:1281-1316`,
  `main.tex:1403-1434`, and `main.tex:1535-1546`.
- Primary-source evidence: Manolescu--Walker--Wedrich,
  *Skein lasagna modules and handle decompositions*,
  [arXiv:2206.04616](https://arxiv.org/abs/2206.04616), Theorem 3.2
  (paper p. 9) gives the cabled 2-handle quotient with the beta and psi
  relations of Definition 3.1; Proposition 3.4 and Corollary 3.5 (p. 10)
  say respectively that an empty-link 4-handle map is an isomorphism and
  that \(\mathcal S^N_0(S^4)\cong\mathbb Z\) in bidegree zero; Theorem 3.7
  (pp. 11--12) gives the 3-handle coequalizer; Example 3.8 (pp. 12--13)
  gives, for \(N=2\), the relations “one-dotted essential sphere \(=1\)”
  and “undotted essential sphere \(=0\)”; Theorem 3.10 (pp. 14--15)
  iterates those relations; Theorem 4.7 (p. 18) is the one-handle
  coinvariant formula over a field.
- Qualification: Proposition 3.4 is stated only for the **empty boundary
  link**, exactly the case ultimately used here.  Theorem 4.7 supplies a
  quotient of a direct sum of link homologies and its gluing actions; it does
  not by itself construct the paper's later quantum endpoint detector.
- Proof-chain impact: the abstract handle-calculus skeleton and the
  concentration of the standard-sphere module are sourced correctly.  This
  positive verification does not validate the novel C or S comparison maps.

### F-201 — The central quantum “shadow” map is not supplied by BPW/BHPW

- Severity: **Critical**
- Status: **CONFIRMED (citation mismatch and missing construction)**
- Locations: `main.tex:1057-1099` (especially (17) and
  `eq:actualShadow`), propagated through `main.tex:1145-1166`,
  `main.tex:1281-1319`, and Theorem `thm:Cdischarge`.
- Claim audited: BPW's “canonical vertical-to-horizontal functor” and BHPW
  strict functoriality allegedly give a grading-preserving map
  \[
  q\operatorname{Tr}(\mathcal C;M_R)\longrightarrow
  \operatorname{Hom}_{R_q}(E_{86},E_{88})
  \]
  for the **actual MWW coefficient bimodule**, compatible with both gluing
  actions and the later counits.
- Primary-source evidence: BPW,
  *Quantum Link Homology via Trace Functor I*,
  [arXiv:1605.03523](https://arxiv.org/abs/1605.03523), Theorem E
  (intro p. 9; proof in Section 7.2, pp. 71--73), constructs an action of the
  oriented tangle category on quantum annular homology of oriented cablings
  of a **fixed framed annular link** and proves a Jones skein relation.  Its
  general trace theory concerns horizontal traces and quantum Hochschild
  homology of Chen--Khovanov bimodules; it does not state the displayed
  coefficient-to-\(\operatorname{Hom}(E_{86},E_{88})\) map.  BHPW,
  *On the functoriality of \(\mathfrak{sl}_2\) tangle homology*,
  [arXiv:1903.12194](https://arxiv.org/abs/1903.12194), Corollaries E--F
  (pp. 6--7) identify a Chern character for the relevant arc algebras under
  a flatness hypothesis and produce strictly functorial **annular link
  homology**; Theorem 4.6 gives strict functoriality of a tangle complex.
  None of these results identifies the paper's geometrically defined
  \(M_R\), its coefficient trace, or its two MWW module actions with the
  stated endpoint Hom-space.
- Evidence in the manuscript: Lemma `lem:C1` proves the identification only
  by reasserting that the 44 ribbons and 227 circles “give” it and then
  invokes a Lean proof of an abstract representable \(HH_0\) reduction.
  The manuscript supplies no functor, no object-by-object comparison with
  the BHPW arc/web categories, no natural transformation for MWW gluing, and
  no proof that the chosen Chern/decategorification map has the claimed
  domain, codomain, or grading.
- Consequence: \(D_h\), hence \(D_3\), is not yet shown to be a functional
  on the actual MWW coefficient quotient.  The numerical Burau coefficient
  2624 therefore does not presently produce a skein-lasagna class.  This
  breaks the main proof before the 2-handle quotient.
- Required resolution: explicitly construct the coefficient shadow in the
  precise MWW/BHPW categories, prove both action squares and all grading
  shifts, and prove that its specialization is the ordinary MWW
  \(HH_0\), rather than citing trace theory whose stated object is different.

### F-202 — BHPW strict functoriality does not by itself prove equation (17)

- Severity: **Major**
- Status: **CONFIRMED (unsupported inference)**
- Locations: `main.tex:1015-1051`, used in Lemma `lem:C1` and all of C.
- Primary-source evidence: BHPW
  [arXiv:1903.12194](https://arxiv.org/abs/1903.12194), Theorem 4.6, proves
  that their foam-model tangle complex is invariant and strictly functorial
  for tangle cobordisms; Theorems A--D compare specific web/foam and
  Bar--Natan/Chen--Khovanov constructions.  Strictness removes a projective
  sign **after the relevant objects and cobordisms have been placed in that
  theory**.  It does not assert that the two complexes called \(C_R\) and
  \(C\) in (17) are related by the displayed Hattori isomorphism, nor that a
  geometric exchange of the paper's two collars becomes literally the same
  foam under the chosen MWW conventions.
- Consequence: even if the underlying link-homology vector spaces happen to
  be isomorphic by pivotal duality and Kunneth, naturality with respect to
  both coefficient actions is extra data.  A dimension or link-isotopy
  comparison is insufficient for descent to Hochschild coinvariants.
- Required resolution: give the actual chain maps \(H_{T,T'}\), state all
  orientation/pivotal conventions, and verify the left and right action
  diagrams inside a single sourced strict model before passing to homology.

### F-203 — The use of BPW Theorem E for every MWW beta relation is not justified

- Severity: **Major**
- Status: **OPEN**
- Locations: `main.tex:1182-1203` and `main.tex:1243-1257`.
- Primary-source evidence: BPW Theorem E
  [arXiv:1605.03523](https://arxiv.org/abs/1605.03523) acts on oriented
  cablings of a framed annular link.  In BPW's original proof the action is
  initially projective/up to powers of \(q\) (and characteristic 2 is used
  for the sign issue); BHPW later supplies a strict annular theory.  MWW
  [arXiv:2206.04616](https://arxiv.org/abs/2206.04616), Remark 3.3 (p. 9),
  explicitly says that symmetric-group factorization for the anti-parallel
  braid actions relevant to the lasagna quotient is not known.
- Gap: the manuscript says it avoids symmetric-group factorization, which
  is logically possible, but it still must identify **each** MWW beta map at
  every cable state with the BPW/BHPW endpoint action under the unproved C1
  comparison.  “Apply the P0 collar motion simultaneously” is not that
  verification.  In particular, mixed orientations, framing/writhe shifts,
  pivotal charts, and compatibility of the Reynolds averages with the
  actual beta maps are not derived from the cited theorem.
- Proof-chain impact: equations (26) and therefore descent through MWW
  Theorem 3.2 remain unproved even assuming the scalar calculation.

### F-204 — The essential-sphere endpoint factorization is a new unsupported theorem

- Severity: **Critical**
- Status: **CONFIRMED (missing proof at the claimed interface)**
- Locations: `main.tex:1455-1509` (Lemma `lem:Sendpoint`), the endpoint
  square at `main.tex:1511-1522`, and Theorem `thm:Sdischarge`.
- What MWW actually proves: Theorem 3.7 of
  [arXiv:2206.04616](https://arxiv.org/abs/2206.04616) identifies a
  3-handle map with the coequalizer of the two hemisphere maps.  Example 3.8
  and Remark 3.9 identify the local essential-sphere relations.  The proof of
  Theorem 3.10 describes the nontrivial hemisphere by a punctured attaching
  surface plus restored 2-handle cores.  These results do **not** say that
  the paper's Burau/trace detector factors as
  \(\operatorname{Id}_{\rm old}\otimes\Delta^{b-1}\), or that all mixed
  movie data can be pushed to endpoint permutations without changing its
  cubic coefficient.
- Defect in the manuscript proof: disjointness of the sphere and detector
  surfaces only separates their intrinsic Morse critical points.  It does
  not, without a proved monoidal naturality/interchange comparison in the
  actual coefficient category, identify the induced global MWW map with a
  tensor product.  The claim that every mixed event is an endpoint braid and
  that all such braids cancel by simultaneous conjugation is asserted, not
  established.  BHPW strict functoriality fixes signs for its tangle theory;
  it does not supply this factorization or its compatibility with the MWW
  2-handle quotient.
- Internal admission: the proof itself says at `main.tex:1506-1508` that the
  result “remains at the stated claim boundary until the complete MWW map is
  packaged in the global interface,” but `main.tex:1524-1533` immediately
  declares S discharged without providing that package.
- Consequence: the detector is not proved to annihilate the 3-handle
  coequalizer relations.  Thus no nonzero class is established after the
  3-handles, independently of all topology/P0 issues.
- Required resolution: construct and check the full MWW hemisphere maps on
  every relevant cable summand, including quotient compatibility, relative
  homology summands, gradings, signs, and the interchanges with the detector.

### F-205 — Sphere-system kernel invariance is plausible, but its naturality input should be cited precisely

- Severity: **Minor**
- Status: **CONFIRMED modulo standard relative handle calculus**
- Locations: `main.tex:1347-1378` and `main.tex:1436-1450`.
- Evidence: the intrinsic lasagna cobordism maps in MWW obey the composition
  law used in the proof of their Theorem 3.7
  [arXiv:2206.04616](https://arxiv.org/abs/2206.04616), pp. 10--12.  If a
  3--3 handle slide gives a diffeomorphism of the resulting handle
  cobordisms relative to the incoming boundary, naturality indeed yields
  postcomposition by a target isomorphism and hence equal kernels.
- Qualification: this only transports the **kernel**.  It does not keep the
  paper's embedded detector cube fixed under the closed-manifold isotopy and
  does not prove Lemma `lem:Sendpoint` for the replacement system.  The
  manuscript correctly tries to separate these issues, but later conflates
  kernel replacement with completion of S.

### F-206 — The standard-sphere coefficient ring is stated inconsistently

- Severity: **Minor**
- Status: **CONFIRMED**
- Locations: `main.tex:421-423`, `main.tex:1086-1099`, and the later use of
  rational-valued detectors.
- Evidence: MWW Corollary 3.5
  [arXiv:2206.04616](https://arxiv.org/abs/2206.04616), p. 10, states
  \(\mathcal S^N_0(S^4)\cong\mathbb Z\) in bidegree zero for the integral
  theory.  After the manuscript changes coefficients to \(\mathbb Q\), the
  corresponding statement is \(\mathbb Q\), not \(\mathbb Z\).
- Consequence: the degree-494 vanishing survives base change, so this does
  not repair or destroy the obstruction.  The coefficient convention must
  nevertheless be made explicit throughout the comparison.

### F-207 — Two bibliography entries omit existing journal publications

- Severity: **Minor**
- Status: **CONFIRMED**
- Location: `paper/spc4-t73-candidate/references.bib`, entries
  `MorrisonWalkerWedrich2019` and `ManolescuNeithalath2020`.
- Evidence: Morrison--Walker--Wedrich was published as *Geometry & Topology*
  **26** (2022), no. 8, 3367--3420, DOI
  [10.2140/gt.2022.26.3367](https://doi.org/10.2140/gt.2022.26.3367).
  Manolescu--Neithalath was published as *Journal für die reine und
  angewandte Mathematik* **788** (2022), 37--76, DOI
  [10.1515/crelle-2022-0021](https://doi.org/10.1515/crelle-2022-0021).
  Both are still entered as `@misc` with only their original arXiv year.
- Consequence: no mathematical effect, but the audit trail should cite the
  peer-reviewed versions (and any published errata) rather than silently
  treating them as unpublished preprints.

### F-208 — Second-pass audit found no defect in the cited MWW handle theorems themselves

- Severity: **Minor (positive source-chain verification)**
- Status: **CONFIRMED within the published skein-lasagna framework**
- Scope: MWW Theorems 3.2, 3.7, 3.10, 4.7; Proposition 3.4; and
  Corollary 3.5, all in
  [arXiv:2206.04616](https://arxiv.org/abs/2206.04616).
- Proof-chain review:
  - Theorem 3.2 constructs the forward map by adjoining core-parallel
    2-handle disks and the inverse by pushing a filling transverse to the
    cocores.  Its well-definedness refers to the detailed model proof of
    Manolescu--Neithalath Theorem 1.1,
    [arXiv:2009.08520](https://arxiv.org/abs/2009.08520), pp. 10--12.
    That proof separately analyzes regular intervals of a generic cocore
    intersection (the beta relation) and birth/death critical values (the
    dotted psi relations).  The generalization from a 0-handle to arbitrary
    \(W\) is local and does not add a hidden algebraic hypothesis.
  - Proposition 3.4 cites Manolescu--Neithalath Proposition 2.1 (p. 6).
    Surjectivity for a 3-handle is ordinary transversality of a surface away
    from its 1-dimensional cocore; injectivity for a 4-handle uses the same
    argument in a one-parameter family, whose dimension is still below the
    cocore.  Corollary 3.5 then combines 4-handle invariance with the empty
    Khovanov--Rozansky group of \(B^4\).  No questionable external
    classification theorem enters.
  - Theorem 3.7 gives a direct inverse to the 3-handle map by pushing fillings
    off the 1-dimensional cocore.  The only new event in a generic isotopy is
    a cocore crossing, which exchanges the two hemispheres; Lemma 2.1 permits
    all ball replacements to be kept away from the handle.  This proves
    exactly the coequalizer statement, not the candidate's later endpoint
    factorization.
  - Theorem 3.10 is a formal iteration of Theorems 3.2 and 3.7 plus
    Proposition 3.4.  Its local relations (14)--(15) follow from equation
    (11) for the standard cap and equation (13) for the punctured attaching
    sphere.  No extra claim resembling Lemma `lem:Sendpoint` occurs.
  - Theorem 4.7 assumes coefficients in a **field**.  Section 4 explains why:
    Kunneth has no Tor terms and mirror homology is the linear dual without
    Ext terms.  Lemmas 4.4 and 4.6 give surjectivity and the two category
    actions; the proof identifies the kernel by factoring isotopies near and
    away from cocores.  The candidate's use of \(\mathbb Q\) meets the field
    hypothesis.
- Assessment: these proofs are concise, especially the isotopy-factorization
  argument in Theorem 4.7, but they are internally coherent and supported by
  the intrinsic local definition.  I found no published correction that
  invalidates these handle statements.  The candidate's failures remain
  application/interface gaps (F-201--F-204), not evidence that MWW's
  theorems are false.

### F-209 — A 2026 Manolescu--Neithalath erratum changes grading normalizations relevant to the candidate's comparison

- Severity: **Major**
- Status: **OPEN (impact on degree-494 comparison not audited by manuscript)**
- Locations: the source chain behind `main.tex:1014-1021`, the grading
  calculation at `main.tex:1109-1113`, mixed-orientation/writhe discussion at
  `main.tex:1124-1143`, and shifts in diagram (28), `main.tex:1293-1316`.
- Primary-source evidence: Manolescu--Neithalath,
  [*Errata to “Skein lasagna modules for 2-handlebodies”*](https://web.stanford.edu/~cm5/lasagna_errata.pdf),
  p. 1, says that some Section 2.1 normalizations are incorrect and corrects
  the rational comparison to
  \(\operatorname{KhR}_N(L)\otimes\mathbb Q\cong
  \operatorname{KhR}^{\mathbb Q}_N(L)\{-(N-1)w\}\), as well as the
  \(N=2\) conversion to ordinary Khovanov homology.  It also corrects
  Proposition 3.8's target from \(\operatorname{Kh}\) to
  \(\operatorname{KhR}_2\), while stating that the rest of that source paper
  is unaffected because it is formulated in \(\operatorname{KhR}_2\).
- Assessment of source theorem: the erratum does **not** undermine
  Manolescu--Neithalath Theorem 1.1 or Proposition 2.1, nor MWW's intrinsic
  handle formulas; those remain sound in their stated \(\operatorname{KhR}\)
  convention.
- Candidate-specific risk: the candidate compares MWW's intrinsic
  \(\operatorname{KhR}_2\) coefficient to BHPW/BPW foam, quantum-group and
  Burau models and asserts absolute shifts \(-44,+315,-4\) and total degree
  494.  It never cites or applies the corrected writhe normalization.  Writhe
  zero for one selected public word does not automatically settle all
  objects, mixed-orientation pivotal closures, or every cable state used in
  the descent.
- Proof-chain impact: until a convention table derives every shift using the
  corrected formula, the claim that the nonzero functional lies in the
  **absolute MWW quantum degree 494** is unverified.  This is separate from,
  and cumulative with, the missing coefficient map in F-201.

### F-210 — BPW 3.20/3.21 and BHPW 4.6 appear sound, but their hypotheses sharply limit the candidate application

- Severity: **Major (application caveat; positive source verification)**
- Status: **CONFIRMED**
- Locations: `main.tex:1046-1049`, `main.tex:1079-1086`,
  `main.tex:1189-1202`, and `main.tex:1495-1502`.
- BPW proof chain: Proposition 3.20 of
  [arXiv:1605.03523](https://arxiv.org/abs/1605.03523), pp. 34--35, says the
  quantum horizontal trace is the universal quantum preshadow **assuming
  left duals**, and is a shadow when right duals also exist.  Theorem 3.21 is
  the functoriality consequence for locally pregraded endobicategories with
  duals; its explicit construction is omitted because it is a verbatim
  deformation of Theorem 3.10.  The result follows formally from the proved
  universal property, and I found no flaw in that abstract implication.
- BHPW proof chain: Theorem 4.6 of
  [arXiv:1903.12194](https://arxiv.org/abs/1903.12194), pp. 25--26, derives
  strict functoriality of the foam tangle bracket from projective
  functoriality of the Bar--Natan bracket, strict functoriality for closed
  links, and closure of a tangle to a link; its comparison uses the local
  equivalence of foam and Bar--Natan categories.  This is a theorem about the
  homotopy type and maps of the specified tangle complex.  Remark 4.7
  immediately distinguishes the extension to arbitrary knotted webs/foams
  in four-dimensional space as conjectural.
- Candidate-specific missing hypotheses: the manuscript does not define a
  locally pregraded endobicategory-with-duals whose horizontal trace is its
  \(q\operatorname{Tr}(\mathcal C;M_R)\), nor a morphism of such
  endobicategories producing `eq:actualShadow`.  It also does not show that
  every exchanged-collar or essential-sphere movie is evaluated by BHPW's
  specific tangle complex rather than by the broader conjectural foam
  extension.  Thus the primary results themselves appear sound, while the
  manuscript has not met their categorical and geometric hypotheses.

### F-300 — The endpoint “derivation” hard-codes every pivotal coefficient

- Severity: **Critical**
- Status: **CONFIRMED (load-bearing input is assumed, not recomputed)**
- Locations: `main.tex:1120-1143`; `sec-finite-details.tex:9-26`;
  `scripts/build_t73_endpoint_transport.py:211-297`, especially lines
  238--262; `scripts/verify_t73_endpoint_transport.py:30-41,93-109`.
- Evidence: for each of the 88 physical endpoints the builder executes
  `pivotal_sign = 1` and `q_power = 0` (lines 239--240), then serializes those
  literals as the purported endpoint coefficient.  No BPW/BHPW formula is
  evaluated and neither orientation nor local pivotal data determines them.
  This conflicts with the paper's statement at `main.tex:1120-1122` that the
  monomial map and pivotal coefficients “are recomputed from these physical
  identifiers.”
- Mutation-test defect: `expect_fail` does not require a mutated pivotal sign
  to be rejected.  If the output merely differs from the baseline it returns
  the string `FAIL:P_changed` or `FAIL:derived_public_pairing_changed`
  (`verify_t73_endpoint_transport.py:37-40`), and the unit test accepts every
  string beginning with `FAIL`.  Thus “pivotal mutations fail” means only that
  the computation depends on the assumed sign, not that the baseline sign was
  verified.
- Proof-chain impact: the selected cup/cap and hence the scalar \(2624\) are
  sign- and coordinate-sensitive (the paper records a prior endpoint-indexing
  erratum).  Until all pivotal signs and powers are derived in the actual
  oriented BPW/BHPW model, the finite value is a conditional calculation for
  one chosen convention, not a verified value of the paper's geometric
  detector.  This independently reinforces F-201--F-203.
- Required resolution: implement the cited oriented-cabling/pivotal formulas
  from independently supplied orientation and framing data, remove the two
  literal assignments, and test against a separately derived small set of
  hand-checkable mixed-orientation examples.

### F-301 — Lean does not check the braid computation producing 2624

- Severity: **Major**
- Status: **CONFIRMED (formalization-scope overstatement)**
- Locations: `main.tex:1548-1554`; `Smooth4PC/T73Finite.lean:79-89`;
  `Smooth4PC/T73External.lean:15-34`; `Smooth4PC/T73Conditional.lean:5-51`.
- Evidence: Lean defines `cubicBase : Int := -328`,
  `substitutionLinear : Int := -2`, and `computedCubic` as their elementary
  product.  `computedCubic_eq_2624` proves only
  \((-2)^3(-328)=2624\) by `norm_num`.  There is no braid word, Burau matrix,
  endpoint convention, or certificate digest in the theorem's dependency
  chain.  The actual value is simply required again by the external field
  `ell0_x0 : ell0 x0 = computedCubic`.
- Proof-chain impact: `main.tex:1551-1552` says Lean “checks ... the
  geometry-bound Burau value 2624”; that is false in the ordinary meaning of
  “checks.”  Python recomputes the scalar, while Lean checks arithmetic on a
  manually transcribed base coefficient and proves a conditional theorem.
  This does not make the abstract Lean implication invalid, but it removes
  Lean as independent evidence for the computational detector.
- Required resolution: either narrow the prose to “Lean checks arithmetic on
  the imported coefficient -328” or formally reflect/replay the word,
  endpoint maps, and truncated Burau action (with a verified import boundary).

### F-302 — The advertised premise/claim audit is self-certification

- Severity: **Major**
- Status: **CONFIRMED**
- Locations: `scripts/audit_t73_premises.py:25-125,278-320`;
  `scripts/check_t73_claim_boundary.py:27-122`;
  `scripts/certify_t73_e12_s4.py:186-249`.
- Evidence: `audit_t73_premises.py` determines P0/C/S/E13 status largely by
  reading `verdict`, `status`, and desired boolean fields from repository JSON,
  plus checking that a completion Markdown file literally contains `PASS`.
  It then assigns `overall = PASS_MATHEMATICAL_LEAN_PARTIAL` and
  `counterexample_claim_proved = True` unconditionally at lines 281--283.
  Its `--check` mode only compares this regenerated JSON with the committed
  JSON.  `check_t73_claim_boundary.py` similarly checks that desired sentences
  and labels occur in TeX; it performs no mathematical validation.  As a
  concrete example, E12 assigns `s4_degree_494_zero: True`, `E12_status:
  PASS`, and `verdict: PASS`; its hash authenticates this generated assertion,
  not the cited external equivalences.
- Hash assessment: excluding `certificate_sha256` before hashing is standard
  and not circular cryptographically.  The logical circularity is that the
  same code emits the semantic status booleans, hashes them, and later treats
  their presence/hash linkage as proof.  SHA chains establish byte identity
  and freshness only.
- Proof-chain impact: the commands reporting
  `MATHEMATICAL_PASS_LEAN_PARTIAL` and
  `UNCONDITIONAL_PAPER_LEAN_PARTIAL` are not independent audit evidence and
  must not be used to discharge any premise in D-02--D-09.

### F-303 — The “no fake Lean inhabitant” gate is a brittle lexical blacklist

- Severity: **Minor**
- Status: **CONFIRMED tooling defect; current absence independently checked**
- Locations: `scripts/check_t73_external_geometry_boundary.py:13-39`;
  `tests/test_t73_external_geometry_boundary.py:11-18`.
- Evidence: the gate rejects only five exact substrings such as `instance
  ExternalGeometry` and `def t73ExternalGeometry`.  A differently named
  declaration with result type `ExternalGeometry`, qualified syntax, or many
  valid `noncomputable instance` spellings would evade it.  The test merely
  invokes this same lexical check.
- Current-tree result: a separate full-source search found no `axiom`,
  `sorry`, `admit`, `opaque`, `unsafe`, `extern`, `implemented_by`, or
  `run_tac` declaration and no actual candidate inhabitant.  Thus the
  manuscript's present claim that the geometry structures are uninhabited is
  consistent with the checked tree; the defect is that this script cannot
  enforce it robustly.
- Required resolution: inspect elaborated Lean declarations and reject any
  constant whose inferred type constructs the protected structures, rather
  than matching source substrings.

### F-304 — The Artin--Magnus/Andreadakis finite claim replays successfully

- Severity: **Informational (positive result)**
- Status: **CONFIRMED within the public-word boundary**
- Locations: `main.tex:1151-1159`;
  `scripts/verify_t73_gamma3_magnus.py:29-137`;
  `scripts/verify_t73_uniform_order3.py:32-94`.
- Evidence: exact replay on 2026-09-04 reconstructed the 11,340-letter
  \(B_{44}\), computed the Artin action on all 44 free generators through
  Magnus degree 3, and found zero nonidentity coefficients.  Integer
  intermediates had absolute value at most 4.  The full cabled 88-dimensional
  Burau replay checked all 7,744 entries through orders 0, 1, 2 and found none
  nonzero; 7,728 cubic entries were nonzero.  Deleting the final Artin letter
  is rejected by the supplied mutant tests.
- Source check: Darn\'e, *On the Andreadakis problem for subgroups of
  \(IA_n\)*, IMRN 2021, Theorem 6.2, states
  \(\Gamma_*(P_n)=\mathcal A_*\cap P_n\) for the Artin embedding.  Therefore
  identity modulo \(\Gamma_4(F_{44})\) gives \(W\in\Gamma_3(P_{44})\), with
  the same indexing used by the manuscript.  The cited implication itself is
  sound.
- Qualification: this verifies the algebra of the reconstructed public word,
  not that the word is the actual geometric collar, nor the pivotal endpoint
  identification in F-300, nor the MWW/BPW comparison in F-201--F-203.

### F-305 — Public detector provenance names source artifacts absent from the repository

- Severity: **Minor**
- Status: **CONFIRMED reproducibility/provenance gap**
- Locations: `data/T73_DELTA3_PUBLIC_INPUT.json:12-77`;
  `scripts/recompute_t73_delta3.py:312-415`.
- Evidence: the input's provenance names and hashes
  `T73_COLLAR_BRAID.json`, `verify_t73_collar_braid.py`,
  `PRODUCT_NORMAL_CHRISTOFFEL_THXY_MOVIE.json`, `MWW 1handles.tex`, and `BPW
  vertical.tex`; none exists in the repository.  The current recomputation
  instead imports live in-repository Johnson geometry builders and compares
  their derived word with frozen crossing rows.  It cannot verify the listed
  primary-text/source-extract provenance from the hashes alone.
- Proof-chain impact: the scalar calculation is reproducible from the current
  repository state, but its claimed lineage to those named source artifacts
  is not independently auditable.  A digest is not a substitute for the
  hashed object or a stable public locator.

### F-306 — The all-source Lean declaration gate currently fails on comments

- Severity: **Minor**
- Status: **CONFIRMED tooling defect**
- Locations: `scripts/audit_declarations.py:9-22,86-101`;
  `Smooth4PC/ReynoldsCableCocone.lean:42,50`.
- Evidence: running `python3 scripts/audit_declarations.py --root .` exits 1
  with `ReynoldsCableCocone.lean: forbidden constant`.  The only occurrences
  are the English phrases “A constant cubic” and “of a constant cubic” in
  doc comments.  The scanner applies its regular expressions to raw source
  without removing comments or parsing declarations.
- Consequence: this purported fail-closed whole-tree gate has false positives
  on the committed source and therefore cannot presently serve as a CI
  assurance.  This does not introduce a Lean axiom; direct source inspection
  and the compiler/`#print axioms` audit remain the relevant evidence.

### F-500 — The BPW/BHPW shadow has a precise conditional construction, but its required dg coefficient comparison is absent

- Severity: **Critical**
- Status: **OPEN; conditional construction isolated**
- Location: `docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md`; manuscript equations
  (17) and `eq:actualShadow`.
- Source conclusion: BPW's vertical-to-horizontal trace functor and quantum
  preshadow functoriality, followed by the BHPW strict foam functor and
  endpoint qHH/Chern identification, do give a map to
  \(\operatorname{Hom}(E_{86},E_{88})\) after one supplies a homogeneous dg
  coefficient-bimodule equivalence. This is a valid conditional route and
  does not require a new published comparison theorem.
- Missing input: actual natural chain equivalences
  \(H_{T,T'}:C_R(T,T')\simeq\underline{\mathrm{Hom}}(FT,FT')\{-44\}
  \otimes A^{\otimes227}\), including inverses/homotopies and both action
  squares for every homogeneous foam. BPW/BHPW do not construct this
  candidate-specific datum.
- Impact: C-H1 and the identification of 2624 with an MWW functional remain
  unproved.

### F-501 — The C1/C2 programs do not construct the claimed chain maps or action squares

- Severity: **Critical**
- Status: **CONFIRMED**
- Locations: `scripts/certify_t73_c1_cut_link.py` and
  `scripts/certify_t73_c2_comparison.py`.
- Evidence: C1 stores start/end polyline hashes, not a strict foam movie,
  complex, differential, chain map, or homotopy. C2's own module docstring
  says it is not a chain-level Blanchet--Khovanov complex of the actual cut.
  Its left/right “squares” are two support boxes disjoint from the detector;
  they do not define or verify the maps for arbitrary \(f,g,m\).
- Impact: spatial disjointness is useful geometric input, but it does not
  prove the dg naturality equations needed to descend to coefficient qTrace.

### F-502 — The asserted all-cable comparison lacks owner geometry and statewise types

- Severity: **Critical**
- Status: **OPEN**
- Locations: `main.tex:1320--1385`, the count arrays in
  `scripts/certify_t73_c2_comparison.py`, and the 44 selected rectangles in
  `audit/t73_c1_cut_link.json`.
- Evidence: the 44 constructed rectangles cover the selected \(m_2\) and
  \(r_{xy}\) state. General cable states also use the recorded 189
  \(y\)-passages of \(m_3\) and two of \(r_{yz}\), with their z partners and
  residual circles. No corresponding framed simultaneous isotopy, dg
  comparison, or fixed-target closure is present. The MWW source is a product
  of 3-ball categories whose endpoint configurations change with the cable
  state; the manuscript suppresses this typing when it writes a single
  category of tangles \(P_{86}\to P_{88}\).
- Impact: neither all-state beta invariance nor all-state psi compatibility
  follows from the selected-state Hattori picture.

### F-503 — Reynolds and defect-head formalizations assume the substantive beta/psi input

- Severity: **Major**
- Status: **CONFIRMED**
- Locations: `Smooth4PC/ReynoldsCableCocone.lean`,
  `Smooth4PC/HattoriBalancedInput.lean`, and equations (25)--(27) in
  `main.tex`.
- Evidence: the Reynolds theorem proves that an average of entries already
  assumed equal has the common value. The defect-head theorem proves
  zero/identity for abstract maps defined to increment a label counter.
  Neither identifies an actual MWW beta or psi foam on the whole typed source.
  The two separate core counits occur after two-handle attachment and cannot
  be treated as a raw W1 retraction without first proving the quotient
  compatibility at issue.
- Impact: C-H2 remains open even if the selected-state endpoint scalar is
  accepted.

### F-504 — Pivotal coefficients are underdetermined by the committed endpoint data; checking is now fail-closed

- Severity: **Critical for the claimed geometric identification**
- Status: **OPEN; fail-closed checker added**
- Locations: hard-coded assignments at
  `scripts/build_t73_endpoint_transport.py:238--240`; new
  `scripts/check_t73_c_pivotal_grading_inputs.py` and
  `data/T73_C_PIVOTAL_GRADING_INPUT.schema.json`.
- Evidence: BPW (A.4) includes a basis-dependent \(V^*\to V\)
  identification with a q-power, BPW (A.6) has ordered cup/cap coefficients,
  and Blanchet detachment signs require local normal data. The current files
  contain endpoint orientation and order but no complete V/V-dual chart,
  nesting data, atomic duality moves, or sign-producing local normals.
- Positive numerical check: using the standard BPW constant cup and cap
  signs, \(u=e_2+e_{87}\) and \(\ell=e_{87}^*+e_2^*\), the same committed
  Burau word still gives epsilon-cubic \(-328\) and h-cubic 2624. Thus this
  particular sign correction does not destroy the number, but it does not
  supply the missing categorical identification.
- Enforcement: the new checker exits nonzero and refuses pivotal or degree
  certification until all primitive fields are supplied.
- Endpoint-level diagnostic (2026-09-05): the report now contains 88 entries
  keyed by the physical endpoint ID.  For each it records the available base
  passage orientation, cable-copy multiplier, their derived product and the
  exact absent boundary face/tangent/coorientation, BPW boundary-word symbol,
  nesting parent/depth, A.4 atom path, and Blanchet normal/movie.  The two
  selected cup feet additionally name the absent ordered A.6 cup and cap
  terms.  Thus the failure is localized, not a generic missing-field verdict.
- Legacy regression: all 88 serialized legacy coefficients are `+q^0`, with
  zero primitive derivations.  Moreover, the old builder ignores the base
  passage orientation; its orientation disagrees with the derivable
  passage-times-copy sign at four named endpoints.  The checker therefore
  rejects the legacy table even though it is complete as a list of literals.

### F-505 — The intrinsic four-term degree ledger is plausible, but the comparison grading remains uncertified

- Severity: **Major**
- Status: **OPEN**
- Locations: `sec-finite-details.tex:254--271`, the Manolescu--Neithalath
  erratum, and the new fail-closed checker.
- Evidence: in intrinsic framed KhR2, the four stated contributions have the
  expected formal meanings and sum to
  \(-44+227+315-4=494\). The detector braid itself has writhe zero. What is
  missing is the framed-KhR2/BHPW convention and writhe entry for every
  coefficient closure, Hattori target, cup, cap, selected cable state, and
  comparison family. The erratum requires the conversion shift
  \(-(N-1)w\) wherever that conversion is made.
- Impact: arithmetic 494 is confirmed; absolute MWW degree 494 is not.

### F-506 — Constructive C closure attempt stops at explicit, finite missing data

- Severity: **Critical summary**
- Status: **BLOCKED BY MISSING MATHEMATICAL DATA**
- Location: `docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md`.
- Minimum closure data: the actual MWW product source at every state; strict
  natural dg maps \(H^r\); the missing \(m_3/r_{yz}\) product movies; every
  beta/psi comparison square; 88 primitive duality charts; and the complete
  corrected writhe/grading ledger. Until supplied, 2624 remains a verified
  endpoint-model value rather than a functional on the genuine W2 quotient.

### F-507 — All-owner primitive y/z geometry is constructed in the normalized Johnson collar

- Severity: **Remediation / positive finite-geometric result**
- Status: **RESOLVED for the conditional collar prefix; not C-H1**
- Locations: `scripts/build_t73_all_owner_product_primitives.py`,
  `geometry/t73_all_owner_product_primitives.json`,
  `tests/test_t73_all_owner_product_primitives.py`, and the all-owner section
  of `docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md`.
- Result: source-bound reduction gives
  \(n_y=(42,189,2,2,0)\), \(n_z=(269,1271,2,2,0)\), 235 primitive
  y/z rectangles, and 1309 residual z circles per balanced cable pair. Every
  surviving z source is partitioned exactly once. The unique m3 terminal
  reduction and both r-zx product bigons retain their original source IDs.
- Orientation correction: dual cells are traversed opposite to their stored
  disk-boundary order, while the x-slide ledger records the forward order.
  Negating the stored slide orientation gives the exact words
  `r_xy=z y Z Y`, `r_yz=y z Y Z`, and the empty reduced `r_zx` word. Mixing
  the two traversals produced the rejected `Z y z Y` word.
- Arbitrary multiplicities: distinct rational levels inside each product
  neighborhood prove disjoint parallel-copy existence and the formulas
  \(\sum r_i n_{y,i}\) and \(\sum r_i(n_{z,i}-n_{y,i})\). Six focused tests
  and six hostile mutations pass.
- Scope firewall: the artifact explicitly sets
  `actual_partial_W2_claimed=false`. It is conditional on the missing P0
  ambient collar inclusion and supplies no Blanchet--Khovanov dg map or
  action-naturality homotopy. Thus it closes the primitive geometric prefix
  of C-H2, not C-H1 or beta/psi descent.

### F-508 — The cubic is conjugation-gauge invariant but not invariant under the point-push loop choice

- Severity: **Critical for the claim that 2624 is forced by P0 geometry**
- Status: **CONFIRMED by exact calculation**
- Locations: `main.tex:724--731`, the external factor
  \(\rho_h(W)-I\) in the C detector; `scripts/audit_t73_point_push_gauge.py`,
  `audit/t73_point_push_gauge.json`, and
  `tests/test_t73_point_push_gauge.py`.
- Naturality calculation: a chart change transports
  \((A,u,\ell)\) to \((PAP^{-1},Pu,\ell P^{-1})\), and hence
  \((\ell P^{-1})(PAP^{-1}-I)(Pu)=\ell(A-I)u\) exactly. BPW/MWW
  naturality does not force this scalar to vanish.
- Loop-choice counterexample: precomposing the selected returned loop by
  \(P\) replaces (A) by \(\rho(P)A\), not by a conjugate. At order three
  the cubic changes by \(\ell K_Pu\). Taking (P=W^{-1}) preserves returned
  endpoints, returned first-order normals and zero writhe, while changing the
  computed cubic from 2624 to zero.
- Consequence: the six-sweep loop chosen by isotopy extension is not selected
  by the static collar data. It may be used as an explicitly auxiliary,
  noncanonical self-cobordism only after independent beta/psi descent; it
  cannot itself discharge P0/C-H1. To claim geometric canonicity, the paper
  must construct a relative cobordism class selected by the AR collar and
  prove that every allowed presentation change acts only by simultaneous
  conjugation.

### F-509 — A fixed noncanonical point-push is sufficient in principle, but its MWW cocone is missing

- Severity: **Major clarification; Critical remaining interface**
- Status: **CONDITIONAL THEOREM PROVED; APPLICATION OPEN**
- Location: the fixed-\(W\) theorem in
  docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md.
- Positive result: a detector used only to prove nonvanishing need not be
  canonical under changes of its definition. For specified \(W\), the BPW
  horizontal-trace action and strict BHPW foam/qHH functor assign an endpoint
  operator \(A_W\). Given a genuine coefficient shadow,
  \(C_h(A_W-I)\operatorname{Sh}_h\) is well typed on coefficient qTrace.
  Thus F-508 does not force the scalar to vanish.
- Conditional descent: statewise shadows satisfying simultaneous beta
  conjugation and old-factor/local-Frobenius factorization for psi give,
  after placement averaging, beta invariance and undotted-zero/
  dotted-identity. The proof uses \(A_W-I=O(h^3)\) and
  \((\epsilon\otimes\epsilon)\Delta(1)=0\),
  \((\epsilon\otimes\epsilon)\Delta(X)=1\).
- Remaining obstruction: no statewise actual-MWW chain maps, actual-beta
  comparison diagrams, or whole-source actual-psi factorizations are
  supplied. BPW/BHPW evaluate supplied movies but do not construct these
  candidate-specific squares.
- Required wording: \(W\) may be an auxiliary chosen detector, but must not
  then be used to discharge P0/C-H1; beta/psi descent stays hypothetical.

### F-510 — A standard 88-endpoint pivotal convention is now derived and reproduces 2624

- Severity: **Remediation / partial closure**
- Status: **PIVOTAL CERTIFIED; ABSOLUTE DEGREE OPEN**
- Locations: `geometry/t73_p0_marked_vertical_collar.json`,
  `scripts/build_t73_c_pivotal_grading_input.py`,
  `data/T73_C_PIVOTAL_GRADING_INPUT.json`,
  `scripts/check_t73_c_pivotal_grading_inputs.py`, and the updated endpoint
  discussion in `main.tex`.
- Construction: the freely chosen standard collar fixes source/target faces,
  tangents, coorientations, tensor order, 44 `V` and 44 `V*` factors, BPW
  (A.4) duality atoms, BPW (A.6) cup/cap terms, and product-foam normals. The
  input is hash-bound to the static P0 marked collar, not copied from the old
  asserted pivotal coefficients.
- Result: the derived endpoint monomials have positive signs and q-powers 0
  or 1; the cup has powers -1 and +1. Since `rho(W)-I=O(h^3)`, those
  positive-order factors do not alter the cubic, which replays as 2624. Four
  updated tests pass, while the legacy all-`+q^0` table remains rejected as a
  derivation.
- Remaining gap: four global diagrams--the actual MWW coefficient closure,
  Hattori target closure, selected cabled state, and MWW-to-BHPW comparison--
  lack a common framing/writhe conversion ledger. Therefore the intrinsic sum
  494 is not yet certified as the absolute MWW grading.

### F-511 — C-H1 first fails at currying the MWW product coefficient into one morphism category

- Severity: **Critical**
- Status: **CONFIRMED TYPE/GRADING GAP**
- Location: equation (17) and Lemma C1 in main.tex; source-exact analysis in
  docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md.
- MWW source type: Theorem 4.7 gives a coefficient profunctor on the product
  of the 3-ball categories \(\prod_i\mathcal C_{p_i(r)}\). It does not state
  that the cut tangle represents an endofunctor of a single category.
- BPW/BHPW limit: BPW 3.12 and 3.20--3.21 give vertical/horizontal quantum
  trace only after such a morphism-category/endofunctor type is supplied.
  BHPW 4.6 makes specified planar tangle/foam operations strict; it does not
  construct the missing currying operation. There is no K0-only problem,
  since qHH is applied before the endpoint Chern identification.
- Missing datum: a planar/canopolis functor
  \(\iota_r:\prod_i\mathcal C_{p_i(r)}
  \to\mathcal T_2(P_{a_r},P_{b_r})\), together with a natural homogeneous
  coefficient isomorphism for arbitrary tuples of inserted tangles. The
  all-owner rectangles bind fixed attaching arcs but do not specify this
  operation on arbitrary objects or morphisms.
- Concrete grading contradiction: a tangle \(P_{86}\to P_{88}\) has
  \(174=2\cdot87\) boundary points, so MWW Definition 4.5 gives Hom
  normalization \(+87\) for \(N=2\). The manuscript instead uses \(-44\) as
  removal of that normalization. The number 44 belongs to the y-handle
  configuration, and no planar functor or object shift reconciles it with
  the asserted morphism category.
- Consequence: no matrix enumeration is needed once the missing natural
  representability map exists, but C-H1 is not presently constructed and the
  absolute degree ledger cannot use its \(-44\) term as written.

### F-512 — Corrected C-H1 must coend out \(C_{271}\) before oriented doubling

- Severity: **Critical repair specification**
- Status: **CORRECTED TYPE DERIVED; REPRESENTABILITY OPEN**
- Location: corrected equations (C.H1d)--(C.H1h) in
  docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md.
- Correct source: at the selected state MWW Theorem 4.7 uses
  \(\mathcal C_{44}\boxtimes\mathcal C_{271}\) and global shift \(+315\).
  First taking the coefficient coend in the z variable gives a
  \(\mathcal C_{44}\)-bimodule \(M_R^z\); Fubini for coend quotients then
  reduces the product trace to \(HH_0(\mathcal C_{44};M_R^z)\).
- Correct target: if the product rectangles give
  \(M_R^z(T,T')\cong
  \operatorname{Hom}_{\mathcal C_{44}}(BT,BT')\{-44\}
  \otimes A^{\otimes227}\), then \(-44\) is exactly the MWW Hom
  normalization for 88 boundary points. Oriented doubling is applied only
  afterwards and gives a shadow into \(\operatorname{End}(E_{88})\).
  The cup \(E_{86}\to E_{88}\) remains external, so the detector is
  \(\ell(\rho(W)-I)\operatorname{Sh}^{44}(x)u\).
- Remaining first map: the existing geometry does not define the planar
  functor \(J:\mathcal C_{44}\to\mathcal C_{271}\) adding 227 z arcs, nor a
  relative-to-insertion-boxes isotopy identifying the full off-diagonal MWW
  coefficient with two z-representable Hom factors for arbitrary inserted
  tangles. Without that factorization, co-Yoneda cannot establish the
  reduced coefficient isomorphism.
- Source boundary: BHPW canopolis composition and strict functoriality would
  prove all-variable naturality once this planar operation exists. The
  published results do not infer it from endpoint counts or fixed attaching
  arcs.
- Grading: the corrected route makes the formal ledger
  \(-44+227+315-4=494\) type-consistent, but absolute grading stays open
  until the representability isotopy and its writhe/convention table are
  supplied.

### F-513 — Full \(C_{271}\) morphisms mix the 227 added factors with the active factors

- Severity: **Critical for the naive Kunneth/counit argument**
- Status: **REFUTED BEFORE CO-YONEDA; FULL REPRESENTABLE ROUTE OPEN**
- Locations: Lemma C1 and the claim that circle counits are disjoint from
  both actions in main.tex; stress test in
  docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md.
- Category check: MWW Definition 4.5 has all oriented tangles with boundary
  \(P_{271}\) and their full KhR morphism spaces. There is no owner label or
  central idempotent distinguishing 44 active strands from 227 added ones.
  BHPW platforms/weight blocks do not add such provenance.
- Braid counterexample: on \(A\otimes A\), an allowed same-orientation
  exchange \(\tau\) gives
  \((1\otimes\epsilon)(1\otimes X)=1\) but
  \((1\otimes\epsilon)\tau(1\otimes X)=0\).
- Foam counterexample: the allowed merge--split map
  \(S=\Delta m\) sends \(1\otimes1\) to
  \(1\otimes X+X\otimes1\). Hence
  \((1\otimes\epsilon)S(1\otimes1)=1\), whereas the fixed-extra counit of
  \(1\otimes1\) is zero. No active-factor map can make this natural.
- Consequence: the proposed \(A^{\otimes227}\) splitting and counits are not
  natural for the full z action if applied before taking the z coend.
- Surviving possible route: first prove that the complete MWW coefficient is
  a pair of representable profunctors over the full \(\mathcal C_{271}\);
  then co-Yoneda absorbs every mixing morphism; only afterwards apply the
  split-link Kunneth isomorphism and counits. No invariant platform is needed
  in this order, but the required two-sided representable planar
  factorization is still absent.

### F-514 — The current product data do not prove the off-diagonal coefficient is literally split

- Severity: **Critical remaining geometric interface**
- Status: **OPEN; FIRST UNSEPARATED CONNECTOR IDENTIFIED**
- Location: the literal-splitting test in
  docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md and
  geometry/t73_all_owner_product_primitives.json.
- Proposed operation: \(J(T)=T\sqcup I^{\sqcup227}\) is valid, but co-Yoneda
  additionally requires the full coefficient to factor naturally as
  \(\operatorname{Hom}_z(JBT,Z')\otimes
  \operatorname{Hom}_z(Z,JBT')\) relative to all four insertion boxes.
- Missing split: no relative separating sphere or two disjoint 3-balls
  containing the proposed Hom closures are supplied.
- Exact first connector: 41 selected \(m_2\) pairings use Johnson central
  connectors. The last is the cyclic
  \(m_2:C_i\to c1:\mathrm{letter}:0\) connector through the bottom coordinate
  arc and both \(\lambda_i/\mu_i\) bands of the
  \((t,h_{CS})\) cancellation. It has hashes and an endpoint rule, but no
  common-complement surface or split-side assignment.
- Residual issue: all 227 z-circle tracks are explicitly conditional ambient
  transports. Their individual meridians do not form a simultaneous isotopy
  relative to both z insertion boxes and the cyclic connector.
- Assessment: this does not prove that the two-representable factorization is
  impossible. It proves that it is not supplied by the existing rectangles.
  C-H1 requires the relative separating sphere and simultaneous ambient movie
  before (C.split) and co-Yoneda can be used.

### F-515 — Exact two-representable/co-Yoneda theorem is valid under a relative split hypothesis

- Severity: **Remediation theorem; Critical missing hypothesis**
- Status: **CONDITIONAL PROOF COMPLETE; RELATIVE SPLIT OPEN**
- Location: equations (C.rep2)--(C.state-shadow) in
  docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md.
- Exact theorem: for \(p_y\leq p_z\), \(\ell=p_z-p_y\), set
  \(J(T)=T\sqcup I^{\sqcup\ell}\). If a separating sphere relative to all
  four insertion boxes identifies the coefficient link with the two Hom
  closures, then the normalized coefficient is the ordinary tensor of the
  two representables with shift
  \(\{p_y-p_z\}=\{-\ell\}\).
- Co-Yoneda: taking the full \(\mathcal C_{p_z}\)-coend absorbs every mixing
  morphism and gives
  \(\operatorname{Hom}_{\mathcal C_{p_z}}(JBT,JBT')\{-\ell\}\).
  Only afterwards is Kunneth applied.
- Kunneth and shifts:
  \[
  \widehat M_R^z\cong
  \operatorname{Hom}_{\mathcal C_{p_y}}(BT,BT')
  \otimes A^{\otimes\ell},
  \]
  and removing the global \(\{p_y+p_z\}\) gives raw shift
  \(-(p_y+p_z)\).
- Correct endpoint: oriented doubling after the coend produces a statewise
  shadow into \(\operatorname{End}(E_{2p_y})\); at \(p_y=44\) this is
  \(\operatorname{End}(E_{88})\). The cup \(E_{86}\to E_{88}\) remains
  external.
- Why a split is needed: without the separating sphere, canopolis gluing is
  composition/relative tensor over an arc algebra, not an ordinary tensor
  Kunneth isomorphism of Hom homologies. BHPW sweetness does not identify a
  connected planar composite with a split link.
- Remaining gap: F-514's relative separating sphere and simultaneous ambient
  movie are not present, so the theorem does not yet instantiate C-H1.
- Grading consequence: at \((44,271,227)\) the all-\(X\) normalized class
  has degree 227 and cabled degree 223, not 494. Therefore a literal
  two-representable split factorization is incompatible with the
  manuscript's \(-44,+315\) ledger even if the missing sphere exists.

### F-516 — Shift audit refutes using the literal two-representable split to recover degree 494

- Severity: **Critical**
- Status: **CONFIRMED ARITHMETIC/TYPE CONTRADICTION**
- Location: corrected shift computation in the conditional
  two-representable theorem.
- Computation: the normalized MWW coefficient has shift \(p_y+p_z\), while
  two normalized \(\mathcal C_{p_z}\)-Hom factors have total shift \(2p_z\).
  Hence (C.rep2) must carry shift \(p_y-p_z=-\ell\), not \(+p_y\).
  Co-Yoneda retains \(-\ell\), and split-circle Kunneth contributes
  \(+\ell\); the shifts cancel.
- At the selected state, the normalized reduced coefficient is
  \(\operatorname{Hom}_{\mathcal C_{44}}(BT,BT')\otimes A^{\otimes227}\).
  The all-\(X\) class has degree 227 and, after the cabled shift \(-4\),
  degree 223. The raw reduced shift is \(-315\), canceled by the global
  \(+315\).
- Consequence: a literal tensor of two representables cannot yield both the
  claimed raw \(-44\) comparison and degree 494. Recovering those numbers
  would require a different single-Hom factorization, not the proposed
  two-representable/co-Yoneda split.

### F-517 — Under the literal-split hypothesis, degree 223 propagates and still obstructs \(S^4\)

- Severity: **Conditional remediation / correction inventory**
- Status: **CONDITIONAL PROOF COMPLETE; SPLIT AND C/S MAPS OPEN**
- Location: docs/proofs/T73_SPLIT_ROUTE_DEGREE_223.md.
- Degree: the normalized reduced coefficient is
  \(\operatorname{Hom}_{\mathcal C_{44}}(BT,BT')\otimes A^{\otimes227}\);
  the all-\(X\) class has degree 227 and the cabled shift gives 223.
- Detector: \(\epsilon^{\otimes227}\) has degree \(-227\). On the source
  shifted by \(-4\), the divided cubic row has degree \(-223\). The external
  h-adic coefficient extraction has degree zero, so evaluation 2624 is
  compatible with a homogeneous degree-223 class.
- Handle propagation: MWW Theorems 3.2 and 3.7 and Proposition 3.4 are
  absolute-bigrading preserving in the relevant handle maps. Thus, assuming
  the beta/psi and hemisphere cocones, the class remains in degree 223
  through the two-, three-, and four-handle stages.
- Standard sphere: MWW Corollary 3.5 places the standard \(S^4\) module in
  bidegree \((0,0)\); after rational base change its degree-223 summand is
  zero. A genuine nonzero closed degree-223 class gives the same obstruction
  as any other nonzero degree.
- Inventory: the proof note lists every active paper, Lean interface,
  executable test, generated JSON, and proof document semantically hardcoded
  to 494, and separately excludes geometric uses of 494 as an index.
- Firewall: none of those files should be rewritten to 223 while the
  relative split hypothesis and subsequent C/S maps remain unproved.

### F-518 — C-H1 now has a coordinate-only output contract and fail-closed co-Yoneda consumer

- Severity: **Remediation / explicit remaining blocker**
- Status: **CONTRACT AND POLYGONAL SOURCE IMPLEMENTED; SIMPLICIAL MOVIE OPEN**
- Locations: data/T73_C_H1_RELATIVE_ISOTOPY.schema.json,
  scripts/verify_t73_c_h1_relative_isotopy.py,
  scripts/build_t73_c_h1_coend_certificate.py,
  tests/test_t73_c_h1_relative_isotopy_gate.py, and
  docs/proofs/T73_C_H1_GEOMETRIC_OUTPUT_CONTRACT.md.
- Contract: a candidate must give a common rational tetrahedral exterior,
  four parametrized insertion-ball boundary subcomplexes, 630 framed strand
  paths, 1260 oriented endpoints, complete matching, and a sequence of exact
  one-vertex PL moves. Every move fixes all required boundary vertices, has a
  spherical star link, and preserves every incident determinant sign for the
  whole time interval.
- Target/euler checks: final paths must equal the two coordinate canopolis
  closure systems; orientations and product push-offs must agree; no
  births/saddles/deaths are allowed; closed trace Euler characteristic and
  quantum shift must be zero.
- Current result: geometry/t73_selected_source_exterior.json supplies
  combinatorial incidence and rational polygonal routes, but no common
  tetrahedral exterior; geometry/t73_c_h1_relative_isotopy.json is absent.
  The target normal form remains target-only.
- Legacy rejection: geometry/t73_product_ribbon_isotopy.json stores PASS and
  exhibited_product_isotopy=true, but each frame is only a time/hash pair.
  The new verifier refuses it as a coordinate movie.
- Co-Yoneda firewall: the certificate builder raises unless the geometric
  verifier returns PASS_COORDINATE_MOVIE; no certificate is currently
  written. Five regression tests pass, including rejection of status literals
  without coordinates.
- Next required constructor: incorporate the polygonal source exterior,
  insertion-box incidence and framing tracks into one common embedded
  rational tetrahedral mesh. Local torus, cancellation-belt and
  detector-chart hashes cannot be treated as that mesh.

### F-519 — The v1 target endpoint-count defect has been corrected in v2

- Severity: **Corrected constructor defect; matching obstruction remains**
- Status: **SUPERSEDED BY V2 AND F-525**
- Evidence: geometry/t73_selected_source_exterior.json,
  geometry/t73_selected_canopolis_normal_form.json, and the updated
  C-H1 relative-isotopy verifier.
- Source type: the four source insertion spheres have endpoint counts
  \((88,88,542,542)\), with 630 exterior intervals and 1260 total endpoints.
- Old target type: assigning one endpoint to each end of all 315 arcs on every
  ball produced the false multiset \(\{315,315,315,315\}\).
- Repair: schema v2 distinguishes 88 Y--Z arcs from 227 Z--Z arcs on each
  side. Its endpoint multiset is \(\{88,88,542,542\}\), matching the source,
  and its 630 centre arcs and 630 push-offs pass exact pairwise tests.
- Remaining obstruction: equality of counts is not equality of matching.
  F-525 exhibits eight wrong-side connectors and therefore still refutes the
  literal relative split.
- Enforcement: the geometric verifier returns
  IMPOSSIBLE_LITERAL_SPLIT_BOUNDARY_MATCHING, and the co-Yoneda certificate
  builder refuses to write an artifact.

### F-525 — Eight mixed-orientation intervals obstruct a literal two-closure target

- Severity: **Critical topological/type obstruction**
- Status: **REFUTED LITERAL SPLIT MATCHING**
- Evidence: scripts/verify_t73_c_h1_relative_isotopy.py and
  audit/t73_c_h1_relative_isotopy_report.json.
- Exact incidence: the 176 y-incident source intervals split as 84
  \(Y_--Z_+\), 84 \(Y_+-Z_-\), four \(Y_--Z_-\), and four
  \(Y_+-Z_+\).
- Provenance: the eight exceptions are precisely the positive/negative
  cable-copy intervals on both sides of the two negatively oriented base y
  passages \(m_2:C_i\) and \(r_{xy}:\mathrm{vertex}:1\).
- Consequence: a target with 88 active plus 227 z arcs per closure can match
  total arc counts, but two closures using disjoint pairs of insertion balls
  cannot match these eight endpoints. Allowing each closure to use subsets of
  both z balls destroys a relative separating sphere and exposes the subsets
  to arbitrary \(\mathcal C_{271}\) mixing.
- Enforcement: the verifier returns
  IMPOSSIBLE_LITERAL_SPLIT_BOUNDARY_MATCHING and the co-Yoneda builder
  refuses certification.

### F-526 — The eight wrong-side intervals do not derive the single weight defect

- Severity: **Major route refutation**
- Status: **CONFIRMED**
- Evidence: scripts/audit_t73_defect_aware_currying.py,
  audit/t73_defect_aware_currying.json, and
  tests/test_t73_defect_aware_currying.py.
- Count: two negative base y passages times two cable copies times two
  incident sides produce eight exceptions. Correcting the cross matching
  requires four independent endpoint reconnections, whose mate choice,
  Blanchet sign and Euler degree are not supplied.
- Endpoint invariant: pivotal currying changes source/target variance but
  preserves the total 176 active boundary endpoints. A
  \(P_{86}\to P_{88}\) object has 174. Thus the currying cannot itself
  produce the claimed one-cup defect.
- Correct origin: the weight-86 one-defect sector is selected by the external
  cup \(E_{86}\to E_{88}\); it is not a consequence of the eight source
  intervals.
- Result: the single-Hom target may be defined as auxiliary target data, but
  the source-to-target map and its grading remain open.

### F-527 — No cup/cap movie can be assigned to the four endpoint re-pairings from current data

- Severity: **Critical remaining C-H1 cell data**
- Status: **FAIL-CLOSED**
- Location: docs/proofs/T73_DEFECT_AWARE_CURRYING_AUDIT.md and
  audit/t73_defect_aware_currying.json.
- Pairing table correction: the former lexicographic rows are retained only
  as a superseded diagnostic; two produced entry--entry/exit--exit arcs. The
  live four rows are instead uniquely grouped by owner and Y-to-Z/Z-to-Y
  orientation, and every proposed cross arc is listed exit-to-entry.
- Obstruction: a pivotal mate changes Hom presentation but not pointwise
  relative endpoint matching. The proposed pairs change matching, so they
  require saddle/reconnection cells rather than a bare evaluation or
  coevaluation chart.
- Missing fields: these are band reconnections, so a left/right pivotal mate
  is marked not applicable. The embedded band/foam movie, Blanchet sign,
  number of saddles, inverse data, Euler characteristic and quantum degree
  remain UNREALIZED or UNDETERMINED.
- Count obstruction: pivotal mates preserve 176 active boundary endpoints;
  \(P_{86}\to P_{88}\) has 174. The one defect comes from the external cup,
  not these four re-pairings.
- Verification: three focused tests pass and prevent promotion to a
  single-defect currying map.

### F-528 — A top-level constructor now saves and inventories every reconstructible selected-C geometry object

- Severity: **Remediation / reproducibility**
- Status: **RECONSTRUCTION VERIFIED; PROOF COMPLETION OPEN**
- Evidence: `scripts/build_t73_complete_geometry_bundle.py`,
  `geometry/t73_complete_geometry_bundle_manifest.v1.json`,
  `data/T73_COMPLETE_GEOMETRY_BUNDLE_MANIFEST.schema.json`,
  `tests/test_t73_complete_geometry_bundle.py`, and
  `docs/proofs/T73_COMPLETE_GEOMETRY_CONSTRUCTOR.md`.
- Saved objects: the four-cycle source exterior with 1260 endpoints, 630
  framed intervals and 2520 ruled-ribbon triangles; the v2 target template with the same endpoint and arc
  totals; the auxiliary P86-to-P88 target; and the four-reconnection defect
  audit. Full `--write`, reconstruction `--check`, fast `--check-files`, JSON
  Schema validation, and OPEN-to-VERIFIED mutation tests pass.
- Status firewall: every artifact has
  `reconstruction_status=VERIFIED`, but every `completion_status` and effective
  `status` is frozen to `OPEN`. The first open edge is the actual 630-interval
  source-to-target coend/currying transformation, including the eight
  wrong-side intervals.

### F-529 — The manuscript no longer applies the refuted split ledger to the actual C class

- Severity: **Critical logical correction**
- Status: **RESOLVED AS AN EXPLICIT CONDITIONAL STATEMENT**
- Evidence: `paper/spc4-t73-candidate/main.tex`,
  `sec-finite-details.tex`, and `sec-appendices-extra.tex`.
- Correction: the formerly named `HattoriActual` formula is now the
  counterfactual `HattoriSplit` formula. Lemma C1 assumes the literal target
  matching and is explicitly inapplicable to the saved source. The value 223
  is only that target's formal ledger, and degree-zero pivotal mates do not
  restore the historical 494 ledger.
- Actual conditional theorem: Hypothesis C now postulates an actual class
  (x_C) in an unspecified degree (q_C\ne0), a statewise coend/currying
  comparison natural for both actions and all beta/psi maps, its complete
  grading ledger, and evaluation 2624. The abstract obstruction uses only
  (q_C\ne0). The finite endpoint calculation is stated separately as the
  scalar 2624 and no longer as an unconditional MWW value.
- Translation firewall: the Chinese manuscript and auxiliary Chinese TeX
  files contain an explicit version warning that their remaining historical
  C/S text is not authoritative until fully synchronized.

### F-530 — The simplicial coefficient gates reject identity and unbound-movie false positives

- Severity: **Critical verifier repair**
- Status: **RESOLVED FOR THE CURRENT FAIL-CLOSED CONTRACT**
- Evidence: `scripts/verify_t73_coefficient_exterior.py`,
  `scripts/verify_t73_c_h1_relative_isotopy.py`, their two schemas, and their
  focused tests.
- Former false positives: the coefficient-exterior gate accepted an arbitrary
  valid frame with `initial=final` and no moves, without binding either end to
  the saved source/target. The C-H1 validator did not require strand paths to
  be ambient edges, did not bind the 1260 endpoint rows exactly, and did not
  require a bijection onto all 630 target arcs. A supplied movie could also
  overwrite the already proved split obstruction with PASS.
- Repair: movies are nonempty and nonidentity, end at time one, and are SHA
  bound to the current source and target. Initial and final arcs and push-offs
  are bijectively bound to the complete saved rational polylines (collinear
  subdivisions allowed), endpoint IDs and named boundary components are
  checked in order, and ambient moves cannot change typed geometry. The C-H1
  validator rejects the eight wrong-side connectors before considering any
  movie, and report generation cannot overwrite that result.
- Scope: no current simplicial witness exists. These checks specify what a
  future common tetrahedral exterior must contain; they do not construct it.

### F-531 — The source constructor now saves ruled ribbons with an exact global clearance certificate

- Severity: **Geometric constructor remediation**
- Status: **RESOLVED FOR THE CANONICAL POLYGONAL SOURCE**
- Evidence: `geometry/t73_selected_source_exterior.json`, its builder,
  verifier and test.
- Construction: every one of the 630 intervals stores its three-vertex core,
  three-vertex push-off, four ruled-ribbon triangles and complete ribbon
  boundary, for 2520 triangles. New centre routes are accepted only when
  every segment has exact distance greater than (10^{-3}) from all earlier
  routes. The common endpoint normal is (2^{-20}) and the largest
  vertexwise (L^1) width is (23/2^{18}).
- Certificate: exact rational minimization gives actual minimum centre
  distance approximately (1.00655\times10^{-3}), while twice the maximum
  ribbon width is approximately (1.75476\times10^{-4}). The strict squared
  inequality proves ribbons belonging to distinct intervals are disjoint.
  Degenerate-ribbon and clearance mutations fail.
- Scope: this establishes the saved canonical framed polygonal source; it
  does not identify it with the actual AR exterior or yet make the ribbons
  subcomplexes of a common ambient tetrahedralization.

### F-532 — The non-literal C route now has an exact four-variable typing graph and acceptance contract

- Severity: **Critical C remediation / remaining theorem isolated**
- Status: **TYPING COMPLETE; CHAIN EQUIVALENCE OPEN**
- Evidence: `geometry/t73_c_defect_coend_typing_graph.json`,
  `data/T73_C_DEFECT_COEND_TYPING_GRAPH.schema.json`,
  `data/T73_C_DEFECT_COEND_WITNESS.schema.json`,
  `data/T73_C_DEFECT_COEND_FINITE_PRESENTATION.schema.json`, the builder,
  fail-closed verifier, focused tests and
  `docs/proofs/T73_DEFECT_AWARE_COEND_CONTRACT.md`.
- Type: the source is a profunctor on
  (mathcal C_{44}^{op}\timesmathcal C_{271}^{op}\times
  mathcal C_{44}\timesmathcal C_{271}), with all 1260 endpoints, 630
  intervals, both residual (mathcal C_{44}) actions and all eight
  wrong-side intervals explicitly represented.
- Orientation correction: the old lexicographic re-pairing had two invalid
  entry--entry/exit--exit rows. The corrected audit gives the unique four
  owner- and exit-to-entry-preserving band obligations. They remain
  `UNREALIZED` saddle/foam movies, not pivotal mates.
- Sufficient routes: either a four-variable two-sided representability chain
  equivalence, or a direct connected-kernel derived bar/coend equivalence
  (Theta), with inverse homotopies, balancing and both residual naturality
  homotopies. Arc-algebra relative tensor and sweetness reconstruct gluing but
  do not themselves prove the target Hom equivalence.
- Grading: if (deg_qTheta=delta_Theta), then
  (q_C=223-delta_Theta). The gate checks that formula but leaves both
  values open because no witness exists.

### F-533 — A complete rational Kirby/PD exporter is verified, while the actual T73 presentation map is absent

- Severity: **Major infrastructure / exact remaining input**
- Status: **EXPORTER VERIFIED ON TRUTH FIXTURE; T73 INPUT OPEN**
- Evidence: `scripts/export_t73_full_handle_diagram.py`,
  `data/T73_FULL_HANDLE_DIAGRAM.schema.json`, the seven-component fixture and
  export under `geometry/examples`, the Spherogram/SnapPy/Regina receipt,
  `scripts/check_t73_full_handle_diagram_input_gap.py`, the coordinate atlas,
  `docs/proofs/T73_AR_TO_KIRBY_STAGE0_ATLAS.md`, tests and
  `docs/proofs/T73_FULL_HANDLE_DIAGRAM_EXPORTER.md`.
- Export: from seven closed rational cores and five closed push-offs in one
  oriented generic chart, exact arithmetic derives all self/mixed crossings,
  parameters and successor cycles, standard PD, Gauss code, the seven-core
  linking matrix, five integer framings, the surgery matrix and the complete
  twelve-component framed-link PD.
- Open-source cross-check: the fixture gives seven core components and a
  twelve-component, 42-crossing framed link in Spherogram; SnapPy gives seven
  cusps and 36 tetrahedra; Regina reconstructs a valid connected orientable
  ideal triangulation with 36 tetrahedra and seven boundary components.
- Actual first gap: a cut/surgery presentation atlas is required, not an
  embedding of (#^g(S^1\times S^2)) into (S^3). Current (m_i) cores use
  four-coordinate seam charts, dual cells and belt bands use several local
  three-coordinate charts, and no transition to a common dotted-circle
  presentation is supplied. After that, both edges and attachment parameters
  of 6 and 1513 bands, spliced final cores, two dotted meridians and five
  final push-offs remain required.

### F-534 — TetGen verifies a saved ten-ribbon source frame, but monolithic scaling fails before twenty

- Severity: **Triangulation infrastructure / resource obstruction**
- Status: **PREFIX VERIFIED; COMPLETE 630-RIBBON FRAME OPEN**
- Evidence: `scripts/build_t73_selected_source_tetrahedral_frame.py`,
  `scripts/verify_t73_selected_source_tetrahedral_frame.py`,
  `data/T73_SELECTED_SOURCE_TETRAHEDRAL_FRAME.schema.json`,
  `geometry/examples/t73_selected_source_tetrahedral_prefix10.json`, tests and
  `docs/proofs/T73_SELECTED_SOURCE_TETRAHEDRAL_FRAME.md`.
- PLC: the outer cube minus four insertion cubes, core and push-off segments,
  2520 possible ribbon facets and endpoint connectors are supplied with
  unique markers. TetGen uses exact predicates; the constructor can recover
  subdivided marked faces and collinear edge paths, restore authoritative
  rational input vertices and reject lost constraints or zero-volume tets.
- Saved prefix: ten source ribbons give one connected tetrahedral
  3-manifold with five triangulated (S^2) boundary components, 101 vertices,
  858 tetrahedra, ten core paths, ten ribbon disks and exact volume 63968.
  An independent verifier and JSON Schema accept it as `PASS_PREFIX_ONLY`.
- Resource falsification: a 50-ribbon monolithic run produced no result after
  six CPU minutes; a 20-ribbon run reached 14.6 GB RSS (91.7% of the host) in
  roughly 40 seconds. Allowing facet subdivision did not remove the memory
  explosion. Both runs were terminated with no accepted artifact.
- Guard and next route: monolithic requests above ten are now rejected unless
  an explicit unsafe resource-probe flag is passed. The complete frame needs
  a partitioned construction with certified matching boundary
  triangulations and a checked simplicial gluing map; the prefix is not used
  as evidence for the missing full object.

### F-535 — Bundle v2 inventories typing, atlas, PD fixture and tetrahedral prefix without promoting them

- Severity: **Reproducibility / completion firewall**
- Status: **RESOLVED FOR CURRENT ARTIFACT INVENTORY; BUNDLE OPEN**
- Evidence: `scripts/build_t73_complete_geometry_bundle_v2.py`,
  `geometry/t73_complete_geometry_bundle_manifest.v2.json`,
  `data/T73_COMPLETE_GEOMETRY_BUNDLE_V2.schema.json`, its tests and the
  expanded complete-constructor documentation.
- Inventory: v2 hash-binds the verified v1 source/target bundle, the
  four-variable coend typing graph, the AR coordinate atlas, the seven-core
  PD fixture and open-source receipt, and the saved ten-ribbon TetGen prefix.
  Evidence statuses distinguish core reconstruction, typing-only,
  prefix-only and fixture-only results.
- Completion firewall: every artifact still has
  `t73_completion_status=OPEN`. Four separate gates require the actual coend
  chain equivalence, actual complete Kirby input, complete 630-ribbon frame,
  and actual-AR-to-canonical-source binding. Schema and mutation tests reject
  promotion of any fixture or prefix to T73 completion.

### F-536 — Gmsh HXT scales to an independently verified 20-ribbon frame

- Severity: **Alternative triangulation progress / verified prefix frame**
- Status: **PREFIX-20 COMPLETE FRAME PASS; COMPLETE 630-RIBBON FRAME OPEN**
- Evidence: `scripts/probe_t73_selected_source_gmsh.py`,
  `audit/t73_selected_source_gmsh_prefix20.json`, its fail-closed resource
  verifier/tests, the complete prefix-10 and prefix-20 frames and their
  verification receipts, and
  `docs/proofs/T73_SELECTED_SOURCE_GMSH_PROBE.md`.
- First failure and repair: embedding the ribbon surface only in the volume
  left each core--push endpoint connector crossing an unrefined hole-boundary
  facet. The corrected OCC model first embeds each connector in its unique
  insertion-ball boundary surface, then embeds all ribbon surfaces and curves
  in the holed volume.
- Gmsh 4.15.2/HXT observations: prefixes 1, 10 and 20 pass meshing. The
  prefix-20 run has 80 ribbon surfaces, 40 boundary connectors, 4134 nodes and
  23725 tetrahedra. This is substantially better than TetGen's 14.6 GB
  failure at the same prefix.
- Stronger prefix artifacts: the ten- and twenty-ribbon meshes are exported
  with 2664/4134 rationally restored nodes, 14599/23725 tetrahedra, all
  boundary/curve/surface memberships and exact source binding. The independent
  Gmsh-free verifier recovers five \(S^2\) boundaries, every subdivided
  core/push path and ribbon disk, consistent nonzero rational tetrahedron
  orientations and total volume 63968. Both return `PASS_PREFIX_ONLY`.
- Prefix-20 receipt: the first saved receipt was written only after a full
  independent verifier run. It binds frame byte SHA, payload SHA, source SHA,
  verifier path, scope and the exact 4134/23725/20/20/5/63968 counts. Routine
  checks do not rerun the expensive vertex-link calculation and reject
  `PASS_COMPLETE` promotion.
- Scope firewall: the earlier counts-only prefix-20 resource receipt remains
  `PASS_RECEIPT_ONLY`; the new prefix-20 frame is genuine but incomplete.
  Both explicitly leave the 630-ribbon frame open. A prefix-50 run was
  interrupted before a result and is recorded as neither pass nor fail.
- Next construction: run the implemented export/restoration path at larger
  prefixes and ultimately all 630 ribbons, retaining the same independent
  exact checks.

### F-537 — Regina independently recognises the saved P0 dual-block handlebodies, but not the actual W2 boundary

- Severity: **Independent topology-tool validation / scope boundary**
- Status: **P0 DUAL-BLOCK SUBSTRATE VERIFIED; C/S AND ACTUAL W2 OPEN**
- Evidence: `scripts/verify_t73_handlebody_bridge_regina.py`,
  `audit/t73_handlebody_bridge_regina.json`,
  `tests/test_t73_dual_block_handlebodies.py`, and
  `docs/proofs/T73_TOPOLOGY_TOOLCHAIN.md`.
- Reproduction: Regina 7.4.1 in the isolated WSL venv
  `~/.venvs/t73-topology` builds the four stored Johnson/AR face-gluing
  complexes directly and returns `recogniseHandlebody=3` for each of
  `H_J_0,H_J_1,H_AR_0,H_AR_1`. A deliberately reversed first gluing is
  rejected. This independently corroborates the exact dual-block
  genus-three-handlebody substrate used in P0a.
- Boundary: these are the common Heegaard-pair blocks, not a triangulation of
  the actual post-two-handle boundary. Regina recognition provides neither the
  missing relative AR-to-selected-source map nor C's coend/currying chain map,
  nor S's embedded actual sphere system and MWW hemisphere-map factorization.
  The corresponding fail-closed gates therefore remain `OPEN`.

### F-538 — The monolithic Gmsh 630-ribbon frame attempt is killed by the WSL OOM limiter

- Severity: **Resource boundary / no geometric verdict**
- Status: **MONOLITHIC COMPLETE FRAME NOT PRODUCED; PARTITIONED GLUING REQUIRED**
- Evidence: the 5 September 2026 command ran
  `probe_t73_selected_source_gmsh.py --limit 630 --algorithm 10` with output
  paths in `/home/lifesize/.cache` after the same isolated Gmsh 4.15.2
  environment reproduced the prefix-20 4134-node/23725-tetrahedron probe.
  The WSL kernel log records the OOM kill of its Python process at anonymous
  RSS 15008708 KiB. None of the requested prefix-630 `.msh`, entity-map or
  probe JSON files exists afterwards.
- Consequence: this supplies neither a positive mesh nor a negative
  triangulability theorem. The 630-ribbon gate remains open. Future work must
  partition the exterior and prove exact matching triangulations on every cut
  interface before independently verifying their simplicial gluing.

### F-539 — A balanced exterior partition must exactly clip ruled ribbons at its interfaces

- Severity: **Partitioned-frame design constraint**
- Status: **EXACT INTERFACE CLIPPING REQUIRED BEFORE BLOCK MESHING**
- Evidence: evaluating all 2520 saved rational ruled-ribbon triangles against
  axis-aligned cuts gives a best `z` cut that crosses only three triangles, but
  leaves essentially all triangles on one side. In contrast, the central
  `z=0` cut leaves 588 below and 736 above while crossing 1196 triangles.
  Thus a low-crossing single plane cannot balance the 630-ribbon workload.
- Consequence: a valid partitioned constructor must clip every crossed ruled
  triangle in exact rational arithmetic, triangulate the resulting interface
  polygons canonically, bind both adjacent block meshes to those same interface
  simplices, and verify the gluing recovers every original carrier triangle.
  Assigning a whole ribbon to a block by centroid or route index would leave
  unrepresented crossings and cannot certify a common frame.

### F-540 — The first exact two-block partition datum clips all selected-source ruled triangles

- Severity: **Partitioned-frame construction progress / not a frame**
- Status: **EXACT Z=0 INTERFACE DATA PASS; BLOCK MESHES AND GLUING OPEN**
- Evidence: `scripts/build_t73_selected_source_partition_z0.py` and
  `geometry/t73_selected_source_partition_z0.json`.
- Construction: all 2520 source carrier triangles are clipped against `z=0`
  with `Fraction` arithmetic. The two closed half-space records contain 3580
  nondegenerate triangle fragments and share 1128 exact interface segments.
  Rebuilding the artifact byte-for-byte verifies its source binding and all
  clipping output.
- Boundary: this is only the exact input for conforming block meshing. It does
  not contain tetrahedra, does not establish matching interface triangulations,
  and cannot be called a common 630-ribbon frame until both block meshes and a
  simplicial-gluing verifier exist.

### F-541 — The z=0 block interface now has a fixed rational triangulation with the four insertion holes

- Severity: **Partitioned-frame interface progress / two-dimensional only**
- Status: **COMMON INTERFACE TRIANGULATION PASS; BLOCK VOLUMES OPEN**
- Evidence: `scripts/build_t73_z0_interface_triangulation.py` and
  `geometry/t73_z0_interface_triangulation.json`.
- Construction: the plane `z=0` is triangulated as the outer square
  `[-20,20]^2` minus the four projected insertion squares. Its rational grid
  has 36 vertices and 42 triangles. Both future block meshes must use this
  exact interface simplex set.
- Boundary: no lower or upper tetrahedra have yet been generated, so this is
  neither a mesh gluing proof nor a tetrahedral-frame certificate.

### F-542 — The actual AR-to-Kirby generator now saves an explicit missing-data contract

- Severity: **Construction-program remediation / not a witness**
- Status: **OPEN CONTRACT SAVED; GEOMETRIC INPUT ABSENT**
- Evidence: `scripts/build_t73_actual_ar_kirby_construction_request.py`,
  `geometry/t73_actual_ar_kirby_construction_request.json`,
  `data/T73_AR_TO_KIRBY_PRESENTATION.schema.json`, and
  `scripts/verify_t73_ar_to_kirby_presentation.py`.
- Construction: the request is rebuilt from the hash-bound AR coordinate atlas.
  It enumerates the three missing chart transitions, all six t-bands and 1513
  x-bands requiring boundary edges/splices, the four handle feet, and the
  seven final Kirby components with their framing/dotted-circle requirements.
- Boundary: it deliberately remains `OPEN`; no band center, word, hash or
  declared status can substitute for the requested cut-and-surgery PL data.

### F-543 — A complete rational Kirby candidate is available for software exploration but has no AR equivalence witness

- Severity: **Exploratory construction / scope firewall**
- Status: **CANDIDATE_UNVERIFIED; NOT ACTUAL KIRBY DATA**
- Evidence: `scripts/build_t73_candidate_kirby_presentation.py`,
  `geometry/t73_candidate_kirby_presentation.json`, and
  `geometry/t73_candidate_kirby_export.json`.
- Construction: a separated rational seven-component model has complete closed
  cores, five push-offs, dotted circles and a standard-PD/framing export. It
  records the actual AR/t/x source hashes as provenance only.
- Boundary: it does not supply kappa_AR, any band boundary/splice, or a
  relative equivalence to the actual AR presentation. It cannot close P0, C,
  S, P3 or E13 and is retained only for downstream software experiments.

### F-545 — Candidate t/x band movies now have an independent exact record verifier

- Severity: **Candidate PL-movie validation / scope firewall**
- Status: **1519 BAND RECORDS PASS; ACTUAL KIRBY REPLAY OPEN**
- Evidence: `scripts/verify_t73_candidate_band_movies.py`,
  `tests/test_t73_candidate_band_movies.py`, and the saved t/x candidate movies.
- Verification: the independent verifier recomputes all 3035 rational
  rectangle and push-off segments, checks complete t/x coverage, source
  cancellation component/time order, continuous band centerlines, attachment
  and splice bindings, and the 1519-step candidate state chains. A state-chain
  mutation is rejected.
- Boundary: the current link states are identifiers, not complete post-slide
  polylines. The verdict is `PASS_CANDIDATE_MOVIE_RECORDS_ONLY`; it does not
  establish an actual Kirby move or kappa_AR.

### F-546 — All six t-band attachment endpoints are located in the actual AR records

- Severity: **Actual cancellation-data recovery / endpoints only**
- Status: **SIX SOURCE/TARGET LOCATORS VERIFIED; BAND SPLICES OPEN**
- Evidence: `scripts/build_t73_t_band_attachment_locators.py` and
  `geometry/t73_t_band_attachment_locators.json`.
- Verification: the six source endpoints uniquely equal actual AR core
  vertices at `m_1:1,17`, `m_2:1,1871`, and `m_3:1,8777`. Each target's first
  three rational coordinates equals its stored `parallel_h_CS_target`; the
  fourth mapping-torus parameter is saved explicitly.
- Boundary: these endpoint locators do not yet specify source/target intervals,
  full current link states, or the six actual band splices. Their scope is
  `VERIFIED_ENDPOINTS_ONLY`.

### F-547 — Six canonical rational t-band attachment intervals are now explicit

- Severity: **Actual endpoint refinement / candidate interval choice**
- Status: **INTERVALS EXPLICIT; ACTUAL BAND SLIDE STILL OPEN**
- Evidence: `scripts/build_t73_t_band_attachment_intervals.py` and
  `geometry/t73_t_band_attachment_intervals.json`.
- Construction: each source interval lies on the two actual AR core edges
  adjacent to its verified source vertex, using the saved positive band width
  as an exact rational interpolation parameter. Each target interval is the
  symmetric `u=1/2+-width` interval on its stored parallel h_CS target.
- Boundary: the endpoint locations are actual-record bindings; choosing this
  small interval is a canonical rational candidate. No current-link splice or
  actual Kirby slide is inferred from the interval alone.
- Independent verification: all six source intervals are exact subintervals
  of the actual lambda/mu core edges and contain their located core vertex;
  each target is an exact vertical subinterval of its parallel h_CS line and
  contains `u=1/2`. The verdict is
  `PASS_T_INTERVAL_ACTUAL_EDGE_BINDING_CANDIDATE_WIDTH`.
- Actual h_CS binding: subtracting the section point and dividing by the actual
  h_CS framing offset gives the ordered lane coefficients
  `-25,-15,-5,5,15,25`. All target intervals remain on their resulting
  vertical parallel copies. The independent verdict is
  `PASS_ACTUAL_HCS_PARALLEL_TARGET_BINDING`.

### F-548 — The first t-band slide now has an explicit closed candidate core

- Severity: **Sequential-splice construction progress / candidate only**
- Status: **BAND 0 CLOSED POLYLINE PASS; EMBEDDED KIRBY SLIDE OPEN**
- Evidence: `scripts/build_t73_candidate_t_band0_splice.py` and
  `geometry/t73_candidate_t_band0_splice.json`.
- Construction: the actual m1 core is cut at the verified band-0 source
  interval, joined along both candidate band-boundary lanes to the parallel
  h_CS target interval, traverses the mapping-torus complement through the
  seam, and returns to the retained m1 arc. Exact arithmetic verifies a closed
  nondegenerate 4D polyline.
- Boundary: self-disjointness, disjointness from the other link components,
  framed push-off transport and actual Kirby-slide equivalence remain open.

### F-549 — The first t-band splice requires a quotient-aware T3 lift before embeddedness testing

- Severity: **Coordinate-semantics correction / fail-closed gate**
- Status: **OPEN PERIODIC LIFT; NO SELF-INTERSECTION VERDICT**
- Evidence: `scripts/verify_t73_candidate_t_band0_splice.py`.
- Finding: interpreting the saved wrapped `core_polyline_T3xI` as an affine Q4
  polyline produces a first segment collision at indices 16 and 18. The source
  builder separately stores `C_i_universal_cover_lift`, confirming that the
  wrapped points encode a T3 quotient rather than a single affine chart.
- Consequence: the verifier returns `OPEN_PERIODIC_T3_LIFT_REQUIRED`; it does
  not call the curve self-intersecting. A continuous universal-cover lift with
  recorded deck translations is required before exact PL intersection tests.

### F-550 — The three wrapped AR cores now have verified continuous universal-cover lifts

- Severity: **Coordinate-semantics remediation / actual source data**
- Status: **VERIFIED CONTINUOUS LIFTS**
- Evidence: `scripts/build_t73_ar_core_universal_lifts.py` and
  `geometry/t73_ar_core_universal_lifts.json`.
- Verification: exact nearest-deck continuation lifts all wrapped T3 core
  vertices without half-period ambiguity. The closing deck translations for
  m1,m2,m3 are `(-1,0,1)`, `(269,40,0)`, `(1240,189,31)`, exactly the columns
  of `A-I`. All step coordinates and offsets are retained.
- Consequence: affine PL intersection checks for sequential band splices must
  use these lifts and their deck translations, never the wrapped coordinate
  list as an ordinary Q4 polyline.

### F-551 — Band 0 now has a quotient-aware universal-cover candidate splice

- Severity: **Sequential-splice coordinate repair / candidate only**
- Status: **QUOTIENT CLOSURE VERIFIED; EMBEDDED KIRBY SLIDE OPEN**
- Evidence: `scripts/build_t73_candidate_t_band0_quotient_splice.py` and
  `geometry/t73_candidate_t_band0_quotient_splice.json`.
- Construction: the retained actual m1 arc is followed in its verified
  universal-cover lift; the candidate band boundary and parallel h_CS
  complement are placed in the corresponding deck translate. The final point
  equals the initial point translated by `4*(-1,0,1)`, so the path closes in
  T3 with exactly the m1 column of A-I.
- Independent check: the unique direct `u=0` to `u=1` transition is typed as a
  mapping-torus seam gluing cell, not an affine segment through the removed
  target interval. The remaining 31-segment quotient path passes all seven
  exact deck-translate intersection candidates and reports
  `PASS_CANDIDATE_QUOTIENT_FRAMED_EMBEDDEDNESS_ONLY`. The same verifier
  independently reconstructs every push-off vertex, checks the identical
  closing deck translation, and rejects any core/push intersection; twelve
  exact core-versus-push deck candidates pass.
- Partial external clearance: 453 exact deck-translate intersection candidates
  prove that the candidate post-slide core misses the actual m2 and m3
  universal-cover cores, reporting `PASS_CANDIDATE_M2_M3_CLEARANCE_ONLY`.
- Candidate dual clearance: the three dual-cell boundaries have exact
  zero-deck-translation lifts after the explicit candidate choice `u=1/2`.
  Including them gives `PASS_CANDIDATE_FRAMED_ALL_CORE_CLEARANCE_ONLY` for both
  the post-slide core and its push-off against all five other attaching cores;
  906 exact deck candidates pass.
- Boundary: the dual fiber level is not yet an actual AR chart transition;
  framed push-off embeddedness and actual Kirby-slide equivalence remain open.

### F-552 — Six t-band framing extensions match the actual source and h_CS boundary normals

- Severity: **Framed-slide construction progress / candidate interior**
- Status: **BOUNDARY FRAMINGS VERIFIED; INTERIOR EXTENSION CANDIDATE**
- Evidence: `scripts/build_t73_t_band_framing_extensions.py`,
  `scripts/verify_t73_t_band_framing_extensions.py`,
  `geometry/t73_t_band_framing_extensions.json`, and its test.
- Verification: every source normal is recomputed as the moved component's
  actual product direction times its saved width; every target normal equals
  the actual h_CS framing offset. All six linear normal homotopies are nonzero,
  and every rational push-off vertex is independently checked as center plus
  normal.
- Boundary: linear interpolation by centerline vertex index is a canonical
  interior choice. Its global disjointness and actual Kirby-framing transport
  remain open.

### F-553 — Band 0 now has a complete triangulated candidate band disk

- Severity: **Kirby-slide surface construction / candidate combinatorics**
- Status: **FRAMED DISK COMBINATORICS PASS; AMBIENT EMBEDDEDNESS OPEN**
- Evidence: `scripts/build_t73_candidate_t_band0_surface.py`,
  `scripts/verify_t73_candidate_t_band0_surface.py`,
  `geometry/t73_candidate_t_band0_surface.json`, and its test.
- Verification: four rational cross-sections connect the actual source
  attachment interval, both candidate band lanes and the parallel h_CS target
  interval. Six nondegenerate triangles form an 8-vertex disk with Euler
  characteristic one and exactly the declared source/left/target/right
  boundary. The independent verifier reconstructs every framed push-off vertex.
- Local embeddedness: NumPy AABB screening followed by exact rational
  barycentric, segment-triangle and vertex-containment equations checks the two
  nonadjacent triangle pairs whose boxes overlap. Both are disjoint, giving
  `PASS_CANDIDATE_FRAMED_BAND_DISK_AND_PUSH_LOCAL_EMBEDDEDNESS_ONLY`. Two
  nonadjacent push-surface pairs and 28 disk-versus-push pairs also pass the
  exact low-rank intersection algorithm.
- Other-core clearance: the disk and push disk are compared against actual
  m2/m3 and candidate-lifted r_xy/r_yz/r_zx. All 128184 quotient
  triangle/segment pairs are rejected by exact disjoint AABBs, yielding
  `PASS_CANDIDATE_BAND_SURFACE_OTHER_CORE_CLEARANCE_ONLY`.
- Relative-boundary binding: the independent verifier checks that the disk's
  source edge is exactly the lifted actual m1 attachment interval, its target
  edge is exactly the parallel h_CS interval, both remaining boundary chains
  equal the candidate movie lanes, and the endpoint normals equal the actual
  source/target framing records. It reports
  `PASS_CANDIDATE_BAND0_RELATIVE_BOUNDARY_ONLY`.
- Relative-contact closure: exact segment-triangle parameter intervals find six
  m1 contacts and three parallel-h_CS contacts. Every interval endpoint lies
  on the declared source or target attachment edge; no extra curve contact is
  present. The verifier reports
  `PASS_CANDIDATE_BAND0_RELATIVE_CONTACTS_ONLY`.
- Remaining boundary: the actual Kirby-slide/reconnection interpretation and
  the remaining five t-bands are open.

### F-554 — All six t-band disks are explicit in the actual t-belt collar, but only as a sequential candidate movie

- Severity: **Sequential Kirby-movie construction / candidate framing interior**
- Status: **SIX INDIVIDUAL COLLAR DISKS PASS; CURRENT-LINK REPLAY RESOLVED IN F-556**
- Evidence: `scripts/build_t73_t_band_collar_surfaces.py`,
  `scripts/verify_t73_t_band_collar_surfaces.py`,
  `geometry/t73_t_band_collar_surfaces.json`, and its test.
- Actual-coordinate binding: every centerline is the stored AR cancellation
  centerline at `u=1/2`, and every one of its spatial vertices lies exactly on
  the octahedral t-belt sphere. The first and last cross-sections are exactly
  the independently bound source and parallel-h_CS target intervals.
- Exact PL verification: all six triangle complexes have Euler characteristic
  one and precisely the declared four-part boundary. Nonadjacent triangles of
  each individual disk pass exact rational intersection checks. The six
  `movie_time_order` values form the total order `0,1,2,3,4,5`.
- Sequentiality evidence: after the current-link-safe rational reroutes, 236
  exact inter-band triangle comparisons find spatial intersections for band
  pairs `(0,2)`, `(0,4)`, `(1,4)`, and `(2,4)`. These
  are retained in the verifier result and are valid only because the disks
  occur at distinct movie times; the construction makes no simultaneous
  disjointness claim.
- Boundary at this layer: normal fields agree with the actual source and h_CS
  target records, while their interiors are canonical choices. The collar-only
  verdict remains `PASS_T_BAND_COLLAR_DISKS_SEQUENTIAL_CANDIDATE_FRAMING_ONLY`;
  F-556 supplies the missing current-link replay, attachment rebinding, and
  inverse checks for the six-slide sequence.

### F-555 — The first t-band now gives a verified sequential framed Kirby state transition

- Severity: **Actual sequential Kirby reconstruction / first move only**
- Status: **STATE 0 TO STATE 1 PASS; FIVE t-SLIDES REMAIN**
- Evidence: `scripts/build_t73_t_band0_sequential_state.py`,
  `scripts/verify_t73_t_band0_sequential_state.py`,
  `geometry/t73_t_band_sequential_state_01.json`, and its test.
- Construction: the actual lifted m1 core is cut at its independently bound
  source interval. The retained complement is joined to the two verified
  collar-disk boundary lanes and the complement of the specified framed
  parallel of h_CS. The resulting 27-segment lift closes by the original m1
  deck translation, and its pointwise normal field closes by the same deck
  translation.
- Independent verification: every output piece and normal is recomputed from
  the source lift and collar disk. Exact quotient tests prove core and push-off
  embeddedness and mutual separation. The disk contacts m1 and the chosen
  h_CS parallel only on the declared attachments; the disk, its push-off, and
  every newly introduced curve piece avoid actual m2, m3, and h_CS. Clearance
  from r_xy/r_yz/r_zx is certified by exact spatial-projection separation, so
  it is independent of an arbitrary dual-core fiber coordinate. There are 244
  exact stationary-clearance comparisons.
- Inverse move: cutting away the band-sum pieces and restoring the removed
  two-edge source subarc exactly recovers the cyclically refined actual m1
  universal-cover lift, with its original closing deck translation. The
  verdict is `PASS_T_BAND0_SEQUENTIAL_FRAMED_KIRBY_SLIDE`.
- Boundary at this layer: this certifies one concrete legitimate framed slide.
  F-556 extends it through the remaining five t-slides. The 1513 x-slides,
  final cancellation, and kappa_AR remain outside F-555.

### F-556 — All six t-band slides now replay as verified current-link state transitions

- Severity: **Actual sequential t-cancellation geometry / six-slide prefix**
- Status: **SIX FRAMED SLIDES PASS; t-h_CS CANCELLATION AND x-MOVIE OPEN**
- Evidence: `scripts/build_t73_t_band_sequential_movie.py`,
  `scripts/verify_t73_t_band_sequential_movie.py`,
  `geometry/t73_t_band_sequential_movie.json`, and its test.
- Current-state binding: each source interval is located uniquely in the
  immediately preceding moved-component lift. Wrapped input intervals require
  base deck translations `(0,0,0)`, `(0,0,1)`, `(0,0,0)`, `(269,41,0)`,
  `(0,0,0)`, and `(1240,189,32)`; these are derived rather than assumed.
- Routing repair: the scheduled chords for bands 2, 4, and 5 met link
  components retained from earlier states. Deterministic finite rational
  searches supplied the shortest current-link-safe belt-sphere routes, using
  radius fractions `[(0,3/4,1/4)]`, `[(1/4,1/2,1/4)]`, and
  `[(1/4,-3/4,0),(3/4,0,1/4)]`. Every route edge lies on a common supporting
  face of the octahedral belt sphere. Endpoints and boundary framings are
  unchanged.
- Orientation and seam correction: odd source intervals reverse the target
  interval order to prevent a collapsed/twisted ribbon. Their h_CS complements
  traverse the mapping-torus seam as `1 -> 0`; even bands use `0 -> 1`.
  Earlier seam cells are reindexed and propagated through later cuts.
- Independent verification: seven complete current-link manifests and all six
  inverse moves replay from the source files. Exact checks cover 18 source and
  12 target triangle contacts, 80 incremental framed-curve pairs, 2140 new
  piece versus stationary/dual pairs, and 726 disk versus other-component
  pairs. The final vertex counts are m1=35, m2=1891, and m3=8799. The verdict
  is `PASS_SIX_T_BAND_SEQUENTIAL_FRAMED_KIRBY_SLIDES`.
- Storage: the 64-KiB artifact is a complete deterministic delta movie with
  source/target lifts, deck placements, piece ranges, seam data, state
  manifests, geometry hashes, and inverse certificates. Expanded point and
  normal arrays are recomputed exactly, avoiding a redundant 73-MiB snapshot.
- Boundary: this closes the six-slide geometric prefix only. A separately
  verified framed cancellation of t against h_CS must consume state 6 before
  the 1513-step x-m1 movie can start; neither is inferred here.

### F-557 — State-6 cores clear the t-ball and the framing has an explicit outward exteriorization

- Severity: **Framed t-h_CS cancellation readiness / final local gate**
- Status: **FRAMING EXTERIORIZATION PASS; CELLWISE CANCELLATION MAP OPEN**
- Evidence: `audit/t73_t_hcs_cancellation_readiness.json`,
  `geometry/t73_t_hcs_framing_exteriorization.json`, their two builders,
  `scripts/verify_t73_t_hcs_framing_exteriorization.py`, and both tests.
- Fail-closed diagnosis: exact piecewise-linear L1 minimization at every
  coordinate-zero breakpoint proves that all nonseam state-6 core segments
  remain outside or on the t-belt octahedron. The original framing push-offs,
  however, had four segments entering the open t-ball: m1 segments 27 and 33,
  and m3 segments 8789 and 8797. Therefore the legacy `status=PASS`,
  `geometric_intersection=1`, and `t_passages_after=0` fields were not accepted
  as a cancellation proof.
- Construction: at each belt-sphere vertex, a deterministic finite search in
  `{-1,0,1}^3 * width/16` chooses the squared-nearest normal with positive dot
  product against every adjacent octahedral supporting face and excludes
  vectors parallel to incident core edges. Deck-equivalent first/last normals
  are constrained together. This replaces 63 normal vertices without changing
  any core curve.
- Independent verification: every replacement is recomputed; the linear old
  to new normal homotopy avoids the zero section. All exteriorized push-off
  segments have exact minimum L1 clearance `width/16` above the belt radius.
  134 exact changed-push versus all core/push quotient checks pass. The verdict
  is `PASS_STATE6_FRAMING_EXTERIORIZATION`.
- Readiness result: the saved report retains the four original obstructions
  and separately verifies zero exteriorized obstructions, returning
  `READY_FOR_EXPLICIT_T_HCS_CANCELLATION_MAP`.
- Boundary: a conventional cancellation theorem now applies once its local
  identification is instantiated, but the repository still needs the actual
  finite collar cell complex and cellwise map deleting t and h_CS and carrying
  the three exteriorized framed components into the post-cancel boundary.

### F-558 — A finite orientation-preserving collar ejection map now precedes the t-h_CS deletion

- Severity: **PL cancellation-map construction / collar part**
- Status: **COLLAR EJECTION PASS; 4D HANDLE-PAIR DELETION OPEN**
- Evidence: `scripts/build_t73_t_hcs_collar_ejection_map.py`,
  `scripts/verify_t73_t_hcs_collar_ejection_map.py`,
  `geometry/t73_t_hcs_collar_ejection_map.json`, and its test.
- Construction: each of the eight belt-octahedron faces is thickened from
  radius r to 2r and its triangular prism is divided into three tetrahedra.
  The simplicial vertex map sends the inner six vertices from r to 3r/2 and
  fixes all six outer vertices at 2r; it is the identity outside 2r.
- Independent verification: the 12-vertex, 24-tetrahedron source has exactly
  the two declared octahedral boundary spheres (16 boundary triangles). Every
  source/image tetrahedron is nondegenerate, every affine determinant ratio is
  positive, and the minimum ratio is 1/2. The map is therefore a finite PL
  homeomorphism from the complement of the open r-octahedron to the complement
  of the open 3r/2-octahedron, fixed on the outer boundary. F-557 proves the
  exteriorized state-6 framed link lies in its domain.
- Verdict and boundary: `PASS_T_HCS_COLLAR_EJECTION_CELL_MAP` has explicit
  scope `COLLAR_EJECTION_ONLY_HANDLE_PAIR_DELETION_OPEN`. The next witness must
  triangulate the standard 4D cancelling t/h_CS handle pair, identify its
  attaching/belt cells with the actual AR cells, delete that PL 4-ball, and
  emit the carried post-cancel framed-link state consumed by the x movie.

### F-600 — The “actual” sphere-system builder assigns, rather than constructs, the embedding in \(\partial W_2\)

- Severity: **Critical**
- Status: **CONFIRMED; FIRST MISSING GEOMETRIC DATUM**
- Locations: `main.tex:1365--1401`, Proposition `thm:Sgeometry` at
  `main.tex:1436--1451`, Theorem `thm:Sdischarge` at `main.tex:1524--1533`;
  `scripts/build_t73_actual_sphere_system.py:79--109` and `:111--152`;
  `scripts/build_t73_three_handle_surface_transport.py:83--123`;
  `scripts/verify_t73_actual_sphere_system.py:30--49`.
- Evidence: the builder copies three cube-boundary spheres from an abstract
  reversed model, then assigns `embedded_s2_on_actual_W2`, disjointness,
  connected complement, identification with partial \(W_2\), and
  simultaneous surgery-to-\(S^3\) as booleans. The lower “surface transport”
  contains boundary words, counts, and hashes, but no vertices/triangles of
  the transported surfaces and no ambient map; its embeddedness and relative
  map are again assigned. The verifier checks the assigned booleans, counts,
  and Euler arithmetic.
- First missing datum: a common triangulated model of the actual
  \(\partial W_2\), explicit embeddings of the three spheres and detector
  ball, and a checked ambient map through every genuine Kirby move; or a
  complete conventional Kirby proof providing the same identifications.
- Source limitation: Horvat--Jab\l{}onowski Theorem 5.3 can compare a *given
  geometric basis* with the actual attaching system. A unimodular homology
  matrix does not construct the embedded geometric basis in the actual
  boundary.
- Dependency impact: S and the asserted post-three-handle boundary are not
  established.

### F-601 — The hemisphere verifier computes only a local Frobenius scalar and assigns the whole-source MWW factorization

- Severity: **Critical**
- Status: **CONFIRMED; FIRST MISSING CATEGORICAL THEOREM**
- Locations: Lemma `lem:Sendpoint`, `main.tex:1455--1509`, especially its own
  caveat at `:1506--1508`; `scripts/verify_t73_hemisphere_movies.py:63--96`
  and `:99--172`.
- Evidence: the finite function correctly computes
  \(\epsilon^{\otimes b}\Delta^{b-1}(1)=0\) and
  \(\epsilon^{\otimes b}\Delta^{b-1}(X)=1\). The builder then assigns
  `PASS_ACTUAL_C_COCONE`, identical endpoint maps, identity/zero detector
  actions, compatibility on all source summands, and finally
  `actual_w2_lasagna_map=True`. No Khovanov complex, MWW hemisphere map,
  natural transformation, or quotient-compatibility square is constructed.
- Missing theorem: for every cable summand and each actual sphere, identify
  both MWW hemisphere maps under the genuine C comparison with an old-source
  map tensor the punctured-sphere TQFT map, compatibly with every beta/psi
  relation, pivotal/orientation map, and passage to the two-handle quotient.
- Source limitation: MWW Theorems 3.7/3.10 and Example 3.8 provide the
  coequalizer and local essential-sphere relation, not this new detector
  factorization. Strict functoriality removes sign ambiguity inside its own
  theory; it does not prove the asserted tensor factorization.
- Dependency impact: the detector is not shown to descend through any actual
  three-handle coequalizer, even if the topology in F-600 is granted.

### F-602 — P3 has a valid conditional upper-handle proof, but the current certificate lacks the boundary recognition and attaching map

- Severity: **Critical as currently claimed; conditional argument valid**
- Status: **OPEN**
- Locations: Theorem `hyp:P3`, `main.tex:279--303`, final identifications at
  `main.tex:1535--1546`; `scripts/certify_t73_p3_four_handle.py:77--112`,
  `:172--209`, and `:233--257`.
- Evidence: if a genuine P0 diffeomorphism transports the *entire* original
  AR handle decomposition, then its original three 3-handles leave the
  original 4-handle boundary \(S^3\), and the transported original 4-handle
  supplies the attachment. Laudenbach--Po\'enaru removes upper-handle gluing
  ambiguity under the same established boundary hypotheses. This is a sound
  conditional proof.
- Present gap: the P3 script calls boundary-dual surgery a “1--3
  cancellation,” trusts the sphere-system booleans, and constructs only an
  abstract cubical \(I^4\). It supplies no recognition of the actual
  surgered boundary and no orientation-compatible PL homeomorphism
  \(\partial I^4\to\partial W_3\). Homology or an identity dual-loop pairing
  does not recognize \(S^3\).
- Correct language: the 3-handle attaches along a sphere which appears as a
  belt sphere in an upside-down boundary 1-handle presentation; there is no
  index-1/index-3 handle cancellation or canceling “1--3 pair.”
- Dependency impact: MWW Proposition 3.4 is correctly cited for an actual
  empty-link 4-handle, but its geometric premise is not discharged.

### F-603 — The absolute degree 494 has not been reconciled with the Manolescu--Neithalath grading erratum

- Severity: **Major**
- Status: **OPEN**
- Locations: `main.tex:258`, `main.tex:294--299`, grading calculation in
  `sec-finite-details.tex:257--276`, and S endpoint argument
  `main.tex:1495--1503`.
- Primary-source evidence: the author-posted erratum to Manolescu--Neithalath,
  *Skein lasagna modules for 2-handlebodies*, corrects the rational
  normalization by the writhe shift \(\{-(N-1)w(L)\}\), and corrects its
  equation (6). It says the rest of that paper is unaffected because it uses
  the \(\operatorname{KhR}_2\) convention, but every conversion to ordinary
  Khovanov conventions must retain this term.
- Gap: the ledger \(-44+227+315-4=494\) does not mention the erratum. Total
  writhe zero for the 11,340-letter detector braid does not establish zero
  correction for every oriented closure/cable summand, cup/cap map, and
  hemisphere map. No single-convention grading table is given.
- Required resolution: list the exact oriented diagram and writhe for each
  complex and the degree of each cobordism, including the corrected
  \(-(N-1)w\) term, then prove the whole-source maps of F-601 have absolute
  degree zero. Degree 494 may survive, but it is not presently proved.

### F-604 — Constructive closure attempt stops at two independent missing interfaces

- Severity: **Critical summary**
- Status: **BLOCKED BY MISSING MATHEMATICAL DATA (not by computation time)**
- Location: `docs/proofs/T73_S_P3_PAPER_PROOF.md`.
- Result: the local Frobenius identity is proved, and P3 is standard
  conditional on a transported full AR handle decomposition. Unconditional
  closure first requires (i) the actual embedded sphere/ambient-boundary data
  of F-600 and (ii) independently, the natural whole-source MWW comparison of
  F-601. After those, a transported or explicit 4-handle attaching map and
  the corrected grading ledger of F-603 are still required.

### F-605 — Existing lower-handle metadata cannot generate the required common \(\partial W_2\) triangulation

- Severity: **Critical**
- Status: **CONFIRMED / OPEN CONSTRUCTION**
- Locations: `geometry/t73_actual_W2_boundary.json`;
  `geometry/t73_actual_ar_link.json`; builders summarized in
  `docs/proofs/T73_S_P3_PAPER_PROOF.md`, Section 8.
- Evidence: the W2 artifact contains hashes, handle counts, a desired
  homeomorphism-type string, and a detector cube, but no tetrahedra or face
  gluings for the actual post-2-handle boundary. The AR railroad curves and
  attaching words likewise do not specify a triangulated attaching-region
  complement or the face identifications resulting from all five 2-handle
  surgeries. Therefore no deterministic builder can recover a unique common
  boundary triangulation from the committed data.
- Required next construction: triangulate the 0/1-handle boundary, embed
  framed solid-torus attaching regions for all five 2-handles, perform the
  Dehn fillings simplicially, and transport the detector and three sphere
  surfaces into that same output complex.
- Dependency impact: G-S1 cannot be synthesized by rearranging existing
  hashes or owner ledgers.

### F-606 — New G-S1/G-P3 gate fails closed on current data and refuses unreplayed surgery receipts

- Severity: **Major (positive infrastructure result)**
- Status: **CONFIRMED**
- Locations: `audit/t73_gs1_gp3_schema.json`;
  `scripts/verify_t73_gs1_gp3.py`; `tests/test_t73_gs1_gp3_gate.py`.
- Contract: the gate requires a closed tetrahedral \(\partial W_2\), three
  embedded triangular 2-sphere subcomplexes, a disjoint shellable detector
  ball, a bound explicit cut-and-cap trace, a recognized \(S^3\) result, an
  explicit 4-ball, and a simplicial attaching isomorphism. It derives the
  finite incidence, surface, disjointness, shelling, boundary, and
  simplicial-isomorphism predicates instead of reading PASS booleans.
- Current result: `python3 scripts/verify_t73_gs1_gp3.py --check-current`
  returns `verdict=OPEN`, `G_S1=OPEN`, and `G_P3=OPEN` because the current W2
  JSON is metadata rather than a witness. Three unit tests pass and confirm
  that the current artifact and boolean-only substitutes are rejected.
- The initially missing `explicit_simplicial_cut_cap/v1` primitive is now
  implemented as recorded in F-607. Current T73 data still fail before that
  stage because they contain no ambient boundary triangulation.

### F-607 — Explicit simplicial normal-sphere surgery now has replayed finite semantics

- Severity: **Major (positive infrastructure result)**
- Status: **CONFIRMED**
- Locations: `scripts/verify_t73_gs1_gp3.py`, functions
  `canonical_prism_tetrahedra`, `replay_cut_cap_step`, and
  `replay_normal_surgery_trace`; schema
  `audit/t73_gs1_gp3_schema.json`; tests
  `tests/test_t73_gs1_gp3_gate.py`.
- Semantics: for each attaching sphere, the witness gives a disjoint parallel
  vertex copy. The verifier independently derives the staircase
  triangulation of \(S^2\times I\), requires exactly that tetrahedron
  subcomplex, verifies that its boundary is precisely the two sphere copies,
  removes it, appends two new cap vertices, cones both copies, and requires
  exact equality with the next closed combinatorial 3-manifold. Vertex links
  are checked to be triangulated 2-spheres. Product neighborhoods must miss
  the detector and the other attaching spheres. The final complex is bound
  to the trace and then to the explicit \(S^3\) recognition and 4-ball
  attaching isomorphism.
- Synthetic validation: a 36-tetrahedron cyclic three-slab triangulation of
  \(S^2\times S^1\) contains a canonical 12-tetrahedron
  \(S^2\times I\) neighborhood. Removing it and coning its two boundary
  spheres replays to a closed 32-tetrahedron surgery result. Mutations deleting
  a prism tetrahedron or altering the claimed result are rejected.
- Test result: six focused unit tests pass. The current T73 W2 metadata still
  returns `G_S1=OPEN`, `G_P3=OPEN`; no candidate topology is inferred.

### F-608 — A genuine reduced-boundary triangulation prefix exists, but the attaching-link embedding is absent

- Severity: **Major (positive prefix; critical remaining gap)**
- Status: **PARTIAL**
- Locations: `scripts/build_t73_reduced_boundary_prefix.py`;
  `tests/test_t73_reduced_boundary_prefix.py`;
  `docs/proofs/T73_W2_TRIANGULATION_PREFIX.md`.
- Verified prefix: two 36-tetrahedron staircase triangulations of
  \(S^2\times S^1\) are simplicially connected-summed by deleting one
  tetrahedron from each and applying an explicit reversed boundary vertex
  identification. The result has 20 vertices and 70 tetrahedra. Closed face
  pairing, connectedness, absence of duplicates/unused vertices, and
  2-sphere vertex links are derived. Two embedded three-edge generator loops
  are labelled \(y,z\).
- Boundary-update primitive: a canonical 27-tetrahedron solid torus has
  explicit core, meridian, and longitude edge loops. A deterministic Dehn
  filling verifier requires the removed neighborhood to be simplicially
  identical to that solid torus, checks the attaching core and filling
  meridian/framing curve, deletes the removed interior vertices, canonically
  reindexes surviving vertices, requires three explicitly fresh filling-core
  vertices, performs the tetrahedron replacement, and compares the exact
  closed result. A synthetic double-solid-torus filling passes; framing,
  removed-interior reuse, and boolean-only mutations fail.
- First unavailable field: no existing artifact gives a common subdivision
  and simplicial embedding of all five post-cancellation railroad components
  and their framing annuli into this (or another explicit) reduced-boundary
  triangulation. Consequently no actual five-step W2 boundary construction
  can yet be run. Words and PD owner records do not determine this embedded
  framed-link map.
- Tests: three focused tests pass; boundary digest is
  `A389BDA2DDF42D88E504DFF694BA92CC19476A23D886FC19814A149D80CFAE49`.

### F-609 — Transporting the complete AR decomposition can close E13/P3, but not S

- Severity: **Critical distinction / constructive simplification**
- Status: **CONDITIONAL**
- Locations: conceptual proof in
  `docs/proofs/T73_S_P3_PAPER_PROOF.md`, Section 9; current uses at
  `main.tex:977--986` and `main.tex:1535--1546`.
- Exact conditional theorem: a genuine splitting-preserving
  \(\psi\simeq f_A\) relative to the section gives the full AR handle
  decomposition of \(\Sigma_A^0\). Genuine framed handle slides and
  complementary 1/2 cancellations induce boundary diffeomorphisms. If every
  unattached 3/4-handle attaching map is transported by those
  diffeomorphisms, the resulting complete Johnson decomposition presents the
  same manifold. Defining \(X_J\) as that full transported decomposition
  makes \(X_J\cong\Sigma_A^0\), the post-three-handle \(S^3\), and its
  4-handle attachment tautological. No W2 triangulation or
  Laudenbach--Poenaru theorem is needed for this identification.
- Remaining P0 dependency: the theorem requires the global relative Johnson
  diffeomorphism and genuine whole-link framed cancellation movies. The
  current finite certificates do not establish those premises (F-102,
  F-106, F-107). Naming their hash-linked stages “transport” is circular.
- Why S remains open: the transported full decomposition supplies actual
  embedded 3-handle spheres and hence actual MWW hemisphere maps, but it does
  not evaluate those maps under the new detector. Sphere-system uniqueness
  or upper-handle naturality can identify total kernels after a genuine
  geometric basis is supplied; neither proves the whole-source tensor
  factorization and beta/psi compatibility required in F-601.
- Conclusion: this route can legitimately remove the independent P3/E13
  construction from the proof once P0 is proved, but it cannot establish the
  nonzero class after the 3-handles. If \(X_J\) remains defined by the
  independently modelled standard-sphere/P3 artifacts, asserting that it is
  the transported decomposition simply renames the missing equivalence.

### F-610 — Making B44 auxiliary permits boundary disjointness but does not yield the MWW tensor factorization

- Severity: **Critical**
- Status: **CONFIRMED PARTIAL LEMMA / REMAINING OBSTRUCTION**
- Locations: analysis in
  `docs/proofs/T73_S_P3_PAPER_PROOF.md`, Section 10; S argument at
  `main.tex:1455--1509`.
- Positive result: after the actual upper spheres are fixed, an independently
  chosen small detector ball can be placed in their boundary complement. If
  the coefficient object, detector, and both hemisphere maps admit a literal
  tensor separation and the MWW-to-endpoint comparison is symmetric-monoidal
  natural for those maps, strict monoidality proves
  \(\operatorname{Id}\otimes\epsilon^{\otimes b}\Delta^{b-1}\) on the whole
  source. This is the exact separated-support lemma.
- Failure of its hypotheses here: the 44 detector lanes are selected passages
  of the same 2-handle components on which the transported spheres have
  \(12578,1824,409\) core-boundary copies. Their cable endpoints are
  interleaved, so boundary disjointness of a small ball does not provide a
  tensor decomposition of the MWW source. Pulling both constructions into
  the 4-dimensional handle formula produces pairs of 2-surfaces; relative
  transversality gives isolated intersections because \(2+2=4\), not
  disjointness. No intersection-removal/Whitney data are supplied.
- Mixed maps: strict functoriality controls composition and signs but does not
  remove braid/pivotal maps between interleaved endpoints. Showing that they
  are \(P(I+O(h))\) with simultaneous detector conjugation is exactly the
  missing C-S1 naturality theorem.
- Circularity: if B44 is replaced by a genuinely local tensor-separated
  class, S follows formally, but the candidate-specific beta/psi descent and
  the scalar 2624 must be established anew. Assigning the old computation to
  that new class merely renames the missing geometric comparison.

### F-611 — MWW reduces S to an actual surface map, but the statewise shadow on that map is missing

- Severity: **Critical**
- Status: **CONDITIONAL THEOREM PROVED; CANDIDATE HYPOTHESES OPEN**
- Locations: MWW Theorem 3.10 proof, equations (12)--(15); detailed theorem
  in `docs/proofs/T73_S_P3_PAPER_PROOF.md`, Section 11; manuscript
  Lemma `lem:Sendpoint`, `main.tex:1455--1509`.
- Source clarification: after deleting a small hemisphere disk and all
  2-handle cores, MWW obtains
  \(\Sigma_-\subset I\times\partial W_1\). Their commuting diagram proves
  that the nontrivial hemisphere map under the 2-handle isomorphism is the
  cabled skein-lasagna map induced by \(\Sigma_-\). Thus MWW itself supplies
  beta/psi compatibility of that surface map; it does not supply compatibility
  with the proposed detector.
- Conditional result: if a completed statewise shadow is defined and natural
  on every elementary event in a typed movie for \(\Sigma_-\), is symmetric
  monoidal modulo \(h\), all mixed events are
  \(P(I+O(h))\), and the detector rows use the same equivariant permutation
  convention and start in order \(h^3\), then the divided cubic sees exactly
  \(\operatorname{Id}\otimes
  \epsilon^{\otimes b}\Delta^{b-1}\). Interleaving is harmless under these
  hypotheses: constant permutations move through the commutative,
  cocommutative Frobenius operations and cancel at the endpoints, while every
  \(O(h)\) correction changes only order \(h^4\).
- Exact missing data: the all-owner artifact has no typed chronology of all
  mixed Reidemeister/braid/pivotal events; the shadow is not constructed on
  the actual births/deaths/saddles; its naturality squares with every beta/psi
  generator are absent; and constant mixed maps are not proved to match the
  detector's pivotal/permutation convention. JSON assigns the desired
  `PASS_ACTUAL_C_COCONE` conclusion instead.
- Dependency impact: this is a precise sufficient theorem for completing S,
  and shows interleaving is not inherently fatal. It also identifies the
  irreducible missing interface: a statewise monoidal-natural shadow on the
  actual typed \(\Sigma_-\) movie.

### F-612 — The finite typed \(\Sigma_-\) movie prefix is closed; shadow naturality remains open

- Severity: **Major positive result / Critical remaining interface**
- Status: **PARTIAL**
- Locations: `scripts/build_t73_sigma_minus_typed.py`;
  `tests/test_t73_sigma_minus_typed.py`;
  `docs/proofs/T73_S_P3_PAPER_PROOF.md`, Section 12.
- Derived data: for all three owner boundary words, the builder recomputes
  signed owner positions and profiles, the cable-state shifts, explicit
  stable endpoint permutations and inverses, old/new tensor-factor types, and
  parameterized event blocks. The movies have zero births,
  \(b-1\) coproduct saddles and \(b\) restored-core caps for
  \(b=12578,1824,409\).
- Formal MWW consequences: beta preserves multiplicity types; psi pair
  addition commutes componentwise with every surface translation. Thus both
  paths of every beta/psi type square agree. MWW equations (12)--(15) supply
  the induced \(\Sigma_-\) map on the cabled quotient. The local Frobenius
  evaluation is verified as zero on \(1\) and one on \(X\); direct expansions
  through \(b=6\) test the general formula.
- Mutation coverage: changing a sign in an actual owner word breaks the
  recomputed profile; an invalid owner label is rejected; endpoint
  permutations are checked bijective with explicit inverses.
- Remaining map, intentionally OPEN:
  `StatewiseShadowNaturality_Aj` for each sphere. It must define shadow
  maps for the typed critical and mixed events, prove
  \(P(I+O(h))\), detector permutation equivariance, and actual beta/psi
  naturality equalities. Type compatibility does not prove these maps commute.
- Test result: four focused tests pass; generated digest
  `6B680BF1EE75336DD357DCD7B44546D360D1C303460069401DCCFE8EF88D7E23`.
  The generated status remains `S_status=OPEN`.

### F-613 — Cyclic \(m_2\) connector standardization is conditionally harmless but presently undecidable from the artifacts

- Severity: **Critical remaining C/P0 interface**
- Status: **OPEN**
- Locations: `main.tex:1412--1421`;
  `geometry/t73_actual_product_rectangles.json#/rectangles/43`;
  `docs/proofs/T73_CYCLIC_CONNECTOR_ISOTOPY.md`.
- Exact sufficient theorem: in the complement of both insertion boxes, all
  fixed link strands, cancellation collars, and 227 leftover tracks, an
  embedded rectangle between the actual and desired proper arcs, with fixed
  endpoint germs and zero relative framing twist, gives a framed arc isotopy.
  Isotopy extension then gives an ambient boundary isotopy. Transporting the
  whole framed attaching link and every upper-handle attaching map preserves
  the complete \(\Sigma_A^0\) presentation and all linking/framing data.
- Necessary obstruction hierarchy: the relative groupoid element
  \([a_0\bar a_1]\in\pi_1(M\setminus F)\), its linking/intersection
  abelianization, the relative framing integer in \(\pi_1(SO(2))\), and local
  proper-arc knotting. The complete invariant is the component in
  \(\pi_0\operatorname{Emb}^{fr}_{\partial}(I,M\setminus F)\).
- Current evidence: the record supplies a bottom-side polyline, a referenced
  z-lane, two band hashes, and a prose transport rule. It supplies neither
  the cyclic connector in one common complement nor the fixed complement,
  a rectangle/isotopy movie, groupoid word, or twist computation.
- Conclusion: there is no proven obstruction showing the isotopy impossible,
  but even its first necessary invariant cannot be computed from present
  data. Replacing the connector without the relative framed isotopy may
  change the attaching link or framing and would not preserve the closed
  presentation by definition.

### F-614 — Independent MWW grading audit confirms degree 223 for the two-representable route

- Severity: **Critical correction; obstruction survives conditionally**
- Status: **CONFIRMED**
- Locations: `docs/proofs/T73_SHIFT_223_INDEPENDENT_AUDIT.md`;
  MWW `1handles.tex:140--156,173--192,242--274` and
  `kirby.tex:19--35,331--346`; conflicting manuscript ledger at
  `main.tex:1371--1382` and `main.tex:1783--1805`.
- Exact derivation: at \(N=2\), the normalized coefficient has one-handle
  shift \(p_y+p_z=315\). Two normalized
  \(\mathcal C_{271}\)-Hom factors have total shift \(2p_z=542\), forcing
  residual shift \(p_y-p_z=-227\). Grading-preserving co-Yoneda retains
  \(-227\); split-circle Kunneth changes
  \(\operatorname{Hom}_{271}\) to
  \(\operatorname{Hom}_{44}\{+227\}\otimes A^{\otimes227}\), canceling it.
  The normalized reduced coefficient therefore has no Hom shift.
- Selected class: the normalized Hom identity has degree zero. MWW's Euler
  rule makes a cap disk degree \(-1\), so the counit-nonzero unknot generator
  \(X\) has degree \(+1\); \(X^{\otimes227}\) has degree 227. Definition 3.1
  gives the selected state \(|r|=2,\alpha=0\) shift \(-4\). The absolute
  intrinsic MWW degree is \(227-4=223\).
- Euler audit: \(+315\) already compensates one-handle sheet gluing; normalized
  Hom composition makes co-Yoneda degree zero; Kunneth is not a cobordism;
  later 227 cap maps have degree \(-227\) but evaluate rather than regrade the
  source; and the four core-disk Euler contribution is exactly the cabled
  \(-4\). No omitted Euler term restores 494.
- Consequence: MWW Corollary 3.5 is concentrated in quantum degree zero, so a
  nonzero \((0,223)\) class would still obstruct \(S^4\). C and S remain open.
  Adopting this route requires replacing or parameterizing every hard-coded
  494 in the paper and Lean interfaces.

### F-615 — Complete coefficient-exterior geometry now has a fail-closed simplicial contract

- Severity: **Major positive infrastructure / Critical missing witness**
- Status: **PARTIAL**
- Locations: `audit/t73_coefficient_exterior_schema.json`;
  `scripts/verify_t73_coefficient_exterior.py`;
  `tests/test_t73_coefficient_exterior.py`.
- Contract: an admissible frame is a triangulated 3-manifold whose boundary
  has exactly five explicitly enumerated 2-sphere components (outer plus four
  insertion boundaries), 630 owner/side/index-typed embedded edge paths, and
  630 vertex-disjoint framed ribbon disks whose boundaries are exactly their
  core paths, push-offs, and endpoint edges. Face incidence, vertex
  sphere/disk links, boundary components, path incidence, and ribbon topology
  are derived rather than asserted.
- Relative moves: v1 replays vertex-preserving 2-3 and 3-2 bistellar
  replacements with equal local boundary and support disjoint from the typed
  geometry. It also accepts explicit simplicial ambient isomorphisms that fix
  every insertion-boundary vertex and carry every arc and ribbon exactly.
- Adversarial result: the new normal-form JSON fails immediately because it
  contains cuboid/routing metadata rather than a tetrahedral holed
  3-manifold. Six tests validate a synthetic ball/ribbon and reject boundary
  map, ribbon, and boolean/hash mutations.
- Dependency impact: this gate can later bind the typed S movies through
  owner/source/endpoint indices, but no present constructor produces its
  geometric witness.
- Corrected endpoint contract: the four insertion spheres have respectively
  88, 88, 542, and 542 incident endpoints, totaling 1260 endpoints and hence
  630 exterior intervals. Each oriented closure side contains 315 intervals.
  The earlier 542-arc count confused z endpoints with complete exterior
  intervals and is superseded.

### F-616 — The reduced “PD” cannot be converted to Spherogram/SnapPy/Regina

- Severity: **Critical data gap**
- Status: **CONFIRMED**
- Locations: `audit/t73_reduced_link_pd.json`;
  `audit/t73_pd_spherogram_adapter_report.json`;
  `scripts/audit_t73_pd_spherogram_adapter.py`;
  `tests/test_t73_pd_spherogram_adapter.py`.
- Environment: Regina 7.4.1, SnapPy 3.3.2, and Spherogram 2.4.1 were loaded
  from `/tmp/t73-topology-tools`.
- Exact failure: the file is a signed *mixed-owner crossing ledger*, not a
  standard PD code. It lacks four-half-edge incidence rows, cyclic successor
  order along components, all self-crossings, an embedded zero-crossing
  \(r_{zx}\), the two dotted 1-handle components (or a handlebody
  triangulation), and integer diagram framings for \(m_2,m_3\).
  There are 390 railroad segments containing multiple crossings but no
  along-segment order; \(r_{zx}\) has zero incidence.
- Consequence: neither a Spherogram Link nor a link-complement triangulation
  is determined. Crossing signs and segment numbers suffice for selected
  linking sums, but not for planar link reconstruction. The adapter validates
  standard PD label incidence if future data supply it, and otherwise returns
  OPEN without invoking topology recognition.

### F-617 — Exhaustive workspace search cannot recover a unique full Kirby PD diagram

- Severity: **Critical data gap**
- Status: **CONFIRMED**
- Locations: `docs/proofs/T73_FULL_PD_RECOVERY_AUDIT.md`;
  `audit/t73_full_handle_diagram_input_contract.json`;
  `scripts/audit_t73_pd_spherogram_adapter.py`.
- Recoverable distinction: the new selected-source exterior supplies four
  cabled coefficient cycles, all 1260 endpoint successors and 630 rational
  routes. It is not the closed five-component reduced attaching link and has
  arbitrary insertion tangles at its four boundary spheres.
- Nonuniqueness witnesses: (i) segment `m_2:0` has records
  10,74,702,766,1396 with no stored along-segment order, and swapping two
  changes PD successors without changing the ledger; (ii) tying a local knot
  into a component changes self-crossings while preserving every mixed
  record; (iii) an unknot and local trefoil both realize the empty
  \(r_{zx}\) handle word with zero mixed incidence; (iv) blackboard curls
  change integer diagram framing while preserving the string
  `same-product-framing`.
- Other missing geometry: the dotted y/z components or an explicit genus-two
  handlebody triangulation are absent. Therefore the link-in-\(S^3\) input
  required by Spherogram is not determined.
- Minimal new contract: seven closed core polylines, five disjoint framing
  push-offs for the 2-handle components, and one common generic rational projection. These suffice to
  derive all mixed/self crossings, crossing parameters and successor cycles,
  standard PD rows, linking matrix, and integer framings. A bare PD code would
  still not prove AR provenance.

### F-618 — The eight \(r_{xy}\) connectors are a pivotal variance issue, not a source of degree 494

- Severity: **Major**
- Status: **CONFIRMED**
- Locations: `scripts/audit_t73_rxy_pivotal_currying.py`;
  `tests/test_t73_rxy_pivotal_currying.py`;
  `docs/proofs/T73_FULL_PD_RECOVERY_AUDIT.md`.
- Classification: the two oriented \(r_{xy}\) cycles contain eight Y/Z
  exterior intervals: four join the same variance side and four opposite
  variance sides. Standard rigid pivotal duality can bend endpoints to type
  these consistently in a curried morphism.
- Topological qualification: pivotal currying changes the boundary
  presentation/canopolis variance; it is not an ambient isotopy pointwise
  relative to four fixed insertion spheres. The z coend and the selected
  noninvertible cup \(P_{86}\to P_{88}\) remain separate operations.
- Grading: normalized pivotal identifications are degree-zero equivalences.
  They repair typing but cannot contribute the missing \(+271\). Hence they
  do not change the independently audited two-representable degree 223 into
  494. Any nonzero Euler degree would signal use of an actual cup/cap
  cobordism rather than a pivotal equivalence and must be counted explicitly.
- Mutation test: deleting one \(r_{xy}\) interval is rejected; two focused
  tests pass.

## Proof dependency ledger

The main theorem will be expanded into atomic premises.  For each premise this
ledger will record: source/proof location, dependencies, verification method,
and unresolved semantic gaps.

| ID | Atomic obligation | Current evidence/status | Main-theorem impact |
|---|---|---|---|
| D-01 | `det A=1`, `det(A-I)=1` and CS homotopy-sphere criterion | finite arithmetic plus Iwaki Proposition 2.1; **CONFIRMED for the standard surgery object** (F-100) | establishes homotopy-sphere status of `Sigma_A^0`, not the `X_J` identification |
| D-02 | Johnson framed handle picture is the actual `Sigma_A^0` picture | **RESOLVED AT PAPER LEVEL AFTER RETYPING**: Johnson mapping classes and local straightening give the unlabelled AR presentation; standard cancellation/collar lemmas give P0; the auxiliary `B44` is C data, not attaching-link geometry (F-409, F-411--F-413) | supplies the actual manifold/collar without relying on the old E13 booleans |
| D-03 | selected raw class is a genuine, correctly graded MWW one-handle class | standard pivotal data are derived and the literal-split normalization is independently corrected to degree 223, but the source-to-target relative split is absent; **PARTIAL** (F-510, F-512--F-517, F-614) | required to interpret detector categorically |
| D-04 | Burau divided cubic equals an MWW/BPW/BHPW natural functional on the entire typed source | the corrected coend/shadow theorem is proved conditional on the two-representable relative split, whose cyclic connector class is not determined by current artifacts; **OPEN** (F-512--F-516, F-613) | required before quotient descent |
| D-05 | functional kills every two-handle beta/psi relation | abstract/finite cocone exists, but identification of every actual MWW beta/psi map is missing; **OPEN** (F-203) | required for nonzero `W2` class |
| D-06 | actual complete 3-handle sphere system and endpoint maps give undotted-zero/dotted-identity on whole source | typed Sigma-minus movies and local Frobenius formulas are constructed; MWW reduces the rest to statewise shadow naturality, which depends on D-04/D-05; **PARTIAL** (F-611--F-612) | required for surviving `W3` class |
| D-07 | four-handle attachment transports class by grading-preserving isomorphism | **TOPOLOGICAL PART RESOLVED** by transporting the complete original AR upper-handle maps (F-609); MWW Proposition 3.4 has the correct empty-link scope | transports a class only after D-06 establishes that one survives the actual three-handle maps |
| D-08 | standard `S^4` module vanishes in quantum degree 223 | MWW Corollary 3.5 and proof chain **CONFIRMED**, with `Q`/`Z` wording qualification (F-200, F-206, F-208, F-517) | target obstruction is available if the conditional degree-223 class exists |
| D-09 | diffeomorphisms induce absolute-grading-preserving isomorphisms in exactly the theory/coefficient convention used | intrinsic MWW split-route audit gives 223 and the standard pivotal convention is fixed; an extra shift is still possible if the missing source-to-target comparison is a saddle cobordism rather than isotopy; **CONDITIONAL** (F-510, F-614) | converts class mismatch to nondiffeomorphism after the relative split is proved |

At present D-03 through D-06 remain fatal. The abstract linear-algebra theorem
and the P0/E13 topological realization are available, but the Burau detector
has not been identified with a homogeneous functional on the genuine MWW
two-/three-handle quotients.

## Reproduction log

Commands, tool versions, exit status, and significant output will be recorded
here.  Passing scripts are not promoted to mathematical claims beyond their
explicit checked contracts.

- **2026-09-04 topology/P0 audit:** inspected the topology-facing portions of
  `main.tex`, P0/P3/E13 scripts, committed JSON certificates, and verifier
  contracts. Static inspection found the semantic gaps recorded in
  F-100--F-107. Rerunning a generator cannot cure these gaps because the
  desired ambient-topology claims are accepted from status fields or assigned
  by the programs themselves.
- **2026-09-04 primary-source audit:** checked Iwaki Proposition 2.1 in the
  arXiv HTML and extracted pp. 6--12 of the public Aitchison--Rubinstein scan
  using `pdftotext`. The confirmed results and their limits are recorded in
  the topology source table above.
- **2026-09-04 topology source-chain second pass:** downloaded Iwaki's TeX
  source from arXiv and checked Proposition 2.1, Definition 2.5, the trace-73
  table, and its underline legend; checked Johnson Theorem 1 in the publisher
  PDF/HTML; checked Kirby's primary framed-link paper; and extracted the full
  Laudenbach--Po\'enaru paper from Numdam. Findings F-108--F-113 distinguish
  the trustworthy published theorems from candidate-specific hypotheses they
  do not prove. Searches found no published erratum to the Johnson, AR, Kirby,
  or LP results used at this level; a 2025 independent proof corroborates the
  LP extension theorem.
- **2026-09-04 computation/Lean audit:** this host has no `python` executable;
  rerunning with `python3` succeeded. `recompute_t73_delta3.py --check`
  returned B44 length 11340, B88 length 45360, epsilon cubic -328,
  `DELTA3_ETA_T1=2624`, and `DELTA3_XI=0`.
  `verify_t73_gamma3_magnus.py` found the Artin action identical through
  degree 3 on all 44 generators. `verify_t73_uniform_order3.py` checked all
  7744 cabled Burau entries through order 2. Fourteen focused
  detector/arithmetic/boundary tests and both uniform-order mutant tests
  passed. These successful checks have only the finite scope stated in F-304
  and do not resolve F-300--F-303.
- **2026-09-04 gate audit:** `audit_declarations.py --root .` failed on the
  word “constant” in a Lean doc comment (F-306), before subsequent commands
  in that shell chain could run.
- **2026-09-04 full Lean-test attempt:**
  `python3 -m unittest tests.test_t73_minimal_formalization` printed one
  completed test, then remained inside `test_finite_module_exists_and_builds`
  while its `run_lean` subprocess compiled the generated target. It produced
  no further output for more than four minutes and was interrupted as a
  bounded audit run (exit 130). Therefore this audit does **not** claim a
  fresh full compilation/38-axiom-report pass. Static whole-tree search found
  no forbidden proof escape declaration; the focused finite tests above did
  pass.

### F-520 — The C verifier contains no chain-level coefficient map

- Severity: **Critical**
- Status: **CONFIRMED**
- Locations: `scripts/certify_t73_c2_comparison.py:1-8,92-128,167-228`;
  `main.tex` Lemma `lem:C1` and equation (17).
- Evidence: the script expressly says it is not a chain-level
  Blanchet--Khovanov complex of the actual `W2` cut.  Its object `H` stores 44
  start/end arc hashes and PASS strings; the action squares are two disjoint
  bounding boxes.  No complexes, differentials, foam maps, or naturality
  homotopies are defined.
- Impact: the first required datum C-H1 in
  `docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md` is absent, so 2624 is not yet an
  MWW quotient functional.

### F-521 — Selected-state rectangles do not establish the claimed all-cable comparison

- Severity: **Critical**
- Status: **CONFIRMED**
- Locations: `scripts/certify_t73_c2_comparison.py:138-149,200-208` and the
  all-state construction following equation (24) in `main.tex`.
- Evidence: C1 constructs the 44 pairings for
  `s0=e_m2+e_rxy`.  The code lists owner counts for `m3`, `r_yz` and other
  cable states but does not construct their primitive rectangles or a uniform
  verified tubular-neighbourhood map producing every `H_r`.
- Impact: whole-source beta/psi equations cannot be inferred from the selected
  state certificate.  The missing datum is C-H2 in the proof note.

### F-522 — Endpoint pivotal data remain assumed

- Severity: **Critical**
- Status: **CONFIRMED**
- Location: `scripts/build_t73_endpoint_transport.py:228-265`.
- Evidence: every endpoint receives literal assignments
  `pivotal_sign=1`, `q_power=0`; orientation and framing fields are stored but
  do not compute these values.
- Impact: the endpoint vector and cubic evaluation are conditional on an
  unproved convention choice.  C-H3 requires a derivation in the actual
  BPW/BHPW pivotal category.

### F-523 — The BPW/BHPW theorems give only a conditional route after the missing `H` is supplied

- Severity: **Major**
- Status: **CONFIRMED**
- Evidence: BPW trace/shadow results require the relevant dual and pregraded
  categories; BHPW strict functoriality applies after the concrete tangles and
  cobordisms are placed in its foam theory.  Neither source constructs the
  candidate-specific MWW coefficient isomorphism C-H1.
- Impact: citing strict functoriality cannot replace a definition of the
  actual chain map or its two action squares.

### F-524 — Constructive C attempt stops at four explicit missing inputs

- Severity: **Critical**
- Status: **BLOCKED ON NEW MATHEMATICAL DATA, NOT ON LEAN**
- Evidence: `docs/proofs/T73_C_CHAINMAP_PAPER_PROOF.md` isolates C-H1 (actual
  dg coefficient map), C-H2 (all-owner/all-cable rectangles), C-H3 (pivotal
  coefficients), and C-H4 (erratum-corrected absolute grading ledger).
- Impact: the valid conclusion is conditional on C-H1--C-H4.  None can be
  recovered from current status strings, hashes, or abstract Lean parameters.

## P0/E13 focused paper-proof attempt (F-400 onward)

The full argument and the exact completion package are recorded in
`docs/proofs/T73_P0_E13_PAPER_PROOF.md`.  These findings evaluate the current
post-F-017 working tree, including the later Johnson restore hierarchy.

### F-400 — The affine Johnson--AR Heegaard-pair bridge has a direct paper proof

- Severity: **Remediation / positive result**
- Status: **RESOLVED for the affine pair bridge only**
- Locations: `main.tex`, Lemma `lem:P0a`; the detailed proof in
  `docs/proofs/T73_P0_E13_PAPER_PROOF.md`, Section 1.
- Proof: the formula
  (S([u])=[2u-(1/2,1/2,1/2)]) is well defined from
  (mathbb R^3/mathbb Z^3) to (mathbb R^3/(2mathbb Z)^3), has the
  displayed affine inverse and positive determinant (8), sends the two
  coordinate roses to the AR roses at $Q,\\bar Q$, and scales all torus
  distances by two.  It therefore sends Johnson's actual Euclidean Voronoi
  Heegaard pair to a valid AR coordinate-spine pair.
- Scope: this closes only the background identification of the two standard
  Heegaard-pair models.  It does not prove that the candidate's 93-factor
  hierarchy is a homeomorphism preserving that pair.

### F-401 — The final Johnson `ArmRestore` assembly is not a defined global PL map

- Severity: **Critical**
- Status: **BLOCKED BY MISSING MAP DATA**
- Locations: `scripts/build_t73_johnson_restore_assembly.py:118-152`;
  `scripts/build_t73_johnson_pl_generators.py:77-104`;
  `scripts/compose_t73_psi_A.py:37-42,119-135`;
  `scripts/verify_t73_pl_homeomorphism.py`, function `check_arm_restore`.
- Evidence: the restore assembler records strings naming seven layers and
  their inverse order, totals cell counts, and then directly sets the global
  map, owner-preservation, relative identity, isotopy and inverse fields to
  `True`.  It constructs no common subdivision and checks no layer interface
  or composite inverse.  The generator builder hard-codes the zero-mismatch
  Heegaard owner table.  Most decisively, the compositor raises an error when
  asked to evaluate a hierarchical restore at a point and records its general
  point evaluator as `OPEN`.
- Unchecked obligations: top-cell coverage, equality on every shared and
  periodic face, disjoint image interiors, target coverage, both inverse
  composites, and exact images of the two handlebody and protected-ball
  subcomplexes.
- Consequence: the claimed (\psi_A) is not presently a mathematical map in
  the supplied data.  This is the first candidate-specific break in P0 and
  blocks every later use of (\psi_A(C_i)) or its boundary transport.
- Required resolution: provide a flattened source/image simplex table and
  inverse on a common periodic subdivision, or exact layer evaluators with
  proved interface and inverse laws, and verify the four global obligations
  listed in the detailed proof attempt.

### F-402 — The 6+1513 records do not certify sequential framed Kirby slides

- Severity: **Critical**
- Status: **BLOCKED BY MISSING EMBEDDED BANDS AND FRAMING TRANSPORT**
- Locations: `scripts/build_t73_p0_reconstruction_input.py:92-147`;
  `scripts/build_t73_belt_spheres.py:110-132,135-268`;
  `scripts/verify_t73_handle_cancellation.py:64-205,240-280`;
  `scripts/build_t73_johnson_spine_embedding.py:103-135`.
- Evidence: the verifier checks passage counts, that band-core vertices lie
  on a coordinate belt face, distinct target points, and a stored
  `relative_twist=0`.  It does not construct each band as an embedded
  rectangle in the current boundary, test its interior against the current
  full link, update that full embedded link after each slide, or derive the
  pushed framing from the actual normal fields.  `choose_bend` avoids only a
  finite set of obstacle points, not obstacle edges or evolving link curves.
- Source boundary: AR and standard Kirby calculus validate cancellation after
  geometric intersection one and the cancelling framing have been proved;
  neither source proves these candidate-specific band hypotheses.
- Consequence: the word substitutions and handle counts do not establish
  equality of framed handle presentations.  P0 and E13 remain open even if
  F-401 is repaired.

### F-403 — The detector cube and 44+227 pieces are not embedded in a constructed post-cancellation boundary

- Severity: **Critical**
- Status: **BLOCKED BY MISSING AMBIENT INCLUSION**
- Locations: `scripts/build_t73_actual_cut_tangle.py:126-265` and
  `scripts/reconstruct_t73_p0.py:89-176`.
- Evidence: the cut-tangle builder derives event labels and assigns them new
  vertical intervals in a declared cube; it directly sets pairwise
  disjointness and disjointness from the section ball.  The 227 leftovers are
  replaced by coordinate meridians with only a prose standardization.  The
  reconstruction checker accepts the ambient solid as a ball from the input
  `certified_topological_type` field and accepts strand disjointness, normal
  fields and AR binding from stored status fields.
- Consequence: the extracted 11340-letter braid is a reproducible calculation
  in an abstract ball, but no inclusion of that ball and its framed strands
  into the same boundary produced by the proposed Kirby movies is proved.

### F-404 — `actual_W2_boundary` is a declaration ledger, not an ambient boundary model

- Severity: **Critical**
- Status: **CONFIRMED**
- Locations: `geometry/t73_actual_W2_boundary.json`;
  `scripts/build_t73_actual_sphere_system.py:111-151`;
  `scripts/verify_t73_actual_sphere_system.py:30-47`.
- Evidence: the 2.7 kB W2 file contains counts, hashes and strings, but no
  triangulation/cell decomposition.  Its builder directly assigns the
  boundary type (#^3(S^1\times S^2)), the actual-sphere identification,
  pairwise disjointness, connected complement and simultaneous surgery
  (S^3).  The verifier merely requires those same Boolean fields and does
  not perform boundary recognition or sphere surgery.
- Consequence: neither the actual P3 sphere attachments nor the remaining
  (S^3) follow from this artifact.

### F-405 — P3 uses invalid `1--3 cancellation` language and supplies no four-handle attaching map

- Severity: **Critical**
- Status: **CONFIRMED**
- Locations: `scripts/certify_t73_p3_four_handle.py:1-14,172-207,233-256`.
- Evidence: an intersection-one dual loop is converted directly into
  `cancels=True` for a 1/3 pair.  Ordinary four-dimensional handle
  cancellation is between consecutive indices.  A 3-handle attached along
  the belt sphere of a 1-handle is a boundary-dual surgery description, not
  a cancellation of those nonconsecutive handles in the same decomposition.
  The script then declares the boundary to be (S^3) and identifies the
  boundary of an unrelated abstract (I^4) with it without constructing a
  homeomorphism.  Its own module header says it is not a triangulation of
  (W_3) and does not identify (X_J) with (Sigma_A^0).
- Source boundary: Laudenbach--Poenaru gives uniqueness/extension only after
  the required 1-handlebody boundary hypotheses are established.  It does
  not recognize the present declared boundary or supply the absent sphere
  system.

### F-406 — E13 changes handle inventories by asserted stages rather than Kirby/PL maps

- Severity: **Critical**
- Status: **CONFIRMED**
- Locations: `scripts/certify_t73_e13_close.py:501-646,686-723` and
  `scripts/certify_t73_e13_identification.py:270-388`.
- Evidence: E13 creates ten prose pipeline stages and assigns every stage
  `PASS`.  It first calls the two surviving railroad 1-handles 1/3-cancelled,
  then introduces three “extra 1--3 pairs”, without a legal stabilization or
  ambient handle move connecting the new inventory to the CS decomposition.
  The `resolved_maps` statuses and final identification Boolean are assigned,
  not derived from a map.  The outer wrapper then sets
  `identified_with_X_J=True` and `identified_with_Sigma_A_0=True`.
- Live replay: P3 prints `E13=PARTIAL` and
  `IDENTIFIED_WITH_SIGMA=False`; the final wrapper prints `E13=PASS`,
  `IDENTIFIED_WITH_SIGMA=True`, and simultaneously `MISSING_MAPS=1`.
- Consequence: E13 supplies no ambient Kirby/PL equivalence
  (X_J\cong\Sigma_A^0).

### F-407 — The correct P0/E13 paper implication is available only conditionally

- Severity: **Remediation / dependency clarification**
- Status: **RESOLVED AS A CONDITIONAL THEOREM; hypotheses OPEN**
- Location: `docs/proofs/T73_P0_E13_PAPER_PROOF.md`, Section 6.
- Statement: a relative splitting-preserving representative of (A), the
  actual AR framed handle decomposition, two legitimate whole-link Kirby
  cancellations, an actual complete 3-handle sphere system with post-surgery
  (S^3), and a four-handle attaching identification imply
  (X_J\cong\Sigma_A^0).  The proof is the mapping-torus relative-isotopy
  map, invariance under genuine Kirby moves, and the
  Laudenbach--Poenaru upper-handle extension theorem after its boundary
  hypotheses are verified.
- Current status: F-401--F-406 show that the current repository does not
  supply these hypotheses.  Thus no unconditional P0/E13 statement is
  available.

### F-408 — A fail-closed global ArmRestore verifier now defines the missing finite target

- Severity: **Remediation / still open**
- Status: **OPEN ON CURRENT DATA**
- Locations: `audit/t73_canonical_arm_restore_schema.json`,
  `scripts/verify_t73_canonical_arm_restore.py`, and
  `tests/test_t73_canonical_arm_restore_gate.py`.
- Evidence: the new verifier requires a common tetrahedral source/target map
  and checks exact determinants, face incidence, opposite-side adjacency,
  pair separation, chart volume, fixed boundary, owner preservation,
  protected-cube avoidance and state chaining. It ignores semantic PASS
  fields. Two tests pass and the legacy restore assembly returns
  `verdict=OPEN` because it lacks these map data.
- Remaining impact: several lower artifacts explicitly retain `OPEN` for the
  paired-saddle ambient cells, while the old restore assembler replaced that
  state by PASS. A flattening generator must supply an admissible witness
  before P0 can use the composition-of-homeomorphisms paper argument.
- Constructive follow-up (2026-09-05): tracing the paired-support, cap and
  outer-collar builders locates the first absent coordinate object more
  sharply. No simplicial self-map of the complete paired-support boundary
  sphere is supplied which carries source_patch to target_patch and agrees
  on the cap curves with the recorded cap-product transport. Thus
  boundary_halfturn_cells, ambient_pl_cells,
  paired_saddle_ambient_cells, and final_restore_assembly correctly remain
  OPEN upstream. The strict verifier now reports this exact datum. The gate
  tests include one expected-failure invariant demonstrating that the legacy
  assembler improperly promotes those upstream OPEN values to PASS.

### F-409 — The paired-saddle ambient map exists by a checked PL 3-ball argument

- Severity: **Remediation**
- Status: **RESOLVED FOR LOCAL EXISTENCE ONLY**
- Evidence: `scripts/verify_t73_paired_saddle_topology.py` and
  `tests/test_t73_paired_saddle_topology.py` check all vertex links, sphere
  boundaries, collapse certificates, proper source/target disks, and every
  simple boundary-curve triangle move for all four canonical supports.
- Result: PL Schoenflies, uniqueness of proper disks in a 3-ball, and isotopy
  extension across a thin external collar give a local ambient PL
  homeomorphism fixed on the enlarged outer boundary. The four support sizes
  are 85, 83, 122 and 122 tetrahedra; boundary isotopies use 5, 5, 40 and 40
  triangle moves.
- Limit: this is an existence theorem, not the missing canonical coordinate
  evaluator. It is not bound to the later stored spine and detector
  transports, so F-401 and global P0/E13 remain open.

### F-410 — Sequential framed Kirby verification stops before the first band

- Severity: **Critical**
- Status: **BLOCKED BY MISSING BAND INPUTS**
- Evidence: `audit/t73_sequential_framed_bands_schema.json`,
  `scripts/check_t73_sequential_framed_band_inputs.py`, and
  `tests/test_t73_sequential_framed_band_inputs.py` provide a fail-closed
  contract and four passing gate/mutation tests.
- First missing datum: t/h_CS band 0 has no complete `current_link_before`;
  the next absent field is `source_attaching_interval`. The current record
  has only a centerline, target point, width and declared zero twist.
- Consequence: band interiors cannot be checked against the evolving whole
  link, the slid component cannot be rebuilt, and framing twist cannot be
  derived from a pushed-off band. The 6+1513 schedule remains combinatorial,
  not a verified Kirby movie.

### F-411 — Paper-level cancellation existence does not require storing all sequential band coordinates

- Severity: **Remediation / conditional positive result**
- Status: **RESOLVED GIVEN THE ACTUAL AR PRODUCT-COLLAR HYPOTHESIS**
- Location: expanded proof of Lemma `lem:P0b` in `main.tex`.
- Argument: once the actual AR framed link is present, the cancelling component
  meets the belt sphere once with product framing. In a belt-sphere collar the
  other passages are finitely many vertical product arcs. At each step an arc
  in the sphere punctured at the remaining passage points gives an embedded
  narrow band to a fresh parallel. Sequential slides remove every passage;
  the standard geometric 1/2-handle cancellation theorem then applies, and
  the product annuli give relative twist zero.
- Scope: this is an existence proof rather than a coordinate replay of the
  stored 1519-band schedule. It closes explicit-band existence in the paper
  conditional on the genuine common AR collar. The independent fail-closed
  computational gate correctly stays OPEN, and the earlier P0 ambient-link
  construction remains necessary.

### F-412 — Point-push closes only unlabelled E13, not the fixed-marked detector P0

- Severity: **Critical scope distinction / partial remediation**
- Status: **RESOLVED FOR UNLABELLED EXISTENCE; BLOCKED FOR LABELLED P0**
- Location: docs/proofs/T73_P0_E13_CONCEPTUAL_CLOSURE.md.
- Positive result: the 93 Johnson mapping classes give a
  splitting-preserving monodromy inducing A. Local straightening with an
  explicitly chosen even normal-frame path gives epsilon zero. Applying AR,
  performing standard one/two cancellations, and transporting the original
  upper handles gives an unlabelled handle decomposition of Sigma_A^0 without
  a coordinate PL evaluator or any one/three cancellation.
- Obstruction: a boundary-fixed ambient isotopy of the detector cylinder can
  produce only the trivial braid. A point-push producing nontrivial B44
  changes the marked top disk. Applied to the complete presentation, it also
  transports the source, detector, outside closure and endpoint actions, so
  naturality conjugates the apparent Burau operator. Inserted while those
  data stay fixed, it is not a presentation isotopy and loses the Sigma_A^0
  and upper-handle identification.
- Additional mismatch: two selected passages belong to r_xy rather than a
  monodromy spine image, so postcomposing monodromy alone cannot create the
  full committed 44-strand braid.
- Consequence: arbitrary local braid insertion does not justify 2624. A
  direct fixed-marking derivation of the actual tangle and all endpoint data
  is still required.
- Revision: F-413 separates an auxiliary detector morphism from an insertion
  into the attaching link. Under that corrected typing, F-412 remains valid
  as a warning about presentation isotopies but is not an obstruction to
  choosing W independently inside C.

### F-413 — Moving B44 from P0 to the auxiliary C detector removes the braid-insertion obstruction

- Severity: **Dependency correction / remediation**
- Status: **RESOLVED AT THE TYPE-DECOMPOSITION LEVEL; C/S STILL OPEN**
- Location: Section 7 of
  docs/proofs/T73_P0_E13_CONCEPTUAL_CLOSURE.md.
- Correction to F-412: its relative-boundary obstruction applies only if B44
  is inserted into, or claimed as an uncompensated coordinate change of, the
  AR attaching link. P0 may instead stop at a standard product collar with
  42 m2 and two r_xy vertical passages, their framings and fixed endpoint
  marking.
- Type check: the six-sweep W can be chosen independently as auxiliary C
  data. After doubling, rho_h(W) postcomposes the E88 output of
  Sh_h : qTr(C;M_R) -> Hom(E86,E88), so
  ell_h (rho_h(W)-I) Sh_h is a well-typed linear detector. W is neither a
  handle attachment nor part of the selected source class.
- Consequence: W need not be canonical; a nonzero-class detector may depend
  on choices. The fact that W inverse gives another scalar is not by itself a
  defect. What remains load-bearing is construction of the actual shadow and
  proof that this chosen detector annihilates all beta/psi relations and
  descends through the actual three-handle maps.
- Revised scope: the conceptual Johnson--AR route can close P0/E13 up to a
  marked vertical product collar. The 2624 and six-sweep claims belong wholly
  to C/S.

### F-414 — The retyped static P0 marked collar is now explicit and independently verified

- Severity: **Remediation**
- Status: **RESOLVED FOR THE STANDARD STATIC COLLAR**
- Evidence: geometry/t73_p0_marked_vertical_collar.json,
  scripts/build_t73_p0_marked_vertical_collar.py,
  scripts/verify_t73_p0_marked_vertical_collar.py, and
  tests/test_t73_p0_marked_vertical_collar.py.
- Construction: 44 source-bound wickets use an 11-by-4 rational grid inside
  D2, vertical arcs across D2 times [-1,1], constant normal
  (0,1/1000,0), explicit two-triangle framing rectangles, and 88 ordered
  negative/positive normal translates. Owners are exactly 42 m_2 and two
  r_xy; the artifact contains no braid word.
- Verification: exact arithmetic proves distinct centre arcs and push-offs,
  boundary levels, disk containment, framing rectangles, source IDs,
  orientations, owners, and endpoint order. Six mutations are rejected.
- Paper bridge: any genuine product y-handle collar with the same labelled
  transverse passages is carried to this model by a boundary-fixed disk
  isotopy and product extension; the product framing fields are straightened
  in disjoint tubular neighborhoods. B44 remains auxiliary C data.

### F-415 — Hostile re-review validates retyped P0 after repairing two hidden implications

- Severity: **Remediation with corrected proof**
- Status: **RESOLVED FOR P0 AS RETYPED; C/S EXCLUDED**
- Location: docs/proofs/T73_P0_HOSTILE_REVIEW.md and the revised proofs of
  prop:unlabelled-P0 and lem:marked-detector-collar in main.tex.
- Repair 1: equality of ambient mapping classes did not automatically give an
  isotopy relative to the section ball. The proof now fixes the section point
  along the whole isotopy, chooses the endpoint local-straightening class that
  kills the pi1(SO(3)) derivative loop, and applies parametric straightening.
  The mapping-torus map is then identity on Bq times S1, proving epsilon zero
  without changing psi or the Johnson side word.
- Repair 2: a reduced word or abelianization alone does not imply 42 geometric
  passages. The proof now uses Johnson's actual embedded square-slide
  representatives inductively, with repeated edge occurrences placed in
  disjoint parallel lanes. This realizes the verified 42 y letters of m2 as
  geometric passages; the standard r_xy dual cell supplies the other two.
- Validation: actual Johnson representatives compose to the 93-factor
  monodromy A; AR then applies, the two standard one/two cancellations and
  transported upper handles preserve Sigma_A^0, and the verified static collar
  supplies the marked P0 endpoint data without B44.
- Boundary: product rectangle pairing, 227 simultaneous leftovers, the
  coefficient shadow, beta/psi descent and hemisphere maps remain C/S. They
  are not consequences of P0.

### F-416 — The four-box artifact is a complete target template, not a relative split of the source coefficient link

- Severity: **Critical for C-H1 / grading**
- Status: **TARGET COMPLETED; LITERAL SOURCE SPLIT REFUTED BY F-525**
- Evidence: geometry/t73_selected_canopolis_normal_form.json,
  scripts/build_t73_selected_canopolis_normal_form.py,
  scripts/verify_t73_selected_canopolis_normal_form.py,
  tests/test_t73_selected_canopolis_normal_form.py, and
  docs/proofs/T73_SELECTED_CANOPOLIS_NORMAL_FORM.md.
- Positive result: schema v2 has four rational insertion boxes, two disjoint
  closure balls, 1260 explicit endpoints and 630 explicit framed arcs. Each
  closure has 88 Y--Z arcs and 227 Z--Z U-arcs; endpoint counts are
  \(88,542,542,88\). Nine target mutations fail, including an orientation
  mutation.
- Source comparison: F-417 supplies the complete source endpoint matching.
  F-525 finds eight wrong-side connectors, so no simultaneous ambient isotopy
  pointwise fixed on the four spheres can give the literal two-closure target.
- Grading consequence: if the missing map is an ambient isotopy, its trace has
  Euler characteristic zero and ordinary Kunneth introduces no extra shift.
  If endpoint pairings require saddle reconnection, the cobordism has a new
  Euler/framing degree not contained in the minus-44 Hom normalization. Thus
  the p_y/p_z count alone does not certify degree 494.
- Remediation: the verifier reports PASS_COMPLETE_TARGET_TEMPLATE together
  with SOURCE_RELATIVE_ISOTOPY=REFUTED_LITERAL_SPLIT and
  DEFECT_AWARE_CURRYING=OPEN. Lemma C1 in main.tex is explicitly
  counterfactual and its actual replacement remains in Hypothesis C.

### F-417 — Complete selected source endpoint incidence and rational exterior routes are now saved

- Severity: **Remediation / source reconstruction**
- Status: **RESOLVED FOR A CANONICAL SOURCE REPRESENTATIVE; AR RELATIVE ISOTOPY OPEN**
- Evidence: geometry/t73_selected_source_exterior.json,
  scripts/build_t73_selected_source_exterior.py,
  scripts/verify_t73_selected_source_exterior.py,
  tests/test_t73_selected_source_exterior.py, and
  docs/proofs/T73_SELECTED_SOURCE_EXTERIOR.md.
- Data: four oriented cable cycles give 88 endpoints on each Y insertion
  sphere and 542 on each Z insertion sphere, 1260 boundary points total, 630
  exterior intervals, and four cyclic seams. Each cable-sign closure has 88
  cross-handle intervals and 227 z--z residual intervals.
- Geometry: all endpoints and two-segment routes have rational coordinates.
  Every interval now also stores four ruled-ribbon triangles and its complete
  boundary, for 2520 triangles. The endpoint normal is the dyadic value
  \(2^{-20}\); an exact
  minimum-centre-distance versus maximum-\(L^1\)-width certificate proves
  ribbons belonging to distinct intervals are disjoint. Route, push-off,
  insertion-ball, cyclic-seam, ribbon and clearance checks pass; nine
  mutations fail.
- Scope: this is reconstructed from full reduced event records, not hashes,
  but is still a chosen canonical representative. It does not prove a relative
  isotopy from the actual AR exterior.
- Single-Hom boundary: four insertion spheres with 1260 points cannot be
  changed by ambient isotopy into a P86-to-P88 boundary with 174 points.
  The 1084 z endpoints require canopolis gluing/coend evaluation, and the
  remaining y defect requires the selected cup and pivotal turns. Those
  gluing/cobordism cells and their Euler grading are the next missing datum.

### F-418 — A single-Hom P86-to-P88 defect target exists, but the source currying map does not

- Severity: **Remediation / exact type boundary**
- Status: **TARGET RESOLVED; SOURCE MAP OPEN**
- Evidence: geometry/t73_single_hom_defect_target.json,
  scripts/build_t73_single_hom_defect_target.py,
  scripts/verify_t73_single_hom_defect_target.py, and
  tests/test_t73_single_hom_defect_target.py.
- Target: 86 explicit vertical through cells and one explicit cup with the two
  selected physical feet give a P86-to-P88 tangle. The BPW A.6 cup terms and
  product normals are attached to the correct positions.
- Missing map: no fixed ambient isotopy can preserve the four source insertion
  spheres and simultaneously change 1260 boundary points into 174. The 1084
  Z endpoints must be glued through arbitrary C_271 insertions/coend data,
  after which pivotal currying organizes the Y defect. The artifact therefore
  keeps z_coend_gluing_cells and source_to_target_interval_map empty and
  reports both OPEN.
- Grading: without those gluing/currying cells their Euler characteristic and
  additional quantum shift remain undetermined. The target cup alone does not
  certify the full comparison degree.
