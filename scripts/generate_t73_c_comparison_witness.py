#!/usr/bin/env python3
"""Generate the candidate coefficient-comparison witness for theorem C."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_INPUT = ROOT / "data" / "T73_DELTA3_PUBLIC_INPUT.json"
RECEIPT = ROOT / "data" / "T73_DELTA3_PUBLIC_RECEIPT.json"
P0_WITNESS = ROOT / "audit" / "t73_p0_johnson_certificate.json"
DEFAULT_OUTPUT = ROOT / "audit" / "t73_c_comparison_witness.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pair_y_to_next_z(owner: str, word: list[str]) -> dict[str, Any]:
    pairings: list[dict[str, Any]] = []
    used_z: set[int] = set()
    for index, letter in enumerate(word):
        if letter.lower() != "y":
            continue
        z_index = (index + 1) % len(word)
        z_letter = word[z_index]
        if z_letter.lower() != "z":
            raise AssertionError(f"{owner}: y event {index} is not followed by z")
        if z_index in used_z:
            raise AssertionError(f"{owner}: z event {z_index} is paired twice")
        used_z.add(z_index)
        pairings.append(
            {
                "owner": owner,
                "y_index": index,
                "y_letter": letter,
                "z_index": z_index,
                "z_letter": z_letter,
                "subrectangle": "closed interval on the owner product annulus from this y side to the next z side",
            }
        )
    z_indices = {i for i, letter in enumerate(word) if letter.lower() == "z"}
    return {
        "word_length": len(word),
        "word_sha256": canonical_sha(word),
        "pairings": pairings,
        "pair_count": len(pairings),
        "unpaired_z_indices": sorted(z_indices - used_z),
        "unpaired_z_count": len(z_indices - used_z),
        "disjointness_rule": "each pairing interval is one cyclic word edge and distinct pairs use distinct endpoints",
    }


def endpoint_sign_table(recompute, data: dict[str, Any]) -> dict[str, int]:
    b44, _ = recompute.build_oriented_b44(data)
    b88 = recompute.cable_word(b44)
    degree = data["endpoint_model"]["truncation_degree"]
    dimension = data["endpoint_model"]["dimension"]
    result: dict[str, int] = {}
    for cup5 in (1, -1):
        for cap2 in (1, -1):
            vector = recompute.sparse_vector(dimension, degree, [[0, 1], [5, cup5]])
            epsilon_scalar = recompute.apply_covector(
                recompute.delta_apply(b88, vector), [[87, 1], [2, cap2]]
            )
            h_scalar = recompute.substitute_epsilon_with_h(epsilon_scalar, degree)
            value = h_scalar[3]
            if value == 0:
                raise AssertionError("an endpoint sign convention kills the cubic")
            result[f"cup5_{cup5:+d}_cap2_{cap2:+d}"] = value
    return result


def generate_witness() -> dict[str, Any]:
    compact = load_script("generate_t73_compact_kirby_ledger")
    point_push = load_script("verify_t73_compact_point_push")
    p0 = json.loads(P0_WITNESS.read_text(encoding="utf-8"))
    johnson = load_script("search_t73_johnson_alpha_sides").generate()["known_candidate"]
    comparison = load_script("compare_t73_nielsen_passages")
    integer_to_letter = {1: "x", 2: "y", 3: "z", -1: "X", -2: "Y", -3: "Z"}
    m2_word = [integer_to_letter[value] for value in johnson["m2_after_cancellation"]]
    m3_word = [
        integer_to_letter[value]
        for value in comparison.after_x_cancellation(johnson["generator_images"][2], 2)
    ]
    if m2_word != compact.after_x_cancellation(1):
        raise AssertionError("Johnson m2 is not the compact selected word")
    rxy_word = ["z", "y", "Z", "Y"]
    ryz_word = ["y", "z", "Y", "Z"]
    rzx_word: list[str] = []
    m2_pairing = pair_y_to_next_z("m_2", m2_word)
    rxy_pairing = pair_y_to_next_z("r_xy", rxy_word)
    if m2_pairing["pair_count"] != 42 or rxy_pairing["pair_count"] != 2:
        raise AssertionError("balanced y pairing count differs")
    if m2_pairing["unpaired_z_count"] + rxy_pairing["unpaired_z_count"] != 227:
        raise AssertionError("closed z circle count differs")

    point_receipt = point_push.verify(PUBLIC_INPUT)
    frozen = json.loads(RECEIPT.read_text(encoding="utf-8"))["results"]["delta3_eta_R_T1"]
    if frozen != 2624:
        raise AssertionError("frozen public cubic is not Lean's computedCubic 2624")

    witness: dict[str, Any] = {
        "schema": "t73_candidate_c_comparison_witness/v2",
        "C_status": "OPEN",
        "C1_status": "OPEN",
        "C2_status": "OPEN",
        "p0_witness_sha256": p0["certificate_sha256"],
        "product_pairing": {
            "m_2": m2_pairing,
            "r_xy": rxy_pairing,
            "total_yz_rectangles": 44,
            "remaining_z_circles": 227,
            "geometric_realization": (
                "OPEN: pair_y_to_next_z is a cyclic-word pairing. It is not an "
                "isotopy of the actual cut link and does not exhibit 44 product "
                "rectangles in P0c annuli."
            ),
        },
        "coefficient_bimodule_equivalence": {
            "status": "OPEN: MWW Theorem 4.7 is not instantiated; counts 44 and 227 are not the map",
            "source": "M_R(T,T')=KhR_2(R union T' union mirror(T)) with the MWW shift",
            "target": "Hom(F T,F T'){-44} tensor A^tensor227",
            "F": "OPEN: no framed west-to-east tangle of 44 product rectangles",
            "dual_boundary": "OPEN: no dual annulus from an actual cut-link isotopy",
            "left_action_square": "OPEN: paper diagram (17) left square is not certified",
            "right_action_square": "OPEN: paper diagram (17) right square is not certified",
            "proof_rule": "isotopy invariance, pivotal tangle duality, disjoint-union Kunneth over Q, and associativity of gluing, after the isotopy exists",
            "ordinary_representable_reduction": "Smooth4PC/RepresentableCoefficient.lean checks the abstract quotient after the maps exist",
        },
        "selected_class": {
            "object": "T_1=F^-1 U",
            "coefficient_representative": "H^-1(Id_U tensor X^tensor227)",
            "circle_evaluation": "epsilon(X)^227=1",
            "absolute_degree": 494,
            "degree_ledger": "-44+227+315-4=494",
        },
        "quantum_trace_and_completion": {
            "base_ring": "R_q=Q[q,q^-1]",
            "quantum_relation": "L_f(m)=q^degree(f) R_f(m)",
            "specialization": "q=1 gives ordinary coefficient HH0",
            "completion_map": "q maps to 1+h in Q[[h]]",
            "flatness": "localization followed by completion of a Noetherian local ring is flat",
            "circle_counit": "epsilon^tensor227 is a homogeneous coefficient-bimodule morphism",
            "vertical_horizontal_map": "BPW canonical qvTr-to-qhTr functor",
            "endpoint_functor": "BHPW strict tangle/foam functor followed by the flat-base qHH0/Chern isomorphism",
        },
        "endpoint_coordinates": {
            "E86": "weight-86 subspace of V^tensor86, rank one",
            "E88": "weight-86 subspace of V^tensor88, rank 88",
            "label_order": "P0 collar order doubled by the public cabling rule",
            "cup_constant_terms": "e_0 plus-or-minus e_5",
            "cap_constant_terms": "e_87^* plus-or-minus e_2^*",
            "sign_robust_cubic_values": {
                "status": "NOT_USED_AS_FROZEN_CUBIC",
                "historical_mixed_index_note": (
                    "cup/cap variants at indices 0,5 and 87,2 mixed two endpoint "
                    "tables; they are not D3=2624"
                ),
            },
            "mixed_index_variants_are_not_the_frozen_cubic": True,
            "public_normalization": {"source": "T73_DELTA3_PUBLIC_RECEIPT.json", "delta3": frozen},
            "B44_sha256": point_receipt["B44_sha256"],
        },
        "two_handle_naturality": {
            "statewise_W": "apply the same P0 collar isotopy simultaneously to every physical cable copy",
            "beta_movie": (
                "transport a physical-copy braid through the statewise point-push; "
                "the conjugate braid cancels against the identically braided core-disk closure"
            ),
            "psi_undotted": "the added opposite pair closes with the core counit and epsilon(1)=0",
            "psi_dotted": "the once-dotted added pair closes with epsilon(X)=1 and reproduces the source row",
            "whole_source": True,
            "strict_sign_control": "BHPW strict functoriality",
            "owner_y_passage_counts": {
                "m_2": sum(letter.lower() == "y" for letter in m2_word),
                "m_3": sum(letter.lower() == "y" for letter in m3_word),
                "r_xy": sum(letter.lower() == "y" for letter in rxy_word),
                "r_yz": sum(letter.lower() == "y" for letter in ryz_word),
                "r_zx": sum(letter.lower() == "y" for letter in rzx_word),
            },
            "owner_z_passage_counts": {
                "m_2": sum(letter.lower() == "z" for letter in m2_word),
                "m_3": sum(letter.lower() == "z" for letter in m3_word),
                "r_xy": sum(letter.lower() == "z" for letter in rxy_word),
                "r_yz": sum(letter.lower() == "z" for letter in ryz_word),
                "r_zx": sum(letter.lower() == "z" for letter in rzx_word),
            },
            "state_formula": (
                "for r=(r_i), p_y(r)=sum_i r_i n_y(i) and "
                "p_z(r)=sum_i r_i n_z(i); choose injections of the base "
                "m_2 and r_xy copy-pairs and average over their finite orbit"
            ),
            "local_psi_frobenius_checks": {
                "epsilon_tensor_epsilon_delta_1": 0,
                "epsilon_tensor_epsilon_delta_X": 1,
                "r_zx_split_circle_epsilon_1": 0,
                "r_zx_split_circle_epsilon_X": 1,
            },
            "through_degree_firewall": (
                "a balanced pair on every positive-gate owner adds at least "
                "four y endpoints/two cups, so the action-closed undotted image "
                "has through degree <=84; r_zx is the unique zero-gate owner"
            ),
            "placement_orbit_size": (
                "product over active owners of binomial(k_i^-,a_i^-) "
                "times binomial(k_i^+,a_i^+)"
            ),
            "orbit_normalization": (
                "divide by the nonzero rational orbit size; beta reindexes the "
                "sum and successive psi extension ratios telescope"
            ),
        },
        "divided_detector": {
            "formula": "D_h=cap_h (rho_h(W)-I) Sh_h",
            "uniform_order": "rho_h(W)-I lies in h^3 End(E88) on all 7744 entries",
            "division": "Q[[h]] is a domain, so D_h/h^3 is unique and regular",
            "ordinary_functional": "reduce D_h/h^3 modulo h after q=1 specialization",
            "selected_nonzero": True,
        },
    }
    witness["witness_sha256"] = canonical_sha(witness)
    return witness


def verify_committed(path: Path) -> dict[str, Any]:
    expected = generate_witness()
    actual = json.loads(path.read_text(encoding="utf-8"))
    if actual != expected:
        raise AssertionError("committed C witness differs from deterministic regeneration")
    if canonical_sha({k: v for k, v in actual.items() if k != "witness_sha256"}) != actual["witness_sha256"]:
        raise AssertionError("C witness self-hash differs")
    return actual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        witness = generate_witness()
        args.output.write_text(json.dumps(witness, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE={args.output}")
        print(f"WITNESS_SHA256={witness['witness_sha256']}")
    elif args.check:
        witness = verify_committed(args.output)
        print("T73_C_COMPARISON_WITNESS=OPEN")
        print(f"C_STATUS={witness['C_status']}")
        print(f"WITNESS_SHA256={witness['witness_sha256']}")
    else:
        print(json.dumps(generate_witness(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
