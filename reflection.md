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
4. Added preferences and day_start to Owner, passed into Scheduler, so the plan can account for more than total minutes
5. Made Scheduler store its last generated plan so explain_plan() doesn’t need a plan argument
6. Changed priority from a free string to a Priority enum so sorting is well-defined, not alphabetic

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

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
