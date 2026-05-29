import os
import stat
import subprocess
import sys


def _run_permissions_check(env_file):
    return subprocess.run(
        [sys.executable, "scripts/check_permissions.py", "--env-file", str(env_file)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_permissions_check_rejects_group_readable_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET_KEY=redacted\n", encoding="utf-8")
    env_file.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)

    result = _run_permissions_check(env_file)

    assert result.returncode == 1
    assert ".env" in result.stderr


def test_permissions_check_accepts_owner_only_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET_KEY=redacted\n", encoding="utf-8")
    env_file.chmod(stat.S_IRUSR | stat.S_IWUSR)

    result = _run_permissions_check(env_file)

    assert result.returncode == 0
    assert "permissions OK" in result.stdout
    assert os.stat(env_file).st_mode & (stat.S_IRWXG | stat.S_IRWXO) == 0
