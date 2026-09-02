# T73 proof state ledger

**Current authority:** the conditional paper together with the current P0, C,
and relative-S research notes.  Entries below describing unavailable
historical PD/TH objects are recovery history, not current premises.

**Updated:** 2026-09-01 (Asia/Tokyo)
**Purpose:** recovery source of truth for the mathematical chain. Read this
before rerunning any long sphere computation.

## Current carrying class

```text
class:        v_T = eta_R[T_1], T_1 = B_act^{-1} U_(0,5)
not class:    xi
not class:    mixed Z
base value:   D_3(v_T) = -59072
final degree: (homological, quantum) = (0,494)
scope:        h^3 associated graded / ordinary divided functional
```

The outer detector contains one factor `rho_h(W)-I`. Applying it to `xi`
would introduce a second factor and starts in order six. The mixed-Z branch
has an actual raw lift but is contained in the full action-closed two-cup
`psi0` ideal and is retired as the carrying class.

## Layer audit

| layer | current status | current evidence |
|---|---|---|
| E1 paired-annulus Hattori coefficient | DISCHARGED | 44 public product rectangles and 227 residual circles in the C witness |
| E2 selected diagonal class | DISCHARGED | named inverse Hattori image of `Id_U tensor X^227` |
| E3 coefficient q-trace and raw-state binding | DISCHARGED | BPW/BHPW completed shadow and sign-robust endpoint binding |
| E5/E6 one-/two-handle beta/psi quotient | DISCHARGED | divided beta average, through-degree firewall and core-counit psi equations |
| P0 replacement AR framed lift | DISCHARGED | public AR scan, `audit/t73_ar_product_witness.json`, deterministic generator, two product cancellations and embedded detector ball |
| historical G1/DIAGRAM identity | OPEN / RETIRED | the builder and full PD remain unavailable and are not used |
| E8 three chosen sphere rows | NOT REQUIRED BY RELATIVE ROUTE | the historical objects are unavailable, but HJ relative uniqueness plus monoidal C replaces this explicit-sphere route |

The E5/E6 proof uses the one-cup through-86 cell, the ordinary divided
functional, beta's `O(h)` defect against `W-I=O(h^3)`, and split-injectivity of
the dotted direct system after quotienting the undotted image. It does not use
the retired owner-only mixed-Z model.

The first G1 PASS was premature because it treated `Ae_i` as a complete
attaching circle.  The replacement proof instead uses the full
`m_i=t phi_A(x_i) t^-1 x_i^-1` object.  Aitchison--Rubinstein pp. 5--7
construct its bottom/top/base-handle product ribbon, and pp. 16--17 construct
the product normal.  The mapping-torus diffeomorphism transports the whole
labelled framed presentation.  The two product cancellations give
`t->empty` and `x->z`, after which the detector collar is defined in a
standard regular-neighborhood ball.  The empty free word of `r_zx` is not
used to infer a split disk.  No comparison with the historical DIAGRAM is
claimed.
Framing is transported from the actual AR annuli, not inferred from the
emitter's discarded blackboard winding.

## Sphere evidence chronology

The early `OPEN` files are historical diagnostics, not the latest state.

| local time, 2026-08-31 | artifact | status |
|---|---|---|
| 02:01--02:02 | `THREE_SPHERE_MAP_LEVEL_FINAL_VERDICT.md`; `ACTUAL_THREE_SPHERE_H0_FINAL_DECISION.md` | EARLY OPEN; superseded by later chosen-sphere artifacts |
| 12:10--12:16 | TH1 chosen decision and hardened hostile replay | PASS |
| 12:13--12:18 | TH2 chosen decision and hardened hostile replay | PASS |
| 12:35 | THXY full macro successor and re-audit | PASS |
| 12:48 | `FULL_CHAIN_INDEPENDENT_FINAL.md` | later combined audit; its old `xi` wording is not consumed |
| 20:09 | global chain certificates | corroborating combined records; current upstream class is replaced by `v_T` proof |

### Do not rerun before checking these identities

```text
TH1 geometry
EE620E6B085A5F9E1C73CFDD1AD04FC0682CEC74DA3DBF8AFE70DD19C038E3A0
  D:/tmp/r6/matrix_attack/th12_actualization/TH1_EXHAUSTIVE_ALL_ROW_GEOMETRY.json

TH2 geometry
4D1B627C0343A1C464319704EAFADCA127902A2E4E90CF1C283004359B7ADC24
  D:/tmp/r6/matrix_attack/th12_actualization/TH2_EXHAUSTIVE_ALL_ROW_GEOMETRY.json

THXY geometry
EABF67C0D1AE309F0281297710A283B8ED5A11D88C8E810837932313F4C53227
  D:/tmp/r6/fullw_tangent_coend/generators/THXY_FULL_MACRO_P3FREE_HJ_CERT.json
```

The three chosen spheres lie in one actual `W2`, in mutually disjoint movie
sectors, and their class matrix has determinant `+1`. HJ's theorem relates the
chosen system to the historical attaching system by isotopy, permutation and
3--3 handle slides. A 3--3 handle slide gives an equivalent upper cobordism
relative to incoming `W2`; it is not an arbitrary boundary-diffeomorphism
substitution.

For each chosen sphere, every noninvertible event is new--new and the old
one-cup block is an identity cylinder. Actual core counits therefore give the
whole-old-source divided rows

\[
\Lambda_3\Sigma_j(0)=0,
\qquad
\Lambda_3(\Sigma_j(1)-\operatorname{Id})=0,
\qquad j=1,2,3.
\]

## Deliberately unclaimed

- historical attaching-sphere movies were not recovered;
- no full-`q` series cocone is claimed;
- no conclusion should use `D_3(xi)` or the retired mixed-Z all-level model;
- the earlier end-to-end `HOLE` verdict was tied to the incorrect short G1
  bridge; after replacement by the AR product-ribbon proof, a fresh full-chain
  independent review is still required.
