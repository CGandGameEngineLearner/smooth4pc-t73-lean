# -*- coding: utf-8 -*-
"""Cappell-Shaneson mapping-torus handle presentation builder (word level).

Construction: [G10 section 2] (Gompf 2010, "More Cappell-Shaneson spheres are
standard"), exactly as certified word-level by the second party (P2S
cs_compiler.py stage2; word conventions cross-checked against their frozen
run JSON in anchors/anchor_A_word_family.py):

  W = punctured Sigma_A^eps:
    0-handle;  1-handles x, y, z (fiber), t (base);
    2-handles r_xy=[x,y], r_yz=[y,z], r_zx=[z,x]   (fiber, framing 0 conv.),
              m_i = t * phi(x_i) * t^-1 * x_i^-1   (monodromy, fiber-band),
              h_CS: word "t"                        (eps rel section framing);
    3 three-handles (DECLARED; fiber 2-handles x base 1-handle);  no 4-handle.

  phi(x_j) = x^{A[0][j]} y^{A[1][j]} z^{A[2][j]} in canonical power order;
  canonical order = true attaching word only when all exponents <= 1
  (interleaving caveat = gap G-a; embedding_status records it).
"""
from .object_model import MasterObject


def build_X(c, d, n):
    """X_{c,d,n} = [[0,a,b],[0,c,d],[1,0,n-c]], b=(c-1)(n-c-1), a=-f_n(c)/d."""
    b = (c - 1) * (n - c - 1)
    num = -(c ** 3 - n * c ** 2 + (n - 1) * c - 1)
    assert num % d == 0, "d must divide f_n(c)"
    return [[0, num // d, b], [0, c, d], [1, 0, n - c]]


def col_pairs(A, j, names=("x", "y", "z")):
    return [[names[i], A[i][j]] for i in range(3) if A[i][j] != 0]


def cs_master_object(c, d, n, eps, object_id=None, markers="cocore_set"):
    A = build_X(c, d, n)
    o = MasterObject(object_id or "CS_X(%d,%d,%d)_eps%d" % (c, d, n, eps),
                     provenance={"construction": "G10-sec2 mapping torus",
                                 "A": A, "c": c, "d": d, "n": n, "eps": eps,
                                 "word_convention": "canonical power order (P2S stage2)"})
    for g in ("x", "y", "z", "t"):
        o.add_h1(g)
    o.add_h2("r_xy", [["x", 1], ["y", 1], ["x", -1], ["y", -1]],
             {"kind": "fiber_convention_0", "value": 0, "basis": "[GS] T^3 fiber convention"},
             embedding_status="PROVEN", status="CONVENTION")
    o.add_h2("r_yz", [["y", 1], ["z", 1], ["y", -1], ["z", -1]],
             {"kind": "fiber_convention_0", "value": 0, "basis": "[GS] T^3 fiber convention"},
             embedding_status="PROVEN", status="CONVENTION")
    o.add_h2("r_zx", [["z", 1], ["x", 1], ["z", -1], ["x", -1]],
             {"kind": "fiber_convention_0", "value": 0, "basis": "[GS] T^3 fiber convention"},
             embedding_status="PROVEN", status="CONVENTION")
    names = ["x", "y", "z"]
    for j in range(3):
        word = [["t", 1]] + col_pairs(A, j) + [["t", -1], [names[j], -1]]
        big = any(abs(k) > 1 for _g, k in col_pairs(A, j))
        o.add_h2("m_%d" % (j + 1), word,
                 {"kind": "fiber_band", "value": None,
                  "basis": "graph-annulus of phi over base interval"},
                 embedding_status=("UNCERTIFIED" if big else "PROVEN"),
                 status=("WORD CANONICAL; embedding UNCERTIFIED (G-a)" if big
                         else "PROVEN"))
    o.add_h2("h_CS", [["t", 1]],
             {"kind": "eps_rel_section", "value": eps,
              "basis": "[G10 Def 4.1] eps rel canonical section framing"},
             embedding_status="PROVEN", status="PROVEN/DEFINITIONAL")
    for k in range(3):
        o.add_h3("th_%d" % (k + 1), "DECLARED",
                 provenance="fiber 2-handles x base 1-handle", status="PROVEN (count)")
    if markers == "cocore_set":
        for h in ("h_CS", "m_1", "m_2", "m_3"):
            o.add_marker("mu(%s)" % h, "COCORE_MERIDIAN", of_handle=h, word=(),
                         encircles=[{"handle": h, "strand": "ATTACHING_CIRCLE", "mult": 1}])
    o.boundary_map = {"target": "S3",
                      "status": "ABSTRACT_DIFFEO_PROVEN",
                      "witness": "P2S Lemma B1 (standard-ball removal; no Perelman)",
                      "puncture": "standard ball in 0-handle interior (OBJECT_FREEZE)"}
    o.epsilon_branch = {"epsilon": eps, "status": "BOUND",
                        "twist_deposit_rule": "[G10 Def 4.1]: eps=0 none; eps=1 one full twist on rerouted bundle at (t,h_CS) cancellation"}
    o.vacuity_check = {"checked": True, "verdict": "NON_VACUOUS_APRIORI",
                       "basis": "OBJECT_FREEZE clause 2: surviving-cocore meridians are outside the removed ball; literal h_CS-belt objects are excluded by Theorem V"}
    o.freeze_initial()
    return o
