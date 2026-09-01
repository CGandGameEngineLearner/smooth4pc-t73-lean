from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import sympy as sp

DIAGRAM = Path(r"D:\tmp\s4pc_ruler\DIAGRAM")
sys.path.insert(0, str(DIAGRAM))

from words_to_pd import billiard_word  # noqa: E402


A = [[0, 269, 1240], [0, 41, 189], [1, 0, 32]]
P = [[-71, 466, -1], [-610, 4004, -7], [-1, 7, 2]]
D_SIGN = [[-1, 0, 0], [0, 1, 0], [0, 0, -1]]
R_BASIS = [[71, -466, 1], [-610, 4004, -7], [1, -7, -2]]  # D_SIGN * P
# AR-form representative with m=713>0 and lambda=83>=0.
C_AR = [[0, 0, 1], [713, 83, 0], [-902, -105, -10]]
ORDER = {"x": 0, "y": 1, "z": 2}
SWAP = {
    ("y", "x"): ("r_xy", +1),
    ("z", "x"): ("r_zx", -1),
    ("z", "y"): ("r_yz", +1),
}


def expanded_collected(j: int) -> list[str]:
    return [g for g, n in zip(("x", "y", "z"), (A[0][j], A[1][j], A[2][j])) for _ in range(n)]


def slide_sort(j: int) -> dict:
    owner = f"m_{j + 1}"
    raw = [g for g, _ in billiard_word(tuple(A[i][j] for i in range(3)))]
    # Event identity is frozen before sorting, so repeated letters remain distinguishable.
    seen = Counter()
    state = []
    for g in raw:
        state.append([g, seen[g]])
        seen[g] += 1

    h = hashlib.sha256()
    compact_steps = []
    by_relator = Counter()
    steps = 0

    # Stable insertion sort. Each adjacent inverted pair is one whiskered slide.
    for i in range(1, len(state)):
        k = i
        while k and ORDER[state[k - 1][0]] > ORDER[state[k][0]]:
            left = state[k - 1]
            right = state[k]
            relator, sign = SWAP[(left[0], right[0])]
            rec = {
                "owner": owner,
                "step": steps,
                "adjacent_index": k - 1,
                "source_pair": [left, right],
                "target_pair": [right, left],
                "slide_over": relator,
                "orientation_sign": sign,
                "whisker": "current prefix before adjacent_index",
                "normal_rule": "fiber-cell product band; zero relative twist",
            }
            h.update((json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode())
            compact_steps.append((k - 1, left, right, relator, sign))
            by_relator[(relator, sign)] += 1
            state[k - 1], state[k] = state[k], state[k - 1]
            steps += 1
            k -= 1

    final = [x[0] for x in state]
    expected = expanded_collected(j)
    assert final == expected

    # Append x_j^-1 and free-reduce at the canonical end.
    terminal = ("x", "y", "z")[j]
    assert final and final[-1] == terminal
    reduced_pre_x_cancel = final[:-1]
    reduced_after_x_cancel = [("z" if g == "x" else g) for g in reduced_pre_x_cancel]

    h_reverse = hashlib.sha256()
    for reverse_step, (adjacent_index, left, right, relator, sign) in enumerate(reversed(compact_steps)):
        rec = {
            "owner": owner,
            "step": reverse_step,
            "adjacent_index": adjacent_index,
            "source_pair": [right, left],
            "target_pair": [left, right],
            "slide_over": relator,
            "orientation_sign": -sign,
            "whisker": "current prefix before adjacent_index",
            "normal_rule": "fiber-cell product band; zero relative twist",
        }
        h_reverse.update((json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode())

    return {
        "owner": owner,
        "input_billiard_letters": len(raw),
        "stable_collected_letters_before_terminal_inverse": len(final),
        "adjacent_framed_slides": steps,
        "slides_by_relator_and_sign": {
            f"{r}:{s:+d}": n for (r, s), n in sorted(by_relator.items())
        },
        "slide_stream_sha256": h.hexdigest(),
        "reverse_collected_to_billiard_stream_sha256": h_reverse.hexdigest(),
        "after_terminal_free_reduction_length": len(reduced_pre_x_cancel),
        "after_x_to_z_length": len(reduced_after_x_cancel),
        "after_x_to_z_runs": run_length(reduced_after_x_cancel),
    }


def post_x_cancel_slide_sort(j: int) -> dict:
    """Use the registered x->z cancellation first, then slide only over r_yz.

    The origin label is retained by the cancellation receipt.  Equal geometric
    z letters never need a slide; only y/z inversions are exchanged.
    """
    owner = f"m_{j + 1}"
    raw = [g for g, _ in billiard_word(tuple(A[i][j] for i in range(3)))]
    seen = Counter()
    state = []
    for origin in raw:
        state.append({"origin": origin, "event": seen[origin], "geom": "z" if origin == "x" else origin})
        seen[origin] += 1

    # Stable target by original coordinate block; swapping x-origin z with
    # intrinsic z is unnecessary because the post-cancellation geometric
    # letters are identical. Insertion sort below only records unequal geom.
    h = hashlib.sha256()
    steps = []
    for i in range(1, len(state)):
        k = i
        while k and ORDER[state[k - 1]["origin"]] > ORDER[state[k]["origin"]]:
            left, right = state[k - 1], state[k]
            if left["geom"] == right["geom"]:
                state[k - 1], state[k] = right, left
                k -= 1
                continue
            pair = (left["geom"], right["geom"])
            assert pair in (("y", "z"), ("z", "y"))
            # r_yz=[y,z].  r^-1 yz=zy and r zy=yz.
            sign = -1 if pair == ("y", "z") else +1
            rec = {
                "owner": owner,
                "step": len(steps),
                "adjacent_index": k - 1,
                "source_pair": [left, right],
                "target_pair": [right, left],
                "slide_over": "r_yz",
                "orientation_sign": sign,
                "whisker": "current post-x-cancel prefix before adjacent_index",
                "normal_rule": "fiber-cell product band; zero relative twist",
            }
            h.update((json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode())
            steps.append(rec)
            state[k - 1], state[k] = right, left
            k -= 1

    expected_origins = expanded_collected(j)
    assert [s["origin"] for s in state] == expected_origins
    terminal = ("x", "y", "z")[j]
    assert state[-1]["geom"] == ("z" if terminal == "x" else terminal)
    state.pop()  # terminal inverse free cancellation in a product bigon
    geom = [s["geom"] for s in state]

    reverse_hash = hashlib.sha256()
    for n, rec0 in enumerate(reversed(steps)):
        rec = dict(rec0)
        rec["step"] = n
        rec["source_pair"], rec["target_pair"] = rec0["target_pair"], rec0["source_pair"]
        rec["orientation_sign"] = -rec0["orientation_sign"]
        reverse_hash.update((json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode())

    return {
        "owner": owner,
        "slides_over_r_yz_only": len(steps),
        "sign_counts": dict(Counter(f"{s['orientation_sign']:+d}" for s in steps)),
        "billiard_to_collected_stream_sha256": h.hexdigest(),
        "collected_to_billiard_stream_sha256": reverse_hash.hexdigest(),
        "final_runs": run_length(geom),
    }


def run_length(word: list[str]) -> list[list[object]]:
    out: list[list[object]] = []
    for g in word:
        if out and out[-1][0] == g:
            out[-1][1] += 1
        else:
            out.append([g, 1])
    return out


def main() -> None:
    AA, RR, CC = sp.Matrix(A), sp.Matrix(R_BASIS), sp.Matrix(C_AR)
    assert RR.det() == 1 and RR.inv() * CC * RR == AA
    basis_reduction_ops = [
        ["swap", 0, 2],
        ["add", 1, 0, 610],
        ["add", 2, 0, -71],
        ["swap", 1, 2],
        ["add", 2, 1, 9],
        ["swap", 1, 2],
        ["add", 2, 1, -2],
        ["swap", 1, 2],
        ["add", 2, 1, -3],
        ["swap", 1, 2],
        ["add", 2, 1, 2],
        ["swap", 1, 2],
        ["add", 2, 1, 2],
        ["add", 0, 2, 2],
        ["add", 1, 2, -5],
        ["add", 0, 1, 7],
    ]
    check = RR.copy()
    for op in basis_reduction_ops:
        if op[0] == "swap":
            check.row_swap(op[1], op[2])
        else:
            check[op[1], :] = check[op[1], :] + op[3] * check[op[2], :]
    assert check == sp.eye(3)
    rows = [slide_sort(1), slide_sort(2)]
    result = {
        "schema": "t73_christoffel_to_collected_commutator_slide_stream/v1",
        "matrix": A,
        "ar_matrix_basis_bridge": {
            "C_AR": C_AR,
            "AR_parameters": {"a": 73, "lambda": 83, "m": 713, "n": -902, "p": -105},
            "R": R_BASIS,
            "det_R": int(RR.det()),
            "identity": "R^-1 C_AR R = A",
            "row_reduction_of_R_to_I": basis_reduction_ops,
            "interpretation": "reverse operations are a finite oriented 1-handle basis-change program; dual 2-handle slides carry the full framed presentation",
        },
        "algorithm": "stable adjacent sort x<y<z before the two registered 1/2 cancellations",
        "local_identities": {
            "yx_to_xy": "[x,y] yx = xy; slide m over r_xy with sign +1",
            "zx_to_xz": "[z,x]^-1 zx = xz; slide m over r_zx with sign -1",
            "zy_to_yz": "[y,z] zy = yz; slide m over r_yz with sign +1",
        },
        "rows": rows,
        "total_adjacent_framed_slides": sum(r["adjacent_framed_slides"] for r in rows),
        "preferred_post_x_cancel_program": [post_x_cancel_slide_sort(1), post_x_cancel_slide_sort(2)],
        "framing_statement": (
            "Each band is the product band in the corresponding fiber 2-cell. "
            "It transports the fiber-band normal with zero relative twist. This "
            "does not compute its winding relative to the independent C4/C5 blackboard frame."
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
