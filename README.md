# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Implementation Summary

The backend is five classes in `pawpal_system.py`:

1. **Task** — represents one care activity with a priority, optional recurrence (daily/weekly), and completion tracking via `mark_complete()` / `is_due_today()`.
2. **Pet** — holds a list of `Task`s belonging to that pet.
3. **Owner** — manages multiple `Pet`s and exposes `get_all_tasks()`, which flattens every pet's tasks into one list; this is what lets scheduling work across pets instead of just one.
4. **ScheduledTask** — a single entry in a generated plan: which pet, which task, and what time it's scheduled for.
5. **Scheduler** — takes an `Owner` (not a raw task list), pulls tasks via `get_all_tasks()`, filters to what's due today, sorts by priority, and fits tasks into the owner's `available_time` starting at `day_start`, assigning each a clock time as a `ScheduledTask`. `explain_plan()` renders the result as readable text.

`main.py` demonstrates this end-to-end with one owner, two pets, and four tasks.

## ✨ Features

- **Multi-pet task tracking** — each `Owner` manages multiple `Pet`s, each with its own task list.
- **Priority-based daily scheduling** — `Scheduler.generate_plan()` fits due tasks into the owner's available time, highest priority first.
- **Sorting by time** — `Scheduler.sort_by_time()` orders scheduled tasks chronologically.
- **Filtering** — `Owner.filter_tasks()` filters tasks by pet name and/or completion status.
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags scheduled tasks sharing the same start time, returning a warning instead of crashing.
- **Daily/weekly recurrence** — completing a recurring task via `Pet.complete_task()` automatically queues its next occurrence.
- **Explainable plans** — `Scheduler.explain_plan()` renders the generated schedule as readable text.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output of `python main.py`:

```
Today's Schedule:
  08:00 — Biscuit: Morning walk (30 min) [priority: high]
  08:30 — Biscuit: Feeding (10 min) [priority: high]
  08:40 — Whiskers: Litter box clean (10 min) [priority: medium]
  08:50 — Whiskers: Playtime (20 min) [priority: low]
```

## 🧪 Testing PawPal+

Run the suite with:

```bash
python -m pytest
```

The 9 tests cover: task completion (`mark_complete`), adding a task to a pet, sorting scheduled tasks chronologically (`sort_by_time`), recurring task generation on completion (daily task spawns a next-day instance; a one-off task does not), conflict detection (flags duplicate start times, stays quiet when times differ), and two scheduling edge cases (a pet with no tasks, and a task that doesn't fit the time budget being skipped rather than forced in).

Sample test output:

```
================================================= test session starts ==================================================
platform darwin -- Python 3.13.16, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/csturner/codepath-ai110/module2show-pawpal-starter
plugins: anyio-4.15.1
collected 9 items

tests/test_pawpal.py .........                                                                                   [100%]

================================================== 9 passed in 0.01s ===================================================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5). Core scheduling, sorting, recurrence, and conflict detection are all verified with passing tests. Not yet covered: weekly recurrence with a specific weekday, and the Streamlit UI layer itself (only the backend logic is under test).

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts scheduled tasks chronologically by `start_time` ("HH:MM") using a lambda key. |
| Filtering | `Owner.filter_tasks()` | Filters (pet, task) pairs by pet name and/or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups scheduled tasks by exact `start_time` and returns a warning for any time shared by more than one task. Only checks exact time matches, not overlapping durations (see reflection.md §2b). |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a daily/weekly task via `complete_task()` marks it done and automatically queues a fresh `Task` instance due on the next occurrence (`timedelta(days=1)` for daily, `timedelta(weeks=1)` for weekly). |

## 📸 Demo Walkthrough

**Main UI features (`app.py`):**
- Set owner name and available time for the day
- Add one or more pets
- Add tasks to a specific pet (title, category, duration, priority, recurrence)
- Filter the task list by pet and/or completion status
- Mark a task complete, which automatically queues its next occurrence if it's a daily/weekly task
- Generate today's schedule, with conflict warnings and a sorted, time-stamped table

**Example workflow:**
1. Enter an owner name and available time (e.g., 90 minutes).
2. Add two pets, e.g. "Biscuit" (dog) and "Whiskers" (cat).
3. Add 3-4 tasks across both pets with different priorities and durations.
4. Use the pet/status filters to check incomplete tasks for one pet.
5. Click "Mark complete" on a daily or weekly task and confirm a new pending task appears for its next occurrence.
6. Click "Generate schedule" to see a sorted, time-stamped plan plus a conflict warning or success message.

**Key Scheduler behaviors demonstrated:** priority-first scheduling within the time budget, chronological sorting (`sort_by_time`), conflict detection (`detect_conflicts`), and recurrence (`complete_task` queuing the next occurrence) are all visible directly in the UI, not just the CLI demo below.

**Sample CLI output** (`python main.py`):

```
Today's Schedule:
  08:00 — Biscuit: Morning walk (30 min) [priority: high]
  08:30 — Biscuit: Feeding (10 min) [priority: high]
  08:40 — Whiskers: Litter box clean (10 min) [priority: medium]
  08:50 — Whiskers: Playtime (20 min) [priority: low]

-- Sorting demo --
Out-of-order:
  08:50 — Whiskers: Playtime
  08:40 — Whiskers: Litter box clean
  08:30 — Biscuit: Feeding
  08:00 — Biscuit: Morning walk
Sorted by time:
  08:00 — Biscuit: Morning walk
  08:30 — Biscuit: Feeding
  08:40 — Whiskers: Litter box clean
  08:50 — Whiskers: Playtime

-- Filtering demo --
Biscuit's tasks:
  Morning walk
  Feeding
Incomplete tasks:
  Biscuit: Morning walk
  Biscuit: Feeding
  Whiskers: Litter box clean
  Whiskers: Playtime

-- Recurring task demo --
Before: Biscuit has 3 tasks
After completing a daily task: Biscuit has 4 tasks
Next occurrence due: 2026-10-19

-- Conflict detection demo --
  WARNING: Conflict at 08:00 — Biscuit: Morning walk, Whiskers: Vet checkup
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
