#!/usr/bin/env python3
"""Fail-closed gate for an actual defect-aware C_271 coend comparison.

The committed typing graph is useful evidence but is intentionally OPEN.
This gate accepts neither status strings nor endpoint counts as a comparison
proof.  A future witness must bind every saved endpoint/interval, exhibit a
finite rational chain equivalence and its naturality homotopies, account for
the grading, and carry a separately checked no-placeholder Lean receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "geometry" / "t73_c_defect_coend_typing_graph.json"
WITNESS = ROOT / "geometry" / "t73_c_defect_coend_witness.json"
SCHEMA = ROOT / "data" / "T73_C_DEFECT_COEND_WITNESS.schema.json"
REQUIRED_THEOREMS = [
    "T73.DefectAwareCoend.selectedSourcePresentation_complete",
    "T73.DefectAwareCoend.comparison_chainEquivalence",
    "T73.DefectAwareCoend.comparison_zBalanced",
    "T73.DefectAwareCoend.comparison_leftNatural",
    "T73.DefectAwareCoend.comparison_rightNatural",
    "T73.DefectAwareCoend.comparison_homogeneous",
]
ALLOWED_LEAN_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


class CoendWitnessError(ValueError):
    pass


def fail(message: str) -> None:
    raise CoendWitnessError(message)


def content_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_builder():
    path = ROOT / "scripts" / "build_t73_c_defect_coend_typing_graph.py"
    spec = importlib.util.spec_from_file_location("t73_defect_graph", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_fields(raw: Any, fields: list[str], where: str) -> None:
    if not isinstance(raw, dict):
        fail(f"{where} is not an object")
    missing = [field for field in fields if field not in raw]
    if missing:
        fail(f"{where} missing fields: {', '.join(missing)}")


def validate_graph(graph: dict[str, Any]) -> None:
    built = load_builder().build()
    if graph != built:
        fail("committed defect coend typing graph is stale")
    if graph["completion_status"] != "OPEN":
        fail("typing graph must not self-promote to a completed coend proof")
    nodes = graph["endpoint_nodes"]
    edges = graph["interval_edges"]
    if len(nodes) != 1260 or len({item["endpoint_id"] for item in nodes}) != 1260:
        fail("typing graph does not bind 1260 distinct endpoints")
    if len(edges) != 630 or len({item["interval_id"] for item in edges}) != 630:
        fail("typing graph does not bind 630 distinct intervals")
    if sum(item["category"] == "C_44" for item in nodes) != 176:
        fail("typing graph does not contain exactly 176 C_44/Y endpoints")
    wrong = [item for item in edges if item["typing_status"] == "wrong_same_side_active"]
    if len(wrong) != 8:
        fail("typing graph does not contain exactly eight wrong-side intervals")
    obligations = graph["oriented_reconnection_obligations"]
    old = [interval for item in obligations for interval in item["old_interval_ids"]]
    if sorted(old) != sorted(item["interval_id"] for item in wrong):
        fail("oriented reconnection obligations do not cover the eight wrong intervals")
    endpoint = {item["endpoint_id"]: item for item in nodes}
    desired = {
        frozenset(("Y_minus", "Z_plus")),
        frozenset(("Y_plus", "Z_minus")),
    }
    for item in obligations:
        if item["status"] != "UNREALIZED" or not item["not_a_pivotal_mate"]:
            fail("an unrealized band obligation was mislabeled")
        for initial, terminal in item["new_oriented_arcs"]:
            if endpoint[initial]["exterior_incidence"] != "exit":
                fail("candidate band arc does not start at an exit")
            if endpoint[terminal]["exterior_incidence"] != "entry":
                fail("candidate band arc does not end at an entry")
            if frozenset((endpoint[initial]["sphere"], endpoint[terminal]["sphere"])) not in desired:
                fail("candidate band arc does not have a cross-side type")
    accounting = graph["single_hom_boundary_accounting"]
    if (
        accounting["active_endpoints_before_any_mate"] != 176
        or accounting["active_endpoints_after_pivotal_retyping"] != 176
        or accounting["active_endpoints_after_four_rematchings"] != 176
        or accounting["P86_to_P88_endpoints"] != 174
        or accounting["external_cup_endpoint_difference"] != 2
    ):
        fail("176-versus-174 boundary accounting was corrupted")


def rational(value: Any, where: str) -> Fraction:
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise CoendWitnessError(f"{where} is not rational: {error}") from error


Matrix = list[list[Fraction]]


def matrix(raw: Any, rows: int, columns: int, where: str) -> Matrix:
    if not isinstance(raw, list) or len(raw) != rows:
        fail(f"{where} has {len(raw) if isinstance(raw, list) else 'non-list'} rows, expected {rows}")
    result = []
    for index, row in enumerate(raw):
        if not isinstance(row, list) or len(row) != columns:
            fail(f"{where}[{index}] has the wrong number of columns")
        result.append([rational(value, f"{where}[{index}]") for value in row])
    return result


def zero(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [
        [Fraction(1 if row == column else 0) for column in range(size)]
        for row in range(size)
    ]


def add(first: Matrix, second: Matrix) -> Matrix:
    return [
        [first[i][j] + second[i][j] for j in range(len(first[i]))]
        for i in range(len(first))
    ]


def subtract(first: Matrix, second: Matrix) -> Matrix:
    return [
        [first[i][j] - second[i][j] for j in range(len(first[i]))]
        for i in range(len(first))
    ]


def multiply(first: Matrix, second: Matrix) -> Matrix:
    rows = len(first)
    middle = len(second)
    columns = len(second[0]) if second else 0
    if first and len(first[0]) != middle:
        fail("internal matrix multiplication shape mismatch")
    return [
        [sum(first[i][k] * second[k][j] for k in range(middle)) for j in range(columns)]
        for i in range(rows)
    ]


def validate_complex(raw: Any, where: str) -> dict[str, Any]:
    require_fields(raw, ["basis_by_degree", "differentials"], where)
    if not isinstance(raw["basis_by_degree"], list) or not raw["basis_by_degree"]:
        fail(f"{where}.basis_by_degree must be nonempty")
    basis: dict[int, list[dict[str, Any]]] = {}
    all_ids: set[str] = set()
    for index, block in enumerate(raw["basis_by_degree"]):
        require_fields(block, ["degree", "basis"], f"{where}.basis_by_degree[{index}]")
        degree = block["degree"]
        if not isinstance(degree, int) or degree in basis:
            fail(f"{where} has a duplicate or nonintegral homological degree")
        if not isinstance(block["basis"], list):
            fail(f"{where} basis at degree {degree} is not a list")
        entries = []
        for entry in block["basis"]:
            require_fields(entry, ["id", "quantum_degree"], f"{where} basis entry")
            if not isinstance(entry["id"], str) or not entry["id"] or entry["id"] in all_ids:
                fail(f"{where} basis IDs are not globally unique")
            if not isinstance(entry["quantum_degree"], int):
                fail(f"{where} has a nonintegral quantum degree")
            all_ids.add(entry["id"])
            entries.append(entry)
        basis[degree] = entries
    if not all_ids:
        fail(f"{where} is the zero complex; this cannot certify the selected class")

    differentials: dict[int, Matrix] = {}
    for item in raw["differentials"]:
        require_fields(item, ["from_degree", "matrix"], f"{where} differential")
        degree = item["from_degree"]
        if not isinstance(degree, int) or degree in differentials:
            fail(f"{where} has duplicate or nonintegral differential degree")
        rows, columns = len(basis.get(degree + 1, [])), len(basis.get(degree, []))
        value = matrix(item["matrix"], rows, columns, f"{where}.d[{degree}]")
        for i, target in enumerate(basis.get(degree + 1, [])):
            for j, source in enumerate(basis.get(degree, [])):
                if value[i][j] and target["quantum_degree"] != source["quantum_degree"]:
                    fail(f"{where}.d[{degree}] is not quantum-degree zero")
        differentials[degree] = value
    for degree in basis:
        current = differentials.get(degree, zero(len(basis.get(degree + 1, [])), len(basis[degree])))
        following = differentials.get(degree + 1, zero(len(basis.get(degree + 2, [])), len(basis.get(degree + 1, []))))
        if multiply(following, current) != zero(len(basis.get(degree + 2, [])), len(basis[degree])):
            fail(f"{where} differential does not square to zero at degree {degree}")
    return {"basis": basis, "d": differentials}


def component(
    raw_map: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
    degree: int,
    where: str,
) -> Matrix:
    shift = raw_map["homological_degree"]
    matches = [item for item in raw_map["components"] if item.get("from_degree") == degree]
    if len(matches) > 1:
        fail(f"{where} has duplicate components at degree {degree}")
    rows = len(target["basis"].get(degree + shift, []))
    columns = len(source["basis"].get(degree, []))
    return matrix(matches[0]["matrix"], rows, columns, f"{where}[{degree}]") if matches else zero(rows, columns)


def validate_map(
    raw: Any,
    source: dict[str, Any],
    target: dict[str, Any],
    where: str,
    require_chain_map: bool,
) -> dict[str, Any]:
    require_fields(raw, ["homological_degree", "quantum_degree", "components"], where)
    if not isinstance(raw["homological_degree"], int) or not isinstance(raw["quantum_degree"], int):
        fail(f"{where} degrees must be integers")
    if not isinstance(raw["components"], list):
        fail(f"{where}.components is not a list")
    result = {
        "homological_degree": raw["homological_degree"],
        "quantum_degree": raw["quantum_degree"],
        "components": {},
    }
    for degree in source["basis"]:
        value = component(raw, source, target, degree, where)
        result["components"][degree] = value
        target_degree = degree + raw["homological_degree"]
        for i, target_entry in enumerate(target["basis"].get(target_degree, [])):
            for j, source_entry in enumerate(source["basis"][degree]):
                if value[i][j] and target_entry["quantum_degree"] != source_entry["quantum_degree"] + raw["quantum_degree"]:
                    fail(f"{where} is not homogeneous of its declared quantum degree")
    declared = {item.get("from_degree") for item in raw["components"]}
    if declared - set(source["basis"]):
        fail(f"{where} has components outside the source complex")
    if require_chain_map:
        shift = raw["homological_degree"]
        for degree in source["basis"]:
            d_source = source["d"].get(
                degree,
                zero(len(source["basis"].get(degree + 1, [])), len(source["basis"].get(degree, []))),
            )
            d_target = target["d"].get(
                degree + shift,
                zero(
                    len(target["basis"].get(degree + shift + 1, [])),
                    len(target["basis"].get(degree + shift, [])),
                ),
            )
            left = multiply(d_target, result["components"][degree])
            next_component = result["components"].get(
                degree + 1,
                zero(
                    len(target["basis"].get(degree + shift + 1, [])),
                    len(source["basis"].get(degree + 1, [])),
                ),
            )
            right = multiply(next_component, d_source)
            if shift % 2:
                right = [[-value for value in row] for row in right]
            if left != right:
                fail(f"{where} is not a chain map at degree {degree}")
    return result


def composed_component(
    second: dict[str, Any], first: dict[str, Any], degree: int
) -> Matrix:
    middle_degree = degree + first["homological_degree"]
    return multiply(second["components"][middle_degree], first["components"][degree])


def homotopy_rhs(
    homotopy: dict[str, Any], complex_data: dict[str, Any], degree: int
) -> Matrix:
    size = len(complex_data["basis"].get(degree, []))
    lower_size = len(complex_data["basis"].get(degree - 1, []))
    upper_size = len(complex_data["basis"].get(degree + 1, []))
    d_lower = complex_data["d"].get(degree - 1, zero(size, lower_size))
    h_here = homotopy["components"].get(degree, zero(lower_size, size))
    h_upper = homotopy["components"].get(degree + 1, zero(size, upper_size))
    d_here = complex_data["d"].get(degree, zero(upper_size, size))
    lower_term = multiply(d_lower, h_here) if lower_size else zero(size, size)
    upper_term = multiply(h_upper, d_here) if upper_size else zero(size, size)
    return add(lower_term, upper_term)


def validate_fiber_equivalence(raw: Any, where: str) -> dict[str, Any]:
    require_fields(
        raw,
        [
            "fiber_id",
            "source_complex",
            "target_complex",
            "theta",
            "theta_inverse",
            "source_homotopy",
            "target_homotopy",
        ],
        where,
    )
    source = validate_complex(raw["source_complex"], f"{where}.source_complex")
    target = validate_complex(raw["target_complex"], f"{where}.target_complex")
    theta = validate_map(raw["theta"], source, target, f"{where}.theta", True)
    inverse = validate_map(
        raw["theta_inverse"], target, source, f"{where}.theta_inverse", True
    )
    if theta["homological_degree"] != 0 or inverse["homological_degree"] != 0:
        fail("theta and theta_inverse must have homological degree zero")
    if inverse["quantum_degree"] != -theta["quantum_degree"]:
        fail("theta_inverse has the wrong quantum degree")
    source_h = validate_map(
        raw["source_homotopy"], source, source, f"{where}.source_homotopy", False
    )
    target_h = validate_map(
        raw["target_homotopy"], target, target, f"{where}.target_homotopy", False
    )
    for name, homotopy in (("source", source_h), ("target", target_h)):
        if homotopy["homological_degree"] != -1 or homotopy["quantum_degree"] != 0:
            fail(f"{name} homotopy must have bidegree (-1,0)")
    for degree in source["basis"]:
        lhs = subtract(composed_component(inverse, theta, degree), identity(len(source["basis"][degree])))
        if lhs != homotopy_rhs(source_h, source, degree):
            fail(f"theta_inverse theta is not homotopic to identity at source degree {degree}")
    for degree in target["basis"]:
        lhs = subtract(composed_component(theta, inverse, degree), identity(len(target["basis"][degree])))
        if lhs != homotopy_rhs(target_h, target, degree):
            fail(f"theta theta_inverse is not homotopic to identity at target degree {degree}")
    return {
        "source": source,
        "target": target,
        "theta": theta,
        "inverse": inverse,
        "source_homotopy": source_h,
        "target_homotopy": target_h,
    }


def validate_chain_certificate(
    raw: Any, presentation: dict[str, Any] | None = None
) -> dict[str, int]:
    require_fields(raw, ["fibers", "residual_naturality"], "chain_certificate")
    if not isinstance(raw["fibers"], list) or not raw["fibers"]:
        fail("chain_certificate.fibers must be nonempty")
    fibers: dict[str, dict[str, Any]] = {}
    for index, fiber_raw in enumerate(raw["fibers"]):
        where = f"chain_certificate.fibers[{index}]"
        require_fields(fiber_raw, ["fiber_id"], where)
        fiber_id = fiber_raw["fiber_id"]
        if not isinstance(fiber_id, str) or not fiber_id or fiber_id in fibers:
            fail("chain certificate fiber IDs must be nonempty and unique")
        fibers[fiber_id] = validate_fiber_equivalence(fiber_raw, where)

    theta_degrees = {fiber["theta"]["quantum_degree"] for fiber in fibers.values()}
    if len(theta_degrees) != 1:
        fail("fiberwise theta maps do not have one homogeneous quantum degree")
    theta_degree = next(iter(theta_degrees))

    if presentation is not None:
        expected_fibers = {item["fiber_id"] for item in presentation["fibers"]}
        if set(fibers) != expected_fibers:
            fail("chain certificate fibers do not exhaust the finite presentation")

    naturality = raw["residual_naturality"]
    if not isinstance(naturality, list) or not naturality:
        fail("residual_naturality must contain a complete generator list")
    seen_names: set[str] = set()
    expected_generators = (
        {item["name"]: item for item in presentation["residual_action_generators"]}
        if presentation is not None
        else None
    )
    for index, item in enumerate(naturality):
        require_fields(
            item,
            [
                "name",
                "side",
                "from_fiber",
                "to_fiber",
                "source_action",
                "target_action",
                "homotopy",
            ],
            f"residual_naturality[{index}]",
        )
        if item["name"] in seen_names or not isinstance(item["name"], str) or not item["name"]:
            fail("residual action generator names must be nonempty and unique")
        if item["side"] not in ("C44_left", "C44_right"):
            fail("residual naturality has an unknown side")
        if item["from_fiber"] not in fibers or item["to_fiber"] not in fibers:
            fail("residual naturality refers to an unknown fiber")
        if expected_generators is not None:
            expected = expected_generators.get(item["name"])
            if expected is None or {
                key: item[key] for key in ("side", "from_fiber", "to_fiber")
            } != {key: expected[key] for key in ("side", "from_fiber", "to_fiber")}:
                fail("residual naturality does not match the finite presentation")
        seen_names.add(item["name"])
        from_fiber = fibers[item["from_fiber"]]
        to_fiber = fibers[item["to_fiber"]]
        source_action = validate_map(
            item["source_action"],
            from_fiber["source"],
            to_fiber["source"],
            f"source_action[{index}]",
            True,
        )
        target_action = validate_map(
            item["target_action"],
            from_fiber["target"],
            to_fiber["target"],
            f"target_action[{index}]",
            True,
        )
        if source_action["homological_degree"] != 0 or target_action["homological_degree"] != 0:
            fail("residual action maps must have homological degree zero")
        if source_action["quantum_degree"] != target_action["quantum_degree"]:
            fail("source and target action degrees differ")
        homotopy = validate_map(
            item["homotopy"],
            from_fiber["source"],
            to_fiber["target"],
            f"naturality_homotopy[{index}]",
            False,
        )
        expected_q = theta_degree + source_action["quantum_degree"]
        if homotopy["homological_degree"] != -1 or homotopy["quantum_degree"] != expected_q:
            fail("naturality homotopy has the wrong bidegree")
        for degree in from_fiber["source"]["basis"]:
            left = multiply(
                to_fiber["theta"]["components"][degree],
                source_action["components"][degree],
            )
            right = multiply(
                target_action["components"][degree],
                from_fiber["theta"]["components"][degree],
            )
            if subtract(left, right) != homotopy_rhs_between(
                homotopy,
                from_fiber["source"],
                to_fiber["target"],
                degree,
            ):
                fail(f"residual naturality fails for {item['name']} at degree {degree}")
    if expected_generators is not None:
        if seen_names != set(expected_generators):
            fail("residual naturality does not exhaust the presentation generators")
    elif {item["side"] for item in naturality} != {"C44_left", "C44_right"}:
        fail("residual naturality does not cover both C_44 actions")
    return {"theta_quantum_degree": theta_degree}


def homotopy_rhs_between(
    homotopy: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
    degree: int,
) -> Matrix:
    source_size = len(source["basis"].get(degree, []))
    source_upper = len(source["basis"].get(degree + 1, []))
    target_size = len(target["basis"].get(degree, []))
    target_lower = len(target["basis"].get(degree - 1, []))
    d_target_lower = target["d"].get(degree - 1, zero(target_size, target_lower))
    h_here = homotopy["components"].get(degree, zero(target_lower, source_size))
    h_upper = homotopy["components"].get(degree + 1, zero(target_size, source_upper))
    d_source = source["d"].get(degree, zero(source_upper, source_size))
    lower_term = (
        multiply(d_target_lower, h_here)
        if target_lower
        else zero(target_size, source_size)
    )
    upper_term = (
        multiply(h_upper, d_source)
        if source_upper
        else zero(target_size, source_size)
    )
    return add(lower_term, upper_term)


def checked_relative_path(raw: str, expected_sha: str, where: str) -> Path:
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
        fail(f"{where} is not a safe repository-relative path")
    path = ROOT / raw
    if not path.is_file():
        fail(f"{where} does not exist: {raw}")
    if content_sha(path) != expected_sha:
        fail(f"{where} content SHA256 mismatch")
    return path


def validate_finite_presentation(
    path: Path, graph_sha: str, route: str
) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CoendWitnessError(f"bar/arc-algebra presentation is not JSON: {error}") from error
    require_fields(
        raw,
        [
            "schema",
            "typing_graph_sha256",
            "route",
            "fibers",
            "residual_action_generators",
            "z_balanced_relation_generators",
            "completeness_theorem",
        ],
        "bar/arc-algebra presentation",
    )
    if raw["schema"] != "t73_c_defect_coend_finite_presentation/v1":
        fail("bar/arc-algebra presentation has the wrong schema")
    if raw["typing_graph_sha256"] != graph_sha or raw["route"] != route:
        fail("bar/arc-algebra presentation is stale or belongs to another route")
    if raw["completeness_theorem"] != REQUIRED_THEOREMS[0]:
        fail("finite presentation is not tied to the required completeness theorem")
    if not isinstance(raw["fibers"], list) or not raw["fibers"]:
        fail("finite presentation has no coefficient fibers")
    fiber_ids: set[str] = set()
    for item in raw["fibers"]:
        require_fields(item, ["fiber_id", "T_object", "T_prime_object"], "presentation fiber")
        if not isinstance(item["fiber_id"], str) or not item["fiber_id"] or item["fiber_id"] in fiber_ids:
            fail("finite presentation fiber IDs must be nonempty and unique")
        if not isinstance(item["T_object"], str) or not isinstance(item["T_prime_object"], str):
            fail("finite presentation fiber object names must be strings")
        fiber_ids.add(item["fiber_id"])
    generators = raw["residual_action_generators"]
    if not isinstance(generators, list) or not generators:
        fail("finite presentation has no residual action generators")
    names: set[str] = set()
    sides: set[str] = set()
    for item in generators:
        require_fields(item, ["name", "side", "from_fiber", "to_fiber"], "residual generator")
        if not isinstance(item["name"], str) or not item["name"] or item["name"] in names:
            fail("finite presentation generator names must be nonempty and unique")
        if item["side"] not in ("C44_left", "C44_right"):
            fail("finite presentation generator has an unknown side")
        if item["from_fiber"] not in fiber_ids or item["to_fiber"] not in fiber_ids:
            fail("finite presentation generator refers to an unknown fiber")
        names.add(item["name"])
        sides.add(item["side"])
    if sides != {"C44_left", "C44_right"}:
        fail("finite presentation does not contain both residual C_44 actions")
    balanced = raw["z_balanced_relation_generators"]
    if not isinstance(balanced, list) or not balanced:
        fail("finite presentation has no C_271 balanced-relation generators")
    balanced_names = []
    for item in balanced:
        require_fields(item, ["name", "fiber_id", "relation"], "z-balanced generator")
        if item["fiber_id"] not in fiber_ids or item["relation"] != "P(id,g)=P(g,id)":
            fail("z-balanced generator has the wrong fiber or relation type")
        balanced_names.append(item["name"])
    if any(not isinstance(name, str) or not name for name in balanced_names) or len(set(balanced_names)) != len(balanced_names):
        fail("z-balanced generator names must be nonempty and unique")
    return raw


def verify_formal_receipt(raw: Any, graph_sha: str) -> None:
    require_fields(
        raw,
        [
            "module_path",
            "module_sha256",
            "no_placeholder_report_path",
            "no_placeholder_report_sha256",
            "required_theorems",
        ],
        "formal_receipt",
    )
    if raw["module_path"] != "Smooth4PC/DefectAwareCoend.lean":
        fail("formal receipt points to the wrong Lean module")
    if raw["no_placeholder_report_path"] != "audit/t73_defect_coend_lean_axioms.json":
        fail("formal receipt points to the wrong no-placeholder report")
    if raw["required_theorems"] != REQUIRED_THEOREMS:
        fail("formal receipt does not list the exact required theorem chain")
    module_path = checked_relative_path(
        raw["module_path"], raw["module_sha256"], "formal Lean module"
    )
    module_text = module_path.read_text(encoding="utf-8")
    # The independent axiom receipt remains authoritative.  This cheap scan
    # catches ordinary placeholders without rejecting words inside comments.
    scanned = re.sub(r"/-.*?-/", "", module_text, flags=re.DOTALL)
    scanned = re.sub(r"--[^\n]*", "", scanned)
    if re.search(
        r"\b(sorry|admit)\b|^\s*axioms?\b", scanned, flags=re.MULTILINE
    ):
        fail("formal Lean module contains a placeholder declaration")
    report_path = checked_relative_path(
        raw["no_placeholder_report_path"],
        raw["no_placeholder_report_sha256"],
        "Lean no-placeholder report",
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require_fields(
        report,
        [
            "schema",
            "typing_graph_sha256",
            "lake_build_status",
            "sorry_count",
            "declaration_axioms",
            "checked_theorems",
        ],
        "Lean no-placeholder report",
    )
    if report["schema"] != "t73_defect_coend_lean_axioms/v1":
        fail("Lean no-placeholder report has the wrong schema")
    if report["typing_graph_sha256"] != graph_sha or report["lake_build_status"] != "PASS":
        fail("Lean no-placeholder report is stale or did not build")
    if report["sorry_count"] != 0:
        fail("Lean comparison proof contains sorry")
    declaration_axioms = report["declaration_axioms"]
    if not isinstance(declaration_axioms, list) or any(
        item not in ALLOWED_LEAN_AXIOMS for item in declaration_axioms
    ):
        fail("Lean comparison proof contains project-specific axioms")
    if report["checked_theorems"] != REQUIRED_THEOREMS:
        fail("Lean no-placeholder report did not inspect the exact theorem chain")


def verify_reconnection_strategy(raw: dict[str, Any], graph: dict[str, Any]) -> None:
    strategy = raw["geometric_strategy"]
    cells = raw["reconnection_cells"]
    if strategy == "preserve_connected_source_matching":
        if cells:
            fail("connected-kernel strategy must not silently alter interval matching")
        return
    if strategy != "explicit_oriented_band_movie":
        fail("unknown geometric strategy")
    if not isinstance(cells, list) or len(cells) != 4:
        fail("explicit band strategy requires exactly four realized cell records")
    expected = {item["obligation_id"]: item for item in graph["oriented_reconnection_obligations"]}
    if {item.get("obligation_id") for item in cells} != set(expected):
        fail("band cells do not cover the four oriented obligations")
    for cell in cells:
        obligation = expected[cell["obligation_id"]]
        require_fields(
            cell,
            [
                "obligation_id",
                "old_interval_ids",
                "new_oriented_arcs",
                "relative_boundary_fixed",
                "elementary_movie_cells",
                "blanchet_sign",
                "homological_degree",
                "quantum_degree",
                "movie_certificate_path",
                "movie_certificate_sha256",
            ],
            f"reconnection cell {cell['obligation_id']}",
        )
        if cell["old_interval_ids"] != obligation["old_interval_ids"] or cell["new_oriented_arcs"] != obligation["new_oriented_arcs"]:
            fail("realized band cell has the wrong boundary matching")
        if cell["relative_boundary_fixed"] is not True:
            fail("realized band cell is not fixed on the insertion boundaries")
        if cell["blanchet_sign"] not in (-1, 1):
            fail("realized band cell has no Blanchet sign")
        if not isinstance(cell["homological_degree"], int) or not isinstance(cell["quantum_degree"], int):
            fail("realized band cell has undetermined degree")
        movie = cell["elementary_movie_cells"]
        if not isinstance(movie, list) or not movie or "saddle" not in movie:
            fail("a matching-changing band record contains no saddle")
        checked_relative_path(
            cell["movie_certificate_path"],
            cell["movie_certificate_sha256"],
            f"movie certificate {cell['obligation_id']}",
        )


def verify_witness(raw: dict[str, Any], graph: dict[str, Any] | None = None) -> dict[str, Any]:
    if graph is None:
        graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    validate_graph(graph)
    require_fields(
        raw,
        [
            "schema",
            "typing_graph_sha256",
            "route",
            "geometric_strategy",
            "literal_split_used",
            "source_binding",
            "boundary_accounting",
            "reconnection_cells",
            "chain_certificate",
            "grading",
            "formal_receipt",
        ],
        "witness",
    )
    if raw["schema"] != "t73_c_defect_coend_witness/v1":
        fail("witness has the wrong schema")
    if raw["typing_graph_sha256"] != graph["sha256"]:
        fail("witness is bound to a stale typing graph")
    if raw["route"] not in ("two_sided_representability", "direct_derived_bar_comparison"):
        fail("witness has an unsupported categorical route")
    if raw["literal_split_used"] is not False:
        fail("the refuted literal split cannot be used")

    binding = raw["source_binding"]
    require_fields(
        binding,
        [
            "endpoint_ids",
            "interval_ids",
            "complete_bar_or_arc_algebra_presentation_locator",
            "presentation_sha256",
        ],
        "source_binding",
    )
    expected_endpoints = sorted(item["endpoint_id"] for item in graph["endpoint_nodes"])
    expected_intervals = sorted(item["interval_id"] for item in graph["interval_edges"])
    if binding["endpoint_ids"] != expected_endpoints or binding["interval_ids"] != expected_intervals:
        fail("source binding is not an exact ordered bijection on all 1260 endpoints and 630 intervals")
    presentation_path = checked_relative_path(
        binding["complete_bar_or_arc_algebra_presentation_locator"],
        binding["presentation_sha256"],
        "bar/arc-algebra presentation",
    )
    presentation = validate_finite_presentation(
        presentation_path, graph["sha256"], raw["route"]
    )

    accounting = raw["boundary_accounting"]
    expected_accounting = {
        "active_y_endpoints_before": 176,
        "active_y_endpoints_after_pivotal_retyping": 176,
        "single_hom_endpoints": 174,
        "external_cup_endpoint_difference": 2,
        "external_cup_is_separate": True,
    }
    if accounting != expected_accounting:
        fail("witness corrupts the 176-versus-174 boundary accounting")
    verify_reconnection_strategy(raw, graph)
    checked = validate_chain_certificate(raw["chain_certificate"], presentation)

    grading = raw["grading"]
    require_fields(
        grading,
        ["theta_quantum_degree", "all_X_target_degree", "cable_shift", "actual_q_C"],
        "grading",
    )
    if grading["theta_quantum_degree"] != checked["theta_quantum_degree"]:
        fail("grading theta degree differs from the checked chain map")
    if grading["all_X_target_degree"] != 227 or grading["cable_shift"] != -4:
        fail("grading ledger changed the target all-X or cable contributions")
    if grading["actual_q_C"] != 223 - grading["theta_quantum_degree"]:
        fail("actual_q_C does not satisfy 223-delta_Theta")
    verify_formal_receipt(raw["formal_receipt"], graph["sha256"])
    return {
        "verdict": "PASS_DEFECT_AWARE_COEND_COMPARISON",
        "route": raw["route"],
        "geometric_strategy": raw["geometric_strategy"],
        "actual_q_C": grading["actual_q_C"],
        "typing_graph_sha256": graph["sha256"],
    }


def inspect_current() -> dict[str, Any]:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    validate_graph(graph)
    if not WITNESS.is_file():
        return {
            "verdict": "OPEN",
            "reason": "no geometry/t73_c_defect_coend_witness.json exists",
            "typing_graph_sha256": graph["sha256"],
            "first_open_gate": graph["first_open_gate"],
        }
    try:
        return verify_witness(json.loads(WITNESS.read_text(encoding="utf-8")), graph)
    except (CoendWitnessError, json.JSONDecodeError) as error:
        return {
            "verdict": "OPEN",
            "reason": str(error),
            "typing_graph_sha256": graph["sha256"],
            "first_open_gate": graph["first_open_gate"],
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("witness", nargs="?", type=Path)
    parser.add_argument("--check-graph", action="store_true")
    args = parser.parse_args()
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    validate_graph(graph)
    if args.check_graph:
        print("T73_C_DEFECT_COEND_GRAPH=VERIFIED_OPEN")
        return
    if args.witness is not None:
        result = verify_witness(json.loads(args.witness.read_text(encoding="utf-8")), graph)
    else:
        result = inspect_current()
    print(f"VERDICT={result['verdict']}")
    if result["verdict"] == "OPEN":
        print(f"REASON={result['reason']}")
    else:
        print(f"ACTUAL_Q_C={result['actual_q_C']}")


if __name__ == "__main__":
    main()
