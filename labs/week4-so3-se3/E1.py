"""Week 4 E1: SO(3) basic utilities and property tests."""

from __future__ import annotations

import argparse

import numpy as np


def _as_float_array(value: object, shape: tuple[int, ...], name: str) -> np.ndarray:
    """Convert an input to a finite float array with the required shape."""
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain numeric values") from exc

    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def skew(vector: object) -> np.ndarray:
    """Return the 3x3 skew-symmetric matrix for a 3-vector."""
    v = _as_float_array(vector, (3,), "vector")
    return np.array(
        [
            [0.0, -v[2], v[1]],
            [v[2], 0.0, -v[0]],
            [-v[1], v[0], 0.0],
        ]
    )


def project_to_so3(matrix: object) -> np.ndarray:
    """Project a finite 3x3 matrix to the nearest proper rotation matrix."""
    matrix_array = _as_float_array(matrix, (3, 3), "matrix")
    u, _, vt = np.linalg.svd(matrix_array)
    rotation = u @ vt

    # SVD can produce an orthogonal reflection. Flip one singular direction
    # so the result has determinant +1 and therefore belongs to SO(3).
    if np.linalg.det(rotation) < 0.0:
        u[:, -1] *= -1.0
        rotation = u @ vt

    return rotation


def is_rotation_matrix(matrix: object, atol: float = 1e-9) -> bool:
    """Return whether matrix is a finite 3x3 element of SO(3)."""
    if not np.isfinite(atol) or atol < 0.0:
        raise ValueError("atol must be a finite non-negative number")

    try:
        matrix_array = np.asarray(matrix, dtype=float)
    except (TypeError, ValueError):
        return False

    if matrix_array.shape != (3, 3) or not np.all(np.isfinite(matrix_array)):
        return False

    orthogonality_error = np.max(
        np.abs(matrix_array.T @ matrix_array - np.eye(3))
    )
    determinant_error = abs(np.linalg.det(matrix_array) - 1.0)
    return bool(
        orthogonality_error <= atol and determinant_error <= atol
    )


def _random_rotation(rng: np.random.Generator) -> np.ndarray:
    """Generate a reproducible random proper rotation."""
    return project_to_so3(rng.normal(size=(3, 3)))


def run_tests(seed: int = 42, samples: int = 1000) -> dict[str, float | int]:
    """Run E1 property tests and return the largest observed errors."""
    if samples <= 0:
        raise ValueError("samples must be positive")

    rng = np.random.default_rng(seed)
    identity = np.eye(3)
    max_orthogonality_error = 0.0
    max_determinant_error = 0.0
    max_inverse_error = 0.0
    max_projection_orthogonality_error = 0.0
    max_projection_determinant_error = 0.0

    for _ in range(samples):
        rotation = _random_rotation(rng)
        noisy_rotation = rotation + 1e-3 * rng.normal(size=(3, 3))
        projected_rotation = project_to_so3(noisy_rotation)

        for candidate in (rotation, projected_rotation):
            orthogonality_error = np.max(
                np.abs(candidate.T @ candidate - identity)
            )
            determinant_error = abs(np.linalg.det(candidate) - 1.0)
            inverse_error = np.max(np.abs(np.linalg.inv(candidate) - candidate.T))

            max_orthogonality_error = max(
                max_orthogonality_error, float(orthogonality_error)
            )
            max_determinant_error = max(
                max_determinant_error, float(determinant_error)
            )
            max_inverse_error = max(max_inverse_error, float(inverse_error))

        max_projection_orthogonality_error = max(
            max_projection_orthogonality_error,
            float(np.max(np.abs(projected_rotation.T @ projected_rotation - identity))),
        )
        max_projection_determinant_error = max(
            max_projection_determinant_error,
            float(abs(np.linalg.det(projected_rotation) - 1.0)),
        )

    assert np.allclose(skew([1.0, 2.0, 3.0]).T, -skew([1.0, 2.0, 3.0]))
    assert not is_rotation_matrix(np.zeros((2, 2)))
    assert not is_rotation_matrix([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, np.nan]])
    assert is_rotation_matrix(_random_rotation(rng))

    return {
        "seed": seed,
        "samples": samples,
        "max_orthogonality_error": max_orthogonality_error,
        "max_determinant_error": max_determinant_error,
        "max_inverse_error": max_inverse_error,
        "max_projection_orthogonality_error": max_projection_orthogonality_error,
        "max_projection_determinant_error": max_projection_determinant_error,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--samples", type=int, default=1000)
    args = parser.parse_args()

    result = run_tests(seed=args.seed, samples=args.samples)
    for name, value in result.items():
        print(f"{name}={value}")


if __name__ == "__main__":
    main()
