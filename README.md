# Smooth4PC T73 — trace-73 skein-lasagna obstruction

[中文说明](README.zh-CN.md)

This repository presents a paper-level skein-lasagna obstruction for the
trace-73 Cappell--Shaneson homotopy 4-sphere associated with
\[
A=\begin{pmatrix}0&269&1240\\0&41&189\\1&0&32\end{pmatrix}
\]
(Iwaki standard form \(X_{41,189,73}\)).

**The manuscript currently proves P0/E13 at paper level and gives a
conditional skein-lasagna obstruction; C and S remain open at the corrected
coefficient comparison.  No unconditional counterexample is claimed.** The controlling manuscript is
[`paper/spc4-t73-candidate/main.tex`](paper/spc4-t73-candidate/main.tex)
(*A skein-lasagna obstruction for a trace-73 Cappell--Shaneson
sphere*).

## What is proved, and what is open

For an explicit **Johnson-generator** handle presentation the paper now gives
a paper-level construction of **P0** and transports the complete AR upper
handles to obtain **E13/P3**, including \(X_J\cong\Sigma_A^0\).  The
complete source and target constructors now save \(1260\) endpoints and
\(630\) framed arcs each.  Their matchings differ in eight wrong-side
connectors, so the proposed literal two-representable split is refuted.  Its
degree \(223\) is target-only; the actual **C/S** map and its nonzero degree
remain open.

An exact finite calculation gives a nonzero divided cubic \(D_3=2624\). An
Artin--Magnus certificate and the pure-braid Andreadakis theorem establish a
third-order property of the public braid word.

A Lean development formalizes the **abstract quotient argument**: given
interface data assembling the MWW quotients and four-handle transport
(`ExternalGeometry`), a nonzero class in any nonzero quantum degree would obstruct
diffeomorphism with \(S^4\). Those geometric interfaces are **not** constructed
in Lean.

| Layer | Status |
| --- | --- |
| Finite algebra (endpoint scalar \(2624\), historical degree \(494\), \(\det A=\det(A-I)=1\)) | Checked in Lean; no actual MWW class degree is currently constructed |
| Abstract conditional implication | Checked in Lean |
| Johnson P0 / E13 / topological P3 | Proved at paper level after detector retyping |
| C / S coefficient and hemisphere comparison | **Open** at the actual coend/currying and statewise shadow |
| Lean inhabitant of `ExternalGeometry` | **Open** |

The exact Lean boundary is
[`Smooth4PC/T73External.lean`](Smooth4PC/T73External.lean). Premises audit:

```text
python3 scripts/audit_t73_premises.py --check
```

The legacy script still prints historical PASS labels and is not an
authoritative completion test; use `audit/RUNNING_PAPER_AUDIT.md` and the new
fail-closed gates instead.

The complete selected-C geometry bundle is rebuilt and checked with:

```text
python3 scripts/build_t73_complete_geometry_bundle.py --write
python3 scripts/build_t73_complete_geometry_bundle.py --check
python3 scripts/build_t73_complete_geometry_bundle_v2.py --check
```

This saves all currently reconstructible endpoint/arc geometry.  Its manifest
deliberately remains `OPEN` at the actual coend/currying map.

### Gmsh frames and partitioned-frame inputs

The independently verified Gmsh prefix-20 frame is
[`geometry/examples/t73_selected_source_gmsh_prefix20_frame.json`](geometry/examples/t73_selected_source_gmsh_prefix20_frame.json).
Its verification receipt is
[`audit/t73_selected_source_gmsh_prefix20_frame_verification.json`](audit/t73_selected_source_gmsh_prefix20_frame_verification.json).
It contains 4134 vertices, 23725 tetrahedra, 20 arcs/ribbons, five boundary
components and exact exterior volume 63968; its only valid status is
`PASS_PREFIX_ONLY`, not complete T73 geometry.

The partitioned route retains three exact, committed inputs:

- [`geometry/t73_selected_source_partition_z0.json`](geometry/t73_selected_source_partition_z0.json): all ruled-ribbon, core, push-off and connector fragments cut at `z=0`;
- [`geometry/t73_z0_interface_triangulation.json`](geometry/t73_z0_interface_triangulation.json): the common 36-vertex/42-triangle interface with four insertion-hole loops;
- [`scripts/probe_t73_z0_block_volumes_gmsh.py`](scripts/probe_t73_z0_block_volumes_gmsh.py): a fail-closed Gmsh OCC probe. Its `PASS_FRAGMENT_BATCH_ONLY` result covers only the requested lower-side fragment batch, never the complete frame.

For WSL topology runs, use an isolated environment (the Gmsh wheel also needs
the listed system runtime libraries):

```text
python3 -m venv ~/.venvs/t73-topology
~/.venvs/t73-topology/bin/python -m pip install 'regina>=7.4' 'gmsh==4.15.2'
sudo apt-get install libglu1-mesa libxft2
~/.venvs/t73-topology/bin/python scripts/probe_t73_z0_block_volumes_gmsh.py --fragments 10
```

Routine exact checks, which do not rerun a full mesh, are:

```text
python3 scripts/build_t73_selected_source_partition_z0.py --check
python3 scripts/build_t73_z0_interface_triangulation.py --check
python3 scripts/build_t73_gmsh_frame_verification_receipt.py --check-files
python3 scripts/build_t73_gmsh_frame_verification_receipt.py --check-files --frame geometry/examples/t73_selected_source_gmsh_prefix20_frame.json --output audit/t73_selected_source_gmsh_prefix20_frame_verification.json --expected-prefix 20 --expected-vertices 4134 --expected-tetrahedra 23725 --expected-arcs 20 --expected-ribbons 20 --expected-boundary-components 5 --expected-exact-volume 63968
```

The monolithic 630-ribbon HXT attempt was OOM-killed without writing a mesh.
The partition inputs and probes are therefore preserved as construction data;
the common 630-ribbon tetrahedral frame gate remains `OPEN`.

**Erratum (2 September 2026).** An earlier draft mixed two endpoint index
tables and reported \(-59072\). With both objects in the collar table used by
the braid word, the exact value is \(+2624\) (still nonzero).

## PDFs for review

- English: [`output/pdf/spc4-t73-candidate.pdf`](output/pdf/spc4-t73-candidate.pdf)
- Chinese: [`output/pdf/spc4-t73-candidate-zh.pdf`](output/pdf/spc4-t73-candidate-zh.pdf)

Paper sources and build notes:
[`paper/spc4-t73-candidate/README.md`](paper/spc4-t73-candidate/README.md).

The default paper build writes the reviewed English PDF directly to the
repository output directory (Windows path
`C:\Users\Administrator\Documents\ChatGPT\smooth4pc-t73-lean\output\pdf`):

```text
bash scripts/build_papers.sh          # English, default
bash scripts/build_papers.sh --zh     # Chinese only
bash scripts/build_papers.sh --all    # both
```

## Start here

1. Read the paper abstract and §3 (precise statements) in
   [`paper/spc4-t73-candidate/main.tex`](paper/spc4-t73-candidate/main.tex)
   or the English PDF above.
2. Follow [`REPRODUCING.md`](REPRODUCING.md) to build from a fresh clone, audit
   reported axioms, and recompute the detector.
3. Replay the current actual-geometry chain with the single command below
   (or use the individual commands for a failing stage).
4. For the independent-review boundary map, see
   [`docs/INDEPENDENT_REVIEW.md`](docs/INDEPENDENT_REVIEW.md).

## Fast replay

Requires Python 3.10+. From the repository root:

```text
# Current actual AR → C → S → four-handle chain
python3 -B scripts/verify_t73_actual_chain.py

# Also rebuild the expensive 93-factor PL map and aggregate P0 certificate
python3 -B scripts/verify_t73_actual_chain.py --full
```

Expected final lines:

```text
T73_ACTUAL_CHAIN=PASS
T73_FORMAL_STATUS=CONDITIONAL_EXTERNAL_GEOMETRY
```

The first line covers the mathematical certificate chain. The second records
the remaining formalization boundary: no Lean inhabitant of
`ExternalGeometry` or `CSTopologyData` is manufactured from JSON booleans.

## Individual replay commands

Requires **Python 3.10+** from the repository root. On Windows, `python` is
fine wherever `python3` appears. Each `--check` regenerates the certificate
in memory and compares it to the committed JSON under `audit/`.

### Finite detector (\(D_3=2624\))

```text
python -I -B scripts/recompute_t73_delta3.py --check
```

Expect `DELTA3_ETA_T1=2624`, `DELTA3_XI=0`, and `VERIFY=PASS`.

### Johnson P0 → C → S → P3/E13

```text
# P0 (~1–2 min): AR bridge, cancellations, geometric braid
python -B scripts/certify_t73_p0_johnson.py --check

# Actual AR link and both Kirby cancellations
python -B scripts/verify_t73_actual_ar_link.py --check
python -B scripts/verify_t73_handle_cancellation.py --check
python -B scripts/verify_t73_actual_cut_tangle.py --check

# C: every actual rectangle/circle, comparison supports, assembled witness
python -B scripts/verify_t73_actual_product_rectangles.py --check
python -B scripts/verify_t73_actual_leftover_z_circles.py --check
python -B scripts/verify_t73_actual_geometric_braid.py --check
python -B scripts/verify_t73_endpoint_transport.py --check
python -B scripts/certify_t73_c1_cut_link.py --check
python -B scripts/certify_t73_c2_comparison.py --check
python -B scripts/verify_t73_product_ribbon_isotopy.py --check
python -B scripts/generate_t73_c_comparison_witness.py --check

# S: actual H1 disk tracks, Kirby surface transport, sphere/hemisphere maps
python -B scripts/verify_t73_johnson_dual_disk_movie.py --check
python -B scripts/verify_t73_three_handle_surface_transport.py --check
python -B scripts/verify_t73_actual_sphere_system.py --check
python -B scripts/verify_t73_hemisphere_movies.py --check
python -B scripts/certify_t73_s_relative_moves.py --check

# P3: four-handle picture, standard-S^4 support, CS identification
python -B scripts/certify_t73_p3_four_handle.py --check
python -B scripts/certify_t73_e12_s4.py --check
python -B scripts/certify_t73_e13_close.py --check
python -B scripts/certify_t73_e13_identification.py --check

# Premise summary (mathematical PASS; analytic Lean packaging remains open)
python -B scripts/audit_t73_premises.py --check
python -B scripts/check_t73_claim_boundary.py
```

| Script | Role | Expect |
| --- | --- | --- |
| `certify_t73_p0_johnson.py` | P0 Johnson replacement | `T73_P0_JOHNSON_CERTIFICATE=PASS` |
| `verify_t73_actual_ar_link.py` | Seven-component framed AR link | `ACTUAL_AR_LINK=PASS` |
| `verify_t73_handle_cancellation.py` | Actual t/h_CS and x/m_1 movies | `T_HCS=PASS`, `X_M1=PASS` |
| `verify_t73_actual_cut_tangle.py` | Post-cancellation detector | `PASSAGES=44`, `LEFTOVER_Z_CIRCLES=227` |
| `verify_t73_actual_product_rectangles.py` | Every actual y/z rectangle | `RECTANGLES=44` |
| `verify_t73_actual_leftover_z_circles.py` | Every source-bound leftover circle | `CIRCLES=227` |
| `certify_t73_c1_cut_link.py` | 44 ribbons + 227 leftover \(z\) | `RECTANGLES=44`, `LEFTOVER_Z_CIRCLES=227` |
| `certify_t73_c2_comparison.py` | Disjoint C2 supports / \(H\) movies | `T73_C2_COMPARISON=PASS` |
| `generate_t73_c_comparison_witness.py` | C ledger bound to P0/C1/C2 | `C_STATUS=PASS` |
| `verify_t73_johnson_dual_disk_movie.py` | 93-factor H1 disk transport | `GEOMETRIC_CORE_COUNTS=[12578,1824,409]` |
| `verify_t73_three_handle_surface_transport.py` | Disk tracks through every Kirby band | `ACTUAL_THREE_HANDLE_SURFACE_TRANSPORT=PASS` |
| `verify_t73_actual_sphere_system.py` | Actual partial-W2 sphere system | `ACTUAL_SPHERE_SYSTEM=PASS` |
| `verify_t73_hemisphere_movies.py` | Actual MWW three-handle maps | `ACTUAL_W2_LASAGNA_MAP=True` |
| `certify_t73_p3_four_handle.py` | \(X_J\) four-handle layer | `E11`/`E12` PASS; `E13=PARTIAL` by design |
| `certify_t73_e12_s4.py` | Historical empty-link degree \(494\) check; MWW vanishing holds in every nonzero degree, but the actual candidate degree is open | `S4_DEGREE_494_ZERO=True` |
| `certify_t73_e13_*.py` | \(X_J\cong\Sigma_A^0\) pipeline | `IDENTIFIED_WITH_SIGMA=True` |
| `audit_t73_premises.py` | Aggregate status | `PASS_MATHEMATICAL_LEAN_PARTIAL`, `COUNTEREXAMPLE=True` |
| `check_t73_claim_boundary.py` | Paper/Lean claim boundary | `T73_CLAIM_BOUNDARY=UNCONDITIONAL_PAPER_LEAN_PARTIAL` |

**Notes.**

- Certificates are SHA-chained: C binds to P0, S to P0+C, P3 to P0+C+S. Changing an upstream certificate without regenerating dependents will fail `--check`.
- `certify_t73_p3_four_handle.py` reporting `E13=PARTIAL` is expected; full \(\Sigma_A^0\) identification is in the `e13_*` scripts.
- The old word-only `band_slides` and `derived_crossings` route was removed;
  current checks start from the actual framed AR link and source-bound arcs.
- Lean compile (`tests/test_t73_minimal_formalization.py`) is separate and slower (~5–10 min); see [`REPRODUCING.md`](REPRODUCING.md).

### Focused tests and Lean compilation

```text
python3 -m unittest \
  tests.test_t73_actual_cut_tangle \
  tests.test_t73_actual_product_rectangles \
  tests.test_t73_actual_leftover_z_circles \
  tests.test_t73_actual_geometric_braid \
  tests.test_t73_endpoint_transport \
  tests.test_t73_johnson_dual_disk_movie \
  tests.test_t73_three_handle_surface_transport \
  tests.test_t73_actual_three_handle \
  tests.test_t73_e13_close tests.test_t73_e13_identification

python3 scripts/generate_t73_lean_geometry.py --check
python3 scripts/check_t73_external_geometry_boundary.py
lake env lean Smooth4PC/T73CertificateIndex.lean
lake env lean Smooth4PC/T73JohnsonTransvections.lean
lake env lean Smooth4PC/T73GeometryPack.lean
lake env lean Smooth4PC/T73Conditional.lean
```

`lake build` has no default target in this repository; use the explicit module
commands above. The generated Lean index records the actual artifact hashes and
the exact counts `44`, `227`, `93`, `[12578,1824,409]`, `6`, and `1513`.
The boundary checker must report
`OPEN_MISSING_ANALYTIC_MWW_FOUNDATIONS`; changing this to PASS requires actual
Lean definitions of the MWW modules and maps, not a certificate flag.

## Reproducibility contract

- Lean toolchain: `leanprover/lean4:v4.32.1`
- mathlib revision: `520045ab14e26149ee970e2e617ca04b09bde5d6`
- Python: 3.10 or later
- Lean axiom reports are checked by the focused formalization tests rather
  than a hand-maintained count in this README.
- allowed reported axioms: `propext`, `Classical.choice`, `Quot.sound`
- `sorryAx`: absent
- expected detector value: `2624`

The committed `lake-manifest.json` pins Lean dependencies. Build products and
local dependency copies are not part of the source contract.

## Scope

This is a public verification package for a **conditional obstruction**, not
an unconditional counterexample or a claim of complete Lean formalization.
The remaining load-bearing problem is the relative two-representable MWW
coefficient split and its statewise beta/psi/hemisphere naturality.

## Why this is being released on GitHub first

GitHub is the first public release channel for access, speed and
reproducibility—not a substitute for scholarly review. Existing arXiv history
is in computer science; mathematics-category endorsement may be unavailable.
The full argument, Lean sources, certificates and replay instructions are
inspectable here. After substantive scrutiny, a conventional preprint
submission is intended.

## License

The repository is released under the [MIT License](LICENSE).
