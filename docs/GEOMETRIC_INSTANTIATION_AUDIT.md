# Geometric instantiation audit

**Status:** `SUPERSEDED BY THE COMPACT C/S CLOSURE`

> This file audits the retired strategy that attempted to recover the
> historical full PD and TH artifacts.  The compact product-ribbon,
> coefficient-trace and whole-sphere proofs in
> `docs/proofs/T73_EXTERNAL_GEOMETRY_DISCHARGE.md` do not use those objects.
> The OPEN verdicts below remain correct for the historical route but are no
> longer premises of the main paper.

This audit concerns the step from the kernel-checked conditional theorem to a
candidate-specific geometric instance. It does not re-audit the published
integer calculation.

## Constructive progress after the original audit

The historical full PD remains unavailable, but it is no longer the only
possible presentation route.  Three new public constructions narrow the
open boundary:

| construction | result | retained boundary |
|---|---|---|
| compact six-sweep point-push generator | **DISCHARGED** for the local collar: regenerates all 252 rows and the pinned 44-strand word | does not itself identify a global Kirby link |
| compact Aitchison--Rubinstein product-ribbon ledger | **PARTIAL**: publicly constructs the candidate manifold, product framings, cancellations and reduced words without the historical PD | actual MWW coefficient/Hattori binding to the collar remains open |
| 32-step Nielsen sphere ledger plus cubic-jet algebra | **DISCHARGED** for existence of the determinant-one disjoint sphere basis and for `Id+O(h)` cubic invariance | the actual MWW source/target movie charts for the 32 moves remain open |

Thus a revised proof may retire the historical PD rather than recover it.
It may not retire the candidate-specific coefficient naturality or the MWW
sphere-map naturality.

## Result

At commit `cb7f684`, the repository does not contain enough public data to
construct or independently verify an inhabitant of `ExternalGeometry`. The
published source contains hashes and summaries for the load-bearing geometric
objects, but not their bytes. A SHA-256 digest authenticates bytes once they
are supplied; it cannot establish a theorem about unavailable bytes.

Consequently, the strongest supported result remains the conditional theorem
in `Smooth4PC/T73Conditional.lean`. In particular, a synthetic Lean instance
whose fields are filled by arbitrary vector spaces and maps would merely
rename the assumptions and is not an acceptable completion.

Run the availability audit with:

```text
python -B scripts/check_geometric_evidence.py
```

The expected result for the public repository as released is a nonzero exit
status and `MISSING` for the P0--P2 witness artifacts. The required names,
historical locations and hashes are recorded in
`audit/geometric_evidence_manifest.json`.

## Ordered verdicts

Only the following three verdict words are used. `DISCHARGED` means that the
public object and an independently checkable argument are both available;
`PARTIAL` means that the cited general theorem or finite algebra is available
but the candidate-specific identification is not; `OPEN` means that a
load-bearing comparison or geometric instance is absent.

| priority / item | verdict | public boundary |
|---|---|---|
| P0: frozen diagram is the Cappell--Shaneson handlebody | **OPEN** | the full PD, builder, framing/cut data and a labelled Kirby/isotopy ledger are absent |
| P1: truncated Burau cubic is an MWW lasagna evaluation | **OPEN** | the script computes a finite Burau scalar, but no public comparison theorem identifies it with the one-handle/HH0/cabled-quotient functional |
| P2/E7: chosen spheres are valid 3-handle attachments | **OPEN** | Horvat--Jablonowski gives a criterion; the candidate-specific boundary decomposition, irreducibility, handle count, embedded spheres and spherical basis are absent |
| P2/E10: `q01,q12` are the MWW quotients | **OPEN** | MWW gives the general formulas; the actual candidate maps and all required relations are not publicly bound to them |
| P3/E11: four-handle transport | **PARTIAL** | MWW Proposition 3.4 is applicable only after the preceding identification and grading data are supplied |
| P3/E12: standard-sphere control | **PARTIAL** | MWW Corollary 3.5 computes the genuine lasagna module, but the Lean functor `G` is still abstract |
| P3/E13: homotopy-sphere criterion | **PARTIAL** | the determinant criterion and matrix arithmetic are available; identifying the frozen detector manifold with \(\Sigma_A^\varepsilon\) is P0 |

No item in this ordered list is presently `DISCHARGED` as a complete
candidate-specific geometric instance.

## Field-by-field allocation

| Lean obligation | What would discharge it | Current result |
|---|---|---|
| `x0`, `ell0`, `ell0_x0` | A public construction of the selected MWW raw class and detector on the actual cut Kirby presentation | Open: the arithmetic value is reproducible, but the source collar braid and its binding to the full PD diagram are absent |
| `q01`, `ell1_comp_q01` | The complete candidate-specific beta/psi presentation and proof that the detector annihilates every relation | Open as geometry: only derived ledgers and abstract quotient algebra are public |
| `q12`, `ell2_comp_q12` | The three actual attaching spheres (or an HJ-valid replacement) and their two MWW maps on the complete source | Open: the three exhaustive geometry witnesses are absent |
| `transport`, `fourIso` | The published handle-decomposition/four-handle theorems applied to the same identified handlebody | General theorem available; candidate identification still depends on P0--P2 |
| `s4DegreeZero` | The rational, grading-preserving `S^4` computation | Supported by the published MWW result, but still external to Lean |
| `diffeomorphismEquiv` | Graded diffeomorphism invariance of the same lasagna module | Supported as a general external theorem |
| `matrixConditionsToHomotopySphere` | The Cappell--Shaneson criterion applied to the identified matrix | Mathematically supplied by Iwaki, Proposition 2.1; external to Lean |

The last row does not depend on the detector. For the displayed matrix,
`det(A-I)=1`, so the standard Cappell--Shaneson construction is a homotopy
4-sphere. What remains unproved is that the specific frozen Kirby/point-push
presentation carrying the detector is that same construction.

## P0: actual Cappell--Shaneson presentation to frozen point-push

The note `T73_GA1_DESCENDING_BRIDGE.md` gives a plausible strategy based on
Aitchison--Rubinstein product annuli, two cancellations, a whole-boundary
diffeomorphism and a descending-tangle comparison. It is not presently a
reproducible proof because the following witnesses are unavailable:

1. the deterministic presentation builder and its frozen trace-73 input;
2. the full 2,126,291-crossing labelled PD diagram;
3. the cut/gate/successor and normal-field/framing bindings;
4. the collar-braid source and the verifier that extracts the 65,606 public
   crossing rows from the full diagram;
5. an explicit move or isotopy ledger transporting component, cocore,
   basepoint and product-framing labels from the Aitchison--Rubinstein
   presentation to the frozen diagram.

The committed `T73_EVIDENCE_GLOBAL_DESCENDING.json` is output from a check of
the missing PD file. It cannot replace that input. Likewise,
`T73_DELTA3_PUBLIC_INPUT.json` is intentionally only a result-free arithmetic
projection and does not determine the full Kirby link.

Even after the bytes are published, review must check two mathematical joins
that a hash test cannot decide:

- the locally straightened representative of the linear torus map and the
  Aitchison--Rubinstein product-annulus framing must be transported through
  the stated mapping-torus and Laudenbach--Poenaru diffeomorphisms;
- the relative descending-tangle isotopy must preserve all marked gates,
  owner/cocore labels and chosen longitudes needed by the detector and later
  sphere calculations.

Until those joins are written as explicit maps/moves or independently proved,
P0 remains an antecedent rather than a constructed instance.

## P1: comparison with the MWW invariant

The public script `scripts/recompute_t73_delta3.py` performs a precise finite
calculation. From 252 primitive crossing rows it constructs an 11,340-letter
Artin word, cables it to a 45,360-letter word, evaluates an 88-dimensional
unreduced Burau action over
\(\mathbb Z[\varepsilon]/(\varepsilon^7)\), substitutes
\(\varepsilon=(1+h)^{-2}-1\), and extracts the cubic coefficient. This
supports a reproducible statement about a finite scalar, denoted here by
\(\delta^{\mathrm{Bur}}_3\).

It does not by itself define a skein lasagna filling, the MWW one-handle
coefficient category, its \(HH_0\), the beta/psi cabled quotient, or the two
maps associated with a 3-handle sphere. The public JSON cites the missing
`T73_COLLAR_BRAID.json`, `ACTUAL_PD_CABLE_UNIT_CERT.json`, and
`PRODUCT_NORMAL_CHRISTOFFEL_THXY_MOVIE.json`; the last has SHA-256
`DE1AC479699EC79DE76D4265993DE437493A3AAA6CABB636F98998644BF3181C`.
Even publishing those bytes would leave a mathematical obligation: construct
an action-compatible natural transformation from the actual MWW coefficient
category to the Burau endpoint model, prove that it respects every cyclic and
beta/psi relation, and identify coefficient extraction with the claimed
divided lasagna evaluation on the selected class.

No such public comparison theorem is present. Therefore the equation

\[
  \delta^{\mathrm{Bur}}_3=\delta^{\mathrm{MWW}}_3
\]

must remain an explicit hypothesis. This is not repaired by numerical
agreement asserted in Markdown or by Lean's constant `cubicBase = 7384`.

## P2/E7: chosen three-sphere system

Horvat--Jablonowski Proposition 5.1 and Theorem 5.3 provide the right general
criterion: under their boundary and handle-count hypotheses, a pairwise
disjoint embedded sphere system representing an integral basis can replace
the actual 3-handle attaching system up to permutation and 3--3 slides.

The theorem does not prove the candidate-specific hypotheses. The repository
does not include the TH1, TH2 and THXY witnesses that are claimed to establish
embeddedness, common ambient boundary, disjointness, framing and homology
coordinates. The displayed determinant is only the last arithmetic step; it
does not construct the spheres or identify their classes in
`H_2^sph(partial W2)`.

For E7 to pass, the three geometry files and their deterministic replay code
must be published, and the replay must derive (rather than accept as status
fields):

- smooth embedded genus-zero surfaces in one identified `partial W2`;
- pairwise disjointness and normal framings;
- the three integral homology coordinates;
- `partial W2` and handle-count hypotheses required by the HJ theorem;
- compatibility of 3--3 slides with the exact MWW relations used later.

## P2/E10: actual MWW maps

MWW supplies the general coequalizer and handle-decomposition formulas. The
remaining candidate-specific claim is that the selected geometric movies
induce the six maps whose divided-cubic rows are asserted in Section 10 of the
candidate proof. This requires the actual surfaces from E7 and a complete
naturality/transport binding. Constant-term tensor formulas cannot be used as
a substitute for that binding.

## P3: general theorems and candidate-specific joins

MWW Proposition 3.4 states that attaching a 4-handle induces an isomorphism,
and Corollary 3.5 states that \(\mathcal S^N_0(S^4)\cong\mathbb Z\), concentrated
in bidegree zero. These results justify E11 and E12 only for the genuine,
grading-preserving skein lasagna module. The repository's `Universe.G` is an
uninterpreted graded-module family, so a separate identification with the
rational \(N=2\) theory is required, including preservation of quantum degree
494.

Iwaki, Proposition 2.1, restates the Cappell--Shaneson criterion:
\(\Sigma_A^\varepsilon\) is a homotopy 4-sphere exactly when
\(\det(A-I)=\pm1\). The displayed matrix has determinant one and
\(\det(A-I)=1\), but this discharges E13 only for the standard construction
\(\Sigma_A^\varepsilon\). Applying it to the frozen detector presentation
still requires P0.

## Minimal honest route to closure

1. Publish the P0--P2 objects under `evidence/geometric/` (Git LFS or a release
   archive is acceptable) together with generators and schemas.
2. Make a clean replay start from the matrix and convention choices, generate
   the full framed labelled presentation, and reproduce every pinned hash.
3. Emit a compact, independently checkable Kirby/isotopy ledger rather than
   only a terminal `PASS` receipt.
4. Prove the Burau--MWW comparison on the full coefficient category and the
   complete beta/psi and sphere relation systems.
5. Generate the `ExternalGeometry` data from that replay boundary. Keep the
   published topology theorems as named external results unless they are
   genuinely formalized.

No unconditional SPC4 claim is justified before these steps pass independent
mathematical review.
