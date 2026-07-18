import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "sync" / "environment.py"
)
SPEC = importlib.util.spec_from_file_location("sync_environment", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
SYNC_ENVIRONMENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC_ENVIRONMENT)


class FindRepoRootTests(unittest.TestCase):
    def test_finds_nearest_ancestor_with_repository_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "Justfile").touch()
            for directory in ("configs", "skills", "memory"):
                (root / directory).mkdir()
            nested = root / "scripts" / "sync"
            nested.mkdir(parents=True)

            self.assertEqual(SYNC_ENVIRONMENT.find_repo_root(nested), root)

    def test_rejects_directory_without_repository_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(RuntimeError, "Repository root not found"):
                SYNC_ENVIRONMENT.find_repo_root(Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
