"""
NOVA Benchmark Suite — v1.0

A simple but real evaluation framework for NOVA. Run this against a live
NOVA server to test core capabilities, log results, and compare runs over
time.

Usage:
    1. Make sure app.py (NOVA) is running on http://127.0.0.1:5001
    2. Run: python3 benchmark.py
    3. Results print to terminal AND save to benchmark_results.json

Each test case has:
    - id: short identifier
    - category: which subsystem this tests (chat, memory, date_time, etc.)
    - message: what to send NOVA
    - check: a function that decides pass/fail given NOVA's reply

This is intentionally simple — automated keyword/pattern checks, not
human judgment. It catches obvious regressions, not subtle quality issues.
Expand the TEST_CASES list over time as you find new things worth checking.
"""

import requests
import json
import time
from datetime import datetime

NOVA_URL = "http://127.0.0.1:5001/chat"


def send_to_nova(message):
    """Send a message to NOVA and return (reply_text, elapsed_seconds, error)."""
    start = time.time()
    try:
        response = requests.post(
            NOVA_URL,
            headers={"Content-Type": "application/json"},
            json={"message": message},
            timeout=120
        )
        elapsed = time.time() - start
        if response.status_code != 200:
            return None, elapsed, "HTTP " + str(response.status_code)
        data = response.json()
        return data.get("reply", ""), elapsed, None
    except requests.exceptions.Timeout:
        return None, time.time() - start, "Timeout (>120s)"
    except Exception as e:
        return None, time.time() - start, str(e)


def reset_nova_memory():
    """Clear NOVA's conversation history before each test so results aren't
    polluted by leftover context (e.g. a previous 'reply in Hindi' instruction
    leaking into later, unrelated tests)."""
    try:
        requests.post(NOVA_URL, headers={"Content-Type": "application/json"},
                      json={"message": "reset memory"}, timeout=10)
    except Exception:
        pass


def contains_any(reply, keywords):
    reply_lower = reply.lower()
    return any(kw.lower() in reply_lower for kw in keywords)


def contains_all(reply, keywords):
    reply_lower = reply.lower()
    return all(kw.lower() in reply_lower for kw in keywords)


def not_contains(reply, keywords):
    reply_lower = reply.lower()
    return not any(kw.lower() in reply_lower for kw in keywords)


TEST_CASES = [
    # --- Basic chat ---
    {
        "id": "chat_01",
        "category": "chat",
        "message": "Hello, how are you?",
        "check": lambda r: len(r) > 0 and not_contains(r, ["error", "sorry, something went wrong"]),
        "description": "Basic greeting should get a friendly, non-error reply"
    },
    {
        "id": "chat_02",
        "category": "chat",
        "message": "What is the capital of France?",
        "check": lambda r: contains_any(r, ["paris"]),
        "description": "Simple factual question should be answered correctly"
    },

    # --- Date/Time (should use Python datetime, not web search) ---
    {
        "id": "datetime_01",
        "category": "date_time",
        "message": "What's today's date?",
        "check": lambda r: contains_any(r, ["today is", "2026"]),
        "description": "Date question should return an actual date, not a vague answer"
    },
    {
        "id": "datetime_02",
        "category": "date_time",
        "message": "What time is it right now?",
        "check": lambda r: contains_any(r, ["am", "pm", "time is"]),
        "description": "Time question should return an actual time"
    },

    # --- Project Memory ---
    {
        "id": "memory_01",
        "category": "project_memory",
        "message": "what are my projects",
        "check": lambda r: len(r) > 0,
        "description": "Should return a project summary (even if empty) without crashing"
    },

    # --- Commands / Tool routing ---
    {
        "id": "tool_01",
        "category": "tool_routing",
        "message": "open calculator",
        "check": lambda r: contains_any(r, ["opening", "calculator"]),
        "description": "Should recognize and confirm an app-opening command"
    },

    # --- Document handling ---
    {
        "id": "doc_01",
        "category": "document",
        "message": "forget the document",
        "check": lambda r: contains_any(r, ["cleared", "document"]),
        "description": "Should confirm clearing document context"
    },

    # --- Creator Mode ---
    {
        "id": "creator_01",
        "category": "creator_mode",
        "message": "give me video ideas for free fire",
        "check": lambda r: len(r) > 200 and contains_any(r, ["video", "idea"]),
        "description": "Should generate substantial, relevant video ideas"
    },

    # --- Multi-step planning ---
    {
        "id": "planning_01",
        "category": "planning",
        "message": "help me start a study routine",
        "check": lambda r: len(r) > 200 and contains_any(r, ["step", "1.", "first"]),
        "description": "Should produce a structured, multi-step plan, not a one-liner"
    },

    # --- Self-correction should NOT misfire on simple casual messages ---
    {
        "id": "selfcorrect_01",
        "category": "self_correction",
        "message": "thanks!",
        "check": lambda r: not_contains(r, ["please ask your question again", "i'm here to help with your question"]),
        "description": "Casual acknowledgment should NOT trigger an unhelpful 'please ask again' fallback"
    },

    # --- Multi-language ---
    {
        "id": "lang_01",
        "category": "multi_language",
        "message": "say hello in hindi",
        "check": lambda r: len(r) > 0,
        "description": "Should attempt to respond, ideally in Hindi script"
    },
    {
        "id": "lang_02",
        "category": "multi_language",
        "message": "tell me a fact about space in kannada",
        "check": lambda r: len(r) > 0,
        "description": "Should attempt to respond in Kannada for a non-trivial request"
    },

    # --- More chat variety (different question types) ---
    {
        "id": "chat_03",
        "category": "chat",
        "message": "What is 15 times 8?",
        "check": lambda r: contains_any(r, ["120"]),
        "description": "Basic arithmetic should be answered correctly"
    },
    {
        "id": "chat_04",
        "category": "chat",
        "message": "Explain what an API is in one sentence",
        "check": lambda r: len(r) > 10 and contains_any(r, ["api", "application", "interface", "request"]),
        "description": "Should give a relevant, on-topic technical explanation"
    },
    {
        "id": "chat_05",
        "category": "chat",
        "message": "asdkjhaskjdh meaningless gibberish test",
        "check": lambda r: len(r) > 0 and not_contains(r, ["sorry, something went wrong"]),
        "description": "Nonsense input should not crash NOVA, should respond gracefully"
    },

    # --- Project memory edge cases ---
    {
        "id": "memory_02",
        "category": "project_memory",
        "message": "my goal is to test the NOVA benchmark suite",
        "check": lambda r: contains_any(r, ["created a new project", "got it"]),
        "description": "Should successfully create a new tracked project from a goal statement"
    },
    {
        "id": "memory_03",
        "category": "project_memory",
        "message": "what are my projects",
        "check": lambda r: len(r) > 0 and not_contains(r, ["sorry, something went wrong"]),
        "description": "Project summary should not crash even with multiple projects tracked"
    },

    # --- Document handling edge cases ---
    {
        "id": "doc_02",
        "category": "document",
        "message": "what does the uploaded document say",
        "check": lambda r: len(r) > 0,
        "description": "Should respond gracefully even when no document was actually uploaded in this test"
    },

    # --- Specialist agent detection ---
    {
        "id": "specialist_01",
        "category": "specialist_agents",
        "message": "I'm getting a syntax error in my python code, what should I check",
        "check": lambda r: contains_any(r, ["syntax", "error", "code", "check", "python"]),
        "description": "Coding question should get a relevant, technically-focused answer"
    },
    {
        "id": "specialist_02",
        "category": "specialist_agents",
        "message": "what subjects should I take for engineering admission in karnataka",
        "check": lambda r: len(r) > 50,
        "description": "Career/college question should get a substantial, relevant answer"
    },

    # --- Self-correction stress tests (should NOT misfire) ---
    {
        "id": "selfcorrect_02",
        "category": "self_correction",
        "message": "ok",
        "check": lambda r: not_contains(r, ["please ask your question again", "i'm here to help with your question"]),
        "description": "Short casual acknowledgment should not trigger a broken retry loop"
    },
    {
        "id": "selfcorrect_03",
        "category": "self_correction",
        "message": "lol nice",
        "check": lambda r: not_contains(r, ["please ask your question again", "i'm here to help with your question"]),
        "description": "Casual slang reply should not be flagged as 'off-topic' and broken"
    },
    {
        "id": "selfcorrect_04",
        "category": "self_correction",
        "message": "What's the boiling point of water in Celsius?",
        "check": lambda r: contains_any(r, ["100"]),
        "description": "Clear factual question should be answered correctly, not flagged unnecessarily"
    },

    # --- Tool routing variety ---
    {
        "id": "tool_02",
        "category": "tool_routing",
        "message": "open notes",
        "check": lambda r: contains_any(r, ["opening", "notes"]),
        "description": "Should recognize a different app-opening command correctly"
    },
    {
        "id": "tool_03",
        "category": "tool_routing",
        "message": "what is the weather like today",
        "check": lambda r: len(r) > 0 and not_contains(r, ["sorry, something went wrong"]),
        "description": "Weather query (no weather tool exists) should still respond gracefully, not crash"
    },

    # --- Creator mode variety ---
    {
        "id": "creator_02",
        "category": "creator_mode",
        "message": "give me titles for my free fire video",
        "check": lambda r: len(r) > 100 and contains_any(r, ["title"]),
        "description": "Should generate substantial title suggestions for YouTube content"
    },

    # --- Planning variety ---
    {
        "id": "planning_02",
        "category": "planning",
        "message": "how do i start saving money as a student",
        "check": lambda r: len(r) > 200 and contains_any(r, ["step", "1.", "first", "save"]),
        "description": "Budget/finance planning question should produce a structured plan"
    },
]


def run_benchmark():
    print("=" * 70)
    print("  NOVA BENCHMARK SUITE — v1.0")
    print("  Running", len(TEST_CASES), "test cases against", NOVA_URL)
    print("=" * 70)

    results = []
    passed = 0
    failed = 0
    total_time = 0

    for test in TEST_CASES:
        reset_nova_memory()
        print("\n[" + test["id"] + "] (" + test["category"] + ") " + test["description"])
        print("  > Sending:", test["message"])

        reply, elapsed, error = send_to_nova(test["message"])
        total_time += elapsed

        if error:
            print("  ✗ FAILED (error: " + error + ") [" + str(round(elapsed, 1)) + "s]")
            results.append({
                "id": test["id"], "category": test["category"], "passed": False,
                "elapsed_seconds": round(elapsed, 2), "error": error, "reply": None
            })
            failed += 1
            continue

        try:
            test_passed = test["check"](reply)
        except Exception as e:
            test_passed = False
            error = "Check function crashed: " + str(e)

        status = "✓ PASSED" if test_passed else "✗ FAILED"
        print("  " + status + " [" + str(round(elapsed, 1)) + "s]")
        print("  Reply preview:", reply[:120].replace("\n", " ") + ("..." if len(reply) > 120 else ""))

        results.append({
            "id": test["id"], "category": test["category"], "passed": test_passed,
            "elapsed_seconds": round(elapsed, 2), "error": error, "reply": reply[:300]
        })

        if test_passed:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print("  Passed: " + str(passed) + "/" + str(len(TEST_CASES)))
    print("  Failed: " + str(failed) + "/" + str(len(TEST_CASES)))
    print("  Total time: " + str(round(total_time, 1)) + "s")
    print("  Average response time: " + str(round(total_time / len(TEST_CASES), 1)) + "s")

    category_stats = {}
    for r in results:
        cat = r["category"]
        if cat not in category_stats:
            category_stats[cat] = {"passed": 0, "total": 0}
        category_stats[cat]["total"] += 1
        if r["passed"]:
            category_stats[cat]["passed"] += 1

    print("\n  By category:")
    for cat, stats in category_stats.items():
        print("    " + cat + ": " + str(stats["passed"]) + "/" + str(stats["total"]))

    run_summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "passed": passed,
        "failed": failed,
        "total": len(TEST_CASES),
        "pass_rate": round(passed / len(TEST_CASES) * 100, 1),
        "total_time_seconds": round(total_time, 1),
        "average_response_seconds": round(total_time / len(TEST_CASES), 1),
        "category_stats": category_stats,
        "results": results
    }

    history = []
    try:
        with open("benchmark_results.json", "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(run_summary)

    with open("benchmark_results.json", "w") as f:
        json.dump(history, f, indent=2)

    print("\n  Results saved to benchmark_results.json")
    print("  This run is #" + str(len(history)) + " in your benchmark history.")

    if len(history) > 1:
        prev_rate = history[-2]["pass_rate"]
        curr_rate = run_summary["pass_rate"]
        diff = curr_rate - prev_rate
        if diff > 0:
            print("  📈 Pass rate improved by " + str(round(diff, 1)) + " points since last run!")
        elif diff < 0:
            print("  📉 Pass rate dropped by " + str(round(abs(diff), 1)) + " points since last run.")
        else:
            print("  ➡️  Pass rate unchanged since last run.")

    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
