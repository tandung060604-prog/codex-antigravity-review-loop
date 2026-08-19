import importlib.util
import json
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 local fallback; CI uses 3.11.
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "agy-review-loop"
SCRIPT = SKILL / "scripts" / "agy_round.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("agy_round", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()

    def test_schema_requires_core_fields(self) -> None:
        schema = json.loads((SKILL / "assets" / "agy-result.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(schema["required"]),
            {"status", "changed_files", "checks", "risks", "blocker"},
        )
        self.assertFalse(schema["additionalProperties"])

    def test_routing_policy_is_bounded(self) -> None:
        policy = json.loads((SKILL / "assets" / "routing-policy.json").read_text(encoding="utf-8"))
        self.assertEqual(
            {name: route["max_rounds"] for name, route in policy["classes"].items()},
            {"routine": 2, "standard": 3, "complex": 4, "critical": 5},
        )
        self.assertTrue(policy["pro_requires_user_approval"])

    def test_stream_parser_and_usage_aggregation(self) -> None:
        output = "\n".join(
            [
                json.dumps({"event": "init", "conversation_id": "abc", "init": {"model": "m"}}),
                json.dumps(
                    {
                        "event": "result",
                        "result": {
                            "status": "SUCCESS",
                            "structured_output": {
                                "status": "DONE",
                                "changed_files": [],
                                "checks": [],
                                "risks": [],
                                "blocker": None,
                            },
                            "usage": {"input_tokens": 10, "output_tokens": 2, "total_tokens": 12},
                        },
                    }
                ),
            ]
        )
        events, warnings = self.runner.parse_events(output)
        self.assertEqual(len(events), 2)
        self.assertEqual(warnings, [])
        result = events[-1]["result"]["structured_output"]
        self.assertEqual(self.runner.validate_result(result), [])
        totals = self.runner.aggregate(
            [
                {"model": "m", "usage": {"input_tokens": 10, "output_tokens": 2, "total_tokens": 12}},
                {"model": "m2", "usage": {"input_tokens": 5, "thinking_tokens": 1, "total_tokens": 6}},
            ]
        )
        self.assertEqual(totals["round_count"], 2)
        self.assertEqual(totals["model_sequence"], ["m", "m2"])
        self.assertEqual(totals["usage"]["total_tokens"], 18)

    def test_permission_failure_is_not_reported_as_bad_protocol(self) -> None:
        failure = self.runner.classify_failure(
            1,
            {
                "status": "ERROR",
                "error": 'permission check failed for command "git status": user denied permission',
            },
            "",
        )
        self.assertEqual(failure["kind"], "PERMISSION_BLOCKED")

    def test_fresh_round_gets_an_isolated_project(self) -> None:
        self.assertEqual(self.runner.project_scope_args(None), ["--new-project"])
        self.assertEqual(
            self.runner.project_scope_args("conversation-1"),
            ["--conversation", "conversation-1"],
        )

    def test_codex_templates_are_valid_toml(self) -> None:
        files = list((ROOT / "examples" / "codex-profiles").glob("*.toml"))
        files += list((ROOT / "examples" / "codex-agents").glob("*.toml"))
        self.assertEqual(len(files), 6)
        for path in files:
            with self.subTest(path=path.name):
                if tomllib is not None:
                    with path.open("rb") as handle:
                        tomllib.load(handle)
                else:
                    text = path.read_text(encoding="utf-8")
                    self.assertIn("model = ", text)
                    self.assertEqual(text.count('"""') % 2, 0)


if __name__ == "__main__":
    unittest.main()
