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

## Current verdict (2026-09-04)

**The unconditional Trace-73 counterexample theorem is not proved.**  The
abstract linear-algebra implication is valid; the determinant calculation,
public-word Burau value `2624`, and Artin--Magnus/Andreadakis finite checks
replay.  The relevant published MWW handle theorems and classical topology
results appear sound within their stated hypotheses.

The proof fails at multiple independent candidate-specific bridges:

1. no verified ambient identification of the Johnson model with the actual
   Cappell--Shaneson handle presentation (`D-02`);
2. no constructed BPW/BHPW/MWW coefficient-shadow map turning the Burau cubic
   into a functional on the genuine two-handle quotient (`D-03`--`D-05`);
3. no proof of the actual three-handle endpoint factorization or complete
   `W2`/`W3` geometry (`D-06`--`D-07`);
4. pivotal coefficients are hard-coded, and a 2026 grading erratum has not
   been reconciled with the claimed absolute degree `494`.

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

## Proof dependency ledger

The main theorem will be expanded into atomic premises.  For each premise this
ledger will record: source/proof location, dependencies, verification method,
and unresolved semantic gaps.

| ID | Atomic obligation | Current evidence/status | Main-theorem impact |
|---|---|---|---|
| D-01 | `det A=1`, `det(A-I)=1` and CS homotopy-sphere criterion | finite arithmetic plus Iwaki Proposition 2.1; **CONFIRMED for the standard surgery object** (F-100) | establishes homotopy-sphere status of `Sigma_A^0`, not the `X_J` identification |
| D-02 | Johnson framed handle picture is the actual `Sigma_A^0` picture | internally called both discharged and OPEN; E13 assigns the desired boolean without constructing/verifying an ambient equivalence; **UNPROVED** (F-101--F-107) | load-bearing identification |
| D-03 | selected raw class is a genuine, correctly graded MWW one-handle class | pivotal coefficients are hard-coded and the Hattori/endpoint bridge is absent; **OPEN** (F-201--F-202, F-209--F-210, F-300) | required to interpret detector geometrically |
| D-04 | Burau divided cubic equals an MWW/BPW/BHPW natural functional on the entire typed source | no cited theorem supplies the claimed shadow map; paper itself says comparison remains OPEN; **UNPROVED** (F-007, F-201) | required before quotient descent |
| D-05 | functional kills every two-handle beta/psi relation | abstract/finite cocone exists, but identification of every actual MWW beta/psi map is missing; **OPEN** (F-203) | required for nonzero `W2` class |
| D-06 | actual complete 3-handle sphere system and endpoint maps give undotted-zero/dotted-identity on whole source | MWW local formulas are sound, but global detector factorization and actual `W2` geometry are unproved; **OPEN** (F-012, F-204--F-205) | required for surviving `W3` class |
| D-07 | four-handle attachment transports class by grading-preserving isomorphism | MWW theorem scope is correct for an actual empty-link 4-handle, but the purported `S^3` boundary and attaching map are not established; **OPEN** (F-104--F-105, F-200) | required for closed `X_J` class |
| D-08 | standard `S^4` module vanishes in quantum degree 494 | MWW Corollary 3.5 and proof chain **CONFIRMED**, with `Q`/`Z` wording qualification (F-200, F-206, F-208) | target obstruction is available if an actual degree-494 class exists |
| D-09 | diffeomorphisms induce absolute-grading-preserving isomorphisms in exactly the theory/coefficient convention used | general invariant framework appears sound, but a 2026 grading erratum is not reconciled with this paper's absolute shifts; **RECHECK REQUIRED** (F-209) | converts class mismatch to nondiffeomorphism only after convention audit |

At present D-02 through at least D-04 are independently fatal: the abstract
linear-algebra theorem is valid, but its intended geometric instantiation has
not been established by the manuscript's own status statements.

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

### F-500 — The C verifier contains no chain-level coefficient map

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

### F-501 — Selected-state rectangles do not establish the claimed all-cable comparison

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

### F-502 — Endpoint pivotal data remain assumed

- Severity: **Critical**
- Status: **CONFIRMED**
- Location: `scripts/build_t73_endpoint_transport.py:228-265`.
- Evidence: every endpoint receives literal assignments
  `pivotal_sign=1`, `q_power=0`; orientation and framing fields are stored but
  do not compute these values.
- Impact: the endpoint vector and cubic evaluation are conditional on an
  unproved convention choice.  C-H3 requires a derivation in the actual
  BPW/BHPW pivotal category.

### F-503 — The BPW/BHPW theorems give only a conditional route after the missing `H` is supplied

- Severity: **Major**
- Status: **CONFIRMED**
- Evidence: BPW trace/shadow results require the relevant dual and pregraded
  categories; BHPW strict functoriality applies after the concrete tangles and
  cobordisms are placed in its foam theory.  Neither source constructs the
  candidate-specific MWW coefficient isomorphism C-H1.
- Impact: citing strict functoriality cannot replace a definition of the
  actual chain map or its two action squares.

### F-504 — Constructive C attempt stops at four explicit missing inputs

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
