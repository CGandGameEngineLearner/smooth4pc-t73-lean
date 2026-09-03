# AUD-B — hostile audit of the q494 / t73 falsification chain

Date: 2026-08-30. Attack order: top-down (terminal implication first).
Scope: the five named artifacts + everything I had to pull to check them.
No subagents. All temp work in `D:\tmp\r6\AUD_B\`.

Evidence grades: **PROVED** / **DERIVED (from granted premises)** / **UNVERIFIED** /
**WRITTEN (asserted, no derivation in the chain)**.

---

## 1. Verdict

```text
CHAIN_HAS_HOLE
```

The load-bearing scalar `-59072` is real and I reproduced it from the raw braid word.
What is not established is that it is the value of the functional **on the class the
chain now names as the carrier**. The chain's own SHA-pinned inputs record that
`eta_R[T1]` has shadow `Id_{U1}` — a braid-free, `h`-constant object — while `-59072` was
computed as `[h^3] ell (rho_h(W)-I) u`, i.e. as the value on the *difference* `xi`, the
carrier the chain explicitly RETRACTS. Two SHA-pinned inputs to the same certificate give
mutually exclusive accounts of whether `(rho_h(W)-I)` belongs to the functional or to the
class, and the answer decides between `-59072` and `0`.

Second, independent hole: the standard-`S4` ANCHOR firewall is zero **by the identity
`B_{R_std}=I`, before any of the audited machinery runs**. It exercises none of the
beta / psi / sphere / three-handle descent it is claimed to firewall, so it cannot detect
the failure mode it exists to detect.

---

## 2. Holes, by severity

### H-1 (fatal to the scalar) — the number was re-carried, not recomputed

**Where:** `V3_FINAL_CANDIDATE_RESULT.md` "Detected class"; `FINAL_CLEAN_Q494_CHAIN_HOSTILE_AUDIT.md` sections 1-2.

The V3 report states: *"The functional is evaluated on `v_base = eta_R[T1]`, `T1 = F_Omega^-1 W^-1 U1` ... Its complete cubic row evaluates to `-59072`."*

The chain's own machine records say otherwise.

`D:\tmp\r6\agents\sphere_data_excavation\PRODUCT_NORMAL_CHRISTOFFEL_THXY_MOVIE.json`
(a SHA-pinned input read by `v3_final_candidate.py`), key
`one_cup_regular_slice.fixed_R_relative_class.Hattori_components`, verbatim:

```
"eta_Rw[T0] -> Id_(W U1) tensor X^227",
"eta_Rw[T1] -> Id_(W W^-1 U1)=Id_U1 tensor X^227"
```

and in the same object:

```
"shadow_K0": "[W U1]-[U1]",
"anchor_control": "when W=I the two framing-corrected objects coincide and xi_Omega=0",
"status": "PASS_ONE_HANDLE_BETA_PSI_FILTRATION; SPHERE_NOT_CHECKED"
```

`D:\tmp\r6\agents\finite_type_leading\qhh_endpoint_s87_functional_audit.py:112-120`,
verbatim source:

```python
"T0": "F_Omega^-1 U1 : 86->88",
"T1": "F_Omega^-1 W^-1 U1 : 86->88",
"xi": "eta_R[T0]-s_inv eta_R[T1]",
    "qAKh(Sh(eta_R[T0]))=rho_h(W) u",
    "qAKh(Sh(eta_R[T1]))=u",
"u": "e_0-e_5 in the one-defect target",
"difference": "(rho_h(W)-I)(e_0-e_5)",
```

So: the `W` in `T1` **cancels** (`Id_(W W^-1 U1)=Id_U1`); `eta_R[T1]`'s image is the
constant integer vector `u = e_0-e_5`, with no `h`-dependence at all; and
`(rho_h(W)-I)u` is the image of **`xi`**, the retracted carrier.

`RELATIVE_QLEADING_DOWNSTREAM_RESULT.md` section 3 computes the number in exactly that
frame: *"Use `xi_Omega = eta_R[F_Omega^-1 U_1] - s_inv eta_R[F_Omega^-1 W^-1 U_1]`, so its
shadows are literally `Id_(W U1)` and `Id_U1`. ... `[h^3] ell(W-I)u = -59072`."* The
section is titled **"Corrected physical one-cup coefficient"** — the coefficient of `xi`.

Against this stands one other SHA-pinned input,
`RELATIVE_QLEADING_DOWNSTREAM_CERT.json`, key `strategy`:

```
"families": ["tau_W,h(v)=rho_h(W) Phi_h(Sh(v))", "tau_I,h(v)=Phi_h(Sh(v))"],
"difference": "Delta_h(v)=(rho_h(W)-I)Phi_h(Sh(v))"
```

Under this second reading the operator is part of the **functional**, and then
`Delta_3(eta_R[T1]) = ell A_3 u = -59072` while `Delta_3(xi)=O(h^6)=0` — self-consistent
with V3's retraction.

**The two readings are not reconcilable as written**, because reading (A) requires
`Phi_h(Sh(eta_R[T0]))` to be `W`-free while `qhh_endpoint_s87_functional_audit.py:116`
records it as `rho_h(W)u`. Nowhere in the chain are `Phi_h(Sh(-))` and `qAKh(Sh(-))`
distinguished; they are used interchangeably.

**Missing object, named exactly:** a computation of `[h^3] ell . (image of eta_R[T1]
alone)` under one fixed, stated definition of the functional, with the same definition
used for the retraction of `Delta_3(xi)`. I searched `D:\tmp\r6\agents\**` (`*.md`,
`*.py`, `*.json`) and found no evaluation of the functional on a *single* `eta_R[T_i]`;
every computation evaluates `(rho_h(W)-I)u`, which is `xi`'s image.

Grade: the reassignment of `-59072` from `xi` to `eta_R[T1]` is **WRITTEN**, not derived.
Under the reading forced by the two SHA-pinned records above, the correct value is **0**
and the chain is void; under the other reading it is `-59072` and H-2 below applies.

### H-2 (fatal to the discrimination) — the ANCHOR firewall is white-given

`ACTUAL_STANDARD_CONTROL_RESULT.md` section 7, verbatim:

> standard branch 满足 B_{R_std}=I，所以 I(R_std)=0 在 harmonic projection、beta、psi、
> z caps 或 sphere maps 之前已经 exact 成立。

and in the same file:

> 我们仍没有计算 t73 非零候选是否通过 sphere，但 standard control 不会在 sphere 阶段凭空变成非零。

and `actual_standard_control_probe.py:225`: `"relative_operator": "W_std-I=0"`.

The control returns `0` because the operator is identically zero **before** beta, psi, the
sphere maps and the three-handle quotient. It exercises **none** of the machinery under
audit. Any broken descent argument returns `0` on this control too, because `0` descends.
Discriminating power: **zero**.

Not my inference alone — the chain's own earlier files say it:

* `agents/finite_type_leading/SPHERE_GR3_SURVIVAL_RESULT.md:219` — *"stabilized ANCHOR control 满足 relative input `W_std-I=0`，所以在任何 sphere map 之前就是 0；linear quotient 保持 0。这是合法 good control，却不决定 t73 非零 branch。"*
* `agents/secondary/SECONDARY_RESULT.md:151` — *"`ANCHOR-537` | **FAIL** | No stable full quotient or blowdown/3-handle map has been evaluated on `X(5,3,7)`. There is no proof that the derived construction collapses to the standard `S4` value."*
* `agents/mixed_relations/MIXED_RELATIONS_RESULT.md:143` — a valid route requires *"...(iii) calculate `beta`, both `psi` maps, and **both sphere maps** as homogeneous, with a nonzero t73 class that is **killed on ANCHOR-537**. Such a construction would be a new route, not a completion of the argument presently stated."*
* `agents/blowdown_orbit/BLOWDOWN_RESULT.md:60` — precedent for exactly this failure mode: a functional *"在 `A_m`、`ANCHOR-537`、t73 以及任何别的候选 homotopy sphere 上逐字同值。它过 good-case 门，但判别力为零。"*

The named requirement (killed on ANCHOR-537 by ANCHOR's own sphere maps) has never been
met, and V3 closes without it.

**Cheap decisive test the chain never ran** (main constructive recommendation): run the
*identical* Reynolds / D-U / three-handle transport on the stabilized ANCHOR
(`X(5,3,7) = S^4`) with a **nonzero** admissible base row — e.g. `ell . A_3` imported from
any `Gamma_3` collar braid, or any nonzero covector satisfying the pairwise
(negative,positive) equality. Because `Sz(S^4) = Z` in bidegree zero (`kirby.tex:430`), a
`q=494` class there **must** be zero. If the recipe still reports "nonzero q494 class",
the recipe is refuted. I could not run it: the ANCHOR sphere maps do not exist in the
corpus (`TL88_MR_CYCLE_MOVIE_RESULT.md:418` — *"当前没有 t73 或 ANCHOR 对应的 sphere
matrices"*). `NOT COMPUTED` — missing object: `ANCHOR537_THREE_HANDLE_SPHERE_MAPS`.

### H-3 (structural) — the three-handle "descent" is bookkeeping, not a constraint

MWW's relations, verbatim, `kirby.tex:729-740` (Theorem `thm:main`, `eq:P1`/`eq:P2`):

```
\bPsi_{I \times \del \Wone; \Sigma_j(n\bullet), \alpha'}(v)=0, \ \  n =0, 1, \dots, N-2,
\bPsi_{I \times \del \Wone; \Sigma_j((N-1)\bullet), \alpha'}(v)= v
```

For `N=2` this is exactly `f(Uv)=0`, `f(Dv)=f(v)`. **PROVED** that the chain states MWW
faithfully.

The chain's discharge is `PEIFFER_RIBBON_H0_UNIT_MINOR.md` part (c): with `A=Z[X]/(X^2)`,
`D_b = X^{tensor b}`, `U_b = Delta^{b-1}(1) = sum_a X^a (x) 1 (x) X^{b-1-a}`, rows
`E_b = eps^{tensor b}`, `Q_b = one* (x) eps^{tensor (b-1)}`. I checked the four
evaluations by hand: `E_b(D_b)=1, E_b(U_b)=0, Q_b(D_b)=0, Q_b(U_b)=1`. **Arithmetic: correct.**

But this is the ordinary Frobenius identity `eps(X)=1, eps(1)=0` on a genus-0 tree. It
depends only on `b` and on `A`. It has **no** t73-specific content, and the row at every
non-base level is *defined* by the transport `rho_t := rho_s . R` that inverts `D` and
kills `U`. The relation is therefore satisfied **by construction**; the witness is the
constructed transport itself. Construction self-check: **triggered — bookkeeping, not a
discovery.**

Consequence: the same discharge goes through verbatim for the standard-`S^4` presentation
with the same leaf counts, where the `q494` class must be zero. That is the inconsistency
H-2's test would expose.

I found **no** artifact in `D:\tmp\r6\agents\**` that evaluates the functional on an
actual three-handle relation element `U_j(w)` for a specific `w` and obtains `0`
numerically. The single numeric relation check I did find
(`HOSTILE_FULL_DOMAIN_DESCENT_AUDIT.md` section 2: `rho psi0_rxy = -27552-(-27552) = 0`)
belongs to the **retracted** `-28864` row and was never redone for `-59072`.

### H-4 — a conditional verdict was string-grepped into an unconditional PASS

`v3_final_candidate.py:83` asserts:

```python
assert "H0 UNIT MINOR, CONDITIONAL ON THE STATED GEOMETRY:     YES" in minor
```

The file it greps, `PEIFFER_RIBBON_H0_UNIT_MINOR.md`, ends:

```
H0 UNIT MINOR, CONDITIONAL ON THE STATED GEOMETRY:     YES
EXISTING RETRACTED TH1/TH2 GEOMETRY ARTIFACT:          STILL RETRACTED
CURRENT FILES ALONE ESTABLISH ALL LEMMA HYPOTHESES:    NO
```

and opens with *"If 'embedded corridor', 'DAG' and 'bigons' mean only individually
embedded samples, word hashes or detached prose assertions, the answer is **NO**."*

The compiler takes the conditional line and drops the condition. The independent route
audit at `agents/hj_scope_hostile/PEIFFER_RIBBON_ROUTE_AUDIT.md` reaches
`OVERALL ACTUAL th1/th2/thxy APPLICATION: CONDITIONAL` and `current actual artifacts meet
them: NO`, quoting the same line. The promotion to `ESTABLISHED` is done by prose in
`PEIFFER_RIBBON_GEOMETRY_ARBITRATION.md` / `PEIFFER_RIBBON_FINAL_GEOMETRY_AUDIT.md`, which
re-assert hypotheses 1-6 rather than exhibiting the objects.

### H-5 — Horvat-Jablonowski is invoked past its hypotheses

The geometry route replaces t73's **actual** three-handle attaching spheres with a
**chosen synthetic** basis, licensed by one sentence in
`PEIFFER_RIBBON_FINAL_GEOMETRY_AUDIT.md` section 3: *"Horvat--Jablonowski then permits
their use as the 3-handle attaching system up to isotopy, permutation and sphere slides."*

The chain's own source-checked audit,
`agents/hj_scope_hostile/HOSTILE_HJ_TOPOLOGY_AUDIT.md` (which pins HJ v3
`version_23_RM.tex:644-675`, SHA-256 `974CE1C240BFE0E6624817ED5EF45E5F162901AD1BA56D26B509AE59F27CF529`),
lists six hypotheses and rules:

```
OVERALL:                                      NOT PROVED
(3) HJ replacement by actual 3-handles:       NOT PROVED AS INVOKED
(5) old-link-relative conclusion:             NOT PROVED
```

> "The three reviewed memos do not discharge assumptions 1--5. They merely call the
> coordinate triple an 'owner basis' and invoke HJ after computing a determinant. ...
> **The theorem does not mention, and does not preserve, a background old link.**"

Its item (1) (the `det[K1 K2 th2]=189` contradiction) targets the retracted 63-route and
is superseded. Items **(2), (3), (5) are not**: identifying the owner lattice with
`H2^sph(bdry W2)`, HJ's global hypotheses, and relativity to the retained coefficient link
`L_old` (which MWW's setting requires and HJ does not supply). The arbiter never revisits
them.

Grade: the sphere substitution is **UNVERIFIED**. `det D = +1` is a correct conditional
algebra gate whose antecedent (embedded, disjoint, in `H2^sph`, relative to `L_old`) is
not established. Arithmetic recomputed and **PROVED**:
`det[[-1311,-189,41],[8608,1241,-269],[-1,0,1]] = +1`; M2/M3 minor `40*1271 - 189*269 = -1`;
`b1+b2+b3 = 350176+229198+11115 = 590489` (and the `590493` registry figure differs by the
four old `xi` core lanes as claimed).

---

## 3. Seven-point findings

**(1) Terminal implication.** Both MWW anchors quoted accurately.
`kirby.tex:424-425`: *"$i_*$ is a surjection for $k=3$ and an isomorphism for $k=4$."*
`kirby.tex:429-430`: *"We have $\Sz(S^4)\cong \Z$, concentrated in bidegree zero."*
The implication "nonzero homogeneous class in bidegree `(0,494)` => module != `Z` in
bidegree zero => not `S^4`" is **PROVED** as a schema. Coefficients are comparable: MWW's
one-handle theorem is over a field (`1handles.tex:15`: *"Throughout this section we will
work with coefficients in a field $\k$."*), the chain works over `Q`, and `Sz(S^4;Q)=Q` in
bidegree zero. Grading bookkeeping is right: `def:cabled` (`kirby.tex:336`) carries the
shift `{(1-N)(2|r|+|alpha|)}`, which at `N=2, alpha=0, |r|=2` is `-4`, matching
`498 - 4 = 494` — **DERIVED**, conditional on the `(0,498)` one-handle degree, which is
recorded (`degree_in_current_MR: [0,498]`) but which I did not re-derive: **UNVERIFIED**.
The implication is not where the chain breaks.

**(2) Four-handle map + three-handle quotient.** Statement faithful to `eq:P1`/`eq:P2`
(`kirby.tex:729-740`). **PROVED.** Whether the functional satisfies them: see H-3,
**bookkeeping**.

**(3) Full-quotient well-definedness (beta / psi / sphere / changing-endpoint).**
* MWW's relations verbatim, `kirby.tex:341-346` (`eq:sim`):
  `\beta_i(b)v \sim v, \ \ \psi^{[d]}_i(v) \sim 0 \text{ for } d < N-1,\ \ \psi^{[N-1]}_i(v) \sim v`.
  Correctly stated by the chain.
* Base beta group `B_(1,1)`: `base_beta_multiplicity_reaudit.py` reads the physical ledger
  `CUT_OBJECT.json` and verifies `alpha=0`, `r = e_rxy + e_m2`, four physical components,
  gate counts `2` and `42` **per copy**. Given MWW's `k^+- = r -+ alpha^-+`, `B_(1,1)`
  follows. **DERIVED.** The `-28864` retraction is correct: `S2xS2xS42xS42` permuted gate
  passages inside one cable, which is not MWW's `beta_i`.
* But retracting `-28864` does not repair the finding that motivated it.
  `FULL_BETA_BLOCK_COVECTOR_AUDIT.md:62`: `old ell=e87*-e2* as a full beta row: FAIL`.
  `FINAL_CHAIN_HOSTILE_AUDIT_CORRECTED.md:56`: *"The old coordinate row `ell=e87*-e2*` is
  not invariant under all same-orientation permutations."* At the base `r=(1,1)` there is
  nothing to be invariant under — but `eq:sim` identifies the base with level `r+e_i`,
  where the constant quotient is `S2^- x S2^+` (the reaudit's own "Higher levels"
  paragraph concedes this). The base value is therefore pinned by the symmetric level.
  The chain's answer is the pointwise-replication Reynolds row: **DERIVED from the
  transport construction; the transport is defined, not verified against an independent
  computation of the level-`r+e_i` row.** After one `psi` on `m2` the endpoint module is
  `M_43(172)`, dimension `C(172,43)` (about 1e38) — `NOT COMPUTED`, and correctly so; but
  that means nothing beyond the base was ever evaluated.
* `psi0` kill: see the h-order table, item **W5** — **white-given**.
* Changing-endpoint `K_t C_0 = C_0 K_s` (`WEAK_ALL_EDGE_CUBIC_NATURALITY_THEOREM.md`): the
  argument that a labelled pure braid acts as the identity at `q=1` (symmetric monoidal
  `Rep(sl_2)`, braiding = flip) is **sound** and does answer the winding counterexample of
  `HOSTILE_FULL_DOMAIN_DESCENT_AUDIT.md` section 4 at cubic order. **DERIVED.** Credit.
* `ell = e_87^* - e_2^*` is **WRITTEN**. No file derives it. It is called "the
  quotient-valid covector" / "separating covector (annihilates the all-ones line)" — but
  *every* difference of two coordinates annihilates the all-ones line; there are 3828 such
  choices, giving values from `-64` upward. Nonvanishing does not depend on the choice
  (all 88 entries nonzero — confirmed), but *descent* does, and the choice is not derived.

**(4) h-order arguments.** See section 4.

**(5) Geometry.** See H-4, H-5. Arithmetic **PROVED** as listed there. Everything
geometric above the arithmetic is **UNVERIFIED**. `det D = +1` is *computed*, not chosen —
but computed from the signed leaf ledger of the *constructed* spheres, so it inherits
their status.

**(6) `v = eta_R[T1]` and `-59072`.** I recomputed the scalar independently from raw data
(`D:\tmp\r6\AUD_B\recompute.py`): `agents\t73_collar_braid\T73_COLLAR_BRAID.json` ->
`B44_Artin_word` (11,340 letters) -> 2-cabled to 45,360 letters -> 88x88 Burau-type
`(t-1)`-series:

```
deg 0: 0 nonzero entries   deg 1: 0   deg 2: 0   deg 3: 88 nonzero
recomputed deg-3 image vector == recorded epsilon3_vector : True
ell(img3) = img3[87]-img3[2] = 7384        h3 = -8 * 7384 = -59072
```

**PROVED:** first nonzero order is exactly 3 (`Gamma_3`, not `Gamma_4`); the 88-vector is
exactly the recorded one; the `epsilon`/`h` reparametrisation is consistent
(`h3 = -8*eps3` entrywise, all 88 checked); the vector sums to zero; and
`h3[2k]=h3[2k+1]` for all 44 wickets. **The number is genuine and reproducible.** What is
not established is which class it is the value on (H-1).

Structural note: the 44 pair-values are `2592, 32, 96, 160, ..., 2656, -59040` — an
arithmetic progression of step 64 plus one outlier, and the outlier `-59040` is *forced*
by the sum-zero constraint (minus the sum of the rest). `ell` picks exactly that forced
entry against a small one (`32`). So the magnitude of `-59072` is an artifact of the
covector choice, not an invariant; only its **nonvanishing** carries meaning.

**(7) Anchor firewall.** See H-2. Passes vacuously.

---

## 4. The h-order argument table

Every h-order argument in the chain has the same one-line form: *"the error is `I+O(h)`,
it multiplies an `O(h^3)` quantity, therefore it lands in `O(h^4)` and the `h^3`
coefficient is clean."*

| # | Argument | Where | Judgement |
|---|---|---|---|
| W1 | `rho_h(sigma_i^2)-I = O(h)` on the flat-boundary / weight module | `RELATIVE_QLEADING...CERT.json` `uniform_order.pure_generator` | **DERIVED** — standard for a `q=1+h` deformation of a symmetric category |
| W2 | `W in Gamma_3` => `rho_h(W)-I = O(h^3)` | same `.Gamma3`; `relative_leading_trace.py` Magnus cert | **PROVED** — I reproduced degrees 0,1,2 exactly zero, degree 3 nonzero (88/88) |
| W3 | q-trace `Delta(fg)=q^{deg f}Delta(gf)`, `q^{deg}=1+O(h)`, `Delta=O(h^3)` => `delta_3(fg)=delta_3(gf)` | `RELATIVE_QLEADING...RESULT.md` sec 2 | **DERIVED** — algebra is right |
| W4 | membrane/shift ambiguity is `q^k=1+O(h)` => `h^3` coefficient unchanged | same sec 2 | **DERIVED** |
| W5 | `beta` pure kernel `= I+O(h)` => correction from order 4 | same sec 4; `BASE_BETA_MULTIPLICITY_REAUDIT.md` | **DERIVED at the base**; at higher levels the *permutation* part is not `I` and is handled by the Reynolds transport, i.e. by construction |
| W6 | cap standardisation = permutation x pure braid; pure part `I+O(h)` | same sec 4 | **DERIVED**, same caveat |
| W7 | changing-endpoint residual `H_e(h)=I+O(h)` => `K_t C_0 = C_0 K_s` | `WEAK_ALL_EDGE...THEOREM.md` sec 4, 7 | **DERIVED** — the `q=1` symmetric-flip argument is genuinely sound |
| W8 | conjugation by `Q_s(h)=Q_{s,0}+O(h)` changes the cubic only from order 4 | same sec 6 | **DERIVED** |
| W9 | `psi_1` raw degree `+2` cancels the `N=2` level shift `-2` | several | not an h-order argument; a q-degree one. Consistent with `eq:sim` + `def:cabled` shift. **DERIVED** |
| W10 | *"exact full-h cocone: NOT_CLAIMED; mod h4 leading cubic is the scope"* | `V3_FINAL_CANDIDATE_RESULT.md` | scope statement, see section 5 |

Every individual step W1-W9 is defensible. Their **joint** consequence is not disclosed
anywhere in the chain, and it is decisive:

> Since `rho_h(W)-I = h^3 A_3 + O(h^4)`, the `h^3` coefficient of the product is
> `delta_3(v) = ell . A_3 . Phi_0(Sh(v))`, where `Phi_0` is the **h=0, i.e. undeformed,
> classical** shadow.

The entire q-deformed apparatus collapses to: *one hand-chosen covector, composed with one
fixed matrix (the third Magnus derivative of the collar braid), composed with the ordinary
classical decategorified shadow.* Nothing of the deformation survives except `A_3`. In
particular `Phi_0(Sh(eta_R[T0])) = Phi_0(Sh(eta_R[T1]))` — `W` is invisible at `h=0` — so
`delta_3` cannot tell the two apart, and its value is a property of `W` (the
presentation), not of the class.

### W5 is white-given — verified empirically

The `psi_0` kill needs `c_{i,-,p} = c_{i,+,p}`, i.e. the row equal on the
`(negative, positive)` halves of each wicket. The actual row `ell . Delta_3` is
**pairwise-equal in all 44 wickets, 0 mismatches** — and the *whole* `Delta_3` matrix has
column `2k` = column `2k+1` and row `2k` = row `2k+1`.

Controls (`D:\tmp\r6\AUD_B\control_pairwise.py`, `control_pure.py`, `control_gamma3.py`):

```
arbitrary braid words, arbitrary covector    : pairwise-equal FALSE (0/6)
arbitrary PURE braid words                   : pairwise-equal FALSE (0/6)
random Gamma_3 words with nonzero degree-3   : pairwise-equal TRUE  (14/14)
```

=> The `psi_0`-killing structure of the `-59072` row follows from `W in Gamma_3` +
2-cabling — the exact hypothesis the chain independently asserts — and is therefore an
identity of the construction. The witness is the constrained object itself. It is **not**
a t73-specific fact and would hold verbatim for any `Gamma_3` collar braid, including one
attached to a standard presentation. Empirical, 14 samples, `B_8 -> B_16`; I do **not**
claim a proof of the general statement, only that the property is not distinguishing.

---

## 5. Judgement on "mod h^4"

**Honest as a stated scope; concealing as a mechanism.**

Honest: the report says plainly *"exact full-h cocone: NOT_CLAIMED; mod h4 leading cubic
is the scope"*, and the sub-theorems repeat it (`exact finite-h common-P: NOT REQUIRED AND
NOT CLAIMED`; `pure-braid holonomy exactly trivial: NO`). Nobody is hiding the truncation.

Concealing: what is not said is that the truncation is the *reason every relation check
passes*. Each of W3-W8 has the identical shape — the relation's failure is `O(h)`, it
multiplies `O(h^3)`, so at `h^3` it is invisible. **None of those relations is shown to
hold. What is shown is that its failure is below the resolution of the detector.** Being
blind to an obstruction is not the same as the obstruction vanishing.

That distinction matters here specifically, because on the `S^4` side the relations *must*
kill the `q494` class (`kirby.tex:430`), and the only thing preventing this chain's
argument from "proving" a nonzero `q494` class for `S^4` too is that `A_3^{std}=0`. The
chain has an argument whose soundness cannot be tested, and a control that cannot test it.
That is a fundamental problem, and "mod h^4" is where it lives.

---

## 6. Fifth instance of the retraction mechanism

**Common mechanism of the four retractions:**

| # | Retraction | What was swapped |
|---|---|---|
| 1 | `-28864` block-mean Reynolds | index set: gate passages (`2`,`42`) read as physical cable copies; the averaging group rode along |
| 2 | `63-C3` route | the sphere: one construction replaced by another, verdict kept |
| 3 | `Delta_3(xi) != 0` | the carrier: a number computed for one object asserted of another |
| 4 | flat Peiffer geometry | the category: word-level algebra (`corridor_output_interfaces=0`, `GEOMETRY=NOT_CLAIMED`) read as embedded geometry |

Stated once: **a verdict is verified about object/category A; A is then replaced by B
bearing the same name or the same number; the verdict travels with the label, not with the
verification.** What is invariant across all four is a *label* — a scalar, a "PASS"
string, a sphere name. What changes is what the label is about.

**Fifth instance: yes, two of them.**

**(5a) — the load-bearing one, = H-1.** `-59072` was computed as `[h^3] ell (rho_h(W)-I)u`
where, by the chain's own SHA-pinned records, `(rho_h(W)-I)u` **is** the image of `xi`
(`shadow_K0: "[W U1]-[U1]"`; `difference: "(rho_h(W)-I)(e_0-e_5)"`). `xi` was retracted as
the carrier and the number reassigned to `eta_R[T1]` — the summand whose own record reads
`eta_Rw[T1] -> Id_(W W^-1 U1)=Id_U1`, i.e. braid-free and h-constant. The number stayed;
the object it is about was swapped. **Exactly mechanism 3, one level up.**

**(5b) — the compiler-level one, = H-4.** `v3_final_candidate.py:83` greps
`"H0 UNIT MINOR, CONDITIONAL ON THE STATED GEOMETRY:     YES"` out of a file whose next
two lines are `EXISTING RETRACTED TH1/TH2 GEOMETRY ARTIFACT: STILL RETRACTED` and
`CURRENT FILES ALONE ESTABLISH ALL LEMMA HYPOTHESES: NO`. The `YES` label travels; the
condition does not. **Exactly mechanism 4.**

Both are instances of the disease the four retractions were symptoms of, and neither was
caught by `FINAL_CLEAN_Q494_CHAIN_HOSTILE_AUDIT.md`, written by the same executor.

Why it keeps happening: `v3_final_candidate.py` is not a proof checker. It is a
**string-grep aggregator**. Its 12/12 test suite (which I ran — passes) asserts that a
dict literal in the source file has the values written in that same source file; its only
external contact is `assert "<verdict string>" in <markdown>`. It cannot detect a
conditional promoted to unconditional, a number re-carried to a new object, or a retracted
premise. Its `12/12 OK` is evidence about string constants and nothing else.

---

## 7. Anchor firewall verdict

```text
ANCHOR FIREWALL: PASSES VACUOUSLY — NO DISCRIMINATING POWER
```

Zero because `B_{R_std}=I` makes the relative operator identically zero **before** beta,
psi, z caps, sphere maps and the three-handle quotient
(`ACTUAL_STANDARD_CONTROL_RESULT.md` section 7). The reason is structural, not
coincidental — but it is the *wrong* structure: `W_std = I`, i.e. the functional itself is
the zero functional on that branch. A firewall that returns `0` because the probe is `0`
cannot detect a descent argument that wrongly claims to descend, since `0` descends under
any relations whatsoever.

The correct control is the one named by the chain's own earlier file
(`MIXED_RELATIONS_RESULT.md:143`): a nonzero class killed by **ANCHOR-537's own sphere
maps**. `NOT COMPUTED` — the ANCHOR sphere matrices do not exist in the corpus.

---

## 8. Self-check gate log

* **Construction self-check** — triggered 3x:
  * W5 / `psi_0` kill: true by construction from `Gamma_3` + 2-cabling; empirically confirmed non-distinguishing (14/14 controls). Downgraded to bookkeeping.
  * H-3 three-handle `f(D)=f`, `f(U)=0`: satisfied because `rho_t` is *defined* by the row that inverts `D` and kills `U`; the witness is the transport itself. Downgraded to bookkeeping.
  * H-2 anchor `= 0`: white-given by `W_std - I = 0`; the witness is the constrained object. Downgraded to bookkeeping.
* **Universal-claim gate**: my `Gamma_3` pairwise-equality control is 14 non-vacuous samples at `B_8 -> B_16`. That is a **sample**, not a proof; I claim only "not distinguishing", never "holds for all `Gamma_3`".
* **"I did not find" discipline**: every negative is scoped. I searched `D:\tmp\r6\agents\**` (`*.md`, `*.py`, `*.json`) for (i) an evaluation of the functional on a single `eta_R[T_i]`, (ii) a numeric three-handle relation check for the `-59072` row, (iii) ANCHOR sphere maps. Found none in that scope; the missing objects are named in H-1, H-3, H-2.
* **Mid-run counting**: all computations ran to completion; no intermediate counts reported.
* **"Can't compute" attribution**: the two things I could not compute are the level-`r+e_i` row (`M_43(172)`, dimension `C(172,43)`) and the ANCHOR sphere maps (absent from the corpus). Both marked `NOT COMPUTED` with reason and scale.
* **External citations**: every MWW / BHPW quote here is `file:line` + verbatim, from `D:\tmp\qstar3_review\NOKILL\mww_src\` and `D:\tmp\r6\agents\finite_type_leading\bphw_1903_src\`. I did not quote Horvat-Jablonowski myself; I quoted the chain's audit of it, which pins the source with a SHA.
* **No new sealed artifacts; no candidate-table / radius / `Dmax` expansion.**

## Files I produced

```
D:\tmp\r6\AUD_B\AUD_B_REPORT.md        this report
D:\tmp\r6\AUD_B\recompute.py           independent recomputation of -59072 from the raw braid word
D:\tmp\r6\AUD_B\control_pairwise.py    control: pairwise equality for arbitrary words
D:\tmp\r6\AUD_B\control_pure.py        control: pairwise equality for pure braids
D:\tmp\r6\AUD_B\control_gamma3.py      control: pairwise equality for Gamma_3 braids
```
