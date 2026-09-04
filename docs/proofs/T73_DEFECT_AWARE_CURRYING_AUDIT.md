# Defect-aware C-H1 currying audit

Date: 2026-09-05

## Incidence classification

The source coefficient exterior contains 176 intervals incident to a y
insertion sphere. Of these, 168 already have the two-representable
opposite-side type. The remaining eight form four pairs:

| pair | old \(Y_--Z_-\) interval | old \(Y_+-Z_+\) interval |
|---|---|---|
| \(m_2\), negative cable | m_2:negative:interval:310 | m_2:negative:interval:0 |
| \(m_2\), positive cable | m_2:positive:interval:310 | m_2:positive:interval:309 |
| \(r_{xy}\), negative cable | r_xy:negative:interval:3 | r_xy:negative:interval:1 |
| \(r_{xy}\), positive cable | r_xy:positive:interval:3 | r_xy:positive:interval:1 |

For each row, audit/t73_defect_aware_currying.json records the four exact
endpoint IDs and the crosswise re-pairing which sends them to
\(Y_--Z_+\) and \(Y_+-Z_-\).

The eight intervals arise from two negative base y passages,
\[
m_2:C_i,\qquad r_{xy}:\mathrm{vertex}:1,
\]
each with two cable copies and two incident sides.

## Why these are not four verified cup/cap cells

A pivotal mate moves a boundary object from one side of a Hom to the other
and replaces it by its dual. It does not change endpoint matching while all
four insertion-sphere boundaries are fixed. The four crosswise pairings do
change that matching. Relative to the current boxes, they require a band
reconnection, not merely a choice of BPW evaluation or coevaluation.

A saddle can change matching but is not invertible. A merge--split pair can
return component count, but is not a pivotal equivalence and has nonzero
Euler contribution. Without explicit cells, one cannot determine the
left/right mate, ordered BPW A.6 term, Blanchet sign, number of saddles,
Euler characteristic, or quantum degree. The artifact records these fields
as UNDETERMINED.

## No reduction from eight intervals to one defect

Pivotal currying preserves the total number of active boundary endpoints,
which is 176. A tangle \(P_{86}\to P_{88}\) has 174 boundary endpoints.
Hence the four pairs cannot produce that single-Hom type.

The one-defect weight space instead comes from the external cup
\[
E_{86}\longrightarrow E_{88}
\]
after oriented doubling. geometry/t73_single_hom_defect_target.json defines
that auxiliary target but correctly leaves source_to_target_interval_map and
z_coend_gluing_cells empty.

Pure pivotal mates have normalized degree zero and cannot supply the missing
\(+271\) in the old degree-494 ledger. A true reconnection requires a surface
movie; for \(N=2\) its raw degree is \(-\chi\). Since its critical cells are
absent, its strict degree remains open.

Machine verdict:

    NO_SINGLE_DEFECT_CURRYING_FROM_CURRENT_INCIDENCE
    ACTIVE=176
    WRONG_SIDE=8
    RECONNECTIONS=4

This closes the finite incidence classification but not the coend/currying
map or its grading.
