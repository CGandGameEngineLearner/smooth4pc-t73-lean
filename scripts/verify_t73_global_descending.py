from __future__ import annotations

import argparse
import hashlib
import json
from array import array
from pathlib import Path


EXPECTED_PD_SHA256 = "e6912a64457557469e5c691b4d57abdbbf4c45adb05492777c574223d0c06f8a"
EXPECTED_ORDER = {"r_xy": 0, "r_yz": 1, "m_2": 2, "m_3": 3}
EXPECTED_SELF = {"r_xy": 9, "r_yz": 3, "m_2": 64631, "m_3": 1445582}
EXPECTED_MUTUAL = {
    ("r_xy", "r_yz"): 16,
    ("r_xy", "m_2"): 336,
    ("r_xy", "m_3"): 1512,
    ("r_yz", "m_2"): 336,
    ("r_yz", "m_3"): 1512,
    ("m_2", "m_3"): 608786,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verify(path: Path) -> dict[str, object]:
    digest = sha256(path)
    if digest != EXPECTED_PD_SHA256:
        raise ValueError(f"unexpected PD identity: {digest}")
    data = json.loads(path.read_text(encoding="utf-8"))
    pd = data["pd"]
    names = [row["component_id"] for row in data["components"]]

    maximum = max(max(row) for row in pd)
    parent = array("I", range(maximum + 1))
    rank = bytearray(maximum + 1)

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        left = find(left)
        right = find(right)
        if left == right:
            return
        if rank[left] < rank[right]:
            left, right = right, left
        parent[right] = left
        if rank[left] == rank[right]:
            rank[left] += 1

    # In the emitted PD convention, entries 0/2 are the under branch and
    # entries 1/3 are the over branch.
    for under_in, over_a, under_out, over_b in pd:
        union(under_in, under_out)
        union(over_a, over_b)

    root_data: dict[int, list[int]] = {}
    for label in range(1, maximum + 1):
        root = find(label)
        if root not in root_data:
            root_data[root] = [label, label, 0]
        row = root_data[root]
        row[1] = label
        row[2] += 1

    components = sorted(root_data.values())
    if len(components) != len(names):
        raise AssertionError("PD component count does not match component ledger")
    ranges = []
    for name, (lower, upper, count) in zip(names, components):
        if upper - lower + 1 != count:
            raise AssertionError(f"{name}: non-contiguous arc labels")
        ranges.append((lower, upper, count, name))

    # Arc labels are contiguous and component ordered by emit_pd.
    def component_of(label: int) -> tuple[int, int, int, str]:
        for index, (lower, upper, count, name) in enumerate(ranges):
            if lower <= label <= upper:
                return index, lower, count, name
        raise KeyError(label)

    self_counts = {name: 0 for name in EXPECTED_ORDER}
    self_pairs: dict[str, list[tuple[int, int]]] = {
        name: [] for name in EXPECTED_ORDER
    }
    gate_candidates: dict[str, set[int]] = {
        name: set() for name in EXPECTED_ORDER
    }
    mutual_counts: dict[tuple[str, str], int] = {}
    bad_mutual = []

    for crossing_index, (under_in, over_a, under_out, over_b) in enumerate(pd):
        under_component, under_lower, under_count, under_name = component_of(under_in)
        over_component, over_lower, over_count, over_name = component_of(over_a)

        next_over_a = over_lower + ((over_a - over_lower + 1) % over_count)
        next_over_b = over_lower + ((over_b - over_lower + 1) % over_count)
        if next_over_a == over_b:
            over_in, over_out = over_a, over_b
        elif next_over_b == over_a:
            over_in, over_out = over_b, over_a
        else:
            raise AssertionError(f"crossing {crossing_index}: over arcs not consecutive")

        if under_component == over_component and under_name in EXPECTED_ORDER:
            self_counts[under_name] += 1
            over_position = over_in - over_lower
            under_position = under_in - under_lower
            self_pairs[under_name].append((over_position, under_position))
        elif under_name in EXPECTED_ORDER and over_name in EXPECTED_ORDER:
            key = (over_name, under_name)
            mutual_counts[key] = mutual_counts.get(key, 0) + 1
            if not EXPECTED_ORDER[over_name] < EXPECTED_ORDER[under_name]:
                bad_mutual.append([crossing_index, over_name, under_name])

        # A gate cut may begin on either side of the owner/gate crossing.
        if under_name in EXPECTED_ORDER and over_name.startswith("gate_"):
            gate_candidates[under_name].update(
                ((under_in - under_lower) % under_count,
                 (under_out - under_lower) % under_count)
            )
        if over_name in EXPECTED_ORDER and under_name.startswith("gate_"):
            gate_candidates[over_name].update(
                ((over_in - over_lower) % over_count,
                 (over_out - over_lower) % over_count)
            )

    if self_counts != EXPECTED_SELF:
        raise AssertionError(f"self counts differ: {self_counts}")
    if mutual_counts != EXPECTED_MUTUAL:
        raise AssertionError(f"mutual counts differ: {mutual_counts}")
    if bad_mutual:
        raise AssertionError(f"mutual-height failures: {bad_mutual[:3]}")

    gate_aligned: dict[str, dict[str, int]] = {}
    self_failures = 0
    for name in EXPECTED_ORDER:
        count = next(row[2] for row in ranges if row[3] == name)
        difference = [0] * (count + 1)

        def forbid(left: int, right: int) -> None:
            if left <= right:
                difference[left] += 1
                difference[right + 1] -= 1
            else:
                difference[left] += 1
                difference[count] -= 1
                difference[0] += 1
                difference[right + 1] -= 1

        # For a self crossing with over event o and under event u, bases in
        # the cyclic interval (o,u] encounter under first and are forbidden.
        for over_position, under_position in self_pairs[name]:
            forbid((over_position + 1) % count, under_position)

        allowed = set()
        coverage = 0
        for position in range(count):
            coverage += difference[position]
            if coverage == 0:
                allowed.add(position)
        allowed_gate = sorted(allowed.intersection(gate_candidates[name]))
        if not allowed_gate:
            raise AssertionError(f"{name}: no gate-aligned descending basepoint")
        chosen = allowed_gate[0]
        failures = sum(
            not ((over_position - chosen) % count <
                 (under_position - chosen) % count)
            for over_position, under_position in self_pairs[name]
        )
        if failures:
            raise AssertionError(f"{name}: chosen gate base has {failures} failures")
        self_failures += failures
        gate_aligned[name] = {
            "chosen_arc_position": chosen,
            "gate_candidate_count": len(gate_candidates[name]),
            "allowed_gate_basepoint_count": len(allowed_gate),
        }

    return {
        "schema": "t73_global_descending_exact_replay/v1",
        "pd_path": str(path),
        "pd_sha256": digest,
        "pd_bytes": path.stat().st_size,
        "pd_crossings": len(pd),
        "component_arc_ranges": {
            name: {"lower": lower, "upper": upper, "count": count}
            for lower, upper, count, name in ranges
        },
        "self_crossings": self_counts,
        "gate_aligned_basepoints": gate_aligned,
        "self_crossing_over_first_failures": self_failures,
        "mutual_crossings_over_under": {
            f"{over}>{under}": count
            for (over, under), count in mutual_counts.items()
        },
        "mutual_height_order": ["r_xy", "r_yz", "m_2", "m_3"],
        "mutual_height_failures": len(bad_mutual),
        "verdict": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pd",
        nargs="?",
        type=Path,
        default=(
            Path(__file__).resolve().parents[1]
            / "evidence"
            / "public_geometry"
            / "t73_reduced_billiard.pd.json"
        ),
    )
    args = parser.parse_args()
    print(json.dumps(verify(args.pd), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
