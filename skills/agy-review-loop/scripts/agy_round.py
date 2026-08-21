"""Run one structured Antigravity round and persist a compact usage summary."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = SKILL_ROOT / "assets" / "routing-policy.json"
DEFAULT_SCHEMA = SKILL_ROOT / "assets" / "agy-result.schema.json"
TASK_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")
DURATION_PART_RE = re.compile(r"(?P<value>\d+(?:\.\d+)?)(?P<unit>[hms])")
USAGE_FIELDS = (
    "input_tokens",
    "output_tokens",
    "thinking_tokens",
    "cache_read_tokens",
    "total_tokens",
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def resolve_agy(explicit: str | None) -> str:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.is_file():
            return str(path)
        raise FileNotFoundError(f"agy executable not found: {path}")
    found = shutil.which("agy")
    if found:
        return found
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidate = Path(local_app_data) / "agy" / "bin" / "agy.exe"
        if candidate.is_file():
            return str(candidate)
    raise FileNotFoundError("agy is not on PATH; pass --agy with the executable path")


def parse_events(stdout: str) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    for number, line in enumerate(stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            warnings.append(f"line {number} was not JSON")
            continue
        if isinstance(value, dict):
            events.append(value)
        else:
            warnings.append(f"line {number} was not a JSON object")
    return events, warnings


def validate_result(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["structured_output is not an object"]
    required = {"status", "changed_files", "checks", "risks", "blocker"}
    missing = sorted(required - set(value))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if value.get("status") not in {"DONE", "BLOCKED"}:
        errors.append("status must be DONE or BLOCKED")
    if not isinstance(value.get("changed_files"), list):
        errors.append("changed_files must be an array")
    if not isinstance(value.get("checks"), list):
        errors.append("checks must be an array")
    if not isinstance(value.get("risks"), list):
        errors.append("risks must be an array")
    if value.get("blocker") is not None and not isinstance(value.get("blocker"), str):
        errors.append("blocker must be a string or null")
    return errors


def classify_failure(returncode: int, result_event: dict[str, Any] | None, stderr: str) -> dict[str, str] | None:
    status = result_event.get("status") if result_event else None
    if returncode == 0 and status != "ERROR":
        return None

    error = result_event.get("error", "") if result_event else ""
    details = f"{error}\n{stderr}".lower()
    if "permission check failed" in details or "user denied permission" in details:
        return {
            "kind": "PERMISSION_BLOCKED",
            "message": "Antigravity could not approve a tool request in non-interactive print mode.",
        }
    if "not logged into antigravity" in details or "authentication required" in details:
        return {
            "kind": "AUTH_REQUIRED",
            "message": "Antigravity authentication is required.",
        }
    if "timed out" in details or "timeout" in details:
        return {
            "kind": "TIMEOUT",
            "message": "Antigravity did not finish before the configured timeout.",
        }
    return {
        "kind": "AGY_RUNTIME_ERROR",
        "message": "Antigravity exited before producing a usable result.",
    }


def project_scope_args(conversation: str | None) -> list[str]:
    return ["--conversation", conversation] if conversation else ["--new-project"]


def parse_duration(value: str) -> float:
    text = value.strip().lower()
    if text.isdigit():
        return float(text)
    matches = list(DURATION_PART_RE.finditer(text))
    if not matches or "".join(match.group(0) for match in matches) != text:
        raise ValueError(f"invalid duration: {value!r} (use e.g. 5m, 30s, or 1m30s)")
    scales = {"h": 3600.0, "m": 60.0, "s": 1.0}
    seconds = sum(float(match.group("value")) * scales[match.group("unit")] for match in matches)
    if seconds <= 0:
        raise ValueError("duration must be greater than zero")
    return seconds


def run_process(
    command: list[str],
    repo: Path,
    host_timeout: float,
    heartbeat_seconds: float,
) -> tuple[int, str, str, bool]:
    process = subprocess.Popen(
        command,
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stop_heartbeat = threading.Event()
    started = time.monotonic()

    def heartbeat() -> None:
        while not stop_heartbeat.wait(heartbeat_seconds):
            if process.poll() is not None:
                return
            elapsed = int(time.monotonic() - started)
            print(f"[agy-review-loop] AGY still running ({elapsed}s elapsed)", file=sys.stderr, flush=True)

    monitor = None
    if heartbeat_seconds > 0:
        monitor = threading.Thread(target=heartbeat, daemon=True)
        monitor.start()
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=host_timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        stdout, stderr = process.communicate()
    finally:
        stop_heartbeat.set()
        if monitor is not None:
            monitor.join(timeout=1)
    return process.returncode, stdout or "", stderr or "", timed_out


def aggregate(rounds: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {field: 0 for field in USAGE_FIELDS}
    models: list[str] = []
    for item in rounds:
        model = item.get("model")
        if isinstance(model, str) and (not models or models[-1] != model):
            models.append(model)
        usage = item.get("usage", {})
        if isinstance(usage, dict):
            for field in USAGE_FIELDS:
                value = usage.get(field, 0)
                if isinstance(value, (int, float)):
                    totals[field] += value
    return {"round_count": len(rounds), "model_sequence": models, "usage": totals}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="target Git repository")
    parser.add_argument("--task-id", required=True, help="safe task identifier")
    parser.add_argument("--round", type=int, required=True, dest="round_number")
    parser.add_argument(
        "--class",
        required=True,
        choices=("routine", "standard", "complex", "critical"),
        dest="task_class",
    )
    parser.add_argument("--prompt-file", required=True, help="UTF-8 prompt file")
    parser.add_argument("--model", help="override AGY model from the routing policy")
    parser.add_argument("--conversation", help="verified conversation ID for this task")
    parser.add_argument("--print-timeout", default="5m")
    parser.add_argument(
        "--host-timeout",
        help="hard host watchdog; defaults to --print-timeout plus 30 seconds",
    )
    parser.add_argument(
        "--heartbeat-seconds",
        type=float,
        default=30.0,
        help="write a liveness heartbeat to stderr (0 disables it)",
    )
    parser.add_argument("--agy", help="path to agy executable")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    parser.add_argument("--metrics-dir", default=".agy-review")
    parser.add_argument("--save-events", action="store_true", help="persist raw JSONL; may contain sensitive data")
    parser.add_argument("--sandbox", action="store_true", help="enable AGY terminal sandbox")
    parser.add_argument("--approve-pro", action="store_true", help="confirm explicit user approval for Gemini Pro")
    parser.add_argument("--force", action="store_true", help="replace an existing record for this round")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not TASK_ID_RE.fullmatch(args.task_id):
        raise SystemExit("task-id must match [A-Za-z0-9][A-Za-z0-9._-]{0,79}")

    repo = Path(args.repo).resolve()
    prompt_path = Path(args.prompt_file).resolve()
    policy = load_json(Path(args.policy).resolve())
    route = policy["classes"][args.task_class]
    max_rounds = int(route["max_rounds"])
    if args.round_number < 1 or args.round_number > max_rounds:
        raise SystemExit(f"round must be between 1 and {max_rounds} for {args.task_class}")
    if not prompt_path.is_file():
        raise SystemExit(f"prompt file not found: {prompt_path}")

    git_check = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if git_check.returncode:
        raise SystemExit(f"not a Git repository: {repo}")

    try:
        print_timeout = parse_duration(args.print_timeout)
        host_timeout = parse_duration(args.host_timeout) if args.host_timeout else print_timeout + 30.0
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if args.heartbeat_seconds < 0:
        raise SystemExit("--heartbeat-seconds cannot be negative")

    model = args.model or route["agy_model"]
    allowed_models = set(policy.get("agy_models", []))
    if model not in allowed_models:
        raise SystemExit(f"model is not allowed by routing policy: {model}")
    if model == "gemini-3.1-pro-high" and policy.get("pro_requires_user_approval", True) and not args.approve_pro:
        raise SystemExit("Gemini Pro requires explicit user approval; pass --approve-pro only after approval")

    task_dir = repo / args.metrics_dir / args.task_id
    summary_path = task_dir / "summary.json"
    existing = load_json(summary_path) if summary_path.is_file() else {"version": 1, "task_id": args.task_id, "rounds": []}
    rounds = existing.get("rounds", [])
    if not isinstance(rounds, list):
        raise SystemExit(f"invalid existing summary: {summary_path}")
    if any(item.get("round") == args.round_number for item in rounds if isinstance(item, dict)) and not args.force:
        raise SystemExit(f"round {args.round_number} already exists; pass --force to replace it")
    if args.conversation:
        known_ids = {
            item.get("conversation_id")
            for item in rounds
            if isinstance(item, dict) and isinstance(item.get("conversation_id"), str)
        }
        if args.conversation not in known_ids:
            raise SystemExit("conversation ID is not owned by an earlier round of this task")

    agy = resolve_agy(args.agy)
    prompt = prompt_path.read_text(encoding="utf-8")
    command = [
        agy,
        *project_scope_args(args.conversation),
        "-p",
        prompt,
        "--mode",
        "accept-edits",
        "--model",
        model,
        "--output-format",
        "stream-json",
        "--json-schema",
        str(Path(args.schema).resolve()),
        "--print-timeout",
        args.print_timeout,
    ]
    if args.sandbox:
        command.append("--sandbox")

    started_at = datetime.now(timezone.utc).isoformat()
    returncode, stdout, stderr, host_timed_out = run_process(
        command,
        repo,
        host_timeout,
        args.heartbeat_seconds,
    )
    finished_at = datetime.now(timezone.utc).isoformat()
    events, warnings = parse_events(stdout)
    result_event = next((item["result"] for item in reversed(events) if item.get("event") == "result" and isinstance(item.get("result"), dict)), None)
    structured_output = result_event.get("structured_output") if result_event else None
    failure = (
        {
            "kind": "TIMEOUT",
            "message": f"Host watchdog stopped Antigravity after {host_timeout:g} seconds.",
        }
        if host_timed_out
        else classify_failure(returncode, result_event, stderr)
    )
    protocol_errors = [] if failure else validate_result(structured_output)

    init_event = next((item.get("init") for item in events if item.get("event") == "init"), None)
    conversation_id = None
    if events and events[0].get("event") == "init":
        conversation_id = events[0].get("conversation_id")
    if not conversation_id and result_event:
        conversation_id = result_event.get("conversation_id")

    usage = result_event.get("usage", {}) if result_event else {}
    record = {
        "round": args.round_number,
        "class": args.task_class,
        "model": model,
        "max_rounds": max_rounds,
        "started_at": started_at,
        "finished_at": finished_at,
        "conversation_id": conversation_id,
        "process_returncode": returncode,
        "agy_status": result_event.get("status") if result_event else "MISSING_RESULT",
        "protocol_status": (
            structured_output.get("status")
            if isinstance(structured_output, dict)
            else "NOT_REACHED" if failure else "INVALID"
        ),
        "failure": failure,
        "review_outcome": "PENDING_CODEX_REVIEW",
        "duration_seconds": result_event.get("duration_seconds") if result_event else None,
        "usage": usage,
        "structured_output": structured_output,
        "warnings": warnings + protocol_errors,
        "raw_events_saved": args.save_events,
        "host_timeout_seconds": host_timeout,
        "heartbeat_seconds": args.heartbeat_seconds,
    }
    if isinstance(init_event, dict) and init_event.get("model") != model:
        record["warnings"].append(f"AGY initialized unexpected model: {init_event.get('model')}")
    if failure:
        record["warnings"].append(failure["message"])
    elif stderr.strip():
        record["warnings"].append("AGY wrote to stderr; inspect the live run output")

    task_dir.mkdir(parents=True, exist_ok=True)
    if args.save_events:
        (task_dir / f"round-{args.round_number}.jsonl").write_text(stdout, encoding="utf-8")
    (task_dir / f"round-{args.round_number}.summary.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    kept_rounds = [item for item in rounds if not isinstance(item, dict) or item.get("round") != args.round_number]
    kept_rounds.append(record)
    kept_rounds.sort(key=lambda item: item.get("round", 0) if isinstance(item, dict) else 0)
    summary = {
        "version": 1,
        "task_id": args.task_id,
        "rounds": kept_rounds,
        "totals": aggregate([item for item in kept_rounds if isinstance(item, dict)]),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False, indent=2))

    if failure or result_event is None:
        return 2
    if protocol_errors:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
