# Geometric instantiation audit

**Status:** `CURRENT -- P0 DISCHARGED BY AR REPLACEMENT; C OPEN`

> This file audits the retired strategy that attempted to recover the
> historical full PD and TH artifacts.  The compact product-ribbon,
> coefficient-trace and whole-sphere proofs in
> `docs/proofs/T73_EXTERNAL_GEOMETRY_DISCHARGE.md` do not use those objects.
> The historical frozen-PD verdict remains open, but that route is retired.
> The public AR product witness now discharges P0 for the replacement
> presentation used by the paper.

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
| public Aitchison--Rubinstein product witness | **DISCHARGED**: constructs the simultaneous embedded framed link, two cancellations and actual detector ball from the public AR source | actual MWW coefficient/Hattori binding to the collar remains open |
| relative standard-sphere theorem | **DISCHARGED as P0 + monoidal C => S** | candidate S remains partial while C is open |

Thus a revised proof may retire the historical PD rather than recover it.
It may not retire the candidate-specific coefficient naturality or the MWW
sphere-map naturality.

## Result

The repository now contains enough public data to discharge P0 through the
replacement AR construction.  It still does not contain the actual monoidal
coefficient comparison needed to construct an inhabitant of
`ExternalGeometry`.  Historical hashes alone remain non-evidence for the
retired route.

Consequently, the strongest supported result remains the conditional theorem
in `Smooth4PC/T73Conditional.lean`. In particular, a synthetic Lean instance
whose fields are filled by arbitrary vector spaces and maps would merely
rename the assumptions and is not an acceptable completion.

Run the availability audit with:

```text
python -B scripts/check_geometric_evidence.py
```

The expected result remains `MISSING` for the retired historical artifacts.
That output no longer measures P0: the replacement witness is
`audit/t73_ar_product_witness.json` and has its own deterministic replay.

## Ordered verdicts

Only the following three verdict words are used. `DISCHARGED` means that the
public object and an independently checkable argument are both available;
`PARTIAL` means that the cited general theorem or finite algebra is available
but the candidate-specific identification is not; `OPEN` means that a
load-bearing comparison or geometric instance is absent.

| priority / item | verdict | public boundary |
|---|---|---|
| P0: replacement AR presentation is the Cappell--Shaneson handlebody | **DISCHARGED** | public AR scan, parameterized product-annulus witness, exact matrix bridge, two geometric cancellations and embedded collar |
| historical frozen diagram identity | **OPEN / RETIRED** | the full PD and builder remain absent and are not used |
| P1: truncated Burau cubic is an MWW lasagna evaluation | **OPEN** | the script computes a finite Burau scalar, but no public comparison theorem identifies it with the one-handle/HH0/cabled-quotient functional |
| P2/E7: chosen spheres are valid 3-handle attachments | **DISCHARGED** | P0 supplies the handle pattern/ball; HJ plus the relative complete-system lemma gives the standard system outside it |
| P2/E10: `q01,q12` are the MWW quotients | **PARTIAL** | MWW's local module-action formula and symmetric-monoidal C imply the three-handle relations; C remains uninstantiated |
| P3/E11: four-handle transport | **DISCHARGED** | P0 fixes the handle decomposition and MWW Proposition 3.4 gives the grading-preserving isomorphism |
| P3/E12: standard-sphere control | **DISCHARGED** | MWW Corollary 3.5 computes the genuine module concentrated in bidegree zero |
| P3/E13: homotopy-sphere criterion | **DISCHARGED** | P0 identifies the replacement presentation and the determinant criterion applies |

The remaining open candidate-specific comparison is P1/C.

## Field-by-field allocation

| Lean obligation | What would discharge it | Current result |
|---|---|---|
| `x0`, `ell0`, `ell0_x0` | A public construction of the selected MWW raw class and detector on the actual cut presentation | Open: P0 supplies the collar, but the MWW/Hattori binding is absent |
| `q01`, `ell1_comp_q01` | The complete candidate-specific beta/psi presentation and proof that the detector annihilates every relation | Open as geometry: only derived ledgers and abstract quotient algebra are public |
| `q12`, `ell2_comp_q12` | An HJ-valid replacement and the two MWW relations on the complete source | Derived from P0 and symmetric-monoidal C; partial while C is open |
| `transport`, `fourIso` | The published handle-decomposition/four-handle theorems applied to the same identified module | General theorem available; candidate identification now depends on C |
| `s4DegreeZero` | The rational, grading-preserving `S^4` computation | Supported by the published MWW result, but still external to Lean |
| `diffeomorphismEquiv` | Graded diffeomorphism invariance of the same lasagna module | Supported as a general external theorem |
| `matrixConditionsToHomotopySphere` | The Cappell--Shaneson criterion applied to the identified matrix | Discharged mathematically by P0 plus Iwaki, Proposition 2.1; external to Lean |

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

The public AR replacement now checks the two mathematical joins that the old
hash test could not decide:

- the locally straightened representative of the linear torus map and the
  Aitchison--Rubinstein product-annulus framing must be transported through
  the stated mapping-torus and Laudenbach--Poenaru diffeomorphisms;
- the relative descending-tangle isotopy must preserve all marked gates,
  owner/cocore labels and chosen longitudes needed by the detector and later
  sphere calculations.

They are written as the mapping-torus diffeomorphism, product-annulus normal
fields, simultaneous cancellation bands and embedded collar in the P0
discharge proof.  The historical PD route remains unverified but unused.

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

The explicit owner-coordinate route still lacks the TH1, TH2 and THXY
witnesses.  It is no longer load-bearing.  Once P0 supplies the actual handle
pattern and a detector ball, reversing the three 3-handles gives
`partial W2 ~= #3(S1 x S2)`.  HJ Theorem 5.3 and its relative
complete-system lemma then provide a standard attaching system disjoint from
that ball.  Thus E7 is a proved consequence of P0, rather than an independent
large-certificate requirement.

## P2/E10: actual MWW maps

MWW supplies both the coequalizer and an intrinsic local module-action
description.  At `N=2` the local relations set the one-dotted essential sphere
to the identity and the undotted sphere to zero.  For the relative standard
system outside the detector ball, these equations follow on the whole source
from the symmetric-monoidal naturality required in C.  Therefore S introduces
no independent signed-movie input; it remains partial only while C is open.

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

1. Publish or reconstruct the P0 embedded witness and the actual monoidal C
   coefficient comparison under `evidence/geometric/`, together with
   generators and schemas.
2. Make a clean replay start from the matrix and convention choices, generate
   the full framed labelled presentation, and reproduce every pinned hash.
3. Emit a compact, independently checkable Kirby/isotopy ledger rather than
   only a terminal `PASS` receipt.
4. Prove the Burau--MWW comparison on the full coefficient category, including
   beta/psi naturality and monoidality away from the detector ball; S then
   follows from the relative theorem.
5. Generate the `ExternalGeometry` data from that replay boundary. Keep the
   published topology theorems as named external results unless they are
   genuinely formalized.

No unconditional SPC4 claim is justified before these steps pass independent
mathematical review.
