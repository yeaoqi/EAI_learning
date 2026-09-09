"""Week 4 E5: visualize a two-level SE(3) transform chain.

Convention:
    T_ab maps coordinates in frame {B} to coordinates in frame {A}.
    Therefore T_wb = T_wa @ T_ab for a B -> A -> W chain.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from E3 import compose_transforms, make_transform, transform_points
from E4 import so3_exp


def _random_transform(rng: np.random.Generator) -> np.ndarray:
    rotation_vector = rng.normal(size=3)
    rotation_vector *= rng.uniform(0.2, 1.2) / np.linalg.norm(rotation_vector)
    translation = rng.uniform(-1.0, 1.0, size=3)
    return make_transform(so3_exp(rotation_vector), translation)


def _set_equal_axes(axis, points: list[np.ndarray], padding: float = 0.4) -> None:
    stacked = np.vstack(points)
    lower = stacked.min(axis=0)
    upper = stacked.max(axis=0)
    center = (lower + upper) / 2.0
    radius = max(float(np.max(upper - lower)) / 2.0, 1.0) + padding
    axis.set_xlim(center[0] - radius, center[0] + radius)
    axis.set_ylim(center[1] - radius, center[1] + radius)
    axis.set_zlim(center[2] - radius, center[2] + radius)
    axis.set_box_aspect((1.0, 1.0, 1.0))


def _draw_frame(axis, transform: np.ndarray, name: str, length: float = 0.45) -> None:
    origin = transform[:3, 3]
    directions = transform[:3, :3]
    colors = ("tab:red", "tab:green", "tab:blue")
    labels = ("x", "y", "z")

    axis.scatter(*origin, color="black", s=24)
    axis.text(*origin, f"  {name}", color="black")
    for index, (color, label) in enumerate(zip(colors, labels)):
        direction = length * directions[:, index]
        axis.quiver(
            *origin,
            *direction,
            color=color,
            linewidth=2.0,
            arrow_length_ratio=0.18,
        )
        axis.text(
            *(origin + direction),
            f"{label}_{name}",
            color=color,
            fontsize=9,
        )


def run_experiment(seed: int = 42) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    identity = np.eye(4)

    transform_wa = _random_transform(rng)
    transform_ab = _random_transform(rng)
    transform_wb = compose_transforms(transform_wa, transform_ab)
    point_b = rng.uniform(-0.6, 0.6, size=3)

    point_a = transform_points(transform_ab, point_b)
    point_w_sequential = transform_points(transform_wa, point_a)
    point_w_composed = transform_points(transform_wb, point_b)

    # Matrix multiplication is not commutative. The reversed product is
    # intentionally calculated only as a numerical comparison.
    wrong_order = transform_ab @ transform_wa
    noncommutativity_error = float(np.max(np.abs(transform_wb - wrong_order)))
    chain_error = float(np.max(np.abs(point_w_sequential - point_w_composed)))
    inverse_error = float(
        np.max(np.abs(transform_wb @ np.linalg.inv(transform_wb) - identity))
    )

    if chain_error > 1e-10:
        raise AssertionError("sequential and composed transforms disagree")
    if noncommutativity_error <= 1e-8:
        raise AssertionError("random transform pair was accidentally commutative")

    return {
        "seed": seed,
        "T_wa": transform_wa,
        "T_ab": transform_ab,
        "T_wb": transform_wb,
        "T_wrong_order": wrong_order,
        "point_b": point_b,
        "point_a": point_a,
        "point_w_sequential": point_w_sequential,
        "point_w_composed": point_w_composed,
        "chain_max_abs_error": chain_error,
        "inverse_max_abs_error": inverse_error,
        "noncommutativity_max_abs_difference": noncommutativity_error,
    }


def save_parameters(result: dict[str, object], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    serializable = {}
    for key, value in result.items():
        serializable[key] = value.tolist() if isinstance(value, np.ndarray) else value
    output.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    return output


def plot_experiment(result: dict[str, object], output_path: str | Path) -> Path:
    import matplotlib.pyplot as plt

    transform_wa = np.asarray(result["T_wa"])
    transform_wb = np.asarray(result["T_wb"])
    point_b = np.asarray(result["point_b"])
    point_a = np.asarray(result["point_a"])
    point_world = np.asarray(result["point_w_composed"])

    figure = plt.figure(figsize=(9, 7))
    axis = figure.add_subplot(111, projection="3d")
    axis.set_title("SE(3) coordinate transform: B -> A -> W")
    axis.set_xlabel("X")
    axis.set_ylabel("Y")
    axis.set_zlabel("Z")

    world = np.eye(4)
    _draw_frame(axis, world, "W")
    _draw_frame(axis, transform_wa, "A")
    _draw_frame(axis, transform_wb, "B")

    axis.scatter(
        *point_world,
        color="darkorange",
        s=70,
        marker="o",
        label="same point in W",
    )
    axis.text(
        *point_world,
        "  p_W=" + np.array2string(point_world, precision=2),
        color="darkorange",
    )
    axis.plot(
        [transform_wb[0, 3], point_world[0]],
        [transform_wb[1, 3], point_world[1]],
        [transform_wb[2, 3], point_world[2]],
        linestyle="--",
        color="darkorange",
        alpha=0.7,
    )

    text = (
        "p_B = " + np.array2string(point_b, precision=3) + "\n"
        "p_A = " + np.array2string(point_a, precision=3) + "\n"
        "p_W = " + np.array2string(point_world, precision=3) + "\n"
        f"chain error = {result['chain_max_abs_error']:.2e}\n"
        f"wrong-order diff = {result['noncommutativity_max_abs_difference']:.2e}"
    )
    axis.text2D(
        0.02,
        0.97,
        text,
        transform=axis.transAxes,
        verticalalignment="top",
        family="monospace",
        bbox={"facecolor": "white", "alpha": 0.8},
    )
    axis.legend(loc="lower left")

    origins_and_point = [
        np.zeros(3),
        transform_wa[:3, 3],
        transform_wb[:3, 3],
        point_world,
    ]
    _set_equal_axes(axis, origins_and_point)
    figure.tight_layout()

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "e5-coordinate-transforms.png",
    )
    parser.add_argument(
        "--params",
        type=Path,
        default=Path(__file__).resolve().parent / "e5-coordinate-transforms.json",
    )
    args = parser.parse_args()

    result = run_experiment(seed=args.seed)
    image_path = plot_experiment(result, args.out)
    params_path = save_parameters(result, args.params)

    print(f"image={image_path}")
    print(f"params={params_path}")
    print(f"chain_max_abs_error={result['chain_max_abs_error']}")
    print(f"inverse_max_abs_error={result['inverse_max_abs_error']}")
    print(
        "noncommutativity_max_abs_difference="
        f"{result['noncommutativity_max_abs_difference']}"
    )


if __name__ == "__main__":
    main()
