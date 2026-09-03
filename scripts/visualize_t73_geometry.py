#!/usr/bin/env python3
"""Orthogonal slices and split-scale 3D views of the Johnson-replacement PL objects.

The P0 cube is about 45 x 4402 x 45362. Belt spheres sit in the far +y/+z
corner. One equal-aspect 3D plot would hide them, so this program draws
the near field and far field separately, plus xy/xz slices at the
certificate coordinates.
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
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


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


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cube_edges(box: dict[str, float]) -> list[list[list[float]]]:
    x0, x1 = box["xmin"], box["xmax"]
    y0, y1 = box["ymin"], box["ymax"]
    z0, z1 = box["zmin"], box["zmax"]
    corners = [
        [x0, y0, z0],
        [x1, y0, z0],
        [x1, y1, z0],
        [x0, y1, z0],
        [x0, y0, z1],
        [x1, y0, z1],
        [x1, y1, z1],
        [x0, y1, z1],
    ]
    pairs = (
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
    return [[corners[a], corners[b]] for a, b in pairs]


def draw_cube(ax, box: dict[str, float], color: str, lw: float = 1.2) -> None:
    for a, b in cube_edges(box):
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color=color, lw=lw)


def box_center(box: dict[str, float]) -> list[float]:
    return [
        0.5 * (box["xmin"] + box["xmax"]),
        0.5 * (box["ymin"] + box["ymax"]),
        0.5 * (box["zmin"] + box["zmax"]),
    ]


def faces(box: dict[str, float]) -> list[list[list[float]]]:
    x0, x1 = box["xmin"], box["xmax"]
    y0, y1 = box["ymin"], box["ymax"]
    z0, z1 = box["zmin"], box["zmax"]
    return [
        [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]],
        [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]],
        [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]],
        [[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]],
        [[x0, y0, z0], [x0, y1, z0], [x0, y1, z1], [x0, y0, z1]],
        [[x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]],
    ]


def shade_cube(ax, box: dict[str, float], color: str, alpha: float = 0.18) -> None:
    ax.add_collection3d(Poly3DCollection(faces(box), facecolors=color, alpha=alpha, linewidths=0))


def set_equal_3d(ax, boxes: list[dict[str, float]], pad: float = 4.0) -> None:
    xs = [b["xmin"] for b in boxes] + [b["xmax"] for b in boxes]
    ys = [b["ymin"] for b in boxes] + [b["ymax"] for b in boxes]
    zs = [b["zmin"] for b in boxes] + [b["zmax"] for b in boxes]
    lo = [min(xs) - pad, min(ys) - pad, min(zs) - pad]
    hi = [max(xs) + pad, max(ys) + pad, max(zs) + pad]
    span = max(hi[i] - lo[i] for i in range(3)) or 1.0
    mid = [(lo[i] + hi[i]) / 2 for i in range(3)]
    ax.set_xlim(mid[0] - span / 2, mid[0] + span / 2)
    ax.set_ylim(mid[1] - span / 2, mid[1] + span / 2)
    ax.set_zlim(mid[2] - span / 2, mid[2] + span / 2)


def leftover_boxes(c1: dict) -> list[dict[str, int]]:
    boxes = []
    for item in c1["circles"]:
        pts = item["vertices"]
        boxes.append(
            {
                "xmin": min(p[0] for p in pts),
                "xmax": max(p[0] for p in pts),
                "ymin": min(p[1] for p in pts),
                "ymax": max(p[1] for p in pts),
                "zmin": min(p[2] for p in pts),
                "zmax": max(p[2] for p in pts),
            }
        )
    return boxes


def load_objects() -> dict:
    s = json.loads((ROOT / "audit" / "t73_s_standard_spheres.json").read_text(encoding="utf-8"))
    c1 = json.loads((ROOT / "audit" / "t73_c1_cut_link.json").read_text(encoding="utf-8"))
    c2 = json.loads((ROOT / "audit" / "t73_c2_comparison.json").read_text(encoding="utf-8"))
    ball = s["model_ball"]["bounds"]
    return {
        "ball": ball,
        "spheres": [item["box"] for item in s["spheres"]],
        "sphere_names": [item["name"] for item in s["spheres"]],
        "loops": [item["dual_loop"]["chart_arc_boxes"] for item in s["spheres"]],
        "handles": s["one_handles"],
        "c2_left": c2["action_squares"]["left"]["support"]["bounds"],
        "c2_right": c2["action_squares"]["right"]["support"]["bounds"],
        "leftovers": leftover_boxes(c1),
        "leftover_count": len(c1["circles"]),
    }


def plot_near(obj: dict, path: Path) -> None:
    fig = plt.figure(figsize=(8.2, 6.4))
    ax = fig.add_subplot(111, projection="3d")
    shade_cube(ax, obj["ball"], "#4C78A8", 0.12)
    draw_cube(ax, obj["ball"], "#4C78A8", 1.4)
    shade_cube(ax, obj["c2_left"], "#F58518", 0.35)
    draw_cube(ax, obj["c2_left"], "#F58518", 1.6)
    shade_cube(ax, obj["c2_right"], "#F58518", 0.35)
    draw_cube(ax, obj["c2_right"], "#F58518", 1.6)
    xs, ys, zs = [], [], []
    for box in obj["leftovers"]:
        c = box_center(box)
        xs.append(c[0])
        ys.append(c[1])
        zs.append(c[2])
    ax.scatter(xs, ys, zs, s=8, c="#54A24B", depthshade=False, label="227 条剩余 z-圆")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("P0 立方体近角（整体延伸到 y=4401，z=45361）")
    ax.set_xlim(-30, 70)
    ax.set_ylim(-20, 25)
    ax.set_zlim(-25, 20)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_far(obj: dict, path: Path) -> None:
    fig = plt.figure(figsize=(8.2, 6.4))
    ax = fig.add_subplot(111, projection="3d")
    colors = ["#E45756", "#72B7B2", "#B279A2"]
    boxes = []
    for name, box, color, loop, handle in zip(
        obj["sphere_names"], obj["spheres"], colors, obj["loops"], obj["handles"]
    ):
        shade_cube(ax, box, color, 0.28)
        draw_cube(ax, box, color, 1.8)
        for foot in handle["feet"]:
            draw_cube(ax, foot["bounds"], color, 0.9)
            boxes.append(foot["bounds"])
        pts = [box_center(item) for item in loop]
        ax.plot(
            [p[0] for p in pts],
            [p[1] for p in pts],
            [p[2] for p in pts],
            color=color,
            lw=1.6,
            label=f"{name} 图卡回路",
        )
        boxes.append(box)
        boxes.extend(loop)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("远场：腰带立方体、1-把手脚、对偶环图卡回路")
    set_equal_3d(ax, boxes, pad=6)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_slices(obj: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.2))
    ax = axes[0]
    ball = obj["ball"]
    ax.add_patch(
        Rectangle(
            (ball["xmin"], ball["ymin"]),
            ball["xmax"] - ball["xmin"],
            min(40, ball["ymax"] - ball["ymin"]),
            fill=False,
            ec="#4C78A8",
            lw=1.6,
            label="P0 立方体（y 已裁切，实际到 4401）",
        )
    )
    for name, box, color in (
        ("C2 左侧", obj["c2_left"], "#F58518"),
        ("C2 右侧", obj["c2_right"], "#F58518"),
    ):
        ax.add_patch(
            Rectangle(
                (box["xmin"], box["ymin"]),
                box["xmax"] - box["xmin"],
                box["ymax"] - box["ymin"],
                facecolor=color,
                alpha=0.45,
                ec=color,
                label=name,
            )
        )
    xs = [box_center(b)[0] for b in obj["leftovers"]]
    ys = [box_center(b)[1] for b in obj["leftovers"]]
    ax.scatter(xs, ys, s=10, c="#54A24B", label=f"{obj['leftover_count']} 条剩余圆")
    ax.set_xlim(-30, 72)
    ax.set_ylim(-16, 28)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("z ≈ 0 附近的 xy 切片（原点角）")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.25)

    ax = axes[1]
    colors = ["#E45756", "#72B7B2", "#B279A2"]
    for name, box, color in zip(obj["sphere_names"], obj["spheres"], colors):
        ax.add_patch(
            Rectangle(
                (box["xmin"], box["ymin"]),
                box["xmax"] - box["xmin"],
                box["ymax"] - box["ymin"],
                facecolor=color,
                alpha=0.5,
                ec=color,
                label=name,
            )
        )
        ax.text(box["xmin"] + 0.15, box["ymax"] + 0.45, name, color=color, fontsize=9)
    ax.set_xlim(60, 102)
    ax.set_ylim(4436, 4448)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("z = 45402 处的 xy 切片（腰带立方体）")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.25)
    fig.suptitle("Johnson 替换的 PL 对象，证书坐标")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.88, bottom=0.12, wspace=0.28)
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_strand_slice(path: Path, sample_z: int = 2000) -> None:
    reconstructor = load_script("reconstruct_t73_p0")
    control = load_script("generate_t73_target_braid_control")
    collar = control.control_collar(reconstructor)
    fig, ax = plt.subplots(figsize=(8.0, 5.6))
    for strand in collar["strands"]:
        verts = strand["vertices"]
        chosen = None
        best = 10**9
        for point in verts[::80]:
            dist = abs(point[2] - sample_z)
            if dist < best:
                best = dist
                chosen = point
        if chosen is None:
            continue
        ax.scatter([chosen[0]], [chosen[1]], s=18, c="#4C78A8")
        ax.annotate(str(strand["id"]), (chosen[0], chosen[1]), fontsize=7, color="#4C78A8")
    ax.set_xlabel("x（辫次序）")
    ax.set_ylabel("y（上跨/下穿 + 休息高度）")
    ax.set_title(f"44 股在 z ≈ {sample_z} 处的 xy 采样")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-strands", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    obj = load_objects()
    plot_near(obj, OUT / "near_field_3d.png")
    plot_far(obj, OUT / "far_field_3d.png")
    plot_slices(obj, OUT / "xy_slices.png")
    if not args.skip_strands:
        plot_strand_slice(OUT / "strand_xy_sample.png")
    print(f"WROTE={OUT}")
    for item in sorted(OUT.glob("*.png")):
        print(item.name)


if __name__ == "__main__":
    main()
