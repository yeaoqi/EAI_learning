"""Week 4 E2: axis-angle, rotation matrix, and quaternion conversions."""

from __future__ import annotations

import argparse

import numpy as np

from E1 import is_rotation_matrix, skew


_EPS = 1e-12


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


def _as_angle(angle: object) -> float:
    array = np.asarray(angle, dtype=float)
    if array.shape != ():
        raise ValueError("angle must be a scalar")
    if not np.isfinite(array):
        raise ValueError("angle must be finite")
    return float(array)


def _check_rotation_matrix(matrix: object) -> np.ndarray:
    rotation = _as_float_array(matrix, (3, 3), "matrix")
    if not is_rotation_matrix(rotation, atol=1e-8):
        raise ValueError("matrix must be a valid SO(3) rotation matrix")
    return rotation


def axis_angle_to_matrix(axis: object, angle: object) -> np.ndarray:
    """Convert an axis and angle to a rotation matrix using Rodrigues' formula."""
    axis_array = _as_float_array(axis, (3,), "axis")
    angle_value = _as_angle(angle)
    axis_norm = np.linalg.norm(axis_array)
    if axis_norm <= _EPS:
        raise ValueError("axis must be non-zero")

    unit_axis = axis_array / axis_norm
    k = skew(unit_axis)
    identity = np.eye(3)
    return identity + np.sin(angle_value) * k + (1.0 - np.cos(angle_value)) * (k @ k)


def _axis_near_pi(rotation: np.ndarray) -> np.ndarray:
    """Recover an axis near pi, where the skew part is close to zero."""
    diagonal = np.maximum((np.diag(rotation) + 1.0) / 2.0, 0.0)
    index = int(np.argmax(diagonal))
    axis = np.zeros(3)
    axis[index] = np.sqrt(diagonal[index])

    if axis[index] > _EPS:
        for other in range(3):
            if other != index:
                axis[other] = (
                    rotation[index, other] + rotation[other, index]
                ) / (4.0 * axis[index])
    else:
        eigenvalues, eigenvectors = np.linalg.eigh(rotation)
        axis = eigenvectors[:, int(np.argmin(np.abs(eigenvalues - 1.0)))]

    axis_norm = np.linalg.norm(axis)
    if axis_norm <= _EPS:
        raise ValueError("could not recover a rotation axis")
    return axis / axis_norm


def matrix_to_axis_angle(matrix: object) -> tuple[np.ndarray, float]:
    """Convert an SO(3) matrix to a unit axis and principal angle in [0, pi]."""
    rotation = _check_rotation_matrix(matrix)
    cosine = np.clip((np.trace(rotation) - 1.0) / 2.0, -1.0, 1.0)
    skew_vector = np.array(
        [
            rotation[2, 1] - rotation[1, 2],
            rotation[0, 2] - rotation[2, 0],
            rotation[1, 0] - rotation[0, 1],
        ]
    )
    sine = 0.5 * np.linalg.norm(skew_vector)
    angle = float(np.arctan2(sine, cosine))

    if angle <= _EPS:
        return np.array([1.0, 0.0, 0.0]), 0.0
    if np.pi - angle <= 1e-7:
        return _axis_near_pi(rotation), angle

    axis = skew_vector / (2.0 * np.sin(angle))
    return axis / np.linalg.norm(axis), angle


def quaternion_to_matrix(quaternion: object) -> np.ndarray:
    """Convert a quaternion in [w, x, y, z] order to SO(3)."""
    q = _as_float_array(quaternion, (4,), "quaternion")
    norm = np.linalg.norm(q)
    if norm <= _EPS:
        raise ValueError("quaternion must be non-zero")
    w, x, y, z = q / norm

    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def _canonicalize_quaternion(quaternion: np.ndarray) -> np.ndarray:
    """Choose one representative from the equivalent pair q and -q."""
    q = quaternion / np.linalg.norm(quaternion)
    if q[0] < 0.0 or (
        np.isclose(q[0], 0.0)
        and q[1 + int(np.argmax(np.abs(q[1:])))] < 0.0
    ):
        q = -q
    return q


def matrix_to_quaternion(matrix: object) -> np.ndarray:
    """Convert an SO(3) matrix to a unit quaternion in [w, x, y, z] order."""
    rotation = _check_rotation_matrix(matrix)
    trace = float(np.trace(rotation))

    if trace > 0.0:
        scale = 2.0 * np.sqrt(trace + 1.0)
        w = 0.25 * scale
        x = (rotation[2, 1] - rotation[1, 2]) / scale
        y = (rotation[0, 2] - rotation[2, 0]) / scale
        z = (rotation[1, 0] - rotation[0, 1]) / scale
    elif rotation[0, 0] > rotation[1, 1] and rotation[0, 0] > rotation[2, 2]:
        scale = 2.0 * np.sqrt(
            max(0.0, 1.0 + rotation[0, 0] - rotation[1, 1] - rotation[2, 2])
        )
        w = (rotation[2, 1] - rotation[1, 2]) / scale
        x = 0.25 * scale
        y = (rotation[0, 1] + rotation[1, 0]) / scale
        z = (rotation[0, 2] + rotation[2, 0]) / scale
    elif rotation[1, 1] > rotation[2, 2]:
        scale = 2.0 * np.sqrt(
            max(0.0, 1.0 + rotation[1, 1] - rotation[0, 0] - rotation[2, 2])
        )
        w = (rotation[0, 2] - rotation[2, 0]) / scale
        x = (rotation[0, 1] + rotation[1, 0]) / scale
        y = 0.25 * scale
        z = (rotation[1, 2] + rotation[2, 1]) / scale
    else:
        scale = 2.0 * np.sqrt(
            max(0.0, 1.0 + rotation[2, 2] - rotation[0, 0] - rotation[1, 1])
        )
        w = (rotation[1, 0] - rotation[0, 1]) / scale
        x = (rotation[0, 2] + rotation[2, 0]) / scale
        y = (rotation[1, 2] + rotation[2, 1]) / scale
        z = 0.25 * scale

    return _canonicalize_quaternion(np.array([w, x, y, z]))


def _random_axis(rng: np.random.Generator) -> np.ndarray:
    axis = rng.normal(size=3)
    return axis / np.linalg.norm(axis)


def _rotation_error(first: np.ndarray, second: np.ndarray) -> float:
    relative = first.T @ second
    cosine = np.clip((np.trace(relative) - 1.0) / 2.0, -1.0, 1.0)
    sine = 0.5 * np.linalg.norm(
        np.array(
            [
                relative[2, 1] - relative[1, 2],
                relative[0, 2] - relative[2, 0],
                relative[1, 0] - relative[0, 1],
            ]
        )
    )
    return float(np.arctan2(sine, cosine))


def run_tests(seed: int = 42, samples: int = 1000) -> dict[str, float | int]:
    if samples <= 0:
        raise ValueError("samples must be positive")

    rng = np.random.default_rng(seed)
    max_axis_angle_error = 0.0
    max_quaternion_error = 0.0
    max_quaternion_round_trip_error = 0.0

    test_angles = [0.0, 1e-10, 0.5, np.pi - 1e-10, np.pi]
    for angle in test_angles:
        axis = _random_axis(rng)
        rotation = axis_angle_to_matrix(axis, angle)
        recovered_axis, recovered_angle = matrix_to_axis_angle(rotation)
        recovered_rotation = axis_angle_to_matrix(recovered_axis, recovered_angle)
        max_axis_angle_error = max(
            max_axis_angle_error,
            _rotation_error(rotation, recovered_rotation),
        )

        quaternion = matrix_to_quaternion(rotation)
        reconstructed = quaternion_to_matrix(quaternion)
        max_quaternion_error = max(
            max_quaternion_error,
            _rotation_error(rotation, reconstructed),
        )

    for _ in range(samples):
        axis = _random_axis(rng)
        angle = rng.uniform(0.0, np.pi)
        rotation = axis_angle_to_matrix(axis, angle)

        recovered_axis, recovered_angle = matrix_to_axis_angle(rotation)
        recovered_rotation = axis_angle_to_matrix(recovered_axis, recovered_angle)
        max_axis_angle_error = max(
            max_axis_angle_error,
            _rotation_error(rotation, recovered_rotation),
        )

        quaternion = matrix_to_quaternion(rotation)
        reconstructed = quaternion_to_matrix(quaternion)
        max_quaternion_error = max(
            max_quaternion_error,
            _rotation_error(rotation, reconstructed),
        )
        round_trip_quaternion = matrix_to_quaternion(reconstructed)
        max_quaternion_round_trip_error = max(
            max_quaternion_round_trip_error,
            1.0 - abs(float(np.dot(quaternion, round_trip_quaternion))),
        )

    assert is_rotation_matrix(axis_angle_to_matrix([1.0, 0.0, 0.0], 0.0))
    assert is_rotation_matrix(quaternion_to_matrix([2.0, 0.0, 0.0, 0.0]))

    for bad_axis in ([0.0, 0.0, 0.0], [1.0, 2.0]):
        try:
            axis_angle_to_matrix(bad_axis, 0.5)
        except ValueError:
            pass
        else:
            raise AssertionError("zero or malformed axis was accepted")

    try:
        quaternion_to_matrix([0.0, 0.0, 0.0, 0.0])
    except ValueError:
        pass
    else:
        raise AssertionError("zero quaternion was accepted")

    return {
        "seed": seed,
        "samples": samples,
        "max_axis_angle_rotation_error": max_axis_angle_error,
        "max_quaternion_rotation_error": max_quaternion_error,
        "max_quaternion_round_trip_error": max_quaternion_round_trip_error,
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
