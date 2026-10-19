# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
1. Add/edit a pet care task (walks, feeding, meds, enrichment, grooming)
2. Generate a daily schedule based on constraints (time available, priority, owner preferences)
3. Daily plan view, with reasoning for the order, inclusion of tasks

- What classes did you include, and what responsibilities did you assign to each?
The design includes four classes: Owner, Pet, Task, Scheduler
1. Owner: name (str), pets (List[Pet]), available_time (int, minutes/day). Responsible for registering pets and retrieving the day’s plan.
2. Pet: name (str), species (str), owner (Owner), tasks (List[Task]). Responsible for adding/removing its own care tasks.
3. Task: name (str), category (str — walk/feeding/meds/grooming/enrichment), duration (int), priority (str), recurrence (str — daily/weekly/none). A simple data record for one care item; checks if it’s due today.
4. Scheduler: tasks (List[Task]), time_available (int). Kept separate from the data classes — responsible for producing an ordered daily plan and explaining the reasoning behind it, so scheduling logic stays out of Owner/Pet/Task.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
1. Added ScheduledTask (pet + task + start_time) so the plan no longer loses which pet each task belongs to
2. Made Owner.add_pet() set Pet.owner, keeping the two-way link in sync
3. Added weekday and last_completed to Task so is_due_today() has enough data to evaluate recurrence
4. Added day_start to Owner, which the scheduler applies when assigning start times. Also added a preferences field to Owner for future constraints (e.g., preferred time-of-day), but it is not yet read by the scheduler.
5. Made Scheduler store its last generated plan so explain_plan() doesn’t need a plan argument
6. Changed priority from a free string to a Priority enum so sorting is well-defined, not alphabetic
7. Phase 4 update: recurrence was reworked further. Task gained a due_date field, and completing a task via Pet.complete_task() now creates a fresh Task instance for the next occurrence (via next_occurrence()) rather than resetting the same task in place.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    The scheduler includes tasks that are due today, sorts them from high to low priority, and schedules them sequentially starting at the owner’s day_start. The total scheduled duration cannot exceed available_time. If a task doesn’t fit in the remaining time, it skips that task and considers the next one. The owner’s preferences field exists but is not used yet; the scheduler currently does not apply preferred time-of-day constraints.
- How did you decide which constraints mattered most?
    The available-time budget is the hard limit. Priority determines the order in which tasks are considered, but it does not guarantee that every task will fit. This gives higher-priority tasks first consideration while allowing shorter, lower-priority tasks to use time left over.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    The scheduler uses a greedy, priority-first approach rather than searching for the best combination of tasks. For example, with 15 minutes available, a high-priority 11-minute task is scheduled before medium- and low-priority tasks of 8 and 7 minutes. The remaining 4 minutes are unused, even though the two lower-priority tasks would fill the budget exactly.    
- Why is that tradeoff reasonable for this scenario?
    The approach is simple to follow: tasks are considered in priority order, and each task is either scheduled or skipped based on the remaining time. For a small number of daily tasks, that transparency is useful, even though a different combination could sometimes use the available time more fully.

- A second tradeoff: Scheduler.detect_conflicts() only checks for exact start_time matches, not overlapping durations. A task scheduled at 08:00 for 30 minutes and another at 08:15 for 10 minutes clearly overlap, but the current check would not flag them since their start times differ.
    This is reasonable for now because exact-match checking is simple and cheap, and in practice the scheduler itself assigns sequential, non-overlapping start times, so conflicts only arise from edge cases like manually added tasks. Catching true overlapping-duration conflicts would need to compare time ranges, not just start times, which is a reasonable next improvement but was out of scope for this phase.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    I used AI to brainstorm the initial classes and their responsibilities, draft the Mermaid UML diagram, and help implement the classes and tests. I also used it to review the design.

- What kinds of prompts or questions were most helpful?
    The most useful prompt was a focused one: “Review the skeleton and point out any missing relationships or bottlenecks.” That surfaced the issue that a flat task list would lose which pet each task belonged to.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    I didn’t adopt that design suggestion without checking it. I compared it with the project’s multi-pet requirement and confirmed that the scheduler needed to keep each task associated with its pet. I changed the design so the scheduler receives an Owner and gets pet-task pairs from that owner.

- How did you evaluate or verify what the AI suggested?
    I ran main.py and checked that the sample schedule was ordered by priority and that all sample tasks fit within the available time. I also ran the tests for task completion and adding a task to a pet. Those tests don’t yet cover over-budget scheduling, so I would add a test for that behavior next.

**c. AI Strategy**

- Which AI coding assistant features were most effective for building your scheduler?
    The most effective pattern was asking for a targeted review (attaching a skeleton or a specific method and asking what's missing or how it could be simplified) rather than open-ended generation requests. That surfaced concrete, checkable issues, like the flat task list losing pet context, instead of vague stylistic feedback.

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
    In Phase 4, a suggested simplification of detect_conflicts() replaced the explicit loop with a defaultdict and a list comprehension. It was more compact, but the comprehension buried its filter condition mid-expression and was harder to scan, so I kept the original explicit-loop version for readability and future debuggability.

- How did using separate chat sessions for different phases help you stay organized?
    Keeping design/skeleton work, algorithmic work, and testing in separate sessions kept each conversation's context focused on one concern. It made it easier to ask pointed follow-up questions without earlier, unrelated context influencing the answers, and easier to tell whether a new suggestion reflected fresh reasoning rather than confusion from an overloaded context window.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
    I tested task completion (mark_complete), adding a task to a pet, sorting scheduled tasks chronologically, recurrence (a daily task spawns a next-day instance on completion; a one-off task does not), conflict detection (flags duplicate start times, stays quiet when times differ), and two edge cases (a pet with no tasks, and a task that doesn't fit the time budget being skipped rather than forced in). These matter because they're exactly the "smart" behaviors the README promises; without tests, a later change to the scheduling algorithm could silently break sorting or recurrence.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
    I'm fairly confident (4/5) in the core logic since all 9 tests pass and match the implementation. What's not yet covered: weekly recurrence tied to a specific weekday, true overlapping-duration conflicts (only exact start-time matches are tested), and the Streamlit UI layer itself. If I had more time, I'd add tests for a weekly task's exact due date, for two tasks that overlap without sharing a start time, and for the owner's preferences field once it's actually used by the scheduler.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    The Owner/Pet/Task/Scheduler split held up across all six phases without a major rewrite, aside from the one early fix (Scheduler reading from Owner instead of a flat task list). The tested cases for conflict detection and recurrence (duplicate start times, and a daily task creating its next occurrence) passed on the first run, which suggested the design was sound going into implementation. That doesn't cover overlapping-duration conflicts or weekly recurrence, which aren't tested yet.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    I'd wire the preferences field into actual scheduling logic instead of leaving it unused, and replace exact-time conflict detection with real overlapping-duration checks. On the UI side, the app currently supports adding pets and tasks and generating a schedule, but not editing a task, marking one complete, or seeing why a task was skipped from the plan (it just silently doesn't appear). I'd add a "mark complete" action so recurrence is visible in the UI rather than only the CLI demo, a way to edit or remove an existing task, and a short explanation next to any skipped task (e.g., "didn't fit in remaining time").

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    Being the lead architect meant treating AI output as a draft to verify, not a final answer: checking suggestions against actual requirements, confirming behavior by running the code and tests, and deciding when a "more Pythonic" option wasn't actually the better choice for this project. The AI was fastest at generating structure and catching omissions; the judgment about what the system should actually do, and which tradeoffs were acceptable, stayed with me throughout.
