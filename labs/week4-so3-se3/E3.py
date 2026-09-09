"""Week 4 E3: SE(3) transforms and property tests.

Convention:
    T_ab maps coordinates expressed in frame {B} to coordinates in frame {A}.
    Points are column vectors, so a chain is T_ab @ T_bc.
"""

from __future__ import annotations

import argparse

import numpy as np

from E1 import project_to_so3, is_rotation_matrix


_ATOL = 1e-9


def _as_float_array(value: object, shape: tuple[int, ...], name: str) -> np.ndarray:
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain numeric values") from exc
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def _validate_transform(transform: object, name: str = "transform") -> np.ndarray:
    matrix = _as_float_array(transform, (4, 4), name)
    if not is_rotation_matrix(matrix[:3, :3], atol=1e-8):
        raise ValueError(f"{name} has an invalid rotation block")
    if not np.allclose(matrix[3], [0.0, 0.0, 0.0, 1.0], atol=1e-8):
        raise ValueError(f"{name} must have homogeneous bottom row [0, 0, 0, 1]")
    return matrix


def make_transform(rotation: object, translation: object) -> np.ndarray:
    """Construct a homogeneous transform from SO(3) rotation and translation."""
    rotation_array = _as_float_array(rotation, (3, 3), "rotation")
    translation_array = _as_float_array(translation, (3,), "translation")
    if not is_rotation_matrix(rotation_array, atol=1e-8):
        raise ValueError("rotation must be a valid SO(3) matrix")

    transform = np.eye(4)
    transform[:3, :3] = rotation_array
    transform[:3, 3] = translation_array
    return transform


def inverse_transform(transform: object) -> np.ndarray:
    """Return the inverse of a homogeneous rigid-body transform."""
    matrix = _validate_transform(transform)
    rotation = matrix[:3, :3]
    translation = matrix[:3, 3]

    inverse = np.eye(4)
    inverse[:3, :3] = rotation.T
    inverse[:3, 3] = -rotation.T @ translation
    return inverse


def transform_points(transform: object, points: object) -> np.ndarray:
    """Transform one point (3,) or a batch of points (N, 3)."""
    matrix = _validate_transform(transform)
    point_array = np.asarray(points, dtype=float)
    if point_array.ndim == 1 and point_array.shape == (3,):
        if not np.all(np.isfinite(point_array)):
            raise ValueError("points must contain only finite values")
        return matrix[:3, :3] @ point_array + matrix[:3, 3]

    if point_array.ndim == 2 and point_array.shape[1] == 3:
        if not np.all(np.isfinite(point_array)):
            raise ValueError("points must contain only finite values")
        return point_array @ matrix[:3, :3].T + matrix[:3, 3]

    raise ValueError("points must have shape (3,) or (N, 3)")


def compose_transforms(transform_ab: object, transform_bc: object) -> np.ndarray:
    """Compose T_ab and T_bc to obtain T_ac = T_ab @ T_bc."""
    first = _validate_transform(transform_ab, "transform_ab")
    second = _validate_transform(transform_bc, "transform_bc")
    return first @ second


def _random_transform(rng: np.random.Generator) -> np.ndarray:
    rotation = project_to_so3(rng.normal(size=(3, 3)))
    translation = rng.normal(size=3)
    return make_transform(rotation, translation)


def run_tests(seed: int = 42, samples: int = 1000) -> dict[str, float | int]:
    """Run reproducible single-point, batch, inverse, and composition tests."""
    if samples <= 0:
        raise ValueError("samples must be positive")

    rng = np.random.default_rng(seed)
    identity = np.eye(4)
    max_inverse_error = 0.0
    max_single_batch_error = 0.0
    max_composition_error = 0.0
    max_round_trip_point_error = 0.0

    for _ in range(samples):
        transform_ab = _random_transform(rng)
        transform_bc = _random_transform(rng)
        point = rng.normal(size=3)
        points = rng.normal(size=(rng.integers(1, 20), 3))

        inverse = inverse_transform(transform_ab)
        max_inverse_error = max(
            max_inverse_error,
            float(np.max(np.abs(transform_ab @ inverse - identity))),
            float(np.max(np.abs(inverse @ transform_ab - identity))),
        )

        single_result = transform_points(transform_ab, point)
        batch_result = transform_points(transform_ab, points)
        max_single_batch_error = max(
            max_single_batch_error,
            float(
                np.max(
                    np.abs(
                        single_result
                        - transform_points(transform_ab, point.reshape(1, 3))[0]
                    )
                )
            ),
        )

        composed = compose_transforms(transform_ab, transform_bc)
        sequential_result = transform_points(
            transform_ab,
            transform_points(transform_bc, points),
        )
        composed_result = transform_points(composed, points)
        max_composition_error = max(
            max_composition_error,
            float(np.max(np.abs(sequential_result - composed_result))),
        )

        round_trip = transform_points(inverse, single_result)
        max_round_trip_point_error = max(
            max_round_trip_point_error,
            float(np.max(np.abs(round_trip - point))),
        )

    assert np.allclose(
        transform_points(np.eye(4), np.array([1.0, 2.0, 3.0])),
        [1.0, 2.0, 3.0],
        atol=_ATOL,
    )

    try:
        make_transform(np.eye(2), [0.0, 0.0, 0.0])
    except ValueError:
        pass
    else:
        raise AssertionError("invalid rotation shape was accepted")

    try:
        transform_points(np.eye(4), np.ones(4))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid point shape was accepted")

    return {
        "seed": seed,
        "samples": samples,
        "max_inverse_matrix_error": max_inverse_error,
        "max_single_batch_point_error": max_single_batch_error,
        "max_composition_point_error": max_composition_error,
        "max_round_trip_point_error": max_round_trip_point_error,
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
