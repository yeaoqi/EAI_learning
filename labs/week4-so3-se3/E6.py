"""Week 4 E6: observe ZYX Euler-angle gimbal lock numerically."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def _rotation_x(angle: float) -> np.ndarray:
    cosine, sine = np.cos(angle), np.sin(angle)
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, cosine, -sine],
            [0.0, sine, cosine],
        ]
    )


def _rotation_y(angle: float) -> np.ndarray:
    cosine, sine = np.cos(angle), np.sin(angle)
    return np.array(
        [
            [cosine, 0.0, sine],
            [0.0, 1.0, 0.0],
            [-sine, 0.0, cosine],
        ]
    )


def _rotation_z(angle: float) -> np.ndarray:
    cosine, sine = np.cos(angle), np.sin(angle)
    return np.array(
        [
            [cosine, -sine, 0.0],
            [sine, cosine, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def euler_zyx_to_matrix(
    yaw: float,
    pitch: float,
    roll: float,
) -> np.ndarray:
    """Convert active ZYX Euler angles to a rotation matrix."""
    return _rotation_z(yaw) @ _rotation_y(pitch) @ _rotation_x(roll)


def matrix_to_euler_zyx(
    rotation: object,
    singularity_tolerance: float = 1e-10,
) -> tuple[float, float, float]:
    """Recover principal ZYX Euler angles from a rotation matrix.

    The returned pitch is in [-pi/2, pi/2]. At gimbal lock, yaw is set to
    zero and roll absorbs the remaining observable combination.
    """
    matrix = np.asarray(rotation, dtype=float)
    if (
        matrix.shape != (3, 3)
        or not np.all(np.isfinite(matrix))
        or not np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-8)
        or not np.isclose(np.linalg.det(matrix), 1.0, atol=1e-8)
    ):
        raise ValueError("rotation must be a valid SO(3) matrix")
    if not np.isfinite(singularity_tolerance) or singularity_tolerance < 0.0:
        raise ValueError("singularity_tolerance must be non-negative and finite")

    sine_pitch = np.clip(-matrix[2, 0], -1.0, 1.0)
    pitch = float(np.arcsin(sine_pitch))
    cosine_pitch = np.sqrt(max(0.0, 1.0 - sine_pitch * sine_pitch))

    if cosine_pitch > singularity_tolerance:
        yaw = float(np.arctan2(matrix[1, 0], matrix[0, 0]))
        roll = float(np.arctan2(matrix[2, 1], matrix[2, 2]))
        return yaw, pitch, roll

    # At pitch=+/-pi/2, yaw and roll are coupled. Set yaw=0 to select
    # one valid representative and recover the observable combination.
    yaw = 0.0
    if sine_pitch > 0.0:
        roll = float(np.arctan2(matrix[0, 1], matrix[0, 2]))
    else:
        roll = float(np.arctan2(-matrix[0, 1], -matrix[0, 2]))
    return yaw, pitch, roll


def _wrap_angle(angle: np.ndarray) -> np.ndarray:
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


def run_experiment(
    yaw_degrees: float = 35.0,
    roll_degrees: float = -25.0,
    start_degrees: float = 80.0,
    end_degrees: float = 100.0,
    samples: int = 401,
) -> dict[str, object]:
    if samples < 3:
        raise ValueError("samples must be at least 3")
    if not all(
        np.isfinite(value)
        for value in (
            yaw_degrees,
            roll_degrees,
            start_degrees,
            end_degrees,
        )
    ):
        raise ValueError("angle parameters must be finite")

    input_pitch_degrees = np.linspace(start_degrees, end_degrees, samples)
    yaw = np.deg2rad(yaw_degrees)
    roll = np.deg2rad(roll_degrees)
    input_angles = np.column_stack(
        [
            np.full(samples, yaw),
            np.deg2rad(input_pitch_degrees),
            np.full(samples, roll),
        ]
    )

    matrices = np.array(
        [
            euler_zyx_to_matrix(yaw_value, pitch_value, roll)
            for yaw_value, pitch_value, _ in input_angles
        ]
    )
    recovered_angles = np.array(
        [matrix_to_euler_zyx(matrix) for matrix in matrices]
    )
    reconstructed_matrices = np.array(
        [
            euler_zyx_to_matrix(yaw_value, pitch_value, roll_value)
            for yaw_value, pitch_value, roll_value in recovered_angles
        ]
    )

    matrix_step_errors = np.max(np.abs(np.diff(matrices, axis=0)), axis=(1, 2))
    reconstruction_errors = np.max(
        np.abs(matrices - reconstructed_matrices),
        axis=(1, 2),
    )
    angle_step_errors = np.max(
        np.abs(_wrap_angle(np.diff(recovered_angles, axis=0))),
        axis=1,
    )

    singular_index = int(np.argmin(np.abs(input_pitch_degrees - 90.0)))
    return {
        "yaw_degrees": yaw_degrees,
        "roll_degrees": roll_degrees,
        "start_pitch_degrees": start_degrees,
        "end_pitch_degrees": end_degrees,
        "samples": samples,
        "input_pitch_degrees": input_pitch_degrees,
        "input_angles_degrees": np.rad2deg(input_angles),
        "recovered_angles_degrees": np.rad2deg(recovered_angles),
        "matrices": matrices,
        "recovered_matrices": reconstructed_matrices,
        "matrix_step_errors": matrix_step_errors,
        "angle_step_errors_degrees": np.rad2deg(angle_step_errors),
        "reconstruction_errors": reconstruction_errors,
        "singular_index": singular_index,
        "max_matrix_step_error": float(np.max(matrix_step_errors)),
        "max_reconstruction_error": float(np.max(reconstruction_errors)),
        "max_recovered_angle_step_degrees": float(np.max(np.rad2deg(angle_step_errors))),
    }


def save_result(result: dict[str, object], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    serializable = {}
    for key, value in result.items():
        serializable[key] = value.tolist() if isinstance(value, np.ndarray) else value
    output.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    return output


def plot_result(result: dict[str, object], output_path: str | Path) -> Path:
    import matplotlib.pyplot as plt

    input_pitch = np.asarray(result["input_pitch_degrees"])
    input_angles = np.asarray(result["input_angles_degrees"])
    recovered_angles = np.asarray(result["recovered_angles_degrees"])
    matrix_step_errors = np.asarray(result["matrix_step_errors"])
    reconstruction_errors = np.asarray(result["reconstruction_errors"])

    figure, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    labels = ("yaw", "pitch", "roll")
    colors = ("tab:blue", "tab:orange", "tab:green")
    for index, (label, color) in enumerate(zip(labels, colors)):
        axes[0].plot(
            input_pitch,
            input_angles[:, index],
            color=color,
            linestyle="--",
            alpha=0.55,
            label=f"input {label}",
        )
        axes[0].plot(
            input_pitch,
            recovered_angles[:, index],
            color=color,
            label=f"recovered {label}",
        )

    for axis in axes:
        axis.axvline(90.0, color="black", linestyle=":", linewidth=1.2)
        axis.grid(True, alpha=0.3)
    axes[0].set_ylabel("angle (deg)")
    axes[0].set_title("ZYX Euler angles across pitch = 90 degrees")
    axes[0].legend(ncol=2, fontsize=9)

    axes[1].plot(
        input_pitch[1:],
        matrix_step_errors,
        label="adjacent matrix max error",
        color="tab:purple",
    )
    axes[1].plot(
        input_pitch,
        reconstruction_errors,
        label="Euler reconstruction max error",
        color="tab:red",
    )
    axes[1].set_yscale("log")
    axes[1].set_xlabel("input pitch (deg)")
    axes[1].set_ylabel("matrix error")
    axes[1].set_title("Rotation matrices stay continuous and reconstruct correctly")
    axes[1].legend(fontsize=9)

    figure.tight_layout()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yaw", type=float, default=35.0)
    parser.add_argument("--roll", type=float, default=-25.0)
    parser.add_argument("--start", type=float, default=80.0)
    parser.add_argument("--end", type=float, default=100.0)
    parser.add_argument("--samples", type=int, default=401)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "e6-gimbal-lock.png",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path(__file__).resolve().parent / "e6-gimbal-lock.json",
    )
    args = parser.parse_args()

    result = run_experiment(
        yaw_degrees=args.yaw,
        roll_degrees=args.roll,
        start_degrees=args.start,
        end_degrees=args.end,
        samples=args.samples,
    )
    image_path = plot_result(result, args.out)
    data_path = save_result(result, args.data)

    print(f"image={image_path}")
    print(f"data={data_path}")
    print(f"max_matrix_step_error={result['max_matrix_step_error']}")
    print(f"max_reconstruction_error={result['max_reconstruction_error']}")
    print(
        "max_recovered_angle_step_degrees="
        f"{result['max_recovered_angle_step_degrees']}"
    )


if __name__ == "__main__":
    main()
