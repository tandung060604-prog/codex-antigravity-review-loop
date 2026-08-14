import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryStructureTests(unittest.TestCase):
    def test_repository_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_repo.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_daily_snapshot_is_read_only_and_usable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "daily_snapshot.py"), str(ROOT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("BRANCH:", result.stdout)
        self.assertIn("STATE_FILES:", result.stdout)


if __name__ == "__main__":
    unittest.main()
