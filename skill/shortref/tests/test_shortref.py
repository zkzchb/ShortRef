import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "shortref.py"
spec = importlib.util.spec_from_file_location("shortref", MODULE_PATH)
shortref = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(shortref)


class ShortRefTests(unittest.TestCase):
    def test_normalize_url(self):
        self.assertEqual(
            shortref.normalize_url(" HTTPS://Example.COM:443/docs?q=1 "),
            "https://example.com/docs?q=1",
        )
        self.assertEqual(shortref.normalize_url("https://example.com"), "https://example.com/")

    def test_rejects_unsafe_urls(self):
        for value in ("javascript:alert(1)", "https://user:pass@example.com/"):
            with self.assertRaises(shortref.ShortRefError):
                shortref.normalize_url(value)

    def test_hash_is_deterministic(self):
        url = shortref.normalize_url("https://example.com/docs")
        token = shortref.hash_token(url)
        self.assertEqual(len(token), 43)
        self.assertEqual(token, shortref.hash_token(url))
        self.assertRegex(token[:8], r"^[0-9A-Za-z]{8}$")

    def test_remote_payload_excludes_private_metadata(self):
        record = {
            "target_url": "https://example.com/docs",
            "status": "active",
            "title": "Private title",
            "notes": "Private notes",
        }
        self.assertEqual(
            shortref.remote_payload(record),
            {"version": 1, "url": "https://example.com/docs", "status": "active"},
        )

    def test_relative_data_dir_is_resolved_from_config(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps({
                    "base_url": "https://reference.gany.app",
                    "data_dir": "private-data",
                    "cloudflare": {"account_id": "x", "namespace_id": "y"},
                }),
                encoding="utf-8",
            )
            config, _ = shortref.load_config(str(config_path))
            self.assertEqual(Path(config["data_dir"]), root / "private-data")

    def test_markdown_contains_private_context(self):
        record = {
            "id": "Ab12Cd34",
            "short_url": "https://reference.gany.app/Ab12Cd34",
            "source_url": "https://example.com/old",
            "target_url": "https://example.com/new",
            "status": "active",
            "title": "Internal notes",
            "project": "Demo",
            "tags": ["docs"],
            "notes": "Keep this local",
            "created_at": "2026-08-03T00:00:00Z",
            "updated_at": "2026-08-03T00:00:00Z",
            "history": [{"at": "2026-08-03T00:00:00Z", "action": "created"}],
        }
        rendered = shortref.markdown(record)
        self.assertIn("Keep this local", rendered)
        self.assertIn("target_url", rendered)


if __name__ == "__main__":
    unittest.main()
