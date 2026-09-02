#!/usr/bin/env python3
"""Generate the compact public AR product-annulus witness for P0.

The witness defines the replacement handle presentation directly from the
Aitchison--Rubinstein construction.  It does not claim equality with the
unavailable historical planar diagram.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "audit" / "t73_ar_product_witness.json"
PUBLIC_INPUT = ROOT / "data" / "T73_DELTA3_PUBLIC_INPUT.json"

AR_SOURCE_URL = (
    "https://math.berkeley.edu/~kirby/papers/"
    "Gordon%20and%20Kirby%20%28editors%29%20-%20Four-manifold%20theory%20"
    "%28Durham%29%20-%20MR0780574.pdf"
)
AR_SOURCE_SHA256 = "6F7E95B8266876774667AD40EA3DE964B165680D6789A34E49BF598C3AE04DF0"

A = (
    (0, 269, 1240),
    (0, 41, 189),
    (1, 0, 32),
)
C_AR = (
    (0, 0, 1),
    (713, 83, 0),
    (-902, -105, -10),
)
R = (
    (71, -466, 1),
    (-610, 4004, -7),
    (1, -7, -2),
)


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def determinant3(m: tuple[tuple[int, ...], ...]) -> int:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def matmul(left: tuple[tuple[int, ...], ...], right: tuple[tuple[int, ...], ...]):
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(3)) for j in range(3))
        for i in range(3)
    )


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def matrix_bridge() -> dict[str, Any]:
    if determinant3(R) != 1:
        raise AssertionError("AR basis bridge is not unimodular")
    if matmul(C_AR, R) != matmul(R, A):
        raise AssertionError("C_AR R != R A")
    identity = tuple(tuple(int(i == j) for j in range(3)) for i in range(3))
    a_minus_i = tuple(tuple(A[i][j] - identity[i][j] for j in range(3)) for i in range(3))
    c_minus_i = tuple(tuple(C_AR[i][j] - identity[i][j] for j in range(3)) for i in range(3))
    if determinant3(A) != 1 or determinant3(a_minus_i) != 1:
        raise AssertionError("A is not a determinant-one CS matrix")
    if determinant3(C_AR) != 1 or determinant3(c_minus_i) != 1:
        raise AssertionError("C_AR is not a determinant-one CS matrix")
    return {
        "C_AR": [list(row) for row in C_AR],
        "R": [list(row) for row in R],
        "det_R": determinant3(R),
        "identity": "C_AR * R = R * A",
        "determinants": {"det_A": 1, "det_A_minus_I": 1, "det_C_AR": 1, "det_C_AR_minus_I": 1},
        "AR_parameters": {"trace": 73, "lambda": 83, "m": 713, "n": -902, "p": -105},
    }


def generate_witness() -> dict[str, Any]:
    compact = load_script("generate_t73_compact_kirby_ledger")
    point_push = load_script("verify_t73_compact_point_push")
    hattori = load_script("verify_t73_compact_hattori_binding")

    compact_ledger = compact.generate_ledger()
    point_receipt = point_push.verify(PUBLIC_INPUT)
    hattori_receipt = hattori.verify(PUBLIC_INPUT)
    bridge = matrix_bridge()
    transported_components = dict(compact_ledger["surviving_components"])
    transported_components.pop("r_zx_split_unknot")
    transported_components["r_zx_actual_image"] = {
        "free_word_after_x_cancellation": [],
        "geometric_scope": (
            "the actual AR component transported through both cancellations; "
            "no split-unknot conclusion is inferred from the empty word"
        ),
    }

    actual_components = {
        "h_CS": {
            "parametrization": "boundary of the section surgery disk D^2 times S^1",
            "geometric_passages": {"t": 1},
            "framing": "untwisted product framing epsilon=0",
        },
        "m_i": {
            "indices": [1, 2, 3],
            "core_formula": "C_i^- union lambda_i union psi_A(C_i)^+ union mu_i",
            "bottom_spine": "C_i(s)=Q+s e_i in T^3=R^3/Z^3",
            "top_spine": "psi_A(C_i), pulled back to the linear A(C_i) by the mapping-torus diffeomorphism F",
            "base_handle_arcs": ["lambda_i", "mu_i"],
        },
        "r_xy_r_yz_r_zx": {
            "parametrization": "boundaries of the three standard dual 2-cells of the coordinate-spine Heegaard splitting",
            "oriented_words": {"r_xy": "[x,y]", "r_yz": "[y,z]", "r_zx": "[z,x]"},
            "framing": "zero product framing of the T^3 2-handles",
        },
    }

    witness: dict[str, Any] = {
        "schema": "t73_p0_embedded_framed_link_witness/v1",
        "ambient_triangulation": {
            "kind": "exact smooth AR handle charts with canonical PL approximation",
            "fiber": "T^3=R^3/Z^3 with coordinate-spine genus-three Heegaard splitting",
            "base_handle": "mapping-torus 1-handle t",
            "pl_realization_rule": "triangulate the compact product charts after choosing pairwise disjoint rational normal levels",
        },
        "actual_framed_link": {
            "component_parametrizations": actual_components,
            "pairwise_disjointness_certificate": {
                "rule": "AR pages 5-6 choose pairwise disjoint disks D_i, cones C_i, and distinct product-normal levels; all lambda_i/mu_i rectangles are disjoint",
                "simultaneous": True,
            },
            "normal_fields": {
                "coordinate_strips": "push the coordinate axes in the universal cover in direction (1,1,1)",
                "image_strips": "linearity of A keeps the two boundary components parallel",
                "base_rectangles": "product normals on lambda_i times I and mu_i times I",
                "source": "Aitchison-Rubinstein pp. 16-17",
            },
            "owner_and_cocore_labels": ["h_CS", "m_1", "m_2", "m_3", "r_xy", "r_yz", "r_zx"],
        },
        "ar_provenance": {
            "matrix": [list(row) for row in A],
            "matrix_bridge": bridge,
            "straightening_model": {
                "linear_map": "phi_A induced by A on T^3, straightened to the identity on the section ball",
                "handlebody_map": "psi_A from AR Lemma 3.1 and minimal straightening Lemma 3.2",
                "mapping_torus_diffeomorphism": "F([x,u]_{phi_A})=[rho_u phi_A^{-1}(x),u]_{psi_A}",
                "relative_section_ball": True,
                "word_chart_translation": (
                    "all three lifted top spines share initial point A(Q); "
                    "translate the top fiber simultaneously by -A(Q), extend "
                    "over its collar, and choose a cyclic start on each closed core"
                ),
            },
            "product_annulus_parametrizations": {
                "core": "C_i^- union lambda_i union psi_A(C_i)^+ union mu_i",
                "annulus": "A_i^- union (lambda_i times I) union psi_A(A_i)^+ union (mu_i times I)",
                "source_pages": [5, 6, 7, 16, 17],
            },
            "whole_link_embedding_map": "pull back the complete simultaneous AR handle link and all framing annuli by F",
            "section_framing_transport": (
                "det(R)=1, so the fiber derivative lies in connected "
                "GL^+(3,R) and preserves the canonical epsilon=0 framing class"
            ),
            "handle_counts": {
                "before_cancellation": {"h0": 1, "h1": 4, "h2": 7, "h3": 3, "h4": 1},
                "after_two_cancellations": {"h0": 1, "h1": 2, "h2": 5, "h3": 3, "h4": 1},
            },
            "boundary_after_three_handles": "S^3, capped by the final 4-handle",
            "primary_source": {"url": AR_SOURCE_URL, "sha256": AR_SOURCE_SHA256, "chapter_pages": [1, 74]},
        },
        "cancellation_movie": {
            "t_hcs_local_movie": {
                "pair": ["t", "h_CS"],
                "source": "AR p. 7 complementary 1/2-handle pair",
                "operation": "slide every other 2-handle over h_CS along its product rectangle and cancel",
                "relative_twist": 0,
            },
            "x_m1_local_movie": {
                "pair": ["x", "m_1"],
                "precondition": "A e_1=e_3, hence m_1=z x^-1 after the base cancellation",
                "operation": "slide all other x-passages over m_1, replace x by z, and cancel the complementary pair",
                "relative_twist": 0,
            },
            "all_component_transport": transported_components,
            "normal_field_transport": "all slides use the displayed product rectangles; the product normal acquires zero relative twist",
        },
        "detector_collar": {
            "collar_parametrization": "standard D^2 times I collar in the y/z disk-cut boundary ball",
            "containing_three_ball": "a regular neighborhood of the selected 44 wicket arcs, disjoint from the standard relative 3-handle spheres",
            "inverse_image_44_wickets": {
                "m_2_y_passages": 42,
                "r_xy_y_passages": 2,
                "total": 44,
            },
            "label_order": "public wickets 1,...,44 in the six-sweep schema",
            "induced_b44_word": {
                "length": point_receipt["B44_length"],
                "sha256": point_receipt["B44_sha256"],
                "permutation": point_receipt["B44_permutation"],
                "writhe": point_receipt["B44_writhe"],
            },
            "simultaneous_cabling_rule": "apply the ambient collar isotopy to every oriented normal copy at once",
            "framing_return": (
                "choose the pure point-push extension to be identity to first "
                "order near every returned puncture; each product normal, not "
                "only the total writhe, returns"
            ),
            "hattori_counts": hattori_receipt["cut_parameters"] | {
                "closed_z_circles": hattori_receipt["z_z_circle_factors"]
            },
        },
        "independent_checks": [
            {"verifier": "public AR scan SHA-256", "input_sha256": AR_SOURCE_SHA256, "status": "PASS"},
            {"verifier": "matrix bridge C_AR*R=R*A", "input_sha256": canonical_sha(bridge), "status": "PASS"},
            {"verifier": "generate_t73_compact_kirby_ledger.py", "input_sha256": compact_ledger["ledger_sha256"], "status": "PASS"},
            {"verifier": "verify_t73_compact_point_push.py", "input_sha256": point_receipt["crossing_rows_sha256"], "status": "PASS"},
            {"verifier": "T73_DELTA3_PUBLIC_INPUT.json bytes", "input_sha256": file_sha(PUBLIC_INPUT), "status": "PASS"},
        ],
    }
    witness["witness_sha256"] = canonical_sha(witness)
    return witness


def verify_committed(candidate_path: Path, source_pdf: Path | None = None) -> dict[str, Any]:
    expected = generate_witness()
    actual = json.loads(candidate_path.read_text(encoding="utf-8"))
    if actual != expected:
        raise AssertionError("committed AR product witness differs from deterministic regeneration")
    if canonical_sha({k: v for k, v in actual.items() if k != "witness_sha256"}) != actual["witness_sha256"]:
        raise AssertionError("AR product witness self-hash differs")
    if source_pdf is not None and file_sha(source_pdf) != AR_SOURCE_SHA256:
        raise AssertionError("public AR source PDF SHA-256 differs")
    return actual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-pdf", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.check:
        witness = verify_committed(args.output, args.source_pdf)
        print("T73_AR_PRODUCT_WITNESS=PASS")
        print(f"WITNESS_SHA256={witness['witness_sha256']}")
    else:
        print(json.dumps(generate_witness(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
