#!/usr/bin/env python3
"""Redraw T73 objects as manifolds rather than axis-aligned cubes.

The 4-manifold itself is not triangulated.  These figures restore the
pieces that do exist as PL curves and combinatorial 2-spheres:

- the 44-strand control braid (polylines), displayed with over/under
  instead of rest height y = 100 * id
- leftover C1 circles as their actual 4-cycles
- belt 2-spheres as round S^2 inscribed in the certified cubes, with
  dual loops that pierce the balls (Kirby picture of #^3(S^1 x S^2))
- the five-component railroad attaching link on two rails
- the linear CS cores of A, wrapped onto T^3 = I^3
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import matplotlib
from matplotlib import font_manager

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def configure_chinese_font() -> None:
    available = {item.name for item in font_manager.fontManager.ttflist}
    for name in ("Microsoft YaHei", "SimHei", "SimSun", "KaiTi"):
        if name in available:
            plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            return
    plt.rcParams["axes.unicode_minus"] = False


configure_chinese_font()


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit" / "t73_geometry_views"
MATRIX_A = (
    (0, 269, 1240),
    (0, 41, 189),
    (1, 0, 32),
)


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def box_center(box: dict) -> np.ndarray:
    return np.array(
        [
            0.5 * (box["xmin"] + box["xmax"]),
            0.5 * (box["ymin"] + box["ymax"]),
            0.5 * (box["zmin"] + box["zmax"]),
        ],
        dtype=float,
    )


def sphere_mesh(center: np.ndarray, radius: float, nu: int = 28, nv: int = 16):
    u = np.linspace(0.0, 2.0 * np.pi, nu)
    v = np.linspace(0.0, np.pi, nv)
    uu, vv = np.meshgrid(u, v)
    x = center[0] + radius * np.cos(uu) * np.sin(vv)
    y = center[1] + radius * np.sin(uu) * np.sin(vv)
    z = center[2] + radius * np.cos(vv)
    return x, y, z


def piercing_circle(center: np.ndarray, axis: int, radius: float = 1.45, n: int = 96) -> np.ndarray:
    """Circle through the ball center in a plane containing the handle axis."""
    theta = np.linspace(0.0, 2.0 * np.pi, n)
    e_axis = np.zeros(3)
    e_axis[axis] = 1.0
    e_rad = np.zeros(3)
    e_rad[(axis + 2) % 3] = 1.0
    e_theta = np.cross(e_axis, e_rad)
    origin = center + radius * e_rad
    return origin + np.outer(np.cos(theta), -radius * e_rad) + np.outer(np.sin(theta), radius * e_theta)


def equal_3d(ax, pad: float = 0.15) -> None:
    xlim = ax.get_xlim3d()
    ylim = ax.get_ylim3d()
    zlim = ax.get_zlim3d()
    ranges = np.array([xlim[1] - xlim[0], ylim[1] - ylim[0], zlim[1] - zlim[0]], dtype=float)
    ranges = np.maximum(ranges, 1e-6)
    ax.set_box_aspect(ranges)


def inscribed_circle(vertices: list, n: int = 48) -> np.ndarray:
    pts = np.array(vertices, dtype=float)
    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    center = pts.mean(axis=0)
    e1 = pts[1] - pts[0]
    e1 = e1 / np.linalg.norm(e1)
    normal = np.cross(pts[1] - pts[0], pts[2] - pts[0])
    normal = normal / np.linalg.norm(normal)
    e2 = np.cross(normal, e1)
    radius = 0.5 * min(np.linalg.norm(pts[1] - pts[0]), np.linalg.norm(pts[2] - pts[1]))
    theta = np.linspace(0.0, 2.0 * np.pi, n)
    return center + np.outer(np.cos(theta), radius * e1) + np.outer(np.sin(theta), radius * e2)


def cube_wire(ax, lo: np.ndarray, hi: np.ndarray, color: str, lw: float = 0.8, alpha: float = 0.7) -> None:
    corners = np.array(
        [
            [lo[0], lo[1], lo[2]],
            [hi[0], lo[1], lo[2]],
            [hi[0], hi[1], lo[2]],
            [lo[0], hi[1], lo[2]],
            [lo[0], lo[1], hi[2]],
            [hi[0], lo[1], hi[2]],
            [hi[0], hi[1], hi[2]],
            [lo[0], hi[1], hi[2]],
        ]
    )
    edges = (
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    )
    for a, b in edges:
        ax.plot(
            [corners[a, 0], corners[b, 0]],
            [corners[a, 1], corners[b, 1]],
            [corners[a, 2], corners[b, 2]],
            color=color,
            lw=lw,
            alpha=alpha,
        )


def draw_braid_panel(ax, word: list[int], n_strands: int = 44) -> None:
    slots = list(range(n_strands))
    cmap = plt.cm.viridis
    colors = [cmap(i / (n_strands - 1)) for i in range(n_strands)]
    histories = {sid: [(float(sid), 0.0)] for sid in range(n_strands)}
    overs: list[tuple[int, int]] = []
    for step, letter in enumerate(word):
        g = abs(letter) - 1
        left, right = slots[g], slots[g + 1]
        over = right if letter > 0 else left
        next_slots = slots[:]
        next_slots[g], next_slots[g + 1] = right, left
        next_pos = {sid: i for i, sid in enumerate(next_slots)}
        for sid in range(n_strands):
            histories[sid].append((float(next_pos[sid]), float(step + 1)))
        overs.append((over, step))
        slots = next_slots
    for sid in range(n_strands):
        xs = [p[0] for p in histories[sid]]
        ys = [p[1] for p in histories[sid]]
        ax.plot(xs, ys, color=colors[sid], lw=0.85, solid_capstyle="round", zorder=1)
    for over, step in overs:
        (x0, t0) = histories[over][step]
        (x1, t1) = histories[over][step + 1]
        ax.plot([x0, x1], [t0, t1], color=colors[over], lw=1.9, zorder=3, solid_capstyle="round")
    ax.set_xlim(-1, n_strands)
    ax.set_ylim(len(word) + 1, -1)


def plot_braid_window(path: Path, n_letters: int = 64) -> None:
    reconstructor = load_script("reconstruct_t73_p0")
    word = reconstructor.expected_public_word()
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 7.6), sharey=False)
    draw_braid_panel(axes[0], word[:n_letters])
    axes[0].set_title(f"第 1–{n_letters} 个字母：点推移让一股横穿")
    axes[0].set_xlabel("辫槽位")
    axes[0].set_ylabel("沿词的高度（每个 Artin 字母一格，向下）")
    mid = 5600
    draw_braid_panel(axes[1], word[mid : mid + n_letters])
    axes[1].set_title(f"第 {mid + 1}–{mid + n_letters} 个字母：同一词的中段窗口")
    axes[1].set_xlabel("辫槽位")
    fig.suptitle("由 11340 字母公开词还原的 44 股控制辫")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_braid_tube(path: Path, n_letters: int = 48) -> None:
    reconstructor = load_script("reconstruct_t73_p0")
    control = load_script("generate_t73_target_braid_control")
    word = reconstructor.expected_public_word()[:n_letters]
    collar = control.control_collar(reconstructor, word=word)
    fig = plt.figure(figsize=(10.4, 7.2))
    ax = fig.add_subplot(111, projection="3d")
    cmap = plt.cm.viridis
    for strand in collar["strands"]:
        color = cmap((strand["id"] - 1) / 43)
        pts = []
        for x, y, z in strand["vertices"]:
            if y == 1:
                dy = 0.45
            elif y == 0:
                dy = -0.45
            else:
                dy = 0.0
            pts.append((float(x), dy, float(z) / 4.0))
        xs, ys, zs = zip(*pts)
        ax.plot(xs, ys, zs, color=color, lw=0.7, alpha=0.9)
    ax.set_xlabel("x（槽位）")
    ax.set_ylabel("上跨 / 下穿")
    ax.set_zlabel("词高度")
    ax.set_title("同一条辫在 3-球图卡中：压掉休息高度，保留上跨下穿")
    ax.set_box_aspect((44, 4, n_letters))
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_leftover_circles(path: Path) -> None:
    c1 = json.loads((ROOT / "audit" / "t73_c1_cut_link.json").read_text(encoding="utf-8"))
    circles = c1["circles"]
    owner_color = {"m_2": "#4C78A8", "m_3": "#F58518", "r_xy": "#54A24B", "r_yz": "#E45756", "r_zx": "#B279A2"}
    fig = plt.figure(figsize=(11.6, 5.6))
    ax3 = fig.add_subplot(121, projection="3d")
    axz = fig.add_subplot(122, projection="3d")
    seen = set()
    for item in circles:
        ring = inscribed_circle(item["vertices"])
        color = owner_color.get(item["owner"], "#888888")
        label = item["owner"] if item["owner"] not in seen else None
        seen.add(item["owner"])
        ax3.plot(ring[:, 0], ring[:, 1], ring[:, 2], color=color, lw=0.7, label=label)
    ax3.view_init(elev=18, azim=-72)
    ax3.set_xlabel("x")
    ax3.set_ylabel("y")
    ax3.set_zlabel("z")
    ax3.set_title(f"{len(circles)} 条剩余圆（画在各自平面上）")
    if seen:
        ax3.legend(loc="upper left", fontsize=8)

    zoom = circles[80:88]
    for item in zoom:
        ring = inscribed_circle(item["vertices"], n=64)
        color = owner_color.get(item["owner"], "#888888")
        axz.plot(ring[:, 0], ring[:, 1], ring[:, 2], color=color, lw=2.0)
    axz.set_title("放大：连续八条剩余圆")
    axz.set_xlabel("x")
    axz.set_ylabel("y")
    axz.set_zlabel("z")
    equal_3d(axz)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_kirby_spheres(path: Path) -> None:
    s = json.loads((ROOT / "audit" / "t73_s_standard_spheres.json").read_text(encoding="utf-8"))
    colors = ["#E45756", "#72B7B2", "#B279A2"]
    axes = {"h1": 0, "h2": 1, "h3": 2}
    fig = plt.figure(figsize=(11.6, 5.6))

    ax = fig.add_subplot(121, projection="3d")
    local = [np.array([0.0, 0.0, 0.0]), np.array([4.0, 0.0, 0.0]), np.array([8.0, 0.0, 0.0])]
    for center, color, handle, sphere in zip(local, colors, s["one_handles"], s["spheres"]):
        x, y, z = sphere_mesh(center, 1.0)
        ax.plot_surface(x, y, z, color=color, alpha=0.35, linewidth=0, shade=True)
        loop = piercing_circle(center, axes[handle["name"]], radius=1.5)
        ax.plot(loop[:, 0], loop[:, 1], loop[:, 2], color=color, lw=2.0, label=sphere["name"])
    ax.set_xlim(-2.2, 10.2)
    ax.set_ylim(-2.2, 3.2)
    ax.set_zlim(-2.2, 3.2)
    ax.set_title("腰带 2-球面与对偶环\n（组合类型为 #^3(S^1 x S^2)）")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.legend(loc="upper left", fontsize=8)
    equal_3d(ax)

    ax = fig.add_subplot(122, projection="3d")
    for sphere, handle, color in zip(s["spheres"], s["one_handles"], colors):
        center = box_center(sphere["box"])
        x, y, z = sphere_mesh(center, 1.0)
        ax.plot_surface(x, y, z, color=color, alpha=0.4, linewidth=0, shade=True)
        loop = piercing_circle(center, axes[handle["name"]], radius=1.5)
        ax.plot(loop[:, 0], loop[:, 1], loop[:, 2], color=color, lw=1.8, label=sphere["name"])
    ax.set_title("同一组球面，内切于证书中的 2×2×2 立方体")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.legend(loc="upper left", fontsize=8)
    equal_3d(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def railroad_polyline(word: list[int], component_id: int) -> np.ndarray:
    n = len(word)
    pts = []
    for index, letter in enumerate(word):
        axis = "y" if abs(letter) == 2 else "z"
        time = index / n
        height = time + component_id / 10.0
        if axis == "y":
            pts.append((0.0, time, height))
        else:
            pts.append((1.0, time, height))
    pts.append(pts[0])
    return np.array(pts, dtype=float)


def split_unknot() -> np.ndarray:
    theta = np.linspace(0.0, 2.0 * np.pi, 80)
    return np.stack(
        [0.50 + 0.10 * np.cos(theta), 0.84 + 0.10 * np.sin(theta), np.full_like(theta, 1.38)],
        axis=1,
    )


def plot_railroad(path: Path) -> None:
    e13 = load_script("certify_t73_e13_close")
    compact = load_script("generate_t73_compact_kirby_ledger")
    words = {
        "r_xy": e13.letters_to_int(
            ["z" if value == "x" else "Z" if value == "X" else value for value in compact.commutator("x", "y")]
        ),
        "r_yz": e13.letters_to_int(compact.commutator("y", "z")),
        "m_2": e13.letters_to_int(compact.after_x_cancellation(1)),
        "m_3": e13.letters_to_int(compact.after_x_cancellation(2)),
        "r_zx": [],
    }
    colors = {
        "r_xy": "#54A24B",
        "r_yz": "#E45756",
        "m_2": "#4C78A8",
        "m_3": "#F58518",
        "r_zx": "#B279A2",
    }
    fig = plt.figure(figsize=(12.4, 6.0))
    ax = fig.add_subplot(121, projection="3d")
    ax2 = fig.add_subplot(122, projection="3d")
    for name, word in words.items():
        if name == "r_zx":
            pts = split_unknot()
        else:
            pts = railroad_polyline(word, list(words).index(name))
        ax.plot(
            pts[:, 0],
            pts[:, 1],
            pts[:, 2],
            color=colors[name],
            lw=0.45 if name == "m_3" else 1.4,
            alpha=0.28 if name == "m_3" else 1.0,
            label=f"{name}（{len(word)} 个字母）",
        )
        if name != "m_3":
            ax2.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=colors[name], lw=1.6, label=name)
    ax.plot([0, 0], [0, 1], [0, 1], color="#bbbbbb", lw=3.0, alpha=0.35)
    ax.plot([1, 1], [0, 1], [0, 1], color="#bbbbbb", lw=3.0, alpha=0.35)
    ax2.plot([0, 0], [0, 1], [0, 1], color="#bbbbbb", lw=3.0, alpha=0.35)
    ax2.plot([1, 1], [0, 1], [0, 1], color="#bbbbbb", lw=3.0, alpha=0.35)
    ax.set_title("两条 1-把手轨上的铁路附着链")
    ax2.set_title("去掉 m_3 后的同一条链（1460 个字母会挡住其余部分）")
    for axis in (ax, ax2):
        axis.set_xlabel("轨（y=0，z=1）")
        axis.set_ylabel("字母时间")
        axis.set_zlabel("高度")
        axis.legend(loc="upper left", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def wrapped_segments(vector: tuple[int, int, int], samples: int) -> list[np.ndarray]:
    ts = np.linspace(0.0, 1.0, samples)
    raw = ts[:, None] * np.array(vector, dtype=float)
    wrapped = np.mod(raw, 1.0)
    segs = []
    current = [wrapped[0]]
    for i in range(1, samples):
        if np.any(np.abs(wrapped[i] - wrapped[i - 1]) > 0.5):
            segs.append(np.array(current))
            current = [wrapped[i]]
        else:
            current.append(wrapped[i])
    segs.append(np.array(current))
    return segs


def plot_t3_cores(path: Path) -> None:
    fig = plt.figure(figsize=(12.2, 5.8))
    ax = fig.add_subplot(121, projection="3d")
    ax2 = fig.add_subplot(122, projection="3d")
    cube_wire(ax, np.zeros(3), np.ones(3), "#888888", 1.0, 0.8)
    colors = ["#E45756", "#4C78A8", "#F58518"]
    names = ["A e1 = (0,0,1)", "A e2 = (269,41,0)", "A e3 = (1240,189,32)"]
    samples = [40, 900, 2400]
    for column, color, name, n in zip(range(3), colors, names, samples):
        vector = tuple(MATRIX_A[row][column] for row in range(3))
        for seg in wrapped_segments(vector, n):
            if len(seg) < 2:
                continue
            ax.plot(seg[:, 0], seg[:, 1], seg[:, 2], color=color, lw=1.1 if column else 2.2, alpha=0.85 if column < 2 else 0.22)
        ax.plot([], [], [], color=color, lw=2.0, label=name)
        end = np.array(vector, dtype=float)
        ax2.plot([0, end[0]], [0, end[1]], [0, end[2]], color=color, lw=2.0, label=name)
    ax.scatter([0], [0], [0], color="black", s=30, zorder=5)
    ax.set_title("缠在 T^3 = I^3 / ~ 上的 CS 核")
    ax.set_xlabel("x mod 1")
    ax.set_ylabel("y mod 1")
    ax.set_zlabel("z mod 1")
    ax.legend(loc="upper left", fontsize=7)
    ax.set_box_aspect((1, 1, 1))
    ax2.set_title("展开：R^3 中从 0 到 A e_j 的直线段")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.set_zlabel("z")
    ax2.legend(loc="upper left", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_mapping_torus(path: Path) -> None:
    fig = plt.figure(figsize=(10.8, 5.4))
    ax = fig.add_subplot(121, projection="3d")
    cube_wire(ax, np.array([0, 0, 0]), np.array([1, 1, 1]), "#4C78A8", 1.4)
    cube_wire(ax, np.array([0, 0, 1.6]), np.array([1, 1, 2.6]), "#E45756", 1.4)
    for x, y in ((0, 0), (1, 0), (0, 1), (1, 1)):
        ax.plot([x, x], [y, y], [1, 1.6], color="#888888", lw=0.8, ls="--")
    ax.scatter([0], [0], [0], color="black", s=25)
    ax.scatter([0], [0], [1.6], color="black", s=25)
    ax.plot([0, 0], [0, 0], [0, 2.6], color="#54A24B", lw=2.4, label="截面 {0} x I，随后做 0-手术")
    ax.set_title("映射环面示意：T^3 x I，两端用 A 粘合")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("t（画成高度）")
    ax.legend(loc="upper left", fontsize=8)

    ax2 = fig.add_subplot(122, projection="3d")
    origin = np.zeros(3)
    cols = [np.array([MATRIX_A[row][j] for row in range(3)], dtype=float) for j in range(3)]
    colors = ["#E45756", "#4C78A8", "#F58518"]
    for col, color, name in zip(cols, colors, ("A e1", "A e2", "A e3")):
        ax2.plot([0, col[0]], [0, col[1]], [0, col[2]], color=color, lw=2.2, label=name)
    for a, b in (
        (origin, cols[0]),
        (origin, cols[1]),
        (origin, cols[2]),
        (cols[0], cols[0] + cols[1]),
        (cols[0], cols[0] + cols[2]),
        (cols[1], cols[1] + cols[0]),
        (cols[1], cols[1] + cols[2]),
        (cols[2], cols[2] + cols[0]),
        (cols[2], cols[2] + cols[1]),
        (cols[0] + cols[1], cols[0] + cols[1] + cols[2]),
        (cols[0] + cols[2], cols[0] + cols[1] + cols[2]),
        (cols[1] + cols[2], cols[0] + cols[1] + cols[2]),
    ):
        ax2.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color="#888888", lw=0.7, alpha=0.7)
    ax2.set_title("单值胞腔 A(I^3)")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.set_zlabel("z")
    ax2.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-braid", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if not args.skip_braid:
        plot_braid_window(OUT / "braid_artin_window.png")
        plot_braid_tube(OUT / "braid_tube_3d.png")
    plot_leftover_circles(OUT / "leftover_z_circles.png")
    plot_kirby_spheres(OUT / "belt_spheres_round.png")
    plot_railroad(OUT / "railroad_link_3d.png")
    plot_t3_cores(OUT / "t3_cs_cores.png")
    plot_mapping_torus(OUT / "mapping_torus_schematic.png")
    print(f"WROTE={OUT}")
    for item in sorted(OUT.glob("*.png")):
        print(item.name)


if __name__ == "__main__":
    main()
