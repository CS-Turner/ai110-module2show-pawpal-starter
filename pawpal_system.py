"""
pawpal_system.py
Core logic layer for PawPal+.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import List, Optional, Tuple


class Priority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    """A single pet care activity: what, how long, how often, and whether it's done."""
    name: str
    category: str
    duration: int                        # minutes
    priority: Priority
    recurrence: Recurrence = Recurrence.NONE
    weekday: Optional[int] = None        # 0=Mon..6=Sun; required if recurrence == WEEKLY
    completed: bool = False
    last_completed: Optional[date] = None
    due_date: Optional[date] = None   # explicit next-due date; None = due immediately

    def mark_complete(self, today: Optional[date] = None) -> None:
        """Mark this task done and record when."""
        self.completed = True
        self.last_completed = today or date.today()

    def is_due_today(self, today: Optional[date] = None) -> bool:
        """Return whether this task should appear in today's plan."""
        today = today or date.today()
        if self.completed:
            return False
        if self.recurrence == Recurrence.WEEKLY and self.weekday is not None:
            if today.weekday() != self.weekday:
                return False
            return self.due_date is None or today >= self.due_date
        if self.due_date is not None:
            return today >= self.due_date
        return True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh pending Task for this task's next occurrence, or None if it doesn't recur."""
        if self.recurrence == Recurrence.NONE:
            return None
        base_date = self.last_completed or date.today()
        if self.recurrence == Recurrence.DAILY:
            next_date = base_date + timedelta(days=1)
        elif self.recurrence == Recurrence.WEEKLY:
            next_date = base_date + timedelta(weeks=1)
        else:
            return None
        return Task(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            recurrence=self.recurrence,
            weekday=self.weekday,
            due_date=next_date,
        )


@dataclass
class Pet:
    """A pet and the care tasks assigned to it."""
    name: str
    species: str
    owner: Optional["Owner"] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet, if present (matched by identity, not value)."""
        self.tasks = [t for t in self.tasks if t is not task]

    def complete_task(self, task: Task, today: Optional[date] = None) -> None:
        """Mark a task complete and, if it recurs, queue its next occurrence."""
        task.mark_complete(today)
        next_task = task.next_occurrence()
        if next_task is not None:
            self.add_task(next_task)


@dataclass
class Owner:
    """A pet owner: their household of pets, time budget, and preferences."""
    name: str
    available_time: int                  # minutes available per day
    day_start: str = "08:00"             # "HH:MM"
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this household, keeping the owner<->pet link in sync."""
        if pet.owner is not None and pet.owner is not self and pet in pet.owner.pets:
            pet.owner.pets.remove(pet)
        pet.owner = self
        if pet not in self.pets:
            self.pets.append(pet)

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Return every (pet, task) pair across all of this owner's pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def get_daily_plan(self, today: Optional[date] = None) -> List["ScheduledTask"]:
        """Return today's scheduled plan across all pets, via Scheduler."""
        return Scheduler(self).generate_plan(today)

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Tuple[Pet, Task]]:
        """Return (pet, task) pairs filtered by pet name and/or completion status."""
        results = self.get_all_tasks()
        if pet_name is not None:
            results = [(p, t) for p, t in results if p.name == pet_name]
        if completed is not None:
            results = [(p, t) for p, t in results if t.completed == completed]
        return results


@dataclass
class ScheduledTask:
    """One entry in a generated plan: which pet, which task, and when it starts."""
    pet: Pet
    task: Task
    start_time: str   # "HH:MM"


class Scheduler:
    """Builds and explains a daily plan from an Owner's pets' tasks."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self, today: Optional[date] = None) -> List[ScheduledTask]:
        """Pick due tasks, sort by priority, fit them into available time, assign start times."""
        today = today or date.today()
        due = [(pet, task) for pet, task in self.owner.get_all_tasks() if task.is_due_today(today)]
        due.sort(key=lambda pair: pair[1].priority.value, reverse=True)

        plan: List[ScheduledTask] = []
        minutes_used = 0
        clock = self._to_minutes(self.owner.day_start)

        for pet, task in due:
            if minutes_used + task.duration > self.owner.available_time:
                continue
            plan.append(ScheduledTask(pet=pet, task=task, start_time=self._to_clock(clock)))
            minutes_used += task.duration
            clock += task.duration

        self._last_plan = plan
        return plan

    def sort_by_time(self, scheduled_tasks: Optional[List[ScheduledTask]] = None) -> List[ScheduledTask]:
        """Return scheduled tasks ordered chronologically by their start_time."""
        tasks = scheduled_tasks if scheduled_tasks is not None else self._last_plan
        return sorted(tasks, key=lambda st: st.start_time)

    def detect_conflicts(self, scheduled_tasks: Optional[List[ScheduledTask]] = None) -> List[str]:
        """Return a warning message for each start_time shared by more than one task."""
        tasks = scheduled_tasks if scheduled_tasks is not None else self._last_plan
        by_time: dict = {}
        for st in tasks:
            by_time.setdefault(st.start_time, []).append(st)

        warnings = []
        for start_time, group in by_time.items():
            if len(group) > 1:
                names = ", ".join(f"{st.pet.name}: {st.task.name}" for st in group)
                warnings.append(f"Conflict at {start_time} — {names}")
        return warnings

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the most recently generated plan."""
        if not getattr(self, "_last_plan", None):
            return "No tasks scheduled for today."
        lines = ["Today's Schedule:"]
        for st in self._last_plan:
            lines.append(
                f"  {st.start_time} — {st.pet.name}: {st.task.name} "
                f"({st.task.duration} min) [priority: {st.task.priority.name.lower()}]"
            )
        return "\n".join(lines)

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m

    @staticmethod
    def _to_clock(minutes: int) -> str:
        return f"{minutes // 60:02d}:{minutes % 60:02d}"
