#!/usr/bin/env python3
"""Master Test Suite — runs all AION OS tests in sequence.

Usage:
    # Local (SQLite)
    AION_TEST_MODE=1 OPENAI_API_KEY=gsk_your_key python test_all.py

    # Docker (PostgreSQL)
    python test_all.py
"""

import asyncio
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

TESTS = [
    ("test_server.py", "REST API endpoints (11 checks)", 30),
    ("test_websocket.py", "WebSocket lifecycle (9 checks)", 30),
    ("test_agents_live.py", "AI Agent pipeline (6 checks)", 90),
]

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header():
    print()
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  AION OS — Master Test Suite{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  AION_TEST_MODE: {os.environ.get('AION_TEST_MODE', 'not set')}")
    print(f"  Groq key: {'✅ configured' if os.environ.get('OPENAI_API_KEY') else '❌ not set'}")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def run_test(name: str, file: str, timeout: int, env: dict | None = None) -> tuple[bool, str]:
    """Run a single test script and return (passed, output).
    Streams output live so the developer sees progress in real-time.
    """
    merge_env = os.environ.copy()
    if env:
        merge_env.update(env)

    print(f"  {YELLOW}▶ Running{RESET} {name}")
    print(f"    File: {file}")
    print(f"    Timeout: {timeout}s")
    print()

    import io
    output_buf = io.StringIO()

    try:
        # Ensure UTF-8 encoding for subprocess output (Windows cp1251 fix)
        merge_env["PYTHONIOENCODING"] = "utf-8"
        process = subprocess.Popen(
            [sys.executable, file],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=merge_env,
            bufsize=1,  # line-buffered
            text=True,
            encoding="utf-8",
        )

        assert process.stdout is not None
        for line in iter(process.stdout.readline, ""):
            output_buf.write(line)
            # Live stream — show important lines
            stripped = line.strip()
            if stripped and any(k in stripped for k in ["PASS", "FAIL", "✅", "❌", "Error", "Traceback", "  ➡", "═══", "Query:", "Agent"]):
                print(f"  {stripped[:120]}", flush=True)

        process.wait(timeout=timeout)
        output = output_buf.getvalue()

        # Check for pass/fail indicators
        if "PASSED" in output or "ALL TEST" in output.upper():
            return True, output
        elif "FAIL" in output.upper() and "PASS" not in output:
            return False, output
        elif process.returncode == 0:
            return True, output
        else:
            return False, output

    except subprocess.TimeoutExpired:
        process.kill()
        return False, output_buf.getvalue() + "\n[TIMEOUT]\n"
    except Exception as e:
        return False, output_buf.getvalue() + f"\n[ERROR] {e}\n"


def print_result(name: str, passed: bool, output: str):
    status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
    print(f"  {status} — {name}")

    if not passed:
        # Show relevant error lines
        lines = output.split("\n")
        error_lines = [l for l in lines if "FAIL" in l or "ERROR" in l or "Error" in l or "Traceback" in l]
        if error_lines:
            print(f"  {RED}Errors:{RESET}")
            for l in error_lines[:5]:
                print(f"    {l[:120]}")
    print()


def main():
    print_header()

    # Check for Groq API key
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"  {YELLOW}⚠ No Groq API key set. Set OPENAI_API_KEY for agent tests.{RESET}")
        print(f"    export OPENAI_API_KEY=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")
        print()

    results = []
    passed_count = 0
    failed_count = 0

    for script_file, display_name, timeout in TESTS:
        passed, output = run_test(display_name, script_file, timeout)
        results.append((display_name, passed, output))
        if passed:
            passed_count += 1
        else:
            failed_count += 1
        print_result(display_name, passed, output)

    # Summary
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Master Test Suite Summary{RESET}")
    print(f"{'='*60}")
    print(f"  Total:  {len(results)}")
    print(f"  {GREEN}Passed: {passed_count}{RESET}")
    print(f"  {RED}Failed: {failed_count}{RESET}")

    if failed_count == 0:
        print(f"\n  {GREEN}{BOLD}✅ ALL TESTS PASSED — Product ready for handoff{RESET}")
    else:
        print(f"\n  {RED}❌ {failed_count} test(s) failed — review errors above{RESET}")

    print()
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
