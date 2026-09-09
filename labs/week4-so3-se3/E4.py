"""Week 4 E4: SO(3) exponential/logarithm maps and numerical tests."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from E1 import is_rotation_matrix, skew


_EPS = 1e-12


def _as_rotation_vector(value: object) -> np.ndarray:
    try:
        vector = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("rotation_vector must contain numeric values") from exc
    if vector.shape != (3,):
        raise ValueError("rotation_vector must have shape (3,)")
    if not np.all(np.isfinite(vector)):
        raise ValueError("rotation_vector must contain only finite values")
    return vector


def _as_rotation_matrix(value: object) -> np.ndarray:
    try:
        matrix = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("rotation must contain numeric values") from exc
    if matrix.shape != (3, 3) or not np.all(np.isfinite(matrix)):
        raise ValueError("rotation must be a finite matrix with shape (3, 3)")
    if not is_rotation_matrix(matrix, atol=1e-8):
        raise ValueError("rotation must be a valid SO(3) matrix")
    return matrix


def so3_exp(rotation_vector: object) -> np.ndarray:
    """Map a rotation vector in R^3 to SO(3) using Rodrigues' formula."""
    phi = _as_rotation_vector(rotation_vector)
    theta = float(np.linalg.norm(phi))
    phi_hat = skew(phi)

    if theta < 1e-4:
        theta_squared = theta * theta
        coefficient_a = (
            1.0
            - theta_squared / 6.0
            + theta_squared * theta_squared / 120.0
        )
        coefficient_b = (
            0.5
            - theta_squared / 24.0
            + theta_squared * theta_squared / 720.0
        )
    else:
        coefficient_a = np.sin(theta) / theta
        coefficient_b = (1.0 - np.cos(theta)) / (theta * theta)

    return np.eye(3) + coefficient_a * phi_hat + coefficient_b * (phi_hat @ phi_hat)


def _axis_near_pi(rotation: np.ndarray) -> np.ndarray:
    diagonal = np.maximum((np.diag(rotation) + 1.0) / 2.0, 0.0)
    index = int(np.argmax(diagonal))
    axis = np.zeros(3)
    axis[index] = np.sqrt(diagonal[index])

    for other in range(3):
        if other != index:
            axis[other] = (
                rotation[index, other] + rotation[other, index]
            ) / (4.0 * axis[index])

    norm = np.linalg.norm(axis)
    if norm <= _EPS:
        raise ValueError("could not recover the rotation axis near pi")
    return axis / norm


def so3_log(rotation: object) -> np.ndarray:
    """Map an SO(3) matrix to its principal rotation vector."""
    matrix = _as_rotation_matrix(rotation)
    skew_vector = np.array(
        [
            matrix[2, 1] - matrix[1, 2],
            matrix[0, 2] - matrix[2, 0],
            matrix[1, 0] - matrix[0, 1],
        ]
    )
    sine = 0.5 * np.linalg.norm(skew_vector)
    cosine = np.clip((np.trace(matrix) - 1.0) / 2.0, -1.0, 1.0)
    theta = float(np.arctan2(sine, cosine))

    if theta < 1e-7:
        # Near zero, sin(theta) is too small for direct division. The
        # first-order approximation is Log(R) vee ~= (R - R.T) vee / 2.
        return 0.5 * skew_vector

    if np.pi - theta < 1e-7:
        return theta * _axis_near_pi(matrix)

    axis = skew_vector / (2.0 * np.sin(theta))
    return theta * axis


def rotation_error(first: np.ndarray, second: np.ndarray) -> float:
    """Return the relative rotation angle between two SO(3) matrices."""
    relative = first.T @ second
    skew_vector = np.array(
        [
            relative[2, 1] - relative[1, 2],
            relative[0, 2] - relative[2, 0],
            relative[1, 0] - relative[0, 1],
        ]
    )
    sine = 0.5 * np.linalg.norm(skew_vector)
    cosine = np.clip((np.trace(relative) - 1.0) / 2.0, -1.0, 1.0)
    return float(np.arctan2(sine, cosine))


def run_tests(seed: int = 42, samples: int = 1000) -> dict[str, float | int]:
    if samples <= 0:
        raise ValueError("samples must be positive")

    rng = np.random.default_rng(seed)
    max_exp_log_matrix_error = 0.0
    max_log_exp_matrix_error = 0.0
    max_small_angle_vector_error = 0.0
    max_pi_case_matrix_error = 0.0

    test_angles = [0.0, 1e-10, 1e-6, 0.5, np.pi - 1e-8, np.pi, np.pi + 0.2]
    for angle in test_angles:
        axis = rng.normal(size=3)
        axis /= np.linalg.norm(axis)
        rotation_vector = angle * axis
        rotation = so3_exp(rotation_vector)

        recovered_vector = so3_log(rotation)
        exp_log_error = rotation_error(so3_exp(recovered_vector), rotation)
        max_exp_log_matrix_error = max(max_exp_log_matrix_error, exp_log_error)

        log_exp_error = rotation_error(so3_exp(so3_log(rotation)), rotation)
        max_log_exp_matrix_error = max(max_log_exp_matrix_error, log_exp_error)

        if angle <= 1e-6:
            max_small_angle_vector_error = max(
                max_small_angle_vector_error,
                float(np.linalg.norm(recovered_vector - rotation_vector)),
            )
        if abs(angle - np.pi) <= 1e-8:
            max_pi_case_matrix_error = max(
                max_pi_case_matrix_error,
                exp_log_error,
            )

    for _ in range(samples):
        axis = rng.normal(size=3)
        axis /= np.linalg.norm(axis)
        angle = rng.uniform(0.0, np.pi)
        rotation_vector = angle * axis
        rotation = so3_exp(rotation_vector)
        recovered_vector = so3_log(rotation)

        max_exp_log_matrix_error = max(
            max_exp_log_matrix_error,
            rotation_error(so3_exp(recovered_vector), rotation),
        )
        max_log_exp_matrix_error = max(
            max_log_exp_matrix_error,
            rotation_error(so3_exp(so3_log(rotation)), rotation),
        )

    assert is_rotation_matrix(so3_exp([0.0, 0.0, 0.0]))
    assert np.allclose(so3_log(np.eye(3)), np.zeros(3), atol=1e-12)

    try:
        so3_log(np.zeros((3, 3)))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid rotation matrix was accepted")

    return {
        "seed": seed,
        "samples": samples,
        "max_exp_log_rotation_error": max_exp_log_matrix_error,
        "max_log_exp_rotation_error": max_log_exp_matrix_error,
        "max_small_angle_vector_error": max_small_angle_vector_error,
        "max_pi_case_rotation_error": max_pi_case_matrix_error,
    }


def plot_error_curve(
    output_path: str | Path,
    points: int = 500,
) -> Path:
    """Plot ||Exp(Log(R(theta))) - R(theta)|| over theta in [0, pi]."""
    if points < 2:
        raise ValueError("points must be at least 2")

    import matplotlib.pyplot as plt

    axis = np.array([1.0, 2.0, 3.0])
    axis /= np.linalg.norm(axis)
    angles = np.linspace(0.0, np.pi, points)
    errors = []
    for angle in angles:
        rotation = so3_exp(angle * axis)
        errors.append(rotation_error(so3_exp(so3_log(rotation)), rotation))

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(figsize=(7, 4))
    axes.plot(angles, errors)
    axes.set_xlabel("rotation angle (rad)")
    axes.set_ylabel("round-trip rotation error (rad)")
    axes.set_title(r"$\mathrm{Exp}(\mathrm{Log}(R))$ round-trip error")
    axes.grid(True, alpha=0.3)
    figure.tight_layout()
    figure.savefig(output, dpi=150)
    plt.close(figure)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--plot", action="store_true")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "e4-exp-log-error.png",
    )
    args = parser.parse_args()

    result = run_tests(seed=args.seed, samples=args.samples)
    for name, value in result.items():
        print(f"{name}={value}")

    if args.plot:
        print(f"plot={plot_error_curve(args.out)}")


if __name__ == "__main__":
    main()
