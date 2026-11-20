"""Hardware-free duration regressions for the Phase 5 ten-minute protocol."""
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from training.holistic_migration import camera


class ReachedSpawn(Exception):
    pass


def test_ten_minute_duration_reaches_owned_spawn_without_opening_camera():
    binding = type("Binding", (), {"binary": Path("/not-used")})()
    seen = []

    def spawn(command, **kwargs):
        seen.append(command)
        raise ReachedSpawn()

    with patch.object(camera, "verify_binding"), pytest.raises(ReachedSpawn):
        camera.OwnedCapture(binding, duration=600, popen=spawn)
    assert seen == [["/not-used", "--capture", "600"]]


@pytest.mark.parametrize("duration", [True, False, 0, -1, float("nan"), float("inf"), 900.001])
def test_invalid_duration_rejected_before_binding_or_spawn(duration):
    def forbidden(*args, **kwargs):
        pytest.fail("invalid duration reached binding or spawn")

    with patch.object(camera, "verify_binding", forbidden), pytest.raises(ValueError):
        camera.OwnedCapture(None, duration=duration, popen=forbidden)


def test_native_duration_check_is_pure_and_accepts_ten_minutes(tmp_path):
    binding = camera.build_helper(tmp_path)
    camera.verify_binding(binding)
    for value in ("600", "900", "0.001"):
        completed = subprocess.run([str(binding.binary), "--check-duration", value],
                                   capture_output=True, timeout=10, check=True)
        assert json.loads(completed.stdout) == {
            "camera_access": False, "duration_s": float(value), "status": "ok"}
    for value in ("nan", "inf", "0", "-1", "900.001", "bad"):
        completed = subprocess.run([str(binding.binary), "--check-duration", value],
                                   capture_output=True, timeout=10, check=False)
        assert completed.returncode != 0
        assert completed.stdout == b""
        assert b"invalid-duration" in completed.stderr
