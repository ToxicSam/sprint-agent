"""P0 API Alignment Integration Test Suite"""
import requests
import json
from datetime import date

BASE = "http://127.0.0.1:8000"
errors = []

def test(name, method, path, expected_status, body=None, check_fn=None):
    url = f"{BASE}{path}"
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        elif method == "POST":
            r = requests.post(url, json=body, timeout=10)
        elif method == "PATCH":
            r = requests.patch(url, json=body, timeout=10)
        elif method == "DELETE":
            r = requests.delete(url, timeout=10)
        else:
            r = requests.request(method, url, json=body, timeout=10)

        ok = r.status_code == expected_status
        extra = ""
        if check_fn and ok:
            ok, extra = check_fn(r)

        status = "PASS" if ok else "FAIL"
        if not ok:
            errors.append(name)
            extra = extra or f"got {r.status_code}, expected {expected_status} body={r.text[:100]}"
        print(f"  [{status}] {name}: {method} {path} {extra}")
    except Exception as e:
        errors.append(name)
        print(f"  [FAIL] {name}: {method} {path} - {e}")


# ============================================================
# TEST 1: All endpoints respond with correct methods
# ============================================================
print("=" * 60)
print("TEST 1: Verify all endpoints respond with correct methods")
print("=" * 60)

test("GET /api/sprint", "GET", "/api/sprint", 200)
test("POST /api/sprint", "POST", "/api/sprint", 200, {
    "name": "Test Sprint", "goal": "Test", "status": "active",
    "start_date": "2026-06-01", "end_date": "2026-06-14",
})
test("PATCH /api/sprint/{id} (404)", "PATCH", "/api/sprint/fake-id", 404, {"name": "Updated"})

test("GET /api/members", "GET", "/api/members", 200)
test("POST /api/members", "POST", "/api/members", 200, {"name": "Test User", "role": "dev"})
test("PATCH /api/members/{id} (404)", "PATCH", "/api/members/fake-id", 404, {"name": "Updated"})
test("DELETE /api/members/{id} (404)", "DELETE", "/api/members/fake-id", 404)

test("GET /api/tasks", "GET", "/api/tasks", 200)
test("POST /api/tasks (422 missing data)", "POST", "/api/tasks", 422, {"title": "needs sprint_id"})
test("PATCH /api/tasks/{id} (404)", "PATCH", "/api/tasks/fake-id", 404, {"title": "Updated"})
test("DELETE /api/tasks/{id} (404)", "DELETE", "/api/tasks/fake-id", 404)

test("GET /api/standup", "GET", "/api/standup", 200)
test("GET /api/standup/today", "GET", "/api/standup/today", 200)
test("POST /api/standup (422)", "POST", "/api/standup", 422, {})

test("GET /api/retro/{sprint_id}", "GET", "/api/retro/fake-sprint", 200)
test("POST /api/retro (422)", "POST", "/api/retro", 422, {})
test("DELETE /api/retro/{item_id} (404)", "DELETE", "/api/retro/fake-item", 404)

test("GET /api/agent/history", "GET", "/api/agent/history", 200)
test("DELETE /api/agent/history", "DELETE", "/api/agent/history", 200)

test("GET /api/export", "GET", "/api/export", 200)
test("GET /api/health", "GET", "/api/health", 200)


# ============================================================
# TEST 3: AgentPanel - send a message
# ============================================================
print()
print("=" * 60)
print("TEST 3: Agent chat - send message and get response")
print("=" * 60)

r = requests.post(f"{BASE}/api/agent/chat", json={"role": "user", "content": "hello"}, timeout=10)
if r.status_code == 200:
    data = r.json()
    has_msg = "message" in data and len(data["message"]) > 0
    print(f"  [{'PASS' if has_msg else 'FAIL'}] Agent chat response: {json.dumps(data)[:120]}")
    if not has_msg:
        errors.append("Agent chat response")
else:
    print(f"  [FAIL] Agent chat: status {r.status_code}")
    errors.append("Agent chat")


# ============================================================
# TEST 4: Standup - submit and verify persistence
# ============================================================
print()
print("=" * 60)
print("TEST 4: Standup - submit daily log and verify")
print("=" * 60)

# Get sprint + member from existing data
r = requests.get(f"{BASE}/api/sprint", timeout=10)
sprint = r.json()
if sprint:
    sprint_id = sprint["id"]
else:
    r = requests.post(f"{BASE}/api/sprint", json={"name": "Standup Sprint", "status": "active"}, timeout=10)
    sprint_id = r.json()["id"]

r = requests.get(f"{BASE}/api/members", timeout=10)
members = r.json()
if members:
    member_id = members[0]["id"]
else:
    r = requests.post(f"{BASE}/api/members", json={"name": "Standup User", "role": "dev"}, timeout=10)
    member_id = r.json()["id"]

today = date.today().isoformat()
r = requests.post(f"{BASE}/api/standup", json={
    "sprint_id": sprint_id,
    "member_id": member_id,
    "date": today,
    "completed": "Finished API tests",
    "planned": "More testing",
    "blockers": "None",
    "hours_spent": 8.0,
}, timeout=10)
if r.status_code == 200:
    log = r.json()
    log_id = log.get("id", "")
    print(f"  [PASS] Created daily log: id={log_id}")

    # Verify GET /today returns it
    r2 = requests.get(f"{BASE}/api/standup/today?sprint_id={sprint_id}", timeout=10)
    if r2.status_code == 200:
        today_logs = r2.json()
        found = any(l.get("id") == log_id for l in today_logs)
        print(f"  [{'PASS' if found else 'FAIL'}] Today endpoint returns the log (found={found})")
        if not found:
            errors.append("Standup today")
    else:
        print(f"  [FAIL] GET /api/standup/today: {r2.status_code}")
        errors.append("Standup today")
else:
    print(f"  [FAIL] Create daily log: {r.status_code} {r.text[:100]}")
    errors.append("Standup create")


# ============================================================
# TEST 5: Retro - create, vote, delete
# ============================================================
print()
print("=" * 60)
print("TEST 5: Retro - create, vote, delete")
print("=" * 60)

r = requests.post(f"{BASE}/api/retro", json={
    "sprint_id": sprint_id,
    "category": "liked",
    "item": "Good teamwork",
}, timeout=10)
if r.status_code == 200:
    retro = r.json()
    retro_id = retro["id"]
    print(f"  [PASS] Created retro item: id={retro_id}")

    # Vote
    r2 = requests.post(f"{BASE}/api/retro/vote", json={"retro_id": retro_id}, timeout=10)
    if r2.status_code == 200:
        voted = r2.json()
        print(f"  [PASS] Voted: votes={voted.get('votes', '?')}")
    else:
        print(f"  [FAIL] Vote: {r2.status_code}")
        errors.append("Retro vote")

    # Delete
    r3 = requests.delete(f"{BASE}/api/retro/{retro_id}", timeout=10)
    if r3.status_code == 200:
        print(f"  [PASS] Deleted retro item")
    else:
        print(f"  [FAIL] Delete: {r3.status_code}")
        errors.append("Retro delete")
else:
    print(f"  [FAIL] Create retro item: {r.status_code} {r.text[:100]}")
    errors.append("Retro create")


# ============================================================
# TEST 6: Settings - export/import round-trip
# ============================================================
print()
print("=" * 60)
print("TEST 6: Settings - export/import round-trip")
print("=" * 60)

r = requests.get(f"{BASE}/api/export", timeout=10)
if r.status_code == 200:
    export_data = r.json()
    print(f"  [PASS] Export: got data with keys={list(export_data.keys())[:5]}")

    r2 = requests.post(f"{BASE}/api/import", json=export_data, timeout=10)
    if r2.status_code == 200:
        print(f"  [PASS] Import round-trip successful")
    else:
        print(f"  [FAIL] Import: {r2.status_code} {r2.text[:100]}")
        errors.append("Settings import")
else:
    print(f"  [FAIL] Export: {r.status_code}")
    errors.append("Settings export")


# ============================================================
# TEST 7: Board - task move (drag-and-drop)
# ============================================================
print()
print("=" * 60)
print("TEST 7: Board - task move endpoint")
print("=" * 60)

r = requests.post(f"{BASE}/api/tasks", json={
    "title": "Move Test Task",
    "sprint_id": sprint_id,
    "status": "todo",
}, timeout=10)
if r.status_code == 200:
    task = r.json()
    task_id = task["id"]
    print(f"  [PASS] Created task: id={task_id}, status={task['status']}")

    # Move to progress
    r2 = requests.post(f"{BASE}/api/tasks/{task_id}/move", json={"status": "progress"}, timeout=10)
    if r2.status_code == 200:
        moved = r2.json()
        ok = moved["status"] == "progress"
        print(f"  [{'PASS' if ok else 'FAIL'}] Moved task to progress: status={moved['status']}")
        if not ok:
            errors.append("Task move")
    else:
        print(f"  [FAIL] Move task: {r2.status_code}")
        errors.append("Task move")
else:
    print(f"  [FAIL] Create task for move: {r.status_code}")
    errors.append("Task create for move")


# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 60)
total_checks = 25 + 6  # 25 from TEST 1 + 6 from TESTS 3-7
passed = total_checks - len(errors)
print(f"RESULT: {passed}/{total_checks} checks passed, {len(errors)} failures")
if errors:
    print(f"FAILED: {errors}")
else:
    print("ALL TESTS PASSED")
