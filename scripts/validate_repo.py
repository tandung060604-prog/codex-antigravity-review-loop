"""Validate the installable skill and repository contract without third-party packages."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "agy-review-loop"


def fail(message: str) -> None:
    raise SystemExit(f"validation failed: {message}")


def main() -> int:
    required = [
        SKILL / "SKILL.md",
        SKILL / "agents" / "openai.yaml",
        SKILL / "references" / "integrations.md",
        SKILL / "references" / "van-hanh-hang-ngay.md",
        SKILL / "references" / "chi-phi-va-rui-ro.md",
        SKILL / "references" / "routing-and-escalation.md",
        SKILL / "assets" / "agy-result.schema.json",
        SKILL / "assets" / "routing-policy.json",
        SKILL / "scripts" / "agy_round.py",
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CONTRIBUTING.md",
        ROOT / "SECURITY.md",
        ROOT / "docs" / "van-hanh-hang-ngay.md",
        ROOT / "docs" / "chi-phi-va-rui-ro.md",
        ROOT / "scripts" / "daily_snapshot.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if len(text.splitlines()) > 500:
        fail("SKILL.md must stay under 500 lines")
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        fail("SKILL.md frontmatter is not closed")
    frontmatter = parts[1]
    if not re.search(r"^name:\s*agy-review-loop\s*$", frontmatter, re.MULTILINE):
        fail("frontmatter name must be agy-review-loop")
    if not re.search(r"^description:\s*.+$", frontmatter, re.MULTILINE):
        fail("frontmatter description is required")
    if (SKILL / "README.md").exists():
        fail("keep user-facing README at repository root, not inside the skill")
    for marker in ("## Daily reconciliation (on demand)", "## Cost controls"):
        if marker not in text:
            fail(f"SKILL.md is missing {marker}")
    for marker in ("stream-json", "routing-and-escalation.md", "agy_round.py"):
        if marker not in text:
            fail(f"SKILL.md is missing structured protocol marker: {marker}")

    yaml = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for marker in ("display_name:", "short_description:", "default_prompt:", "allow_implicit_invocation: true"):
        if marker not in yaml:
            fail(f"openai.yaml is missing {marker}")

    print("repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
